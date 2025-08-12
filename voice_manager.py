"""
Enhanced Voice System Integration for ULTRON Agent 3.0
Fixes all threading and API issues with proper fallback mechanisms
"""

from asyncio import run as asyncio_run, run_coroutine_threadsafe
from logging import getLogger, info, error, warning
from os import name as os_name, unlink
from threading import Thread
from time import sleep
from queue import Queue, Empty, Full
from tempfile import NamedTemporaryFile
from subprocess import run as subprocess_run, DEVNULL
from sys import platform
from pathlib import Path

# Import original voice module
try:
    from voice import VoiceSystem as OriginalVoiceSystem
except ImportError:
    OriginalVoiceSystem = None

# Import enhanced voice engine
try:
    from voice_enhanced import UltronVoiceEngine, speak as enhanced_speak
except ImportError:
    UltronVoiceEngine = None
    enhanced_speak = None

# TTS Engines
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logger = getLogger(__name__)

class UltronVoiceManager:
    """Unified voice manager that handles all voice operations for ULTRON"""
    
    def __init__(self, config=None):
        self.config = config
        self.voice_engines = {}
        self.active_engine = None
        self.fallback_chain = ['enhanced', 'pyttsx3', 'openai', 'console']
        
        # Voice settings
        self.rate = 180
        self.volume = 0.9
        self.voice_id = None
        
        # Threading
        self.voice_queue = Queue()
        self.is_running = False
        self.worker_thread = None
        
        # Initialize engines
        self._initialize_engines()
        
    def _initialize_engines(self):
        """Initialize all available voice engines"""
        info("Initializing ULTRON voice engines...")
        
        # Enhanced Engine (Process-based pyttsx3)
        if UltronVoiceEngine:
            try:
                self.voice_engines['enhanced'] = UltronVoiceEngine()
                info("Enhanced voice engine initialized")
            except Exception as e:
                from security_utils import sanitize_log_input
                error(f"Enhanced voice engine failed: {sanitize_log_input(str(e))}")
        
        # Direct pyttsx3
        if PYTTSX3_AVAILABLE:
            try:
                engine = pyttsx3.init()
                voices = engine.getProperty('voices')
                if voices:
                    engine.setProperty('voice', voices[0].id)
                engine.setProperty('rate', self.rate)
                engine.setProperty('volume', self.volume)
                self.voice_engines['pyttsx3'] = engine
                info("Direct pyttsx3 engine initialized")
            except Exception as e:
                from security_utils import sanitize_log_input
                error(f"Direct pyttsx3 failed: {sanitize_log_input(str(e))}")
        
        # OpenAI TTS
        if OPENAI_AVAILABLE and self.config:
            try:
                api_key = self.config.data.get('openai_api_key')
                if api_key:
                    self.voice_engines['openai'] = {'api_key': api_key}
                    info("OpenAI TTS engine initialized")
            except Exception as e:
                from security_utils import sanitize_log_input
                error(f"OpenAI TTS failed: {sanitize_log_input(str(e))}")
        
        # Console fallback
        self.voice_engines['console'] = True
        
        # Set active engine
        for engine_name in self.fallback_chain:
            if engine_name in self.voice_engines:
                self.active_engine = engine_name
                info(f"Active voice engine: {engine_name}")
                break
    
    def speak(self, text, async_mode=True):
        """Main speak function with comprehensive fallback"""
        if not text or not text.strip():
            return
        
        from security_utils import sanitize_log_input
        info(f"[ULTRON VOICE] Speaking: {sanitize_log_input(text[:50])}...")
        
        if async_mode:
            self._speak_async(text)
        else:
            return self._speak_sync(text)
    
    def _speak_async(self, text):
        """Async voice output"""
        if not self.is_running:
            self._start_voice_worker()
        
        try:
            self.voice_queue.put(text, block=False)
        except Full:
            warning("Voice queue full, skipping")
    
    def _speak_sync(self, text):
        """Synchronous voice output with fallback chain"""
        for engine_name in self.fallback_chain:
            try:
                if engine_name not in self.voice_engines:
                    continue
                
                success = self._try_engine(engine_name, text)
                if success:
                    info(f"[ULTRON VOICE] Success with {engine_name}")
                    return True
                    
            except Exception as e:
                from security_utils import sanitize_log_input
                warning(f"Engine {engine_name} failed: {sanitize_log_input(str(e))}")
                continue
        
        error("All voice engines failed")
        return False
    
    def _try_engine(self, engine_name, text):
        """Try specific engine"""
        try:
            if engine_name == 'enhanced' and 'enhanced' in self.voice_engines:
                return self.voice_engines['enhanced'].speak_sync(text)
            
            elif engine_name == 'pyttsx3' and 'pyttsx3' in self.voice_engines:
                engine = self.voice_engines['pyttsx3']
                engine.say(text)
                engine.runAndWait()
                return True
            
            elif engine_name == 'openai' and 'openai' in self.voice_engines:
                return self._speak_openai(text)
            
            elif engine_name == 'console':
                print(f"[ULTRON VOICE]: {text}")
                return True
                
        except Exception as e:
            from security_utils import sanitize_log_input
            error(f"Engine {engine_name} error: {sanitize_log_input(str(e))}")
            return False
        
        return False
    
    def _speak_openai(self, text):
        """OpenAI TTS implementation"""
        try:
            import openai
            
            api_key = self.voice_engines['openai']['api_key']
            client = openai.OpenAI(api_key=api_key)
            
            response = client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text
            )
            
            # Save and play audio
            with NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                f.write(response.content)
                audio_file = f.name
            
            try:
                # Play audio file
                if os_name == 'nt':
                    import winsound
                    winsound.PlaySound(audio_file, winsound.SND_FILENAME)
                else:
                    subprocess_run(['mpg123', audio_file], check=True, stdout=DEVNULL, stderr=DEVNULL)
                
                return True
            finally:
                try:
                    unlink(audio_file)
                except OSError:
                    pass
                    
        except Exception as e:
            from security_utils import sanitize_log_input
            error(f"OpenAI TTS error: {sanitize_log_input(str(e))}")
            return False
    
    def _start_voice_worker(self):
        """Start voice worker thread"""
        if not self.is_running:
            self.is_running = True
            self.worker_thread = Thread(target=self._voice_worker, daemon=True)
            self.worker_thread.start()
    
    def _voice_worker(self):
        """Voice worker thread"""
        while self.is_running:
            try:
                text = self.voice_queue.get(timeout=1.0)
                if text is None:
                    break
                self._speak_sync(text)
            except Empty:
                continue
            except Exception as e:
                from security_utils import sanitize_log_input
                error(f"Voice worker error: {sanitize_log_input(str(e))}")
    
    def test_voice(self):
        """Test voice system"""
        test_messages = [
            "ULTRON voice system test initiated.",
            "Neural networks are operational.",
            "Voice test complete."
        ]
        
        for msg in test_messages:
            if self._speak_sync(msg):
                info("Voice test successful!")
                return True
            sleep(0.5)
        
        error("Voice test failed!")
        return False
    
    def shutdown(self):
        """Shutdown voice system"""
        self.is_running = False
        if self.voice_queue:
            self.voice_queue.put(None)
        
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2.0)
        
        # Shutdown engines
        for engine_name, engine in self.voice_engines.items():
            try:
                if engine_name == 'enhanced' and hasattr(engine, 'shutdown'):
                    engine.shutdown()
                elif engine_name == 'pyttsx3' and hasattr(engine, 'stop'):
                    engine.stop()
            except:
                pass
        
        info("Voice system shutdown complete")

# Global voice manager
_voice_manager = None

def get_voice_manager(config=None):
    """Get global voice manager"""
    global _voice_manager
    if _voice_manager is None:
        _voice_manager = UltronVoiceManager(config)
    return _voice_manager

def speak(text, async_mode=True):
    """Global speak function"""
    manager = get_voice_manager()
    return manager.speak(text, async_mode)

def test_voice_system(config=None):
    """Test voice system"""
    manager = get_voice_manager(config)
    return manager.test_voice()

if __name__ == "__main__":
    # Test the system
    print("Testing ULTRON Voice Manager...")
    test_voice_system()
