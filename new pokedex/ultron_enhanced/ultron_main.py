#!/usr/bin/env python3
"""
ULTRON AI - Complete Voice-Controlled AI Assistant
A comprehensive AI system with voice recognition, GPT integration, OCR, file sorting, and more.

Based on the Ultron AI Developer's Guide implementation.
Structure: D:\\ULTRON
"""

import os
import sys
import json
import time
import threading
import subprocess
import logging
import traceback
import hashlib
import ctypes
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import asyncio

# Core imports
import psutil
import speech_recognition as sr
import pyttsx3
import pyautogui
from PIL import Image, ImageGrab
import numpy as np
import requests
import pygame
from pygame import mixer

# AI and ML imports
try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI not available")

try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, AutoProcessor
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers not available")

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    logging.warning("OpenCV not available")

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logging.warning("Tesseract not available")

# Local imports
from core.voice_processor import VoiceProcessor
from core.vision_system import VisionSystem  
from core.system_automation import SystemAutomation
from core.web_server import UltronWebServer

# Constants
ULTRON_ROOT = Path("D:/ULTRON")
CONFIG_PATH = ULTRON_ROOT / "config.json"
MODEL_DIR = ULTRON_ROOT / "models"
CORE_DIR = ULTRON_ROOT / "core"
ASSETS_DIR = ULTRON_ROOT / "assets"
LOG_DIR = ULTRON_ROOT / "logs"
PLUGIN_DIR = CORE_DIR / "plugins"
WAKE_WORDS = ["ultron", "hello", "speak", "ultra", "ultro", "alta"]
SYSTEM_ROLE = ("You are ULTRON - an advanced AI system controller with full access. "
               "Respond concisely, execute commands when appropriate, and provide system insights.")

@dataclass
class UltronConfig:
    """Configuration class for ULTRON AI system"""
    openai_api_key: str = ""
    voice_engine: str = "pyttsx3"
    voice_gender: str = "male"
    theme: str = "red"
    offline_mode: bool = False
    vision_enabled: bool = True
    web_port: int = 3000
    debug_mode: bool = False
    auto_sort_enabled: bool = True
    security_enabled: bool = True
    trusted_mac_addresses: List[str] = None
    performance_monitoring: bool = True
    
    def __post_init__(self):
        if self.trusted_mac_addresses is None:
            self.trusted_mac_addresses = []

class UltronCore:
    """Main ULTRON AI System Class"""
    
    def __init__(self):
        self.config = self._load_config()
        self.running = False
        self.voice_processor = None
        self.vision_system = None
        self.system_automation = None
        self.web_server = None
        self.openai_client = None
        self.local_llm = None
        self.conversation_history = []
        self.performance_metrics = {}
        self.error_count = 0
        
        # Initialize directories
        self._setup_directories()
        
        # Initialize logging
        self._setup_logging()
        
        # Initialize components
        self._initialize_components()
        
        # Set up error handling
        self._setup_error_handling()
        
    def _setup_directories(self):
        """Create necessary directories"""
        directories = [ULTRON_ROOT, MODEL_DIR, CORE_DIR, ASSETS_DIR, LOG_DIR, PLUGIN_DIR]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
        self.log_info(f"Directories initialized: {ULTRON_ROOT}")
    
    def _setup_logging(self):
        """Configure logging system"""
        log_file = LOG_DIR / f"ultron_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.DEBUG if self.config.debug_mode else logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger("ULTRON")
        self.logger.info("ULTRON AI System initializing...")
    
    def _load_config(self) -> UltronConfig:
        """Load configuration from file"""
        try:
            if CONFIG_PATH.exists():
                with open(CONFIG_PATH, 'r') as f:
                    config_data = json.load(f)
                return UltronConfig(**config_data)
            else:
                # Create default config
                config = UltronConfig()
                self._save_config(config)
                return config
        except Exception as e:
            self.log_error(f"Failed to load config: {e}")
            return UltronConfig()
    
    def _save_config(self, config: UltronConfig):
        """Save configuration to file"""
        try:
            with open(CONFIG_PATH, 'w') as f:
                json.dump(asdict(config), f, indent=2)
        except Exception as e:
            self.log_error(f"Failed to save config: {e}")
    
    def _initialize_components(self):
        """Initialize all ULTRON components"""
        try:
            # Initialize OpenAI client
            if OPENAI_AVAILABLE and self.config.openai_api_key:
                self.openai_client = OpenAI(api_key=self.config.openai_api_key)
                self.log_info("OpenAI client initialized")
            
            # Initialize Voice Processor
            self.voice_processor = VoiceProcessor(self.config)
            self.log_info("Voice processor initialized")
            
            # Initialize Vision System
            if self.config.vision_enabled:
                self.vision_system = VisionSystem(self.config)
                self.log_info("Vision system initialized")
            
            # Initialize System Automation
            self.system_automation = SystemAutomation(self.config)
            self.log_info("System automation initialized")
            
            # Initialize Web Server
            self.web_server = UltronWebServer(asdict(self.config), self)
            self.log_info("Web server initialized")
            
            # Initialize Local LLM if needed
            if self.config.offline_mode or not self.openai_client:
                self._initialize_local_llm()
            
        except Exception as e:
            self.log_error(f"Component initialization failed: {e}")
            raise
    
    def _initialize_local_llm(self):
        """Initialize local LLM for offline operation"""
        if not TRANSFORMERS_AVAILABLE:
            self.log_error("Transformers not available for local LLM")
            return
            
        try:
            # Try to load a lightweight local model
            model_name = "microsoft/DialoGPT-small"  # Lightweight alternative
            self.log_info(f"Loading local LLM: {model_name}")
            
            self.local_tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.local_llm = AutoModelForCausalLM.from_pretrained(model_name)
            
            self.log_info("Local LLM initialized successfully")
            
        except Exception as e:
            self.log_error(f"Failed to initialize local LLM: {e}")
            self.local_llm = None
    
    def _setup_error_handling(self):
        """Set up global error handling"""
        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
                
            error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            self.logger.error(f"Unhandled exception: {error_msg}")
            
            if self.voice_processor:
                self.voice_processor.speak("An internal error occurred. Please check the logs.")
                
            self.error_count += 1
            
        sys.excepthook = handle_exception
    
    def log_info(self, message: str):
        """Log info message"""
        if hasattr(self, 'logger'):
            self.logger.info(message)
        else:
            print(f"INFO: {message}")
    
    def log_error(self, message: str):
        """Log error message"""
        if hasattr(self, 'logger'):
            self.logger.error(message)
        else:
            print(f"ERROR: {message}")
    
    def log_warning(self, message: str):
        """Log warning message"""
        if hasattr(self, 'logger'):
            self.logger.warning(message)
        else:
            print(f"WARNING: {message}")
    
    async def start(self):
        """Start the ULTRON AI system"""
        try:
            self.running = True
            self.log_info("🔴 ULTRON AI System starting...")
            
            # Start web server
            if self.web_server:
                await self.web_server.start()
                self.log_info(f"Web interface available at: http://localhost:{self.config.web_port}")
            
            # Start voice processor
            if self.voice_processor:
                self.voice_processor.start_listening()
                self.log_info("Voice recognition active")
            
            # Start file sorting if enabled
            if self.config.auto_sort_enabled:
                await self._start_file_sorting()
            
            # Main loop
            await self._main_loop()
            
        except Exception as e:
            self.log_error(f"Failed to start ULTRON: {e}")
            raise
    
    async def _main_loop(self):
        """Main system loop"""
        self.log_info("ULTRON AI System ready - Main loop started")
        self.voice_processor.speak("ULTRON AI System is now online and ready for commands.")
        
        while self.running:
            try:
                await asyncio.sleep(0.1)  # Non-blocking sleep
                
                # Process voice commands
                if self.voice_processor and self.voice_processor.has_command():
                    command = self.voice_processor.get_command()
                    if command:
                        await self._process_voice_command(command)
                
                # Monitor system performance
                if self.config.performance_monitoring:
                    self._update_performance_metrics()
                
            except Exception as e:
                self.log_error(f"Error in main loop: {e}")
                await asyncio.sleep(1)  # Prevent rapid error loops
    
    async def _process_voice_command(self, command: str):
        """Process voice command through AI"""
        try:
            start_time = time.time()
            self.log_info(f"Processing command: {command}")
            
            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": command})
            
            # Get AI response
            response = await self._get_ai_response(command)
            
            # Add AI response to history
            self.conversation_history.append({"role": "assistant", "content": response})
            
            # Execute any actions if needed
            await self._execute_ai_actions(response, command)
            
            # Speak response
            if self.voice_processor:
                self.voice_processor.speak(response)
            
            # Log performance
            processing_time = time.time() - start_time
            self.performance_metrics['last_command_time'] = processing_time
            self.log_info(f"Command processed in {processing_time:.2f}s")
            
        except Exception as e:
            self.log_error(f"Error processing voice command: {e}")
            if self.voice_processor:
                self.voice_processor.speak("Sorry, I encountered an error processing that command.")
    
    async def _get_ai_response(self, command: str) -> str:
        """Get AI response from OpenAI or local LLM"""
        try:
            # Try OpenAI first
            if self.openai_client and not self.config.offline_mode:
                return await self._get_openai_response(command)
            
            # Fallback to local LLM
            elif self.local_llm:
                return self._get_local_llm_response(command)
            
            else:
                return "I'm sorry, no AI engine is available at the moment."
                
        except Exception as e:
            self.log_error(f"AI response error: {e}")
            return "I encountered an error while thinking. Please try again."
    
    async def _get_openai_response(self, command: str) -> str:
        """Get response from OpenAI API"""
        try:
            # Prepare conversation context
            messages = [{"role": "system", "content": SYSTEM_ROLE}]
            
            # Add recent conversation history (last 10 exchanges)
            recent_history = self.conversation_history[-20:] if len(self.conversation_history) > 20 else self.conversation_history
            messages.extend(recent_history)
            
            # Make API call
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Using cost-effective model
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.log_error(f"OpenAI API error: {e}")
            # Fallback to local LLM
            if self.local_llm:
                return self._get_local_llm_response(command)
            else:
                return "OpenAI service is currently unavailable."
    
    def _get_local_llm_response(self, command: str) -> str:
        """Get response from local LLM"""
        try:
            if not self.local_llm:
                return "Local AI is not available."
            
            # Simple response generation with local model
            input_text = f"User: {command}\nAssistant:"
            inputs = self.local_tokenizer.encode(input_text, return_tensors='pt')
            
            with torch.no_grad():
                outputs = self.local_llm.generate(
                    inputs,
                    max_length=inputs.shape[1] + 100,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.local_tokenizer.eos_token_id
                )
            
            response = self.local_tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
            return response.strip()
            
        except Exception as e:
            self.log_error(f"Local LLM error: {e}")
            return "I'm having trouble processing that request locally."
    
    async def _execute_ai_actions(self, ai_response: str, original_command: str):
        """Execute actions based on AI response"""
        try:
            # Check for specific action keywords
            lower_response = ai_response.lower()
            lower_command = original_command.lower()
            
            # Screenshot/Vision actions
            if any(word in lower_command for word in ["screenshot", "capture", "see", "look"]):
                if self.vision_system:
                    screenshot_path = await self.vision_system.take_screenshot()
                    self.log_info(f"Screenshot saved: {screenshot_path}")
            
            # Screen analysis
            if any(word in lower_command for word in ["analyze", "read", "ocr"]):
                if self.vision_system:
                    analysis = await self.vision_system.analyze_screen()
                    self.log_info(f"Screen analysis: {analysis}")
            
            # System commands
            if any(word in lower_command for word in ["shutdown", "restart", "sleep"]):
                if self.system_automation:
                    await self.system_automation.handle_power_command(lower_command)
            
            # File operations
            if any(word in lower_command for word in ["sort files", "organize", "clean"]):
                await self._trigger_file_sorting()
            
        except Exception as e:
            self.log_error(f"Error executing AI actions: {e}")
    
    async def _start_file_sorting(self):
        """Start automatic file sorting"""
        try:
            from core.file_sorter import FileSorter
            self.file_sorter = FileSorter(self.config)
            await self.file_sorter.start_monitoring()
            self.log_info("File sorting system started")
        except Exception as e:
            self.log_error(f"Failed to start file sorting: {e}")
    
    async def _trigger_file_sorting(self):
        """Manually trigger file sorting"""
        try:
            if hasattr(self, 'file_sorter'):
                await self.file_sorter.sort_directory()
                self.voice_processor.speak("File sorting completed.")
            else:
                self.voice_processor.speak("File sorting system is not available.")
        except Exception as e:
            self.log_error(f"File sorting error: {e}")
            self.voice_processor.speak("File sorting encountered an error.")
    
    def _update_performance_metrics(self):
        """Update system performance metrics"""
        try:
            self.performance_metrics.update({
                'cpu_percent': psutil.cpu_percent(interval=None),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'timestamp': time.time()
            })
        except Exception as e:
            self.log_error(f"Performance metrics error: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        return {
            'running': self.running,
            'voice_active': self.voice_processor.is_listening if self.voice_processor else False,
            'vision_enabled': self.config.vision_enabled,
            'ai_available': bool(self.openai_client or self.local_llm),
            'performance': self.performance_metrics,
            'error_count': self.error_count,
            'conversation_length': len(self.conversation_history)
        }
    
    async def stop(self):
        """Stop the ULTRON AI system"""
        try:
            self.running = False
            self.log_info("Stopping ULTRON AI System...")
            
            if self.voice_processor:
                self.voice_processor.stop_listening()
            
            if self.web_server:
                await self.web_server.stop()
            
            self.log_info("ULTRON AI System stopped")
            
        except Exception as e:
            self.log_error(f"Error stopping ULTRON: {e}")

# CLI Interface
async def main():
    """Main entry point"""
    try:
        print("🔴 ULTRON AI - Advanced Voice-Controlled Assistant")
        print("=" * 50)
        
        # Initialize ULTRON
        ultron = UltronCore()
        
        # Start the system
        await ultron.start()
        
    except KeyboardInterrupt:
        print("\n🔴 ULTRON AI shutdown requested")
        if 'ultron' in locals():
            await ultron.stop()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Ensure proper event loop handling
    if sys.platform.startswith('win'):
        # Windows specific event loop policy
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(main())
