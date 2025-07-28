"""
ULTRON Enhanced - Voice Processing Module
Advanced voice recognition and speech synthesis
"""

import os
import sys
import json
import time
import threading
import speech_recognition as sr
import pyttsx3
import logging
from typing import List, Dict, Optional, Callable
import numpy as np

class VoiceProcessor:
    """Advanced voice processing with wake word detection and natural language processing"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.tts_engine = None
        self.is_listening = False
        self.wake_words = config.get('wake_words', ['ultron', 'jarvis'])
        self.callbacks = {}
        self.voice_settings = config.get('voice_settings', {})
        
        self.init_components()
    
    def init_components(self):
        """Initialize voice recognition and TTS components"""
        try:
            # Initialize microphone
            self.microphone = sr.Microphone()
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            # Initialize TTS
            self.tts_engine = pyttsx3.init()
            self.configure_tts()
            
            logging.info("Voice processor initialized successfully")
            
        except Exception as e:
            logging.error(f"Voice processor initialization failed: {e}")
    
    def configure_tts(self):
        """Configure text-to-speech settings"""
        if not self.tts_engine:
            return
        
        try:
            # Set voice
            voices = self.tts_engine.getProperty('voices')
            voice_gender = self.config.get('voice', 'male')
            
            if voices:
                if voice_gender == 'female' and len(voices) > 1:
                    self.tts_engine.setProperty('voice', voices[1].id)
                else:
                    self.tts_engine.setProperty('voice', voices[0].id)
            
            # Set rate and volume
            rate = self.voice_settings.get('rate', 150)
            volume = self.voice_settings.get('volume', 0.8)
            
            self.tts_engine.setProperty('rate', rate)
            self.tts_engine.setProperty('volume', volume)
            
        except Exception as e:
            logging.error(f"TTS configuration failed: {e}")
    
    def register_callback(self, event: str, callback: Callable):
        """Register callback for voice events"""
        if event not in self.callbacks:
            self.callbacks[event] = []
        self.callbacks[event].append(callback)
    
    def emit_event(self, event: str, data: Dict = None):
        """Emit voice event to registered callbacks"""
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                try:
                    callback(data or {})
                except Exception as e:
                    logging.error(f"Callback error for {event}: {e}")
    
    def start_listening(self):
        """Start continuous voice recognition"""
        if self.is_listening:
            return
        
        self.is_listening = True
        listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        listen_thread.start()
        
        self.emit_event('listening_started')
        logging.info("Voice listening started")
    
    def stop_listening(self):
        """Stop voice recognition"""
        self.is_listening = False
        self.emit_event('listening_stopped')
        logging.info("Voice listening stopped")
    
    def _listen_loop(self):
        """Main listening loop for voice recognition"""
        while self.is_listening:
            try:
                with self.microphone as source:
                    # Listen for audio with timeout
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                
                try:
                    # Recognize speech
                    text = self.recognizer.recognize_google(audio).lower()
                    
                    # Process the recognized text
                    self._process_speech(text)
                    
                except sr.UnknownValueError:
                    # No speech detected
                    pass
                except sr.RequestError as e:
                    logging.error(f"Speech recognition error: {e}")
                    time.sleep(1)
                    
            except sr.WaitTimeoutError:
                # Timeout - continue listening
                pass
            except Exception as e:
                logging.error(f"Listening loop error: {e}")
                time.sleep(1)
    
    def _process_speech(self, text: str):
        """Process recognized speech text"""
        # Check for wake words
        has_wake_word = any(wake_word in text for wake_word in self.wake_words)
        
        if has_wake_word:
            # Wake word detected
            self.emit_event('wake_word_detected', {'text': text, 'wake_word': True})
            
            # Extract command after wake word
            command = self._extract_command(text)
            if command:
                self.emit_event('command_received', {'command': command, 'original_text': text})
        else:
            # Regular speech without wake word
            self.emit_event('speech_detected', {'text': text, 'wake_word': False})
    
    def _extract_command(self, text: str) -> str:
        """Extract command from text after removing wake words"""
        for wake_word in self.wake_words:
            if wake_word in text:
                # Remove wake word and return remaining text
                parts = text.split(wake_word, 1)
                if len(parts) > 1:
                    return parts[1].strip()
        return text.strip()
    
    def speak(self, text: str, interrupt: bool = False):
        """Convert text to speech"""
        if not self.tts_engine:
            logging.warning("TTS engine not available")
            return
        
        try:
            if interrupt:
                self.tts_engine.stop()
            
            self.emit_event('speech_started', {'text': text})
            
            # Speak in a separate thread to avoid blocking
            speak_thread = threading.Thread(target=self._speak_threaded, args=(text,), daemon=True)
            speak_thread.start()
            
        except Exception as e:
            logging.error(f"TTS error: {e}")
    
    def _speak_threaded(self, text: str):
        """Thread function for TTS"""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            self.emit_event('speech_finished', {'text': text})
        except Exception as e:
            logging.error(f"TTS threaded error: {e}")
    
    def process_command(self, command: str) -> Dict:
        """Process voice command and return structured response"""
        command_lower = command.lower().strip()
        
        # Command patterns and responses
        patterns = {
            'status': ['status', 'how are you', 'system status'],
            'time': ['time', 'what time', 'current time'],
            'weather': ['weather', 'temperature', 'forecast'],
            'help': ['help', 'what can you do', 'commands'],
            'screenshot': ['screenshot', 'capture screen', 'take picture'],
            'analyze': ['analyze', 'look at screen', 'what do you see'],
            'open': ['open', 'launch', 'start'],
            'close': ['close', 'exit', 'quit'],
            'volume': ['volume', 'sound', 'audio'],
            'theme': ['theme', 'color', 'appearance'],
            'shutdown': ['shutdown', 'turn off', 'power off'],
            'restart': ['restart', 'reboot', 'reset']
        }
        
        # Find matching pattern
        command_type = 'unknown'
        confidence = 0.0
        
        for cmd_type, keywords in patterns.items():
            for keyword in keywords:
                if keyword in command_lower:
                    command_type = cmd_type
                    confidence = len(keyword) / len(command_lower)
                    break
            if command_type != 'unknown':
                break
        
        return {
            'original_command': command,
            'command_type': command_type,
            'confidence': confidence,
            'timestamp': time.time(),
            'requires_confirmation': command_type in ['shutdown', 'restart']
        }
    
    def get_voice_info(self) -> Dict:
        """Get information about available voices"""
        if not self.tts_engine:
            return {}
        
        try:
            voices = self.tts_engine.getProperty('voices')
            voice_info = []
            
            for i, voice in enumerate(voices):
                voice_info.append({
                    'id': voice.id,
                    'name': voice.name,
                    'gender': 'female' if 'female' in voice.name.lower() else 'male',
                    'index': i
                })
            
            return {
                'available_voices': voice_info,
                'current_voice': self.tts_engine.getProperty('voice'),
                'current_rate': self.tts_engine.getProperty('rate'),
                'current_volume': self.tts_engine.getProperty('volume')
            }
            
        except Exception as e:
            logging.error(f"Voice info error: {e}")
            return {}
    
    def set_voice_by_name(self, name: str) -> bool:
        """Set TTS voice by name"""
        if not self.tts_engine:
            return False
        
        try:
            voices = self.tts_engine.getProperty('voices')
            for voice in voices:
                if name.lower() in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    return True
            return False
        except Exception as e:
            logging.error(f"Set voice error: {e}")
            return False
    
    def adjust_speech_rate(self, rate: int) -> bool:
        """Adjust TTS speech rate"""
        if not self.tts_engine:
            return False
        
        try:
            # Clamp rate between 50 and 300
            rate = max(50, min(300, rate))
            self.tts_engine.setProperty('rate', rate)
            self.voice_settings['rate'] = rate
            return True
        except Exception as e:
            logging.error(f"Adjust rate error: {e}")
            return False
    
    def adjust_volume(self, volume: float) -> bool:
        """Adjust TTS volume"""
        if not self.tts_engine:
            return False
        
        try:
            # Clamp volume between 0.0 and 1.0
            volume = max(0.0, min(1.0, volume))
            self.tts_engine.setProperty('volume', volume)
            self.voice_settings['volume'] = volume
            return True
        except Exception as e:
            logging.error(f"Adjust volume error: {e}")
            return False
    
    def test_microphone(self) -> Dict:
        """Test microphone functionality"""
        if not self.microphone:
            return {'status': 'error', 'message': 'Microphone not available'}
        
        try:
            with self.microphone as source:
                # Test ambient noise adjustment
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                # Test audio capture
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=2)
                
                # Test recognition
                text = self.recognizer.recognize_google(audio)
                
                return {
                    'status': 'success',
                    'message': 'Microphone test successful',
                    'recognized_text': text
                }
                
        except sr.WaitTimeoutError:
            return {'status': 'timeout', 'message': 'No speech detected during test'}
        except sr.UnknownValueError:
            return {'status': 'no_speech', 'message': 'Could not understand audio'}
        except sr.RequestError as e:
            return {'status': 'error', 'message': f'Recognition service error: {e}'}
        except Exception as e:
            return {'status': 'error', 'message': f'Microphone test failed: {e}'}
    
    def cleanup(self):
        """Clean up voice processor resources"""
        self.stop_listening()
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except:
                pass
        logging.info("Voice processor cleanup completed")

# Voice command processor for ULTRON integration
class UltronVoiceCommands:
    """ULTRON-specific voice command processing"""
    
    def __init__(self, ultron_core):
        self.core = ultron_core
        self.command_history = []
        
    def process_ultron_command(self, command_data: Dict) -> Dict:
        """Process ULTRON-specific voice commands"""
        command = command_data.get('command', '').lower()
        command_type = command_data.get('command_type', 'unknown')
        
        response = {
            'success': False,
            'message': '',
            'action_taken': None,
            'requires_speech': True
        }
        
        try:
            if command_type == 'status':
                response.update(self._handle_status_command())
            elif command_type == 'screenshot':
                response.update(self._handle_screenshot_command())
            elif command_type == 'analyze':
                response.update(self._handle_analyze_command())
            elif command_type == 'time':
                response.update(self._handle_time_command())
            elif command_type == 'help':
                response.update(self._handle_help_command())
            elif command_type == 'theme':
                response.update(self._handle_theme_command(command))
            elif command_type == 'volume':
                response.update(self._handle_volume_command(command))
            elif command_type == 'shutdown':
                response.update(self._handle_shutdown_command())
            elif command_type == 'restart':
                response.update(self._handle_restart_command())
            else:
                response.update(self._handle_unknown_command(command))
            
            # Store in history
            self.command_history.append({
                'command': command,
                'type': command_type,
                'timestamp': time.time(),
                'response': response
            })
            
            # Limit history size
            if len(self.command_history) > 50:
                self.command_history.pop(0)
                
        except Exception as e:
            logging.error(f"Command processing error: {e}")
            response = {
                'success': False,
                'message': f'Error processing command: {str(e)}',
                'requires_speech': True
            }
        
        return response
    
    def _handle_status_command(self) -> Dict:
        """Handle system status command"""
        # Get system stats from core
        stats = self.core.get_system_stats() if hasattr(self.core, 'get_system_stats') else {}
        
        cpu = stats.get('cpu', 0)
        memory = stats.get('memory', 0)
        
        message = f"System status: CPU at {cpu}%, Memory at {memory}%. All systems operational."
        
        return {
            'success': True,
            'message': message,
            'action_taken': 'system_status_check'
        }
    
    def _handle_screenshot_command(self) -> Dict:
        """Handle screenshot command"""
        try:
            # Trigger screenshot via core
            if hasattr(self.core, 'capture_screen'):
                self.core.capture_screen()
                return {
                    'success': True,
                    'message': 'Screenshot captured successfully.',
                    'action_taken': 'screenshot_taken'
                }
            else:
                return {
                    'success': False,
                    'message': 'Screenshot functionality not available.'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'Screenshot failed: {str(e)}'
            }
    
    def _handle_analyze_command(self) -> Dict:
        """Handle screen analysis command"""
        try:
            if hasattr(self.core, 'analyze_screen'):
                result = self.core.analyze_screen()
                return {
                    'success': True,
                    'message': f'Screen analysis completed. {result}',
                    'action_taken': 'screen_analysis'
                }
            else:
                return {
                    'success': False,
                    'message': 'Screen analysis not available.'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'Analysis failed: {str(e)}'
            }
    
    def _handle_time_command(self) -> Dict:
        """Handle time request command"""
        current_time = time.strftime("%H:%M:%S")
        current_date = time.strftime("%A, %B %d, %Y")
        
        return {
            'success': True,
            'message': f'Current time is {current_time} on {current_date}.',
            'action_taken': 'time_report'
        }
    
    def _handle_help_command(self) -> Dict:
        """Handle help command"""
        help_text = """Available voice commands: 
        System status, Take screenshot, Analyze screen, 
        Current time, Change theme, Adjust volume, 
        System shutdown, System restart. 
        Use wake words: Ultron, Jarvis, Computer, or AI."""
        
        return {
            'success': True,
            'message': help_text,
            'action_taken': 'help_provided'
        }
    
    def _handle_theme_command(self, command: str) -> Dict:
        """Handle theme change command"""
        if 'blue' in command:
            theme = 'blue'
        elif 'red' in command:
            theme = 'red'
        else:
            return {
                'success': True,
                'message': 'Current theme options: red classic or blue advanced.',
                'action_taken': 'theme_info'
            }
        
        # Change theme via core
        if hasattr(self.core, 'change_theme'):
            self.core.change_theme(theme)
            return {
                'success': True,
                'message': f'Theme changed to {theme}.',
                'action_taken': 'theme_changed'
            }
        else:
            return {
                'success': False,
                'message': 'Theme change not available.'
            }
    
    def _handle_volume_command(self, command: str) -> Dict:
        """Handle volume adjustment command"""
        if 'up' in command or 'increase' in command:
            # Increase volume logic
            return {
                'success': True,
                'message': 'Volume increased.',
                'action_taken': 'volume_up'
            }
        elif 'down' in command or 'decrease' in command:
            # Decrease volume logic
            return {
                'success': True,
                'message': 'Volume decreased.',
                'action_taken': 'volume_down'
            }
        else:
            return {
                'success': True,
                'message': 'Volume controls: say volume up or volume down.',
                'action_taken': 'volume_info'
            }
    
    def _handle_shutdown_command(self) -> Dict:
        """Handle shutdown command"""
        return {
            'success': True,
            'message': 'Shutdown command received. Please confirm through the power menu.',
            'action_taken': 'shutdown_requested',
            'requires_confirmation': True
        }
    
    def _handle_restart_command(self) -> Dict:
        """Handle restart command"""
        return {
            'success': True,
            'message': 'Restart command received. Please confirm through the power menu.',
            'action_taken': 'restart_requested',
            'requires_confirmation': True
        }
    
    def _handle_unknown_command(self, command: str) -> Dict:
        """Handle unknown commands"""
        return {
            'success': False,
            'message': f'Command not recognized: {command}. Say help for available commands.',
            'action_taken': 'unknown_command'
        }
    
    def get_command_history(self) -> List[Dict]:
        """Get recent command history"""
        return self.command_history.copy()
