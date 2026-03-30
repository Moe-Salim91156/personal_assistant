#!/usr/bin/env python3
import sys, json, hashlib, subprocess
import numpy as np
import soundfile as sf
from pathlib import Path

CACHE_DIR = Path.home() / ".jarvis" / "voice_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_RATE = 24000

_vibevoice = None
_vibevoice_ok = False
_kokoro = None
_kokoro_ok = False

def load_vibevoice():
    global _vibevoice, _vibevoice_ok
    try:
        from vibevoice import VoicePipeline
        _vibevoice = VoicePipeline.from_pretrained(
            "microsoft/VibeVoice-Realtime-0.5B", device="cuda")
        _vibevoice_ok = True
        print("[tts] VibeVoice-Realtime loaded", file=sys.stderr)
    except Exception as e:
        print(f"[tts] VibeVoice failed: {e} — trying Kokoro", file=sys.stderr)
        load_kokoro()

def load_kokoro():
    global _kokoro, _kokoro_ok
    try:
        from kokoro_onnx import Kokoro
        _kokoro = Kokoro(
            model_path=str(Path.home() / ".jarvis" / "kokoro" / "kokoro-v1.0.onnx"),
            voices_path=str(Path.home() / ".jarvis" / "kokoro" / "voices.bin"),
        )
        _kokoro_ok = True
        print("[tts] Kokoro loaded", file=sys.stderr)
    except Exception as e:
        print(f"[tts] Kokoro failed: {e} — will use piper", file=sys.stderr)

def get_or_generate(text):
    key = hashlib.md5(text.strip().lower().encode()).hexdigest()[:12]
    cache_path = CACHE_DIR / f"{key}.wav"
    if cache_path.exists():
        return str(cache_path)

    if _vibevoice_ok:
        try:
            chunks = list(_vibevoice.synthesize_stream(text))
            sf.write(str(cache_path), np.concatenate(chunks), SAMPLE_RATE)
            return str(cache_path)
        except Exception as e:
            print(f"[tts] VibeVoice synthesis failed: {e}", file=sys.stderr)

    if _kokoro_ok:
        try:
            samples, sr = _kokoro.create(text, voice="af_sarah", speed=1.0, lang="en-us")
            sf.write(str(cache_path), samples, sr)
            return str(cache_path)
        except Exception as e:
            print(f"[tts] Kokoro synthesis failed: {e}", file=sys.stderr)

    model = Path.home() / ".jarvis" / "voices" / "en_US-ryan-medium.onnx"
    try:
        r = subprocess.run(["piper-tts", "--model", str(model), "--output_file", str(cache_path)],
                           input=text.encode(), capture_output=True)
        if r.returncode == 0:
            return str(cache_path)
    except Exception:
        pass
    return None

def speak(text):
    text = text.strip()
    if not text:
        return {"ok": True}
    print(f"🔊 Jarvis: {text}", file=sys.stderr, flush=True)
    path = get_or_generate(text)
    if not path:
        return {"ok": False, "error": "all TTS engines failed"}
    subprocess.run(["aplay", "-q", path], check=False)
    return {"ok": True}

def handle(line):
    try:
        req = json.loads(line.strip())
    except Exception as e:
        return {"ok": False, "error": str(e)}
    if req.get("cmd") == "speak":
        return speak(req.get("text", ""))
    return {"ok": False, "error": f"unknown cmd: {req.get('cmd')}"}

def main():
    load_vibevoice()
    print(json.dumps({"ok": True, "data": "tts ready"}), flush=True)
    for line in sys.stdin:
        if line.strip():
            print(json.dumps(handle(line)), flush=True)

if __name__ == "__main__":
    main()
