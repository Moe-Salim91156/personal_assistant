from srcs.load import open_yaml

def check_command(text):
    commands = open_yaml()

    for key in sorted(commands, key=len, reverse=True):
        if text.startswith(key):
            args = text[len(key):].strip()
            return key, args, commands
    return None, None, None


