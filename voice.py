import logging
import os
import json
import time
import hashlib
import speech_recognition as sr
import pyttsx3
import asyncio
from typing import Optional, Dict, Any, Union
from pathlib import Path
from contextlib import contextmanager
from elevenlabs import generate, stream, set_api_key, voices, Voice
from elevenlabs.api import Models, Voices
from elevenlabs.error import AuthenticationError, APIError, RateLimitError
from tools.audio_manager import AudioManager

# Configure module-level logger
logger = logging.getLogger(__name__)

class VoiceAssistant:
    """Production-ready voice assistant with ElevenLabs integration and fallback chains"""

    def __init__(self, config):
        """Initialize voice assistant with configuration"""
        self.config = config
        self.recognizer = sr.Recognizer()
        self.tts_engine = None
        self.elevenlabs_voices = None
        self.audio_manager = AudioManager()
        self.cache_dir = Path(config.data.get("cache_dir", "cache/voice"))
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Voice settings
        self.voice_rate = config.data.get("voice_rate", 150)
        self.voice_volume = config.data.get("voice_volume", 0.9)
        self.voice_stability = config.data.get("voice_stability", 0.5)
        self.voice_similarity = config.data.get("voice_similarity", 0.75)
        self.preferred_voice_id = config.data.get("elevenlabs_agent_id")

        # Initialize voice systems
        self._init_elevenlabs()
        self._init_fallback_tts()

        # Set microphone energy threshold for better recognition
        if hasattr(self.recognizer, "energy_threshold"):
            self.recognizer.energy_threshold = config.data.get("mic_energy_threshold", 300)
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8

        logger.info("Voice Assistant initialized successfully")

    def _init_elevenlabs(self):
        """Initialize ElevenLabs with proper error handling"""
        elevenlabs_api_key = self.config.data.get("elevenlabs_api_key")
        if not elevenlabs_api_key:
            logger.info("ElevenLabs API key not found in config, skipping initialization")
            return

        try:
            # Set API key globally for the elevenlabs package
            set_api_key(elevenlabs_api_key)

            # Verify API key by retrieving available voices
            self.elevenlabs_voices = voices()

            # Validate preferred voice exists
            if self.preferred_voice_id:
                voice_exists = any(voice.voice_id == self.preferred_voice_id for voice in self.elevenlabs_voices)
                if not voice_exists:
                    logger.warning(f"Configured voice ID {self.preferred_voice_id} not found in ElevenLabs account")
                    # Try to get a default voice
                    if self.elevenlabs_voices:
                        self.preferred_voice_id = self.elevenlabs_voices[0].voice_id
                        logger.info(f"Using default voice: {self.preferred_voice_id}")

            logger.info(f"ElevenLabs initialized successfully with {len(self.elevenlabs_voices)} voices available")

        except AuthenticationError as e:
            logger.error(f"ElevenLabs authentication failed: {e}")
            self.elevenlabs_voices = None
        except APIError as e:
            logger.error(f"ElevenLabs API error: {e}")
            self.elevenlabs_voices = None
        except Exception as e:
            logger.error(f"ElevenLabs initialization failed: {e}")
            self.elevenlabs_voices = None

    def _init_fallback_tts(self):
        """Initialize pyttsx3 as fallback TTS engine"""
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', self.voice_rate)
            self.tts_engine.setProperty('volume', self.voice_volume)

            # Try to set a natural voice if available
            voices = self.tts_engine.getProperty('voices')
            for voice in voices:
                # Prefer female voices if available, otherwise use first voice
                if voice.gender == 'female' or 'female' in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    logger.info(f"Using pyttsx3 voice: {voice.name}")
                    break

            logger.info("pyttsx3 TTS initialized as fallback")
        except Exception as e:
            logger.error(f"pyttsx3 initialization failed: {e}")
            self.tts_engine = None

    def _clean_speech_text(self, text: str) -> str:
        """Clean text to prevent repetitive speech and improve natural flow"""
        if not text:
            return text

        # Remove excessive word repetition
        words = text.split()
        cleaned_words = []
        last_word = None
        repeat_count = 0

        for word in words:
            word_clean = word.lower().strip('.,!?;:')
            if word_clean == last_word:
                repeat_count += 1
                if repeat_count < 2:  # Allow max 1 repetition
                    cleaned_words.append(word)
            else:
                cleaned_words.append(word)
                repeat_count = 0
            last_word = word_clean

        # Replace common TTS-unfriendly patterns
        cleaned_text = ' '.join(cleaned_words)
        replacements = {
            "...": ", ",
            "--": ", ",
            "  ": " ",
            " - ": ", "
        }

        for old, new in replacements.items():
            cleaned_text = cleaned_text.replace(old, new)

        return cleaned_text

    def _get_cache_path(self, text: str) -> Path:
        """Generate a cache file path for the given text"""
        # Create a hash of the text plus voice settings to use as filename
        settings = f"{self.preferred_voice_id}-{self.voice_stability}-{self.voice_similarity}"
        text_hash = hashlib.md5(f"{text}{settings}".encode()).hexdigest()
        return self.cache_dir / f"{text_hash}.mp3"

    async def speak(self, text: str) -> bool:
        """
        Speak the given text using available TTS engines

        Args:
            text: The text to speak

        Returns:
            bool: True if speech was successful, False otherwise
        """
        if not text:
            return False

        # Clean text to improve speech quality
        cleaned_text = self._clean_speech_text(text)

        # Check cache first if not disabled
        if not self.config.data.get("disable_tts_cache", False):
            cache_path = self._get_cache_path(cleaned_text)
            if cache_path.exists():
                try:
                    logger.debug(f"Using cached audio for: {cleaned_text[:30]}...")
                    self.audio_manager.play_audio(str(cache_path))
                    return True
                except Exception as e:
                    logger.warning(f"Failed to use cached audio: {e}")

        # Try ElevenLabs TTS
        if self.elevenlabs_voices:
            try:
                # Use ElevenLabs streaming API for better performance
                logger.debug(f"Generating ElevenLabs audio for: {cleaned_text[:30]}...")
                audio_stream = generate(
                    text=cleaned_text,
                    voice=self.preferred_voice_id,
                    model="eleven_monolingual_v1",
                    stream=True,
                    stability=self.voice_stability,
                    similarity_boost=self.voice_similarity
                )

                # Save to cache file while streaming
                cache_path = self._get_cache_path(cleaned_text)
                with open(cache_path, "wb") as f:
                    for chunk in audio_stream:
                        f.write(chunk)

                # Play the saved file
                self.audio_manager.play_audio(str(cache_path))
                logger.info(f"ElevenLabs TTS completed for: {cleaned_text[:30]}...")
                return True

            except RateLimitError:
                logger.error("ElevenLabs rate limit reached, falling back to local TTS")
            except AuthenticationError:
                logger.error("ElevenLabs authentication error, falling back to local TTS")
            except Exception as e:
                logger.error(f"ElevenLabs TTS error: {e}, falling back to local TTS")

        # Fallback to pyttsx3
        if self.tts_engine:
            try:
                self.tts_engine.say(cleaned_text)
                self.tts_engine.runAndWait()
                logger.info(f"Used pyttsx3 for speech: {cleaned_text[:30]}...")
                return True
            except Exception as e:
                logger.error(f"pyttsx3 speech error: {e}")

        # Final fallback - text output
        logger.warning(f"All TTS methods failed, using text fallback: {cleaned_text[:30]}...")
        print(f"[Voice]: {cleaned_text} - voice.py:223")
        return False

    # Synchronous wrapper for compatibility
    def speak_sync(self, text: str) -> bool:
        """Synchronous wrapper for speak method"""
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return asyncio.run_coroutine_threadsafe(self.speak(text), loop).result()
        else:
            return asyncio.run(self.speak(text))

    @contextmanager
    def _get_microphone(self, device_index=None):
        """Context manager for microphone to ensure proper resource cleanup"""
        mic = sr.Microphone(device_index=device_index)
        try:
            yield mic
        finally:
            # No explicit cleanup needed for Microphone object in speech_recognition
            pass

    async def listen(self, timeout: int = 10, phrase_time_limit: int = 10) -> str:
        """
        Listen for speech and return recognized text

        Args:
            timeout: Maximum time to wait for speech to start
            phrase_time_limit: Maximum duration of speech to capture

        Returns:
            str: Recognized text or empty string if recognition failed
        """
        # Try ElevenLabs STT if available
        if hasattr(Models, "speech_recognition") and self.elevenlabs_voices:
            try:
                # Record audio using audio manager
                logger.info("Recording audio for ElevenLabs STT...")
                audio_path = await self.audio_manager.record_audio_to_file(
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )

                # Use ElevenLabs for STT
                with open(audio_path, "rb") as audio_file:
                    response = Models.speech_recognition(audio_file.read())

                if response and response.get("text"):
                    recognized_text = response["text"]
                    logger.info(f"ElevenLabs STT recognized: {recognized_text}")
                    return recognized_text
                else:
                    logger.warning("ElevenLabs STT returned empty result")
            except Exception as e:
                logger.error(f"ElevenLabs STT error: {e}")

        # Fallback to local speech recognition
        device_index = self.config.data.get("microphone_device_index")

        try:
            with self._get_microphone(device_index) as source:
                logger.info("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

                logger.info("Listening for speech...")
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )

                # Try multiple recognition services in order of preference
                services = [
                    ("google", self._recognize_google),
                    ("whisper", self._recognize_whisper),
                    ("sphinx", self._recognize_sphinx)
                ]

                for name, recognizer_func in services:
                    try:
                        text = await recognizer_func(audio)
                        if text:
                            logger.info(f"{name.capitalize()} STT recognized: {text}")
                            return text
                    except Exception as e:
                        logger.warning(f"{name.capitalize()} recognition failed: {e}")

                logger.error("All speech recognition methods failed")
                return ""

        except sr.WaitTimeoutError:
            logger.warning("Speech recognition timeout - no speech detected")
            return ""
        except Exception as e:
            logger.error(f"Speech recognition error: {e}")
            return ""

    # Synchronous wrapper for compatibility
    def listen_sync(self, timeout: int = 10, phrase_time_limit: int = 10) -> str:
        """Synchronous wrapper for listen method"""
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return asyncio.run_coroutine_threadsafe(self.listen(timeout, phrase_time_limit), loop).result()
        else:
            return asyncio.run(self.listen(timeout, phrase_time_limit))

    async def _recognize_google(self, audio):
        """Use Google Speech Recognition"""
        try:
            return self.recognizer.recognize_google(audio)
        except Exception as e:
            logger.debug(f"Google recognition failed: {e}")
            raise

    async def _recognize_whisper(self, audio):
        """Use OpenAI Whisper (if available)"""
        if not hasattr(self.recognizer, "recognize_whisper"):
            return None

        try:
            return self.recognizer.recognize_whisper(audio)
        except Exception as e:
            logger.debug(f"Whisper recognition failed: {e}")
            raise

    async def _recognize_sphinx(self, audio):
        """Use CMU Sphinx (offline)"""
        if not hasattr(self.recognizer, "recognize_sphinx"):
            return None

        try:
            return self.recognizer.recognize_sphinx(audio)
        except Exception as e:
            logger.debug(f"Sphinx recognition failed: {e}")
            raise

    def get_available_voices(self) -> list:
        """Get list of available TTS voices across all engines"""
        voices = []

        # Get ElevenLabs voices
        if self.elevenlabs_voices:
            voices.extend([{
                'name': voice.name,
                'id': voice.voice_id,
                'source': 'elevenlabs'
            } for voice in self.elevenlabs_voices])

        # Get pyttsx3 voices
        if self.tts_engine:
            pyttsx3_voices = self.tts_engine.getProperty('voices')
            voices.extend([{
                'name': voice.name,
                'id': voice.id,
                'source': 'pyttsx3'
            } for voice in pyttsx3_voices])

        return voices

    def set_voice(self, voice_id: str, source: str = 'elevenlabs') -> bool:
        """Set the voice to use for TTS"""
        if source == 'elevenlabs' and self.elevenlabs_voices:
            self.preferred_voice_id = voice_id
            logger.info(f"Set ElevenLabs voice to: {voice_id}")
            return True
        elif source == 'pyttsx3' and self.tts_engine:
            try:
                self.tts_engine.setProperty('voice', voice_id)
                logger.info(f"Set pyttsx3 voice to: {voice_id}")
                return True
            except Exception as e:
                logger.error(f"Failed to set pyttsx3 voice: {e}")
                return False
        return False

    def get_available_microphones(self) -> list:
        """Get list of available microphones"""
        mics = []
        try:
            for i, mic_name in enumerate(sr.Microphone.list_microphone_names()):
                mics.append({
                    'index': i,
                    'name': mic_name
                })
        except Exception as e:
            logger.error(f"Failed to list microphones: {e}")
        return mics

    def set_microphone(self, device_index: int) -> bool:
        """Set the microphone to use for STT"""
        try:
            # Test if the microphone works
            with sr.Microphone(device_index=device_index) as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.1)

            # Update config
            self.config.data["microphone_device_index"] = device_index
            logger.info(f"Set microphone to device index: {device_index}")
            return True
        except Exception as e:
            logger.error(f"Failed to set microphone: {e}")
            return False

    def check_tts_health(self) -> Dict[str, bool]:
        """Check health of TTS services"""
        health = {
            "elevenlabs": False,
            "pyttsx3": False
        }

        # Check ElevenLabs
        if self.elevenlabs_voices:
            try:
                # Simple test - get voices list
                test_voices = voices()
                health["elevenlabs"] = len(test_voices) > 0
            except Exception:
                health["elevenlabs"] = False

        # Check pyttsx3
        if self.tts_engine:
            try:
                # Simple property access to verify engine is working
                _ = self.tts_engine.getProperty('rate')
                health["pyttsx3"] = True
            except Exception:
                health["pyttsx3"] = False

        return health

    def check_stt_health(self) -> Dict[str, bool]:
        """Check health of STT services"""
        health = {
            "google": False,
            "whisper": False,
            "sphinx": False,
            "elevenlabs": False,
            "microphone": False
        }

        # Check microphone access
        try:
            device_index = self.config.data.get("microphone_device_index")
            with sr.Microphone(device_index=device_index) as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.1)
                health["microphone"] = True
        except Exception:
            health["microphone"] = False

        # We can't fully test the STT services without audio input,
        # but we can check if the methods are available
        health["google"] = hasattr(self.recognizer, "recognize_google")
        health["whisper"] = hasattr(self.recognizer, "recognize_whisper")
        health["sphinx"] = hasattr(self.recognizer, "recognize_sphinx")
        health["elevenlabs"] = hasattr(Models, "speech_recognition") and self.elevenlabs_voices is not None

        return health

    def stop_voice(self):
        """Release any audio resources (mic, audio, etc)."""
        try:
            if hasattr(self, 'audio_manager') and hasattr(self.audio_manager, 'stop_audio'):
                self.audio_manager.stop_audio()

            # Clean up pyttsx3 if needed
            if self.tts_engine:
                try:
                    self.tts_engine.stop()
                except Exception:
                    pass

        except Exception as e:
            logger.error(f"Error releasing voice/audio resources: {e}")

def text_fallback_tts(text):
    """Fallback text output when voice synthesis fails."""
    print(f"[Voice]: {text} - voice.py:499")
    logger.warning(f"Voice output failed, using text fallback: {text[:50]}...")

