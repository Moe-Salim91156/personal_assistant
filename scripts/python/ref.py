#!/usr/bin/env python3
import sys
import os
import re
from pathlib import Path

# Base directory for references  
REF_BASE = Path(__file__).parent.parent.parent / "references"

class Colors:
    """ANSI color codes - optimized for dark terminals"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Bright colors for dark backgrounds
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    
    # Special colors
    ORANGE = '\033[38;5;214m'
    PINK = '\033[38;5;205m'

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
    if not line.strip():
        return line
    
    indent = len(line) - len(line.lstrip())
    stripped = line.strip()
    
    if stripped.startswith('//') or stripped.startswith('#'):
        return ' ' * indent + colorize(stripped, Colors.GRAY)
    
    keywords = r'\b(if|else|while|for|return|class|struct|public|private|protected|void|int|const|std|include|import|def|from|typedef|template|typename|virtual|static|enum|namespace|using|throw|try|catch|new|delete|size_t|bool|char|float|double|long|short|unsigned)\b'
    stripped = re.sub(keywords, lambda m: colorize(m.group(), Colors.BOLD, Colors.MAGENTA), stripped)
    
    stripped = re.sub(r'"(?:[^"\\]|\\.)*"', lambda m: colorize(m.group(), Colors.GREEN), stripped)
    stripped = re.sub(r"'(?:[^'\\]|\\.)*'", lambda m: colorize(m.group(), Colors.GREEN), stripped)
    
    stripped = re.sub(r'\b\d+\b', lambda m: colorize(m.group(), Colors.CYAN), stripped)
    
    stripped = re.sub(r'(\w+)(\s*\()', lambda m: colorize(m.group(1), Colors.YELLOW) + m.group(2), stripped)
    
    return ' ' * indent + stripped

def format_reference_line(line, in_code_block, line_num):
    """Format a single line with appropriate styling"""
    stripped = line.strip()
    
    if line.startswith('==='):
        return colorize(line, Colors.BOLD, Colors.CYAN)
    
    if stripped and stripped.endswith(':') and stripped.isupper() and len(stripped) < 40:
        section_colors = {
            'HEADER:': (Colors.CYAN, '📦'),
            'IMPORT:': (Colors.CYAN, '📦'),
            'HEADERS:': (Colors.CYAN, '📦'),
            'PROTOTYPE:': (Colors.MAGENTA, '⚙️'),
            'DECLARATION:': (Colors.MAGENTA, '⚙️'),
            'SYNTAX:': (Colors.MAGENTA, '⚙️'),
            'PARAMETERS:': (Colors.BLUE, '🔧'),
            'ARGUMENTS:': (Colors.BLUE, '🔧'),
            'METHODS:': (Colors.GREEN, '🛠️'),
            'COMMON METHODS:': (Colors.GREEN, '🛠️'),
            'USAGE:': (Colors.GREEN, '🛠️'),
            'BASIC USAGE:': (Colors.GREEN, '🛠️'),
            'EXAMPLE:': (Colors.YELLOW, '💡'),
            'BASIC EXAMPLE:': (Colors.YELLOW, '💡'),
            'ADVANCED EXAMPLE:': (Colors.YELLOW, '💡'),
            'GOTCHAS:': (Colors.RED, '⚠️'),
            'WARNING:': (Colors.RED, '⚠️'),
            'NOTES:': (Colors.CYAN, '📝'),
            '42 SPECIFIC NOTES:': (Colors.ORANGE, '📝'),
            'RELATED:': (Colors.PINK, '🔗'),
            'WHAT IS': (Colors.WHITE, '❓'),
            'WHAT ARE': (Colors.WHITE, '❓'),
        }
        
        for key, (color, icon) in section_colors.items():
            if key in stripped:
                return f"\n{colorize(icon + ' ' + stripped, Colors.BOLD, color)}"
        
        return f"\n{colorize('▶️ ' + stripped, Colors.BOLD, Colors.YELLOW)}"
    
    if in_code_block or line.startswith('    ') or line.startswith('\t'):
        if stripped.startswith('//') or stripped.startswith('#'):
            return colorize(line, Colors.GRAY)
        return highlight_code_line(line)
    
    if stripped.startswith('✅'):
        return colorize(line, Colors.GREEN)
    elif stripped.startswith('❌'):
        return colorize(line, Colors.RED)
    elif stripped.startswith('-') or stripped.startswith('•'):
        return colorize(line, Colors.WHITE)
    
    if stripped.startswith('IMPORTANT:') or stripped.startswith('CRITICAL:'):
        return colorize(line, Colors.BOLD, Colors.RED)
    elif stripped.startswith('NOTE:'):
        return colorize(line, Colors.BOLD, Colors.YELLOW)
    
    return line

def list_references():
    """List all available references organized by category"""
    print_header("📚 Available References")
    
    if not REF_BASE.exists():
        print(colorize("❌ No references directory found!", Colors.BOLD, Colors.RED))
        print(f"Expected at: {REF_BASE}")
        return
    
    for lang_dir in sorted(REF_BASE.iterdir()):
        if not lang_dir.is_dir():
            continue
            
        print(colorize(f"\n┌─ 📁 {lang_dir.name.upper()}", Colors.BOLD, Colors.CYAN))
        
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
                    print(colorize(f"│  • {topic}", Colors.WHITE))
            else:
                print(colorize(f"│  └─ {category}/", Colors.CYAN))
                for topic in sorted(categories[category]):
                    print(colorize(f"│     • {topic}", Colors.WHITE))
    
    print(colorize("\n└─ 💡 Usage: ref <topic>", Colors.BOLD, Colors.GREEN))
    print(colorize("   Example: ref vector, ref subprocess\n", Colors.GREEN))

def find_reference(topic):
    """Find a reference file by topic name"""
    if not REF_BASE.exists():
        return None
    
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
    
    try:
        with open(ref_file, 'r') as f:
            content = f.read()
        
        output_lines = []
        lines = content.split('\n')
        in_code_block = False
        
        for i, line in enumerate(lines):
            if line.strip() and not line[0].isspace() and not line.startswith('==='):
                if i > 0 and lines[i-1].strip() and lines[i-1].strip().endswith(':'):
                    in_code_block = True
            
            if line.strip() and not line[0].isspace() and line.strip().endswith(':') and line.strip().isupper():
                in_code_block = False
            
            formatted_line = format_reference_line(line, in_code_block, i)
            output_lines.append(formatted_line)
        
        rel_path = ref_file.relative_to(REF_BASE)
        output_lines.append(colorize(f"\n└─ 📄 {rel_path}", Colors.GRAY))
        output_lines.append("")
        
        use_pager(output_lines)
        
    except Exception as e:
        print(colorize(f"❌ Error reading reference: {e}", Colors.BOLD, Colors.RED))

def use_pager(lines):
    """Display content using less with proper flags for ANSI codes"""
    import subprocess
    import shutil
    
    if shutil.which('less'):
        content = '\n'.join(lines)
        try:
            # -R: raw control chars (for colors)
            # -F: quit if one screen
            # -X: don't clear screen on exit
            # -S: chop long lines instead of wrap
            process = subprocess.Popen(
                ['less', '-RFX'], 
                stdin=subprocess.PIPE, 
                text=True
            )
            process.communicate(input=content)
        except (BrokenPipeError, KeyboardInterrupt):
            pass
    else:
        # Fallback: print directly
        print('\n'.join(lines))

def search_references(query):
    """Search for references containing a keyword"""
    print_header(f"🔍 Search Results for: '{query}'")
    
    if not REF_BASE.exists():
        print(colorize("❌ No references directory found!", Colors.BOLD, Colors.RED))
        return
    
    found = []
    query_lower = query.lower()
    
    for ref_file in REF_BASE.rglob("*.ref"):
        try:
            with open(ref_file, 'r') as f:
                content = f.read()
                if query_lower in content.lower():
                    rel_path = ref_file.relative_to(REF_BASE)
                    topic = ref_file.stem
                    category = rel_path.parent
                    
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
            print(colorize(f"  📄 {topic}", Colors.BOLD, Colors.GREEN) + 
                  colorize(f" ({category})", Colors.GRAY))
            for match in matches[:1]:
                print(colorize(f"     → {match}...", Colors.WHITE))
        print(colorize(f"\n└─ 💡 Use: ref <topic> to view", Colors.BOLD, Colors.YELLOW))
    else:
        print(colorize(f"❌ No references found containing '{query}'", Colors.RED))
    
    print()

# Script execution
if len(sys.argv) == 1:
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
    topic = command
    show_reference(topic)
