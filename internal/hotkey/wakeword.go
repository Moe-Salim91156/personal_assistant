package hotkey

import (
	"bufio"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

// WakeWordListener runs wake_word.py in the background and sends on the
// returned channel whenever a wake word is detected.
func WakeWordListener() (<-chan struct{}, error) {
	home, _ := os.UserHomeDir()
	script := filepath.Join(home, ".jarvis", "wake_word.py")
	venv   := filepath.Join(home, ".jarvis", ".venv", "bin", "python3")

	python := venv
	if _, err := os.Stat(venv); err != nil {
		python = "python3"
	}

	cmd := exec.Command(python, script)
	cmd.Stderr = os.Stderr

	stdout, err := cmd.StdoutPipe()
	if err != nil {
		return nil, fmt.Errorf("wake word stdout pipe: %w", err)
	}

	if err := cmd.Start(); err != nil {
		return nil, fmt.Errorf("wake word start: %w", err)
	}

	ch := make(chan struct{}, 1)

	go func() {
		scanner := bufio.NewScanner(stdout)
		for scanner.Scan() {
			if strings.TrimSpace(scanner.Text()) == "WAKE" {
				select {
				case ch <- struct{}{}:
				default:
				}
			}
		}
		cmd.Wait()
		fmt.Println("⚠  wake word process exited — restart Jarvis to re-enable")
	}()

	fmt.Println("👂 Wake word listener active — say 'Jarvis', 'Hey Jarvis', or 'Wake up Jarvis'")
	return ch, nil
}
