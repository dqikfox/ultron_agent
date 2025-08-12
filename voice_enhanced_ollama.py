"""
Enhanced Voice Manager for ULTRON Agent 2
Incorporates wake-word detection, ambient noise adjustment, and accessibility features
Based on advanced voice-controlled Ollama client patterns
"""

import threading
import queue
import time
import logging
from typing import Optional, Callable, Dict, Any
import speech_recognition as sr
import pyttsx3

logger = logging.getLogger(__name__)

class UltronEnhancedVoiceManager:
    """Enhanced voice manager with wake-word detection and accessibility features"""
    
    # Special tokens for communication between threads
    WAKE_TOKEN = "__ULTRON_WAKE__"
    STOP_TOKEN = "__ULTRON_STOP__"
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize enhanced voice manager with configuration"""
        self.config = config or {}
        
        # Wake-word configuration
        self.wake_word = self.config.get('wake_word', 'ultron').lower()
        self.stop_word = self.config.get('stop_word', 'stop').lower()
        
        # Voice recognition setup
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # TTS setup with accessibility configuration
        self.tts_engine = pyttsx3.init()
        self._configure_tts()
        
        # State management
        self.active = False  # True after wake-word detection
        self.listening = False
        self.voice_queue = queue.Queue()
        
        # Threading
        self.speech_thread = None
        self.running = False
        
        # Callbacks
        self.on_wake_callback: Optional[Callable] = None
        self.on_command_callback: Optional[Callable[[str], None]] = None
        self.on_stop_callback: Optional[Callable] = None
        
        logger.info(f"Enhanced Voice Manager initialized - Wake word: '{self.wake_word}'")
    
    def _configure_tts(self):
        """Configure TTS engine for accessibility"""
        # Speech rate optimization for cognitive disabilities
        speech_rate = self.config.get('speech_rate', 170)  # WPM
        self.tts_engine.setProperty('rate', speech_rate)
        
        # Volume for hearing impairments
        volume = self.config.get('volume', 1.0)
        self.tts_engine.setProperty('volume', volume)
        
        # Voice selection for clarity
        voice_id = self.config.get('voice_id')
        if voice_id:
            voices = self.tts_engine.getProperty('voices')
            if voice_id < len(voices):
                self.tts_engine.setProperty('voice', voices[voice_id].id)
        
        logger.info(f"TTS configured - Rate: {speech_rate} WPM, Volume: {volume}")
    
    def speak(self, text: str, priority: bool = False):
        """Speak text with accessibility considerations"""
        try:
            if priority:
                # Priority speech (interrupts current speech)
                self.tts_engine.stop()
            
            logger.info(f"Speaking: {text[:50]}...")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            
        except Exception as e:
            logger.error(f"TTS error: {e}")
    
    def start_listening(self):
        """Start the voice recognition system"""
        if self.running:
            logger.warning("Voice manager already running")
            return
        
        self.running = True
        self.speech_thread = threading.Thread(target=self._voice_recognition_loop, daemon=True)
        self.speech_thread.start()
        
        logger.info("Voice recognition started - Listening for wake-word")
        self.speak(f"ULTRON voice system ready. Say '{self.wake_word}' to begin.", priority=True)
    
    def stop_listening(self):
        """Stop the voice recognition system"""
        self.running = False
        self.active = False
        
        if self.speech_thread and self.speech_thread.is_alive():
            self.speech_thread.join(timeout=2)
        
        logger.info("Voice recognition stopped")
        self.speak("ULTRON voice system deactivated.", priority=True)
    
    def _voice_recognition_loop(self):
        """Main voice recognition loop with wake-word detection"""
        # Ambient noise adjustment for better accuracy
        try:
            with self.microphone as source:
                logger.info("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                logger.info("Ambient noise adjustment complete")
        except Exception as e:
            logger.error(f"Ambient noise adjustment failed: {e}")
        
        while self.running:
            try:
                self._listen_for_speech()
            except Exception as e:
                logger.error(f"Voice recognition error: {e}")
                time.sleep(1)  # Brief pause before retrying
    
    def _listen_for_speech(self):
        """Listen for speech and process based on current state"""
        try:
            with self.microphone as source:
                # Use timeout and phrase limits for better control
                audio = self.recognizer.listen(
                    source, 
                    phrase_time_limit=8,
                    timeout=1
                )
            
            # Recognize speech (using Google by default, could add offline option)
            text = self.recognizer.recognize_google(audio).lower()
            logger.debug(f"Recognized: {text}")
            
            if not self.active:
                # Waiting for wake-word
                if self.wake_word in text:
                    self._handle_wake_activation()
            else:
                # Active conversation mode
                if self.stop_word in text:
                    self._handle_stop_command()
                else:
                    self._handle_voice_command(text)
                    
        except sr.WaitTimeoutError:
            # Normal timeout - continue listening
            pass
        except sr.UnknownValueError:
            # Silence or unclear speech - ignore
            pass
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {e}")
            time.sleep(2)  # Back-off on service errors
    
    def _handle_wake_activation(self):
        """Handle wake-word detection"""
        self.active = True
        logger.info("Wake-word detected - ULTRON activated")
        
        # Accessibility feedback
        self.speak("ULTRON activated. How can I assist you?", priority=True)
        
        # Trigger callback
        if self.on_wake_callback:
            try:
                self.on_wake_callback()
            except Exception as e:
                logger.error(f"Wake callback error: {e}")
    
    def _handle_stop_command(self):
        """Handle stop command"""
        self.active = False
        logger.info("Stop command received - ULTRON deactivated")
        
        # Accessibility feedback
        self.speak("ULTRON deactivated. Say 'ultron' to reactivate.", priority=True)
        
        # Trigger callback
        if self.on_stop_callback:
            try:
                self.on_stop_callback()
            except Exception as e:
                logger.error(f"Stop callback error: {e}")
    
    def _handle_voice_command(self, command: str):
        """Handle voice command during active conversation"""
        logger.info(f"Processing command: {command}")
        
        # Queue command for processing
        self.voice_queue.put(command)
        
        # Trigger callback
        if self.on_command_callback:
            try:
                self.on_command_callback(command)
            except Exception as e:
                logger.error(f"Command callback error: {e}")
        
        # Accessibility feedback for confirmation
        self.speak("Processing your request...", priority=False)
    
    def set_wake_callback(self, callback: Callable):
        """Set callback for wake-word detection"""
        self.on_wake_callback = callback
    
    def set_command_callback(self, callback: Callable[[str], None]):
        """Set callback for voice commands"""
        self.on_command_callback = callback
    
    def set_stop_callback(self, callback: Callable):
        """Set callback for stop command"""
        self.on_stop_callback = callback
    
    def get_pending_commands(self):
        """Get all pending voice commands"""
        commands = []
        try:
            while True:
                command = self.voice_queue.get_nowait()
                commands.append(command)
        except queue.Empty:
            pass
        return commands
    
    def is_active(self) -> bool:
        """Check if voice manager is in active conversation mode"""
        return self.active
    
    def is_listening(self) -> bool:
        """Check if voice manager is listening"""
        return self.running
    
    def emergency_stop(self):
        """Emergency stop for all voice operations"""
        logger.warning("Emergency stop activated")
        self.tts_engine.stop()
        self.stop_listening()
        self.speak("Emergency stop activated. ULTRON systems halted.", priority=True)


# Integration with existing ULTRON systems
class UltronVoiceIntegration:
    """Integration layer for ULTRON Agent 2"""
    
    def __init__(self, agent_core=None, action_logger=None):
        self.agent_core = agent_core
        self.action_logger = action_logger
        
        # Voice manager configuration for accessibility
        voice_config = {
            'wake_word': 'ultron',
            'stop_word': 'stop',
            'speech_rate': 150,  # Slower for cognitive disabilities
            'volume': 1.0
        }
        
        self.voice_manager = UltronEnhancedVoiceManager(voice_config)
        self._setup_callbacks()
        
    def _setup_callbacks(self):
        """Setup callbacks for ULTRON integration"""
        
        def on_wake():
            if self.action_logger:
                self.action_logger.log_voice_action("wake_word_detected", "ULTRON voice system activated")
            
        def on_command(command: str):
            if self.action_logger:
                self.action_logger.log_voice_action("voice_command", command)
            
            # Process command through existing ULTRON systems
            if self.agent_core:
                try:
                    response = self.agent_core.process_command(command)
                    self.voice_manager.speak(f"Command executed. {response}")
                except Exception as e:
                    self.voice_manager.speak(f"Error processing command: {str(e)}")
        
        def on_stop():
            if self.action_logger:
                self.action_logger.log_voice_action("stop_command", "ULTRON voice system deactivated")
        
        self.voice_manager.set_wake_callback(on_wake)
        self.voice_manager.set_command_callback(on_command)
        self.voice_manager.set_stop_callback(on_stop)
    
    def start(self):
        """Start integrated voice system"""
        self.voice_manager.start_listening()
    
    def stop(self):
        """Stop integrated voice system"""
        self.voice_manager.stop_listening()


# Example usage for ULTRON Agent 2
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create enhanced voice manager
    voice_integration = UltronVoiceIntegration()
    
    try:
        voice_integration.start()
        
        # Keep running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down ULTRON voice system...")
        voice_integration.stop()
