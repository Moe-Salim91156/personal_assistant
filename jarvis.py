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

            # Error handling: check if response is None or invalid
            if response is None:
                print("❌ Could not parse command. Please try again.")
                continue

            # Error handling: safely extract fields
            try:
                plugin = response["plugin"]
                target = response["target"]
                args = response["args"]
            except KeyError as e:
                print(f"❌ Missing field in response: {e}")
                print("💡 Ollama returned incomplete data. Try rephrasing.")
                continue
            except TypeError:
                print("❌ Invalid response format from parser.")
                continue

            print("Plugin to use:", plugin)
            print("Target:", target)
            print("Args:", args)

            if not plugin:
                print("❌ Could not understand command.")
                continue

            success = execute(plugin, target, args)
            print("✅ Done" if success else "❌ Failed")

        except KeyboardInterrupt:
            print("\nExiting Jarvis.")
            break
        except Exception as e:
            # Catch any other unexpected errors to keep Jarvis running
            print(f"❌ Unexpected error: {e}")
            print("💡 Jarvis will continue running...")


if __name__ == "__main__":
    main()
