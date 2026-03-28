#!/bin/bash
# =============================================================================
# Jarvis — dependency installer & checker
# Uses uv for fast Python package management
# =============================================================================

set -e

BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
RESET="\033[0m"

ok()   { echo -e "  ${GREEN}✓${RESET} $1"; }
warn() { echo -e "  ${YELLOW}⚠${RESET}  $1"; }
fail() { echo -e "  ${RED}✗${RESET} $1"; }
header() { echo -e "\n${BOLD}$1${RESET}"; }

ERRORS=0

# =============================================================================
# 1. uv
# =============================================================================
header "[ 1/5 ] uv"

if ! command -v uv &>/dev/null; then
    echo "  installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
    ok "uv installed"
else
    ok "uv $(uv --version)"
fi

# =============================================================================
# 2. system packages
# =============================================================================
header "[ 2/5 ] system packages"

SYS_DEPS=(ffmpeg arecord aplay piper-tts)
MISSING_SYS=()

for dep in "${SYS_DEPS[@]}"; do
    if command -v "$dep" &>/dev/null; then
        ok "$dep"
    else
        fail "$dep not found"
        MISSING_SYS+=("$dep")
        ERRORS=$((ERRORS + 1))
    fi
done

if [ ${#MISSING_SYS[@]} -gt 0 ]; then
    echo ""
    warn "Install missing system packages with:"
    # arecord/aplay come from alsa-utils, piper-tts is manual
    echo "    sudo apt install alsa-utils ffmpeg"
    if [[ " ${MISSING_SYS[*]} " == *"piper-tts"* ]]; then
        echo "    # piper-tts: https://github.com/rhasspy/piper/releases"
    fi
fi

# =============================================================================
# 3. Python + venv via uv
# =============================================================================
header "[ 3/5 ] Python environment"

VENV_DIR="$HOME/.jarvis/.venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "  creating venv at $VENV_DIR..."
    uv venv "$VENV_DIR" --python 3.11
    ok "venv created"
else
    ok "venv exists at $VENV_DIR"
fi

# activate for the rest of this script
source "$VENV_DIR/bin/activate"

# =============================================================================
# 4. Python packages
# =============================================================================
header "[ 4/5 ] Python packages"

# torch with CUDA 12.1 — matches RTX 2060 driver stack on modern Ubuntu
echo "  installing torch (CUDA 12.1)..."
uv pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121 --quiet
ok "torch + torchaudio"

echo "  installing faster-whisper, silero-vad, soundfile..."
uv pip install \
    faster-whisper \
    silero-vad \
    soundfile \
    --quiet
ok "faster-whisper, silero-vad, soundfile"

# =============================================================================
# 5. checks
# =============================================================================
header "[ 5/5 ] checks"

# CUDA
CUDA_OK=$(python3 - <<'EOF'
import torch
print("yes" if torch.cuda.is_available() else "no")
EOF
)
if [ "$CUDA_OK" = "yes" ]; then
    GPU=$(python3 -c "import torch; print(torch.cuda.get_device_name(0))")
    ok "CUDA available — $GPU"
else
    fail "CUDA not available — torch will use CPU (Whisper large-v3 will be slow)"
    warn "Fix: make sure nvidia drivers are loaded: nvidia-smi"
    warn "     and reinstall torch for the correct CUDA version"
    ERRORS=$((ERRORS + 1))
fi

# faster-whisper import
python3 -c "from faster_whisper import WhisperModel" 2>/dev/null \
    && ok "faster-whisper importable" \
    || { fail "faster-whisper import failed"; ERRORS=$((ERRORS + 1)); }

# silero-vad import
python3 -c "import torch; torch.hub.load('snakers4/silero-vad', 'silero_vad', verbose=False)" 2>/dev/null \
    && ok "silero-vad loadable" \
    || { warn "silero-vad hub model will download on first Jarvis run"; }

# soundfile
python3 -c "import soundfile" 2>/dev/null \
    && ok "soundfile importable" \
    || { fail "soundfile import failed"; ERRORS=$((ERRORS + 1)); }

# ffmpeg
ffmpeg -version &>/dev/null \
    && ok "ffmpeg works" \
    || { fail "ffmpeg not working"; ERRORS=$((ERRORS + 1)); }

# arecord
arecord --version &>/dev/null \
    && ok "arecord works" \
    || { fail "arecord not found — install alsa-utils"; ERRORS=$((ERRORS + 1)); }

# piper-tts voice model
VOICE="$HOME/.jarvis/voices/en_US-ryan-medium.onnx"
if [ -f "$VOICE" ]; then
    ok "piper voice model found"
else
    fail "piper voice model not found at $VOICE"
    warn "Download from: https://huggingface.co/rhasspy/piper-voices/tree/main/en/en_US/ryan/medium"
    ERRORS=$((ERRORS + 1))
fi

# patch whisper_bridge.py shebang to use the venv python
BRIDGE="$(dirname "$0")/whisper_bridge.py"
if [ -f "$BRIDGE" ]; then
    sed -i "1s|.*|#!$VENV_DIR/bin/python3|" "$BRIDGE"
    ok "whisper_bridge.py shebang patched to use venv"
else
    warn "whisper_bridge.py not found at $BRIDGE — skipping shebang patch"
fi

# =============================================================================
# summary
# =============================================================================
echo ""
if [ "$ERRORS" -eq 0 ]; then
    echo -e "${GREEN}${BOLD}All checks passed. Run Jarvis with:${RESET}"
    echo "    go build -o jarvis . && ./jarvis"
else
    echo -e "${RED}${BOLD}$ERRORS issue(s) found. Fix them before running Jarvis.${RESET}"
    exit 1
fi
