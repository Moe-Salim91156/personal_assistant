import subprocess

def run_command(commands, cmd_key, args_text):
    cmd_info = commands[cmd_key]
    script_path = cmd_info["script"]

    if script_path.endswith(".py"):
        result = subprocess.run(
            ["python3", script_path] + args_text.split(),
            capture_output=True,
            text=True
        )
    elif script_path.endswith(".sh"):
        result = subprocess.run(
            ["bash", script_path] + args_text.split())
    else:
        print(f"Unsupported script type for command '{cmd_key}'")
        return

    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print("Error:", result.stderr.strip())



