import base64
import time
import hashlib
import asyncio
import threading
import uuid
import logging
import os
import re
from queue import Queue
from typing import Optional, Dict, Any, TYPE_CHECKING, List
import subprocess
from pathlib import Path
from contextlib import contextmanager
import requests
import speech_recognition as sr
import pyttsx3

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    AudioSegment = None  # type: ignore
    PYDUB_AVAILABLE = False

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

try:
    from elevenlabs import ElevenLabs, VoiceSettings, play, save
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    VoiceSettings = None  # type: ignore
    print("Warning: ElevenLabs not available - voice.py:37")

try:
    import websockets
    from websockets.exceptions import ConnectionClosed
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    websockets = None
    ConnectionClosed = Exception
    WEBSOCKETS_AVAILABLE = False

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    pyaudio = None
    PYAUDIO_AVAILABLE = False

if TYPE_CHECKING:
    from websockets.legacy.client import WebSocketClientProtocol
else:
    WebSocketClientProtocol = Any

if load_dotenv:
    load_dotenv()

try:
    from tools.audio_manager import AudioManager
except ImportError:
    try:
        import pygame
        from pygame import mixer
        _PYGAME_AVAILABLE = True
    except Exception:
        pygame = None
        mixer = None
        _PYGAME_AVAILABLE = False

    class AudioManager:
        """Fallback audio manager for basic playback and recording support."""

        def __init__(self, playback_gain_db: float = 0.0, mixer_volume: float = 1.0):
            self._logger = logging.getLogger(__name__)
            self._temp_dir = Path("cache/voice_temp")
            self._temp_dir.mkdir(parents=True, exist_ok=True)
            self._play_lock = threading.Lock()
            self._mixer_ready = False
            self._pygame_warning_logged = False
            self._playback_gain_db = playback_gain_db
            self._mixer_volume = max(0.0, min(1.0, mixer_volume))

        @property
        def playback_gain_db(self) -> float:
            return self._playback_gain_db

        def set_playback_gain(self, gain_db: float) -> None:
            self._playback_gain_db = gain_db

        def set_mixer_volume(self, volume: float) -> None:
            self._mixer_volume = max(0.0, min(1.0, volume))

        def _create_temp_path(self, suffix: str) -> Path:
            self._temp_dir.mkdir(parents=True, exist_ok=True)
            return self._temp_dir / f"ultron_voice_{uuid.uuid4().hex}{suffix}"

        def _prepare_playback_file(self, path: Path) -> Path:
            """Apply gain adjustments when requested, returning a playable path."""
            gain = self._playback_gain_db
            if not PYDUB_AVAILABLE or abs(gain) < 1e-3:
                return path

            try:
                segment = AudioSegment.from_file(path)
                boosted = segment + gain
                adjusted_path = self._create_temp_path(path.suffix)
                boosted.export(adjusted_path, format=path.suffix.lstrip('.'))
                return adjusted_path
            except Exception as exc:
                self._logger.warning(
                    f"Failed to apply playback gain ({gain} dB): {exc}"
                )
                return path

        def _ensure_mixer(self) -> bool:
            if not _PYGAME_AVAILABLE:
                if not self._pygame_warning_logged:
                    self._logger.warning("pygame not available; audio playback will be limited")
                    self._pygame_warning_logged = True
                return False

            if self._mixer_ready and mixer and mixer.get_init():
                return True

            try:
                mixer.init()
                self._mixer_ready = True
                return True
            except Exception as exc:
                if not self._pygame_warning_logged:
                    self._logger.warning(f"pygame mixer initialization failed: {exc}")
                    self._pygame_warning_logged = True
                return False

        def _play_with_pygame(self, path: str) -> bool:
            if not self._ensure_mixer():
                return False

            try:
                mixer.music.stop()
            except Exception:
                pass

            try:
                mixer.music.set_volume(self._mixer_volume)
                mixer.music.load(path)
                mixer.music.play()
                while mixer.music.get_busy():
                    time.sleep(0.1)
                return True
            except Exception as exc:
                self._logger.debug(
                    f"pygame playback failed during load/play: {exc}"
                )
                return False

        def _fallback_play(self, path: str) -> bool:
            try:
                import simpleaudio as sa
                wave_obj = sa.WaveObject.from_wave_file(path)
                play_obj = wave_obj.play()
                play_obj.wait_done()
                return True
            except Exception:
                pass

            try:
                from playsound import playsound
                playsound(path)
                return True
            except Exception as exc:
                self._logger.warning(
                    f"Unable to play audio file '{path}': {exc}"
                )
                return False

        def _play_with_backends(self, playback_path: Path) -> bool:
            if self._play_with_pygame(str(playback_path)):
                return True

            if self._fallback_play(str(playback_path)):
                return True

            self._logger.error(
                f"All playback backends failed for '{playback_path}'"
            )
            return False

        def play_audio(self, path: str) -> bool:
            file_path = Path(path)
            if not file_path.exists():
                raise FileNotFoundError(f"Audio file not found: {file_path}")

            with self._play_lock:
                cleanup_path: Optional[Path] = None
                playback_path = self._prepare_playback_file(file_path)
                if playback_path != file_path:
                    cleanup_path = playback_path

                try:
                    return self._play_with_backends(playback_path)
                finally:
                    if cleanup_path and cleanup_path.exists():
                        try:
                            cleanup_path.unlink()
                        except Exception:
                            self._logger.debug(
                                f"Failed to remove adjusted temp file: {cleanup_path}"
                            )

        def _write_temp_audio(self, data: bytes, suffix: str) -> Path:
            temp_path = self._create_temp_path(suffix)
            temp_path.write_bytes(data)
            return temp_path

        def play_audio_bytes(self, data: bytes) -> bool:
            if not data:
                self._logger.warning("No audio data supplied for playback")
                return False

            suffix = ".mp3" if data[:3] == b"ID3" or data[:2] == b"\xff\xfb" else ".wav"
            temp_path = self._write_temp_audio(data, suffix)
            try:
                playback_path = self._prepare_playback_file(temp_path)
                cleanup_path: Optional[Path] = None
                if playback_path != temp_path:
                    cleanup_path = playback_path

                try:
                    return self._play_with_backends(playback_path)
                finally:
                    if cleanup_path and cleanup_path.exists():
                        try:
                            cleanup_path.unlink()
                        except Exception:
                            self._logger.debug(
                                f"Failed to remove adjusted temp file: {cleanup_path}"
                            )
            finally:
                try:
                    temp_path.unlink()
                except Exception:
                    self._logger.debug(
                        f"Failed to remove temporary audio file: {temp_path}"
                    )
            return False

        def _record_to_file_sync(
            self,
            timeout: int,
            phrase_time_limit: int,
            output_path: Optional[str],
            device_index: Optional[int]
        ) -> str:
            recognizer = sr.Recognizer()
            mic_kwargs = {"device_index": device_index} if device_index is not None else {}

            with sr.Microphone(**mic_kwargs) as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )

            wav_data = audio.get_wav_data()
            target_path = Path(output_path) if output_path else self._create_temp_path(".wav")
            target_path.write_bytes(wav_data)
            return str(target_path)

        async def record_audio_to_file(
            self,
            timeout: int = 10,
            phrase_time_limit: int = 10,
            output_path: Optional[str] = None,
            device_index: Optional[int] = None
        ) -> str:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.get_event_loop()
            try:
                return await loop.run_in_executor(
                    None,
                    self._record_to_file_sync,
                    timeout,
                    phrase_time_limit,
                    output_path,
                    device_index
                )
            except Exception as exc:
                self._logger.error(f"Audio recording failed: {exc}")
                raise


class ElevenLabsRealtimeSession:
    """Manage realtime ElevenLabs agent conversations over WebSockets."""

    def __init__(
        self,
        api_key: str,
        agent_id: str,
        voice_id: Optional[str] = None,
        *,
        sample_rate: int = 16000,
        chunk_size: int = 1024,
        event_system=None,
        input_device_index: Optional[int] = None,
        output_device_index: Optional[int] = None
    ):
        self.api_key = api_key
        self.agent_id = agent_id
        self.voice_id = voice_id
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self._event_system = event_system
        self._input_device_index = input_device_index
        self._output_device_index = output_device_index

        self._logger = logging.getLogger(__name__)
        self._queue: Queue = Queue(maxsize=100)
        self._stop_event = threading.Event()
        self._record_thread: Optional[threading.Thread] = None
        self._audio = None
        self._input_stream = None
        self._output_stream = None
        self._websocket: Optional[WebSocketClientProtocol] = None

    @property
    def is_running(self) -> bool:
        return self._record_thread is not None and self._record_thread.is_alive()

    async def run(self) -> bool:
        if not WEBSOCKETS_AVAILABLE:
            self._logger.error("websockets package unavailable; cannot start realtime session")
            return False
        if not PYAUDIO_AVAILABLE:
            self._logger.error("pyaudio package unavailable; cannot start realtime session")
            return False
        if not self.api_key or not self.agent_id:
            self._logger.error("ElevenLabs realtime credentials are missing")
            return False

        await self._connect()
        if not self._websocket:
            return False

        if not self._start_audio_streams():
            await self._close_websocket()
            return False

        self._record_thread = threading.Thread(target=self._record_loop, daemon=True)
        self._record_thread.start()

        if self._event_system:
            await self._event_system.emit("voice_realtime_start", {
                "agent_id": self.agent_id,
                "voice_id": self.voice_id,
                "sample_rate": self.sample_rate
            })

        try:
            await asyncio.gather(
                self._send_audio_loop(),
                self._receive_loop()
            )
        except Exception as exc:
            self._logger.error(f"Realtime session error: {exc}")
        finally:
            await self.stop()

        return True

    def request_stop(self):
        self._stop_event.set()
        try:
            self._queue.put_nowait(None)
        except Exception:
            pass

    async def stop(self):
        self.request_stop()
        await self._shutdown()

    async def _connect(self):
        ws_url = f"wss://api.elevenlabs.io/v1/agent/{self.agent_id}/conversation"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            self._logger.info("Connecting to ElevenLabs realtime agent...")
            self._websocket = await websockets.connect(ws_url, extra_headers=headers)
            self._logger.info("Connected to ElevenLabs agent")
        except Exception as exc:
            self._logger.error(f"Failed to connect to ElevenLabs agent: {exc}")
            self._websocket = None

    def _start_audio_streams(self) -> bool:
        try:
            self._audio = pyaudio.PyAudio()
            self._input_stream = self._audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                input_device_index=self._input_device_index
            )
            self._output_stream = self._audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                output=True,
                frames_per_buffer=self.chunk_size,
                output_device_index=self._output_device_index
            )
            return True
        except Exception as exc:
            self._logger.error(f"Failed to initialize audio streams: {exc}")
            return False

    def _record_loop(self):
        while not self._stop_event.is_set():
            try:
                data = self._input_stream.read(self.chunk_size, exception_on_overflow=False)
                self._queue.put(data, timeout=1)
            except Exception as exc:
                self._logger.error(f"Audio capture error: {exc}")
                break

    async def _send_audio_loop(self):
        loop = asyncio.get_running_loop()
        while not self._stop_event.is_set():
            data = await loop.run_in_executor(None, self._queue.get)
            if data is None:
                break

            try:
                payload = {
                    "type": "audio",
                    "data": base64.b64encode(data).decode("utf-8")
                }
                await self._websocket.send(json.dumps(payload))
            except Exception as exc:
                self._logger.error(f"Failed to send audio chunk: {exc}")
                break

            await asyncio.sleep(0.01)

    async def _receive_loop(self):
        try:
            async for message in self._websocket:
                if self._stop_event.is_set():
                    break

                try:
                    data = json.loads(message)
                except json.JSONDecodeError:
                    self._logger.debug("Received non-JSON message from ElevenLabs agent")
                    continue

                message_type = data.get("type")
                if message_type == "audio" and data.get("data"):
                    audio_bytes = base64.b64decode(data["data"])
                    self._output_stream.write(audio_bytes)
                elif message_type == "text":
                    text_payload = data.get("data", "")
                    self._logger.info(f"Agent: {text_payload}")
                    if self._event_system:
                        await self._event_system.emit("voice_realtime_text", {
                            "text": text_payload
                        })
                elif message_type == "status":
                    status_message = data.get("data", "")
                    self._logger.debug(f"ElevenLabs status: {status_message}")
                else:
                    self._logger.debug(f"Unhandled ElevenLabs message type: {message_type}")
        except ConnectionClosed:
            self._logger.info("ElevenLabs realtime connection closed")
        except Exception as exc:
            self._logger.error(f"ElevenLabs receive loop error: {exc}")

    async def _shutdown(self):
        if self._event_system:
            await self._event_system.emit("voice_realtime_stop", {
                "agent_id": self.agent_id
            })

        if self._record_thread:
            self._stop_event.set()
            self._queue.put_nowait(None)
            self._record_thread.join(timeout=1)
            self._record_thread = None

        if self._input_stream:
            try:
                self._input_stream.stop_stream()
                self._input_stream.close()
            except Exception:
                pass
            self._input_stream = None

        if self._output_stream:
            try:
                self._output_stream.stop_stream()
                self._output_stream.close()
            except Exception:
                pass
            self._output_stream = None

        if self._audio:
            try:
                self._audio.terminate()
            except Exception:
                pass
            self._audio = None

        await self._close_websocket()

    async def _close_websocket(self):
        if self._websocket:
            try:
                await self._websocket.close()
            except Exception:
                pass
            self._websocket = None

# Import event system for integration
try:
    from utils.event_system import EventSystem, get_event_system
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

        self.voice_output_gain_db = float(
            config.get("voice_output_gain_db", 0.0)
        )
        self.voice_playback_volume = max(
            0.0,
            min(1.0, float(config.get("voice_playback_volume", 1.0))),
        )

        try:
            self.audio_manager = AudioManager(
                playback_gain_db=self.voice_output_gain_db,
                mixer_volume=self.voice_playback_volume,
            )
        except TypeError:
            logger.warning(
                "AudioManager signature mismatch; falling back to default constructor"
            )
            self.audio_manager = AudioManager()
            if hasattr(self.audio_manager, "set_playback_gain"):
                self.audio_manager.set_playback_gain(self.voice_output_gain_db)
            if hasattr(self.audio_manager, "set_mixer_volume"):
                self.audio_manager.set_mixer_volume(self.voice_playback_volume)
        self.cache_dir = Path(config.get("voice_cache_dir", "cache/voice"))
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # ElevenLabs model defaults sourced from env or config
        self.elevenlabs_model_id = (
            os.getenv("ELEVENLABS_MODEL_ID")
            or config.get("elevenlabs_tts_model_id")
            or "eleven_multilingual_v2"
        )
        self.elevenlabs_output_format = (
            os.getenv("ELEVENLABS_OUTPUT_FORMAT")
            or config.get("elevenlabs_output_format")
            or "mp3_44100_128"
        )

        # Realtime conversation state
        self.elevenlabs_api_key = None
        self.realtime_agent_id = None
        self.realtime_voice_id = None
        self.realtime_session = None
        self.realtime_sample_rate = config.get("realtime_sample_rate", 16000)
        self.realtime_chunk_size = config.get("realtime_chunk_size", 1024)
        self.realtime_input_device_index = config.get("realtime_input_device_index")
        self.realtime_output_device_index = config.get("realtime_output_device_index")

        # Initialize event system and performance monitor
        self.event_system = self._initialize_event_system()
        self.performance_monitor = PerformanceMonitor() if PERFORMANCE_MONITOR_AVAILABLE else None

        # Deduplicate rapid-fire speech requests (prevents double narration)
        self._speech_dedup_window = float(config.get("speech_dedup_window", 2.0))
        self._recent_speeches: List[tuple[str, float]] = []
        self._screen_event_registered = False

        # Voice settings
        self.voice_rate = config.get("voice_rate", 150)
        self.voice_volume = config.get("voice_volume", 1.0)
        self.voice_stability = config.get("voice_stability", 0.5)
        self.voice_similarity = config.get("voice_similarity", 0.75)
        self.preferred_voice_id = (
            config.get("elevenlabs_voice_id")
            or config.get("elevenlabs_agent_voice_id")
            or config.get("elevenlabs_agent_id")
        )

        # Initialize with visual feedback
        print("🔄 Initializing Voice Assistant... - voice.py:635")
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

        self._register_event_handlers()

        self._show_progress("Voice Assistant ready", 100)
        logger.info("Voice Assistant initialized successfully")

    def _show_progress(self, message: str, percent: int = None):
        """Show visual progress indicator"""
        if percent is not None:
            bar_length = 30
            filled_length = int(bar_length * percent // 100)
            bar = '█' * filled_length + '-' * (bar_length - filled_length)
            print(f"\r{message} [{bar}] {percent}% - voice.py:660", end='', flush=True)
        else:
            print(f"\r{message} - voice.py:662", end='', flush=True)
        time.sleep(0.1)  # Brief pause for visual effect

    def _initialize_event_system(self):
        """Return the shared event system instance when available."""
        if not EVENT_SYSTEM_AVAILABLE:
            return None

        try:
            return get_event_system()
        except Exception as exc:
            logger.warning(f"Falling back to dedicated event system: {exc}")
            try:
                return EventSystem()
            except Exception as inner_exc:
                logger.error(f"Event system unavailable: {inner_exc}")
                return None

    def _register_event_handlers(self) -> None:
        """Subscribe to shared events for cross-component coordination."""
        event_system = self.event_system
        if not event_system or self._screen_event_registered:
            return

        async def _subscribe():
            try:
                await event_system.subscribe(
                    "screen_analysis_result",
                    self._handle_screen_analysis_event,
                )
                self._screen_event_registered = True
                logger.info("Voice assistant subscribed to screen analysis events")
            except Exception as exc:
                logger.warning(f"Failed to subscribe to screen events: {exc}")

        try:
            loop = asyncio.get_running_loop()
            loop.create_task(_subscribe())
        except RuntimeError:
            asyncio.run(_subscribe())
        except Exception as exc:
            logger.warning(f"Event subscription scheduling failed: {exc}")

    async def _handle_screen_analysis_event(self, event_data: Dict[str, Any]) -> None:
        """Narrate screen analysis results as soon as they are available."""
        if not event_data:
            return

        analysis = (event_data.get("analysis") or "").strip()
        if not analysis:
            return

        try:
            speak_text = f"Current screen description: {analysis}"
            await self.speak_async(speak_text)
        except Exception as exc:
            logger.error(f"Failed to narrate screen analysis: {exc}")

    def _normalize_for_dedup(self, text: str) -> str:
        """Normalize speech text to detect rapid duplicates."""
        normalized = text.lower()
        normalized = normalized.replace("current screen description", "")
        normalized = normalized.replace("here's what i see", "")
        normalized = normalized.replace("heres what i see", "")
        normalized = normalized.replace("🖥️", "")
        normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return normalized or text.lower().strip()

    def _is_duplicate_speech(self, normalized_text: str) -> bool:
        """Check whether a speech request was recently spoken."""
        if not normalized_text:
            return False

        now = time.time()
        self._recent_speeches = [
            entry for entry in self._recent_speeches
            if now - entry[1] < self._speech_dedup_window
        ]
        return any(entry[0] == normalized_text for entry in self._recent_speeches)

    def _record_speech_entry(self, normalized_text: str) -> None:
        """Record a speech snippet to avoid duplicates."""
        if not normalized_text:
            return
        self._recent_speeches.append((normalized_text, time.time()))


    def _collect_audio_bytes(self, audio_response):
        """Collate ElevenLabs streaming responses into a raw bytes payload."""
        if not audio_response:
            return b""

        if isinstance(audio_response, (bytes, bytearray)):
            return bytes(audio_response)

        collected = bytearray()
        try:
            for chunk in audio_response:
                if chunk is None:
                    continue

                if isinstance(chunk, (bytes, bytearray)):
                    collected.extend(chunk)
                    continue

                if isinstance(chunk, dict):
                    audio_chunk = chunk.get("audio")
                    if not audio_chunk:
                        continue

                    if isinstance(audio_chunk, (bytes, bytearray)):
                        collected.extend(audio_chunk)
                        continue

                    if isinstance(audio_chunk, str):
                        try:
                            collected.extend(base64.b64decode(audio_chunk))
                        except Exception as decode_error:
                            logger.debug(
                                f"Failed to decode ElevenLabs audio chunk: {decode_error}"
                            )
                        continue

                try:
                    collected.extend(bytes(chunk))
                except Exception:
                    logger.debug("Skipping unsupported ElevenLabs audio chunk type")

        except TypeError:
            try:
                return bytes(audio_response)
            except Exception:
                logger.debug("Unable to coerce ElevenLabs response into bytes")
                return b""

        return bytes(collected)

    def _synthesize_via_elevenlabs_rest(
        self,
        text: str,
        *,
        voice_id: Optional[str] = None,
        model_id: Optional[str] = None,
        output_format: Optional[str] = None
    ) -> bytes:
        if not self.elevenlabs_api_key:
            return b""

        target_voice_id = voice_id or self.preferred_voice_id
        if not target_voice_id:
            return b""

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{target_voice_id}"
        model_choice = model_id or self.elevenlabs_model_id
        selected_format = output_format or self.elevenlabs_output_format
        payload = {
            "text": text,
            "model_id": model_choice,
            "voice_settings": {
                "stability": self.voice_stability,
                "similarity_boost": self.voice_similarity
            }
        }

        if selected_format:
            payload["output_format"] = selected_format

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.elevenlabs_api_key
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
        except Exception as exc:
            logger.warning(f"ElevenLabs REST TTS request failed: {exc}")
            return b""

        if response.status_code == 200:
            return response.content

        logger.warning(
            "ElevenLabs REST TTS error %s: %s",
            response.status_code,
            response.text[:200]
        )
        return b""

    def _init_elevenlabs(self):
        """Initialize ElevenLabs with proper error handling"""
        # First try to get API key from environment variable
        elevenlabs_api_key = (
            os.getenv('ELEVENLABS_APIKEY') or
            os.getenv('ELEVENLABS_API_KEY')
        )
        if not elevenlabs_api_key:
            # Fallback to config file
            elevenlabs_api_key = self.config.get("elevenlabs_api_key")

        self.elevenlabs_api_key = elevenlabs_api_key

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

        # Resolve agent/voice identifiers from environment or configuration
        env_agent_id = os.getenv('ELEVENLABS_AGENT_ID')
        env_voice_id = os.getenv('ELEVENLABS_VOICE_ID')

        agent_id = env_agent_id or self.config.get("elevenlabs_agent_id")
        voice_id = (
            env_voice_id
            or self.config.get("elevenlabs_voice_id")
            or self.config.get("elevenlabs_agent_voice_id")
        )

        if not voice_id and agent_id:
            # Backwards compatibility with configs that only specify agent_id
            voice_id = agent_id

        self.realtime_agent_id = agent_id

        if voice_id:
            self.preferred_voice_id = voice_id
            logger.info(
                "Using ElevenLabs voice ID: %s",
                self.preferred_voice_id
            )
        else:
            # Final fallback to default voice ID
            self.preferred_voice_id = "e3mik6xHn4Sl51poljxK"
            logger.info(
                "Using default ElevenLabs voice ID: %s",
                self.preferred_voice_id
            )

        self.realtime_voice_id = self.preferred_voice_id

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

            self.realtime_voice_id = self.preferred_voice_id

            print("\n✅ ElevenLabs connected successfully - voice.py:956")
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

            print("✅ Fallback TTS engine ready - voice.py:989")
            logger.info("pyttsx3 TTS initialized as fallback")
        except Exception as e:
            self._show_progress("❌ pyttsx3 initialization failed", 65)
            logger.error(f"pyttsx3 initialization failed: {e}")
            self.tts_engine = None

    def _clean_speech_text(self, text: str) -> str:
        """Clean text to prevent repetitive speech and improve natural flow"""
        if not text:
            return text

        # Remove excessive word repetition while keeping natural emphasis
        words = text.split()
        cleaned_words = []
        last_word = None
        repeat_count = 0

        for word in words:
            word_clean = word.lower().strip('.,!?;:')
            if word_clean == last_word:
                repeat_count += 1
                if repeat_count < 2:
                    cleaned_words.append(word)
            else:
                cleaned_words.append(word)
                repeat_count = 0
            last_word = word_clean

        cleaned_text = ' '.join(cleaned_words)

        # Strip role labels that the Continue extension prepends before TTS
        role_tokens = r"assistant|user|system|ultron|response"
        cleaned_text = re.sub(
            rf"(?im)^(?:\s*(?:\*\*\s*)?(?:{role_tokens})(?:\*\*\s*)?[:\-]?\s*)",
            "",
            cleaned_text
        )

        # Collapse lingering repeated role tokens mid-sentence
        cleaned_text = re.sub(
            rf"\b({role_tokens})\b(?:\s+\1)+",
            r"\1",
            cleaned_text,
            flags=re.IGNORECASE
        )

        # Replace common TTS-unfriendly patterns
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

    def create_realtime_session(self) -> ElevenLabsRealtimeSession:
        """Create a realtime ElevenLabs session using configured credentials."""
        if not self.elevenlabs_api_key or not self.realtime_agent_id:
            raise ValueError("ElevenLabs realtime credentials are not configured")

        session = ElevenLabsRealtimeSession(
            api_key=self.elevenlabs_api_key,
            agent_id=self.realtime_agent_id,
            voice_id=self.realtime_voice_id,
            sample_rate=self.realtime_sample_rate,
            chunk_size=self.realtime_chunk_size,
            event_system=self.event_system,
            input_device_index=self.realtime_input_device_index,
            output_device_index=self.realtime_output_device_index
        )

        self.realtime_session = session
        return session

    async def start_realtime_conversation(self) -> bool:
        """Start a realtime ElevenLabs conversation loop."""
        if self.realtime_session and self.realtime_session.is_running:
            logger.info("ElevenLabs realtime session already running")
            return True

        try:
            session = self.create_realtime_session()
        except ValueError as exc:
            logger.error(str(exc))
            return False

        result = await session.run()
        self.realtime_session = None
        return result

    async def stop_realtime_conversation(self):
        """Stop an active realtime ElevenLabs conversation."""
        if self.realtime_session:
            await self.realtime_session.stop()
            self.realtime_session = None

    async def ollama_text_chat(self, prompt: str, model: Optional[str] = None, speak: bool = True) -> str:
        """Send a text prompt to Ollama and optionally speak the response."""
        if not prompt:
            return ""

        model_name = model or self.config.get("ollama_model", "llama3.1")

        def _invoke_ollama():
            return subprocess.run(
                ["ollama", "run", model_name, prompt],
                capture_output=True,
                text=True
            )

        result = await asyncio.to_thread(_invoke_ollama)

        if result.returncode != 0:
            logger.error(f"Ollama command failed: {result.stderr.strip()}")
            return ""

        response_text = result.stdout.strip()

        if speak and response_text:
            await self.speak_async(response_text)

        return response_text

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
            normalized_entry = self._normalize_for_dedup(cleaned_text)
            cache_path: Optional[Path] = None
            caching_enabled = not self.config.get("disable_tts_cache", False)

            if self._is_duplicate_speech(normalized_entry):
                logger.debug("Skipping duplicate speech request")
                return True

            # Check cache first if not disabled
            if caching_enabled:
                cache_path = self._get_cache_path(cleaned_text)
                if cache_path.exists():
                    try:
                        logger.debug(
                            f"Using cached audio for: {cleaned_text[:30]}..."
                        )
                        played = self.audio_manager.play_audio(
                            str(cache_path)
                        )
                        if played:
                            engine_used = "cached"

                            self._record_speech_entry(normalized_entry)

                            if self.event_system:
                                await self.event_system.emit(
                                    "voice_speak_success",
                                    {
                                        "engine": engine_used,
                                        "cached": True,
                                        "duration": time.time()
                                        - speak_start_time,
                                    },
                                )

                            return True
                        logger.warning(
                            "Cached audio playback failed, regenerating TTS"
                        )
                    except Exception as e:
                        logger.warning(f"Failed to play cached audio: {e}")

            # Try ElevenLabs first (only if available)
            if (ELEVENLABS_AVAILABLE and hasattr(self, 'elevenlabs_client') and
                    self.elevenlabs_client and self.preferred_voice_id):
                try:
                    logger.debug(
                        f"Using ElevenLabs TTS for: {cleaned_text[:30]}..."
                    )
                    voice_settings_obj = None
                    if ELEVENLABS_AVAILABLE and VoiceSettings is not None:
                        voice_settings_obj = VoiceSettings(
                            stability=self.voice_stability,
                            similarity_boost=self.voice_similarity
                        )
                    audio_response = self.elevenlabs_client.text_to_speech.convert(
                        text=cleaned_text,
                        voice_id=self.preferred_voice_id,
                        model_id=self.elevenlabs_model_id,
                        output_format=self.elevenlabs_output_format,
                        voice_settings=voice_settings_obj
                    )

                    audio = self._collect_audio_bytes(audio_response)
                    if not audio:
                        raise ValueError("No audio returned from ElevenLabs")

                    # Cache the audio if caching is enabled
                    if caching_enabled and cache_path:
                        try:
                            cache_path.write_bytes(audio)
                        except Exception as e:
                            logger.warning(f"Failed to cache audio: {e}")

                    played = self.audio_manager.play_audio_bytes(audio)
                    if played:
                        engine_used = "elevenlabs"

                        self._record_speech_entry(normalized_entry)

                        if self.event_system:
                            await self.event_system.emit(
                                "voice_speak_success",
                                {
                                    "engine": engine_used,
                                    "cached": False,
                                    "duration": time.time()
                                    - speak_start_time,
                                },
                            )

                        self._record_performance_metric(
                            "elevenlabs_tts",
                            time.time() - speak_start_time,
                            success=True,
                            metadata={"engine": "elevenlabs"},
                        )

                        return True

                    logger.warning(
                        "ElevenLabs audio playback failed, attempting fallback"
                    )

                except Exception as e:
                    logger.warning(f"ElevenLabs TTS failed: {e}")

                    # Emit failure event
                    if self.event_system:
                        await self.event_system.emit("voice_speak_error", {
                            "engine": "elevenlabs",
                            "error": str(e),
                            "duration": time.time() - speak_start_time
                        })

            # Attempt REST fallback if SDK is unavailable or failed
            if self.elevenlabs_api_key:
                rest_audio = await asyncio.to_thread(
                    self._synthesize_via_elevenlabs_rest,
                    cleaned_text,
                    voice_id=self.preferred_voice_id,
                    model_id=self.elevenlabs_model_id,
                    output_format=self.elevenlabs_output_format
                )

                if rest_audio:
                    if caching_enabled and cache_path:
                        try:
                            cache_path.write_bytes(rest_audio)
                        except Exception as cache_exc:
                            logger.warning(
                                f"Failed to cache REST audio: {cache_exc}"
                            )

                    played = self.audio_manager.play_audio_bytes(rest_audio)
                    if played:
                        engine_used = "elevenlabs_rest"

                        self._record_speech_entry(normalized_entry)

                        if self.event_system:
                            await self.event_system.emit(
                                "voice_speak_success",
                                {
                                    "engine": engine_used,
                                    "cached": False,
                                    "duration": time.time()
                                    - speak_start_time,
                                },
                            )

                        self._record_performance_metric(
                            "elevenlabs_rest_tts",
                            time.time() - speak_start_time,
                            success=True,
                            metadata={"engine": "elevenlabs_rest"},
                        )

                        return True

                    logger.warning(
                        "REST audio playback failed, falling back to pyttsx3"
                    )

            # Fallback to pyttsx3
            if self.tts_engine:
                try:
                    logger.debug(
                        f"Using pyttsx3 TTS for: {cleaned_text[:30]}..."
                    )
                    self.tts_engine.say(cleaned_text)
                    self.tts_engine.runAndWait()
                    engine_used = "pyttsx3"

                    self._record_speech_entry(normalized_entry)

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
                    self._record_speech_entry(
                        self._normalize_for_dedup(text)
                    )
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
    print(f"[Voice]: {text} - voice.py:1877")
    logger.warning(f"Voice output failed, using text fallback: {text[:50]}...")
