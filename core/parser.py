# core/parser.py
import requests
import json


def parse_intent_ollama(user_input):
    """
    Uses Ollama API to infer which plugin and script should be executed based on natural language input.
    """
    prompt = f"""
You are an advanced NLP-based command parser for a modular developer assistant called Jarvis. Your goal is to **always accurately determine the plugin, target, and args** for user commands.

INPUT: "{user_input}"

Respond ONLY with JSON. No markdown, no explanations, no extra text.

JSON STRUCTURE:
{{
  "plugin": "<plugin_name>",       # Must be "run_scripts" or "open_apps"
  "target": "<command_target>",    # Exact command to execute
  "args": "<optional_arguments>"   # Always a string, never omitted
}}

RULES:

1. PLUGIN SELECTION
  1.1 **Reference-related commands** (highest priority):
      - Keywords: ref, reference, references, list references, list my references
      - Action words: fetch, show, get, open, please, me, the → all **strip** from args
      - **Search commands**: if input contains "search" or "find", args = "search <topic>"
          Examples:
            • "find vector keyword" → args="search vector"
            • "find me std::vector" → args="search std::vector"
            • "search HTTP requests" → args="search HTTP requests"
      - **View commands**: if input contains "fetch", "show", "get", "open" → args = "<topic>"
          Examples:
            • "fetch HTTP" → args="HTTP"
            • "show vectors" → args="vectors"
            • "get webserv reference" → args="webserv"
      - **Listing commands**: "list all references", "list my references", "list references" → args="list"
      - **Important**: Preserve exact topic capitalization (HTTP, std::vector, etc.)
      - Normalize common typos: "refrence" → "reference"

  1.2 **Export commands**
      - Keyword: export
      - Syntax: "export <reference_name>" → plugin="run_scripts", target="export", args="<reference_name>"

  1.3 **Other run_scripts commands**
      - push → target="push"
      - clean → target="clean"
      - cleaner → target="cleaner"
      - todo → target="todo"
      - deploy → target="deploy"
      - ch_forb → target="ch_forb"
      - Default: run, execute, launch, start, trigger → plugin="run_scripts"
      - Args = remaining text after command, else ""

  1.4 **Open_apps commands**
      - Keywords: open, launch app, start app, show app
      - App names: terminal, vs code, code, discord, slack, browser, visual studio
      - If detected → plugin="open_apps", target="<app_name>", args=""

2. TARGET RESOLUTION
  - For ref commands → target="ref", args determined above
  - For export commands → target="export", args=reference name
  - For other scripts → map exactly as above
  - For open_apps → target = normalized app name

3. ARGS FIELD
  - Always include as a string
  - Never include filler words in args
  - Always preserve user capitalization in topic names

4. PRIORITY & DISAMBIGUATION
  1. Detect ref/reference commands first
  2. Detect export commands second
  3. Detect other scripts (push, clean, cleaner, todo, deploy, ch_forb)
  4. Detect open apps last
  5. Default → plugin="run_scripts", target inferred from keywords if possible, args=remaining

5. EXAMPLES (all valid JSON):
  {{
    "plugin": "run_scripts",
    "target": "ref",
    "args": "vectors"
  }}
  {{
    "plugin": "run_scripts",
    "target": "ref",
    "args": "HTTP"
  }}
  {{
    "plugin": "run_scripts",
    "target": "ref",
    "args": "search std::vector"
  }}
  {{
    "plugin": "run_scripts",
    "target": "ref",
    "args": "list"
  }}
  {{
    "plugin": "run_scripts",
    "target": "export",
    "args": "webserv"
  }}
  {{
    "plugin": "run_scripts",
    "target": "cleaner",
    "args": ""
  }}
  {{
    "plugin": "open_apps",
    "target": "vs code",
    "args": ""
  }}
  {{
    "plugin": "open_apps",
    "target": "terminal",
    "args": ""
  }}

6. IMPORTANT NOTES
  - Plugin must always be "run_scripts" or "open_apps"
  - Target must always be accurate
  - Args must always exist and reflect exactly what the user wants
  - Ref command edge cases must always map correctly:
      • fetch/show/get/open → ref <topic>
      • find/search → ref search <topic>
      • list → ref list
  - Preserve capitalization of topics
  - Strip filler/action words only from args
  - No unknown plugins or targets allowed
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
