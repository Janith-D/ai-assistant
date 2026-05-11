"""
Voice - Speech to Text using faster-whisper (runs locally, no API needed)
"""

import os
import re
import tempfile
import warnings
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, asdict
from typing import Optional
import threading

_WHISPER_MODEL = None
_VOICE_EXECUTOR = ThreadPoolExecutor(max_workers=1)


@dataclass
class VoiceResult:
    ok: bool
    text: str = ""
    code: str = "ok"
    message: str = ""
    capture_ms: int = 0
    transcribe_ms: int = 0
    total_ms: int = 0


def _get_whisper_model():
    """Load Whisper model once and reuse it for faster repeated calls."""
    global _WHISPER_MODEL
    if _WHISPER_MODEL is not None:
        return _WHISPER_MODEL

    from faster_whisper import WhisperModel
    model_name = "base"
    try:
        import config
        model_name = getattr(config, "WHISPER_MODEL", "base")
    except Exception:
        model_name = "base"

    _WHISPER_MODEL = WhisperModel(model_name, device="cpu", compute_type="int8")
    return _WHISPER_MODEL


def preload_model() -> VoiceResult:
    """Preload whisper model once so first command is faster."""
    t0 = time.perf_counter()
    try:
        _get_whisper_model()
        total_ms = int((time.perf_counter() - t0) * 1000)
        return VoiceResult(ok=True, code="ok", message="Model ready", total_ms=total_ms)
    except Exception as e:
        total_ms = int((time.perf_counter() - t0) * 1000)
        return VoiceResult(ok=False, code="model_load_failure", message=str(e), total_ms=total_ms)


def _get_settings(duration: Optional[int], samplerate: Optional[int]):
    cfg_duration = 3
    cfg_samplerate = 16000
    beam_size = 1
    min_silence_ms = 400
    silence_rms = 0.008

    try:
        import config

        cfg_duration = int(getattr(config, "VOICE_DURATION", 3))
        cfg_samplerate = int(getattr(config, "VOICE_SAMPLE_RATE", 16000))
        beam_size = int(getattr(config, "VOICE_BEAM_SIZE", 1))
        min_silence_ms = int(getattr(config, "VOICE_VAD_MIN_SILENCE_MS", 400))
        silence_rms = float(getattr(config, "VOICE_SILENCE_RMS_THRESHOLD", 0.008))
    except Exception:
        pass

    return {
        "duration": int(duration if duration is not None else cfg_duration),
        "samplerate": int(samplerate if samplerate is not None else cfg_samplerate),
        "beam_size": max(1, beam_size),
        "min_silence_ms": max(100, min_silence_ms),
        "silence_rms": max(0.001, silence_rms),
    }


def _resolve_input_device(sd_module):
    """Pick input device in this order: configured -> default -> first valid."""
    try:
        import config
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

        # 3) First input-capable device
        for i, d in enumerate(devices):
            if (d.get("max_input_channels", 0) or 0) > 0:
                return i
    except Exception:
        return None
    return None


def listen_with_meta(duration: Optional[int] = None, samplerate: Optional[int] = None) -> VoiceResult:
    """Record from mic and transcribe with robust errors + latency metadata."""
    settings = _get_settings(duration, samplerate)
    duration = settings["duration"]
    samplerate = settings["samplerate"]
    beam_size = settings["beam_size"]
    min_silence_ms = settings["min_silence_ms"]
    silence_rms = settings["silence_rms"]

    t0 = time.perf_counter()
    tmp_path = ""

    try:
        os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
        os.environ.setdefault("HF_HUB_VERBOSITY", "error")
        warnings.filterwarnings(
            "ignore",
            message="You are sending unauthenticated requests to the HF Hub.*",
        )

        import sounddevice as sd
        import numpy as np
        from scipy.io.wavfile import write
    except ImportError as e:
        return VoiceResult(
            ok=False,
            code="missing_dependency",
            message=f"Missing dependency: {e}",
            total_ms=int((time.perf_counter() - t0) * 1000),
        )

    # Check microphone availability.
    try:
        devices = sd.query_devices()
        has_input = any((d.get("max_input_channels", 0) or 0) > 0 for d in devices)
        if not has_input:
            return VoiceResult(
                ok=False,
                code="no_mic",
                message="No microphone input device found.",
                total_ms=int((time.perf_counter() - t0) * 1000),
            )
    except Exception as e:
        return VoiceResult(
            ok=False,
            code="no_mic",
            message=f"Unable to query microphone devices: {e}",
            total_ms=int((time.perf_counter() - t0) * 1000),
        )

    input_device = _resolve_input_device(sd)

    try:
        # Capture
        capture_start = time.perf_counter()
        audio = sd.rec(
            int(duration * samplerate),
            samplerate=samplerate,
            channels=1,
            dtype="float32",
            device=input_device,
        )
        sd.wait()
        capture_ms = int((time.perf_counter() - capture_start) * 1000)

        rms = float((audio ** 2).mean() ** 0.5)
        if rms < silence_rms:
            return VoiceResult(
                ok=False,
                code="silent_audio",
                message="No clear speech detected. Please speak louder or closer to the mic.",
                capture_ms=capture_ms,
                total_ms=int((time.perf_counter() - t0) * 1000),
            )

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name
            wav_audio = np.clip(audio, -1.0, 1.0)
            wav_audio = (wav_audio * 32767).astype("int16")
            write(tmp_path, samplerate, wav_audio)

        # Transcription
        transcribe_start = time.perf_counter()
        model = _get_whisper_model()
        segments, _ = model.transcribe(
            tmp_path,
            beam_size=beam_size,
            temperature=0.0,
            condition_on_previous_text=False,
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": min_silence_ms},
        )
        transcribe_ms = int((time.perf_counter() - transcribe_start) * 1000)

        cleaned_parts = []
        for segment in segments:
            part = segment.text.strip()
            if not part:
                continue
            if re.fullmatch(r"[\W_\.\-\s]+", part):
                continue
            cleaned_parts.append(part)

        text = " ".join(cleaned_parts).strip()
        if not text:
            return VoiceResult(
                ok=False,
                code="silent_audio",
                message="Could not hear anything clearly.",
                capture_ms=capture_ms,
                transcribe_ms=transcribe_ms,
                total_ms=int((time.perf_counter() - t0) * 1000),
            )

        return VoiceResult(
            ok=True,
            text=text,
            code="ok",
            message="Transcription successful",
            capture_ms=capture_ms,
            transcribe_ms=transcribe_ms,
            total_ms=int((time.perf_counter() - t0) * 1000),
        )

    except Exception as e:
        message = str(e)
        code = "voice_error"
        if "Permission" in message or "permission" in message:
            code = "permission_denied"
        elif "WhisperModel" in message or "model" in message.lower():
            code = "model_load_failure"
        return VoiceResult(
            ok=False,
            code=code,
            message=message,
            total_ms=int((time.perf_counter() - t0) * 1000),
        )
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


def listen_async(duration: Optional[int] = None, samplerate: Optional[int] = None):
    """Run capture+transcription in background thread."""
    return _VOICE_EXECUTOR.submit(listen_with_meta, duration, samplerate)


def listen(duration: Optional[int] = None, samplerate: Optional[int] = None) -> str:
    """
    Record audio from microphone and transcribe to text.
    
    Args:
        duration: How many seconds to record (default 5)
        samplerate: Audio sample rate (16000 for Whisper)
    
    Returns:
        Transcribed text string
    """
    settings = _get_settings(duration, samplerate)
    print(f"🎤 Listening for {settings['duration']} seconds... (speak now)")
    result = listen_with_meta(duration=duration, samplerate=samplerate)

    if result.ok:
        print("✅ Recording done. Transcribing...")
        print(f"📝 You said: {result.text}")
        print(
            f"⏱ Latency: capture={result.capture_ms}ms, "
            f"transcribe={result.transcribe_ms}ms, total={result.total_ms}ms"
        )
        return result.text

    print(f"❌ {result.message}")
    return ""


def listen_push_to_talk(samplerate: Optional[int] = None, max_seconds: int = 15) -> VoiceResult:
    """Push-to-talk capture: press Enter to start and Enter to stop recording."""
    settings = _get_settings(duration=3, samplerate=samplerate)
    sr = settings["samplerate"]
    t0 = time.perf_counter()

    try:
        import sounddevice as sd
        import numpy as np
        from scipy.io.wavfile import write
    except ImportError as e:
        return VoiceResult(
            ok=False,
            code="missing_dependency",
            message=f"Missing dependency: {e}",
            total_ms=int((time.perf_counter() - t0) * 1000),
        )

    input_device = _resolve_input_device(sd)
    print("🎙 Push-to-talk: press Enter to start recording.")
    input()

    # Start async recording with hard max timeout protection.
    frames_total = int(max_seconds * sr)
    capture_start = time.perf_counter()
    recording = sd.rec(
        frames_total,
        samplerate=sr,
        channels=1,
        dtype="float32",
        device=input_device,
    )

    print("🔴 Recording... speak now, then press Enter to stop.")
    input()
    sd.stop()
    capture_ms = int((time.perf_counter() - capture_start) * 1000)

    # Use only the actually recorded portion.
    actual_samples = max(1, min(frames_total, int((capture_ms / 1000.0) * sr)))
    audio = recording[:actual_samples]

    rms = float((audio ** 2).mean() ** 0.5)
    if rms < settings["silence_rms"]:
        return VoiceResult(
            ok=False,
            code="silent_audio",
            message="No clear speech detected in push-to-talk recording.",
            capture_ms=capture_ms,
            total_ms=int((time.perf_counter() - t0) * 1000),
        )

    tmp_path = ""
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name
            wav_audio = np.clip(audio, -1.0, 1.0)
            wav_audio = (wav_audio * 32767).astype("int16")
            write(tmp_path, sr, wav_audio)

        transcribe_start = time.perf_counter()
        model = _get_whisper_model()
        segments, _ = model.transcribe(
            tmp_path,
            beam_size=settings["beam_size"],
            temperature=0.0,
            condition_on_previous_text=False,
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": settings["min_silence_ms"]},
        )
        transcribe_ms = int((time.perf_counter() - transcribe_start) * 1000)

        cleaned_parts = []
        for segment in segments:
            part = segment.text.strip()
            if not part:
                continue
            if re.fullmatch(r"[\W_\.\-\s]+", part):
                continue
            cleaned_parts.append(part)

        text = " ".join(cleaned_parts).strip()
        if not text:
            return VoiceResult(
                ok=False,
                code="silent_audio",
                message="Could not hear anything clearly in push-to-talk recording.",
                capture_ms=capture_ms,
                transcribe_ms=transcribe_ms,
                total_ms=int((time.perf_counter() - t0) * 1000),
            )

        return VoiceResult(
            ok=True,
            text=text,
            code="ok",
            message="Push-to-talk transcription successful",
            capture_ms=capture_ms,
            transcribe_ms=transcribe_ms,
            total_ms=int((time.perf_counter() - t0) * 1000),
        )
    except Exception as e:
        return VoiceResult(
            ok=False,
            code="voice_error",
            message=str(e),
            total_ms=int((time.perf_counter() - t0) * 1000),
        )
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


if __name__ == "__main__":
    # Test voice input directly
    pre = preload_model()
    if not pre.ok:
        print(f"⚠ Model preload issue: {pre.message}")
    result = listen()
    print(f"Result: {result}")
