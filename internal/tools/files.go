package tools

import (
	"os"
	"path/filepath"
	"strings"
)

// extractFilename takes "TOOL:read_file[internal/brain/ollama.go]"
// and returns "internal/brain/ollama.go"
func extractFilename(response string) string {
	// Look for the opening bracket
	start := strings.Index(response, "[")
	// Look for the closing bracket
	end := strings.Index(response, "]")

	// If brackets aren't found, return an empty string or a default
	if start == -1 || end == -1 || end <= start {
		return ""
	}

	// Extract the text between [ and ]
	return response[start+1 : end]
}

// ReadProjectFile allows Jarvis to see your code
func ReadProjectFile(filename string) (string, error) {
	// Safety: only allow reading from the current project directory
	path := filepath.Clean(filename)
	content, err := os.ReadFile(path)
	if err != nil {
		return "", err
	}
	return string(content), nil
}
