package brain

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"jarvis/internal/mcp"
	"net/http"
)

// Define the structure of a Tool Call coming FROM the AI
type ToolCall struct {
	Function struct {
		Name      string         `json:"name"`
		Arguments map[string]any `json:"arguments"`
	} `json:"function"`
}

type Message struct {
	Role      string     `json:"role"`
	Content   string     `json:"content"`
	ToolCalls []ToolCall `json:"tool_calls"` // MUST BE TOOL_CALLS (plural)
}

type Response struct {
	Message Message `json:"message"`
}


func Ask(messages []Message) (*Response, error) {
	url := "http://localhost:11434/api/chat"

	// Define the tools (Functions) the AI is allowed to use
	tools := []map[string]any{
		{
			"type": "function",
			"function": map[string]any{
				"name":        "read_file",
				"description": "Read the contents of a file in the project directory",
				"parameters": map[string]any{
					"type": "object",
					"properties": map[string]any{
						"path": map[string]any{
							"type":        "string",
							"description": "The path to the file (e.g., go.mod or cmd/main.go)",
						},
					},
					"required": []string{"path"},
				},
			},
		},
	}

	payload := map[string]any{
		"model":      "qwen2.5-coder:7b",
		"messages":   messages,
		"tools":      tools,
		"stream":     false,
		"keep_alive": 0, // Unload from VRAM immediately after thinking
	}

	jsonData, _ := json.Marshal(payload)
	resp, err := http.Post(url, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("ollama connection failed: %w", err)
	}
	defer resp.Body.Close()

	var result Response
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("failed to decode ollama response: %w", err)
	}

	return &result, nil
}
