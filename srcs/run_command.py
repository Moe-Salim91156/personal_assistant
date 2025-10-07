import subprocess

def run_command(commands, cmd_key, args_text):
    """Execute a command from commands.yaml"""
    cmd_info = commands[cmd_key]
    script_path = cmd_info["script"]
    
    args_list = args_text.split() if args_text else []

    # Handle multi-word commands (e.g., "ref list")
    if " " in cmd_key:
        parts = cmd_key.split()
        subcommand = " ".join(parts[1:])
        args_list = [subcommand] + args_list

    if script_path.endswith(".py"):
        # Special handling for ref.py - don't capture output so pager works
        if 'ref.py' in script_path:
            result = subprocess.run(
                ["python3", script_path] + args_list,
            )
            if result.returncode != 0:
                print(f"\033[93m⚠️  Script exited with code {result.returncode}\033[0m")
        else:
            # Normal Python scripts - capture and display output
            result = subprocess.run(
                ["python3", script_path] + args_list,
                capture_output=True,
                text=True
            )
            if result.stdout.strip():
                print(result.stdout.strip())
            if result.stderr.strip():
                print("\033[91mError:\033[0m", result.stderr.strip())
            if result.returncode != 0:
                print(f"\033[93m⚠️  Script exited with code {result.returncode}\033[0m")
            
    elif script_path.endswith(".sh"):
        result = subprocess.run(
            ["bash", script_path] + args_list)
        if result.returncode != 0:
            print(f"\033[93m⚠️  Script exited with code {result.returncode}\033[0m")
    else:
        print(f"\033[91mUnsupported script type for command '{cmd_key}'\033[0m")
        return
