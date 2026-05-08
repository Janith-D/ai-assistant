"""
Configuration — Edit these settings to customize your assistant
"""

# ─────────────────────────────────────────────
# AI MODEL SETTINGS
# ─────────────────────────────────────────────

# Ollama model to use (must be pulled first with: ollama pull <model>)
# Options: llama3.1, mistral, phi3, qwen2.5
OLLAMA_MODEL = "llama3.1"

# Model temperature: 0 = focused/deterministic, 1 = creative
OLLAMA_TEMPERATURE = 0

# Max tokens in response
OLLAMA_MAX_TOKENS = 512

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

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
AUDIO_DIR = os.path.join(DATA_DIR, "audio")
CONVERSATIONS_DIR = os.path.join(DATA_DIR, "conversations")
