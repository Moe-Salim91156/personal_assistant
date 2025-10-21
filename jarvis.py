from prompt_toolkit import prompt
import os
from core.parser import parse_intent_ollama
from core.runner_manager import execute


def main():
    print("Jarvis Phase 2 - Modular Assistant")
    while True:
        try:
            user_input = prompt("Jarvis > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye, Sir.")
                break
            if user_input.lower() == "clear":
                os.system("clear")
                continue

            response = parse_intent_ollama(user_input)
            plugin = response["plugin"]
            target = response["target"]
            args = response["args"]

            if not plugin:
                print("❌ Could not understand command.")
                continue
            # print("target is : ", target)
            # print("plugin is : ", plugin)
            success = execute(plugin, target)
            print("✅ Done" if success else "❌ Failed")

        except KeyboardInterrupt:
            print("\nExiting Jarvis.")
            break


if __name__ == "__main__":
    main()
