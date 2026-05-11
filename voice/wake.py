"""
Wake-word detector using VOSK (offline ASR) to spot a simple phrase like "okay javis".

This module exposes `start_wake_service(on_wake)` and `stop_wake_service()`.
The service runs a low-priority background thread that streams microphone audio
to a small VOSK model and calls `on_wake()` when the configured wake phrase is detected.

Notes:
- Requires `vosk` and `sounddevice` installed and a VOSK model downloaded.
- Set `VOSK_MODEL_PATH` in `config.py` to point to the model directory.
"""

import threading
import queue
import time
import json
import os
import re
import sys

# Allow running this file directly from the `voice` folder.
if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

try:
    from vosk import Model, KaldiRecognizer
    import sounddevice as sd
except Exception:
    Model = None
    KaldiRecognizer = None
    sd = None

import config

_thread = None
_q = None
_running = False
_last_trigger = 0
_debug_enabled = False


def _resolve_input_device(sd_module):
    """Pick input device in this order: configured -> default -> first valid."""
    try:
        devices = sd_module.query_devices()

        # 1) Explicit config index
        raw = str(getattr(config, "VOICE_INPUT_DEVICE", "")).strip()
        if raw:
            idx = int(raw)
            if 0 <= idx < len(devices) and (devices[idx].get("max_input_channels", 0) or 0) > 0:
                return idx

        # 2) PortAudio default input index
        default_input = None
        try:
            default_input = sd_module.default.device[0]
        except Exception:
            default_input = None
        if isinstance(default_input, int) and 0 <= default_input < len(devices):
            if (devices[default_input].get("max_input_channels", 0) or 0) > 0:
                return default_input

        # 3) First device with input channels
        for i, d in enumerate(devices):
            if (d.get("max_input_channels", 0) or 0) > 0:
                return i
    except Exception:
        return None
    return None


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _is_wake_phrase_detected(text: str) -> bool:
    """Fuzzy-ish matching for common wake phrase variants."""
    t = _normalize_text(text)
    if not t:
        return False

    canonical = _normalize_text(getattr(config, "WAKEWORD_PHRASE", "okay javis"))
    aliases = {
        canonical,
        "okay javis",
        "ok javis",
        "okay jarvis",
        "ok jarvis",
        "hello javis",
        "hello jarvis",
        "hey javis",
        "hey jarvis",
    }
    return any(a in t for a in aliases)


def _wake_aliases():
    canonical = _normalize_text(getattr(config, "WAKEWORD_PHRASE", "okay javis"))
    return sorted({
        canonical,
        "okay javis",
        "ok javis",
        "okay jarvis",
        "ok jarvis",
        "hello javis",
        "hello jarvis",
        "hey javis",
        "hey jarvis",
    })


def _audio_callback(indata, frames, time_info, status):
    if status:
        pass
    try:
        _q.put(indata.copy().tobytes())
    except Exception:
        pass


def _wake_loop(on_wake):
    global _running, _last_trigger

    model_path = getattr(config, "VOSK_MODEL_PATH", None)
    if not model_path or not os.path.exists(model_path):
        print("[wake] VOSK model not found. Set config.VOSK_MODEL_PATH to a downloaded model path.")
        _running = False
        return

    model = Model(model_path)
    sample_rate = int(config.VOICE_SAMPLE_RATE)

    # Bias recognizer toward wake phrases for higher recall.
    aliases = _wake_aliases()
    try:
        rec = KaldiRecognizer(model, sample_rate, json.dumps(aliases))
    except Exception:
        rec = KaldiRecognizer(model, sample_rate)

    print(f"[wake] Listening for wake phrase: '{config.WAKEWORD_PHRASE}'")
    if _debug_enabled:
        print(f"[wake][debug] aliases={aliases}")

    input_device = _resolve_input_device(sd)
    try:
        devices = sd.query_devices()
        if input_device is not None and 0 <= input_device < len(devices):
            print(f"[wake] Using input device {input_device}: {devices[input_device].get('name', 'unknown')}")
        else:
            print("[wake] Using system default input device")
    except Exception:
        pass

    try:
        with sd.InputStream(
            samplerate=sample_rate,
            channels=1,
            dtype="int16",
            callback=_audio_callback,
            device=input_device,
        ):
            last_partial = ""
            while _running:
                try:
                    data = _q.get(timeout=0.5)
                except queue.Empty:
                    continue

                if rec.AcceptWaveform(data):
                    try:
                        res = json.loads(rec.Result())
                    except Exception:
                        continue
                    text = res.get("text", "").lower()
                    if not text:
                        continue
                    if _is_wake_phrase_detected(text):
                        now = time.time()
                        if now - _last_trigger > (config.WAKEWORD_DEBOUNCE_MS / 1000.0):
                            _last_trigger = now
                            print(f"[wake] detected in final text: {text}")
                            try:
                                on_wake()
                            except Exception:
                                pass
                else:
                    # Check partial text too, so short wake phrases trigger quickly.
                    try:
                        pres = json.loads(rec.PartialResult())
                        ptext = pres.get("partial", "")
                    except Exception:
                        ptext = ""
                    if _debug_enabled and ptext and ptext != last_partial:
                        print(f"[wake][debug] partial: {ptext}")
                        last_partial = ptext
                    if ptext and _is_wake_phrase_detected(ptext):
                        now = time.time()
                        if now - _last_trigger > (config.WAKEWORD_DEBOUNCE_MS / 1000.0):
                            _last_trigger = now
                            print(f"[wake] detected in partial text: {ptext}")
                            try:
                                on_wake()
                            except Exception:
                                pass
    except Exception as e:
        print(f"[wake] audio stream error: {e}")
        _running = False


def start_wake_service(on_wake):
    """Start the background wake-word service.

    on_wake: callable invoked with no args when wake phrase detected.
    """
    global _thread, _q, _running, _debug_enabled
    if Model is None or sd is None:
        raise ImportError("VOSK or sounddevice not installed. Install: pip install vosk sounddevice")

    if _running:
        return

    _q = queue.Queue(maxsize=200)
    _debug_enabled = str(getattr(config, "WAKEWORD_DEBUG", "0")).strip().lower() in {"1", "true", "yes", "on"}
    _running = True
    _thread = threading.Thread(target=_wake_loop, args=(on_wake,), daemon=True)
    _thread.start()


def stop_wake_service():
    global _running, _thread
    _running = False
    try:
        if _thread and _thread.is_alive():
            _thread.join(timeout=1)
    except Exception:
        pass


if __name__ == "__main__":
    # Standalone wake detector test runner.
    print("[wake] standalone test mode. Press Ctrl+C to stop.")

    def _on_wake():
        print("[wake] ✅ wake callback fired")

    start_wake_service(_on_wake)
    try:
        while True:
            time.sleep(0.2)
    except KeyboardInterrupt:
        stop_wake_service()
        print("\n[wake] stopped")
