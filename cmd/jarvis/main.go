package main

import (
	"encoding/json"
	"fmt"
	"jarvis/internal/brain"
	"jarvis/internal/ears"
	"jarvis/internal/mcp"
	"jarvis/internal/voice"
	"log"
	"os"
	"os/signal"
	"strings"
	"syscall"
)

var junkPhrases = map[string]bool{
	"[blank_audio]": true,
	"thank you.":    true,
	"you":           true,
	".":             true,
	"...":           true,
	"[silence]":     true,
	"[ silence ]":   true,
}

const historyFile = "history.json"

// saveHistory writes the current conversation to a JSON file
func saveHistory(history []brain.Message) {
	data, err := json.MarshalIndent(history, "", "  ")
	if err != nil {
		fmt.Println("Error encoding history:", err)
		return
	}
	err = os.WriteFile(historyFile, data, 0644)
	if err != nil {
		fmt.Println("Error writing history file:", err)
	}
}

// loadHistory reads the previous conversation from the JSON file
func loadHistory() []brain.Message {
	data, err := os.ReadFile(historyFile)
	if err != nil {
		return nil // Return nil if no file exists
	}
	var history []brain.Message
	if err := json.Unmarshal(data, &history); err != nil {
		fmt.Println("Error parsing history file, starting fresh.")
		return nil
	}
	return history
}
func normalize(resp *brain.Response) {
	// If Ollama already gave us structured tool calls, we are good.
	if len(resp.Message.ToolCalls) > 0 {
		return
	}

	content := resp.Message.Content
	// Look for the FIRST '{' and the LAST '}' to extract JSON from the "JSON shit"
	start := strings.Index(content, "{")
	end := strings.LastIndex(content, "}")

	if start != -1 && end != -1 && end > start {
		jsonStr := content[start : end+1]
		var raw struct {
			Name      string         `json:"name"`
			Arguments map[string]any `json:"arguments"`
		}
		if err := json.Unmarshal([]byte(jsonStr), &raw); err == nil && raw.Name != "" {
			tc := brain.ToolCall{}
			tc.Function.Name = raw.Name
			tc.Function.Arguments = raw.Arguments
			resp.Message.ToolCalls = []brain.ToolCall{tc}
			resp.Message.Content = "" // Clear the "text" so it doesn't speak the JSON
			return
		}
	}
}
func main() {
	// 1. Load History from file
	history := loadHistory()

	// 2. Initialize System Prompt if history is empty
	if len(history) == 0 {
		history = []brain.Message{
			{
				Role: "system",
				Content: `You are JARVIS, a highly efficient AI terminal assistant for Moe (Sir).
Your goal is to execute tasks proactively using your MCP tools.

### CORE OPERATING PROTOCOLS:
1. DISCOVERY FIRST: If Moe asks about "files", ALWAYS call "list_directory" with "path: ." first.
2. NO GUESSING: Never assume a file exists. Use "read_file" to see content.
3. SILENT EXECUTION: Do not explain tool calls. Just execute them.
4. FINAL RESPONSE: Call Moe "Sir". Provide natural language answers ONLY after gathering data.
5. PATHS: Use relative paths starting with "./".
6. RECURSIVE: Use "list_directory" on subfolders to find code files (.go, .py, etc).

### RESPONSE FORMAT:
- If data is needed: Use the tool-calling function.
-  Plain, concise English. No JSON.`,
			},
		}
	}

	bridge, err := mcp.NewBridge("npx", "-y", "@modelcontextprotocol/server-filesystem", ".")
	if err != nil {
		log.Fatalf("MCP bridge failed: %v", err)
	}

	// 3. Graceful Shutdown: Save history on Ctrl+C
	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt, syscall.SIGTERM)
	go func() {
		<-c
		fmt.Println("\nJARVIS: Saving memory and shutting down, Sir.")
		saveHistory(history)
		bridge.Stop()
		os.Exit(0)
	}()

	tools := bridge.GetToolsForOllama()
	fmt.Printf("JARVIS: Online. %d MCP tools loaded.\n", len(tools))
	fmt.Println("JARVIS: Listening...")

	for {
		input, err := ears.Listen()
		if err != nil {
			continue
		}

		clean := strings.TrimSpace(strings.ToLower(input))
		if clean == "" || junkPhrases[clean] {
			continue
		}

		fmt.Printf("\nMOE: %s\n", input)
		history = append(history, brain.Message{Role: "user", Content: input})

		resp, err := brain.Ask(history, tools)
		if err != nil {
			fmt.Println("Brain error:", err)
			continue
		}
		normalize(resp)

		// Tool Loop
		for i := 0; i < 6 && len(resp.Message.ToolCalls) > 0; i++ {
			// Add assistant tool-call intent to history
			history = append(history, brain.Message{
				Role:      "assistant",
				ToolCalls: resp.Message.ToolCalls,
			})

			for _, call := range resp.Message.ToolCalls {
				fmt.Printf("JARVIS: [Tool] %s %v\n", call.Function.Name, call.Function.Arguments)

				result, toolErr := bridge.CallTool(call.Function.Name, call.Function.Arguments)
				if toolErr != nil {
					result = fmt.Sprintf("Error: %v", toolErr)
				}

				// Append tool result to history
				history = append(history, brain.Message{
					Role:    "tool",
					Content: result,
				})
			}

			// Ask brain again with tool results
			resp, err = brain.Ask(history, tools)
			if err != nil {
				fmt.Println("Brain error:", err)
				break
			}
			normalize(resp)
		}

		// Final spoken response
		finalText := resp.Message.Content
		if finalText != "" {
			history = append(history, brain.Message{Role: "assistant", Content: finalText})
			fmt.Printf("JARVIS: %s\n", finalText)
			voice.Speak(finalText)
		}

		// 4. Save history after every successful turn
		saveHistory(history)
	}
}
