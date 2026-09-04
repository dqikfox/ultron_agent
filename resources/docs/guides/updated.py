"""
UltronSysAgent Voice Engine v2.2
Complete production-ready implementation with all fixes
"""

import asyncio
import logging
import threading
import queue
import numpy as np
from typing import Optional, Dict, Any
import io
import wave
import sys

# Conditional imports with fallback
try:
    import sounddevice as sd
    import webrtcvad
    import whisper
    import pyttsx3
    VOICE_DEPS_AVAILABLE = True
except ImportError as e:
    VOICE_DEPS_AVAILABLE = False
    logging.warning(f"Voice dependencies missing: {e}")

from ...core.event_bus import EventBus, EventTypes

class VoiceEngine:
    def __init__(self, config, event_bus: EventBus):
        self.config = config
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)
        
        # Thread safety
        self._state_lock = threading.Lock()
        self._buffer_lock = threading.Lock()
        
        # Audio config
        self.sample_rate = 16000
        self.frame_duration = 20  # ms
        self.frame_size = int(self.sample_rate * self.frame_duration / 1000)
        
        # State
        self._is_listening = False
        self._is_muted = False
        self._is_speaking = False
        
        # Buffers
        self.audio_buffer = queue.Queue()
        self.speech_buffer = []
        
        # Models
        self.vad = webrtcvad.Vad(2) if VOICE_DEPS_AVAILABLE else None
        self.whisper_model = None
        self.tts_engine = None
        
        # Initialize
        self._initialize_models()
        self._setup_event_handlers()
        
        # Event loop
        self.main_loop = asyncio.get_event_loop() if sys.platform == 'win32' else None

    def _initialize_models(self):
        """Initialize voice models with error handling"""
        if not VOICE_DEPS_AVAILABLE:
            return

        try:
            # Whisper STT
            if self.config.get('voice.stt_provider') == 'whisper':
                model_size = self.config.get('voice.whisper_model', 'base')
                self.whisper_model = whisper.load_model(model_size)
            
            # PyTTSx3 TTS
            if self.config.get('voice.tts_provider') == 'pyttsx3':
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', self.config.get('voice.speech_rate', 200))
                self.tts_engine.setProperty('volume', self.config.get('voice.speech_volume', 0.8))
                
        except Exception as e:
            self.logger.error(f"Model initialization failed: {e}", exc_info=True)

    def _setup_event_handlers(self):
        """Configure event bus subscriptions"""
        self.event_bus.subscribe(EventTypes.MUTE_TOGGLE, self._handle_mute_toggle)
        self.event_bus.subscribe(EventTypes.TTS_START, self._handle_tts_request)

    async def start(self):
        """Start voice processing"""
        if not VOICE_DEPS_AVAILABLE:
            return

        try:
            self.main_loop = asyncio.get_running_loop()
        except RuntimeError:
            self.main_loop = asyncio.new_event_loop()

        if self.config.get('voice.always_listening', True):
            await self.start_listening()

    async def stop(self):
        """Clean shutdown"""
        await self.stop_listening()
        
        if self.tts_engine:
            self.tts_engine.stop()
            self.tts_engine = None

    async def start_listening(self):
        """Begin audio capture"""
        with self._state_lock:
            if self._is_listening or self._is_muted:
                return
            
            self._is_listening = True
            
        # Start processing threads
        self.listen_thread = threading.Thread(
            target=self._audio_capture_loop,
            daemon=True
        )
        self.process_thread = threading.Thread(
            target=self._audio_process_loop,
            daemon=True
        )
        self.listen_thread.start()
        self.process_thread.start()

    def _audio_capture_loop(self):
        """Capture audio from microphone"""
        try:
            def callback(indata, frames, time, status):
                if status:
                    self.logger.warning(f"Audio status: {status}")
                
                if self.is_listening and not self.is_muted:
                    audio_bytes = (indata * 32767).astype(np.int16).tobytes()
                    with self._buffer_lock:
                        self.audio_buffer.put(audio_bytes)

            with sd.InputStream(
                callback=callback,
                channels=1,
                samplerate=self.sample_rate,
                blocksize=self.frame_size,
                dtype=np.float32
            ):
                while self.is_listening:
                    sd.sleep(100)
                    
        except Exception as e:
            self.logger.error(f"Capture loop crashed: {e}", exc_info=True)

    def _audio_process_loop(self):
        """Process audio with VAD and STT"""
        speech_frames = []
        silence_count = 0
        
        try:
            while self.is_listening:
                try:
                    # Get audio frame
                    with self._buffer_lock:
                        audio_bytes = self.audio_buffer.get(timeout=0.1)
                    
                    # Voice activity detection
                    is_speech = self.vad.is_speech(audio_bytes, self.sample_rate)
                    
                    if is_speech:
                        speech_frames.append(audio_bytes)
                        silence_count = 0
                    elif speech_frames:
                        silence_count += 1
                        if silence_count > 10:  # ~200ms silence
                            self._process_speech_frames(speech_frames)
                            speech_frames = []
                            silence_count = 0
                            
                except queue.Empty:
                    continue
                except Exception as e:
                    self.logger.error(f"Process error: {e}")

        except Exception as e:
            self.logger.error(f"Process loop crashed: {e}", exc_info=True)

    def _process_speech_frames(self, frames):
        """Convert speech to text"""
        try:
            audio_np = np.frombuffer(b''.join(frames), dtype=np.int16).astype(np.float32) / 32767.0
            text = self._speech_to_text(audio_np)
            
            if text:
                asyncio.run_coroutine_threadsafe(
                    self.event_bus.publish(
                        EventTypes.SPEECH_RECOGNIZED,
                        {"text": text},
                        source="voice_engine"
                    ),
                    self.main_loop
                )
                
        except Exception as e:
            self.logger.error(f"STT processing failed: {e}", exc_info=True)

    def _speech_to_text(self, audio_data: np.ndarray) -> str:
        """Convert audio to text using Whisper with WAV formatting"""
        if not self.whisper_model:
            return ""

        try:
            with io.BytesIO() as wav_buffer:
                with wave.open(wav_buffer, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(self.sample_rate)
                    wf.writeframes((audio_data * 32767).astype(np.int16).tobytes())
                
                wav_buffer.seek(0)
                result = self.whisper_model.transcribe(wav_buffer)
            
            return result.get('text', '').strip()
        
        except Exception as e:
            self.logger.error(f"STT failed: {e}", exc_info=True)
            return ""

    async def speak(self, text: str, interrupt: bool = True):
        """Text-to-speech output"""
        if not text or self.is_muted:
            return

        async with self._state_lock:
            if interrupt and self.is_speaking:
                await self._stop_speaking()
            
            self._is_speaking = True

        try:
            if self.tts_engine:
                def tts_task():
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
                
                thread = threading.Thread(target=tts_task, daemon=True)
                thread.start()
                
                while thread.is_alive():
                    await asyncio.sleep(0.1)
                    
        except Exception as e:
            self.logger.error(f"TTS failed: {e}", exc_info=True)
        finally:
            async with self._state_lock:
                self._is_speaking = False

    async def _stop_speaking(self):
        """Stop current speech"""
        if self.tts_engine:
            self.tts_engine.stop()
        self._is_speaking = False

    async def _handle_mute_toggle(self, event):
        """Event handler for mute toggle"""
        with self._state_lock:
            self._is_muted = not self._is_muted

    async def _handle_tts_request(self, event):
        """Event handler for TTS requests"""
        if 'text' in event.data:
            await self.speak(event.data['text'])

    @property
    def is_listening(self):
        with self._state_lock:
            return self._is_listening

    @property
    def is_muted(self):
        with self._state_lock:
            return self._is_muted

    @property
    def is_speaking(self):
        with self._state_lock:
            return self._is_speaking

    def get_status(self) -> Dict[str, Any]:
        """System status snapshot"""
        return {
            "listening": self.is_listening,
            "muted": self.is_muted,
            "speaking": self.is_speaking,
            "stt_ready": bool(self.whisper_model),
            "tts_ready": bool(self.tts_engine)
        }