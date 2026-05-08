"""
Voice - Speech to Text using faster-whisper (runs locally, no API needed)
"""

import os
import tempfile


def listen(duration: int = 5, samplerate: int = 16000) -> str:
    """
    Record audio from microphone and transcribe to text.
    
    Args:
        duration: How many seconds to record (default 5)
        samplerate: Audio sample rate (16000 for Whisper)
    
    Returns:
        Transcribed text string
    """
    try:
        import sounddevice as sd
        import numpy as np
        from scipy.io.wavfile import write
        from faster_whisper import WhisperModel
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Install with: pip install faster-whisper sounddevice scipy numpy")
        return ""

    print(f"🎤 Listening for {duration} seconds... (speak now)")
    
    try:
        # Record audio
        audio = sd.rec(
            int(duration * samplerate),
            samplerate=samplerate,
            channels=1,
            dtype="int16"
        )
        sd.wait()
        print("✅ Recording done. Transcribing...")

        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name
            write(tmp_path, samplerate, audio)

        # Transcribe with Whisper
        # Using "base" model - good speed/accuracy balance
        # Options: tiny, base, small, medium (larger = more accurate but slower)
        model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, info = model.transcribe(tmp_path, beam_size=5)
        
        text = " ".join(segment.text.strip() for segment in segments).strip()
        
        # Cleanup temp file
        os.unlink(tmp_path)

        if text:
            print(f"📝 You said: {text}")
        else:
            print("❌ Could not hear anything clearly.")
        
        return text

    except Exception as e:
        print(f"❌ Voice error: {e}")
        return ""


if __name__ == "__main__":
    # Test voice input directly
    result = listen()
    print(f"Result: {result}")
