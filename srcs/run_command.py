import subprocess

def run_command(commands, cmd_key, args_text):
    cmd_info = commands[cmd_key]
    script_path = cmd_info["script"]
    
    args_list = args_text.split() if args_text else []

    if script_path.endswith(".py"):
        result = subprocess.run(
            ["python3", script_path] + args_list,
            capture_output=True,
            text=True
        )
        if result.stdout.strip():
            print(result.stdout.strip())
        if result.stderr.strip():
            print("Error:", result.stderr.strip())
            
    elif script_path.endswith(".sh"):
        result = subprocess.run(
            ["bash", script_path] + args_list)
        if result.returncode != 0:
            print(f"⚠️  Script exited with code {result.returncode}")
    else:
        print(f"Unsupported script type for command '{cmd_key}'")
        return
