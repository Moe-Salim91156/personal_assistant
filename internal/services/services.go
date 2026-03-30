package services

import (
	"bufio"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"sync"
)

type Service struct {
	name   string
	cmd    *exec.Cmd
	stdin  io.WriteCloser
	reader *bufio.Reader
	mu     sync.Mutex
}

type rpcResp struct {
	Ok    bool            `json:"ok"`
	Data  json.RawMessage `json:"data"`
	Error string          `json:"error"`
}

func startService(name, script string) (*Service, error) {
	home, _ := os.UserHomeDir()
	venv := filepath.Join(home, ".jarvis", ".venv", "bin", "python3")

	python := venv
	if _, err := os.Stat(venv); err != nil {
		python = "python3"
	}

	cmd := exec.Command(python, script)
	cmd.Stderr = os.Stderr

	stdin, err := cmd.StdinPipe()
	if err != nil {
		return nil, err
	}
	stdout, err := cmd.StdoutPipe()
	if err != nil {
		return nil, err
	}
	if err := cmd.Start(); err != nil {
		return nil, fmt.Errorf("start %s: %w", name, err)
	}

	svc := &Service{
		name:   name,
		cmd:    cmd,
		stdin:  stdin,
		reader: bufio.NewReader(stdout),
	}

	resp, err := svc.read()
	if err != nil || !resp.Ok {
		return nil, fmt.Errorf("%s not ready", name)
	}

	fmt.Printf("✓ %s ready\n", name)
	return svc, nil
}

func (s *Service) Call(req map[string]any) (*rpcResp, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	data, _ := json.Marshal(req)
	fmt.Fprintf(s.stdin, "%s\n", data)
	return s.read()
}

func (s *Service) read() (*rpcResp, error) {
	line, err := s.reader.ReadString('\n')
	if err != nil {
		return nil, err
	}
	var resp rpcResp
	json.Unmarshal([]byte(strings.TrimSpace(line)), &resp)
	return &resp, nil
}

func (s *Service) Close() {
	s.stdin.Close()
	s.cmd.Wait()
}

// ---------------------------------------------------------------------------
// Manager
// ---------------------------------------------------------------------------

type Manager struct {
	TTS    *Service
	Memory *Service
	Search *Service
}

func NewManager() (*Manager, error) {
	home, _ := os.UserHomeDir()
	jarvisDir := filepath.Join(home, ".jarvis")

	m := &Manager{}
	var err error

	m.TTS, err = startService("tts", filepath.Join(jarvisDir, "tts.py"))
	if err != nil {
		return nil, fmt.Errorf("TTS service failed: %w", err)
	}

	m.Memory, err = startService("memory", filepath.Join(jarvisDir, "memory_service.py"))
	if err != nil {
		return nil, fmt.Errorf("memory service failed: %w", err)
	}

	m.Search, err = startService("search", filepath.Join(jarvisDir, "search.py"))
	if err != nil {
		fmt.Println("⚠  search service unavailable (is SearXNG running?)")
		m.Search = nil
	}

	return m, nil
}

// ---------------------------------------------------------------------------
// TTS
// ---------------------------------------------------------------------------

func (m *Manager) Say(text string) {
	if strings.TrimSpace(text) == "" {
		return
	}
	fmt.Printf("🔊 Jarvis: %s\n", text)
	if m.TTS != nil {
		m.TTS.Call(map[string]any{"cmd": "speak", "text": text})
	}
}

// ---------------------------------------------------------------------------
// Memory
// ---------------------------------------------------------------------------

func (m *Manager) MemoryStore(text, kind string) {
	if m.Memory == nil {
		return
	}
	m.Memory.Call(map[string]any{"cmd": "store", "text": text, "kind": kind})
}

func (m *Manager) MemoryRecall(query string, n int) string {
	if m.Memory == nil {
		return ""
	}
	resp, err := m.Memory.Call(map[string]any{"cmd": "recall", "query": query, "n": n})
	if err != nil || !resp.Ok {
		return ""
	}

	var entries []struct {
		Text      string  `json:"text"`
		Kind      string  `json:"kind"`
		Relevance float64 `json:"relevance"`
	}
	json.Unmarshal(resp.Data, &entries)

	var parts []string
	for _, e := range entries {
		if e.Relevance > 0.4 {
			parts = append(parts, fmt.Sprintf("[%s] %s", e.Kind, e.Text))
		}
	}
	return strings.Join(parts, "\n")
}

func (m *Manager) ProfileStore(key, value string) {
	if m.Memory == nil {
		return
	}
	m.Memory.Call(map[string]any{"cmd": "store_profile", "key": key, "value": value})
}

func (m *Manager) ProfileGet() string {
	if m.Memory == nil {
		return ""
	}
	resp, err := m.Memory.Call(map[string]any{"cmd": "get_profile"})
	if err != nil || !resp.Ok {
		return ""
	}

	var entries []struct {
		Key   string `json:"key"`
		Value string `json:"value"`
	}
	json.Unmarshal(resp.Data, &entries)

	var parts []string
	for _, e := range entries {
		parts = append(parts, fmt.Sprintf("%s: %s", e.Key, e.Value))
	}
	return strings.Join(parts, "\n")
}

// ---------------------------------------------------------------------------
// Search
// ---------------------------------------------------------------------------

func (m *Manager) WebSearch(query string) string {
	if m.Search == nil {
		return "Web search is unavailable. SearXNG may not be running."
	}
	resp, err := m.Search.Call(map[string]any{"cmd": "search", "query": query, "n": 3})
	if err != nil || !resp.Ok {
		return "Search failed."
	}

	var data struct {
		Summary string `json:"summary"`
		Error   string `json:"error"`
	}
	json.Unmarshal(resp.Data, &data)

	if data.Error != "" {
		return "Search returned no results."
	}
	return data.Summary
}

func (m *Manager) Close() {
	if m.TTS != nil {
		m.TTS.Close()
	}
	if m.Memory != nil {
		m.Memory.Close()
	}
	if m.Search != nil {
		m.Search.Close()
	}
}
