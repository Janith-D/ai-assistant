# 🤖 Personal AI Assistant

A Windows AI assistant using Google Gemini + LangChain.
Fast startup, smooth responses, and no local model load during development.

## Quick Start

```cmd
# 1. Add your Gemini API key to .env
#    GOOGLE_API_KEY=your_key_here
#    GEMINI_MODEL=gemini-2.5-flash

# 2. Activate virtual environment
venv\Scripts\activate

# 3. Install packages
pip install -r requirements.txt

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
