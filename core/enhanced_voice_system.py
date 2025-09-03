#!/usr/bin/env python3
"""
Enhanced Voice System with Wake Word Detection
==============================================

Advanced voice processing with wake word detection, noise reduction,
and intelligent voice-to-AI pipeline for natural interaction.
"""

import asyncio
import threading
import time
import logging
import wave
import queue
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import numpy as np
from pathlib import Path

# Audio processing imports
try:
    import pyaudio
    import audioop
    import speech_recognition as sr
    import pyttsx3
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    logging.warning("Audio libraries not available - voice system will be limited")

# Wake word detection imports
try:
    import pvporcupine
    import pvrecorder
    PORCUPINE_AVAILABLE = True
except ImportError:
    PORCUPINE_AVAILABLE = False
    logging.warning("Porcupine wake word detection not available")

@dataclass
class VoiceConfig:
    """Voice system configuration"""
    wake_words: List[str] = None
    wake_word_sensitivity: float = 0.7
    voice_activation_timeout: int = 5
    continuous_listening: bool = True
    noise_reduction: bool = True
    voice_feedback: bool = True
    voice_speed: int = 180
    voice_volume: float = 0.9
    preferred_voice: str = "male"
    language: str = "en-US"
    
    def __post_init__(self):
        if self.wake_words is None:
            self.wake_words = ["ultron", "computer", "assistant", "hey ultron"]

class WakeWordDetector:
    """Advanced wake word detection using Porcupine"""
    
    def __init__(self, config: VoiceConfig):
        self.config = config
        self.logger = logging.getLogger("ULTRON.WakeWord")
        self.porcupine = None
        self.recorder = None
        self.is_listening = False
        self.detection_callbacks: List[Callable] = []
        
        if PORCUPINE_AVAILABLE:
            self._setup_porcupine()
    
    def _setup_porcupine(self):
        """Setup Porcupine wake word detection"""
        try:
            # Try to use built-in wake words or custom models
            keywords = []
            for wake_word in self.config.wake_words:
                if wake_word.lower() in ["computer", "hey google", "alexa"]:
                    keywords.append(wake_word.lower())
            
            if not keywords:
                # Fallback to generic keywords
                keywords = ["computer"]
            
            self.porcupine = pvporcupine.create(
                keywords=keywords,
                sensitivities=[self.config.wake_word_sensitivity] * len(keywords)
            )
            
            # Setup audio recorder
            self.recorder = pvrecorder.PvRecorder(
                device_index=-1,  # Use default device
                frame_length=self.porcupine.frame_length
            )
            
            self.logger.info(f"Porcupine initialized with keywords: {keywords}")
            
        except Exception as e:
            self.logger.error(f"Porcupine setup failed: {e}")
            self.porcupine = None
            self.recorder = None
    
    def add_detection_callback(self, callback: Callable[[str], None]):
        """Add callback for wake word detection"""
        self.detection_callbacks.append(callback)
    
    async def start_detection(self):
        """Start wake word detection"""
        if not self.porcupine or not self.recorder:
            self.logger.warning("Wake word detection not available")
            return
        
        self.is_listening = True
        self.logger.info("Wake word detection started")
        
        try:
            self.recorder.start()
            
            while self.is_listening:
                # Process audio frame
                pcm = self.recorder.read()
                result = self.porcupine.process(pcm)
                
                if result >= 0:
                    # Wake word detected
                    detected_word = self.config.wake_words[result] if result < len(self.config.wake_words) else "unknown"
                    self.logger.info(f"Wake word detected: {detected_word}")
                    
                    # Trigger callbacks
                    for callback in self.detection_callbacks:
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                await callback(detected_word)
                            else:
                                callback(detected_word)
                        except Exception as e:
                            self.logger.error(f"Wake word callback error: {e}")
                
                # Small delay to prevent high CPU usage
                await asyncio.sleep(0.01)
                
        except Exception as e:
            self.logger.error(f"Wake word detection error: {e}")
        finally:
            if self.recorder:
                self.recorder.stop()
    
    def stop_detection(self):
        """Stop wake word detection"""
        self.is_listening = False
        if self.recorder:
            self.recorder.stop()
        self.logger.info("Wake word detection stopped")
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop_detection()
        if self.porcupine:
            self.porcupine.delete()
        if self.recorder:
            self.recorder.delete()

class NoiseReduction:
    """Audio noise reduction and enhancement"""
    
    def __init__(self, config: VoiceConfig):
        self.config = config
        self.logger = logging.getLogger("ULTRON.NoiseReduction")
    
    def reduce_noise(self, audio_data: np.ndarray, sample_rate: int = 16000) -> np.ndarray:
        """Apply noise reduction to audio data"""
        try:
            if not self.config.noise_reduction:
                return audio_data
            
            # Simple noise gate - remove low amplitude sounds
            threshold = np.max(audio_data) * 0.1
            audio_data = np.where(np.abs(audio_data) > threshold, audio_data, 0)
            
            # Apply simple low-pass filter to remove high frequency noise
            # This is a basic implementation - more advanced methods could be added
            from scipy import signal
            b, a = signal.butter(4, 0.3, 'low')
            audio_data = signal.filtfilt(b, a, audio_data)
            
            return audio_data
            
        except Exception as e:
            self.logger.warning(f"Noise reduction failed: {e}")
            return audio_data
    
    def enhance_speech(self, audio_data: np.ndarray) -> np.ndarray:
        """Enhance speech quality in audio data"""
        try:
            # Normalize audio levels
            max_val = np.max(np.abs(audio_data))
            if max_val > 0:
                audio_data = audio_data / max_val * 0.8
            
            return audio_data
            
        except Exception as e:
            self.logger.warning(f"Speech enhancement failed: {e}")
            return audio_data

class EnhancedVoiceSystem:
    """Enhanced voice processing system"""
    
    def __init__(self, config: VoiceConfig):
        self.config = config
        self.logger = logging.getLogger("ULTRON.EnhancedVoice")
        
        # Core components
        self.wake_word_detector = None
        self.noise_reducer = NoiseReduction(config)
        self.recognizer = None
        self.microphone = None
        self.tts_engine = None
        
        # State management
        self.is_listening = False
        self.is_processing = False
        self.voice_callbacks: List[Callable] = []
        self.audio_queue = queue.Queue()
        
        # Performance metrics
        self.recognition_stats = {
            "total_attempts": 0,
            "successful_recognitions": 0,
            "average_confidence": 0.0
        }
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize voice system components"""
        try:
            if not AUDIO_AVAILABLE:
                self.logger.warning("Audio libraries not available")
                return
                
            # Initialize speech recognition
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
            
            # Try to initialize microphone
            try:
                self.microphone = sr.Microphone()
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                self.logger.info("Microphone initialized and calibrated")
            except Exception as e:
                self.logger.warning(f"Microphone initialization failed: {e}")
                self.microphone = None
            
            # Initialize text-to-speech
            try:
                self.tts_engine = pyttsx3.init()
                self._configure_tts()
                self.logger.info("Text-to-speech initialized")
            except Exception as e:
                self.logger.warning(f"TTS initialization failed: {e}")
                self.tts_engine = None
            
            # Initialize wake word detector
            if PORCUPINE_AVAILABLE:
                self.wake_word_detector = WakeWordDetector(self.config)
                self.wake_word_detector.add_detection_callback(self._on_wake_word_detected)
                
        except Exception as e:
            self.logger.error(f"Voice system initialization failed: {e}")
    
    def _configure_tts(self):
        """Configure text-to-speech settings"""
        if not self.tts_engine:
            return
            
        try:
            # Set voice properties
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Try to select preferred voice gender
                for voice in voices:
                    if (self.config.preferred_voice.lower() in voice.name.lower() or
                        self.config.preferred_voice.lower() in str(voice.gender).lower()):
                        self.tts_engine.setProperty('voice', voice.id)
                        break
            
            # Set speech rate and volume
            self.tts_engine.setProperty('rate', self.config.voice_speed)
            self.tts_engine.setProperty('volume', self.config.voice_volume)
            
        except Exception as e:
            self.logger.warning(f"TTS configuration failed: {e}")
    
    def add_voice_callback(self, callback: Callable[[str, float], None]):
        """Add callback for voice recognition results"""
        self.voice_callbacks.append(callback)
    
    async def _on_wake_word_detected(self, wake_word: str):
        """Handle wake word detection"""
        self.logger.info(f"Wake word '{wake_word}' detected - starting voice recognition")
        
        # Provide audio feedback
        if self.config.voice_feedback and self.tts_engine:
            await self._speak_async("Yes?")
        
        # Start listening for command
        await self.listen_for_command(timeout=self.config.voice_activation_timeout)
    
    async def start_continuous_listening(self):
        """Start continuous voice monitoring"""
        if not self.microphone or not self.recognizer:
            self.logger.error("Voice recognition not available")
            return
        
        self.is_listening = True
        self.logger.info("Starting continuous voice listening")
        
        # Start wake word detection if available
        if self.wake_word_detector:
            asyncio.create_task(self.wake_word_detector.start_detection())
        
        # Start background audio processing
        if self.config.continuous_listening:
            asyncio.create_task(self._continuous_audio_processing())
    
    async def _continuous_audio_processing(self):
        """Continuous background audio processing"""
        while self.is_listening:
            try:
                if not self.is_processing and not self.audio_queue.empty():
                    audio_data = self.audio_queue.get_nowait()
                    await self._process_audio(audio_data)
                
                await asyncio.sleep(0.1)  # Prevent high CPU usage
                
            except Exception as e:
                self.logger.error(f"Continuous audio processing error: {e}")
                await asyncio.sleep(1)
    
    async def listen_for_command(self, timeout: int = 5) -> Optional[str]:
        """Listen for a voice command with timeout"""
        if not self.microphone or not self.recognizer:
            return None
            
        try:
            self.is_processing = True
            self.logger.info(f"Listening for command (timeout: {timeout}s)")
            
            with self.microphone as source:
                # Listen for audio with timeout
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            # Process the audio
            result = await self._recognize_speech(audio)
            
            return result
            
        except sr.WaitTimeoutError:
            self.logger.info("Voice command timeout")
            return None
        except Exception as e:
            self.logger.error(f"Voice command listening error: {e}")
            return None
        finally:
            self.is_processing = False
    
    async def _recognize_speech(self, audio) -> Optional[str]:
        """Recognize speech from audio data"""
        try:
            start_time = time.time()
            
            # Update statistics
            self.recognition_stats["total_attempts"] += 1
            
            # Try Google Speech Recognition first
            try:
                text = self.recognizer.recognize_google(
                    audio, 
                    language=self.config.language,
                    show_all=False
                )
                
                if text:
                    processing_time = time.time() - start_time
                    confidence = 1.0  # Google API doesn't return confidence
                    
                    self.recognition_stats["successful_recognitions"] += 1
                    self.logger.info(f"Speech recognized: '{text}' (time: {processing_time:.2f}s)")
                    
                    # Trigger callbacks
                    for callback in self.voice_callbacks:
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                await callback(text, confidence)
                            else:
                                callback(text, confidence)
                        except Exception as e:
                            self.logger.error(f"Voice callback error: {e}")
                    
                    return text
                    
            except sr.UnknownValueError:
                self.logger.debug("Speech not understood")
            except sr.RequestError as e:
                self.logger.warning(f"Google Speech Recognition error: {e}")
                
                # Fallback to offline recognition
                try:
                    text = self.recognizer.recognize_sphinx(audio)
                    if text:
                        self.logger.info(f"Offline speech recognized: '{text}'")
                        return text
                except Exception as offline_e:
                    self.logger.debug(f"Offline recognition failed: {offline_e}")
            
            return None
            
        except Exception as e:
            self.logger.error(f"Speech recognition error: {e}")
            return None
    
    async def _process_audio(self, audio_data):
        """Process raw audio data"""
        try:
            # Apply noise reduction if enabled
            if self.config.noise_reduction:
                audio_data = self.noise_reducer.reduce_noise(audio_data)
                audio_data = self.noise_reducer.enhance_speech(audio_data)
            
            # Convert to speech recognition format and process
            # This would need additional implementation for raw audio processing
            
        except Exception as e:
            self.logger.error(f"Audio processing error: {e}")
    
    async def speak(self, text: str, priority: bool = False):
        """Speak text using TTS"""
        if not self.tts_engine:
            self.logger.warning(f"TTS not available, would speak: {text}")
            return
            
        try:
            self.logger.info(f"Speaking: {text}")
            
            # Run TTS in thread to avoid blocking
            await self._speak_async(text)
            
        except Exception as e:
            self.logger.error(f"TTS error: {e}")
    
    async def _speak_async(self, text: str):
        """Async wrapper for TTS"""
        def _speak():
            if self.tts_engine:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _speak)
    
    def stop_listening(self):
        """Stop voice recognition"""
        self.is_listening = False
        
        if self.wake_word_detector:
            self.wake_word_detector.stop_detection()
        
        self.logger.info("Voice listening stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get voice system status"""
        return {
            "listening": self.is_listening,
            "processing": self.is_processing,
            "wake_word_available": bool(self.wake_word_detector and self.wake_word_detector.porcupine),
            "tts_available": bool(self.tts_engine),
            "microphone_available": bool(self.microphone),
            "recognition_stats": self.recognition_stats,
            "config": {
                "wake_words": self.config.wake_words,
                "continuous_listening": self.config.continuous_listening,
                "noise_reduction": self.config.noise_reduction,
                "voice_feedback": self.config.voice_feedback
            }
        }
    
    async def test_voice_system(self) -> Dict[str, Any]:
        """Test all voice system components"""
        results = {
            "microphone": False,
            "tts": False,
            "wake_word": False,
            "recognition": False
        }
        
        try:
            # Test microphone
            if self.microphone:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                results["microphone"] = True
            
            # Test TTS
            if self.tts_engine:
                await self._speak_async("Voice system test")
                results["tts"] = True
            
            # Test wake word detection
            if self.wake_word_detector and self.wake_word_detector.porcupine:
                results["wake_word"] = True
            
            # Test recognition (short test)
            if self.microphone:
                test_result = await self.listen_for_command(timeout=1)
                results["recognition"] = test_result is not None
                
        except Exception as e:
            self.logger.error(f"Voice system test error: {e}")
        
        return results
    
    def cleanup(self):
        """Cleanup voice system resources"""
        self.stop_listening()
        
        if self.wake_word_detector:
            self.wake_word_detector.cleanup()
        
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except:
                pass