from prompt_toolkit import prompt
import os
from core.parser import parse_intent
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
                os.system('clear')
                continue

            main_dict = parse_intent(user_input)
            plugin = main_dict.get("action")
            target = main_dict.get("target")

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

