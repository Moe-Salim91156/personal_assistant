package main

import (
	"fmt"
	"strings"

	"jarvis/internal/brain"
	"jarvis/internal/ears"
	"jarvis/internal/tools"
	"jarvis/internal/voice"
)

func main() {
	fmt.Println("JARVIS: Systems Online. I am listening.")

	for {
		// 1. EARS: Listen for 4-5 seconds
		input, err := ears.Listen()
		if err != nil {
			fmt.Printf("Ears Error: %v\n", err)
			continue
		}

		// Skip if Whisper didn't hear anything or heard background noise
		cleanInput := strings.TrimSpace(input)
		if cleanInput == "" || strings.Contains(cleanInput, "[BLANK_AUDIO]") {
			continue
		}

		fmt.Printf("\nDEBUG - What Whisper Heard: [%s]\n", cleanInput)

		// 2. BRAIN: Initial Thought
		response, err := brain.Ask(cleanInput)
		if err != nil {
			fmt.Printf("Brain Error: %v\n", err)
			continue
		}

		fmt.Printf("DEBUG - Brain Response: [%s]\n", response)

		// 3. TOOL CHECK: Did the Brain ask to read a file?
		// We check for both "TOOL:read_file" and "TOOL: read_file" to be safe
		if strings.Contains(response, "TOOL:read_file") || strings.Contains(response, "TOOL: read_file") {

			filename := extractFilename(response)
			if filename != "" {
				fmt.Printf("JARVIS: Accessing %s...\n", filename)

				// 4. HANDS: Go physically reads the file
				content, err := tools.ReadProjectFile(filename)
				if err != nil {
					errMsg := fmt.Sprintf("I'm sorry Moe, I couldn't find the file %s.", filename)
					fmt.Println("Tool Error:", err)
					voice.Speak(errMsg)
					continue
				}

				// 5. RE-PROCESS: Feed the file content back to the Brain
				fmt.Println("JARVIS: Analyzing content...")
				contextPrompt := fmt.Sprintf("FILE_CONTENT(%s):\n%s", filename, content)

				finalResponse, err := brain.Ask(contextPrompt)
				if err != nil {
					fmt.Println("Brain Error:", err)
					continue
				}

				fmt.Printf("JARVIS: %s\n", finalResponse)
				voice.Speak(finalResponse)
				continue // Back to the start of the loop
			}
		}

		// 6. VOICE: If no tool was needed, just speak the normal response
		fmt.Printf("JARVIS: %s\n", response)
		voice.Speak(response)
	}
}

// extractFilename pulls the filename out of TOOL:read_file[filename.go]
func extractFilename(response string) string {
	start := strings.Index(response, "[")
	end := strings.Index(response, "]")

	if start == -1 || end == -1 || end <= start {
		return ""
	}

	// Extract and clean up any accidental spaces
	return strings.TrimSpace(response[start+1 : end])
}
