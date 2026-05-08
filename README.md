# 🤖 Personal AI Assistant

A Windows AI assistant running 100% locally using Ollama + LangChain.
No cloud. No API keys. No cost. Full privacy.

## Quick Start

```cmd
# 1. Activate virtual environment
venv\Scripts\activate

# 2. Install packages
pip install -r requirements.txt

# 3. Pull AI model (one time only)
ollama pull llama3.1

# 4. Run the assistant
python main.py
```

## Read the full guide
👉 See **IMPLEMENTATION_PLAN.md** for complete step-by-step instructions.

## What it can do
- 📁 Create, list, read files and folders
- 💻 Run Windows shell commands
- 🌐 Search the web (DuckDuckGo, free)
- 📊 Get system info (IP, RAM, CPU, disk)
- 🚀 Open any application
- 🎤 Voice input (optional, uses Whisper)
