"""
Voice Manager for ULTRON Agent
Provides unified voice interface with multiple TTS engines
"""

import logging
import threading
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class UltronVoiceManager:
    """Voice manager with multiple TTS engine support"""

    def __init__(self, config=None):
        """Initialize voice manager with configuration"""
        self.config = config
        self.engines = {}
        self.executor = ThreadPoolExecutor(max_workers=2)
        self._initialize_engines()

    def _initialize_engines(self):
        """Initialize available TTS engines"""
        try:
            import pyttsx3
            self.engines['pyttsx3'] = pyttsx3.init()
            logger.info("pyttsx3 engine initialized")
        except Exception as e:
            logger.error(f"Failed to initialize pyttsx3: {e}")

        # Add other engines as needed
        self.engines['enhanced'] = None  # Placeholder for enhanced engine

    def speak(self, text: str, async_mode: bool = False):
        """Speak text using available engines"""
        if async_mode:
            self._speak_async(text)
        else:
            self._speak_sync(text)

    def _speak_async(self, text: str):
        """Speak asynchronously"""
        self.executor.submit(self._speak_sync, text)

    def _speak_sync(self, text: str):
        """Speak synchronously with fallback"""
        engines_to_try = ['pyttsx3', 'enhanced']

        for engine_name in engines_to_try:
            if self._try_engine(engine_name, text):
                return True

        logger.error("All TTS engines failed")
        return False

    def _try_engine(self, engine_name: str, text: str) -> bool:
        """Try to speak using specific engine"""
        if engine_name not in self.engines:
            return False

        engine = self.engines[engine_name]
        if engine is None:
            return False

        try:
            if engine_name == 'pyttsx3':
                engine.say(text)
                engine.runAndWait()
                return True
            # Add other engine implementations here
        except Exception as e:
            logger.error(f"Engine {engine_name} failed: {e}")
            return False

        return False
