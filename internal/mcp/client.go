package mcp

import (
	"context"
	// "encoding/json"
	"fmt"
	"os/exec"
	"strings"

	mcp_golang "github.com/metoro-io/mcp-golang"
	"github.com/metoro-io/mcp-golang/transport/stdio"
)

type MCPBridge struct {
	Client *mcp_golang.Client
	cmd    *exec.Cmd
}

func NewBridge(command string, args ...string) (*MCPBridge, error) {
	cmd := exec.Command(command, args...)

	stdin, err := cmd.StdinPipe()
	if err != nil {
		return nil, fmt.Errorf("stdin pipe failed: %w", err)
	}
	stdout, err := cmd.StdoutPipe()
	if err != nil {
		return nil, fmt.Errorf("stdout pipe failed: %w", err)
	}
	if err := cmd.Start(); err != nil {
		return nil, fmt.Errorf("failed to start MCP server: %w", err)
	}

	transport := stdio.NewStdioServerTransportWithIO(stdout, stdin)
	client := mcp_golang.NewClient(transport)

	if _, err := client.Initialize(context.Background()); err != nil {
		cmd.Process.Kill()
		return nil, fmt.Errorf("failed to initialize MCP client: %w", err)
	}

	return &MCPBridge{Client: client, cmd: cmd}, nil
}
func (b *MCPBridge) GetToolsForOllama() []map[string]any {
	// Pass empty string cursor instead of nil to avoid null cursor bug
	cursor := ""
	resp, err := b.Client.ListTools(context.Background(), &cursor)
	if err != nil {
		fmt.Println("ListTools error:", err)
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
func (b *MCPBridge) CallTool(name string, arguments map[string]any) (string, error) {
	resp, err := b.Client.CallTool(context.Background(), name, arguments)
	if err != nil {
		return "", fmt.Errorf("MCP tool %q failed: %w", name, err)
	}
	var sb strings.Builder
	for _, c := range resp.Content {
		if c.TextContent != nil {
			sb.WriteString(c.TextContent.Text)
		}
	}
	return sb.String(), nil
}
func (b *MCPBridge) Stop() {
	if b.cmd != nil && b.cmd.Process != nil {
		b.cmd.Process.Kill()
	}
}
