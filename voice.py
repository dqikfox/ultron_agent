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
    def stop_voice(self):
        """Release any audio resources (mic, audio, etc)."""
        try:
            if hasattr(self, 'audio_manager') and hasattr(self.audio_manager, 'stop_audio'):
                self.audio_manager.stop_audio()
            # If using speech_recognition Microphone, release it (future-proof)
            if hasattr(self, 'recognizer') and hasattr(self.recognizer, 'reset'):  # Not standard, but for custom
                self.recognizer.reset()
        except Exception as e:
            logging.error(f"Error releasing voice/audio resources: {e} - voice.py:23")
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
            logging.info("Audio system test successful - voice.py:35")
        else:
            logging.warning("Audio system test failed, attempting to find working device - voice.py:37")

        # Initialize speech recognizer
        try:
            self.recognizer = sr.Recognizer() if sr else None
        except Exception as e:
            logging.error(f"SpeechRecognition not available: {e} - voice.py:43")

        # Initialize TTS engines based on configuration
        tts_engine = config.data.get("tts_engine") or config.data.get("voice_engine") or "openai"
        
        # Initialize OpenAI tools if API key is available
        if config.data.get("openai_api_key"):
            try:
                self.openai_tools = OpenAITools(config)
                logging.info("OpenAI tools initialized. - voice.py:52")
            except Exception as e:
                logging.error(f"OpenAI tools initialization failed: {e} - voice.py:54")
        
        # Initialize ElevenLabs if configured
        if tts_engine == "elevenlabs" and config.data.get("elevenlabs_api_key"):
            try:
                self.elevenlabs = ElevenLabs(api_key=config.data.get("elevenlabs_api_key"))
                logging.info("ElevenLabs TTS initialized. - voice.py:60")
            except Exception as e:
                logging.error(f"ElevenLabs initialization failed: {e} - voice.py:62")
        
        # Initialize pyttsx3 as fallback (always initialize for reliability)
        try:
            self.tts_engine = pyttsx3.init()
            # Set properties for better performance
            self.tts_engine.setProperty('rate', 150)  # Speed of speech
            self.tts_engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
            logging.info("pyttsx3 TTS initialized as fallback. - voice.py:68")
        except Exception as e:
            logging.error(f"pyttsx3 initialization failed: {e} - voice.py:70")
        
        if not self.openai_tools and not self.elevenlabs and not self.tts_engine:
            logging.warning("No TTS engine available. Voice output will be text only. - voice.py:73")

        # Initialize Whisper STT
        stt_engine = config.data.get("stt_engine") or "whisper"
        if stt_engine == "whisper":
            try:
                self.whisper_model = whisper.load_model("base")
                logging.info("Whisper STT initialized. - voice.py:80")
            except Exception as e:
                logging.error(f"Whisper initialization failed: {e} - voice.py:82")
        if not self.whisper_model:
            logging.warning("No STT engine available. Voice input will be disabled. - voice.py:84")

    async def listen(self, timeout: int = 5) -> str:
        if not self.recognizer:
            return ""

        temp_path = Path("temp_audio.wav")
        audio = None
        try:
            self.audio_manager.record_audio(str(temp_path), timeout)
            logging.info("Recording completed - voice.py:94")

            # Use context manager to ensure file and mic are released
            with sr.AudioFile(str(temp_path)) as source:
                audio = self.recognizer.record(source)

            # Try OpenAI Whisper API first
            if self.openai_tools:
                try:
                    text = await self.openai_tools.speech_to_text(str(temp_path))
                    logging.info(f"OpenAI Whisper recognized: {text} - voice.py:104")
                    return text
                except Exception as e:
                    logging.error(f"OpenAI Whisper STT error: {e} - voice.py:107")

            # Try local Whisper next
            if self.whisper_model:
                try:
                    result = self.whisper_model.transcribe(str(temp_path))
                    return result["text"]
                except Exception as e:
                    logging.error(f"Local Whisper STT error: {e} - voice.py:115")

            # Fallback to Google
            try:
                text = self.recognizer.recognize_google(audio)
                logging.info(f"Google STT recognized: {text} - voice.py:120")
                return text
            except Exception as e:
                logging.error(f"Google STT error: {e} - voice.py:123")
                return ""
        finally:
            # Clean up temp file
            temp_path.unlink(missing_ok=True)
            # Explicitly release any lingering Microphone resources (if any)
            try:
                if hasattr(sr, 'Microphone'):
                    mic = sr.Microphone()
                    if hasattr(mic, '__exit__'):
                        mic.__exit__(None, None, None)
            except Exception as e:
                logging.warning(f"Microphone release workaround failed: {e}  listen:finally - voice.py:135")

    async def speak(self, text: str) -> None:
        if not text:
            return
        
        temp_path = Path("temp_audio")
        
        # Try OpenAI TTS first if API key is available
        if self.openai_tools and self.config.data.get("openai_api_key"):
            try:
                voice = self.config.data.get("openai_voice", "alloy")
                output_file = await self.openai_tools.text_to_speech(text, voice=voice)
                logging.info(f"Generated speech using OpenAI TTS: {output_file} - voice.py:148")
                # Play using audio manager
                self.audio_manager.play_audio(output_file)
                return
            except Exception as e:
                logging.error(f"OpenAI TTS error: {e} - voice.py:153")
        
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
                return
            except Exception as e:
                logging.error(f"ElevenLabs TTS error: {e} - voice.py:166")
        
        # Fallback to pyttsx3 for direct speech
        if self.tts_engine:
            try:
                # Try direct speech first (faster)
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                logging.info(f"Used pyttsx3 direct speech for: {text[:50]}... - voice.py:174")
                return
            except Exception as e:
                logging.error(f"pyttsx3 direct speech error: {e} - voice.py:176")
                
                # Fallback to file-based speech
                try:
                    temp_audio = temp_path.with_suffix('.wav')
                    self.tts_engine.save_to_file(text, str(temp_audio))
                    self.tts_engine.runAndWait()
                    self.audio_manager.play_audio(str(temp_audio))
                    temp_audio.unlink(missing_ok=True)
                    logging.info(f"Used pyttsx3 file-based speech for: {text[:50]}... - voice.py:184")
                    return
                except Exception as e2:
                    logging.error(f"pyttsx3 file-based speech error: {e2} - voice.py:186")
        
        # Final fallback - text output
        print(f"[Voice]: {text} - voice.py:189")
        logging.warning(f"Voice output failed, using text fallback: {text[:50]}... - voice.py:190")