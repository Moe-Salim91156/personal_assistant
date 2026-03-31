package brain

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
)

type ToolCall struct {
	Function struct {
		Name      string         `json:"name"`
		Arguments map[string]any `json:"arguments"`
	} `json:"function"`
}

type Message struct {
	Role      string     `json:"role"`
	Content   string     `json:"content"`
	ToolCalls []ToolCall `json:"tool_calls,omitempty"`
}

type Response struct {
	Message Message `json:"message"`
}

func Ask(messages []Message, tools []map[string]any) (*Response, error) {
	payload := map[string]any{
		"model":      "llama3.1:8b",
		"messages":   messages,
		"tools":      tools,
		"stream":     false,
		"keep_alive": 0,
	}

	jsonData, _ := json.Marshal(payload)
	resp, err := http.Post("http://localhost:11434/api/chat", "application/json", bytes.NewBuffer(jsonData))
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
