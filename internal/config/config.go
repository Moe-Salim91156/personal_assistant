package config

import (
	"os"
	"gopkg.in/yaml.v3"
)

type Config struct {
	Hotkey   string             `yaml:"hotkey"`
	Commands map[string]Command `yaml:"commands"`
	Planner  PlannerConfig      `yaml:"planner"`
}

type Command struct {
	Plugin         string   `yaml:"plugin"`
	Script         string   `yaml:"script"`
	Keywords       []string `yaml:"keywords"`
	SpeechTemplate string   `yaml:"speech_template"`
	Action         string   `yaml:"action"`
	HasArgs        bool     `yaml:"has_args"`
}

type PlannerConfig struct {
	Model     string   `yaml:"model"`
	OllamaURL string   `yaml:"ollama_url"`
	KeepAlive int      `yaml:"keep_alive"`
	Triggers  []string `yaml:"triggers"`
}

func Load(path string) (*Config, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	var cfg Config
	err = yaml.NewDecoder(f).Decode(&cfg)
	return &cfg, err
}
