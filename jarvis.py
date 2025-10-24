#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                              J.A.R.V.I.S.                                    ║
║              Just A Rather Very Intelligent System                           ║
║                                                                              ║
║  Personal AI Development Assistant                                          ║
║  Version 2.0 - Modular Architecture                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
from prompt_toolkit import prompt
from prompt_toolkit.styles import Style
from core.parser import parse_intent_ollama
from core.runner_manager import execute

# ═══════════════════════════════════════════════════════════════════════════
# VISUAL CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════


class Colors:
    """ANSI color codes for terminal styling"""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Main colors
    CYAN = "\033[96m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"

    # Special effects
    BLINK = "\033[5m"
    UNDERLINE = "\033[4m"

    # Backgrounds
    BG_BLUE = "\033[44m"
    BG_GREEN = "\033[42m"
    BG_RED = "\033[41m"


# Prompt toolkit style for input
prompt_style = Style.from_dict(
    {
        "prompt": "#00d9ff bold",  # Cyan
        "input": "#ffffff",  # White
    }
)

# ═══════════════════════════════════════════════════════════════════════════
# ASCII ART & ANIMATIONS
# ═══════════════════════════════════════════════════════════════════════════

JARVIS_LOGO = f"""{Colors.CYAN}{Colors.BOLD}
     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗
     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝
     ██║███████║██████╔╝██║   ██║██║███████╗
██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║
╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║
 ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝{Colors.RESET}
{Colors.GRAY}    Just A Rather Very Intelligent System{Colors.RESET}
"""

STARTUP_MESSAGES = [
    f"{Colors.CYAN}[●{Colors.RESET}{Colors.GRAY}○○{Colors.RESET}] Initializing neural networks...",
    f"{Colors.CYAN}[●●{Colors.RESET}{Colors.GRAY}○{Colors.RESET}] Loading natural language processor...",
    f"{Colors.CYAN}[●●●{Colors.RESET}] Connecting to Ollama inference engine...",
    f"{Colors.GREEN}[✓]{Colors.RESET} {Colors.BOLD}All systems operational{Colors.RESET}",
]

THINKING_FRAMES = [
    f"{Colors.CYAN}⠋{Colors.RESET}",
    f"{Colors.CYAN}⠙{Colors.RESET}",
    f"{Colors.CYAN}⠹{Colors.RESET}",
    f"{Colors.CYAN}⠸{Colors.RESET}",
    f"{Colors.CYAN}⠼{Colors.RESET}",
    f"{Colors.CYAN}⠴{Colors.RESET}",
    f"{Colors.CYAN}⠦{Colors.RESET}",
    f"{Colors.CYAN}⠧{Colors.RESET}",
    f"{Colors.CYAN}⠇{Colors.RESET}",
    f"{Colors.CYAN}⠏{Colors.RESET}",
]

# ═══════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════


def clear_screen():
    """Clear terminal screen"""
    os.system("clear" if os.name != "nt" else "cls")


def print_box(text, color=Colors.CYAN, width=80):
    """Print text in a fancy box"""
    lines = text.split("\n")
    max_len = max(len(line) for line in lines)
    width = max(max_len + 4, width)

    print(f"{color}╔{'═' * (width - 2)}╗{Colors.RESET}")
    for line in lines:
        padding = width - len(line) - 4
        print(f"{color}║{Colors.RESET} {line}{' ' * padding} {color}║{Colors.RESET}")
    print(f"{color}╚{'═' * (width - 2)}╝{Colors.RESET}")


def typewriter_effect(text, delay=0.02):
    """Print text with typewriter effect"""
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()


def animate_startup():
    """Show startup animation"""
    clear_screen()
    print(JARVIS_LOGO)
    print()

    for msg in STARTUP_MESSAGES:
        print(f"  {msg}")
        time.sleep(0.3)

    print()
    time.sleep(0.2)


def show_thinking_animation(duration=1.0):
    """Show thinking animation"""
    import sys

    end_time = time.time() + duration
    i = 0

    while time.time() < end_time:
        sys.stdout.write(
            f"\r  {THINKING_FRAMES[i % len(THINKING_FRAMES)]} Processing..."
        )
        sys.stdout.flush()
        time.sleep(0.08)
        i += 1

    sys.stdout.write("\r" + " " * 50 + "\r")  # Clear the line
    sys.stdout.flush()


def print_status(success, message):
    """Print status message with icon"""
    if success:
        icon = f"{Colors.GREEN}✓{Colors.RESET}"
        color = Colors.GREEN
    else:
        icon = f"{Colors.RED}✗{Colors.RESET}"
        color = Colors.RED

    print(f"\n  [{icon}] {color}{message}{Colors.RESET}\n")


def print_command_info(plugin, target, args):
    """Display parsed command information"""
    print(
        f"\n{Colors.GRAY}╭─ Command Analysis ─────────────────────────────╮{Colors.RESET}"
    )
    print(
        f"{Colors.GRAY}│{Colors.RESET} {Colors.CYAN}Plugin:{Colors.RESET}  {Colors.BOLD}{plugin}{Colors.RESET}"
    )
    print(
        f"{Colors.GRAY}│{Colors.RESET} {Colors.CYAN}Target:{Colors.RESET}  {Colors.BOLD}{target}{Colors.RESET}"
    )
    if args:
        print(
            f"{Colors.GRAY}│{Colors.RESET} {Colors.CYAN}Args:{Colors.RESET}    {Colors.YELLOW}{args}{Colors.RESET}"
        )
    print(
        f"{Colors.GRAY}╰────────────────────────────────────────────────╯{Colors.RESET}\n"
    )


def show_welcome():
    """Display welcome message"""
    welcome_text = f"""
{Colors.BOLD}Welcome, Sir.{Colors.RESET}

I am JARVIS, your personal development assistant.
Ready to assist with your projects and tasks.

{Colors.GRAY}Available commands:{Colors.RESET}
  {Colors.CYAN}•{Colors.RESET} ref <topic>      - Access documentation
  {Colors.CYAN}•{Colors.RESET} push            - Commit and push changes  
  {Colors.CYAN}•{Colors.RESET} clean/cleaner   - System cleanup
  {Colors.CYAN}•{Colors.RESET} todo            - Task management
  {Colors.CYAN}•{Colors.RESET} export          - Generate PDFs
  {Colors.CYAN}•{Colors.RESET} deploy          - Infrastructure deployment
  
{Colors.GRAY}Type 'help' for more information or 'exit' to quit.{Colors.RESET}
"""
    print(welcome_text)


def show_help():
    """Display help information"""
    help_text = f"""
{Colors.CYAN}{Colors.BOLD}JARVIS Command Reference{Colors.RESET}

{Colors.YELLOW}Documentation & References:{Colors.RESET}
  ref <topic>          Show documentation for a topic
  ref list             List all available references
  ref search <query>   Search documentation by keyword

{Colors.YELLOW}Development Tools:{Colors.RESET}
  push [msg]           Git add, commit, and push
  clean                Clean 42 project files
  cleaner              Deep system cleanup
  todo                 Show TODO/FIXME comments
  ch_forb              Check for forbidden functions

{Colors.YELLOW}Export & Deployment:{Colors.RESET}
  export <file>        Export markdown to PDF
  deploy               Deploy infrastructure

{Colors.YELLOW}System Commands:{Colors.RESET}
  clear                Clear screen
  help                 Show this help message
  exit/quit            Exit JARVIS

{Colors.GRAY}Powered by Ollama + Natural Language Processing{Colors.RESET}
"""
    print_box(help_text, Colors.CYAN, 70)


def show_goodbye():
    """Display goodbye message"""
    goodbye = f"""
{Colors.CYAN}╔═══════════════════════════════════════════════════════╗
║                                                       ║
║  {Colors.BOLD}Thank you, Sir. Until next time.{Colors.RESET}{Colors.CYAN}                ║
║                                                       ║
║  {Colors.GRAY}JARVIS offline{Colors.RESET}{Colors.CYAN}                                     ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝{Colors.RESET}
"""
    print(goodbye)


# ═══════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════════════


def main():
    """Main JARVIS loop"""
    # Show startup animation
    animate_startup()

    # Welcome message
    show_welcome()

    # Main interaction loop
    while True:
        try:
            # Get user input with styled prompt
            user_input = prompt(
                [("class:prompt", "╭─ JARVIS\n╰─❯ ")], style=prompt_style
            ).strip()

            # Handle empty input
            if not user_input:
                continue

            # Handle exit commands
            if user_input.lower() in ["exit", "quit", "bye"]:
                show_goodbye()
                break

            # Handle clear command
            if user_input.lower() == "clear":
                clear_screen()
                print(JARVIS_LOGO)
                continue

            # Handle help command
            if user_input.lower() in ["help", "?"]:
                show_help()
                continue

            # Show thinking animation
            print()
            show_thinking_animation(0.5)

            # Parse command using NLP
            response = parse_intent_ollama(user_input)

            if not response:
                print_status(False, "Unable to process command. Please try again.")
                continue

            # Extract command components
            plugin = response.get("plugin", "")
            target = response.get("target", "")
            args = response.get("args", "")

            # Display parsed command
            print_command_info(plugin, target, args)

            # Execute command
            print(
                f"{Colors.GRAY}─────────────────────────────────────────────────{Colors.RESET}\n"
            )
            success = execute(plugin, target, args)
            print(
                f"\n{Colors.GRAY}─────────────────────────────────────────────────{Colors.RESET}"
            )

            # Show result status
            if success:
                print_status(True, "Command executed successfully")
            else:
                print_status(False, "Command execution failed")

        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}⚠{Colors.RESET}  Interrupt received")
            confirm = (
                prompt([("class:prompt", "Exit JARVIS? (y/n): ")], style=prompt_style)
                .strip()
                .lower()
            )

            if confirm in ["y", "yes"]:
                show_goodbye()
                break
            else:
                print(f"{Colors.GREEN}Resuming operation...{Colors.RESET}\n")
                continue

        except Exception as e:
            print_status(False, f"System error: {str(e)}")
            print(
                f"{Colors.GRAY}Please report this issue if it persists.{Colors.RESET}\n"
            )


# ═══════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n{Colors.RED}Critical error: {e}{Colors.RESET}")
        sys.exit(1)
