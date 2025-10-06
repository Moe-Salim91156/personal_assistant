import subprocess
import subprocess

def run_command(commands, cmd_key, args_text):
    cmd_info = commands[cmd_key]
    script_path = cmd_info["script"]
    
    # Split args properly (handles empty args)
    args_list = args_text.split() if args_text else []

    if script_path.endswith(".py"):
        # Python scripts - capture output for clean display
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
        # Bash scripts - allow interactive input
        # Don't capture output, let it flow directly to terminal
        result = subprocess.run(
            ["bash", script_path] + args_list
            # No capture_output=True
            # No text=True
            # Scripts can now use read, prompt_toolkit, etc.
        )
        # Return code is still available
        if result.returncode != 0:
            print(f"⚠️  Script exited with code {result.returncode}")
    else:
        print(f"Unsupported script type for command '{cmd_key}'")
        return


