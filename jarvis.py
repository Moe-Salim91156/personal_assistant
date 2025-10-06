from prompt_toolkit import prompt
from srcs.Check_Command import check_command
from srcs.run_command import run_command

def run_jarvis():
    print("Welcome Sir! , What do we have for today")
    while True:
        text = prompt("Jarvis > ").strip()
        if text == "exit" or text == "quit":
            break
        cmd_key, args_text, commands = check_command(text)
        if cmd_key:
            run_command(commands, cmd_key, args_text)

run_jarvis()
