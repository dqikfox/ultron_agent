#!/usr/bin/env python3
"""
ULTRON - Complete AI Assistant System
Main entry point with full functionality
"""

import os
import sys
import json
import time
import asyncio
import threading
import logging
import subprocess
from pathlib import Path
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.voice_engine import VoiceEngine
from core.vision_system import VisionSystem
from core.ai_brain import AIBrain
from core.system_control import SystemControl
from core.file_manager import FileManager
from core.web_interface import WebInterface
from gui.ultron_gui import UltronGUI

class UltronCore:
    """Main ULTRON system coordinator"""
    
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config = self.load_config()
        self.running = True
        
        # Setup logging
        self.setup_logging()
        
        # Initialize components
        self.voice = VoiceEngine(self.config)
        self.vision = VisionSystem(self.config)
        self.ai = AIBrain(self.config)
        self.system = SystemControl(self.config)
        self.files = FileManager(self.config)
        self.web = WebInterface(self.config, self)
        
        # Control variables
        self.listening = False
        self.last_command = None
        self.conversation_history = []
        
        logging.info("ULTRON Core initialized successfully")
    
    def load_config(self):
        """Load configuration from file"""
        default_config = {
            "voice": {
                "enabled": True,
                "wake_words": ["ultron", "hello", "computer"],
                "tts_rate": 150,
                "recognition_timeout": 5
            },
            "ai": {
                "openai_api_key": "",
                "model": "gpt-4",
                "local_model": "microsoft/DialoGPT-small",
                "use_local": False
            },
            "system": {
                "admin_required": True,
                "safe_commands_only": True,
                "log_activities": True
            },
            "web": {
                "enabled": True,
                "port": 3000,
                "host": "localhost"
            },
            "vision": {
                "enabled": True,
                "auto_enhance": True,
                "ocr_language": "eng"
            },
            "files": {
                "auto_sort": True,
                "watch_downloads": True,
                "backup_before_sort": True
            }
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in loaded_config:
                            loaded_config[key] = value
                        elif isinstance(value, dict):
                            for subkey, subvalue in value.items():
                                if subkey not in loaded_config[key]:
                                    loaded_config[key][subkey] = subvalue
                    return loaded_config
            else:
                # Create default config
                with open(self.config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
                return default_config
                
        except Exception as e:
            logging.error(f"Config load error: {e}")
            return default_config
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Configure logging
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # Main log file
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(log_dir / "ultron.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        # Component-specific loggers
        for component in ['voice', 'vision', 'ai', 'system', 'files', 'web']:
            logger = logging.getLogger(component)
            handler = logging.FileHandler(log_dir / f"{component}.log")
            handler.setFormatter(logging.Formatter(log_format))
            logger.addHandler(handler)
    
    async def start_web_interface(self):
        """Start web interface if enabled"""
        if self.config['web']['enabled']:
            try:
                await self.web.start()
                logging.info(f"Web interface started on http://{self.config['web']['host']}:{self.config['web']['port']}")
            except Exception as e:
                logging.error(f"Web interface start failed: {e}")
    
    def start_voice_loop(self):
        """Start voice command listening loop"""
        if not self.config['voice']['enabled']:
            return
            
        self.listening = True
        
        def voice_loop():
            while self.listening and self.running:
                try:
                    command = self.voice.listen_for_command()
                    if command:
                        logging.info(f"Voice command received: {command}")
                        asyncio.run_coroutine_threadsafe(
                            self.process_command(command, source="voice"),
                            asyncio.get_event_loop()
                        )
                except Exception as e:
                    logging.error(f"Voice loop error: {e}")
                    time.sleep(1)
        
        threading.Thread(target=voice_loop, daemon=True).start()
        logging.info("Voice listening started")
    
    async def process_command(self, command, source="text", callback=None):
        """Process command from any source"""
        try:
            start_time = time.time()
            
            # Log command
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "source": source,
                "command": command,
                "response": None
            })
            
            # Parse command
            command_lower = command.lower().strip()
            response = ""
            
            # System commands
            if any(word in command_lower for word in ["screenshot", "capture", "screen"]):
                result = await self.vision.take_screenshot()
                if result['success']:
                    ocr_text = await self.vision.extract_text(result['path'])
                    response = f"Screenshot saved. " + (f"Text found: {ocr_text[:100]}..." if ocr_text else "No text detected.")
                else:
                    response = "Screenshot failed: " + result.get('error', 'Unknown error')
            
            elif any(word in command_lower for word in ["system", "status", "info"]):
                system_info = await self.system.get_status()
                response = f"System Status - CPU: {system_info['cpu']:.1f}%, Memory: {system_info['memory']:.1f}%, Admin: {system_info['admin']}"
            
            elif any(word in command_lower for word in ["sort", "organize", "files"]):
                result = await self.files.auto_sort()
                response = f"File sorting complete. Processed {result.get('total', 0)} files."
            
            elif "open" in command_lower:
                app_name = command_lower.replace("open", "").strip()
                result = await self.system.launch_application(app_name)
                response = result['message']
            
            elif any(word in command_lower for word in ["time", "clock"]):
                current_time = datetime.now().strftime("%I:%M %p")
                response = f"The current time is {current_time}"
            
            elif any(word in command_lower for word in ["date", "today"]):
                current_date = datetime.now().strftime("%A, %B %d, %Y")
                response = f"Today is {current_date}"
            
            elif any(word in command_lower for word in ["shutdown", "restart", "sleep"]):
                if "shutdown" in command_lower:
                    await self.system.shutdown()
                    response = "Initiating system shutdown..."
                elif "restart" in command_lower:
                    await self.system.restart()
                    response = "Initiating system restart..."
                elif "sleep" in command_lower:
                    await self.system.sleep()
                    response = "Putting system to sleep..."
            
            else:
                # Use AI for general conversation
                response = await self.ai.generate_response(command, self.conversation_history[-5:])
            
            # Record response time
            response_time = time.time() - start_time
            
            # Update conversation history
            self.conversation_history[-1]['response'] = response
            self.conversation_history[-1]['response_time'] = response_time
            
            # Speak response if voice command
            if source == "voice":
                self.voice.speak(response)
            
            # Call callback if provided
            if callback:
                callback(response)
            
            logging.info(f"Command processed in {response_time:.2f}s: {command[:50]}... -> {response[:50]}...")
            
            return {
                "success": True,
                "response": response,
                "response_time": response_time
            }
            
        except Exception as e:
            error_msg = f"Error processing command: {e}"
            logging.error(error_msg)
            
            if source == "voice":
                self.voice.speak("Sorry, I encountered an error processing your command.")
            
            if callback:
                callback(error_msg)
            
            return {
                "success": False,
                "error": error_msg
            }
    
    def get_status(self):
        """Get overall system status"""
        return {
            "running": self.running,
            "listening": self.listening,
            "components": {
                "voice": self.voice.is_available(),
                "vision": self.vision.is_available(),
                "ai": self.ai.is_available(),
                "system": self.system.is_available(),
                "files": self.files.is_available(),
                "web": self.web.is_running()
            },
            "last_command": self.last_command,
            "conversation_count": len(self.conversation_history)
        }
    
    async def run_async(self):
        """Run ULTRON with async support"""
        try:
            # Start web interface
            await self.start_web_interface()
            
            # Start voice loop
            self.start_voice_loop()
            
            # Keep running
            while self.running:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logging.info("Shutdown requested")
        finally:
            await self.shutdown()
    
    def run_gui(self):
        """Run ULTRON with GUI interface"""
        try:
            gui = UltronGUI(self)
            gui.run()
        except Exception as e:
            logging.error(f"GUI error: {e}")
        finally:
            self.running = False
    
    def run_console(self):
        """Run ULTRON in console mode"""
        print("🔴 ULTRON AI Assistant - Console Mode")
        print("=" * 50)
        print("Commands: screenshot, system info, sort files, open <app>")
        print("Type 'help' for more commands, 'quit' to exit")
        print()
        
        while self.running:
            try:
                command = input("ULTRON> ").strip()
                
                if command.lower() in ['quit', 'exit']:
                    break
                elif command.lower() == 'help':
                    self.show_help()
                elif command:
                    result = asyncio.run(self.process_command(command, source="console"))
                    if result['success']:
                        print(f"Response: {result['response']}")
                    else:
                        print(f"Error: {result['error']}")
                        
            except KeyboardInterrupt:
                break
            except Exception as e:
                logging.error(f"Console error: {e}")
        
        print("ULTRON shutting down...")
    
    def show_help(self):
        """Show available commands"""
        print("\n🔴 ULTRON Commands:")
        print("─" * 30)
        print("• screenshot - Take and analyze screenshot")
        print("• system info - Show system status")
        print("• sort files - Organize files by type")
        print("• open <app> - Launch application")
        print("• time - Get current time")
        print("• date - Get current date")
        print("• shutdown - Shutdown system (admin required)")
        print("• restart - Restart system (admin required)")
        print("• sleep - Put system to sleep")
        print("• <any text> - AI conversation")
        print()
    
    async def shutdown(self):
        """Graceful shutdown"""
        logging.info("Initiating ULTRON shutdown...")
        
        self.running = False
        self.listening = False
        
        # Stop components
        if hasattr(self, 'web') and self.web:
            await self.web.stop()
        
        # Save conversation history
        try:
            with open("conversation_history.json", "w") as f:
                json.dump(self.conversation_history, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save conversation history: {e}")
        
        logging.info("ULTRON shutdown complete")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ULTRON AI Assistant')
    parser.add_argument('--mode', choices=['gui', 'console', 'async'], default='gui',
                       help='Interface mode (default: gui)')
    parser.add_argument('--config', default='config.json',
                       help='Configuration file path')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create ULTRON instance
    ultron = UltronCore(args.config)
    
    try:
        if args.mode == 'gui':
            ultron.run_gui()
        elif args.mode == 'console':
            ultron.run_console()
        elif args.mode == 'async':
            asyncio.run(ultron.run_async())
    except KeyboardInterrupt:
        print("\nShutdown requested")
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
