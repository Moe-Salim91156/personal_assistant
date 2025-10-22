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
   - For any command that involves opening applications (e.g., "terminal", "vs code", "discord", "slack"), the plugin is "open_apps".
   - Default to "run_scripts" if unsure, but prioritize keywords:
       • run, execute, launch, start, trigger → run_scripts
       • open, launch app, start app, show app → open_apps

2. TARGET RESOLUTION
   Available targets for run_scripts:
     - push      → pushing updates, commits, uploads.
     - cleaner   → deep or advanced cleanup, the default cleaning script.
     - clean     → light cleanup scripts(for 42 cluster devices).
     - ref       → reference viewer, reads or searches docs.
     - export    → exports data or references.
     - todo      → task list management.
     - deploy    → deployment or production pushes.
     - ch_forb   → check forbidden function (internal command).

   Available targets for open_apps (examples, no need to implement yet):
     - terminal
     - vs Code
     - discord
     - slack
     - browser
     - code editors, or any common application name in the input

   Logic hints:
     - If the user input contains words like “ref”, “reference”, or “list my references”, map to plugin="run_scripts", target="ref", args=everything after "ref" or "list".
     - If the user input contains words like “push my code”, “run deploy”, “clean up”, map to corresponding run_scripts target.
     - If the input contains "open", "launch", or mentions app names, map to plugin="open_apps" and target=<app name>.
     - Always prioritize app-specific keywords for open_apps over generic "run" words.

3. ARGS FIELD
   - Always include "args" as a string.
   - If user input contains additional arguments after the main command, include them.
   - If no arguments exist, use an empty string "" (never omit args).

4. OUTPUT
   - Strictly output JSON only.
   - Never include comments, markdown, or explanations.
   - Examples:
     {{
       "plugin": "run_scripts",
       "target": "cleaner",
       "args": ""
     }}
     {{
       "plugin": "run_scripts",
       "target": "ref",
       "args": "list"
     }}
     {{
       "plugin": "open_apps",
       "target": "terminal",
       "args": ""
     }}
     {{
       "plugin": "open_apps",
       "target": "vs Code",
       "args": ""
     }}

5. IMPORTANT
   - Make sure the plugin is **always correct**: either run_scripts or open_apps.
   - Make sure "args" field **always exists**.
   - Do not create plugins that don’t exist yet; just classify correctly.
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
