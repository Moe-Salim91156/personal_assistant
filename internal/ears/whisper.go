package ears

import (
	"fmt"
	"os"
	"os/exec"
	"strings"
)

func Listen() (string, error) {
	tempFile := "input.wav"
	fmt.Println("JARVIS: Listening...")

	// Record 4 seconds of audio at 16kHz (required by Whisper)
	// 'rec' is part of the sox package
	recordCmd := exec.Command("rec", "-r", "16000", "-c", "1", tempFile, "trim", "0", "4")
	if err := recordCmd.Run(); err != nil {
		return "", fmt.Errorf("mic record failed: %w", err)
	}

	// Transcribe using your compiled whisper-cli
	// -f: input file, -nt: no timestamps, -np: no prints (cleaner output)
	whisperCmd := exec.Command("./whisper-cli", "-m", "models/ggml-base.en.bin", "-f", tempFile, "-nt", "-np")

	out, err := whisperCmd.Output()
	if err != nil {
		return "", fmt.Errorf("transcription failed: %w", err)
	}

	// Clean up the temp file
	os.Remove(tempFile)

	text := strings.TrimSpace(string(out))
	return text, nil
}
