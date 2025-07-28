"""
Voice Engine for UltronSysAgent
Handles Speech-to-Text (STT) and Text-to-Speech (TTS) with streaming support
"""

import asyncio
import logging
import threading
import queue
import numpy as np
from typing import Optional, Callable, Dict, Any
import io
import wave

try:
    import sounddevice as sd
    import webrtcvad
    import whisper
    import pyttsx3
    VOICE_DEPS_AVAILABLE = True
except ImportError as e:
    VOICE_DEPS_AVAILABLE = False
    print(f"⚠️  Voice dependencies not available: {e}")

from ...core.event_bus import EventBus, EventTypes

class VoiceEngine:
    """Voice processing engine with real-time STT/TTS capabilities"""
    
    def __init__(self, config, event_bus: EventBus):
        self.config = config
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)
        
        # Voice activity detection
        self.vad = None
        self.vad_threshold = config.get('voice.vad_threshold', 0.3)
        
        # Audio settings
        self.sample_rate = 16000
        self.frame_duration = 20  # ms
        self.frame_size = int(self.sample_rate * self.frame_duration / 1000)
        
        # State
        self.is_listening = False
        self.is_muted = False
        self.is_speaking = False
        
        # Buffers
        self.audio_buffer = queue.Queue()
        self.speech_buffer = []
        
        # Models
        self.whisper_model = None
        self.tts_engine = None
        
        # Threads
        self.listen_thread = None
        self.process_thread = None
        
        # Initialize components
        self._initialize_components()
        
        # Subscribe to events
        self._setup_event_handlers()
    
    def _initialize_components(self):
        """Initialize voice processing components"""
        if not VOICE_DEPS_AVAILABLE:
            self.logger.error("Voice dependencies not available, voice engine disabled")
            return
        
        try:
            # Initialize VAD
            self.vad = webrtcvad.Vad(2)  # Aggressiveness level 0-3
            
            # Initialize Whisper for STT
            if self.config.get('voice.stt_provider') == 'whisper':
                model_size = self.config.get('voice.whisper_model', 'base')
                self.logger.info(f"Loading Whisper model: {model_size}")
                self.whisper_model = whisper.load_model(model_size)
            
            # Initialize TTS engine
            self._initialize_tts()
            
            self.logger.info("✅ Voice engine components initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize voice components: {e}")
            raise
    
    def _initialize_tts(self):
        """Initialize Text-to-Speech engine"""
        tts_provider = self.config.get('voice.tts_provider', 'pyttsx3')
        
        if tts_provider == 'pyttsx3':
            self.tts_engine = pyttsx3.init()
            
            # Configure voice settings
            rate = self.config.get('voice.speech_rate', 200)
            volume = self.config.get('voice.speech_volume', 0.8)
            
            self.tts_engine.setProperty('rate', rate)
            self.tts_engine.setProperty('volume', volume)
            
            # Set voice if specified
            voices = self.tts_engine.getProperty('voices')
            voice_id = self.config.get('voice.voice_id', 'default')
            
            if voice_id != 'default' and voices:
                for voice in voices:
                    if voice_id.lower() in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
    
    def _setup_event_handlers(self):
        """Setup event bus handlers"""
        self.event_bus.subscribe(EventTypes.MUTE_TOGGLE, self._handle_mute_toggle)
        self.event_bus.subscribe(EventTypes.TTS_START, self._handle_tts_request)
    
    async def start(self):
        """Start the voice engine"""
        if not VOICE_DEPS_AVAILABLE:
            self.logger.warning("Voice engine cannot start - dependencies missing")
            return
        
        self.logger.info("🎙️ Starting voice engine...")
        
        if self.config.get('voice.always_listening', True):
            await self.start_listening()
        
        await self.event_bus.publish(EventTypes.MODULE_STARTED, 
                                    {"module": "voice_engine"}, 
                                    source="voice_engine")
    
    async def stop(self):
        """Stop the voice engine"""
        self.logger.info("🔇 Stopping voice engine...")
        
        await self.stop_listening()
        
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except:
                pass
        
        await self.event_bus.publish(EventTypes.MODULE_STOPPED, 
                                    {"module": "voice_engine"}, 
                                    source="voice_engine")
    
    async def start_listening(self):
        """Start listening for voice input"""
        if self.is_listening or self.is_muted:
            return
        
        self.is_listening = True
        self.logger.info("👂 Started listening for voice input")
        
        # Start audio capture thread
        self.listen_thread = threading.Thread(target=self._audio_capture_loop, daemon=True)
        self.listen_thread.start()
        
        # Start audio processing thread
        self.process_thread = threading.Thread(target=self._audio_process_loop, daemon=True)
        self.process_thread.start()
    
    async def stop_listening(self):
        """Stop listening for voice input"""
        if not self.is_listening:
            return
        
        self.is_listening = False
        self.logger.info("🔇 Stopped listening for voice input")
        
        # Wait for threads to finish
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=1.0)
        
        if self.process_thread and self.process_thread.is_alive():
            self.process_thread.join(timeout=1.0)
    
    def _audio_capture_loop(self):
        """Main audio capture loop"""
        try:
            def audio_callback(indata, frames, time, status):
                if status:
                    self.logger.warning(f"Audio callback status: {status}")
                
                if self.is_listening and not self.is_muted:
                    # Convert to bytes for VAD
                    audio_bytes = (indata * 32767).astype(np.int16).tobytes()
                    self.audio_buffer.put(audio_bytes)
            
            # Start audio stream
            with sd.InputStream(callback=audio_callback,
                               channels=1,
                               samplerate=self.sample_rate,
                               blocksize=self.frame_size,
                               dtype=np.float32):
                
                while self.is_listening:
                    sd.sleep(100)  # Sleep for 100ms
                    
        except Exception as e:
            self.logger.error(f"Error in audio capture loop: {e}")
    
    def _audio_process_loop(self):
        """Process captured audio for voice activity"""
        speech_frames = []
        silence_count = 0
        
        try:
            while self.is_listening:
                try:
                    # Get audio frame with timeout
                    audio_bytes = self.audio_buffer.get(timeout=0.1)
                    
                    # Voice Activity Detection
                    is_speech = self.vad.is_speech(audio_bytes, self.sample_rate)
                    
                    if is_speech:
                        speech_frames.append(audio_bytes)
                        silence_count = 0
                        
                        # Publish speech detected event
                        asyncio.run_coroutine_threadsafe(
                            self.event_bus.publish(EventTypes.SPEECH_DETECTED, 
                                                 {"frame_count": len(speech_frames)}, 
                                                 source="voice_engine"),
                            asyncio.get_event_loop()
                        )
                    else:
                        silence_count += 1
                        
                        # If we have speech and silence, process it
                        if speech_frames and silence_count > 10:  # ~200ms silence
                            self._process_speech_frames(speech_frames)
                            speech_frames = []
                            silence_count = 0
                
                except queue.Empty:
                    continue
                except Exception as e:
                    self.logger.error(f"Error processing audio frame: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error in audio process loop: {e}")
    
    def _process_speech_frames(self, frames):
        """Process detected speech frames with STT"""
        try:
            # Combine frames into single audio
            audio_data = b''.join(frames)
            
            # Convert to numpy array
            audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32767.0
            
            # Perform STT
            text = self._speech_to_text(audio_np)
            
            if text and text.strip():
                self.logger.info(f"🎤 Recognized: {text}")
                
                # Publish recognition event
                asyncio.run_coroutine_threadsafe(
                    self.event_bus.publish(EventTypes.SPEECH_RECOGNIZED, 
                                         {"text": text.strip()}, 
                                         source="voice_engine"),
                    asyncio.get_event_loop()
                )
                
        except Exception as e:
            self.logger.error(f"Error processing speech: {e}")
    
    def _speech_to_text(self, audio_data: np.ndarray) -> str:
        """Convert speech to text using configured STT provider"""
        try:
            if self.config.get('voice.stt_provider') == 'whisper' and self.whisper_model:
                result = self.whisper_model.transcribe(audio_data)
                return result['text']
            else:
                # Fallback or other STT providers
                self.logger.warning("No STT provider available")
                return ""
                
        except Exception as e:
            self.logger.error(f"STT error: {e}")
            return ""
    
    async def speak(self, text: str, interrupt: bool = True):
        """Convert text to speech and play it"""
        if not text or self.is_muted:
            return
        
        if interrupt and self.is_speaking:
            await self.stop_speaking()
        
        self.is_speaking = True
        
        try:
            await self.event_bus.publish(EventTypes.TTS_START, 
                                       {"text": text}, 
                                       source="voice_engine")
            
            # Use configured TTS provider
            if self.config.get('voice.tts_provider') == 'pyttsx3' and self.tts_engine:
                await self._speak_with_pyttsx3(text)
            else:
                self.logger.warning("No TTS provider available")
            
            await self.event_bus.publish(EventTypes.TTS_COMPLETE, 
                                       {"text": text}, 
                                       source="voice_engine")
                                       
        except Exception as e:
            self.logger.error(f"TTS error: {e}")
        finally:
            self.is_speaking = False
    
    async def _speak_with_pyttsx3(self, text: str):
        """Speak using pyttsx3 engine"""
        try:
            # Run TTS in separate thread to avoid blocking
            def tts_worker():
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            
            thread = threading.Thread(target=tts_worker, daemon=True)
            thread.start()
            
            # Wait for completion
            while thread.is_alive():
                await asyncio.sleep(0.1)
                
        except Exception as e:
            self.logger.error(f"pyttsx3 error: {e}")
    
    async def stop_speaking(self):
        """Stop current speech output"""
        if not self.is_speaking:
            return
        
        try:
            if self.tts_engine:
                self.tts_engine.stop()
            self.is_speaking = False
            
        except Exception as e:
            self.logger.error(f"Error stopping speech: {e}")
    
    def toggle_mute(self):
        """Toggle mute state"""
        self.is_muted = not self.is_muted
        state = "muted" if self.is_muted else "unmuted"
        self.logger.info(f"🔇 Voice engine {state}")
        
        return self.is_muted
    
    async def _handle_mute_toggle(self, event):
        """Handle mute toggle event"""
        self.toggle_mute()
    
    async def _handle_tts_request(self, event):
        """Handle TTS request event"""
        if 'text' in event.data:
            await self.speak(event.data['text'])
    
    def get_status(self) -> Dict[str, Any]:
        """Get current voice engine status"""
        return {
            "listening": self.is_listening,
            "muted": self.is_muted,
            "speaking": self.is_speaking,
            "stt_provider": self.config.get('voice.stt_provider'),
            "tts_provider": self.config.get('voice.tts_provider'),
            "dependencies_available": VOICE_DEPS_AVAILABLE
        }
