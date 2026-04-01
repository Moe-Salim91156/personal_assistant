#!/bin/bash

# --- 1. Detect OS ---
if [ -f /etc/arch-release ]; then
    PKGMGR="sudo pacman -S --needed --noconfirm"
    DEPS="ffmpeg pkg-config alsa-lib nodejs npm"
elif [ -f /etc/debian_version ]; then
    PKGMGR="sudo apt-get install -y"
    DEPS="ffmpeg pkg-config libasound2-dev nodejs npm"
fi

echo "--- Checking for missing dependencies ---"
$PKGMGR $DEPS

# --- 2. Check for Go (Skip if you already have 1.25+) ---
if ! command -v go &> /dev/null; then
    echo "--- Go not found, installing... ---"
    [ "$DISTRO" == "arch" ] && sudo pacman -S go || sudo apt-get install -y golang
fi

# --- 3. Start Kokoro (Only if not running) ---
if [ ! "$(docker ps -q -f name=kokoro-tts)" ]; then
    echo "--- Starting Kokoro-TTS ---"
    docker run -d -p 8880:8880 --name kokoro-tts ghcr.io/remsky/kokoro-fastapi-cpu:latest
fi

# --- 4. Pull Models (Only if missing) ---
echo "--- Checking Models ---"
ollama list | grep -q "llama3.1:8b" || ollama pull llama3.1:8b

# --- 5. Build Binary ---
echo "--- Building JARVIS ---"
go mod tidy
go build -o jarvis_bin cmd/jarvis/main.go

echo "DONE. Run ./jarvis_bin"
