package main

import (
	"fmt"
	"log"
	"strings"

	"jarvis/internal/brain"
	"jarvis/internal/ears"
	"jarvis/internal/mcp"
	"jarvis/internal/voice"
)

func main() {
	// Swap this command for any MCP server you want
	bridge, err := mcp.NewBridge("npx", "-y", "@modelcontextprotocol/server-filesystem", ".")
	if err != nil {
		log.Fatalf("MCP bridge failed: %v", err)
	}
	defer bridge.Stop()

	tools := bridge.GetToolsForOllama()
	fmt.Printf("JARVIS: Online. %d MCP tools loaded.\n", len(tools))

	history := []brain.Message{
		{Role: "system", Content: "You are JARVIS. Use available tools to help Moe with his code."},
	}

	for {
		input, err := ears.Listen()
		if err != nil || strings.TrimSpace(input) == "" {
			continue
		}

		fmt.Printf("\nMOE: %s\n", input)
		history = append(history, brain.Message{Role: "user", Content: input})

		resp, err := brain.Ask(history, tools)
		if err != nil {
			fmt.Println("Brain error:", err)
			continue
		}

		// Tool loop — handles chained tool calls
		for len(resp.Message.ToolCalls) > 0 {
			for _, call := range resp.Message.ToolCalls {
				fmt.Printf("JARVIS: [Tool] %s %v\n", call.Function.Name, call.Function.Arguments)

				result, toolErr := bridge.CallTool(call.Function.Name, call.Function.Arguments)
				if toolErr != nil {
					result = fmt.Sprintf("Error: %v", toolErr)
				}

				history = append(history, brain.Message{Role: "tool", Content: result})
			}

			resp, err = brain.Ask(history, tools)
			if err != nil {
				fmt.Println("Brain error:", err)
				break
			}
		}

		finalText := resp.Message.Content
		if finalText != "" {
			history = append(history, brain.Message{Role: "assistant", Content: finalText})
			fmt.Printf("JARVIS: %s\n", finalText)
			voice.Speak(finalText)
		}
	}
}
