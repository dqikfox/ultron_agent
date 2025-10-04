import logging
import os
import json
import time
import hashlib
import speech_recognition as sr
import pyttsx3
import asyncio
from typing import Optional, Dict
from pathlib import Path
from contextlib import contextmanager

try:
    from elevenlabs import ElevenLabs, play, save
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    print("Warning: ElevenLabs not available - voice.py:20")

try:
    from tools.audio_manager import AudioManager
except ImportError:
    # Fallback audio manager
    class AudioManager:
        def play_audio(self, path): pass
        def play_audio_bytes(self, data): pass

# Import event system for integration
try:
    from utils.event_system import EventSystem
    EVENT_SYSTEM_AVAILABLE = True
except ImportError:
    EVENT_SYSTEM_AVAILABLE = False

# Import performance monitor
try:
    from utils.performance_monitor import PerformanceMonitor
    PERFORMANCE_MONITOR_AVAILABLE = True
except ImportError:
    PERFORMANCE_MONITOR_AVAILABLE = False

# Configure module-level logger
logger = logging.getLogger(__name__)


class VoiceAssistant:
    """
    Production-ready voice assistant with ElevenLabs integration
    and fallback chains.
    """

    def __init__(self, config):
        """Initialize voice assistant with configuration"""
        self.config = config
        self.recognizer = sr.Recognizer()
        self.tts_engine = None
        self.elevenlabs_voices = None
        self.elevenlabs_client = None
        self.audio_manager = AudioManager()
        self.cache_dir = Path(config.get("voice_cache_dir", "cache/voice"))
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Initialize event system and performance monitor
        self.event_system = EventSystem() if EVENT_SYSTEM_AVAILABLE else None
        self.performance_monitor = PerformanceMonitor() if PERFORMANCE_MONITOR_AVAILABLE else None

        # Voice settings
        self.voice_rate = config.get("voice_rate", 150)
        self.voice_volume = config.get("voice_volume", 0.9)
        self.voice_stability = config.get("voice_stability", 0.5)
        self.voice_similarity = config.get("voice_similarity", 0.75)
        self.preferred_voice_id = config.get("elevenlabs_agent_id")

        # Initialize with visual feedback
        print("🔄 Initializing Voice Assistant... - voice.py:76")
        self._show_progress("Loading cache directory", 10)

        # Initialize voice systems
        self._init_elevenlabs()
        self._init_fallback_tts()

        # Set microphone energy threshold for better recognition
        if hasattr(self.recognizer, "energy_threshold"):
            threshold = config.get("mic_energy_threshold", 300)
            self.recognizer.energy_threshold = threshold
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8

        self._show_progress("Voice Assistant ready", 100)
        logger.info("Voice Assistant initialized successfully")

    def _show_progress(self, message: str, percent: int = None):
        """Show visual progress indicator"""
        if percent is not None:
            bar_length = 30
            filled_length = int(bar_length * percent // 100)
            bar = '█' * filled_length + '-' * (bar_length - filled_length)
            print(f"\r{message} [{bar}] {percent}% - voice.py:99", end='', flush=True)
        else:
            print(f"\r{message} - voice.py:101", end='', flush=True)
        time.sleep(0.1)  # Brief pause for visual effect

    def _init_elevenlabs(self):
        """Initialize ElevenLabs with proper error handling"""
        # First try to get API key from environment variable
        elevenlabs_api_key = os.getenv('ELEVENLABS_APIKEY')
        if not elevenlabs_api_key:
            # Fallback to config file
            elevenlabs_api_key = self.config.get("elevenlabs_api_key")

        if not elevenlabs_api_key:
            self._show_progress(
                "⚠️  ElevenLabs API key not found in environment or config",
                30
            )
            logger.info(
                "ElevenLabs API key not found in environment variable "
                "ELEVENLABS_APIKEY or config file"
            )
            return

        # Set the preferred voice ID from environment variable or config
        elevenlabs_agent_id = os.getenv('ELEVENLABS_AGENT_ID')
        if not elevenlabs_agent_id:
            # Fallback to config file
            elevenlabs_agent_id = self.config.get("elevenlabs_agent_id")

        if elevenlabs_agent_id:
            self.preferred_voice_id = elevenlabs_agent_id
            logger.info(f"Using ElevenLabs voice ID from environment: "
                        f"{self.preferred_voice_id}")
        else:
            # Final fallback to default voice ID
            self.preferred_voice_id = "e3mik6xHn4Sl51poljxK"  # Default
            logger.info(f"Using default ElevenLabs voice ID: "
                        f"{self.preferred_voice_id}")

        # Only proceed with ElevenLabs initialization if available
        if not ELEVENLABS_AVAILABLE:
            self._show_progress(
                "⚠️  ElevenLabs library not available, using fallback TTS",
                30
            )
            logger.info("ElevenLabs library not available, "
                        "skipping initialization")
            return

        try:
            # Initialize ElevenLabs client with API key
            self._show_progress("🔌 Connecting to ElevenLabs...", 40)
            self.elevenlabs_client = ElevenLabs(api_key=elevenlabs_api_key)

            # Verify API key by retrieving available voices
            voices_response = self.elevenlabs_client.voices.get_all()
            self.elevenlabs_voices = voices_response.voices

            self._show_progress(
                f"🎤 Loaded {len(self.elevenlabs_voices)} ElevenLabs voices",
                50
            )

            # Validate preferred voice exists (though we know this one exists)
            if self.preferred_voice_id:
                voice_exists = any(
                    voice.voice_id == self.preferred_voice_id
                    for voice in self.elevenlabs_voices)
                if not voice_exists:
                    self._show_progress(
                        "⚠️  Configured voice not found in account", 55
                    )
                    logger.warning(
                        f"Configured voice ID {self.preferred_voice_id} "
                        "not found - will use default voice"
                    )
                    # Try to get a default voice
                    if self.elevenlabs_voices:
                        self.preferred_voice_id = (
                            self.elevenlabs_voices[0].voice_id
                        )
                        logger.info(
                            f"Using default voice: {self.preferred_voice_id}")

            print("\n✅ ElevenLabs connected successfully - voice.py:183")
            logger.info(
                f"ElevenLabs initialized successfully with "
                f"{len(self.elevenlabs_voices)} voices available")

        except Exception as e:
            self._show_progress("❌ ElevenLabs initialization failed", 50)
            logger.error(f"ElevenLabs initialization failed: {e}")
            self.elevenlabs_voices = None

    def _init_fallback_tts(self):
        """Initialize pyttsx3 as fallback TTS engine"""
        try:
            self._show_progress("⚙️  Initializing fallback TTS engine...", 60)
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', self.voice_rate)
            self.tts_engine.setProperty('volume', self.voice_volume)

            # Try to set a natural voice if available
            voices = self.tts_engine.getProperty('voices')
            voice_set = False
            for voice in voices:
                # Prefer female voices if available, otherwise use first voice
                if voice.gender == 'female' or 'female' in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    logger.info(f"Using pyttsx3 voice: {voice.name}")
                    voice_set = True
                    break

            if not voice_set and voices:
                self.tts_engine.setProperty('voice', voices[0].id)
                logger.info(f"Using pyttsx3 voice: {voices[0].name}")

            print("✅ Fallback TTS engine ready - voice.py:216")
            logger.info("pyttsx3 TTS initialized as fallback")
        except Exception as e:
            self._show_progress("❌ pyttsx3 initialization failed", 65)
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
        settings = (
            f"{self.preferred_voice_id}-{self.voice_stability}-"
            f"{self.voice_similarity}"
        )
        text_hash = hashlib.md5(f"{text}{settings}".encode()).hexdigest()
        return self.cache_dir / f"{text_hash}.mp3"

    async def speak_async(self, text: str) -> bool:
        """
        Speak the given text using available TTS engines

        Args:
            text: The text to speak

        Returns:
            bool: True if speech was successful, False otherwise
        """
        if not text:
            return False

        # Emit speak start event
        if self.event_system:
            await self.event_system.emit("voice_speak_start", {
                "text": text[:100] + "..." if len(text) > 100 else text,
                "length": len(text)
            })

        # Start performance monitoring
        speak_start_time = time.time()
        engine_used = "unknown"

        try:
        # Clean text to improve speech quality
            cleaned_text = self._clean_speech_text(text)

            # Check cache first if not disabled
            if not self.config.get("disable_tts_cache", False):
                cache_path = self._get_cache_path(cleaned_text)
                if cache_path.exists():
                    try:
                        logger.debug(
                            f"Using cached audio for: {cleaned_text[:30]}..."
                        )
                        self.audio_manager.play_audio(str(cache_path))
                        engine_used = "cached"

                        # Emit success event
                        if self.event_system:
                            await self.event_system.emit(
                                "voice_speak_success", {
                                    "engine": engine_used,
                                    "cached": True,
                                    "duration": time.time() - speak_start_time
                                }
                            )

                        return True
                    except Exception as e:
                        logger.warning(f"Failed to play cached audio: {e}")

            # Try ElevenLabs first (only if available)
            if (ELEVENLABS_AVAILABLE and hasattr(self, 'elevenlabs_client') and
                    self.elevenlabs_client and self.preferred_voice_id):
                try:
                    logger.debug(
                        f"Using ElevenLabs TTS for: {cleaned_text[:30]}..."
                    )
                    audio = self.elevenlabs_client.text_to_speech.convert(
                        text=cleaned_text,
                        voice_id=self.preferred_voice_id,
                        model_id="eleven_multilingual_v2"
                    )

                    # Cache the audio if caching is enabled
                    if not self.config.get("disable_tts_cache", False):
                        try:
                            cache_path.write_bytes(audio)
                        except Exception as e:
                            logger.warning(f"Failed to cache audio: {e}")

                    # Play the audio
                    self.audio_manager.play_audio_bytes(audio)
                    engine_used = "elevenlabs"

                    # Emit success event
                    if self.event_system:
                        await self.event_system.emit("voice_speak_success", {
                            "engine": engine_used,
                            "cached": False,
                            "duration": time.time() - speak_start_time
                        })

                    # Record performance metric
                    self._record_performance_metric(
                        "elevenlabs_tts",
                        time.time() - speak_start_time,
                        success=True,
                        metadata={"engine": "elevenlabs"}
                    )

                    return True

                except Exception as e:
                    logger.warning(f"ElevenLabs TTS failed: {e}")

                    # Emit failure event
                    if self.event_system:
                        await self.event_system.emit("voice_speak_error", {
                            "engine": "elevenlabs",
                            "error": str(e),
                            "duration": time.time() - speak_start_time
                        })

            # Fallback to pyttsx3
            if self.tts_engine:
                try:
                    logger.debug(
                        f"Using pyttsx3 TTS for: {cleaned_text[:30]}..."
                    )
                    self.tts_engine.say(cleaned_text)
                    self.tts_engine.runAndWait()
                    engine_used = "pyttsx3"

                    # Emit success event
                    if self.event_system:
                        await self.event_system.emit("voice_speak_success", {
                            "engine": engine_used,
                            "cached": False,
                            "duration": time.time() - speak_start_time
                        })

                    return True
                except Exception as e:
                    logger.error(f"pyttsx3 TTS failed: {e}")

                    # Emit failure event
                    if self.event_system:
                        await self.event_system.emit("voice_speak_error", {
                            "engine": "pyttsx3",
                            "error": str(e),
                            "duration": time.time() - speak_start_time
                        })

            logger.error("All TTS engines failed")

            # Emit final failure event
            if self.event_system:
                await self.event_system.emit("voice_speak_failed", {
                    "text": text[:100] + "..." if len(text) > 100 else text,
                    "duration": time.time() - speak_start_time
                })

            return False

        except Exception as e:
            logger.error(f"Unexpected error in speak method: {e}")

            # Emit error event
            if self.event_system:
                await self.event_system.emit("voice_speak_error", {
                    "engine": engine_used,
                    "error": str(e),
                    "duration": time.time() - speak_start_time
                })

            return False

    def listen(self, timeout: int = 5) -> Optional[str]:
        """Listen for speech input and return transcribed text"""
        try:
            # Get microphone device index from config
            device_index = self.config.get("microphone_device_index")

            # Initialize microphone properly
            if device_index is not None:
                logger.debug(f"Using microphone device index: {device_index}")
                mic = sr.Microphone(device_index=device_index)
            else:
                logger.debug("Using default microphone")
                mic = sr.Microphone()

            with mic as source:
                logger.debug("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

                logger.debug("Listening for speech...")
                audio = self.recognizer.listen(
                    source, timeout=timeout, phrase_time_limit=10
                )

            logger.debug("Processing speech...")
            text = self.recognizer.recognize_google(audio)
            logger.info(f"Speech recognized: {text}")
            return text

        except sr.WaitTimeoutError:
            logger.debug("Speech recognition timeout")
            return None
        except sr.UnknownValueError:
            logger.debug("Could not understand speech")
            return None
        except Exception as e:
            logger.error(f"Speech recognition failed: {e}")
            return None

    # Synchronous wrapper for compatibility
    def speak(self, text: str) -> bool:
        """Synchronous speak method for TTS"""
        try:
            # Try to run async method synchronously
            loop = None
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Create new event loop in thread for blocking call
                    import threading
                    result = [False]
                    def run_speak():
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        try:
                            result[0] = new_loop.run_until_complete(self.speak_async(text))
                        finally:
                            new_loop.close()

                    thread = threading.Thread(target=run_speak, daemon=True)
                    thread.start()
                    thread.join(timeout=30)  # 30 second timeout
                    return result[0]
                else:
                    return asyncio.run(self.speak_async(text))
            except RuntimeError:
                # No event loop, create one
                return asyncio.run(self.speak_async(text))
        except Exception as e:
            logger.error(f"Speak failed: {e}")
            # Fallback to pyttsx3 if available
            if self.tts_engine:
                try:
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
                    return True
                except Exception as fallback_error:
                    logger.error(f"Fallback TTS failed: {fallback_error}")
            return False

    @contextmanager
    def _get_microphone(self, device_index=None):
        """Context manager for microphone to ensure proper resource cleanup"""
        mic = sr.Microphone(device_index=device_index)
        try:
            yield mic
        finally:
            # No explicit cleanup needed for Microphone object
            # in speech_recognition
            pass

    async def listen_async(
        self, timeout: int = 10, phrase_time_limit: int = 10
    ) -> str:
        """
        Listen for speech and return recognized text

        Args:
            timeout: Maximum time to wait for speech to start
            phrase_time_limit: Maximum duration of speech to capture

        Returns:
            str: Recognized text or empty string if recognition failed
        """
        # Emit listen start event
        if self.event_system:
            await self.event_system.emit("voice_listen_start", {
                "timeout": timeout,
                "phrase_time_limit": phrase_time_limit
            })

        listen_start_time = time.time()
        engine_used = "unknown"

        # Try ElevenLabs STT if available
        if ELEVENLABS_AVAILABLE and self.elevenlabs_voices:
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
                    logger.info(
                        f"ElevenLabs STT recognized: {recognized_text}"
                    )
                    engine_used = "elevenlabs"

                    # Emit success event
                    if self.event_system:
                        await self.event_system.emit("voice_listen_success", {
                            "engine": engine_used,
                            "text": recognized_text[:100] + "..." if len(
                                recognized_text) > 100 else recognized_text,
                            "duration": time.time() - listen_start_time
                        })

                    return recognized_text
                else:
                    logger.warning("ElevenLabs STT returned empty result")

                    # Emit empty result event
                    if self.event_system:
                        await self.event_system.emit("voice_listen_empty", {
                            "engine": "elevenlabs",
                            "duration": time.time() - listen_start_time
                        })

            except Exception as e:
                logger.error(f"ElevenLabs STT error: {e}")

                # Emit error event
                if self.event_system:
                    await self.event_system.emit("voice_listen_error", {
                        "engine": "elevenlabs",
                        "error": str(e),
                        "duration": time.time() - listen_start_time
                    })

        # Fallback to local speech recognition
        device_index = self.config.get("microphone_device_index")

        try:
            # Initialize microphone properly
            if device_index is not None:
                logger.info(f"Using microphone device index: {device_index}")
                mic = sr.Microphone(device_index=device_index)
            else:
                logger.info("Using default microphone")
                mic = sr.Microphone()

            with mic as source:
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
                            logger.info(
                                f"{name.capitalize()} STT recognized: {text}"
                            )
                            engine_used = name

                            # Emit success event
                            if self.event_system:
                                await self.event_system.emit(
                                    "voice_listen_success", {
                                        "engine": engine_used,
                                        "text": text[:100] + "..." if len(
                                            text) > 100 else text,
                                        "duration": time.time() - listen_start_time
                                    }
                                )

                            return text
                    except Exception as e:
                        logger.warning(
                            f"{name.capitalize()} recognition failed: {e}"
                        )

                        # Emit error event for this service
                        if self.event_system:
                            await self.event_system.emit("voice_listen_error", {
                                "engine": name,
                                "error": str(e),
                                "duration": time.time() - listen_start_time
                            })

                logger.error("All speech recognition methods failed")

                # Emit final failure event
                if self.event_system:
                    await self.event_system.emit("voice_listen_failed", {
                        "duration": time.time() - listen_start_time
                    })

                return ""

        except sr.WaitTimeoutError:
            logger.warning("Speech recognition timeout - no speech detected")

            # Emit timeout event
            if self.event_system:
                await self.event_system.emit("voice_listen_timeout", {
                    "timeout": timeout,
                    "duration": time.time() - listen_start_time
                })

            return ""
        except Exception as e:
            logger.error(f"Speech recognition error: {e}")

            # Emit error event
            if self.event_system:
                await self.event_system.emit("voice_listen_error", {
                    "engine": "system",
                    "error": str(e),
                    "duration": time.time() - listen_start_time
                })

            return ""

    # Synchronous wrapper for compatibility
    def listen_sync(
        self, timeout: int = 10, phrase_time_limit: int = 10
    ) -> str:
        """Synchronous wrapper for listen method"""
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return asyncio.run_coroutine_threadsafe(
                self.listen_async(timeout, phrase_time_limit), loop
            ).result()
        else:
            return asyncio.run(self.listen_async(timeout, phrase_time_limit))

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
            for i, mic_name in enumerate(
                sr.Microphone.list_microphone_names()
            ):
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
            self.config["microphone_device_index"] = device_index
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
        if ELEVENLABS_AVAILABLE and self.elevenlabs_voices:
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
            device_index = self.config.get("microphone_device_index")
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
        health["elevenlabs"] = (
            ELEVENLABS_AVAILABLE and
            hasattr(self, 'elevenlabs_voices') and
            self.elevenlabs_voices is not None
        )

        return health

    def _record_performance_metric(self, operation: str, duration: float,
                                   success: bool = True, metadata: Dict = None):
        """Record performance metrics for voice operations"""
        if not self.performance_monitor:
            return

        try:
            metric_data = {
                "operation": operation,
                "duration": duration,
                "success": success,
                "timestamp": time.time()
            }

            if metadata:
                metric_data.update(metadata)

            # Record the metric
            engine_tag = (metadata.get("engine", "unknown")
                          if metadata else "unknown")
            self.performance_monitor.record_metric(
                f"voice_{operation}",
                duration,
                tags={
                    "success": str(success),
                    "engine": engine_tag
                }
            )

            logger.debug(
                f"Recorded performance metric: {operation} = {duration:.2f}s"
            )

        except Exception as e:
            logger.warning(f"Failed to record performance metric: {e}")

    def get_performance_stats(self) -> Dict:
        """Get performance statistics for voice operations"""
        if not self.performance_monitor:
            return {"error": "Performance monitor not available"}

        try:
            stats = {}

            # Get stats for different operations
            operations = [
                "speak", "listen", "elevenlabs_tts", "pyttsx3_tts",
                "google_stt", "whisper_stt", "sphinx_stt"
            ]

            for op in operations:
                op_stats = self.performance_monitor.get_operation_stats(
                    f"voice_{op}"
                )
                if op_stats:
                    stats[op] = op_stats

            return stats

        except Exception as e:
            logger.error(f"Failed to get performance stats: {e}")
            return {"error": str(e)}


def text_fallback_tts(text):
    """Fallback text output when voice synthesis fails."""
    print(f"[Voice]: {text} - voice.py:901")
    logger.warning(f"Voice output failed, using text fallback: {text[:50]}...")
