package stt

import (
	"bytes"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

func Transcribe(audio []byte) (string, error) {
	if len(audio) == 0 {
		return "", nil
	}

	home, _ := os.UserHomeDir()
	rawPath := filepath.Join(home, ".jarvis/raw_audio.wav")
	cleanPath := filepath.Join(home, ".jarvis/clean_audio.wav")
	
	// Save the raw stereo audio
	os.WriteFile(rawPath, audio, 0644)

	// Clean audio: High-pass at 200Hz to kill laptop fan hum, 
	// low-pass at 3000Hz to kill high-frequency hiss, and normalize.
	// We use -ac 1 to force it to mono for Whisper.
	cleanCmd := exec.Command("ffmpeg", "-y", "-i", rawPath, "-af", "highpass=f=200,lowpass=f=3000,loudnorm", "-ac", "1", cleanPath)
	cleanCmd.Run()

	script := filepath.Join(home, ".jarvis/whisper_bridge.py")
	cmd := exec.Command("python3", script, cleanPath)

	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr

	if err := cmd.Run(); err != nil {
		return "", err
	}

	return strings.TrimSpace(stdout.String()), nil
}
