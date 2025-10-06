#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Base directory for references  
REF_BASE = Path(__file__).parent.parent.parent / "references"

def colorize(text, color_code):
    """Add color to terminal output"""
    return f"\033[{color_code}m{text}\033[0m"

def print_header(text):
    """Print a colored header"""
    print("\n" + colorize("=" * 60, "1;36"))
    print(colorize(f"  {text}", "1;36"))
    print(colorize("=" * 60, "1;36") + "\n")

def list_references():
    """List all available references organized by category"""
    print_header("📚 Available References")
    
    if not REF_BASE.exists():
        print(colorize("❌ No references directory found!", "1;31"))
        print(f"Expected at: {REF_BASE}")
        return
    
    # Walk through the directory structure
    for lang_dir in sorted(REF_BASE.iterdir()):
        if not lang_dir.is_dir():
            continue
            
        print(colorize(f"\n📁 {lang_dir.name.upper()}", "1;33"))
        
        for category_dir in sorted(lang_dir.iterdir()):
            if not category_dir.is_dir():
                # Direct files in language dir
                if category_dir.suffix == ".ref":
                    topic = category_dir.stem
                    print(f"  • {topic}")
            else:
                # Files in category subdirectories
                refs = list(category_dir.glob("*.ref"))
                if refs:
                    print(colorize(f"  └─ {category_dir.name}/", "0;36"))
                    for ref_file in sorted(refs):
                        topic = ref_file.stem
                        print(f"     • {topic}")
    
    print(colorize("\n💡 Usage: ref <topic>", "0;32"))
    print(colorize("   Example: ref vector, ref subprocess\n", "0;32"))

def find_reference(topic):
    """Find a reference file by topic name"""
    if not REF_BASE.exists():
        return None
    
    # Search recursively for the topic
    for ref_file in REF_BASE.rglob(f"{topic}.ref"):
        return ref_file
    
    return None

def show_reference(topic):
    """Display the content of a reference"""
    ref_file = find_reference(topic)
    
    if not ref_file:
        print(colorize(f"❌ Reference '{topic}' not found!", "1;31"))
        print(colorize("\n💡 Try: ref list (to see all available references)", "0;33"))
        return
    
    # Read and display the reference
    try:
        with open(ref_file, 'r') as f:
            content = f.read()
        
        # Display with some basic formatting
        lines = content.split('\n')
        for line in lines:
            if line.startswith('==='):
                print(colorize(line, "1;36"))
            elif line.startswith('HEADER:') or line.startswith('PROTOTYPE:'):
                print(colorize(line, "1;33"))
            elif line.endswith(':') and line.isupper():
                print(colorize(line, "1;32"))
            elif line.strip().startswith('//') or line.strip().startswith('#'):
                print(colorize(line, "0;90"))
            else:
                print(line)
        
        print()  # Empty line at end
        
    except Exception as e:
        print(colorize(f"❌ Error reading reference: {e}", "1;31"))

def search_references(query):
    """Search for references containing a keyword"""
    print_header(f"🔍 Search Results for: '{query}'")
    
    if not REF_BASE.exists():
        print(colorize("❌ No references directory found!", "1;31"))
        return
    
    found = []
    query_lower = query.lower()
    
    # Search through all reference files
    for ref_file in REF_BASE.rglob("*.ref"):
        try:
            with open(ref_file, 'r') as f:
                content = f.read().lower()
                if query_lower in content:
                    # Get relative path for display
                    rel_path = ref_file.relative_to(REF_BASE)
                    topic = ref_file.stem
                    category = rel_path.parent
                    found.append((topic, category))
        except:
            continue
    
    if found:
        for topic, category in found:
            print(f"  • {colorize(topic, '1;32')} ({category})")
        print(colorize(f"\n💡 Use: ref <topic> to view", "0;33"))
    else:
        print(colorize(f"No references found containing '{query}'", "0;31"))
    
    print()

# Called by Jarvis via subprocess with run_command.py
# For multi-word commands like "ref list", run_command.py passes the subcommand
# 
# Examples:
# "ref list" → sys.argv = ["ref.py", "list"]
# "ref vector" → sys.argv = ["ref.py", "vector"]
# "ref search iterator" → sys.argv = ["ref.py", "search", "iterator"]

if len(sys.argv) == 1:
    # No arguments - show usage
    print(colorize("❌ Usage:", "1;31"))
    print("  ref <topic>         - Show reference for topic")
    print("  ref list            - List all available references")
    print("  ref search <query>  - Search references by keyword")
    sys.exit(1)

command = sys.argv[1]

if command == "list":
    list_references()
elif command == "search":
    if len(sys.argv) < 3:
        print(colorize("❌ Usage: ref search <query>", "1;31"))
        sys.exit(1)
    query = " ".join(sys.argv[2:])
    search_references(query)
else:
    # Anything else is treated as a topic name
    topic = command
    show_reference(topic)
