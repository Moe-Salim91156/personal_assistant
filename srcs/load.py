import yaml

def open_yaml():
    with open("commands.yaml") as f:
        commands = yaml.safe_load(f)
    return commands


