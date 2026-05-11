# 🚀 Setup Guide: Google Gemini Free Tier

## Quick Start (5 minutes)

### Step 1️⃣: Get Your Free API Key

1. Go to: **https://aistudio.google.com/app/apikey**
2. Click **"Create API Key"**
3. Click **"Create API key in new project"**
4. **Copy the key** (looks like: `AIzaSy...xyz123`)
5. Keep it **secret!** Don't share or commit to git

---

### Step 2️⃣: Add API Key to Project

**Option A: Direct in config.py (Easy)**
```python
# In config.py, replace this:
GOOGLE_API_KEY = "YOUR_API_KEY_HERE"

# With your actual key:
GOOGLE_API_KEY = "AIzaSy...xyz123"
```

**Option B: Using .env file (Safer)**
1. Copy `.env.example` to `.env`
2. Replace `your_api_key_here_replace_this` with your actual key
3. Update `agent.py` to load from `.env`:
   ```python
   from dotenv import load_dotenv
   import os
   load_dotenv()
   GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
   ```

⚠️ **Note:** `.env` is in `.gitignore` so it won't be committed

---

### Step 3️⃣: Install Updated Dependencies

```cmd
# Make sure venv is active
(venv) pip install -r requirements.txt
```

This installs `langchain-google-genai` (replaces `langchain-ollama`)

---

### Step 4️⃣: Run the Assistant

```cmd
(venv) python main.py
```

You should see:
```
╭─────────────────────────────────────────────╮
│   🤖 Personal AI Assistant                  │
│   Powered by Google Gemini                  │
│                                             │
│   Type 'voice' to switch to voice input     │
│   Type 'exit' to quit                       │
╰─────────────────────────────────────────────╯
⏳ Loading agent...
✓ Agent ready! Ask me anything.

You: 
```

---

### Step 5️⃣: Test It!

```
You: what is my IP address
```

**Expected:** Response in **2–3 seconds** ⚡ (much faster!)

---

## 📊 Gemini Free Tier Limits

| Feature | Limit | Status |
|---------|-------|--------|
| Requests per minute | 60 | ✅ Plenty |
| Daily usage | Unlimited | ✅ Free |
| Cost | $0 | ✅ Free |
| Model | Gemini 1.5 Flash | ✅ Fast & capable |

**You'll never hit these limits** for personal use.

---

## ⚠️ Important Notes

1. **Keep API key secret** — Never share or commit to git
2. **Internet required** — Gemini is cloud-based (no offline mode)
3. **No monthly costs** — Free tier is truly free
4. **Better quality** — Gemini is smarter than local mistral
5. **Faster responses** — 2–3 seconds instead of 8–12 seconds

---

## 🔧 If You Change Your Mind

Want to go back to local mistral?

1. Revert `requirements.txt` to use `langchain-ollama`
2. Revert `agent.py` to use `ChatOllama` 
3. Revert `config.py` to use `OLLAMA_MODEL`
4. Run: `pip install -r requirements.txt`

It's easy to switch back!

---

## ❓ Troubleshooting

**Error: "API key not valid"**
- Check your key is correct (copy-paste again from Google AI Studio)
- Make sure you didn't add extra spaces

**Error: "Quota exceeded"**
- You hit the 60 requests/minute limit
- Wait 1 minute and try again
- (Almost impossible for personal use)

**Error: "Network error"**
- Check your internet connection
- Gemini requires internet to work

---

**Ready?** Add your API key to config.py and run `python main.py`! 🚀
