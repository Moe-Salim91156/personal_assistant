package executor

import (
	"fmt"
	"os/exec"
	"strings"

	"jarvis/internal/config"
)

func Run(cmd *config.Command, args string) (string, error) {
	var out []byte
	var err error

	switch cmd.Plugin {
	case "scripts":
		if strings.HasSuffix(cmd.Script, ".sh") {
			out, err = exec.Command("bash", cmd.Script, args).CombinedOutput()
		} else if strings.HasSuffix(cmd.Script, ".py") {
			out, err = exec.Command("python3", cmd.Script, args).CombinedOutput()
		}
	case "docker":
		out, err = exec.Command("docker", cmd.Action).CombinedOutput()
	case "terraform":
		out, err = exec.Command("terraform", cmd.Action, "-auto-approve").CombinedOutput()
	default:
		return "Unknown plugin type", fmt.Errorf("plugin %s not supported", cmd.Plugin)
	}

	if err != nil {
		return string(out), fmt.Errorf("execution failed: %v", err)
	}
	return string(out), nil
}

// RunRaw runs an arbitrary shell command — used by brain tool executor
func RunRaw(name string, args ...string) (string, error) {
	out, err := exec.Command(name, args...).CombinedOutput()
	if err != nil {
		return string(out), fmt.Errorf("command failed: %v", err)
	}
	return string(out), nil
}
