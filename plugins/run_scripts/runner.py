import subprocess
import yaml
from pathlib import Path


def open_yaml():
    base_dir = Path(__file__).parent  # directory of this file
    yaml_path = base_dir / "commands.yaml"
    with open(yaml_path, "r") as f:
        return yaml.safe_load(f)


def run(target, args):
    """
    Execute a command defined in commands.yaml or directly run a script.

    target = command key (e.g. "ref" or "clean")
    args = optional string of arguments
    """
    print("args are :", args)
    base_dir = Path(__file__).resolve().parent

    # load yaml file
    commands = open_yaml()

    if target not in commands:
        print(f"❌ Command '{target}' not found in commands.yaml.")
        return False

    cmd_info = commands[target]
    script_path = (base_dir / cmd_info["script"]).resolve()

    # Handle args properly (it's a string, not a dict)
    args_list = args.split() if args else []

    # Handle multi-word command keys
    if " " in target:
        parts = target.split()
        subcommand = " ".join(parts[1:])
        args_list = [subcommand] + args_list
        print("Updated args_list for multi-word command:", args_list)

    if script_path.suffix == ".py":
        # Special handling for ref.py
        if "ref.py" in str(script_path):
            print(args_list)
            result = subprocess.run(["python3", script_path] + args_list)
        else:
            result = subprocess.run(
                ["python3", script_path] + args_list, capture_output=True, text=True
            )
            if result.stdout.strip():
                print(result.stdout.strip())
            if result.stderr.strip():
                print("\033[91mError:\033[0m", result.stderr.strip())

    elif script_path.suffix == ".sh":
        result = subprocess.run(["bash", script_path] + args_list)
    else:
        print(f"❌ Unsupported script type: {script_path.suffix}")
        return False

    if result.returncode != 0:
        print(f"⚠️  Script exited with code {result.returncode}")
    return result.returncode == 0
