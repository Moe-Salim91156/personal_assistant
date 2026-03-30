#!/usr/bin/env python3
import sys
import time
import numpy as np
import pyaudio
from openwakeword.model import Model

CHUNK       = 1280
SAMPLE_RATE = 16000
THRESHOLD   = 0.7
COOLDOWN    = 2.0
WAKE_MODELS = ["hey_jarvis", "jarvis"]

def main():
    oww = Model(wakeword_models=WAKE_MODELS, inference_framework="onnx")
    audio = pyaudio.PyAudio()
    stream = audio.open(
        rate=SAMPLE_RATE, channels=1,
        format=pyaudio.paInt16, input=True,
        frames_per_buffer=CHUNK,
    )

    last_trigger = 0.0
    print("[wake_word] listening...", file=sys.stderr, flush=True)

    while True:
        raw = stream.read(CHUNK, exception_on_overflow=False)
        pcm = np.frombuffer(raw, dtype=np.int16)
        prediction = oww.predict(pcm)

        for model_name, score in prediction.items():
            if score >= THRESHOLD:
                now = time.time()
                if now - last_trigger > COOLDOWN:
                    last_trigger = now
                    print("WAKE", flush=True)
                    oww.reset()
                break

if __name__ == "__main__":
    main()
