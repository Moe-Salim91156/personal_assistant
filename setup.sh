#!/bin/bash

# --- 1. System Dependencies (Ubuntu/Debian focus) ---
echo "--- Installing System Dependencies ---"
sudo apt-get update
sudo apt-get install -y curl git build-essential ffmpeg pkg-config libasound2-dev

# --- 2. Install Go (1.21+) if not present ---
if ! command -v go &> /dev/null; then
    echo "--- Installing Go ---"
    GO_VER="1.22.1"
    curl -OL "https://golang.org/dl/go${GO_VER}.linux-amd64.tar.gz"
    sudo tar -C /usr/local -xzf "go${GO_VER}.linux-amd64.tar.gz"
    echo "export PATH=\$PATH:/usr/local/go/bin" >> ~/.bashrc
    export PATH=$PATH:/usr/local/go/bin
    rm "go${GO_VER}.linux-amd64.tar.gz"
fi

# --- 3. Install Docker if not present ---
if ! command -v docker &> /dev/null; then
    echo "--- Installing Docker ---"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
fi

# --- 4. Launch Kokoro TTS (Docker) ---
echo "--- Starting Kokoro-TTS Container ---"
# Check if already running to avoid port conflicts
if [ ! "$(docker ps -q -f name=kokoro-tts)" ]; then
    if [ "$(docker ps -aq -f status=exited -f name=kokoro-tts)" ]; then
        docker rm kokoro-tts
    fi
    docker run -d -p 8880:8880 --name kokoro-tts \
      -e "KOKORO_MODEL=v1.0" \
      ghcr.io/remsky/kokoro-fastapi-cpu:latest
fi

# --- 5. Install Ollama & Pull Llama3.1 ---
echo "--- Setting up Ollama ---"
if ! command -v ollama &> /dev/null; then
    curl -fsSL https://ollama.com/install.sh | sh
fi

# Give Ollama a second to start, then pull models
sleep 5
ollama pull llama3.1:8b
# JARVIS might need a coder model too for better tool use:
# ollama pull qwen2.5-coder:7b

# --- 6. Go Project Dependencies ---
echo "--- Preparing JARVIS ---"
go mod tidy
go build -o jarvis_bin cmd/jarvis/main.go

echo "------------------------------------------------"
echo "SETUP COMPLETE, SIR."
echo "Memory (history.json) will be created on first run."
echo "Please run: ./jarvis_bin"
echo "------------------------------------------------"
