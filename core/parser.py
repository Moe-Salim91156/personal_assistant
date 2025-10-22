# core/parser.py
import requests
import json


def parse_intent_ollama(user_input):
    """
    Uses Ollama API to infer which plugin and script should be executed based on natural language input.
    """
    prompt = f"""
You are an NLP-based command parser for a modular developer assistant called Jarvis.

Your task: interpret the user's input and output a single JSON object that determines which plugin and command (script) should be executed.

INPUT: "{user_input}"

Respond ONLY with JSON, no explanations, no markdown.

JSON STRUCTURE:
{{
  "plugin": "<plugin_name>",
  "target": "<command_target>",
  "args": "<optional_arguments>"
}}

RULES AND CONTEXT:

1. PLUGIN SELECTION
   - For any command that involves running scripts (bash or python), the plugin is "run_scripts".
   - Assume "run_scripts" unless explicitly stated otherwise.

2. TARGET RESOLUTION
   Available targets:
     - push      → related to pushing updates, commits, or uploads.
     - clean     → light cleanup scripts.
     - cleaner   → deep or advanced cleanup.
     - ref       → reference viewer, reads or searches docs.
     - export    → exports data or references.
     - todo      → task list management.
     - deploy    → deployment or production pushes.
     - ch_forb   → change forbidden flag (special internal command).

   Logic hints:
     - If the user says things like “run”, “execute”, “launch”, “trigger”, or “start”, treat that as intent to run a script.
     - Match approximate synonyms (e.g., “cleanup” → “cleaner”, “push my code” → “push”, “show references” → “ref”).
     - If both “clean” and “deep” are mentioned, use “cleaner”.
     - “ref” and “reference” refer to Python scripts; same for “export”.
     - Everything else (push, clean, cleaner, todo, deploy, ch_forb) are Bash scripts.

3. ARGS FIELD
   - Always include "args" as a string. 
   - If user input contains additional arguments after the command, include them.
   - Example: “run push with force” → {{"plugin": "run_scripts", "target": "push", "args": "with force"}}
   - If no arguments, use an empty string "".

4. OUTPUT
   - Strictly output JSON (no markdown, no explanation).
   - Never include comments or trailing commas.
   - Example valid output:
     {{
       "plugin": "run_scripts",
       "target": "cleaner",
       "args": ""
     }}
"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5:3b",  # or "mistral:7b" for better parsing accuracy
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
