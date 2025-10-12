# 🧠 Personal Python Assistant

A lightweight personal assistant built with Python to help you explore documentation, concepts, and technical references directly from your terminal.  
Use simple `ref` commands to quickly browse and fetch documentation — no need to leave your environment.

---

## 🚀 Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/personal-assistant.git
cd personal-assistant
```

---

### 2. Create a Virtual Environment

#### On Linux / macOS:
```bash
python3 -m venv env
source env/bin/activate
```

#### On Windows:
```bash
python -m venv env
\.env\Scripts\activate
```

Once activated, your terminal prompt should start with `(.venv)`.

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🧭 Usage

The assistant operates through the `ref` command.

### run jarvis cli
```bash
python3 jarvis.py
```

### 🗂 List Available Documentation

To list all available reference topics:
```bash
ref # view commands with ref
ref "list"
```

This command displays all indexed documentation and concept files that can be explored.

---

### 📚 search a Specific Concept

After listing topics, you can open any documentation by referencing its name:

```bash
ref search "concept"
```

---


Each file represents one topic or concept.  
Once added, you can access it immediately using `ref "<filename or concept>"`.

---

## 🛠 Example Session

``` bash
ref list
##### doc names appear
ref search #for a keyword in some docs 

ref (doc_name) # opens like a man page
```

---

## 🧼 Deactivate the Virtual Environment

When finished, deactivate the environment using:

```bash
deactivate
```

---

## 💡 Tips
- Always activate `.venv` before running the assistant.
- Keep `requirements.txt` updated with:
```bash
pip freeze > requirements.txt
```
- To make `ref` a global terminal command, you can set an alias in your shell config:
```bash
alias ref='python /path/to/personal-assistant/main.py'
```

---

**Built with ❤️ and Python.**
