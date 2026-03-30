#!/bin/bash
set -e

BOLD="\033[1m"; GREEN="\033[0;32m"; YELLOW="\033[0;33m"; RED="\033[0;31m"; CYAN="\033[0;36m"; RESET="\033[0m"
ok()     { echo -e "  ${GREEN}✓${RESET} $1"; }
warn()   { echo -e "  ${YELLOW}⚠${RESET}  $1"; }
fail()   { echo -e "  ${RED}✗${RESET} $1"; ERRORS=$((ERRORS+1)); }
header() { echo -e "\n${BOLD}${CYAN}$1${RESET}"; }

ERRORS=0
JARVIS_DIR="$HOME/.jarvis"
VENV="$JARVIS_DIR/.venv"
mkdir -p "$JARVIS_DIR/voices" "$JARVIS_DIR/kokoro" "$JARVIS_DIR/voice_cache"

# 1. uv
header "[ 1/7 ] uv"
if ! command -v uv &>/dev/null; then
    echo "  installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
fi
ok "uv $(uv --version)"

# 2. system packages
header "[ 2/7 ] system packages"
MISSING=()
for dep in ffmpeg arecord aplay docker ollama; do
    command -v "$dep" &>/dev/null && ok "$dep" || { fail "$dep not found"; MISSING+=("$dep"); }
done
[ ${#MISSING[@]} -gt 0 ] && warn "sudo apt install alsa-utils ffmpeg docker.io  |  ollama: curl -fsSL https://ollama.com/install.sh | sh"

# 3. Ollama model
header "[ 3/7 ] Ollama — llama3.1:8b"
if command -v ollama &>/dev/null; then
    if ollama list 2>/dev/null | grep -q "llama3.1:8b"; then
        ok "llama3.1:8b already pulled"
    else
        echo "  pulling llama3.1:8b (~5 GB)..."
        ollama pull llama3.1:8b && ok "llama3.1:8b pulled" || fail "pull failed"
    fi
else
    warn "ollama not installed — skipping"
fi

# 4. Python venv
header "[ 4/7 ] Python venv"
[ ! -d "$VENV" ] && uv venv "$VENV" --python 3.11
ok "venv at $VENV"
source "$VENV/bin/activate"

# 5. Python packages
header "[ 5/7 ] Python packages"
echo "  torch (CUDA 12.1)..."
uv pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121 --quiet
ok "torch + torchaudio"

echo "  all other packages..."
uv pip install \
    faster-whisper silero-vad soundfile pyaudio \
    openwakeword chromadb sentence-transformers \
    requests beautifulsoup4 kokoro-onnx vibevoice \
    --quiet
ok "all packages installed"

# 6. Models
header "[ 6/7 ] models"
KOKORO_MODEL="$JARVIS_DIR/kokoro/kokoro-v1.0.onnx"
KOKORO_VOICES="$JARVIS_DIR/kokoro/voices.bin"
if [ -f "$KOKORO_MODEL" ] && [ -f "$KOKORO_VOICES" ]; then
    ok "Kokoro model files found"
else
    echo "  downloading Kokoro (~80 MB)..."
    python3 - <<'EOF'
import urllib.request
from pathlib import Path
base = Path.home() / ".jarvis" / "kokoro"
base.mkdir(parents=True, exist_ok=True)
files = {
    "kokoro-v1.0.onnx": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/kokoro-v1.0.onnx",
    "voices.bin":        "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/voices.bin",
}
for name, url in files.items():
    dest = base / name
    if not dest.exists():
        print(f"  {name}...")
        urllib.request.urlretrieve(url, dest)
EOF
    [ -f "$KOKORO_MODEL" ] && ok "Kokoro downloaded" || warn "Kokoro download failed — download manually from github.com/thewh1teagle/kokoro-onnx/releases"
fi

echo "  downloading openwakeword models..."
python3 -c "import openwakeword; openwakeword.utils.download_models()" 2>/dev/null \
    && ok "openwakeword models" || warn "will download on first run"

# 7. SearXNG
header "[ 7/7 ] SearXNG"
if command -v docker &>/dev/null; then
    if docker ps 2>/dev/null | grep -q searxng; then
        ok "SearXNG already running"
    else
        docker run -d --name searxng --restart unless-stopped \
            -p 8888:8080 \
            -e BASE_URL="http://localhost:8888/" \
            -e INSTANCE_NAME="jarvis-search" \
            searxng/searxng:latest 2>/dev/null \
        && ok "SearXNG started at http://localhost:8888" \
        || warn "SearXNG failed — web search disabled"
    fi
else
    warn "Docker not available — web search disabled"
fi

# copy Python scripts to ~/.jarvis/ and patch shebang
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
for script in wake_word.py memory_service.py search.py tts.py whisper_bridge.py; do
    if [ -f "$SCRIPT_DIR/$script" ]; then
        cp "$SCRIPT_DIR/$script" "$JARVIS_DIR/$script"
        sed -i "1s|.*|#!$VENV/bin/python3|" "$JARVIS_DIR/$script"
        ok "installed $script"
    else
        warn "$script not found"
    fi
done

# final checks
header "checks"
CUDA=$(python3 -c "import torch; print('yes' if torch.cuda.is_available() else 'no')" 2>/dev/null)
if [ "$CUDA" = "yes" ]; then
    GPU=$(python3 -c "import torch; print(torch.cuda.get_device_name(0))" 2>/dev/null)
    ok "CUDA — $GPU"
else
    fail "CUDA not available — check: nvidia-smi"
fi

python3 -c "from faster_whisper import WhisperModel" 2>/dev/null && ok "faster-whisper" || fail "faster-whisper broken"
python3 -c "import chromadb"                          2>/dev/null && ok "chromadb"       || fail "chromadb broken"
python3 -c "from kokoro_onnx import Kokoro"           2>/dev/null && ok "kokoro-onnx"    || fail "kokoro-onnx broken"
python3 -c "import openwakeword"                      2>/dev/null && ok "openwakeword"   || fail "openwakeword broken"

echo ""
if [ "$ERRORS" -eq 0 ]; then
    echo -e "${GREEN}${BOLD}✅ All good. Build and run:${RESET}"
    echo ""
    echo "    go mod tidy && go build -o jarvis . && ./jarvis"
    echo ""
else
    echo -e "${RED}${BOLD}$ERRORS issue(s) found. Fix before running.${RESET}"
    exit 1
fi
