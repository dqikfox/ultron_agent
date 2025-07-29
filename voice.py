import logging
import speech_recognition as sr
import pyttsx3
import whisper
import requests
import io
import asyncio
from elevenlabs import ElevenLabs
from tools.openai_tools import OpenAITools
from tools.audio_manager import AudioManager
from pathlib import Path

class VoiceAssistant:
    def __init__(self, config):
        self.config = config
        self.recognizer = None
        self.tts_engine = None
        self.elevenlabs = None
        self.whisper_model = None
        self.openai_tools = None
        self.audio_manager = AudioManager()
        
        # Test audio system
        if self.audio_manager.test_audio():
            logging.info("Audio system test successful")
        else:
            logging.warning("Audio system test failed, attempting to find working device")

        # Initialize speech recognizer
        try:
            self.recognizer = sr.Recognizer() if sr else None
        except Exception as e:
            logging.error(f"SpeechRecognition not available: {e}")

        # Initialize TTS engines based on configuration
        tts_engine = config.data.get("tts_engine") or config.data.get("voice_engine") or "openai"
        
        # Initialize OpenAI tools if API key is available
        if config.data.get("openai_api_key"):
            try:
                self.openai_tools = OpenAITools(config)
                logging.info("OpenAI tools initialized.")
            except Exception as e:
                logging.error(f"OpenAI tools initialization failed: {e}")
        
        # Initialize ElevenLabs if configured
        if tts_engine == "elevenlabs" and config.data.get("elevenlabs_api_key"):
            try:
                self.elevenlabs = ElevenLabs(api_key=config.data.get("elevenlabs_api_key"))
                logging.info("ElevenLabs TTS initialized.")
            except Exception as e:
                logging.error(f"ElevenLabs initialization failed: {e}")
        
        # Initialize pyttsx3 as fallback
        if not self.openai_tools and not self.elevenlabs and tts_engine == "pyttsx3":
            try:
                self.tts_engine = pyttsx3.init()
                logging.info("pyttsx3 TTS initialized.")
            except Exception as e:
                logging.error(f"pyttsx3 initialization failed: {e}")
        
        if not self.openai_tools and not self.elevenlabs and not self.tts_engine:
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

    async def listen(self, timeout: int = 5) -> str:
        if not self.recognizer:
            return ""
            
        temp_path = Path("temp_audio.wav")
        
        # Record audio using AudioManager
        try:
            self.audio_manager.record_audio(str(temp_path), timeout)
            logging.info("Recording completed")
            
            # Create AudioData object from the recorded file
            with sr.AudioFile(str(temp_path)) as source:
                audio = self.recognizer.record(source)
                
            # Try OpenAI Whisper API first
            if self.openai_tools:
                try:
                    text = await self.openai_tools.speech_to_text(str(temp_path))
                    logging.info(f"OpenAI Whisper recognized: {text}")
                    return text
                except Exception as e:
                    logging.error(f"OpenAI Whisper STT error: {e}")

            # Try local Whisper next
            if self.whisper_model:
                try:
                    result = self.whisper_model.transcribe(str(temp_path))
                    return result["text"]
                except Exception as e:
                    logging.error(f"Local Whisper STT error: {e}")

            # Fallback to Google
            try:
                text = self.recognizer.recognize_google(audio)
                logging.info(f"Google STT recognized: {text}")
                return text
            except Exception as e:
                logging.error(f"Google STT error: {e}")
                return ""
        finally:
            # Clean up temp file
            temp_path.unlink(missing_ok=True)

    async def speak(self, text: str) -> None:
        if not text:
            return
        
        temp_path = Path("temp_audio")
        
        # Try OpenAI TTS first
        if self.openai_tools:
            try:
                voice = self.config.data.get("openai_voice", "alloy")
                output_file = await self.openai_tools.text_to_speech(text, voice=voice)
                logging.info(f"Generated speech using OpenAI TTS: {output_file}")
                # Play using audio manager
                self.audio_manager.play_audio(output_file)
                return
            except Exception as e:
                logging.error(f"OpenAI TTS error: {e}")
        
        # Try ElevenLabs next
        if self.elevenlabs:
            try:
                agent_id = self.config.data.get("elevenlabs_agent_id")
                audio = self.elevenlabs.text_to_speech(text, voice_id=agent_id)
                temp_audio = temp_path.with_suffix('.mp3')
                with open(temp_audio, "wb") as f:
                    f.write(audio.read())
                self.audio_manager.play_audio(str(temp_audio))
                temp_audio.unlink(missing_ok=True)
            except Exception as e:
                logging.error(f"ElevenLabs TTS error: {e}")
        elif self.tts_engine:
            try:
                # For pyttsx3, we need to save to a file first
                temp_audio = temp_path.with_suffix('.wav')
                self.tts_engine.save_to_file(text, str(temp_audio))
                self.tts_engine.runAndWait()
                self.audio_manager.play_audio(str(temp_audio))
                temp_audio.unlink(missing_ok=True)
            except Exception as e:
                logging.error(f"pyttsx3 TTS error: {e}")
                print(f"[Voice]: {text}")  # Fallback to text
        else:
            print(f"[Voice]: {text}")