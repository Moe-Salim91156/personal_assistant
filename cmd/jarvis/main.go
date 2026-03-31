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
	fmt.Println("JARVIS: MCP Tools Online. Listening...")

	// Initialize history with the System Identity
	history := []brain.Message{
		{Role: "system", Content: "You are JARVIS. Use the 'read_file' tool to help Moe with his code."},
	}

	for {
		input, err := ears.Listen()
		if err != nil || strings.TrimSpace(input) == "" {
			continue
		}

		fmt.Printf("\nMOE: %s\n", input)
		history = append(history, brain.Message{Role: "user", Content: input})

		// First pass: Ask the brain
		resp, err := brain.Ask(history)
		if err != nil {
			fmt.Println("Brain Error:", err)
			continue
		}

		// 3. TOOL EXECUTION (The "Actuator")
		// If the model sends ToolCalls, we MUST execute them and FEED BACK the result
		if len(resp.Message.ToolCalls) > 0 {
			for _, call := range resp.Message.ToolCalls {
				var toolResult string
				var toolErr error

				if call.Function.Name == "read_file" {
					path := call.Function.Arguments["path"].(string)
					fmt.Printf("JARVIS: [Executing Tool] Reading %s...\n", path)

					toolResult, toolErr = tools.ReadFile(path)
					if toolErr != nil {
						toolResult = fmt.Sprintf("Error: %v", toolErr)
					}
				}

				// IMPORTANT: Add the tool output to history so the AI can "see" the file
				history = append(history, brain.Message{
					Role:    "tool",
					Content: toolResult,
					// Some models/SDKs require the ToolCallID here;
					// for Ollama, 'tool' role with content is usually enough
				})
			}

			// 4. SECOND PASS: Now that the Brain has the file content, ask it for the final answer
			fmt.Println("JARVIS: Processing file content...")
			resp, err = brain.Ask(history)
			if err != nil {
				fmt.Println("Final Brain Error:", err)
				continue
			}
		}

		// 5. VOICE: Final Output
		finalText := resp.Message.Content
		if finalText != "" {
			history = append(history, brain.Message{Role: "assistant", Content: finalText})
			fmt.Printf("JARVIS: %s\n", finalText)
			voice.Speak(finalText)
		}
	}
}
