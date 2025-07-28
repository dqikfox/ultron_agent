import logging
import speech_recognition as sr
import pyttsx3
import whisper
import requests
import io
from elevenlabs import ElevenLabs

class VoiceAssistant:
    def __init__(self, config):
        self.config = config
        self.recognizer = None
        self.tts_engine = None
        self.elevenlabs = None
        self.whisper_model = None

        # Initialize speech recognizer
        try:
            self.recognizer = sr.Recognizer() if sr else None
        except Exception as e:
            logging.error(f"SpeechRecognition not available: {e}")

        # Initialize TTS engine
        tts_engine = config.data.get("tts_engine") or config.data.get("voice_engine") or "pyttsx3"
        if tts_engine == "elevenlabs" and config.data.get("elevenlabs_api_key"):
            try:
                self.elevenlabs = ElevenLabs(api_key=config.data.get("elevenlabs_api_key"))
                logging.info("ElevenLabs TTS initialized.")
            except Exception as e:
                logging.error(f"ElevenLabs initialization failed: {e}")
        if not self.elevenlabs and tts_engine == "pyttsx3":
            try:
                self.tts_engine = pyttsx3.init()
                logging.info("pyttsx3 TTS initialized.")
            except Exception as e:
                logging.error(f"pyttsx3 initialization failed: {e}")
        if not self.elevenlabs and not self.tts_engine:
            logging.warning("No TTS engine available. Voice output will be text only.")

        # Initialize Whisper STT
        stt_engine = config.data.get("stt_engine") or "whisper"
        if stt_engine == "whisper":
            try:
                self.whisper_model = whisper.load_model("base")
                logging.info("Whisper STT initialized.")
            except Exception as e:
                logging.error(f"Whisper initialization failed: {e}")
        if not self.whisper_model:
            logging.warning("No STT engine available. Voice input will be disabled.")

    def listen(self, timeout: int = 5) -> str:
        if not self.recognizer:
            return ""
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            logging.info("Listening for voice input...")
            try:
                audio = self.recognizer.listen(source, timeout=timeout)
            except sr.WaitTimeoutError:
                return ""

            # Try Whisper first
            if self.whisper_model:
                try:
                    with open("temp_audio.wav", "wb") as f:
                        f.write(audio.get_wav_data())
                    result = self.whisper_model.transcribe("temp_audio.wav")
                    return result["text"]
                except Exception as e:
                    logging.error(f"Whisper STT error: {e}")

            # Fallback to Google
            try:
                text = self.recognizer.recognize_google(audio)
                logging.info(f"Google STT recognized: {text}")
                return text
            except Exception as e:
                logging.error(f"Google STT error: {e}")
                return ""

    def speak(self, text: str) -> None:
        if not text:
            return
        if self.elevenlabs:
            try:
                agent_id = self.config.data.get("elevenlabs_agent_id")
                audio = self.elevenlabs.text_to_speech(text, voice_id=agent_id)
                with open("temp_audio.mp3", "wb") as f:
                    f.write(audio.read())
                import pygame
                pygame.mixer.init()
                pygame.mixer.music.load("temp_audio.mp3")
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(100)
            except Exception as e:
                logging.error(f"ElevenLabs TTS error: {e}")
        elif self.tts_engine:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                logging.error(f"pyttsx3 TTS error: {e}")
        else:
            print(f"[Voice]: {text}")