"""
Voice Manager for ULTRON Agent
Provides unified voice interface with multiple TTS engines
"""

import logging
import threading
import os
from typing import Dict
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class UltronVoiceManager:

        def self_test(self) -> dict:
            """
            Run diagnostics on all available TTS engines and basic speak functionality.
            Returns a dict with status and per-engine results.
            """
            results = {"status": "ok", "engines": {}, "errors": []}
            available = self.get_available_engines()
            if not available:
                results["status"] = "fail"
                results["errors"].append("No TTS engines available")
                return results
            for engine in available:
                try:
                    ok = self.test_engine(engine)
                    results["engines"][engine] = "ok" if ok else "fail"
                    if not ok:
                        results["status"] = "fail"
                        results["errors"].append(f"Engine {engine} failed test")
                except Exception as e:
                    results["engines"][engine] = f"error: {e}"
                    results["status"] = "fail"
                    results["errors"].append(f"Engine {engine} error: {e}")
            # Optionally, test basic speak (mute or short text)
            try:
                self.speak("Test.", async_mode=False, engine=available[0])
            except Exception as e:
                results["status"] = "fail"
                results["errors"].append(f"Basic speak failed: {e}")
            return results
    """Voice manager with multiple TTS engine support"""

    def __init__(self, config=None, ultron_config=None):
        """Initialize voice manager with configuration"""
        self.config = config
        self.ultron_config = ultron_config
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

        # Initialize ElevenLabs if API key is available
        self._initialize_elevenlabs()

        # Add other engines as needed
        self.engines['enhanced'] = None  # Placeholder for enhanced engine

    def _initialize_elevenlabs(self):
        """Initialize ElevenLabs TTS engine"""
        try:
            # Get ElevenLabs API key from centralized config or environment
            elevenlabs_key = None
            elevenlabs_agent_id = None

            if self.ultron_config:
                elevenlabs_key = self.ultron_config.get_api_key("elevenlabs")
                elevenlabs_agent_id = self.ultron_config.get_api_key(
                    "elevenlabs_agent_id")

            if not elevenlabs_key:
                elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
                elevenlabs_agent_id = os.getenv("ELEVENLABS_AGENT_ID")

            if elevenlabs_key:
                # Import ElevenLabs client
                try:
                    from elevenlabs import ElevenLabs
                    self.engines['elevenlabs'] = {
                        'client': ElevenLabs(api_key=elevenlabs_key),
                        'agent_id': elevenlabs_agent_id
                    }
                    logger.info("ElevenLabs engine initialized")
                except ImportError:
                    logger.warning("ElevenLabs package not installed")
                except Exception as e:
                    logger.error(f"Failed to initialize ElevenLabs: {e}")
            else:
                logger.info("ElevenLabs API key not available")

        except Exception as e:
            logger.error(f"Error initializing ElevenLabs: {e}")

    def speak(self, text: str, async_mode: bool = False, engine: str = None):
        """Speak text using available engines"""
        if async_mode:
            self._speak_async(text, engine)
        else:
            self._speak_sync(text, engine)

    def _speak_async(self, text: str, engine: str = None):
        """Speak asynchronously"""
        self.executor.submit(self._speak_sync, text, engine)

    def _speak_sync(self, text: str, engine: str = None):
        """Speak synchronously with fallback"""
        engines_to_try = []

        # If specific engine requested, try it first
        if engine and engine in self.engines:
            engines_to_try.append(engine)

        # Default priority: ElevenLabs -> pyttsx3 -> enhanced
        default_priority = ['elevenlabs', 'pyttsx3', 'enhanced']
        for eng in default_priority:
            if eng not in engines_to_try:
                engines_to_try.append(eng)

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
            elif engine_name == 'elevenlabs':
                return self._speak_elevenlabs(text, engine)
            # Add other engine implementations here
        except Exception as e:
            logger.error(f"Engine {engine_name} failed: {e}")
            return False

        return False

    def _speak_elevenlabs(self, text: str, engine_config: Dict) -> bool:
        """Speak using ElevenLabs TTS"""
        try:
            client = engine_config['client']
            agent_id = engine_config.get('agent_id')

            if agent_id:
                # Use conversational AI agent
                client.generate(
                    text=text,
                    voice="Agent",  # Use agent voice
                    model="eleven_monolingual_v1"
                )
            else:
                # Use standard TTS
                client.generate(
                    text=text,
                    voice="Adam",  # Default voice
                    model="eleven_monolingual_v1"
                )

            # Play the audio (this is a simplified implementation)
            # In a real implementation, you'd save to file and play
            logger.info(f"ElevenLabs TTS generated for text: {text[:50]}...")
            return True

        except Exception as e:
            logger.error(f"ElevenLabs TTS failed: {e}")
            return False

    def get_available_engines(self) -> list:
        """Get list of available TTS engines"""
        return [name for name, engine in self.engines.items()
                if engine is not None]

    def test_engine(self, engine_name: str) -> bool:
        """Test if a specific engine is working"""
        test_text = "Hello, this is a test of the voice system."
        return self._try_engine(engine_name, test_text)
