"""
ULTRON Voice Processor - Advanced Voice Recognition and Speech Synthesis
Implements voice recognition optimization strategies from the developer guide.
"""

import os
import time
import threading
import queue
import logging
from typing import Optional, List, Dict, Any
import json

import speech_recognition as sr
import pyttsx3
import numpy as np

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False

try:
    import webrtcvad
    WEBRTC_VAD_AVAILABLE = True
except ImportError:
    WEBRTC_VAD_AVAILABLE = False

try:
    import noisereduce as nr
    NOISE_REDUCE_AVAILABLE = True
except ImportError:
    NOISE_REDUCE_AVAILABLE = False

try:
    import vosk
    import json
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False

class VoiceProcessor:
    """Advanced voice processing with optimization strategies"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger("VoiceProcessor")
        
        # Speech Recognition Setup
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.is_listening = False
        self.command_queue = queue.Queue()
        
        # Voice Activity Detection
        self.vad = None
        if WEBRTC_VAD_AVAILABLE:
            self.vad = webrtcvad.Vad(2)  # Aggressiveness level 0-3
        
        # Text-to-Speech Setup
        self.tts_engine = None
        self._initialize_tts()
        
        # Voice Recognition Settings
        self._configure_recognition()
        
        # Threading
        self.listen_thread = None
        self.should_stop = threading.Event()
        
        # Wake words
        self.wake_words = ["ultron", "hello", "speak", "ultra", "ultro", "alta"]
        self.wake_word_detected = False
        
        # Performance metrics
        self.recognition_times = []
        self.last_command = None
        
        self.logger.info("VoiceProcessor initialized")
    
    def _initialize_tts(self):
        """Initialize text-to-speech engine"""
        try:
            self.tts_engine = pyttsx3.init()
            
            # Configure voice
            voices = self.tts_engine.getProperty('voices')
            if self.config.voice_gender == "female" and len(voices) > 1:
                self.tts_engine.setProperty('voice', voices[1].id)
            else:
                self.tts_engine.setProperty('voice', voices[0].id)
            
            # Set speech rate
            self.tts_engine.setProperty('rate', 150)
            
            self.logger.info("TTS engine initialized")
            
        except Exception as e:
            self.logger.error(f"TTS initialization failed: {e}")
            self.tts_engine = None
    
    def _configure_recognition(self):
        """Configure speech recognition with optimizations"""
        try:
            # Initialize microphone
            self.microphone = sr.Microphone()
            
            # Adjust for ambient noise (optimization strategy)
            with self.microphone as source:
                self.logger.info("Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            
            # Optimization settings from guide
            self.recognizer.energy_threshold = 4000
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.5  # Reduced from default 0.8
            self.recognizer.non_speaking_duration = 0.3  # Shorter detection
            
            self.logger.info(f"Speech recognition configured - Energy threshold: {self.recognizer.energy_threshold}")
            
        except Exception as e:
            self.logger.error(f"Speech recognition configuration failed: {e}")
    
    def start_listening(self):
        """Start voice recognition in background thread"""
        if self.is_listening:
            return
        
        self.is_listening = True
        self.should_stop.clear()
        
        self.listen_thread = threading.Thread(target=self._listen_continuously, daemon=True)
        self.listen_thread.start()
        
        self.logger.info("Voice recognition started")
    
    def stop_listening(self):
        """Stop voice recognition"""
        self.is_listening = False
        self.should_stop.set()
        
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=2)
        
        self.logger.info("Voice recognition stopped")
    
    def _listen_continuously(self):
        """Continuous listening loop with wake word detection"""
        while not self.should_stop.is_set():
            try:
                with self.microphone as source:
                    # Listen for audio
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                
                # Process audio
                self._process_audio(audio)
                
            except sr.WaitTimeoutError:
                # Normal timeout, continue listening
                continue
            except Exception as e:
                self.logger.error(f"Listening error: {e}")
                time.sleep(1)  # Prevent rapid error loops
    
    def _process_audio(self, audio):
        """Process captured audio"""
        try:
            start_time = time.time()
            
            # Apply noise reduction if available
            if NOISE_REDUCE_AVAILABLE:
                audio = self._apply_noise_reduction(audio)
            
            # Voice Activity Detection
            if self.vad and not self._detect_voice_activity(audio):
                return  # Skip if no voice detected
            
            # Speech recognition
            text = self._recognize_speech(audio)
            
            if text:
                processing_time = time.time() - start_time
                self.recognition_times.append(processing_time)
                
                self.logger.info(f"Recognized: '{text}' (in {processing_time:.2f}s)")
                
                # Check for wake words
                if not self.wake_word_detected:
                    if self._contains_wake_word(text):
                        self.wake_word_detected = True
                        self.speak("Yes, I'm listening.")
                        return
                else:
                    # Process command
                    self.command_queue.put(text)
                    self.last_command = text
        
        except Exception as e:
            self.logger.error(f"Audio processing error: {e}")
    
    def _apply_noise_reduction(self, audio):
        """Apply noise reduction to audio"""
        try:
            # Convert to numpy array
            audio_data = np.frombuffer(audio.get_wav_data(), dtype=np.int16)
            
            # Apply noise reduction
            reduced_noise = nr.reduce_noise(y=audio_data, sr=audio.sample_rate)
            
            # Convert back to audio
            return sr.AudioData(reduced_noise.tobytes(), audio.sample_rate, audio.sample_width)
            
        except Exception as e:
            self.logger.error(f"Noise reduction failed: {e}")
            return audio
    
    def _detect_voice_activity(self, audio) -> bool:
        """Detect if audio contains voice activity"""
        try:
            if not self.vad:
                return True  # Assume voice if VAD not available
            
            # Convert audio to format expected by VAD (16kHz, 16-bit)
            audio_data = audio.get_wav_data()
            
            # VAD expects 10, 20, or 30ms frames at 16kHz
            frame_duration = 30  # ms
            frame_size = int(16000 * frame_duration / 1000)
            
            # Check frames for voice activity
            for i in range(0, len(audio_data), frame_size * 2):  # 2 bytes per sample
                frame = audio_data[i:i + frame_size * 2]
                if len(frame) == frame_size * 2:
                    if self.vad.is_speech(frame, 16000):
                        return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"VAD error: {e}")
            return True  # Default to assuming voice
    
    def _recognize_speech(self, audio) -> Optional[str]:
        """Recognize speech from audio using best available method"""
        try:
            # Try multiple recognition engines in order of preference
            
            # 1. Google Speech Recognition (online)
            if not self.config.offline_mode:
                try:
                    text = self.recognizer.recognize_google(audio, language='en-US')
                    return text.lower()
                except sr.UnknownValueError:
                    pass  # Try next method
                except sr.RequestError as e:
                    self.logger.warning(f"Google Speech Recognition error: {e}")
            
            # 2. Vosk (offline) if available
            if VOSK_AVAILABLE:
                try:
                    return self._recognize_with_vosk(audio)
                except Exception as e:
                    self.logger.warning(f"Vosk recognition failed: {e}")
            
            # 3. Sphinx (offline fallback)
            try:
                text = self.recognizer.recognize_sphinx(audio)
                return text.lower()
            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                self.logger.warning(f"Sphinx recognition error: {e}")
            
            return None
            
        except Exception as e:
            self.logger.error(f"Speech recognition error: {e}")
            return None
    
    def _recognize_with_vosk(self, audio) -> Optional[str]:
        """Recognize speech using Vosk offline model"""
        try:
            # This would require downloading Vosk models
            # For now, return None to fallback to other methods
            return None
        except Exception as e:
            self.logger.error(f"Vosk recognition error: {e}")
            return None
    
    def _contains_wake_word(self, text: str) -> bool:
        """Check if text contains wake words"""
        text_lower = text.lower()
        return any(wake_word in text_lower for wake_word in self.wake_words)
    
    def speak(self, text: str):
        """Speak text using TTS"""
        try:
            if self.tts_engine:
                self.logger.info(f"Speaking: {text}")
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            else:
                self.logger.warning("TTS engine not available")
        except Exception as e:
            self.logger.error(f"TTS error: {e}")
    
    def has_command(self) -> bool:
        """Check if there's a pending command"""
        return not self.command_queue.empty()
    
    def get_command(self) -> Optional[str]:
        """Get the next command from queue"""
        try:
            return self.command_queue.get_nowait()
        except queue.Empty:
            return None
    
    def reset_wake_word(self):
        """Reset wake word detection state"""
        self.wake_word_detected = False
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get voice processing performance metrics"""
        if self.recognition_times:
            avg_time = sum(self.recognition_times) / len(self.recognition_times)
            max_time = max(self.recognition_times)
            min_time = min(self.recognition_times)
        else:
            avg_time = max_time = min_time = 0
        
        return {
            'is_listening': self.is_listening,
            'wake_word_active': self.wake_word_detected,
            'commands_processed': len(self.recognition_times),
            'avg_recognition_time': round(avg_time, 2),
            'max_recognition_time': round(max_time, 2),
            'min_recognition_time': round(min_time, 2),
            'last_command': self.last_command,
            'tts_available': self.tts_engine is not None,
            'vad_available': self.vad is not None,
            'noise_reduction_available': NOISE_REDUCE_AVAILABLE
        }
    
    def test_voice_recognition(self):
        """Test voice recognition system"""
        try:
            self.logger.info("Testing voice recognition...")
            
            with self.microphone as source:
                self.speak("Please say something for the voice test.")
                audio = self.recognizer.listen(source, timeout=10)
            
            text = self._recognize_speech(audio)
            
            if text:
                self.speak(f"I heard: {text}")
                self.logger.info(f"Voice test successful: {text}")
                return True
            else:
                self.speak("I didn't understand what you said.")
                self.logger.warning("Voice test failed - no recognition")
                return False
                
        except Exception as e:
            self.logger.error(f"Voice test error: {e}")
            self.speak("Voice test encountered an error.")
            return False
    
    def adjust_sensitivity(self, adjustment: float):
        """Adjust microphone sensitivity"""
        try:
            current_threshold = self.recognizer.energy_threshold
            new_threshold = max(100, current_threshold + (adjustment * 1000))
            self.recognizer.energy_threshold = new_threshold
            
            self.logger.info(f"Energy threshold adjusted: {current_threshold} -> {new_threshold}")
            self.speak(f"Microphone sensitivity adjusted.")
            
        except Exception as e:
            self.logger.error(f"Sensitivity adjustment error: {e}")
    
    def set_voice_speed(self, speed: int):
        """Set TTS voice speed"""
        try:
            if self.tts_engine:
                speed = max(50, min(300, speed))  # Clamp between 50-300
                self.tts_engine.setProperty('rate', speed)
                self.logger.info(f"Voice speed set to: {speed}")
                self.speak("Voice speed has been adjusted.")
            
        except Exception as e:
            self.logger.error(f"Voice speed adjustment error: {e}")
