package mcp

import (
	"context"
	"fmt"

	"github.com/metoro-io/mcp-golang"
	"github.com/metoro-io/mcp-golang/transport/stdio"
)

type MCPBridge struct {
	Client *mcp_golang.Client
}

// NewBridge starts the MCP server (npx) and connects to it
func NewBridge(command string, args ...string) (*MCPBridge, error) {
	// 1. Create the Stdio transport
	t := stdio.NewStdioTransport(command, args...)

	// 2. Create the MCP Client using that transport
	client := mcp_golang.NewClient(t)

	// 3. Initialize the connection
	err := client.Initialize(context.Background())
	if err != nil {
		return nil, fmt.Errorf("failed to initialize MCP client: %w", err)
	}

	return &MCPBridge{Client: client}, nil
}

// GetToolsForOllama translates MCP tools into Ollama-friendly JSON
func (b *MCPBridge) GetToolsForOllama() []map[string]any {
	resp, err := b.Client.ListTools(context.Background(), nil)
	if err != nil {
		return nil
	}

	var ollamaTools []map[string]any
	for _, t := range resp.Tools {
		ollamaTools = append(ollamaTools, map[string]any{
			"type": "function",
			"function": map[string]any{
				"name":        t.Name,
				"description": t.Description,
				"parameters":  t.InputSchema,
			},
		})
	}
	return ollamaTools
}
