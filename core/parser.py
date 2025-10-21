# core/intent_parser.py
import subprocess
import json

def parse_intent_ollama(user_input):
    """
    Uses Ollama locally to infer the intent (plugin) and target (command).
    Example output:
      { "plugin": "run_scripts", "target": "push", "args": "" }
    """

    prompt = f"""
    You are a command parser for a developer assistant.
    Analyze the input: "{user_input}"

    Respond ONLY with JSON:
    {{
      "plugin": "<plugin_name>",
      "target": "<command_target>",
      "args": "<any extra args>"
    }}

    - If it's about running scripts (like clean, push, ref, export), plugin is "run_scripts".
    - If it's about opening apps (VSCode, terminal, etc.), plugin is "open_apps".
    """

    # Call Ollama
    result = subprocess.run(
        ["ollama", "run", "llama3", "--json"],
        input=prompt,
        text=True,
        capture_output=True
    )

    try:
        data = json.loads(result.stdout)
        return data
    except json.JSONDecodeError:
        print("⚠️ Failed to parse Ollama output.")
        return None



# def parse_intent(text):
#     """
#     for now this is a functionting prototype. 

#     later ollama will handle the parsing thing and return the dictionary -> {action: $ACTION, target: $TARGET}

#     """
#     text_lower = text.lower()
#     if text_lower.startswith("run") or text_lower.endswith(".sh") or text_lower.endswith(".py"):
#         target = text_lower.split()[-1]
#         return {"action": "run_scripts", "target": target}

#     # if "ref" in text_lower:
#     #     return {"intent": "ref", "target": None}

#     # if "export" in text_lower:
#     #     return {"intent": "export", "target": None}
#     return {"action": None, "target": None}

