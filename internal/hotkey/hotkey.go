package hotkey

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
)

type Hotkey struct {
	Key     string
	rawPath string
}

func New(key string) *Hotkey {
	home, _ := os.UserHomeDir()
	return &Hotkey{
		Key:     key,
		rawPath: filepath.Join(home, ".jarvis", "hotkey_raw.wav"),
	}
}

func (h *Hotkey) WaitForPress() {
	fmt.Printf("\n[Ready] Press Enter to start recording (Simulating %s)...", h.Key)
	var input string
	fmt.Scanln(&input)
}

// RecordUntilRelease records to a WAV file and returns the path.
func (h *Hotkey) RecordUntilRelease() string {
	fmt.Println("🎙  Recording... Press Enter to stop.")

	os.MkdirAll(filepath.Dir(h.rawPath), 0755)

	cmd := exec.Command(
		"arecord",
		"-t", "wav",
		"-f", "S16_LE",
		"-r", "16000",
		"-c", "1",
		h.rawPath,
	)

	if err := cmd.Start(); err != nil {
		fmt.Printf("Error starting arecord: %v\nIs 'alsa-utils' installed?\n", err)
		return ""
	}

	var input string
	fmt.Scanln(&input)
	cmd.Process.Kill()
	cmd.Wait()

	fmt.Println("🛑 Recording stopped.")
	return h.rawPath
}
