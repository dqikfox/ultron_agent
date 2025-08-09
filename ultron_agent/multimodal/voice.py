from __future__ import annotations

"""
Minimal voice interface stubs for Phase 1. Expand in later phases with Whisper/Vosk.
Gracefully degrades if dependencies are missing.
"""
from typing import Optional

try:
    import speech_recognition as sr  # optional
    SR_AVAILABLE = True
except Exception:
    SR_AVAILABLE = False
    sr = None


def transcribe_once(timeout: int = 5, phrase_time_limit: int = 8) -> Optional[str]:
    if not SR_AVAILABLE:
        return None
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
    try:
        return r.recognize_google(audio)
    except Exception:
        return None