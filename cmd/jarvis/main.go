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
	"[blank_audio]": true,
	"thank you.":    true,
	"you":           true,
	".":             true,
	"...":           true,
	"[silence]":     true,
	"[ silence ]":   true,
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
			Content: `You are JARVIS, a highly efficient AI terminal assistant for Moe, Your (Sir).
Your goal is to execute tasks proactively using your MCP tools.

### CORE OPERATING PROTOCOLS:
1. DISCOVERY FIRST: If Moe asks about the project or "files," ALWAYS call "list_directory" with "path: "."" first to orient yourself. 
2. NO GUESSING: Never assume a file exists. If you need to see code, use "read_file".
3. SILENT EXECUTION: Do not explain that you are calling a tool. Just execute it.
4. FINAL RESPONSE: Only after you have gathered all necessary data from your tools should you provide a natural language answer to Moe.
5. CONTEXT: The current working directory is /home/moe/personal_assistant. Use relative paths starting with ".".
6. RECURSIVE SEARCH: if Moe wanted to locate code files (.cpp, .go , .c, etc..) and they are located inside subdirectories of the current working directory you can execute list_directory on each one of the subdirectories until you see the content of each subdirectories and maybe find what Moe Wants
### RESPONSE FORMAT:
- If you need data: Use the tool-calling function provided.
- If you have the data: Respond in plain, concise English and call him sir. Do not include JSON in your final verbal answer.`,
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
