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

# Recording duration in seconds (target 1-3s capture latency)
VOICE_DURATION = 3

# Retry duration for manual `voice` command when first capture is silent.
VOICE_RETRY_DURATION = int(os.getenv("VOICE_RETRY_DURATION", "5"))

# Whisper expects 16kHz mono audio for best compatibility/performance.
# (If you meant 26Hz, that is too low for speech recognition.)
VOICE_SAMPLE_RATE = 16000

# Optional input device selector for wake-word and STT capture.
# Set to an integer device index from sounddevice query, e.g. "1".
# Leave empty to use system default input device.
VOICE_INPUT_DEVICE = os.getenv("VOICE_INPUT_DEVICE", "").strip()

# Enable text-to-speech for assistant responses (manual voice flows)
VOICE_TTS_ENABLED = os.getenv("VOICE_TTS_ENABLED", "0")
VOICE_TTS_RATE = int(os.getenv("VOICE_TTS_RATE", "180"))
VOICE_TTS_VOLUME = float(os.getenv("VOICE_TTS_VOLUME", "0.9"))

# Lower beam size improves speed (1 is fastest).
VOICE_BEAM_SIZE = 1

# VAD silence threshold tuning (milliseconds)
VOICE_VAD_MIN_SILENCE_MS = 400

# If measured RMS is below this, treat input as silence.
VOICE_SILENCE_RMS_THRESHOLD = 0.008

# ─────────────────────────────────────────────
# WAKEWORD / HOTWORD SETTINGS
# ─────────────────────────────────────────────
# Phrase that triggers the assistant when heard (case-insensitive)
WAKEWORD_PHRASE = os.getenv("WAKEWORD_PHRASE", "okay javis")
# Enable/disable always-on wake-word listener.
# Set to "1"/"true" to enable. Default is disabled for manual `voice` mode.
WAKEWORD_ENABLED = os.getenv("WAKEWORD_ENABLED", "0")
# Minimum debounce between triggers (milliseconds)
WAKEWORD_DEBOUNCE_MS = int(os.getenv("WAKEWORD_DEBOUNCE_MS", "2000"))
# Enable verbose wake detection logs (1/true to enable)
WAKEWORD_DEBUG = os.getenv("WAKEWORD_DEBUG", "0")
# Wait briefly after wake detection before starting capture
WAKE_POST_TRIGGER_DELAY_MS = int(os.getenv("WAKE_POST_TRIGGER_DELAY_MS", "500"))
# Recording length for the command spoken after wake phrase
WAKE_COMMAND_DURATION = int(os.getenv("WAKE_COMMAND_DURATION", "4"))
# Retry once with this duration if first post-wake capture is silent
WAKE_RETRY_DURATION = int(os.getenv("WAKE_RETRY_DURATION", "5"))
# Path to a downloaded VOSK model directory for wake detection
# Default is resolved after `BASE_DIR` is defined below.
VOSK_MODEL_PATH = os.getenv("VOSK_MODEL_PATH", None)

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

# Resolve VOSK_MODEL_PATH default now that BASE_DIR is available
if not VOSK_MODEL_PATH:
    VOSK_MODEL_PATH = os.path.join(BASE_DIR, "voice_models", "vosk-model-small-en-us-0.15")
