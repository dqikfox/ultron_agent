"""
Enhanced Voice Recognition System for Ultron Agent 2

Implements advanced voice recognition optimization techniques including:
- Noise reduction and speech enhancement
- Voice Activity Detection (VAD)
- Dynamic energy threshold adjustment
- Improved speech recognition parameters
- Robust error handling and fallback mechanisms

Based on the Ultron AI Developer's Guide best practices.
"""

import logging
import numpy as np
import speech_recognition as sr
import threading
import queue
import time
from typing import Optional, Callable, Tuple
import os
import sys

# Optional dependencies - will gracefully degrade if not available
try:
    import noisereduce as nr
    HAS_NOISEREDUCE = True
except ImportError:
    HAS_NOISEREDUCE = False
    logging.warning("noisereduce not available  noise reduction disabled - enhanced_voice_recognition.py:30")

try:
    import webrtcvad
    HAS_WEBRTCVAD = True
except ImportError:
    HAS_WEBRTCVAD = False
    logging.warning("webrtcvad not available  VAD disabled - enhanced_voice_recognition.py:37")

try:
    import pyaudio
    HAS_PYAUDIO = True
except ImportError:
    HAS_PYAUDIO = False
    logging.warning("pyaudio not available  advanced audio features disabled - enhanced_voice_recognition.py:44")


class EnhancedVoiceRecognition:
    """
    Enhanced voice recognition with noise reduction, VAD, and dynamic thresholds.
    """

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.recognizer = sr.Recognizer()

        # Enhanced parameters from the guide
        self.energy_threshold = self.config.get('energy_threshold', 4000)
        self.dynamic_energy_threshold = self.config.get('dynamic_energy_threshold', True)
        self.pause_threshold = self.config.get('pause_threshold', 0.5)  # Reduced from default 0.8
        self.non_speaking_duration = self.config.get('non_speaking_duration', 0.3)

        # Configure recognizer
        self.recognizer.energy_threshold = self.energy_threshold
        self.recognizer.dynamic_energy_threshold = self.dynamic_energy_threshold
        self.recognizer.pause_threshold = self.pause_threshold
        self.recognizer.non_speaking_duration = self.non_speaking_duration

        # VAD setup
        self.vad = None
        if HAS_WEBRTCVAD:
            self.vad = webrtcvad.Vad(1)  # Aggressiveness level 0-3

        # Audio processing
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.listen_thread = None

        # Performance tracking
        self.performance_stats = {
            'total_listen_calls': 0,
            'successful_recognitions': 0,
            'failed_recognitions': 0,
            'average_processing_time': 0.0,
            'last_noise_sample_time': 0
        }

        logging.info("Enhanced Voice Recognition initialized - enhanced_voice_recognition.py:89")

    def _apply_noise_reduction(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """
        Apply noise reduction using spectral subtraction.
        """
        if not HAS_NOISEREDUCE or audio_data is None:
            return audio_data

        try:
            # Apply noise reduction
            reduced_noise = nr.reduce_noise(
                y=audio_data,
                sr=sample_rate,
                stationary=True,
                prop_decrease=0.75
            )
            return reduced_noise
        except Exception as e:
            logging.warning(f"Noise reduction failed: {e} - enhanced_voice_recognition.py:108")
            return audio_data

    def _detect_voice_activity(self, audio_chunk: bytes) -> bool:
        """
        Detect voice activity using WebRTC VAD.
        """
        if not HAS_WEBRTCVAD or self.vad is None:
            return True  # Assume voice if VAD not available

        try:
            # Convert to 16-bit PCM if needed
            if len(audio_chunk) % 2 != 0:
                audio_chunk = audio_chunk[:-1]

            return self.vad.is_speech(audio_chunk, self.sample_rate)
        except Exception as e:
            logging.warning(f"VAD detection failed: {e} - enhanced_voice_recognition.py:125")
            return True

    def _calibrate_microphone(self, source: sr.Microphone, duration: float = 5.0):
        """
        Calibrate microphone with ambient noise adjustment.
        """
        try:
            logging.info(f"Calibrating microphone for {duration} seconds... - enhanced_voice_recognition.py:133")
            self.recognizer.adjust_for_ambient_noise(source, duration=duration)
            logging.info(f"Calibration complete. Energy threshold: {self.recognizer.energy_threshold} - enhanced_voice_recognition.py:135")
        except Exception as e:
            logging.error(f"Microphone calibration failed: {e} - enhanced_voice_recognition.py:137")

    def _process_audio_chunk(self, audio_chunk: bytes) -> Optional[str]:
        """
        Process a single audio chunk for speech recognition.
        """
        try:
            # Convert to AudioData
            audio_data = sr.AudioData(audio_chunk, self.sample_rate, 2)

            # Apply noise reduction if available
            if HAS_NOISEREDUCE:
                # Convert to numpy array for processing
                raw_data = np.frombuffer(audio_data.get_raw_data(), dtype=np.int16)
                float_data = raw_data.astype(np.float32) / 32768.0

                # Apply noise reduction
                cleaned_data = self._apply_noise_reduction(float_data, self.sample_rate)

                # Convert back to AudioData
                int_data = (cleaned_data * 32768.0).astype(np.int16)
                audio_data = sr.AudioData(int_data.tobytes(), self.sample_rate, 2)

            # Perform recognition
            text = self.recognizer.recognize_google(audio_data)

            if text and text.strip():
                self.performance_stats['successful_recognitions'] += 1
                return text.strip()

        except sr.UnknownValueError:
            # No speech detected
            pass
        except sr.RequestError as e:
            logging.error(f"Speech recognition service error: {e} - enhanced_voice_recognition.py:171")
            self.performance_stats['failed_recognitions'] += 1
        except Exception as e:
            logging.error(f"Audio processing error: {e} - enhanced_voice_recognition.py:174")
            self.performance_stats['failed_recognitions'] += 1

        return None

    def listen_once(self, timeout: float = 10.0, phrase_time_limit: float = 10.0) -> Optional[str]:
        """
        Listen for a single phrase with enhanced processing.
        """
        start_time = time.time()
        self.performance_stats['total_listen_calls'] += 1

        try:
            with sr.Microphone(sample_rate=self.sample_rate, chunk_size=self.chunk_size) as source:
                # Calibrate if it's been more than 5 minutes since last calibration
                current_time = time.time()
                if current_time - self.performance_stats['last_noise_sample_time'] > 300:
                    self._calibrate_microphone(source, duration=2.0)
                    self.performance_stats['last_noise_sample_time'] = current_time

                logging.info("Listening for speech... - enhanced_voice_recognition.py:194")

                # Listen with timeout
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

                # Process the audio
                text = self._process_audio_chunk(audio.get_raw_data())

                # Update performance stats
                processing_time = time.time() - start_time
                self.performance_stats['average_processing_time'] = (
                    (self.performance_stats['average_processing_time'] *
                     (self.performance_stats['total_listen_calls'] - 1) +
                     processing_time) / self.performance_stats['total_listen_calls']
                )

                return text

        except sr.WaitTimeoutError:
            logging.info("Listening timeout  no speech detected - enhanced_voice_recognition.py:213")
        except sr.UnknownValueError:
            logging.info("Speech detected but not understood - enhanced_voice_recognition.py:215")
        except Exception as e:
            logging.error(f"Listening error: {e} - enhanced_voice_recognition.py:217")

        return None

    def listen_continuous(self, callback: Callable[[str], None],
                         timeout: float = 10.0, phrase_time_limit: float = 10.0):
        """
        Continuously listen for speech with callback on recognition.
        """
        self.is_listening = True

        def _listen_loop():
            while self.is_listening:
                try:
                    text = self.listen_once(timeout, phrase_time_limit)
                    if text and callback:
                        callback(text)
                except Exception as e:
                    logging.error(f"Continuous listening error: {e} - enhanced_voice_recognition.py:235")
                    time.sleep(1)  # Brief pause before retrying

        self.listen_thread = threading.Thread(target=_listen_loop, daemon=True)
        self.listen_thread.start()
        logging.info("Continuous listening started - enhanced_voice_recognition.py:240")

    def stop_listening(self):
        """
        Stop continuous listening.
        """
        self.is_listening = False
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=2.0)
        logging.info("Continuous listening stopped - enhanced_voice_recognition.py:249")

    def get_performance_stats(self) -> dict:
        """
        Get current performance statistics.
        """
        stats = self.performance_stats.copy()
        stats['success_rate'] = (
            stats['successful_recognitions'] / max(stats['total_listen_calls'], 1) * 100
        )
        return stats

    def reset_performance_stats(self):
        """
        Reset performance statistics.
        """
        self.performance_stats = {
            'total_listen_calls': 0,
            'successful_recognitions': 0,
            'failed_recognitions': 0,
            'average_processing_time': 0.0,
            'last_noise_sample_time': 0
        }


class VoiceRecognitionManager:
    """
    Manager class for enhanced voice recognition with fallback mechanisms.
    """

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.enhanced_recognizer = EnhancedVoiceRecognition(self.config)
        self.fallback_recognizer = sr.Recognizer()  # Basic fallback

        # Configure fallback
        self.fallback_recognizer.energy_threshold = 3000
        self.fallback_recognizer.dynamic_energy_threshold = True

    def listen_for_command(self, timeout: float = 10.0) -> Optional[str]:
        """
        Listen for a voice command with fallback support.
        """
        # Try enhanced recognition first
        text = self.enhanced_recognizer.listen_once(timeout=timeout)

        if text:
            return text

        # Fallback to basic recognition
        logging.info("Enhanced recognition failed, trying fallback... - enhanced_voice_recognition.py:299")
        try:
            with sr.Microphone() as source:
                self.fallback_recognizer.adjust_for_ambient_noise(source, duration=1.0)
                audio = self.fallback_recognizer.listen(source, timeout=timeout)

                return self.fallback_recognizer.recognize_google(audio).strip()

        except Exception as e:
            logging.error(f"Fallback recognition also failed: {e} - enhanced_voice_recognition.py:308")
            return None

    def start_continuous_listening(self, callback: Callable[[str], None]):
        """
        Start continuous listening with enhanced features.
        """
        self.enhanced_recognizer.listen_continuous(callback)

    def stop_continuous_listening(self):
        """
        Stop continuous listening.
        """
        self.enhanced_recognizer.stop_listening()

    def get_stats(self) -> dict:
        """
        Get performance statistics.
        """
        return self.enhanced_recognizer.get_performance_stats()


# Convenience functions for easy integration
def create_voice_recognizer(config: Optional[dict] = None) -> VoiceRecognitionManager:
    """
    Create a voice recognition manager instance.
    """
    return VoiceRecognitionManager(config)


def quick_listen(timeout: float = 5.0) -> Optional[str]:
    """
    Quick utility function for simple voice recognition.
    """
    recognizer = create_voice_recognizer()
    return recognizer.listen_for_command(timeout)


if __name__ == "__main__":
    # Test the enhanced voice recognition
    logging.basicConfig(level=logging.INFO)

    print("Testing Enhanced Voice Recognition... - enhanced_voice_recognition.py:350")
    print("Speak a command (you have 5 seconds)... - enhanced_voice_recognition.py:351")

    recognizer = create_voice_recognizer()
    text = recognizer.listen_for_command(timeout=5.0)

    if text:
        print(f"Recognized: '{text}' - enhanced_voice_recognition.py:357")
    else:
        print("No speech detected or recognition failed - enhanced_voice_recognition.py:359")

    # Show performance stats
    stats = recognizer.get_stats()
    print(f"Performance Stats: {stats} - enhanced_voice_recognition.py:363")
