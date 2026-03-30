package brain

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"strings"

	"jarvis/internal/config"
)

type ToolCall struct {
	Tool string            `json:"tool"`
	Args map[string]string `json:"args"`
}

type Decision struct {
	Thought  string     `json:"thought"`
	Tools    []ToolCall `json:"tools"`
	Response string     `json:"response"`
}

const systemPrompt = `You are Jarvis, a highly intelligent personal assistant running locally on Mohammad's PC.
You know Mohammad well and grow smarter about him with every interaction.

You have access to these tools:
- run_command: run a configured command (args: name = command name)
- web_search: search the web (args: query)
- open_app: open an application (args: app = binary or app name)
- docker: control docker (args: action = up/down/status/ps)
- terraform: control terraform (args: action = apply/plan/destroy)
- git_push: add, commit, push (args: message = commit message)
- system_info: get CPU, RAM, GPU, disk info (args: none)
- recall_memory: recall relevant memories (args: query)
- store_preference: store something learned about Mohammad (args: key, value)
- none: respond directly, no tool needed (args: none)

Mohammad's profile and relevant memories:
%s

Recent conversation:
%s

Reply ONLY with valid JSON:
{
  "thought": "brief reasoning",
  "tools": [{"tool": "tool_name", "args": {"key": "value"}}],
  "response": "spoken reply if no tool, else empty string"
}

Rules:
- Use "none" tool + fill "response" for greetings, questions, conversation
- You can chain multiple tools in order
- Be concise and natural — you speak, not write
- Remember details about Mohammad and use them
- If Mohammad shares code, be specific and constructive in feedback`

type Brain struct {
	cfg config.PlannerConfig
}

func New(cfg config.PlannerConfig) *Brain {
	return &Brain{cfg: cfg}
}

func (b *Brain) Think(input, profile, history string) (*Decision, error) {
	prompt := fmt.Sprintf(systemPrompt, profile, history)

	body, _ := json.Marshal(map[string]any{
		"model":  b.cfg.Model,
		"system": prompt,
		"prompt": fmt.Sprintf(`User said: "%s"\n\nRespond with JSON only.`, input),
		"stream":     false,
		"format":     "json",
		"keep_alive": b.cfg.KeepAlive,
		"options": map[string]any{
			"temperature": 0.3,
			"num_predict": 512,
		},
	})

	resp, err := http.Post(
		b.cfg.OllamaURL+"/api/generate",
		"application/json",
		bytes.NewReader(body),
	)
	if err != nil {
		return nil, fmt.Errorf("ollama unreachable: %w", err)
	}
	defer resp.Body.Close()

	var raw struct {
		Response string `json:"response"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&raw); err != nil {
		return nil, fmt.Errorf("decode failed: %w", err)
	}

	cleaned := strings.TrimSpace(raw.Response)
	cleaned = strings.TrimPrefix(cleaned, "```json")
	cleaned = strings.TrimPrefix(cleaned, "```")
	cleaned = strings.TrimSuffix(cleaned, "```")

	var decision Decision
	if err := json.Unmarshal([]byte(cleaned), &decision); err != nil {
		return &Decision{
			Response: raw.Response,
			Tools:    []ToolCall{{Tool: "none"}},
		}, nil
	}

	return &decision, nil
}

// LearnFromInteraction asks the LLM if anything is worth storing in profile
func (b *Brain) LearnFromInteraction(input, response string) (key, value string, shouldStore bool) {
	prompt := fmt.Sprintf(`Did this interaction reveal something worth remembering about the user?
Things worth storing: preferences, habits, tech stack, coding style, projects, tools, corrections.

User said: "%s"
Assistant responded: "%s"

If yes: {"store": true, "key": "short_key", "value": "what to remember"}
If no:  {"store": false}

JSON only.`, input, response)

	body, _ := json.Marshal(map[string]any{
		"model":      b.cfg.Model,
		"prompt":     prompt,
		"stream":     false,
		"format":     "json",
		"keep_alive": b.cfg.KeepAlive,
		"options":    map[string]any{"temperature": 0.1},
	})

	resp, err := http.Post(
		b.cfg.OllamaURL+"/api/generate",
		"application/json",
		bytes.NewReader(body),
	)
	if err != nil {
		return "", "", false
	}
	defer resp.Body.Close()

	var raw struct{ Response string `json:"response"` }
	json.NewDecoder(resp.Body).Decode(&raw)

	var result struct {
		Store bool   `json:"store"`
		Key   string `json:"key"`
		Value string `json:"value"`
	}
	if err := json.Unmarshal([]byte(raw.Response), &result); err != nil {
		return "", "", false
	}

	return result.Key, result.Value, result.Store
}
