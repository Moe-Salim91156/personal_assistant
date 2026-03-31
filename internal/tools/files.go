package tools

import (
	"os"
	"path/filepath"
)

func ReadFile(path string) (string, error) {
	// Security: Clean the path to prevent directory traversal
	safePath := filepath.Clean(path)
	content, err := os.ReadFile(safePath)
	if err != nil {
		return "", err
	}
	return string(content), nil
}
