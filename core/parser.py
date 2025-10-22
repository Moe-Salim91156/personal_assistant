# core/parser.py
import requests
import json


def parse_intent_ollama(user_input):
    """
    Uses Ollama API to infer which plugin and script should be executed based on natural language input.
    """
    prompt = f"""
You are an NLP command parser for a modular developer assistant named **Jarvis**.

Your ONLY job is to understand natural language developer commands and produce a single, strictly valid JSON object that determines which plugin and command (script) should run.

Your output **must always be valid JSON** — never text, never markdown, never comments.

---

## 🔧 JSON OUTPUT FORMAT
{{
  "plugin": "<plugin_name>",
  "target": "<command_target>",
  "args": "<optional_arguments>"
}}

---

## 🧩 PLUGINS

1. **run_scripts**  
   Handles all developer-related internal commands and script executions.  
   Used for commands that mention running, cleaning, pushing, deploying, referencing, exporting, listing, or searching.

2. **open_apps**  
   Handles opening or launching system applications like terminal, vs code, browser, discord, slack, etc.

If the intent involves any script or logic command (run, push, clean, ref, etc.), always choose **"run_scripts"**.  
If it involves opening an app, choose **"open_apps"**.

Default to **run_scripts** if unsure.

---

## ⚙️ TARGET RESOLUTION RULES

### 🎯 Targets for `run_scripts`:
| Target  | Intent Keywords or Meanings |
|----------|-----------------------------|
| `push` | push my code, upload, send, commit, deploy my repo |
| `clean` | clean, cleanup, light clean, cluster clean |
| `cleaner` | deep clean, advanced cleanup, full reset |
| `ref` | reference, references, ref, doc, documentation, show, search, find, list |
| `export` | export, save, backup |
| `todo` | tasks, todo list, add task, show todos |
| `deploy` | deploy, production, release |
| `ch_forb` | check forbidden, forbidden functions, 42 forbidden |

---

## 🧠 SPECIAL FOCUS: REF COMMAND LOGIC

Jarvis’s **ref** command has sub-modes depending on the user’s wording.

When detecting “ref” or anything related to references, decide the correct args:

| User Intent Example | Expected Output |
|----------------------|----------------|
| "ref list", "show my references", "list all references" | plugin="run_scripts", target="ref", args="list" |
| "ref vector", "show vector", "fetch http", "open sockets reference" | plugin="run_scripts", target="ref", args="<topic>" |
| "find vector keyword", "search http", "find me std::vector", "search for poll" | plugin="run_scripts", target="ref", args="search <query>" |

⚠️ Always lowercase the args (e.g., "http" not "HTTP").  
⚠️ Never return duplicate words or partial phrases like “show ref”.  
⚠️ Always ensure the “args” field is present — if empty, set to "".

---

## 💡 Examples of correct JSON outputs

**Case 1: simple ref topic**
User: “ref vector”  
→ {{
  "plugin": "run_scripts",
  "target": "ref",
  "args": "vector"
}}

**Case 2: search**
User: “find me std::vector”  
→ {{
  "plugin": "run_scripts",
  "target": "ref",
  "args": "search std::vector"
}}

**Case 3: list**
User: “show my references”  
→ {{
  "plugin": "run_scripts",
  "target": "ref",
  "args": "list"
}}

**Case 4: app opening**
User: “open terminal”  
→ {{
  "plugin": "open_apps",
  "target": "terminal",
  "args": ""
}}

**Case 5: generic script**
User: “run my push script”  
→ {{
  "plugin": "run_scripts",
  "target": "push",
  "args": ""
}}

---

## ⚖️ RULES TO FOLLOW

- Always include all 3 keys: `plugin`, `target`, and `args`.
- Always output **pure JSON only** — no explanations.
- Always lowercase targets and args (unless code keywords like std::vector).
- For “ref” commands, never capitalize HTTP or other protocol names.
- If no clear args exist, set "args": "".
- If multiple targets appear, pick the most relevant (prefer ref > clean > push > todo > deploy).
- Never invent new plugin names.

---

INPUT: "{user_input}"

Now analyze the input carefully and output the correct JSON.
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
            timeout=100,
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
