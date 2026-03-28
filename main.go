package main

import (
	"fmt"
	"os"
	"os/signal"
	"syscall"

	"jarvis/internal/config"
	"jarvis/internal/greeting"
	"jarvis/internal/hotkey"
	"jarvis/internal/memory"
	"jarvis/internal/router"
	"jarvis/internal/speaker"
	"jarvis/internal/stt"
)

func main() {
	fmt.Println("⚡ Jarvis starting...")

	// 1. load config (commands.yaml)
	cfg, err := config.Load("config/commands.yaml")
	if err != nil {
		fmt.Fprintf(os.Stderr, "failed to load config: %v\n", err)
		os.Exit(1)
	}

	// 2. open memory (SQLite)
	mem, err := memory.Open("~/.jarvis/memory.db")
	if err != nil {
		fmt.Fprintf(os.Stderr, "failed to open memory: %v\n", err)
		os.Exit(1)
	}
	defer mem.Close()

	// 3. boot greeting — checks docker/terraform, speaks status
	go greeting.Boot(mem, speaker.Say)

	// 4. main loop — hotkey triggers listen → understand → act → speak
	hk := hotkey.New(cfg.Hotkey) // e.g. F9
	rt := router.New(cfg, mem)

	fmt.Println("✅ Jarvis ready. Hold", cfg.Hotkey, "to speak.")

	// clean shutdown on Ctrl+C or SIGTERM
	sig := make(chan os.Signal, 1)
	signal.Notify(sig, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		for {
			// blocks until hotkey is held down
			hk.WaitForPress()
			fmt.Print("🎙  Listening... ")

			// record until hotkey released
			audio := hk.RecordUntilRelease()

			// transcribe
			text, err := stt.Transcribe(audio)
			if err != nil || text == "" {
				speaker.Say("Sorry, I didn't catch that.")
				continue
			}

			fmt.Printf("you said: %q\n", text)

			// route and execute
			result := rt.Handle(text)

			// speak result back
			speaker.Say(result.Speech)

			// save to memory
			mem.Log(text, result)
		}
	}()

	<-sig
	fmt.Println("\n👋 Jarvis shutting down.")
}
