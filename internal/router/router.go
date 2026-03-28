package router

import (
	"strings"

	"jarvis/internal/config"
	"jarvis/internal/executor"
	"jarvis/internal/memory"
	"jarvis/internal/planner"
)

type Result struct {
	Speech  string // what Jarvis says back
	Output  string // raw terminal output
	Success bool
}

type Router struct {
	cfg *config.Config
	mem *memory.Memory
}

func New(cfg *config.Config, mem *memory.Memory) *Router {
	return &Router{cfg: cfg, mem: mem}
}

func (r *Router) Handle(input string) Result {
	lower := strings.ToLower(strings.TrimSpace(input))

	// --- shortcircuits first (no LLM ever) ---
	if lower == "" {
		return Result{Speech: "I didn't hear anything."}
	}
	if contains(lower, "what did i do", "last session", "what was i doing") {
		return r.recallLastSession()
	}
	if contains(lower, "run it again", "do it again", "repeat that") {
		return r.repeatLast()
	}

	// --- check if complex multi-step command ---
	if r.isComplex(lower) {
		return r.handleComplex(input)
	}

	// --- simple keyword match ---
	cmd := r.matchKeyword(lower)
	if cmd != nil {
		out, err := executor.Run(cmd, extractArgs(lower, cmd))
		speech := cmd.SpeechTemplate
		if err != nil {
			speech = "Something went wrong. Check the terminal."
		}
		return Result{Speech: speech, Output: out, Success: err == nil}
	}

	// --- nothing matched ---
	return Result{
		Speech: "I'm not sure what you mean. Could you rephrase that?",
	}
}

func (r *Router) isComplex(input string) bool {
	for _, trigger := range r.cfg.Planner.Triggers {
		if strings.Contains(input, trigger) {
			return true
		}
	}
	return false
}

func (r *Router) handleComplex(input string) Result {
	// build context from memory for better planning
	ctx := r.mem.RecentContext(5)

	steps, err := planner.Plan(input, ctx, r.cfg.Planner)
	if err != nil {
		return Result{Speech: "I couldn't plan that out. Try breaking it into separate commands."}
	}

	var finalOutput strings.Builder
	for i, step := range steps {
		cmd := r.matchKeyword(strings.ToLower(step.Intent))
		if cmd == nil {
			continue
		}

		out, err := executor.Run(cmd, step.Args)
		finalOutput.WriteString(out)

		if err != nil {
			return Result{
				Speech:  "Step " + string(rune('1'+i)) + " failed. " + cmd.SpeechTemplate,
				Output:  finalOutput.String(),
				Success: false,
			}
		}
	}

	// summarize the full output naturally
	summary := planner.Summarize(finalOutput.String(), r.cfg.Planner)
	return Result{Speech: summary, Output: finalOutput.String(), Success: true}
}

func (r *Router) matchKeyword(input string) *config.Command {
	for _, cmd := range r.cfg.Commands {
		for _, kw := range cmd.Keywords {
			if strings.Contains(input, kw) {
				return &cmd
			}
		}
	}
	return nil
}

func (r *Router) recallLastSession() Result {
	last := r.mem.LastSession()
	if last == "" {
		return Result{Speech: "I don't have any memory of a previous session yet."}
	}
	return Result{Speech: "Last session: " + last}
}

func (r *Router) repeatLast() Result {
	last := r.mem.LastCommand()
	if last == nil {
		return Result{Speech: "I don't remember your last command."}
	}
	return r.Handle(last.Input)
}

func contains(s string, candidates ...string) bool {
	for _, c := range candidates {
		if strings.Contains(s, c) {
			return true
		}
	}
	return false
}

func extractArgs(input string, cmd *config.Command) string {
	if !cmd.HasArgs {
		return ""
	}
	for _, kw := range cmd.Keywords {
		if idx := strings.Index(input, kw); idx != -1 {
			return strings.TrimSpace(input[idx+len(kw):])
		}
	}
	return ""
}
