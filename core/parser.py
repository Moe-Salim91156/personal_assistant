# core/parser.py
import requests
import json


def parse_intent_ollama(user_input):
    """
    Uses Ollama API to infer the intent (plugin) and target (command).
    Example output:
      { "plugin": "run_scripts", "target": "push", "args": "" }
    """
    prompt = f"""
    You are a command parser for a developer assistant.
    Analyze the input: "{user_input}"

    Respond ONLY with JSON (no markdown, no extra text):
    {{
      "plugin": "run_scripts",
      "target": "push",
      "args": ""
    }}

    Available targets: push, clean, cleaner, ref, export, todo, Deploy, ch_forb
    
    Rules:
    - plugin is ALWAYS "run_scripts"
    - target must be ONE of the available targets above
    - If user mentions "push", target is "push" (not "push_script")
    - If user mentions "clean", target is "clean" or "cleaner"
    - args is always an empty string ""
    """
    try:
        # Call Ollama API instead of CLI
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5:0.5b",
                "prompt": prompt,
                "stream": False,
                "format": "json",
            },
            timeout=10,
        )

        if response.status_code != 200:
            print(f"⚠️ Ollama API error: {response.status_code}")
            return None

        result = response.json()
        ollama_output = result.get("response", "")

        data = json.loads(ollama_output)
        return data

    except requests.exceptions.ConnectionError:
        print("⚠️ Ollama server not running. Start it with: ollama serve")
        return None
    except json.JSONDecodeError:
        print("⚠️ Failed to parse Ollama output.")
        return None
    except Exception as e:
        print(f"⚠️ Error: {e}")
        return None
