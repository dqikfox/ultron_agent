"""
Voice interface management for ULTRON Agent 3.0
Handles speech recognition and text-to-speech functionality
"""
from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Optional, Union, Any, Dict

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

try:
    from elevenlabs import ElevenLabs
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False

from ..config import UltronConfig
from ..errors import UltronError, ErrorCategory, ErrorSeverity

logger = logging.getLogger(__name__)


class VoiceManager:
    """Manages voice input/output with multiple fallback options."""

    def __init__(self, config: UltronConfig) -> None:
        """Initialize voice manager with configuration."""
        self.config = config
        self.recognizer: Optional[sr.Recognizer] = None
        self.tts_engine: Optional[pyttsx3.Engine] = None
        self.elevenlabs: Optional[ElevenLabs] = None
        self.audio_manager: Optional[Any] = None
        
        self._initialize_components()

    def _initialize_components(self) -> None:
        """Initialize voice components based on available libraries and config."""
        # Initialize audio manager if available
        try:
            from tools.audio_manager import AudioManager
            self.audio_manager = AudioManager()
            logger.info("Audio manager initialized")
        except ImportError:
            logger.warning("Audio manager not available")

        # Initialize ElevenLabs if configured and available
        if ELEVENLABS_AVAILABLE and self.config.elevenlabs_api_key:
            try:
                self.elevenlabs = ElevenLabs(api_key=self.config.elevenlabs_api_key)
                logger.info("ElevenLabs TTS initialized")
            except Exception as e:
                logger.error(f"ElevenLabs initialization failed: {e}")

        # Initialize pyttsx3 as fallback
        if PYTTSX3_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 150)
                self.tts_engine.setProperty('volume', 0.9)
                logger.info("pyttsx3 TTS initialized as fallback")
            except Exception as e:
                logger.error(f"pyttsx3 initialization failed: {e}")

        # Initialize speech recognition
        if SPEECH_RECOGNITION_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                logger.info("Speech recognition initialized")
            except Exception as e:
                logger.error(f"Speech recognition initialization failed: {e}")

    async def speak(self, text: str) -> None:
        """Speak the given text using the best available TTS method."""
        if not text or not text.strip():
            return

        text = text.strip()
        logger.debug(f"Speaking: {text[:50]}...")

        # Try ElevenLabs first if available
        if self.elevenlabs and self.config.elevenlabs_api_key:
            try:
                await self._speak_with_elevenlabs(text)
                return
            except Exception as e:
                logger.warning(f"ElevenLabs TTS failed: {e}")

        # Try pyttsx3 as fallback
        if self.tts_engine:
            try:
                await self._speak_with_pyttsx3(text)
                return
            except Exception as e:
                logger.warning(f"pyttsx3 TTS failed: {e}")

        # Final fallback - text output
        self._text_fallback(text)

    async def _speak_with_elevenlabs(self, text: str) -> None:
        """Speak using ElevenLabs TTS."""
        if not self.elevenlabs:
            raise UltronError("ElevenLabs not available", ErrorCategory.VOICE, ErrorSeverity.LOW)

        voice_id = self.config.elevenlabs_agent_id or "default"
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        
        def generate_audio():
            return self.elevenlabs.text_to_speech(text, voice_id=voice_id)
        
        audio = await loop.run_in_executor(None, generate_audio)
        
        if self.audio_manager:
            # Save to temporary file and play
            temp_audio = Path("temp_audio.mp3")
            try:
                with temp_audio.open("wb") as f:
                    f.write(audio)
                
                def play_audio():
                    self.audio_manager.play_audio(str(temp_audio))
                
                await loop.run_in_executor(None, play_audio)
            finally:
                temp_audio.unlink(missing_ok=True)
        else:
            logger.warning("Audio manager not available for ElevenLabs playback")

    async def _speak_with_pyttsx3(self, text: str) -> None:
        """Speak using pyttsx3 TTS."""
        if not self.tts_engine:
            raise UltronError("pyttsx3 not available", ErrorCategory.VOICE, ErrorSeverity.LOW)

        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        
        def speak():
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        
        await loop.run_in_executor(None, speak)
        logger.info(f"Used pyttsx3 for: {text[:50]}...")

    def _text_fallback(self, text: str) -> None:
        """Fallback text output when voice synthesis fails."""
        print(f"[Voice]: {text}")
        logger.warning(f"Voice output failed, using text fallback: {text[:50]}...")

    async def listen(
        self,
        timeout: int = 10,
        phrase_time_limit: int = 10
    ) -> str:
        """Listen for speech and return recognized text."""
        logger.info("Starting speech recognition...")

        # Try ElevenLabs STT if available (future feature)
        if self.elevenlabs and hasattr(self.elevenlabs, "speech_to_text"):
            try:
                return await self._listen_with_elevenlabs(timeout, phrase_time_limit)
            except Exception as e:
                logger.warning(f"ElevenLabs STT failed: {e}")

        # Fallback to speech_recognition
        if self.recognizer and SPEECH_RECOGNITION_AVAILABLE:
            try:
                return await self._listen_with_speech_recognition(timeout, phrase_time_limit)
            except Exception as e:
                logger.warning(f"Speech recognition failed: {e}")

        raise UltronError(
            "No speech recognition method available",
            category=ErrorCategory.VOICE,
            severity=ErrorSeverity.HIGH,
            recovery_suggestion="Install speech_recognition or configure ElevenLabs"
        )

    async def _listen_with_elevenlabs(
        self,
        timeout: int,
        phrase_time_limit: int
    ) -> str:
        """Listen using ElevenLabs STT (future implementation)."""
        # This would be implemented when ElevenLabs adds STT support
        raise NotImplementedError("ElevenLabs STT not yet implemented")

    async def _listen_with_speech_recognition(
        self,
        timeout: int,
        phrase_time_limit: int
    ) -> str:
        """Listen using speech_recognition library."""
        if not self.recognizer:
            raise UltronError("Speech recognizer not available", ErrorCategory.VOICE, ErrorSeverity.HIGH)

        loop = asyncio.get_event_loop()
        
        def listen():
            with sr.Microphone() as source:
                logger.info("Listening for speech...")
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
                text = self.recognizer.recognize_google(audio)
                return text
        
        try:
            text = await loop.run_in_executor(None, listen)
            logger.info(f"Speech recognized: {text}")
            return text
        except sr.WaitTimeoutError:
            logger.info("No speech detected within timeout")
            return ""
        except sr.UnknownValueError:
            logger.info("Could not understand speech")
            return ""
        except sr.RequestError as e:
            raise UltronError(
                f"Speech recognition service error: {e}",
                category=ErrorCategory.VOICE,
                severity=ErrorSeverity.MEDIUM,
                recovery_suggestion="Check internet connection and try again",
                original_error=e
            )

    def stop_voice(self) -> None:
        """Release any audio resources."""
        try:
            if self.audio_manager and hasattr(self.audio_manager, 'stop_audio'):
                self.audio_manager.stop_audio()
                logger.info("Audio resources released")
        except Exception as e:
            logger.error(f"Error releasing voice/audio resources: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get voice system status."""
        return {
            "elevenlabs_available": self.elevenlabs is not None,
            "pyttsx3_available": self.tts_engine is not None,
            "speech_recognition_available": self.recognizer is not None,
            "audio_manager_available": self.audio_manager is not None
        }


# Backward compatibility function
def text_fallback_tts(text: str) -> None:
    """Fallback text output when voice synthesis fails."""
    print(f"[Voice]: {text}")
    logger.warning(f"Voice output failed, using text fallback: {text[:50]}...")