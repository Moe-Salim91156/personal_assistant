package hotkey

import (
	"fmt"
	"os/exec"
)

type Hotkey struct {
	Key string
}

func New(key string) *Hotkey {
	return &Hotkey{Key: key}
}

func (h *Hotkey) WaitForPress() {
	fmt.Printf("\n[Ready] Press Enter to start recording (Simulating %s)...", h.Key)
	var input string
	fmt.Scanln(&input)
}

func (h *Hotkey) RecordUntilRelease() []byte {
	fmt.Println("🎙  Recording... Press Enter to stop.")
	
	// S16_LE, 16000Hz, Mono is the standard for Whisper
	cmd := exec.Command("arecord", "-t", "wav", "-f", "S16_LE", "-r", "16000", "-c", "1")
	
	stdout, err := cmd.StdoutPipe()
	if err != nil {
		fmt.Printf("Error creating pipe: %v\n", err)
		return nil
	}
	
	if err := cmd.Start(); err != nil {
		fmt.Printf("Error starting arecord: %v\n. Is 'alsa-utils' installed?", err)
		return nil
	}

	// Wait for Enter to stop
	var input string
	fmt.Scanln(&input)
	cmd.Process.Kill()

	// Capture the bytes
	out := make([]byte, 1024*1024) // 1MB buffer limit
	n, _ := stdout.Read(out)
	
	fmt.Println("🛑 Recording stopped.")
	return out[:n]
}
