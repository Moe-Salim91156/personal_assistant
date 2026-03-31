package main

import (
	"encoding/json"
	"fmt"
	"log"
	"strings"

	"jarvis/internal/brain"
	"jarvis/internal/ears"
	"jarvis/internal/mcp"
	"jarvis/internal/voice"
)

// Whisper hallucinates these on silence — ignore them
var junkPhrases = map[string]bool{
	"[blank_audio]":        true,
	"thank you.":           true,
	"thanks for watching.": true,
	"you":                  true,
	".":                    true,
	"...":                  true,
	"[silence]":            true,
	"[ silence ]":          true,
}

// normalize moves a plain-text or markdown-fenced tool call into ToolCalls
func normalize(resp *brain.Response) {
	if len(resp.Message.ToolCalls) > 0 || resp.Message.Content == "" {
		return
	}
	content := strings.TrimSpace(resp.Message.Content)

	// Strip ```json ... ``` or ``` ... ```
	if strings.HasPrefix(content, "```") {
		first := strings.Index(content, "\n")
		last := strings.LastIndex(content, "```")
		if first != -1 && last > first {
			content = strings.TrimSpace(content[first+1 : last])
		}
	}

	if !strings.HasPrefix(content, "{") {
		return
	}

	var raw struct {
		Name      string         `json:"name"`
		Arguments map[string]any `json:"arguments"`
	}
	if err := json.Unmarshal([]byte(content), &raw); err != nil || raw.Name == "" {
		return
	}

	tc := brain.ToolCall{}
	tc.Function.Name = raw.Name
	tc.Function.Arguments = raw.Arguments
	resp.Message.ToolCalls = []brain.ToolCall{tc}
	resp.Message.Content = ""
}

func main() {
	bridge, err := mcp.NewBridge("npx", "-y", "@modelcontextprotocol/server-filesystem", ".")
	if err != nil {
		log.Fatalf("MCP bridge failed: %v", err)
	}
	defer bridge.Stop()

	tools := bridge.GetToolsForOllama()
	fmt.Printf("JARVIS: Online. %d MCP tools loaded.\n", len(tools))

	history := []brain.Message{
		{
			Role: "system",
			Content: `You are JARVIS, a coding assistant.
The working directory is '.', which is /home/moe/personal_assistant.
Always use relative paths starting with '.' when calling file tools (e.g. path: "." or path: "./internal").
Never use absolute paths. Never guess paths. If unsure, call list_directory with path "." first.
When you have the answer, respond in plain English — do not call more tools.`,
		},
	}

	for {
		input, err := ears.Listen()
		if err != nil {
			continue
		}

		clean := strings.TrimSpace(strings.ToLower(input))
		if clean == "" || junkPhrases[clean] {
			continue
		}

		fmt.Printf("\nMOE: %s\n", input)
		history = append(history, brain.Message{Role: "user", Content: input})

		resp, err := brain.Ask(history, tools)
		if err != nil {
			fmt.Println("Brain error:", err)
			continue
		}
		normalize(resp)

		// Tool loop — capped at 6 to prevent infinite loops
		for i := 0; i < 6 && len(resp.Message.ToolCalls) > 0; i++ {
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
			normalize(resp)
		}

		finalText := resp.Message.Content
		if finalText != "" {
			history = append(history, brain.Message{Role: "assistant", Content: finalText})
			fmt.Printf("JARVIS: %s\n", finalText)
			voice.Speak(finalText)
		}
	}
}
