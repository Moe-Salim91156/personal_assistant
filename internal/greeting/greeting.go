package greeting

import (
	"fmt"
	"os/exec"
	"strings"
	"time"

	"jarvis/internal/memory"
)

type SpeakFunc func(string)

// Boot runs once at startup — checks system state, speaks a greeting.
// Runs in a goroutine so it doesn't block Jarvis from becoming ready.
func Boot(mem *memory.Memory, say SpeakFunc) {
	// small delay — let audio system fully initialize
	time.Sleep(2 * time.Second)

	hour := time.Now().Hour()
	greeting := timeGreeting(hour)
	name := "Mohammad" // could come from config later

	var parts []string
	parts = append(parts, fmt.Sprintf("%s, %s.", greeting, name))

	// check docker
	if status := dockerStatus(); status != "" {
		parts = append(parts, status)
	}

	// check terraform
	if status := terraformStatus(); status != "" {
		parts = append(parts, status)
	}

	// recall last session
	if last := mem.LastSession(); last != "" {
		parts = append(parts, "Last session you ran: "+last+".")
	}

	parts = append(parts, "I'm ready for your commands.")

	say(strings.Join(parts, " "))
}

func timeGreeting(hour int) string {
	switch {
	case hour < 12:
		return "Good morning"
	case hour < 17:
		return "Good afternoon"
	default:
		return "Good evening"
	}
}

func dockerStatus() string {
	out, err := exec.Command("docker", "ps", "--format", "{{.Names}}").Output()
	if err != nil {
		return "Docker is not running."
	}

	lines := strings.Split(strings.TrimSpace(string(out)), "\n")
	if len(lines) == 0 || lines[0] == "" {
		return "No docker containers running."
	}

	return fmt.Sprintf("%d docker container%s running.",
		len(lines), plural(len(lines)))
}

func terraformStatus() string {
	// check if there's a known terraform dir in memory
	// for now just check if terraform is available
	out, err := exec.Command("terraform", "version").Output()
	if err != nil {
		return ""
	}
	if strings.Contains(string(out), "Terraform") {
		return "Terraform is available."
	}
	return ""
}

func plural(n int) string {
	if n == 1 {
		return ""
	}
	return "s"
}
