"""
Configuration — Edit these settings to customize your assistant
"""

import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# ─────────────────────────────────────────────
# AI MODEL SETTINGS (Google Gemini)
# ─────────────────────────────────────────────

# Put your key in .env:
# GOOGLE_API_KEY=your_key_here
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Gemini model to use
# Fast and smooth for development: "gemini-2.0-flash"
# Higher quality: "gemini-2.0-pro"
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# Model temperature: 0 = focused/deterministic, 1 = creative
GEMINI_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", "0"))

# Max tokens in response (lower = faster responses)
GEMINI_MAX_TOKENS = int(os.getenv("GEMINI_MAX_TOKENS", "256"))

# ─────────────────────────────────────────────
# VOICE SETTINGS
# ─────────────────────────────────────────────

# Whisper model size: tiny, base, small, medium
# tiny  = fastest, least accurate (~75MB)
# base  = good balance (~145MB)  ← RECOMMENDED
# small = more accurate (~466MB)
WHISPER_MODEL = "base"

# Recording duration in seconds
VOICE_DURATION = 5

# ─────────────────────────────────────────────
# SAFETY SETTINGS
# ─────────────────────────────────────────────

# Words that trigger a safety confirmation before executing
DANGEROUS_KEYWORDS = [
    "delete", "remove", "format", "rm -rf",
    "del ", "rmdir", "erase", "wipe"
]

# ─────────────────────────────────────────────
# MEMORY SETTINGS
# ─────────────────────────────────────────────

# How many conversation exchanges to remember in one session
MEMORY_MAX_EXCHANGES = 10

# ─────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
AUDIO_DIR = os.path.join(DATA_DIR, "audio")
CONVERSATIONS_DIR = os.path.join(DATA_DIR, "conversations")
