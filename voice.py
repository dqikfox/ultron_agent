import logging
import speech_recognition as sr
import pyttsx3
import asyncio
from elevenlabs import ElevenLabs
from tools.audio_manager import AudioManager
from pathlib import Path

class VoiceAssistant:
    def stop_voice(self):
        """Release any audio resources (mic, audio, etc)."""
        try:
            if hasattr(self, 'audio_manager') and hasattr(self.audio_manager, 'stop_audio'):
                self.audio_manager.stop_audio()
        except Exception as e:
            logging.error(f"Error releasing voice/audio resources: {e} - voice.py:16")

    def __init__(self, config):
        self.config = config
        self.recognizer = None
        self.tts_engine = None
        self.elevenlabs = None
        self.audio_manager = AudioManager()

        # Initialize ElevenLabs if configured
        if config.data.get("elevenlabs_api_key"):
            try:
                self.elevenlabs = ElevenLabs(api_key=config.data.get("elevenlabs_api_key"))
                logging.info("ElevenLabs TTS initialized. - voice.py:29")
            except Exception as e:
                logging.error(f"ElevenLabs initialization failed: {e} - voice.py:31")

        # Initialize pyttsx3 as fallback (always initialize for reliability)
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)
            self.tts_engine.setProperty('volume', 0.9)
            logging.info("pyttsx3 TTS initialized as fallback. - voice.py:38")
        except Exception as e:
            logging.error(f"pyttsx3 initialization failed: {e} - voice.py:40")

    async def speak(self, text: str) -> None:
        if not text:
            return

        # Try ElevenLabs first (TTS)
        if self.elevenlabs:
            try:
                agent_id = self.config.data.get("elevenlabs_agent_id")
                audio = self.elevenlabs.text_to_speech(text, voice_id=agent_id)
                temp_audio = Path("temp_audio.mp3")
                with open(temp_audio, "wb") as f:
                    f.write(audio.read())
                self.audio_manager.play_audio(str(temp_audio))
                temp_audio.unlink(missing_ok=True)
                return
            except Exception as e:
                logging.error(f"ElevenLabs TTS error: {e} - voice.py:58")

        # Fallback to pyttsx3 for direct speech
        if self.tts_engine:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                logging.info(f"Used pyttsx3 direct speech for: {text[:50]}... - voice.py:65")
                return
            except Exception as e:
                logging.error(f"pyttsx3 direct speech error: {e} - voice.py:68")

        # Final fallback - text output
        print(f"[Voice]: {text} - voice.py:71")
        logging.warning(f"Voice output failed, using text fallback: {text[:50]}... - voice.py:72")

    def listen(self, timeout: int = 10, phrase_time_limit: int = 10) -> str:
        """
        Listen for speech and return recognized text.
        Uses ElevenLabs STT if available, otherwise falls back to speech_recognition.
        """
        # Try ElevenLabs STT (if available in your ElevenLabs SDK)
        if self.elevenlabs and hasattr(self.elevenlabs, "speech_to_text"):
            try:
                audio = self.audio_manager.record_audio(timeout=timeout, phrase_time_limit=phrase_time_limit)
                text = self.elevenlabs.speech_to_text(audio)
                logging.info(f"ElevenLabs STT recognized: {text} - voice.py:84")
                return text
            except Exception as e:
                logging.error(f"ElevenLabs STT error: {e}  STT - voice.py:87")

        # Fallback to speech_recognition
        try:
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                logging.info("Listening for speech (fallback STT)... - voice.py:93")
                audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                text = recognizer.recognize_google(audio)
                logging.info(f"Fallback STT recognized: {text} - voice.py:96")
                return text
        except Exception as e:
            logging.error(f"Fallback STT error: {e}  STT - voice.py:99")
            return ""
```
I've left the original code block unchanged, as it's already complete.
        print(f"[Voice]: {text} - voice.py:103")
        logging.warning(f"Voice output failed, using text fallback: {text[:50]}... - voice.py:104")

