package planner

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"strings"

	"jarvis/internal/config"
)

type Step struct {
	Intent string // maps to a command keyword
	Args   string // any arguments extracted
}

// Plan takes a complex natural language command and breaks it into
// ordered steps using the LLM. The LLM is ONLY called here.
func Plan(input, context string, cfg config.PlannerConfig) ([]Step, error) {
	prompt := fmt.Sprintf(`You are Jarvis, a personal assistant. 
Break this command into ordered steps. 
Return ONLY a JSON array. No explanation. No markdown.

Available actions: terraform_apply, terraform_plan, terraform_destroy,
docker_up, docker_down, docker_status, push, clean, ref, open_app

Recent context:
%s

Command: "%s"

Return format:
[
  {"intent": "docker_up", "args": ""},
  {"intent": "docker_status", "args": ""}
]`, context, input)

	body, _ := json.Marshal(map[string]any{
		"model":      cfg.Model,
		"prompt":     prompt,
		"stream":     false,
		"format":     "json",
		"keep_alive": cfg.KeepAlive, // 0 = unload after response
	})

	resp, err := http.Post(
		cfg.OllamaURL+"/api/generate",
		"application/json",
		bytes.NewReader(body),
	)
	if err != nil {
		return nil, fmt.Errorf("ollama unreachable: %w", err)
	}
	defer resp.Body.Close()

	var result struct {
		Response string `json:"response"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}

	var steps []Step
	if err := json.Unmarshal([]byte(result.Response), &steps); err != nil {
		return nil, fmt.Errorf("bad plan format: %w", err)
	}

	return steps, nil
}

// Summarize takes raw terminal output and returns a natural spoken sentence.
// Also uses the LLM — called once per complex command completion.
func Summarize(output string, cfg config.PlannerConfig) string {
	if strings.TrimSpace(output) == "" {
		return "Done."
	}

	prompt := fmt.Sprintf(`Summarize this terminal output in one or two 
natural spoken sentences. Be concise. No markdown. No bullet points.

Output:
%s`, output)

	body, _ := json.Marshal(map[string]any{
		"model":      cfg.Model,
		"prompt":     prompt,
		"stream":     false,
		"keep_alive": cfg.KeepAlive,
	})

	resp, err := http.Post(
		cfg.OllamaURL+"/api/generate",
		"application/json",
		bytes.NewReader(body),
	)
	if err != nil {
		return "Done. Check the terminal for details."
	}
	defer resp.Body.Close()

	var result struct {
		Response string `json:"response"`
	}
	json.NewDecoder(resp.Body).Decode(&result)

	if result.Response == "" {
		return "Done."
	}
	return result.Response
}
