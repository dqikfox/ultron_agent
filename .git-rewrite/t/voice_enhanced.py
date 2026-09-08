"""
Enhanced Voice System for ULTRON Agent 3.0
Fixes threading issues with pyttsx3 and provides robust voice capabilities
"""

import pyttsx3
import threading
import queue
import time
import logging
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
import subprocess
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UltronVoiceEngine:
    """Enhanced thread-safe voice engine for ULTRON"""
    
    def __init__(self):
        self.voice_queue = queue.Queue()
        self.is_running = False
        self.worker_thread = None
        self.current_engine = None
        self.voice_lock = threading.Lock()
        self.engine_ready = threading.Event()
        
        # Voice settings
        self.rate = 180
        self.volume = 0.9
        self.voice_id = None
        
        # Process-based backup
        self.use_process_fallback = False
        
        # Initialize voice engine
        self._initialize_engine()
        
    def _initialize_engine(self):
        """Initialize pyttsx3 engine in a separate thread"""
        try:
            # Create engine in main thread first
            self.current_engine = pyttsx3.init()
            
            # Configure voice settings
            voices = self.current_engine.getProperty('voices')
            if voices:
                # Try to find a good voice
                for voice in voices:
                    if 'english' in voice.name.lower() or 'david' in voice.name.lower():
                        self.voice_id = voice.id
                        break
                if not self.voice_id and voices:
                    self.voice_id = voices[0].id
                    
                if self.voice_id:
                    self.current_engine.setProperty('voice', self.voice_id)
            
            self.current_engine.setProperty('rate', self.rate)
            self.current_engine.setProperty('volume', self.volume)
            
            logger.info("Voice engine initialized successfully")
            self.engine_ready.set()
            
        except Exception as e:
            logger.error(f"Failed to initialize voice engine: {e}")
            self.use_process_fallback = True
            self.engine_ready.set()
    
    def start_voice_worker(self):
        """Start the voice worker thread"""
        if not self.is_running:
            self.is_running = True
            self.worker_thread = threading.Thread(target=self._voice_worker, daemon=True)
            self.worker_thread.start()
            logger.info("Voice worker thread started")
    
    def _voice_worker(self):
        """Voice worker thread - processes voice requests"""
        while self.is_running:
            try:
                # Get text from queue with timeout
                text = self.voice_queue.get(timeout=1.0)
                if text is None:  # Shutdown signal
                    break
                
                # Process voice output
                self._speak_text(text)
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Voice worker error: {e}")
                time.sleep(0.1)
    
    def _speak_text(self, text):
        """Speak text using the most reliable method available"""
        try:
            # Method 1: Direct pyttsx3 (if no threading conflicts)
            if not self.use_process_fallback and self.current_engine:
                with self.voice_lock:
                    try:
                        self.current_engine.say(text)
                        self.current_engine.runAndWait()
                        logger.info(f"[ULTRON VOICE] Successfully spoke: {text[:50]}...")
                        return True
                    except Exception as e:
                        logger.warning(f"Direct pyttsx3 failed: {e}")
                        self.use_process_fallback = True
            
            # Method 2: Process-based fallback
            if self.use_process_fallback:
                return self._speak_via_process(text)
                
        except Exception as e:
            logger.error(f"All voice methods failed: {e}")
            return False
    
    def _speak_via_process(self, text):
        """Speak using a separate process to avoid threading conflicts"""
        try:
            # Create a temporary Python script for voice output
            script_content = f'''
import pyttsx3
import sys

try:
    engine = pyttsx3.init()
    engine.setProperty('rate', {self.rate})
    engine.setProperty('volume', {self.volume})
    
    voices = engine.getProperty('voices')
    if voices and len(voices) > 0:
        engine.setProperty('voice', voices[0].id)
    
    text = """{text}"""
    engine.say(text)
    engine.runAndWait()
    print("Voice output completed successfully")
except Exception as e:
    print(f"Voice error: {{e}}")
    sys.exit(1)
'''
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(script_content)
                temp_script = f.name
            
            try:
                # Run the script in a separate process
                result = subprocess.run(
                    [sys.executable, temp_script],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd=os.path.dirname(__file__)
                )
                
                if result.returncode == 0:
                    logger.info(f"[ULTRON PROCESS VOICE] Successfully spoke: {text[:50]}...")
                    return True
                else:
                    logger.error(f"Process voice failed: {result.stderr}")
                    return False
                    
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_script)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Process voice method failed: {e}")
            return False
    
    def speak_async(self, text):
        """Add text to voice queue for async processing"""
        if not text or not text.strip():
            return
            
        # Ensure voice worker is running
        if not self.is_running:
            self.start_voice_worker()
        
        # Wait for engine to be ready
        self.engine_ready.wait(timeout=5.0)
        
        try:
            # Add to queue (non-blocking)
            self.voice_queue.put(text, block=False)
            logger.info(f"[ULTRON VOICE QUEUE] Added to queue: {text[:50]}...")
        except queue.Full:
            logger.warning("Voice queue is full, skipping voice output")
    
    def speak_sync(self, text):
        """Speak text synchronously"""
        if not text or not text.strip():
            return
            
        logger.info(f"[ULTRON SYNC VOICE] Speaking: {text[:50]}...")
        return self._speak_text(text)
    
    def test_voice(self):
        """Test voice functionality"""
        test_phrases = [
            "ULTRON neural networks are online and operational.",
            "Voice system test successful.",
            "All systems ready for deployment."
        ]
        
        for phrase in test_phrases:
            logger.info(f"Testing voice with: {phrase}")
            if self.speak_sync(phrase):
                logger.info("Voice test successful!")
                return True
            time.sleep(1)
        
        logger.error("All voice tests failed")
        return False
    
    def shutdown(self):
        """Shutdown voice engine"""
        self.is_running = False
        if self.voice_queue:
            self.voice_queue.put(None)  # Shutdown signal
        
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2.0)
        
        if self.current_engine:
            try:
                self.current_engine.stop()
            except:
                pass
        
        logger.info("Voice engine shutdown complete")

# Global voice engine instance
_voice_engine = None

def get_voice_engine():
    """Get the global voice engine instance"""
    global _voice_engine
    if _voice_engine is None:
        _voice_engine = UltronVoiceEngine()
    return _voice_engine

def speak(text, async_mode=True):
    """Main speak function with improved reliability"""
    if not text or not text.strip():
        return
    
    engine = get_voice_engine()
    
    try:
        if async_mode:
            engine.speak_async(text)
        else:
            return engine.speak_sync(text)
    except Exception as e:
        logger.error(f"Voice speak error: {e}")
        # Fallback to console output
        print(f"[ULTRON VOICE FALLBACK]: {text}")

def test_voice_system():
    """Test the voice system"""
    print("Testing enhanced ULTRON voice system...")
    engine = get_voice_engine()
    return engine.test_voice()

if __name__ == "__main__":
    # Test the voice system
    import sys
    test_voice_system()
