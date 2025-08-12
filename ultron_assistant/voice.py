# voice.py
import speech_recognition as sr
import pyttsx3
import asyncio
import logging
import threading
import time
from threading import Thread, Lock
from typing import Optional, Dict, Any, Callable

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- Speech-to-Text ----------
class VoiceRecognizer:
    """Enhanced speech recognition with multiple engine support."""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.is_listening = False
        self._setup_microphone()
    
    def _setup_microphone(self):
        """Setup microphone with error handling."""
        try:
            self.microphone = sr.Microphone()
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            logger.info("Microphone initialized successfully")
        except OSError as e:
            logger.error(f"No microphone detected: {e}")
            self.microphone = None
        except Exception as e:
            logger.error(f"Error setting up microphone: {e}")
            self.microphone = None
    
    def is_available(self) -> bool:
        """Check if voice recognition is available."""
        return self.microphone is not None
    
    def listen_once(self, timeout: int = 10, phrase_time_limit: int = 10) -> Optional[str]:
        """
        Listen for speech and return recognized text.
        
        Args:
            timeout: Maximum time to wait for speech to start
            phrase_time_limit: Maximum time to record phrase
            
        Returns:
            str: Recognized text or None if failed
        """
        if not self.is_available():
            logger.warning("Microphone not available")
            return None
        
        try:
            self.is_listening = True
            logger.info("Listening for speech...")
            
            with self.microphone as source:
                # Listen for audio with timeout
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
            
            logger.info("Processing speech...")
            # Try to recognize speech using Google's service
            text = self.recognizer.recognize_google(audio)
            logger.info(f"Recognized: {text}")
            return text
            
        except sr.WaitTimeoutError:
            logger.warning("Listening timeout - no speech detected")
            return None
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during speech recognition: {e}")
            return None
        finally:
            self.is_listening = False
    
    def listen_continuously(self, callback: Callable[[str], None], stop_event: threading.Event):
        """
        Continuously listen for speech and call callback with recognized text.
        
        Args:
            callback: Function to call with recognized text
            stop_event: Event to signal when to stop listening
        """
        if not self.is_available():
            logger.error("Cannot start continuous listening - microphone not available")
            return
        
        logger.info("Starting continuous speech recognition...")
        
        while not stop_event.is_set():
            try:
                text = self.listen_once(timeout=1, phrase_time_limit=5)
                if text:
                    callback(text)
            except Exception as e:
                logger.error(f"Error in continuous listening: {e}")
                time.sleep(1)  # Brief pause before retrying
        
        logger.info("Stopped continuous speech recognition")

# Global recognizer instance
recognizer_instance = VoiceRecognizer()

def listen_once(recognizer: sr.Recognizer = None, mic: sr.Microphone = None, timeout: int = 10) -> Optional[str]:
    """
    Compatibility function for the original interface.
    Blocks until a phrase is captured or timeout.
    Returns the recognized text or None.
    """
    return recognizer_instance.listen_once(timeout=timeout)

# ---------- Text-to-Speech ----------
class Speaker:
    """Enhanced text-to-speech with multiple voice options and thread safety."""
    
    def __init__(self):
        self.engine = None
        self.lock = Lock()
        self.is_speaking = False
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize the TTS engine with error handling."""
        try:
            self.engine = pyttsx3.init()
            self._configure_voice()
            logger.info("TTS engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            self.engine = None
    
    def _configure_voice(self):
        """Configure voice properties for Ultron-like speech."""
        if not self.engine:
            return
        
        try:
            voices = self.engine.getProperty('voices')
            
            # Try to find a suitable voice (prefer male, deeper voices)
            selected_voice = None
            voice_preferences = [
                "Microsoft David Desktop",
                "Microsoft Mark Desktop", 
                "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_DAVID_11.0",
                "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0"
            ]
            
            for voice in voices:
                for preferred in voice_preferences:
                    if preferred.lower() in voice.name.lower():
                        selected_voice = voice
                        break
                if selected_voice:
                    break
            
            # Use the first available voice if no preferred voice found
            if not selected_voice and voices:
                selected_voice = voices[0]
            
            if selected_voice:
                self.engine.setProperty('voice', selected_voice.id)
                logger.info(f"Selected voice: {selected_voice.name}")
            
            # Configure speech rate and volume for Ultron-like delivery
            self.engine.setProperty('rate', 170)    # words per minute (slightly slower)
            self.engine.setProperty('volume', 1.0)  # maximum volume
            
        except Exception as e:
            logger.error(f"Error configuring voice: {e}")
    
    def is_available(self) -> bool:
        """Check if TTS is available."""
        return self.engine is not None
    
    def say(self, text: str, block: bool = False):
        """
        Speak the given text.
        
        Args:
            text: Text to speak
            block: Whether to block until speech is complete
        """
        if not self.is_available():
            logger.warning("TTS engine not available")
            return
        
        if not text or not text.strip():
            return
        
        with self.lock:
            if self.is_speaking:
                logger.info("Already speaking, queuing text...")
        
        def _speak():
            try:
                with self.lock:
                    self.is_speaking = True
                    logger.info(f"Speaking: {text[:50]}{'...' if len(text) > 50 else ''}")
                    self.engine.say(text)
                    self.engine.runAndWait()
            except Exception as e:
                logger.error(f"Error during speech: {e}")
            finally:
                with self.lock:
                    self.is_speaking = False
        
        if block:
            _speak()
        else:
            # Run in background thread
            Thread(target=_speak, daemon=True).start()
    
    def stop(self):
        """Stop current speech."""
        if self.engine:
            try:
                self.engine.stop()
                with self.lock:
                    self.is_speaking = False
            except Exception as e:
                logger.error(f"Error stopping speech: {e}")
    
    def get_available_voices(self) -> list:
        """Get list of available voices."""
        if not self.engine:
            return []
        
        try:
            voices = self.engine.getProperty('voices')
            return [{"id": v.id, "name": v.name, "age": getattr(v, 'age', 'unknown')} for v in voices]
        except Exception as e:
            logger.error(f"Error getting voices: {e}")
            return []
    
    def set_voice(self, voice_id: str) -> bool:
        """
        Set the voice by ID.
        
        Args:
            voice_id: Voice ID to use
            
        Returns:
            bool: True if successful
        """
        if not self.engine:
            return False
        
        try:
            self.engine.setProperty('voice', voice_id)
            logger.info(f"Voice changed to: {voice_id}")
            return True
        except Exception as e:
            logger.error(f"Error setting voice: {e}")
            return False
    
    def set_rate(self, rate: int) -> bool:
        """
        Set speech rate.
        
        Args:
            rate: Words per minute (typically 150-200)
            
        Returns:
            bool: True if successful
        """
        if not self.engine:
            return False
        
        try:
            self.engine.setProperty('rate', rate)
            logger.info(f"Speech rate set to: {rate}")
            return True
        except Exception as e:
            logger.error(f"Error setting rate: {e}")
            return False

# ---------- Enhanced Voice Assistant Class ----------
class UltronVoiceAssistant:
    """Complete voice assistant combining speech recognition and synthesis."""
    
    def __init__(self):
        self.recognizer = VoiceRecognizer()
        self.speaker = Speaker()
        self.continuous_listening = False
        self.stop_listening_event = threading.Event()
        self.listening_thread = None
        self.callback = None
    
    def is_available(self) -> bool:
        """Check if both speech recognition and synthesis are available."""
        return self.recognizer.is_available() and self.speaker.is_available()
    
    def speak(self, text: str, block: bool = False):
        """Speak text using the TTS engine."""
        self.speaker.say(text, block)
    
    def listen(self, timeout: int = 10) -> Optional[str]:
        """Listen for a single phrase."""
        return self.recognizer.listen_once(timeout=timeout)
    
    def start_continuous_listening(self, callback: Callable[[str], None]):
        """
        Start continuous listening mode.
        
        Args:
            callback: Function to call with recognized speech
        """
        if self.continuous_listening:
            logger.warning("Continuous listening already active")
            return
        
        self.callback = callback
        self.continuous_listening = True
        self.stop_listening_event.clear()
        
        self.listening_thread = threading.Thread(
            target=self.recognizer.listen_continuously,
            args=(self._handle_speech, self.stop_listening_event),
            daemon=True
        )
        self.listening_thread.start()
        logger.info("Started continuous listening")
    
    def stop_continuous_listening(self):
        """Stop continuous listening mode."""
        if not self.continuous_listening:
            return
        
        self.continuous_listening = False
        self.stop_listening_event.set()
        
        if self.listening_thread:
            self.listening_thread.join(timeout=2)
        
        logger.info("Stopped continuous listening")
    
    def _handle_speech(self, text: str):
        """Handle recognized speech in continuous mode."""
        if self.callback:
            try:
                self.callback(text)
            except Exception as e:
                logger.error(f"Error in speech callback: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get voice assistant status."""
        return {
            "recognition_available": self.recognizer.is_available(),
            "synthesis_available": self.speaker.is_available(),
            "currently_listening": self.recognizer.is_listening,
            "currently_speaking": self.speaker.is_speaking,
            "continuous_listening": self.continuous_listening
        }

# Create global instance for compatibility
voice_assistant = UltronVoiceAssistant()

# Compatibility functions
def say(text: str):
    """Compatibility function for simple TTS."""
    voice_assistant.speak(text)

def listen():
    """Compatibility function for simple speech recognition."""
    return voice_assistant.listen()

if __name__ == "__main__":
    # Test the voice system
    def test_voice_system():
        assistant = UltronVoiceAssistant()
        
        print("Voice System Status:")
        status = assistant.get_status()
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        if assistant.speaker.is_available():
            print("\nTesting TTS...")
            assistant.speak("Hello, I am Ultron. Voice system is operational.")
            
            # List available voices
            voices = assistant.speaker.get_available_voices()
            print(f"\nAvailable voices: {len(voices)}")
            for voice in voices[:3]:  # Show first 3
                print(f"  - {voice['name']}")
        
        if assistant.recognizer.is_available():
            print("\nTesting speech recognition...")
            print("Say something (5 second timeout):")
            text = assistant.listen(timeout=5)
            if text:
                print(f"You said: {text}")
                assistant.speak(f"You said: {text}")
            else:
                print("No speech detected")
    
    test_voice_system()
