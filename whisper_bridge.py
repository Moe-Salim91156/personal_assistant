import sys
from faster_whisper import WhisperModel

# Use 'base' for better noise handling
model = WhisperModel("base", device="cpu", compute_type="int8")

def transcribe(audio_path):
    # The 'initial_prompt' is the secret sauce here. 
    # It tells the AI: "Expect these technical words."
    segments, _ = model.transcribe(
        audio_path, 
        beam_size=5,
        initial_prompt="Docker, Terraform, containers, status, clean, 42, engineering, DevOps."
    )
    
    text = " ".join([segment.text for segment in segments])
    # Print the raw text so we can see it in the console
    print(text.strip().lower())

if __name__ == "__main__":
    if len(sys.argv) > 1:
        transcribe(sys.argv[1])
