"""
ULTRON Voice Processor
=====================

Enhanced voice recognition and text-to-speech system with wake word detection,
multiple engine support, and continuous listening capabilities.
"""

import os
import sys
import time
import threading
import logging
import asyncio
import queue
from typing import Optional, Dict, Any, List, Callable
from pathlib import Path

# Voice recognition and TTS imports
try:
    import speech_recognition as sr
    import pyttsx3
    import pyaudio
    from pydub import AudioSegment
    from pydub.playback import play
except ImportError as e:
    print(f"Voice processing dependencies missing: {e}")
    print("Install with: pip install speechrecognition pyttsx3 pyaudio pydub")

# Wake word detection
try:
    import pvporcupine
    PORCUPINE_AVAILABLE = True
except ImportError:
    PORCUPINE_AVAILABLE = False
    print("Porcupine wake word detection not available. Install with: pip install pvporcupine")


class VoiceProcessor:
    """Advanced voice processing with wake word detection and continuous listening."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize voice processor with configuration."""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize defaults
        self.recognizer = None
        self.microphone = None
        self.tts_engine = None
        self.porcupine = None
        
        # Voice recognition setup
        try:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            self.logger.info("Speech recognition initialized")
        except Exception as e:
            self.logger.warning(f"Speech recognition not available: {e}")
        
        # TTS setup
        try:
            self.tts_engine = pyttsx3.init()
            self._setup_tts()
            self.logger.info("Text-to-speech initialized")
        except Exception as e:
            self.logger.warning(f"Text-to-speech not available: {e}")
        
        # Wake word detection
        self.wake_words = self.config.wake_words if hasattr(self.config, 'wake_words') else ['ultron', 'hello', 'computer']
        self._setup_wake_word_detection()
        
        # Threading and state
        self.listening = False
        self.wake_word_active = False
        self.audio_queue = queue.Queue()
        self.command_callbacks: List[Callable] = []
        
        # Performance optimization
        if self.recognizer:
            self.recognizer.energy_threshold = 4000
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
            self.recognizer.operation_timeout = 1
        
        self.logger.info("Voice processor initialized")
    
    def _setup_tts(self):
        """Configure text-to-speech engine."""
        try:
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Prefer female voice if available
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
                else:
                    self.tts_engine.setProperty('voice', voices[0].id)
            
            # Set speaking rate and volume
            self.tts_engine.setProperty('rate', self.config.get('tts_rate', 150))
            self.tts_engine.setProperty('volume', self.config.get('tts_volume', 0.9))
            
        except Exception as e:
            self.logger.error(f"TTS setup error: {e}")
    
    def _setup_wake_word_detection(self):
        """Initialize wake word detection if available."""
        if not PORCUPINE_AVAILABLE:
            self.logger.warning("Wake word detection not available")
            return
        
        try:
            # Initialize Porcupine for wake word detection
            access_key = self.config.get('porcupine_access_key')
            if access_key:
                self.porcupine = pvporcupine.create(
                    access_key=access_key,
                    keywords=['computer', 'hey google']  # Built-in keywords
                )
                self.logger.info("Wake word detection initialized")
            else:
                self.logger.warning("Porcupine access key not configured")
                
        except Exception as e:
            self.logger.error(f"Wake word detection setup failed: {e}")
    
    def calibrate_microphone(self, duration: int = 2):
        """Calibrate microphone for ambient noise."""
        try:
            with self.microphone as source:
                self.logger.info("Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=duration)
                self.logger.info(f"Microphone calibrated. Energy threshold: {self.recognizer.energy_threshold}")
        except Exception as e:
            self.logger.error(f"Microphone calibration failed: {e}")
    
    def speak(self, text: str, interrupt: bool = True):
        """Convert text to speech with options."""
        try:
            if interrupt and self.tts_engine._inLoop:
                self.tts_engine.stop()
            
            self.logger.info(f"Speaking: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            
        except Exception as e:
            self.logger.error(f"Speech synthesis error: {e}")
    
    async def speak_async(self, text: str):
        """Asynchronous text-to-speech."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.speak, text, False)
    
    def listen_once(self, timeout: int = 5, phrase_timeout: int = 1) -> Optional[str]:
        """Listen for a single command with timeout."""
        try:
            with self.microphone as source:
                self.logger.debug("Listening for command...")
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_timeout
                )
                
                # Try multiple recognition services
                text = self._recognize_speech(audio)
                if text:
                    self.logger.info(f"Recognized: {text}")
                return text
                
        except sr.WaitTimeoutError:
            self.logger.debug("Listening timeout")
        except sr.UnknownValueError:
            self.logger.debug("Could not understand audio")
        except Exception as e:
            self.logger.error(f"Speech recognition error: {e}")
        
        return None
    
    def _recognize_speech(self, audio) -> Optional[str]:
        """Try multiple speech recognition services."""
        # Try Google Speech Recognition (free tier)
        try:
            return self.recognizer.recognize_google(audio)
        except:
            pass
        
        # Try Sphinx (offline)
        try:
            return self.recognizer.recognize_sphinx(audio)
        except:
            pass
        
        # Try Whisper if available
        try:
            return self.recognizer.recognize_whisper(audio)
        except:
            pass
        
        return None
    
    def start_listening(self):
        """Start continuous listening with wake word detection."""
        if self.listening:
            return
        
        self.listening = True
        self.wake_word_active = True
        
        # Start wake word detection thread
        if self.porcupine:
            threading.Thread(target=self._wake_word_listener, daemon=True).start()
        
        # Start main listening thread
        threading.Thread(target=self._continuous_listener, daemon=True).start()
        
        self.logger.info("Started continuous listening")
    
    def stop_listening(self):
        """Stop continuous listening."""
        self.listening = False
        self.wake_word_active = False
        self.logger.info("Stopped continuous listening")
    
    def _wake_word_listener(self):
        """Wake word detection loop."""
        if not self.porcupine:
            return
        
        try:
            audio = pyaudio.PyAudio()
            audio_stream = audio.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length
            )
            
            while self.wake_word_active:
                pcm = audio_stream.read(self.porcupine.frame_length)
                pcm = [int.from_bytes(pcm[i:i+2], byteorder='little', signed=True) 
                       for i in range(0, len(pcm), 2)]
                
                keyword_index = self.porcupine.process(pcm)
                if keyword_index >= 0:
                    self.logger.info("Wake word detected!")
                    self._trigger_wake_word()
            
            audio_stream.close()
            audio.terminate()
            
        except Exception as e:
            self.logger.error(f"Wake word detection error: {e}")
    
    def _continuous_listener(self):
        """Continuous speech recognition loop."""
        while self.listening:
            try:
                if self.wake_word_active:
                    time.sleep(0.1)  # Wait for wake word
                    continue
                
                # Listen for command after wake word
                command = self.listen_once(timeout=10, phrase_timeout=3)
                if command:
                    self._process_command(command)
                
                # Reset wake word detection
                self.wake_word_active = True
                
            except Exception as e:
                self.logger.error(f"Continuous listening error: {e}")
                time.sleep(1)
    
    def _trigger_wake_word(self):
        """Handle wake word detection."""
        self.wake_word_active = False
        
        # Play wake word sound
        self._play_wake_sound()
        
        # Optional: Provide audio feedback
        if self.config.get('wake_word_feedback', True):
            self.speak("Yes?")
    
    def _play_wake_sound(self):
        """Play wake word detection sound."""
        try:
            # Generate a simple beep sound
            import numpy as np
            
            sample_rate = 44100
            duration = 0.2  # 200ms
            frequency = 800  # 800 Hz beep
            
            t = np.linspace(0, duration, int(sample_rate * duration))
            wave = 0.3 * np.sin(frequency * 2 * np.pi * t)
            
            # Convert to audio segment and play
            audio_data = (wave * 32767).astype(np.int16)
            audio_segment = AudioSegment(
                audio_data.tobytes(),
                frame_rate=sample_rate,
                sample_width=2,
                channels=1
            )
            play(audio_segment)
            
        except Exception as e:
            self.logger.debug(f"Wake sound playback failed: {e}")
    
    def _process_command(self, command: str):
        """Process recognized voice command."""
        self.logger.info(f"Processing command: {command}")
        
        # Call registered command callbacks
        for callback in self.command_callbacks:
            try:
                callback(command)
            except Exception as e:
                self.logger.error(f"Command callback error: {e}")
    
    def add_command_callback(self, callback: Callable[[str], None]):
        """Add callback for voice commands."""
        self.command_callbacks.append(callback)
        self.logger.debug(f"Added command callback: {callback.__name__}")
    
    def remove_command_callback(self, callback: Callable[[str], None]):
        """Remove command callback."""
        if callback in self.command_callbacks:
            self.command_callbacks.remove(callback)
            self.logger.debug(f"Removed command callback: {callback.__name__}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get voice processor status."""
        return {
            'listening': self.listening,
            'wake_word_active': self.wake_word_active,
            'wake_word_detection': self.porcupine is not None,
            'tts_available': self.tts_engine is not None,
            'microphone_available': self.microphone is not None,
            'energy_threshold': self.recognizer.energy_threshold
        }


# Utility functions for voice processing
def test_voice_system():
    """Test voice system functionality."""
    processor = VoiceProcessor()
    
    print("Testing voice processor...")
    
    # Test TTS
    processor.speak("Voice processor test initiated")
    
    # Test microphone
    processor.calibrate_microphone(duration=1)
    
    # Test speech recognition
    processor.speak("Please say something")
    result = processor.listen_once(timeout=5)
    
    if result:
        processor.speak(f"I heard: {result}")
        print(f"Recognition result: {result}")
    else:
        processor.speak("No speech detected")
        print("No speech detected")
    
    print("Voice processor test complete")
    return processor.get_status()


if __name__ == "__main__":
    # Run voice system test
    test_voice_system()