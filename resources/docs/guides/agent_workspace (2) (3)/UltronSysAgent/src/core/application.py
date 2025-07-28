"""
UltronSysAgent Core Application
Orchestrates all modules and manages the main event loop
"""

import asyncio
import logging
import signal
import threading
from typing import Dict, Any, Optional

from .config import ConfigManager
from .event_bus import EventBus
from ..modules.voice_engine.voice_engine import VoiceEngine
from ..modules.ai_brain.ai_brain import AIBrain
from ..modules.system_automation.system_automation import SystemAutomation
from ..modules.file_manager.file_manager import FileManager
from ..modules.vision_system.vision_system import VisionSystem
from ..modules.scheduler.scheduler import Scheduler
from ..modules.memory_manager.memory_manager import MemoryManager
from ..gui.main_window import MainWindow

class UltronSysAgent:
    """Main application class for UltronSysAgent"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.modules: Dict[str, Any] = {}
        
        # Event bus for inter-module communication
        self.event_bus = EventBus()
        
        # Initialize modules
        self._initialize_modules()
        
        # Setup signal handlers
        self._setup_signal_handlers()
    
    def _initialize_modules(self):
        """Initialize all system modules"""
        self.logger.info("Initializing UltronSysAgent modules...")
        
        try:
            # Core modules
            self.modules['memory'] = MemoryManager(self.config, self.event_bus)
            self.modules['ai_brain'] = AIBrain(self.config, self.event_bus, self.modules['memory'])
            self.modules['voice'] = VoiceEngine(self.config, self.event_bus)
            self.modules['system'] = SystemAutomation(self.config, self.event_bus)
            self.modules['files'] = FileManager(self.config, self.event_bus)
            self.modules['vision'] = VisionSystem(self.config, self.event_bus)
            self.modules['scheduler'] = Scheduler(self.config, self.event_bus)
            
            # GUI module (runs in separate thread)
            self.modules['gui'] = MainWindow(self.config, self.event_bus)
            
            self.logger.info("✅ All modules initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize modules: {e}")
            raise
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, shutting down...")
            self.stop()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def start(self):
        """Start all modules and begin operation"""
        self.logger.info("🚀 Starting UltronSysAgent...")
        self.running = True
        
        try:
            # Start all modules
            startup_tasks = []
            for name, module in self.modules.items():
                if hasattr(module, 'start') and name != 'gui':  # GUI starts separately
                    startup_tasks.append(module.start())
                    self.logger.info(f"▶️  Started {name} module")
            
            # Wait for all modules to start
            if startup_tasks:
                await asyncio.gather(*startup_tasks)
            
            # Start GUI in separate thread
            gui_thread = threading.Thread(target=self.modules['gui'].start, daemon=True)
            gui_thread.start()
            
            # Speak greeting
            await self._speak_greeting()
            
            self.logger.info("🟢 UltronSysAgent fully operational")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start: {e}")
            await self.stop()
            raise
    
    async def _speak_greeting(self):
        """Speak the initial greeting"""
        try:
            greeting = self.config.get('startup.greeting', 
                "UltronSysAgent online. I am ready to assist you.")
            await self.modules['voice'].speak(greeting)
        except Exception as e:
            self.logger.error(f"Failed to speak greeting: {e}")
    
    async def stop(self):
        """Stop all modules and shutdown gracefully"""
        if not self.running:
            return
            
        self.logger.info("🔴 Stopping UltronSysAgent...")
        self.running = False
        
        # Stop all modules
        stop_tasks = []
        for name, module in self.modules.items():
            if hasattr(module, 'stop'):
                try:
                    if asyncio.iscoroutinefunction(module.stop):
                        stop_tasks.append(module.stop())
                    else:
                        module.stop()
                    self.logger.info(f"⏹️  Stopped {name} module")
                except Exception as e:
                    self.logger.error(f"Error stopping {name}: {e}")
        
        # Wait for async stops
        if stop_tasks:
            await asyncio.gather(*stop_tasks, return_exceptions=True)
        
        self.logger.info("🔴 UltronSysAgent shutdown complete")
    
    async def run(self):
        """Main run loop"""
        try:
            await self.start()
            
            # Main event loop
            while self.running:
                await asyncio.sleep(0.1)  # Prevent busy waiting
                
                # Process events from event bus
                await self.event_bus.process_events()
                
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")
        finally:
            await self.stop()
