#!/usr/bin/env python3
import sys
import os
import re
from pathlib import Path

# Base directory for references  
REF_BASE = Path(__file__).parent.parent.parent / "references"

class Colors:
    """ANSI color codes - portable across terminals"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_BLUE = '\033[44m'
    BG_CYAN = '\033[46m'

def colorize(text, *styles):
    """Apply multiple color/style codes to text"""
    return ''.join(styles) + text + Colors.RESET

def print_header(text):
    """Print a colored header with box"""
    width = 70
    print("\n" + colorize("╔" + "═" * (width - 2) + "╗", Colors.BOLD, Colors.CYAN))
    print(colorize(f"║ {text:^{width - 4}} ║", Colors.BOLD, Colors.CYAN))
    print(colorize("╚" + "═" * (width - 2) + "╝", Colors.BOLD, Colors.CYAN) + "\n")

def highlight_code_line(line):
    """Apply syntax highlighting to a code line"""
    # Don't highlight empty lines
    if not line.strip():
        return line
    
    # Comments - must be done first to avoid highlighting inside comments
    if line.strip().startswith('//') or line.strip().startswith('#'):
        return colorize(line, Colors.DIM, Colors.BRIGHT_BLACK)
    
    # Store the original indentation
    indent = len(line) - len(line.lstrip())
    stripped = line.strip()
    
    # Keywords
    keywords = r'\b(if|else|while|for|return|class|struct|public|private|protected|void|int|const|std|include|import|def|from|typedef|template|typename|virtual|static|enum|namespace|using|throw|try|catch|new|delete)\b'
    stripped = re.sub(keywords, lambda m: colorize(m.group(), Colors.BOLD, Colors.MAGENTA), stripped)
    
    # Strings (single and double quotes)
    stripped = re.sub(r'"(?:[^"\\]|\\.)*"', lambda m: colorize(m.group(), Colors.GREEN), stripped)
    stripped = re.sub(r"'(?:[^'\\]|\\.)*'", lambda m: colorize(m.group(), Colors.GREEN), stripped)
    
    # Numbers
    stripped = re.sub(r'\b\d+\b', lambda m: colorize(m.group(), Colors.CYAN), stripped)
    
    # Function calls (word followed by opening parenthesis)
    stripped = re.sub(r'(\w+)(\s*\()', lambda m: colorize(m.group(1), Colors.YELLOW) + m.group(2), stripped)
    
    return ' ' * indent + stripped

def format_reference_line(line, in_code_block, line_num):
    """Format a single line with appropriate styling"""
    stripped = line.strip()
    
    # Main title
    if line.startswith('==='):
        return colorize(line, Colors.BOLD, Colors.BRIGHT_CYAN, Colors.BG_BLUE)
    
    # Major sections with better colors
    if stripped and stripped.endswith(':') and stripped.isupper() and len(stripped) < 40:
        section_colors = {
            'HEADER:': (Colors.BRIGHT_CYAN, '📦'),
            'IMPORT:': (Colors.BRIGHT_CYAN, '📦'),
            'HEADERS:': (Colors.BRIGHT_CYAN, '📦'),
            'PROTOTYPE:': (Colors.BRIGHT_MAGENTA, '⚙️'),
            'DECLARATION:': (Colors.BRIGHT_MAGENTA, '⚙️'),
            'SYNTAX:': (Colors.BRIGHT_MAGENTA, '⚙️'),
            'PARAMETERS:': (Colors.BRIGHT_BLUE, '🔧'),
            'ARGUMENTS:': (Colors.BRIGHT_BLUE, '🔧'),
            'METHODS:': (Colors.BRIGHT_GREEN, '🛠️'),
            'COMMON METHODS:': (Colors.BRIGHT_GREEN, '🛠️'),
            'USAGE:': (Colors.BRIGHT_GREEN, '🛠️'),
            'BASIC USAGE:': (Colors.BRIGHT_GREEN, '🛠️'),
            'EXAMPLE:': (Colors.YELLOW, '💡'),
            'BASIC EXAMPLE:': (Colors.YELLOW, '💡'),
            'ADVANCED EXAMPLE:': (Colors.YELLOW, '💡'),
            'GOTCHAS:': (Colors.BRIGHT_RED, '⚠️'),
            'WARNING:': (Colors.BRIGHT_RED, '⚠️'),
            'NOTES:': (Colors.CYAN, '📝'),
            '42 SPECIFIC NOTES:': (Colors.CYAN, '📝'),
            'RELATED:': (Colors.MAGENTA, '🔗'),
            'WHAT IS': (Colors.BRIGHT_WHITE, '❓'),
            'WHAT ARE': (Colors.BRIGHT_WHITE, '❓'),
        }
        
        for key, (color, icon) in section_colors.items():
            if key in stripped:
                return f"\n{colorize(icon + ' ' + stripped, Colors.BOLD, color)}"
        
        # Default for other sections
        return f"\n{colorize('▶️ ' + stripped, Colors.BOLD, Colors.BRIGHT_YELLOW)}"
    
    # Code blocks (indented or containing specific patterns)
    if in_code_block or line.startswith('    ') or line.startswith('\t'):
        if stripped.startswith('//') or stripped.startswith('#'):
            return colorize(line, Colors.DIM, Colors.BRIGHT_BLACK)
        return highlight_code_line(line)
    
    # Bullet points with colors
    if stripped.startswith('✅'):
        return colorize(line, Colors.BRIGHT_GREEN)
    elif stripped.startswith('❌'):
        return colorize(line, Colors.BRIGHT_RED)
    elif stripped.startswith('-') or stripped.startswith('•'):
        return colorize(line, Colors.WHITE)
    
    # Important notes
    if stripped.startswith('IMPORTANT:') or stripped.startswith('CRITICAL:'):
        return colorize(line, Colors.BOLD, Colors.BRIGHT_RED)
    elif stripped.startswith('NOTE:'):
        return colorize(line, Colors.BOLD, Colors.BRIGHT_YELLOW)
    
    # Regular text
    return line

def list_references():
    """List all available references organized by category"""
    print_header("📚 Available References")
    
    if not REF_BASE.exists():
        print(colorize("❌ No references directory found!", Colors.BOLD, Colors.RED))
        print(f"Expected at: {REF_BASE}")
        return
    
    # Walk through the directory structure
    for lang_dir in sorted(REF_BASE.iterdir()):
        if not lang_dir.is_dir():
            continue
            
        print(colorize(f"\n┌─ 📁 {lang_dir.name.upper()}", Colors.BOLD, Colors.BRIGHT_CYAN))
        
        categories = {}
        for item in lang_dir.rglob("*.ref"):
            rel_path = item.relative_to(lang_dir)
            category = str(rel_path.parent) if str(rel_path.parent) != '.' else 'root'
            if category not in categories:
                categories[category] = []
            categories[category].append(item.stem)
        
        for category in sorted(categories.keys()):
            if category == 'root':
                for topic in sorted(categories[category]):
                    print(colorize(f"│  • {topic}", Colors.BRIGHT_WHITE))
            else:
                print(colorize(f"│  └─ {category}/", Colors.CYAN))
                for topic in sorted(categories[category]):
                    print(colorize(f"│     • {topic}", Colors.BRIGHT_WHITE))
    
    print(colorize("\n└─ 💡 Usage: ref <topic>", Colors.BOLD, Colors.GREEN))
    print(colorize("   Example: ref vector, ref subprocess\n", Colors.GREEN))

def find_reference(topic):
    """Find a reference file by topic name"""
    if not REF_BASE.exists():
        return None
    
    # Search recursively for the topic
    for ref_file in REF_BASE.rglob(f"{topic}.ref"):
        return ref_file
    
    return None

def show_reference(topic):
    """Display the content of a reference with syntax highlighting"""
    ref_file = find_reference(topic)
    
    if not ref_file:
        print(colorize(f"❌ Reference '{topic}' not found!", Colors.BOLD, Colors.RED))
        print(colorize("\n💡 Try: ref list (to see all available references)", Colors.YELLOW))
        return
    
    # Read and display the reference
    try:
        with open(ref_file, 'r') as f:
            content = f.read()
        
        # Build formatted output first
        output_lines = []
        lines = content.split('\n')
        in_code_block = False
        
        for i, line in enumerate(lines):
            # Detect code blocks
            if line.strip() and not line[0].isspace() and not line.startswith('==='):
                if i > 0 and lines[i-1].strip() and lines[i-1].strip().endswith(':'):
                    in_code_block = True
            
            if line.strip() and not line[0].isspace() and line.strip().endswith(':') and line.strip().isupper():
                in_code_block = False
            
            formatted_line = format_reference_line(line, in_code_block, i)
            output_lines.append(formatted_line)
        
        # Footer with file location
        rel_path = ref_file.relative_to(REF_BASE)
        output_lines.append(colorize(f"\n└─ 📄 {rel_path}", Colors.DIM, Colors.BRIGHT_BLACK))
        output_lines.append("")
        
        # Use 'less' for pagination if available, otherwise print normally
        use_pager(output_lines)
        
    except Exception as e:
        print(colorize(f"❌ Error reading reference: {e}", Colors.BOLD, Colors.RED))

def use_pager(lines):
    """Display content using less starting from the very first line"""
    import subprocess
    import shutil
    import os
    
    # Try to use less - this will work now that output isn't captured
    if shutil.which('less'):
        content = '\n'.join(lines)
        try:
            # Pipe directly to less with -R for colors
            process = subprocess.Popen(['less', '-R'], stdin=subprocess.PIPE, text=True)
            process.communicate(input=content)
        except (BrokenPipeError, KeyboardInterrupt):
            pass
    else:
        # Fallback - just print
        print('\n'.join(lines))

def search_references(query):
    """Search for references containing a keyword"""
    print_header(f"🔍 Search Results for: '{query}'")
    
    if not REF_BASE.exists():
        print(colorize("❌ No references directory found!", Colors.BOLD, Colors.RED))
        return
    
    found = []
    query_lower = query.lower()
    
    # Search through all reference files
    for ref_file in REF_BASE.rglob("*.ref"):
        try:
            with open(ref_file, 'r') as f:
                content = f.read()
                if query_lower in content.lower():
                    # Get relative path for display
                    rel_path = ref_file.relative_to(REF_BASE)
                    topic = ref_file.stem
                    category = rel_path.parent
                    
                    # Find matching lines for context
                    matches = []
                    for line in content.split('\n'):
                        if query_lower in line.lower():
                            matches.append(line.strip()[:60])
                            if len(matches) >= 2:
                                break
                    
                    found.append((topic, category, matches))
        except:
            continue
    
    if found:
        for topic, category, matches in found:
            print(colorize(f"  📄 {topic}", Colors.BOLD, Colors.BRIGHT_GREEN) + 
                  colorize(f" ({category})", Colors.DIM, Colors.BRIGHT_BLACK))
            for match in matches[:1]:  # Show first match
                print(colorize(f"     → {match}...", Colors.DIM, Colors.WHITE))
        print(colorize(f"\n└─ 💡 Use: ref <topic> to view", Colors.BOLD, Colors.YELLOW))
    else:
        print(colorize(f"❌ No references found containing '{query}'", Colors.RED))
    
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
    print(colorize("❌ Usage:", Colors.BOLD, Colors.RED))
    print("  ref <topic>         - Show reference for topic")
    print("  ref list            - List all available references")
    print("  ref search <query>  - Search references by keyword")
    sys.exit(1)

command = sys.argv[1]

if command == "list":
    list_references()
elif command == "search":
    if len(sys.argv) < 3:
        print(colorize("❌ Usage: ref search <query>", Colors.BOLD, Colors.RED))
        sys.exit(1)
    query = " ".join(sys.argv[2:])
    search_references(query)
else:
    # Anything else is treated as a topic name
    topic = command
    show_reference(topic)
