# 📚 Jarvis Reference System Setup Guide

## Quick Setup (5 minutes)

### 1. Create the directory structure:

```bash
cd ~/your-jarvis-project
mkdir -p references/cpp98/containers
mkdir -p references/cpp98/strings
mkdir -p references/cpp98/iterators
mkdir -p references/cpp98/sockets
mkdir -p references/python
```

### 2. Add the ref.py script:

Copy the `ref.py` file I provided into `scripts/python/ref.py`

Make it executable (optional):
```bash
chmod +x scripts/python/ref.py
```

### 3. Update commands.yaml:

Add these lines to your `commands.yaml`:

```yaml
ref list:
  script: scripts/python/ref.py
  args: ["--list"]

ref search:
  script: scripts/python/ref.py
  args: ["--search", "{query}"]

ref:
  script: scripts/python/ref.py
  args: ["{topic}"]
```

**IMPORTANT:** Put `ref list` and `ref search` BEFORE `ref` in the file! 
(Your command parser checks longest matches first, so this order matters)

### 4. Add the reference files:

Save these files in your `references/` folder:
- `references/cpp98/containers/vector.ref`
- `references/cpp98/containers/map.ref`
- `references/cpp98/sockets/socket_basics.ref`
- `references/python/subprocess.ref`

### 5. Test it!

```bash
python jarvis.py
```

Then try:
```
Jarvis > ref list
Jarvis > ref vector
Jarvis > ref subprocess
Jarvis > ref search "iterator"
```

---

## Usage Examples

### View a specific reference:
```
Jarvis > ref vector
Jarvis > ref map
Jarvis > ref socket_basics
Jarvis > ref subprocess
```

### List all available references:
```
Jarvis > ref list
```

### Search for a keyword:
```
Jarvis > ref search iterator
Jarvis > ref search socket
Jarvis > ref search "error handling"
```

---

## Adding Your Own References

### Method 1: Create a new .ref file

1. Navigate to the appropriate category:
```bash
cd references/cpp98/containers
```

2. Create a new file (e.g., `set.ref`):
```bash
touch set.ref
```

3. Edit it with your favorite editor and follow this template:

```
=== CPP98: std::set ===

HEADER:
#include <set>

DECLARATION:
std::set<Type> myset;

COMMON METHODS:
insert(val)    - Add element
erase(val)     - Remove element
find(val)      - Find element
...

BASIC USAGE:
std::set<int> numbers;
numbers.insert(42);
...

GOTCHAS:
- No duplicates allowed
- Automatically sorted
...

RELATED:
map, vector, multiset
```

4. Test it:
```
Jarvis > ref set
```

### Method 2: Copy from existing code

If you have a code snippet you want to reference:
```bash
cp my_useful_snippet.cpp references/cpp98/algorithms/my_snippet.ref
```

---

## Reference File Format Tips

**Good structure:**
- Start with `===` header
- Use UPPERCASE: for section names (HEADER:, USAGE:, etc.)
- Include practical examples
- Add 42-specific notes if relevant
- List related topics at the end

**Useful sections:**
- HEADER / IMPORT
- DECLARATION / PROTOTYPE
- COMMON METHODS
- BASIC USAGE
- ADVANCED USAGE
- GOTCHAS / COMMON MISTAKES
- 42 SPECIFIC NOTES
- CPP98 CONSTRAINTS (what you CAN'T use)
- RELATED

**Color coding (automatic in ref.py):**
- Lines with `===` → Cyan (headers)
- Lines ending with `:` in UPPERCASE → Green (sections)
- Comments (`//` or `#`) → Gray
- Everything else → Normal

---

## Suggested References to Add Next

### For CPP Modules:
- `references/cpp98/containers/set.ref`
- `references/cpp98/containers/list.ref`
- `references/cpp98/containers/stack.ref`
- `references/cpp98/containers/queue.ref`
- `references/cpp98/containers/deque.ref`
- `references/cpp98/iterators/iterator.ref`
- `references/cpp98/algorithms/sort.ref`
- `references/cpp98/algorithms/find.ref`
- `references/cpp98/strings/string.ref`
- `references/cpp98/exceptions/exceptions.ref`
- `references/cpp98/casts/static_cast.ref`
- `references/cpp98/templates/function_templates.ref`
- `references/cpp98/templates/class_templates.ref`

### For Webserv:
- `references/cpp98/sockets/select.ref`
- `references/cpp98/sockets/poll.ref`
- `references/cpp98/http/request_parsing.ref`
- `references/cpp98/http/response_building.ref`
- `references/cpp98/file_io/file_operations.ref`

### For Python:
- `references/python/sys.ref`
- `references/python/os.ref`
- `references/python/argparse.ref`
- `references/python/pathlib.ref`
- `references/python/json.ref`

---

## Pro Tips 💡

1. **Add references as you learn**: Whenever you Google something, add it as a reference
2. **Include your mistakes**: Add GOTCHAS sections with errors you made
3. **42-specific notes**: Add norm compliance notes, forbidden functions, etc.
4. **Use examples from your projects**: Real code you wrote is the best reference
5. **Keep it concise**: You want quick lookups, not full documentation

---

## Troubleshooting

**"Reference not found"**
- Check spelling: `ref vectr` won't work, use `ref vector`
- Use `ref list` to see all available references
- Make sure the file ends with `.ref`

**"No references directory found"**
- Make sure `references/` folder exists in your Jarvis root
- Check the path in `ref.py` (REF_BASE variable)

**Colors not showing**
- Your terminal might not support ANSI colors
- The references still work, just without colors

**Command not recognized**
- Make sure you updated `commands.yaml`
- Put `ref list` and `ref search` BEFORE `ref` in the yaml file
- Restart Jarvis after changing commands.yaml

---

## Next Steps

1. ✅ Set up the basic system
2. ✅ Test with provided references
3. 📝 Add 5-10 references you use most often
4. 🚀 Use it daily and expand as needed
5. 🎯 Eventually have 50+ references covering all your needs

**Goal:** Never Google the same thing twice!

---

Happy coding! 🔥
