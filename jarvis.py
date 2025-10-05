import subprocess
import yaml
import os
import signal
from prompt_toolkit import prompt
def open_yaml():
    with open("commands.yaml") as f:
        commands = yaml.safe_load(f)
    return commands

def check_command(text):
    commands = open_yaml()

    for key in sorted(commands, key=len, reverse=True):
        if text.startswith(key):
            args = text[len(key):].strip()
            return key, args, commands
    return None, None, None

def run_command(commands, cmd_key, args_text):
    """
    Execute the script associated with the matched command.
    """
    cmd_info = commands[cmd_key]
    script_path = cmd_info["script"]
    placeholders = cmd_info.get("args", [])

    # Simple: pass remaining text if placeholders exist
    args = [args_text] if placeholders else []

    # Run the script
    result = subprocess.run(
        ["python3", script_path] + args,
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print(result.stdout.strip())
    else:
        print("Error:", result.stderr.strip())

def run_jarvis():
    print("Welcome Sir! , What do we have for today")
    while True:
        text = prompt("Jarvis > ").strip()
        if text == "exit" or text == "quit":
            break
        cmd_key, args_text, commands = check_command(text)
        run_command(commands, cmd_key, args_text)


run_jarvis()















