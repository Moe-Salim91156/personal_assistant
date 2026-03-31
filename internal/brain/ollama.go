package brain

import (
	"bytes"
	"encoding/json"
	// "fmt"
	"net/http"
)

type Message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type OllamaChatRequest struct {
	Model    string    `json:"model"`
	Messages []Message `json:"messages"`
	Stream   bool      `json:"stream"`
}

type OllamaChatResponse struct {
	Message Message `json:"message"`
	Done    bool    `json:"done"`
}

// Global history to keep Jarvis's memory alive during the session
var History []Message

func Ask(userInput string) (string, error) {
	url := "http://localhost:11434/api/chat"

	// If history is empty, add the System Prompt
	if len(History) == 0 {
		History = append(History, Message{
			Role:    "system",
			Content: "You are JARVIS. You help Moe in his lab. To read files, reply ONLY with: TOOL:read_file[filename.go]. Otherwise, be witty and helpful.",
		})
	}

	// Add User's new message to history
	History = append(History, Message{Role: "user", Content: userInput})

	reqBody := OllamaChatRequest{
		Model:    "qwen2.5-coder:7b",
		Messages: History,
		Stream:   false,
	}

	jsonData, _ := json.Marshal(reqBody)
	resp, err := http.Post(url, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	var result OllamaChatResponse
	json.NewDecoder(resp.Body).Decode(&result)

	// Add Jarvis's response to history so he remembers what he said
	History = append(History, result.Message)

	return result.Message.Content, nil
}
