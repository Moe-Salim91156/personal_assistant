package stt

import (
	"bytes"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

// Transcribe takes a WAV file path, runs ffmpeg noise cleanup,
// then calls whisper_bridge.py on the GPU.
func Transcribe(rawPath string) (string, error) {
	if rawPath == "" {
		return "", fmt.Errorf("no audio file path provided")
	}

	info, err := os.Stat(rawPath)
	if err != nil {
		return "", fmt.Errorf("audio file not found: %w", err)
	}
	if info.Size() < 1024 {
		return "", fmt.Errorf("audio file too small, likely silence")
	}

	home, _ := os.UserHomeDir()
	cleanPath := filepath.Join(home, ".jarvis", "clean_audio.wav")

	cleanCmd := exec.Command(
		"ffmpeg", "-y",
		"-i", rawPath,
		"-af", "highpass=f=200,lowpass=f=3000,loudnorm",
		"-ac", "1",
		"-ar", "16000",
		cleanPath,
	)
	if out, err := cleanCmd.CombinedOutput(); err != nil {
		return "", fmt.Errorf("ffmpeg failed: %v\n%s", err, out)
	}

	venv   := filepath.Join(home, ".jarvis", ".venv", "bin", "python3")
	python := venv
	if _, err := os.Stat(venv); err != nil {
		python = "python3"
	}

	script := filepath.Join(home, ".jarvis", "whisper_bridge.py")
	cmd := exec.Command(python, script, cleanPath)

	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr

	if err := cmd.Run(); err != nil {
		return "", fmt.Errorf("whisper failed: %v\nstderr: %s", err, stderr.String())
	}

	return strings.TrimSpace(stdout.String()), nil
}
