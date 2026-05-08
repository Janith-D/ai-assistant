# 🤖 Personal AI Assistant — Complete Implementation Plan

> **Your Goal:** Build a Windows AI assistant that runs 100% locally using Ollama + LangChain, controllable from the terminal, that can manage files, run commands, search the web, and respond to voice.

---

## 📋 Table of Contents

1. [Before You Start — Prerequisites](#1-before-you-start--prerequisites)
2. [Phase 1 — Environment Setup](#2-phase-1--environment-setup)
3. [Phase 2 — Test Ollama Works](#3-phase-2--test-ollama-works)
4. [Phase 3 — Run the Terminal Assistant](#4-phase-3--run-the-terminal-assistant)
5. [Phase 4 — Add Voice Input](#5-phase-4--add-voice-input)
6. [Phase 5 — Add More Tools](#6-phase-5--add-more-tools)
7. [Phase 6 — Desktop Tray App (Electron)](#7-phase-6--desktop-tray-app-electron)
8. [Phase 7 — Long-Term Memory](#8-phase-7--long-term-memory)
9. [Phase 8 — Package & Ship](#9-phase-8--package--ship)
10. [Troubleshooting](#10-troubleshooting)
11. [Test Commands to Try](#11-test-commands-to-try)
12. [Project Architecture Explained](#12-project-architecture-explained)

---

## 1. Before You Start — Prerequisites

### What You Need on Your Windows PC

| Requirement | Minimum | Recommended |
|---|---|---|
| RAM | 8 GB | 16 GB |
| Storage | 10 GB free | 20 GB free |
| CPU | Any modern CPU | 8+ cores |
| GPU | Not required | NVIDIA (faster LLM) |
| OS | Windows 10 | Windows 11 |

### Software to Install First (do this before anything else)

#### Step 1.1 — Install Python
1. Go to https://python.org/downloads
2. Download Python **3.11** (not 3.12 — some packages have issues)
3. **IMPORTANT:** During install, check ✅ "Add Python to PATH"
4. Verify: open CMD and type `python --version` → should show 3.11.x

#### Step 1.2 — Install Git
1. Go to https://git-scm.com/download/win
2. Download and install with all default options
3. Verify: open CMD and type `git --version`

#### Step 1.3 — Install Ollama
1. Go to https://ollama.com
2. Click Download for Windows
3. Run the installer
4. After install, open CMD and type `ollama --version`
5. If it shows a version number, Ollama is ready ✅

#### Step 1.4 — Install VS Code (recommended editor)
1. Go to https://code.visualstudio.com
2. Download and install
3. Install the Python extension inside VS Code

---

## 2. Phase 1 — Environment Setup

> **Goal:** Get the project folder ready with Python virtual environment

### Step 2.1 — Open the project folder

Navigate to where you cloned/unzipped this project:
```cmd
cd path\to\ai-assistant
```
For example:
```cmd
cd C:\Users\YourName\Desktop\ai-assistant
```

### Step 2.2 — Create a virtual environment

A virtual environment keeps your project's packages separate from other Python projects.

```cmd
python -m venv venv
```

You should see a new `venv/` folder appear.

### Step 2.3 — Activate the virtual environment

```cmd
venv\Scripts\activate
```

Your terminal prompt should now start with `(venv)` — this means it's active. ✅

> ⚠️ **IMPORTANT:** Every time you open a new terminal to work on this project, you must run `venv\Scripts\activate` again.

### Step 2.4 — Install all required packages

```cmd
pip install -r requirements.txt
```

This will install:
- `langchain` — the agent framework
- `langchain-ollama` — connects LangChain to your local Ollama
- `psutil` — reads system info (RAM, CPU, IP)
- `duckduckgo-search` — free web search, no API key needed
- `rich` — makes the terminal look nice

Wait for all packages to finish installing (may take 2–5 minutes).

### Step 2.5 — Verify everything installed

```cmd
python -c "import langchain; import psutil; import rich; print('All good!')"
```

If it prints `All good!` you're ready. ✅

---

## 3. Phase 2 — Test Ollama Works

> **Goal:** Make sure your local AI model is running before connecting it to the assistant

### Step 3.1 — Pull the AI model

This downloads Llama 3.1 (about 4.7 GB) to your computer:

```cmd
ollama pull llama3.1
```

Wait for the download to complete. This only needs to be done once.

> 💡 **Alternative smaller models** (if your RAM is limited):
> - `ollama pull phi3` → 2.3 GB, good for 8 GB RAM systems
> - `ollama pull mistral` → 4.1 GB, great instruction following
> - `ollama pull qwen2.5` → 4.7 GB, strong tool-use support

### Step 3.2 — Test the model in terminal

```cmd
ollama run llama3.1
```

Type "Hello, what can you do?" and press Enter.

If the AI responds → Ollama is working perfectly ✅

Press `Ctrl+D` or type `/bye` to exit the Ollama chat.

### Step 3.3 — Verify Ollama API is accessible

Ollama runs as a local server on port 11434. Test it:

```cmd
curl http://localhost:11434/api/tags
```

Or open this URL in your browser: `http://localhost:11434/api/tags`

You should see a JSON response with model information. ✅

> ⚠️ If Ollama isn't running, start it with: `ollama serve`

---

## 4. Phase 3 — Run the Terminal Assistant

> **Goal:** Get the full assistant working in your terminal

### Step 4.1 — Make sure venv is active

```cmd
venv\Scripts\activate
```

### Step 4.2 — Run the assistant

```cmd
python main.py
```

You should see:
```
╭─────────────────────────────────────────────╮
│   🤖 Personal AI Assistant                  │
│   Powered by Llama 3.1 — Running Locally    │
│                                             │
│   Type 'voice' to switch to voice input     │
│   Type 'exit' to quit                       │
╰─────────────────────────────────────────────╯
⏳ Loading agent...
✓ Agent ready! Ask me anything.

You:
```

### Step 4.3 — Try these test commands

Test each one to confirm everything works:

```
You: what is my IP address
You: what is my RAM usage  
You: create a folder called TestProject on my Desktop
You: list the files in C:\Users
You: search the web for Python tutorials
You: open notepad
You: run the command ipconfig
```

### Step 4.4 — Understanding what happens internally

When you type a request, this is what happens:

```
Your text input
      ↓
LangChain Agent (decides which tool to use)
      ↓
Ollama/Llama 3.1 (understands your intent)
      ↓
Tool is called (e.g., create_folder, run_command)
      ↓
Tool returns result
      ↓
LLM summarizes result in natural language
      ↓
You see the response
```

### Step 4.5 — Customize the model (optional)

If you want to use a different model, edit `config.py`:

```python
OLLAMA_MODEL = "mistral"   # or phi3, qwen2.5, etc.
```

---

## 5. Phase 4 — Add Voice Input

> **Goal:** Speak to the assistant instead of typing

### Step 5.1 — Install voice dependencies

```cmd
pip install faster-whisper sounddevice scipy numpy
```

> ⚠️ `faster-whisper` downloads a Whisper model (~145 MB for "base") on first use.

### Step 5.2 — Test your microphone

Make sure Windows can detect your microphone:
1. Right-click the speaker icon in taskbar → Sound Settings
2. Under Input, check your microphone is listed and active

### Step 5.3 — Test voice input alone

```cmd
python voice\stt.py
```

Speak something when it says "Listening...". It should print what you said.

### Step 5.4 — Use voice in the assistant

When the assistant is running, type `voice` to activate voice mode:

```
You: voice
🎤 Listening for 5 seconds... (speak now)
✅ Recording done. Transcribing...
📝 You said: what is my IP address
```

The assistant will then process your spoken command. ✅

### Step 5.5 — Change recording duration (optional)

If 5 seconds isn't enough time, edit `config.py`:

```python
VOICE_DURATION = 8   # Record for 8 seconds instead
```

---

## 6. Phase 5 — Add More Tools

> **Goal:** Expand what the assistant can do by adding new tools

### How to Add a New Tool

Every tool follows the same pattern. Here's the template:

```python
# In tools/your_tool_file.py

from langchain.tools import tool

@tool
def your_tool_name(parameter: str) -> str:
    """
    Clear description of what this tool does.
    This description is read by the AI to decide when to use it.
    Example: your_tool_name('some input')
    """
    # Your logic here
    result = do_something(parameter)
    return f"Result: {result}"
```

Then register it in `agent.py`:

```python
from tools.your_tool_file import your_tool_name

TOOLS = [
    run_command,
    create_folder,
    your_tool_name,   # ← Add here
    ...
]
```

### Tool Ideas to Build Next

#### Idea A — Screenshot Tool
```python
@tool
def take_screenshot(filename: str = "screenshot") -> str:
    """Take a screenshot of the current screen."""
    import pyautogui
    from datetime import datetime
    path = f"data/{filename}_{datetime.now().strftime('%H%M%S')}.png"
    pyautogui.screenshot(path)
    return f"✅ Screenshot saved: {path}"
```

#### Idea B — Clipboard Tool
```python
@tool
def get_clipboard() -> str:
    """Get the current text content from clipboard."""
    import pyperclip
    return pyperclip.paste()

@tool  
def set_clipboard(text: str) -> str:
    """Copy text to the clipboard."""
    import pyperclip
    pyperclip.copy(text)
    return f"✅ Copied to clipboard: {text[:50]}..."
```

#### Idea C — Weather Tool
```python
@tool
def get_weather(city: str) -> str:
    """Get current weather for a city using a free API."""
    import requests
    url = f"https://wttr.in/{city}?format=3"
    response = requests.get(url)
    return response.text
```

#### Idea D — Write File Tool
```python
@tool
def write_file(path: str, content: str) -> str:
    """Write content to a text file, creating it if it doesn't exist."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"✅ File written: {path}"
```

---

## 7. Phase 6 — Desktop Tray App (Electron)

> **Goal:** Replace the terminal with a proper Windows tray icon + floating window

> ⏱️ **When to start this phase:** Only after Phase 3 is working perfectly

### Step 7.1 — Install Node.js

1. Go to https://nodejs.org
2. Download the LTS version
3. Install with default settings
4. Verify: `node --version` and `npm --version`

### Step 7.2 — Create the Electron app

```cmd
mkdir electron-ui
cd electron-ui
npm init -y
npm install electron react react-dom tailwindcss
```

### Step 7.3 — Architecture

The Electron app and Python backend communicate via WebSocket:

```
Windows Tray Icon (Electron)
         ↓ click
   Floating UI Window (React)
         ↓ user types/speaks
   WebSocket message to Python
         ↓
   LangChain Agent processes
         ↓
   WebSocket response back
         ↑
   UI shows result
```

### Step 7.4 — Add WebSocket server to Python

Install in your venv:
```cmd
pip install websockets
```

Create `server.py`:
```python
import asyncio
import websockets
import json
from agent import build_agent

agent = build_agent()

async def handle(websocket):
    async for message in websocket:
        data = json.loads(message)
        response = agent.invoke({"input": data["text"], "chat_history": []})
        await websocket.send(json.dumps({"output": response["output"]}))

async def main():
    async with websockets.serve(handle, "localhost", 8765):
        print("✅ Assistant server running on ws://localhost:8765")
        await asyncio.Future()

asyncio.run(main())
```

Start the backend with:
```cmd
python server.py
```

### Step 7.5 — Electron connects to Python

In your Electron app's renderer, connect to the Python WebSocket:

```javascript
const ws = new WebSocket('ws://localhost:8765');

function sendMessage(text) {
    ws.send(JSON.stringify({ text }));
}

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    displayResponse(data.output);
};
```

---

## 8. Phase 7 — Long-Term Memory

> **Goal:** The assistant remembers facts between sessions

### Step 8.1 — Install ChromaDB

```cmd
pip install chromadb sentence-transformers
```

### Step 8.2 — Create `memory/long_term.py`

```python
import chromadb
from sentence_transformers import SentenceTransformer

class LongTermMemory:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="data/memory")
        self.collection = self.client.get_or_create_collection("assistant_memory")
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")

    def save(self, text: str, metadata: dict = {}):
        embedding = self.encoder.encode(text).tolist()
        self.collection.add(
            documents=[text],
            embeddings=[embedding],
            metadatas=[metadata],
            ids=[str(hash(text))]
        )

    def search(self, query: str, top_k: int = 3) -> list:
        embedding = self.encoder.encode(query).tolist()
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k
        )
        return results["documents"][0] if results["documents"] else []
```

### Step 8.3 — Inject memories into agent prompt

Modify `agent.py` to load relevant memories before each query:

```python
memory = LongTermMemory()

def ask_with_memory(agent, user_input, chat_history):
    # Find relevant past memories
    past = memory.search(user_input)
    memory_context = "\n".join(past) if past else "No relevant memories."
    
    enriched_input = f"[Past context: {memory_context}]\n\nUser: {user_input}"
    return agent.invoke({"input": enriched_input, "chat_history": chat_history})
```

---

## 9. Phase 8 — Package & Ship

> **Goal:** Create a Windows installer so others can use your assistant

### Step 9.1 — Create executable with PyInstaller

```cmd
pip install pyinstaller
pyinstaller --onefile --name "AIAssistant" main.py
```

The `.exe` file appears in the `dist/` folder.

### Step 9.2 — Package Electron app

```cmd
cd electron-ui
npm install electron-builder --save-dev
npm run build
```

### Step 9.3 — Create Windows installer

Use **Inno Setup** (free):
1. Download from https://jrsoftware.org/isinfo.php
2. Create a script that bundles:
   - Your Python executable
   - The Electron app
   - Ollama (or installer link)
3. Build the installer `.exe`

---

## 10. Troubleshooting

### ❌ "ollama not found" or command not recognized
- Restart your terminal after installing Ollama
- Add Ollama to PATH manually if needed
- Try running: `C:\Users\YourName\AppData\Local\Programs\Ollama\ollama.exe`

### ❌ "Connection refused" to Ollama
- Make sure Ollama is running: open Task Manager → check for ollama.exe
- Start it manually: `ollama serve`
- Default port is 11434 — make sure no firewall is blocking it

### ❌ Agent doesn't use tools, just answers from knowledge
- Set `verbose=True` in `agent.py` to see reasoning
- Try rephrasing: "Use the tool to create a folder called X"
- Some models are better at tool use — try `qwen2.5` or `mistral`

### ❌ Voice not working / "No module named sounddevice"
- Install voice packages: `pip install sounddevice scipy numpy faster-whisper`
- Check your microphone in Windows Sound Settings
- Try a different audio device

### ❌ Slow responses (30+ seconds)
- Normal for CPU-only mode with large models
- Switch to a smaller model: `OLLAMA_MODEL = "phi3"` in config.py
- If you have an NVIDIA GPU: `pip install llama-cpp-python[cuda]`

### ❌ "Permission denied" when running commands
- Run CMD as Administrator
- Some system commands require elevated privileges

---

## 11. Test Commands to Try

Once your assistant is running, test these to verify everything works:

### System Info Tests
```
what is my IP address
show me my RAM usage
how much disk space do I have
what is my CPU usage right now
give me all system information
```

### File System Tests
```
create a folder called TestProject on my Desktop
list the files in my Downloads folder
list files in C:\Users
read the file C:\Users\YourName\Desktop\notes.txt
```

### Shell Command Tests
```
run ipconfig
run the command systeminfo
ping google.com
show me running processes
what version of Python do I have
```

### App Control Tests
```
open notepad
open calculator
open file explorer
open command prompt
```

### Web Search Tests
```
search the web for Python LangChain tutorial
search for Windows 11 keyboard shortcuts
look up the latest news about AI
```

---

## 12. Project Architecture Explained

### How Files Connect to Each Other

```
main.py              ← You run this. Controls the UI loop.
   │
   └── agent.py      ← Builds the LangChain agent with all tools
         │
         ├── tools/filesystem.py   ← create_folder, list_directory, read_file
         ├── tools/shell.py        ← run_command, open_application
         ├── tools/system_info.py  ← get_system_info (IP, RAM, CPU, disk)
         └── tools/web_search.py   ← search_web (DuckDuckGo)

voice/stt.py         ← Optional: records mic + transcribes with Whisper
config.py            ← All settings in one place (model, paths, voice duration)
```

### How the Agent Thinks

The LangChain agent uses a **ReAct** (Reasoning + Acting) loop:

```
1. READ your message
2. THINK: "What does the user want? Which tool should I use?"
3. ACT: Call the right tool with the right parameters
4. OBSERVE: See what the tool returned
5. RESPOND: Summarize the result in natural language
```

This is why you don't need `if "open chrome" in text:` rules. The AI figures
out intent automatically and picks the right tool.

### Why Local AI (Ollama) Instead of Cloud

| | Local (Ollama) | Cloud (GPT/Claude) |
|---|---|---|
| Cost | Free forever | Pay per request |
| Privacy | Data never leaves PC | Data sent to servers |
| Speed | 2–10 sec (CPU) | 0.5–2 sec |
| Offline | Works without internet | Requires internet |
| Quality | Good (Llama 3.1) | Excellent |

For a personal PC assistant, **local wins** because of privacy and zero cost.

---

## 🗓️ Suggested Weekly Schedule

| Week | Focus | Goal |
|---|---|---|
| Week 1 | Phases 1–3 | Terminal assistant working |
| Week 2 | Phase 4–5 | Voice + extra tools |
| Week 3 | Phase 6 start | Electron tray UI shell |
| Week 4 | Phase 6 complete | Full desktop app |
| Week 5 | Phase 7 | Long-term memory |
| Week 6 | Phase 8 | Installer + polish |

---

## 📚 Resources

- **Ollama docs:** https://ollama.com/docs
- **LangChain agents:** https://python.langchain.com/docs/modules/agents
- **faster-whisper:** https://github.com/SYSTRAN/faster-whisper
- **Electron docs:** https://electronjs.org/docs
- **ChromaDB:** https://docs.trychroma.com
- **Rich terminal:** https://rich.readthedocs.io

---

*Built with ❤️ using Python + LangChain + Ollama — 100% local, 100% private.*
