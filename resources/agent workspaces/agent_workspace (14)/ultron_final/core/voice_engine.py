"""Voice recognition and synthesis engine"""
import speech_recognition as sr
import pyttsx3
import logging
import threading
import time

class VoiceEngine:
    def __init__(self, config):
        self.config = config['voice']
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        self.available = False
        self.setup()
    
    def setup(self):
        try:
            # Configure TTS
            voices = self.tts_engine.getProperty('voices')
            if voices:
                self.tts_engine.setProperty('voice', voices[0].id)
            self.tts_engine.setProperty('rate', self.config.get('tts_rate', 150))
            
            # Calibrate microphone
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            self.available = True
            logging.info("Voice engine initialized")
        except Exception as e:
            logging.error(f"Voice engine init failed: {e}")
    
    def listen_for_command(self):
        if not self.available:
            return None
        
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=self.config.get('recognition_timeout', 5))
            
            # Try multiple recognition methods
            for method in [self.recognizer.recognize_google, self.recognizer.recognize_sphinx]:
                try:
                    text = method(audio)
                    logging.info(f"Recognized: {text}")
                    return text.lower()
                except:
                    continue
            
            return None
        except Exception as e:
            logging.error(f"Voice recognition error: {e}")
            return None
    
    def speak(self, text):
        if not self.available:
            return
        
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            logging.error(f"TTS error: {e}")
    
    def is_available(self):
        return self.available
