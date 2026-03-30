package main

import (
	"fmt"
	"os"
	"os/signal"
	"strings"
	"syscall"

	"jarvis/internal/brain"
	"jarvis/internal/config"
	"jarvis/internal/executor"
	"jarvis/internal/greeting"
	"jarvis/internal/hotkey"
	"jarvis/internal/memory"
	"jarvis/internal/services"
	"jarvis/internal/stt"
)

var conversationHistory []string

const maxHistory = 10

func addToHistory(role, text string) {
	conversationHistory = append(conversationHistory, fmt.Sprintf("%s: %s", role, text))
	if len(conversationHistory) > maxHistory {
		conversationHistory = conversationHistory[len(conversationHistory)-maxHistory:]
	}
}

func historyString() string {
	return strings.Join(conversationHistory, "\n")
}

func main() {
	fmt.Println("⚡ Jarvis starting...")

	cfg, err := config.Load("config/commands.yaml")
	if err != nil {
		fmt.Fprintf(os.Stderr, "failed to load config: %v\n", err)
		os.Exit(1)
	}

	mem, err := memory.Open("~/.jarvis/memory.db")
	if err != nil {
		fmt.Fprintf(os.Stderr, "failed to open memory: %v\n", err)
		os.Exit(1)
	}
	defer mem.Close()

	svc, err := services.NewManager()
	if err != nil {
		fmt.Fprintf(os.Stderr, "failed to start services: %v\n", err)
		os.Exit(1)
	}
	defer svc.Close()

	b := brain.New(cfg.Planner)

	go greeting.Boot(mem, svc.Say)

	wakeCh, err := hotkey.WakeWordListener()
	if err != nil {
		fmt.Printf("⚠  wake word unavailable: %v\nFalling back to Enter key.\n", err)
		wakeCh = nil
	}

	hk := hotkey.New(cfg.Hotkey)

	fmt.Println("✅ Jarvis ready.")

	sig := make(chan os.Signal, 1)
	signal.Notify(sig, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		for {
			var audioPath string

			if wakeCh != nil {
				fmt.Println("\n[Listening for wake word...]")
				<-wakeCh
				fmt.Println("🔔 Wake word detected — recording (press Enter to stop)")
				svc.Say("Yes?")
				audioPath = hk.RecordUntilRelease()
			} else {
				hk.WaitForPress()
				audioPath = hk.RecordUntilRelease()
			}

			if audioPath == "" {
				svc.Say("Recording failed.")
				continue
			}

			text, err := stt.Transcribe(audioPath)
			if err != nil {
				fmt.Printf("[STT error] %v\n", err)
				svc.Say("Sorry, I had trouble understanding that.")
				continue
			}
			if text == "" {
				svc.Say("I didn't catch anything.")
				continue
			}

			fmt.Printf("👤 You: %q\n", text)
			addToHistory("Mohammad", text)

			memories := svc.MemoryRecall(text, 5)
			profile := svc.ProfileGet()

			decision, err := b.Think(text, profile+"\n"+memories, historyString())
			if err != nil {
				fmt.Printf("[brain error] %v\n", err)
				svc.Say("I had trouble thinking about that.")
				continue
			}

			var finalResponse string
			if len(decision.Tools) == 0 || decision.Tools[0].Tool == "none" {
				finalResponse = decision.Response
			} else {
				for _, tc := range decision.Tools {
					if result := executeTool(tc, cfg, svc); result != "" {
						finalResponse = result
					}
				}
				if finalResponse == "" {
					finalResponse = decision.Response
				}
			}

			if finalResponse == "" {
				finalResponse = "Done."
			}

			fmt.Printf("🤖 Jarvis: %s\n", finalResponse)
			svc.Say(finalResponse)
			addToHistory("Jarvis", finalResponse)

			svc.MemoryStore(
				fmt.Sprintf("User: %s | Jarvis: %s", text, finalResponse),
				"interaction",
			)

			go func(input, response string) {
				key, value, should := b.LearnFromInteraction(input, response)
				if should && key != "" && value != "" {
					svc.ProfileStore(key, value)
					fmt.Printf("📝 Learned: %s = %s\n", key, value)
				}
			}(text, finalResponse)

			mem.Log(text, finalResponse)
		}
	}()

	<-sig
	fmt.Println("\n👋 Jarvis shutting down.")
}

func executeTool(tc brain.ToolCall, cfg *config.Config, svc *services.Manager) string {
	switch tc.Tool {

	case "web_search":
		query := tc.Args["query"]
		fmt.Printf("🔍 Searching: %s\n", query)
		return svc.WebSearch(query)

	case "system_info":
		out, _ := executor.RunRaw("bash", "-c",
			`echo "CPU: $(top -bn1 | grep 'Cpu(s)' | awk '{print $2}')% | RAM: $(free -h | awk '/^Mem/{print $3"/"$2}') | GPU: $(nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits 2>/dev/null || echo 'N/A')"`,
		)
		return "System status: " + strings.TrimSpace(out)

	case "git_push":
		msg := tc.Args["message"]
		if msg == "" {
			msg = "jarvis auto-commit"
		}
		_, err := executor.RunRaw("bash", "-c",
			fmt.Sprintf("git add . && git commit -m %q && git push", msg),
		)
		if err != nil {
			return "Git push failed. Check the terminal."
		}
		return "Changes pushed to git."

	case "docker":
		action := tc.Args["action"]
		if cmd := findCommand(cfg, "docker"); cmd != nil {
			cmd.Action = action
			if _, err := executor.Run(cmd, ""); err != nil {
				return fmt.Sprintf("Docker %s failed.", action)
			}
			return fmt.Sprintf("Docker %s done.", action)
		}
		return "Docker not configured."

	case "terraform":
		action := tc.Args["action"]
		if cmd := findCommand(cfg, "terraform"); cmd != nil {
			cmd.Action = action
			if _, err := executor.Run(cmd, ""); err != nil {
				return fmt.Sprintf("Terraform %s failed.", action)
			}
			return fmt.Sprintf("Terraform %s complete.", action)
		}
		return "Terraform not configured."

	case "open_app":
		app := tc.Args["app"]
		if _, err := executor.RunRaw("bash", "-c", fmt.Sprintf("nohup %s &>/dev/null &", app)); err != nil {
			return fmt.Sprintf("Couldn't open %s.", app)
		}
		return fmt.Sprintf("Opening %s.", app)

	case "recall_memory":
		memories := svc.MemoryRecall(tc.Args["query"], 5)
		if memories == "" {
			return "I don't have anything relevant in memory."
		}
		return "Here's what I remember: " + memories

	case "store_preference":
		svc.ProfileStore(tc.Args["key"], tc.Args["value"])
		return "Got it, I'll remember that."

	case "run_command":
		if cmd := findCommand(cfg, tc.Args["name"]); cmd != nil {
			if _, err := executor.Run(cmd, ""); err != nil {
				return "Command failed."
			}
			if cmd.SpeechTemplate != "" {
				return cmd.SpeechTemplate
			}
			return "Done."
		}
		return fmt.Sprintf("Unknown command: %s", tc.Args["name"])

	default:
		return ""
	}
}

func findCommand(cfg *config.Config, name string) *config.Command {
	for k, cmd := range cfg.Commands {
		if k == name || cmd.Plugin == name {
			c := cmd
			return &c
		}
	}
	return nil
}
