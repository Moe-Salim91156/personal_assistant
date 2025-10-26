# 🧠 Jarvis — Personal Python Assistant

A lightweight, modular **automation and reference assistant** built in Python.  
Jarvis helps you run scripts, parse natural commands (via Ollama or local NLP), and explore documentation — all from your terminal.

---

## 📁 Project Structure

```
personal_assistant/
├── jarvis.py              # Main entry point (CLI assistant)
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
│
├── core/
│   ├── parser.py          # Natural Language Parser (Ollama or local)
│   ├── runner_manager.py  # Handles command execution and context
│   └── __pycache__/       # Cached Python files
│
├── plugins/
│   ├── run_scripts/       # Custom user Bash/Python scripts for Jarvis
│   └── open_apps/         # (coming soon) Plugin for app control
│
├── references/
│   ├── cpp98              # C++ reference notes
│   └── python             # Python reference notes
│
└── env/                   # Virtual environment (optional local setup)
```

---

## ⚙️ Setup & Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/personal_assistant.git
cd personal_assistant
```

---

### 2️⃣ Create and Activate a Virtual Environment

**On Linux/macOS:**
```bash
python3 -m venv env
source env/bin/activate
```

**On Windows:**
```bash
python -m venv env
env\Scripts\activate
```

---

### 3️⃣ Install Requirements

```bash
pip install -r requirements.txt
```

---

## 🚀 Usage

### 🧩 Start the Assistant

```bash
python3 jarvis.py
```

You’ll enter the **Jarvis CLI**, where you can run commands such as:

```bash
Jarvis > run my cleanup script
Jarvis > push my repo to github
Jarvis > open reference python
Jarvis > ref search oop
```

Jarvis automatically parses your text, identifies the action (plugin), and executes it.

---

## 🧠 Features

✅ **Command Parsing** — Uses Ollama or lightweight NLP to interpret commands.  
✅ **Script Runner** — Executes your Bash/Python scripts dynamically from `plugins/run_scripts`.  
✅ **Reference Fetcher** — Pulls up documentation or notes instantly from `references/`.  
✅ **Extensible Architecture** — Add your own plugins and features without touching the core logic.  
✅ **Local and Offline** — Runs entirely on your machine; no external API calls.  
✅ **Voice Support (Coming Soon)** — Local speech-to-text and voice command execution.  

---

## 🔧 Adding New Plugins

1. Create a new `.py` or `.sh` file inside `plugins/run_scripts/`.  
2. The assistant will automatically detect and execute it when you issue related commands.

Example:
```bash
plugins/run_scripts/deploy.sh
```
Run it:
```bash
Jarvis > deploy project
```

---

## 🧩 NLP Parser (Core Idea)

The assistant currently uses **Ollama** to parse text commands into structured JSON:  
```json
{
  "plugin": "git_ops",
  "target": "push_repo",
  "args": {}
}
```

Later, you can train your **own small NLP model** to replace Ollama:
- Log commands + parsed JSON.
- Train a small classifier (e.g., SVM or FastText).
- Use it locally for near-instant parsing.
- (Future) Fine-tune or train a lightweight transformer for higher accuracy.

---

## 🧱 Roadmap

| Phase | Goal | Description |
|-------|------|-------------|
| ✅ v1 | Core CLI & Parser | Basic command interpretation and execution |
| 🚧 v2 | Local NLP Engine | Fine-tuned or rule-based model replacing LLM |
| 🔜 v3 | Plugin Expansion | New plugins like `open_apps`, `system_ops`, etc. |
| 🔜 v4 | Voice Command Integration | Lightweight speech-to-text and CLI control |
| 🔜 v5 | Advanced NLP Fine-tuning | Higher accuracy and context awareness |

---

## 💡 Tips

- Use `pip freeze > requirements.txt` to keep your dependencies updated.  
- Set a shell alias to run Jarvis globally:
  ```bash
  alias jarvis='python /path/to/personal_assistant/jarvis.py'
  ```
- Keep reference docs in `references/` for instant access.

---

## 🧰 Tech Stack

- **Python 3.10+**
- **Ollama (LLM backend, optional)**
- **scikit-learn / FastText (future NLP)**
- **Bash / Python Plugins**
- **Local File-Based Memory**

---

**Built by Mohammad Isleem**  
✨ Empowering automation through simplicity and local intelligence.
