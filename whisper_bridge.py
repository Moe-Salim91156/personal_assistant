#!/usr/bin/env python3
import sys
import numpy as np
import torch
import soundfile as sf
from faster_whisper import WhisperModel

_vad_model = None
_vad_utils = None

def get_vad():
    global _vad_model, _vad_utils
    if _vad_model is None:
        _vad_model, _vad_utils = torch.hub.load(
            repo_or_dir="snakers4/silero-vad",
            model="silero_vad",
            force_reload=False,
            onnx=False,
        )
    return _vad_model, _vad_utils

def has_speech(audio_path, threshold=0.4):
    try:
        vad_model, (get_speech_timestamps, _, read_audio, *_) = get_vad()
        wav = read_audio(audio_path, sampling_rate=16000)
        timestamps = get_speech_timestamps(wav, vad_model, threshold=threshold, sampling_rate=16000)
        return len(timestamps) > 0
    except Exception as e:
        print(f"[VAD warning] {e}", file=sys.stderr)
        return True

_whisper_model = None

def get_whisper():
    global _whisper_model
    if _whisper_model is None:
        _whisper_model = WhisperModel(
            "large-v3",
            device="cuda",
            compute_type="float16",
            num_workers=2,
        )
    return _whisper_model

def transcribe(audio_path):
    if not has_speech(audio_path):
        return ""

    model = get_whisper()
    segments, _ = model.transcribe(
        audio_path,
        beam_size=5,
        language="en",
        condition_on_previous_text=False,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=400, speech_pad_ms=200),
        initial_prompt=(
            "Docker, Terraform, containers, git push, commit, "
            "clean, status, deploy, infra, DevOps, engineering."
        ),
    )

    text = " ".join(seg.text for seg in segments).strip().lower()

    hallucinations = {
        "thank you", "thanks for watching", "you", ".", "", "bye",
        "bye.", "thanks.", "thank you.", " ", "...",
    }
    if text in hallucinations:
        return ""

    return text

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    print(transcribe(sys.argv[1]))
