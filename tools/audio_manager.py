import pygame
import numpy
import logging
from pathlib import Path
from typing import Optional

class AudioManager:
    def __init__(self):
        self.initialized = False
        self.audio_device = None
        self._init_pygame()

    def _init_pygame(self) -> None:
        """Initialize pygame audio system with error handling."""
        try:
            pygame.mixer.quit()  # Clean up any existing mixer
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
            self.initialized = True
            logging.info("Pygame audio system initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize pygame audio: {e}")
            self.initialized = False

    def list_audio_devices(self) -> list:
        """List all available audio output devices."""
        try:
            # Simple fallback - pygame doesn't have reliable device enumeration
            return ["Default Audio Device"]
        except Exception as e:
            logging.error(f"Failed to list audio devices: {e}")
            return []

    def set_audio_device(self, device_index: int) -> bool:
        """Set the audio output device."""
        try:
            # pygame doesn't have reliable device selection, use default
            self._init_pygame()
            return True
        except Exception as e:
            logging.error(f"Failed to set audio device {device_index}: {e}")
            return False

    def play_audio(self, file_path: str, block: bool = True) -> bool:
        """Play audio file with proper cleanup."""
        if not self.initialized:
            self._init_pygame()
            if not self.initialized:
                return False

        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()

            if block:
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(100)
            return True

        except Exception as e:
            logging.error(f"Failed to play audio {file_path}: {e}")
            return False
        finally:
            try:
                pygame.mixer.music.unload()
            except:
                pass

    def stop_audio(self) -> None:
        """Stop currently playing audio."""
        if self.initialized:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
            except Exception as e:
                logging.error(f"Failed to stop audio: {e}")

    def test_audio(self) -> bool:
        """Test audio system by playing a simple beep."""
        if not self.initialized:
            self._init_pygame()
            if not self.initialized:
                return False

        try:
            # Generate a test tone
            sample_rate = 44100
            duration = 0.1  # 100ms
            frequency = 440  # A4 note
            num_samples = int(duration * sample_rate)

            # Create a stereo wave (2 channels) to match the mixer settings
            wave = numpy.sin(2 * numpy.pi * numpy.arange(num_samples) * frequency / sample_rate)
            stereo_wave = numpy.array([wave, wave]).T.astype(numpy.float32)

            # Ensure the array is C-contiguous for pygame
            if not stereo_wave.flags['C_CONTIGUOUS']:
                stereo_wave = numpy.ascontiguousarray(stereo_wave)

            buffer = pygame.sndarray.make_sound(stereo_wave)

            buffer.play()
            pygame.time.wait(int(duration * 1000))
            return True

        except Exception as e:
            logging.error(f"Audio test failed: {e}")
            return False

    def record_audio(self, file_path: str, timeout: int = 5) -> bool:
        """Record audio to file"""
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            with sr.Microphone() as source:
                logging.info(f"Recording audio for {timeout} seconds...")
                r.adjust_for_ambient_noise(source, duration=1)
                audio_data: sr.AudioData = r.listen(source, timeout=timeout, phrase_time_limit=timeout)
                # audio_data is an AudioData object, which has get_wav_data method
                with open(file_path, "wb") as f:
                    f.write(audio_data.get_wav_data())
                return True
        except Exception as e:
            logging.error(f"Audio recording failed: {e}")
            return False

    async def record_audio_to_file(self, timeout: int = 10, phrase_time_limit: int = 10) -> str:
        """Record audio to a temporary file and return the file path"""
        try:
            import speech_recognition as sr
            import tempfile
            import os

            r = sr.Recognizer()

            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name

            with sr.Microphone() as source:
                logging.info(f"Recording audio for up to {timeout} seconds...")
                r.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

                # Save to temporary file
                with open(temp_path, "wb") as f:
                    f.write(audio_data.get_wav_data())

                logging.info(f"Audio recorded to: {temp_path}")
                return temp_path

        except Exception as e:
            logging.error(f"Audio recording to file failed: {e}")
            return ""

    def cleanup_temp_file(self, file_path: str) -> None:
        """Clean up temporary audio file"""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                logging.info(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            logging.error(f"Failed to cleanup temp file {file_path}: {e}")
