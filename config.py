"""
Configuration — Edit these settings to customize your assistant
"""

import os

# ─────────────────────────────────────────────
# AI MODEL SETTINGS (Ollama - Local, 100% Free)
# ─────────────────────────────────────────────

# ⚠️ IMPORTANT: Make sure Ollama is running!
# Download from: https://ollama.ai
# Start Ollama, then pull the model:
#   ollama pull mistral:latest
#
# This model is:
# - Supports function/tool calling (perfect for this project)
# - ~5GB download, 6-7GB runtime (fits in 8GB RAM)
# - Locally run (100% private, no data sent anywhere)

# Ollama model to use
# Best for tool calling: "mistral:latest" (proven tool support)
# Alternatives: "dolphin-mixtral:8x7b" (excellent quality)
OLLAMA_MODEL = "mistral:latest"  # Supports tool/function calling

# Model temperature: 0 = focused/deterministic, 1 = creative
OLLAMA_TEMPERATURE = 0

# Max tokens in response (lower = faster responses)
# Recommended: 256 for functionary on 8GB RAM
OLLAMA_MAX_TOKENS = 256

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
