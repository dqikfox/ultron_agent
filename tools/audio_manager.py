import pygame
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
            pygame.mixer.quit()
            devices = []
            for i in range(pygame.mixer.get_num_devices()):
                devices.append(pygame.mixer.get_device_info(i))
            return devices
        except Exception as e:
            logging.error(f"Failed to list audio devices: {e}")
            return []
        finally:
            self._init_pygame()  # Reinitialize mixer

    def set_audio_device(self, device_index: int) -> bool:
        """Set the audio output device."""
        try:
            pygame.mixer.quit()
            pygame.mixer.init(devicename=str(device_index))
            self.audio_device = device_index
            return True
        except Exception as e:
            logging.error(f"Failed to set audio device {device_index}: {e}")
            self._init_pygame()  # Fallback to default device
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
            
            buffer = pygame.sndarray.make_sound(
                numpy.sin(2 * numpy.pi * numpy.arange(num_samples) * frequency / sample_rate)
                .astype(numpy.float32)
            )
            
            buffer.play()
            pygame.time.wait(int(duration * 1000))
            return True
            
        except Exception as e:
            logging.error(f"Audio test failed: {e}")
            return False
