package speaker

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"sync"
)

var mu sync.Mutex

func Say(text string) {
	if strings.TrimSpace(text) == "" {
		return
	}
	mu.Lock()
	defer mu.Unlock()

	fmt.Printf("🔊 Jarvis: %s\n", text)

	home, _ := os.UserHomeDir()
	// Ensure this matches your ls -R output exactly
	modelPath := filepath.Join(home, ".jarvis/voices/en_US-ryan-medium.onnx")

	// Use piper-tts (the link we just made)
	piper := exec.Command("piper-tts",
		"--model", modelPath,
		"--output-raw",
	)
	aplay := exec.Command("aplay",
		"--rate", "22050",
		"--format", "S16_LE",
		"--channels", "1",
	)

	pipe, _ := piper.StdoutPipe()
	aplay.Stdin = pipe
	piper.Stdin = strings.NewReader(text)

	if err := piper.Start(); err != nil {
		fmt.Printf("TTS Error: %v. Make sure /usr/local/bin/piper-tts exists.\n", err)
		return
	}
	aplay.Run()
}
