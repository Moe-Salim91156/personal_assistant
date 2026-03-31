package voice

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
)

type KokoroRequest struct {
	Model string  `json:"model"`
	Input string  `json:"input"`
	Voice string  `json:"voice"`
	Speed float64 `json:"speed"`
}

func Speak(text string) error {
	url := "http://localhost:8880/v1/audio/speech"

	reqBody := KokoroRequest{
		Model: "kokoro",
		Input: text,
		Voice: "bm_lewis", // British Male Lewis
		Speed: 1.0,
	}

	jsonData, _ := json.Marshal(reqBody)
	resp, err := http.Post(url, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return fmt.Errorf("could not connect to kokoro: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("kokoro error: %s", string(body))
	}

	// Create temporary audio file
	outFile, err := os.Create("speech.wav")
	if err != nil {
		return err
	}
	defer outFile.Close()

	_, err = io.Copy(outFile, resp.Body)
	if err != nil {
		return err
	}

	// Play using ffplay
	cmd := exec.Command("ffplay", "-nodisp", "-autoexit", "speech.wav")
	return cmd.Run()
}
