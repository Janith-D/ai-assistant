"""
Voice Text-to-Speech helper (optional).
Uses pyttsx3 for offline local speech output.
"""

from __future__ import annotations


def speak_text(text: str) -> None:
    if not text:
        return

    try:
        import pyttsx3
        import config

        enabled = str(getattr(config, "VOICE_TTS_ENABLED", "0")).strip().lower() in {"1", "true", "yes", "on"}
        if not enabled:
            return

        engine = pyttsx3.init()
        try:
            engine.setProperty("rate", int(getattr(config, "VOICE_TTS_RATE", 180)))
            engine.setProperty("volume", float(getattr(config, "VOICE_TTS_VOLUME", 0.9)))
        except Exception:
            pass

        engine.say(text)
        engine.runAndWait()
    except Exception:
        # TTS should never break the assistant flow.
        return
