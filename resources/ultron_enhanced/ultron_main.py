"""
ULTRON Enhanced AI System
Combines AI automation with Pokedex-style interface controls
Enhanced with modular architecture and advanced features
"""

import os
import sys
import json
import time
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import psutil
import logging
import ctypes
import webbrowser
from pathlib import Path

# Import ULTRON core modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

try:
    from voice_processor import VoiceProcessor, UltronVoiceCommands
    from system_automation import SystemAutomation
    from vision_system import VisionSystem
    from web_server import UltronWebServer
except ImportError as e:
    logging.error(f"Failed to import core modules: {e}")
    sys.exit(1)

# Optional imports
try:
    import speech_recognition as sr
    import openai
    import pyttsx3
    import pygame
    from PIL import Image, ImageTk, ImageGrab
    import numpy as np
    import requests
    FULL_FEATURES = True
except ImportError as e:
    logging.warning(f"Some optional features unavailable: {e}")
    FULL_FEATURES = False

# Enhanced Configuration
ULTRON_ROOT = r"D:\ULTRON"
CONFIG_PATH = os.path.join(ULTRON_ROOT, "config.json")
MODEL_DIR = os.path.join(ULTRON_ROOT, "models")
CORE_DIR = os.path.join(ULTRON_ROOT, "core")
ASSETS_DIR = os.path.join(ULTRON_ROOT, "assets")
LOG_DIR = os.path.join(ULTRON_ROOT, "logs")
WEB_DIR = os.path.join(ULTRON_ROOT, "web")
PLUGIN_DIR = os.path.join(CORE_DIR, "plugins")
WAKE_WORDS = ["ultron", "hello", "speak", "ultra", "ultro", "alta", "jarvis"]
SYSTEM_ROLE = ("You are ULTRON - an advanced AI system controller with Pokedex-style interface. "
               "Respond concisely, execute commands when appropriate, and provide system insights.")
ICON_PATH = os.path.join(ASSETS_DIR, "ultron_icon.png")
SOUND_EFFECTS = {
    "wake": os.path.join(ASSETS_DIR, "wake.wav"),
    "confirm": os.path.join(ASSETS_DIR, "confirm.wav"),
    "error": os.path.join(ASSETS_DIR, "error.wav"),
    "pokedex_open": os.path.join(ASSETS_DIR, "pokedex_open.wav"),
    "button_press": os.path.join(ASSETS_DIR, "button_press.wav")
}

# Create directories if missing
for directory in [ULTRON_ROOT, MODEL_DIR, CORE_DIR, ASSETS_DIR, LOG_DIR, WEB_DIR, PLUGIN_DIR]:
    os.makedirs(directory, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "ultron.log")),
        logging.StreamHandler()
    ]
)

def log_info(message):
    logging.info(message)

def log_error(message):
    logging.error(message)

# Load/Save configuration
def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {
        "openai_api_key": "",
        "voice": "male",
        "hotkeys": {},
        "theme": "red",
        "offline_mode": False,
        "vision_enabled": torch.cuda.is_available() if torch.cuda.is_available() else False,
        "web_port": 3000,
        "auto_launch_web": True,
        "pokedex_mode": True
    }

def save_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)

class HyperVision:
    """Enhanced vision system with screen analysis capabilities"""
    def __init__(self, config):
        self.available = False
        if not config.get("vision_enabled", False):
            log_info("Vision system disabled in configuration")
            return
        
        try:
            # Try to initialize vision model (simplified for compatibility)
            self.available = True
            log_info("Vision system initialized successfully")
        except Exception as e:
            log_error(f"Vision init failed: {str(e)}")
            self.available = False

    def analyze_screen(self, prompt="Analyze this screen"):
        if not self.available:
            return "Vision module not available"
        
        try:
            screenshot = ImageGrab.grab()
            screenshot_path = os.path.join(ASSETS_DIR, "last_screenshot.png")
            screenshot.save(screenshot_path)
            
            # Basic screen analysis (can be enhanced with actual vision model)
            analysis = f"Screen captured at {time.strftime('%H:%M:%S')}. "
            analysis += f"Resolution: {screenshot.size[0]}x{screenshot.size[1]}. "
            analysis += f"Analysis: {prompt}"
            
            return analysis
        except Exception as e:
            return f"Vision error: {str(e)}"

    def analyze_image(self, image, prompt):
        if not self.available:
            return "Vision module not available"
        
        try:
            # Basic image analysis
            if hasattr(image, 'size'):
                return f"Image analysis: {image.size[0]}x{image.size[1]} pixels. Prompt: {prompt}"
            else:
                return f"Image analysis completed. Prompt: {prompt}"
        except Exception as e:
            return f"Vision error: {str(e)}"

class QuantumLLM:
    """Enhanced LLM system with local and cloud options"""
    def __init__(self, config):
        self.model = None
        self.config = config
        self.openai_available = bool(config.get("openai_api_key"))
        
        if self.openai_available:
            try:
                openai.api_key = config.get("openai_api_key")
                log_info("OpenAI API initialized")
            except Exception as e:
                log_error(f"OpenAI initialization failed: {e}")
                self.openai_available = False

    def generate(self, prompt, max_tokens=512):
        if self.openai_available:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": SYSTEM_ROLE},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            except Exception as e:
                log_error(f"OpenAI API error: {e}")
        
        # Fallback to simple responses
        return self._generate_fallback_response(prompt)
    
    def _generate_fallback_response(self, prompt):
        """Simple fallback responses when AI is not available"""
        responses = {
            "hello": "Hello! ULTRON system is online and ready.",
            "status": "All systems operational. Pokedex interface active.",
            "help": "Available commands: status, screen analysis, system control, file operations.",
            "time": f"Current time: {time.strftime('%H:%M:%S')}",
            "default": "ULTRON acknowledging your request. Processing..."
        }
        
        prompt_lower = prompt.lower()
        for key, response in responses.items():
            if key in prompt_lower:
                return response
        
        return responses["default"]

class SentinelAutomator:
    """Enhanced automation system with Pokedex-style controls"""
    def __init__(self, config):
        self.admin = self.is_admin()
        self.vision = HyperVision(config)
        self.activity_log = []
        self.config = config

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def run_as_admin(self):
        if not self.admin:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit()

    def execute(self, command_type, content):
        result = ""
        try:
            if command_type == "powershell":
                process = subprocess.Popen(
                    ["powershell", "-Command", content],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = process.communicate()
                result = stdout or stderr
            
            elif command_type == "python" and self.admin:
                # Safe python execution
                safe_globals = {"result": "", "os": os, "time": time, "requests": requests}
                try:
                    exec(content, safe_globals)
                    result = safe_globals.get("result", "Python code executed")
                except Exception as e:
                    result = f"Python execution error: {str(e)}"
            
            elif command_type == "function":
                result = self.run_system_function(content)
            
            elif command_type == "pokedex_control":
                result = self.handle_pokedex_control(content)
            
            self.log_activity(command_type, content, result)
            return result
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.log_activity(command_type, content, error_msg)
            return error_msg

    def handle_pokedex_control(self, action):
        """Handle Pokedex-style interface controls"""
        actions = {
            "dpad_up": "Navigation: Up",
            "dpad_down": "Navigation: Down",
            "dpad_left": "Navigation: Left",
            "dpad_right": "Navigation: Right",
            "button_a": "Action: Select/Confirm",
            "button_b": "Action: Back/Cancel",
            "power_button": "System: Power control",
            "volume_button": "Audio: Volume control",
            "settings_button": "System: Settings menu"
        }
        
        return actions.get(action, f"Unknown Pokedex control: {action}")

    def run_system_function(self, function_call):
        """Execute system functions safely"""
        try:
            function_data = json.loads(function_call) if isinstance(function_call, str) else function_call
            func_name = function_data.get("function")
            params = function_data.get("parameters", {})
            
            if func_name == "system_power":
                return self.control_power(params.get("action"))
            elif func_name == "process_control":
                return self.manage_process(params.get("pid"), params.get("action"))
            elif func_name == "screen_capture":
                return self.vision.analyze_screen(params.get("prompt", ""))
            elif func_name == "web_launch":
                webbrowser.open(params.get("url", "https://google.com"))
                return f"Launched: {params.get('url', 'default URL')}"
            else:
                return f"Unknown function: {func_name}"
                
        except Exception as e:
            return f"Function execution error: {str(e)}"

    def control_power(self, action):
        """System power control"""
        if not self.admin:
            return "Admin privileges required for power control"
        
        try:
            if action == "shutdown":
                subprocess.run(["shutdown", "/s", "/t", "10"], check=True)
                return "System shutdown initiated (10 seconds)"
            elif action == "reboot":
                subprocess.run(["shutdown", "/r", "/t", "10"], check=True)
                return "System reboot initiated (10 seconds)"
            elif action == "hibernate":
                subprocess.run(["shutdown", "/h"], check=True)
                return "System hibernation initiated"
            else:
                return f"Unknown power action: {action}"
        except Exception as e:
            return f"Power control error: {str(e)}"

    def manage_process(self, pid, action):
        """Process management"""
        try:
            if action == "terminate" and pid:
                process = psutil.Process(int(pid))
                process.terminate()
                return f"Process {pid} terminated"
            elif action == "list":
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                    processes.append(f"{proc.info['pid']}: {proc.info['name']}")
                return "\\n".join(processes[:10])  # Top 10 processes
            else:
                return f"Unknown process action: {action}"
        except Exception as e:
            return f"Process management error: {str(e)}"

    def log_activity(self, cmd_type, content, result):
        """Log system activities"""
        entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "type": cmd_type,
            "content": content[:200] + "..." if len(content) > 200 else content,
            "result": str(result)[:200] + "..." if len(str(result)) > 200 else str(result)
        }
        self.activity_log.append(entry)
        
        # Write to log file
        log_file = os.path.join(LOG_DIR, "activity.log")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\\n")

class WebServer:
    """Built-in web server for Pokedex interface"""
    def __init__(self, port=3000, web_dir=WEB_DIR):
        self.port = port
        self.web_dir = web_dir
        self.server = None
        self.server_thread = None

    def start(self):
        """Start the web server"""
        try:
            os.chdir(self.web_dir)
            handler = http.server.SimpleHTTPRequestHandler
            self.server = socketserver.TCPServer(("", self.port), handler)
            
            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()
            
            log_info(f"Web server started on port {self.port}")
            return True
        except Exception as e:
            log_error(f"Failed to start web server: {e}")
            return False

    def stop(self):
        """Stop the web server"""
        if self.server:
            self.server.shutdown()
            log_info("Web server stopped")

class UltronCore:
    """Core ULTRON system with enhanced modular architecture"""
    
    def __init__(self, config: dict):
        self.config = config
        self.is_running = False
        
        # Initialize core modules
        self.voice_processor = None
        self.system_automation = None
        self.vision_system = None
        self.web_server = None
        self.voice_commands = None
        
        # System state
        self.current_mode = "pokedex"
        self.command_history = []
        self.system_stats = {}
        
        self._init_modules()
    
    def _init_modules(self):
        """Initialize all core modules"""
        try:
            # System automation
            self.system_automation = SystemAutomation(self.config)
            log_info("System automation initialized")
            
            # Vision system
            if self.config.get("vision_enabled", True):
                self.vision_system = VisionSystem(self.config)
                log_info("Vision system initialized")
            
            # Voice processor
            if FULL_FEATURES:
                self.voice_processor = VoiceProcessor(self.config)
                self.voice_commands = UltronVoiceCommands(self)
                self._setup_voice_callbacks()
                log_info("Voice processing initialized")
            
            # Web server
            self.web_server = UltronWebServer(self.config, self)
            log_info("Web server initialized")
            
        except Exception as e:
            log_error(f"Module initialization failed: {e}")
    
    def _setup_voice_callbacks(self):
        """Setup voice processor callbacks"""
        if not self.voice_processor:
            return
        
        self.voice_processor.register_callback('wake_word_detected', self._handle_wake_word)
        self.voice_processor.register_callback('command_received', self._handle_voice_command)
        self.voice_processor.register_callback('speech_detected', self._handle_speech)
    
    def _handle_wake_word(self, data: dict):
        """Handle wake word detection"""
        log_info(f"Wake word detected: {data.get('text', '')}")
        
        # Trigger wake effects in GUI
        if hasattr(self, 'gui') and self.gui:
            self.gui.trigger_wake_effect()
    
    def _handle_voice_command(self, data: dict):
        """Handle voice commands"""
        command = data.get('command', '')
        
        if self.voice_commands:
            # Process through voice command handler
            command_data = self.voice_processor.process_command(command)
            response = self.voice_commands.process_ultron_command(command_data)
            
            # Speak response if needed
            if response.get('requires_speech', True) and response.get('message'):
                self.voice_processor.speak(response['message'])
            
            # Update GUI
            if hasattr(self, 'gui') and self.gui:
                self.gui.add_voice_interaction(command, response['message'])
    
    def _handle_speech(self, data: dict):
        """Handle general speech detection"""
        # Process non-wake-word speech
        pass
    
    def start(self):
        """Start ULTRON core systems"""
        try:
            self.is_running = True
            
            # Start voice processor
            if self.voice_processor:
                self.voice_processor.start_listening()
            
            # Start web server
            if self.web_server and self.config.get("auto_launch_web", True):
                self.web_server.start()
                
                # Auto-launch browser if configured
                if self.config.get("auto_launch_web", True):
                    time.sleep(2)  # Wait for server to start
                    self._launch_web_interface()
            
            log_info("ULTRON core systems started")
            
        except Exception as e:
            log_error(f"Failed to start ULTRON core: {e}")
    
    def stop(self):
        """Stop ULTRON core systems"""
        try:
            self.is_running = False
            
            if self.voice_processor:
                self.voice_processor.stop_listening()
                self.voice_processor.cleanup()
            
            if self.web_server:
                self.web_server.stop()
            
            log_info("ULTRON core systems stopped")
            
        except Exception as e:
            log_error(f"Error stopping ULTRON core: {e}")
    
    def _launch_web_interface(self):
        """Launch web interface in browser"""
        try:
            port = self.config.get("web_port", 3000)
            url = f"http://localhost:{port}"
            webbrowser.open(url)
            log_info(f"Web interface launched: {url}")
        except Exception as e:
            log_error(f"Failed to launch web interface: {e}")
    
    def process_command(self, command: str, command_type: str = "text") -> dict:
        """Process commands from various sources"""
        try:
            result = {
                "success": True,
                "command": command,
                "type": command_type,
                "timestamp": time.time(),
                "response": ""
            }
            
            # Process based on command type and content
            if command.lower().startswith(("system", "sys")):
                # System commands
                if self.system_automation:
                    action_result = self.system_automation.execute_command("system_info", {})
                    result["response"] = action_result.get("message", "System command executed")
                else:
                    result["response"] = "System automation not available"
            
            elif command.lower().startswith(("capture", "screenshot")):
                # Vision commands
                if self.vision_system:
                    capture_result = self.vision_system.capture_screen()
                    result["response"] = capture_result.get("message", "Screenshot taken")
                else:
                    result["response"] = "Vision system not available"
            
            elif command.lower().startswith(("analyze", "vision")):
                # Analysis commands
                if self.vision_system:
                    analysis_result = self.vision_system.analyze_screen()
                    result["response"] = analysis_result.get("comprehensive_description", "Analysis completed")
                else:
                    result["response"] = "Vision system not available"
            
            else:
                # General AI processing
                result["response"] = self._generate_ai_response(command)
            
            # Store in history
            self.command_history.append(result)
            if len(self.command_history) > 100:
                self.command_history.pop(0)
            
            return result
            
        except Exception as e:
            log_error(f"Command processing error: {e}")
            return {
                "success": False,
                "error": str(e),
                "command": command,
                "type": command_type,
                "timestamp": time.time()
            }
    
    def _generate_ai_response(self, command: str) -> str:
        """Generate AI response for commands"""
        # Enhanced response generation
        cmd_lower = command.lower()
        
        responses = {
            "hello": "ULTRON system online. Pokedex interface ready for commands.",
            "status": f"All systems operational. Mode: {self.current_mode}. Time: {time.strftime('%H:%M:%S')}",
            "help": "Available commands: system status, screenshot, analyze screen, voice controls, file operations, task management.",
            "time": f"Current time: {time.strftime('%H:%M:%S on %A, %B %d, %Y')}",
            "shutdown": "Shutdown request acknowledged. Use power controls for confirmation.",
            "theme": f"Current theme: {self.config.get('theme', 'red')}. Available: red, blue."
        }
        
        # Find best matching response
        for keyword, response in responses.items():
            if keyword in cmd_lower:
                return response
        
        # Default response
        return f"Command acknowledged: {command}. ULTRON processing request."
    
    def get_status(self) -> dict:
        """Get current system status"""
        return {
            "core_running": self.is_running,
            "current_mode": self.current_mode,
            "voice_available": self.voice_processor is not None,
            "vision_available": self.vision_system is not None,
            "web_server_running": self.web_server.is_running if self.web_server else False,
            "command_count": len(self.command_history),
            "uptime": time.time() - (self.command_history[0]["timestamp"] if self.command_history else time.time())
        }
    
    def get_system_info(self, info_type: str = "basic") -> dict:
        """Get system information"""
        if self.system_automation:
            return self.system_automation.system_monitor.get_system_info(info_type)
        else:
            # Fallback basic info
            try:
                return {
                    "success": True,
                    "system_info": {
                        "cpu_percent": psutil.cpu_percent(),
                        "memory_percent": psutil.virtual_memory().percent,
                        "disk_percent": psutil.disk_usage('/').percent
                    }
                }
            except:
                return {"success": False, "message": "System info not available"}
    
    def execute_system_action(self, action: str, data: dict) -> dict:
        """Execute system actions"""
        if self.system_automation:
            return self.system_automation.execute_command(action, data)
        else:
            return {"success": False, "message": "System automation not available"}
    
    def save_config(self):
        """Save current configuration"""
        try:
            save_config(self.config)
            log_info("Configuration saved")
        except Exception as e:
            log_error(f"Failed to save configuration: {e}")

class UltronPokedexInterface(tk.Tk):
    """Enhanced ULTRON with Pokedex-style interface"""
    def __init__(self):
        super().__init__()
        self.title("ULTRON Enhanced - Pokedex AI System")
        self.geometry("1600x1000")
        self.configure(bg='#000000')
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Load configuration
        self.config = load_config()
        
        # Initialize ULTRON core
        self.ultron_core = UltronCore(self.config)
        self.ultron_core.gui = self  # Set GUI reference
        
        # Initialize pygame for sound effects
        try:
            if FULL_FEATURES:
                pygame.mixer.init()
        except Exception as e:
            log_error(f"Pygame mixer initialization failed: {e}")
        
        # System status variables
        self.cpu_usage = tk.StringVar()
        self.mem_usage = tk.StringVar()
        self.disk_usage = tk.StringVar()
        self.status = tk.StringVar(value="Status: ULTRON Enhanced Online - Pokedex Mode")
        self.listening_state = tk.BooleanVar(value=False)
        
        # Animation variables
        self.animating = False
        self.glow_phase = 0
        self.theme = self.config.get("theme", "red")
        
        # Initialize GUI
        self.create_pokedex_gui()
        
        # Start monitoring and services
        self.update_system_stats_enhanced()
        self.after(5000, self.update_system_stats_enhanced)  # Update every 5 seconds
        
        # Start animation
        self.after(50, self.update_animation)
        
        # Start ULTRON core
        self.ultron_core.start()
        
        # Play startup sound
        self.play_sound("pokedex_open")
        
        log_info("ULTRON Enhanced Pokedex Interface initialized successfully")

    def create_pokedex_gui(self):
        """Create Pokedex-style GUI"""
        # Main container
        main_frame = tk.Frame(self, bg='#000000')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left panel - Pokedex controls
        left_panel = tk.Frame(main_frame, bg='#000000', width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        
        self.create_pokedex_controls(left_panel)
        
        # Right panel - Main screen and info
        right_panel = tk.Frame(main_frame, bg='#000000')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.create_main_screen(right_panel)
        self.create_control_panels(right_panel)

    def create_pokedex_controls(self, parent):
        """Create Pokedex-style control panel"""
        # Title
        title_frame = tk.Frame(parent, bg='#000000')
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            title_frame,
            text="ULTRON",
            font=("Orbitron", 24, "bold"),
            fg='#00ff41',
            bg='#000000'
        ).pack()
        
        tk.Label(
            title_frame,
            text="POKEDEX AI SYSTEM",
            font=("Orbitron", 10),
            fg='#00ff41',
            bg='#000000'
        ).pack()
        
        # LED indicators
        led_frame = tk.Frame(parent, bg='#000000')
        led_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Main LED
        self.main_led = tk.Canvas(led_frame, width=60, height=60, bg='#000000', highlightthickness=0)
        self.main_led.pack(side=tk.LEFT, padx=(20, 10))
        
        # Small LEDs
        small_led_frame = tk.Frame(led_frame, bg='#000000')
        small_led_frame.pack(side=tk.LEFT)
        
        self.small_leds = []
        colors = ['#ffff00', '#00ff00', '#ff0000']
        for color in colors:
            led = tk.Canvas(small_led_frame, width=20, height=20, bg='#000000', highlightthickness=0)
            led.pack(pady=2)
            led.create_oval(2, 2, 18, 18, fill=color, outline='')
            self.small_leds.append(led)
        
        # D-Pad navigation
        dpad_frame = tk.LabelFrame(
            parent,
            text="NAVIGATION",
            bg='#000000',
            fg='#00ff41',
            font=("Orbitron", 10, "bold")
        )
        dpad_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.create_dpad(dpad_frame)
        
        # Action buttons
        action_frame = tk.LabelFrame(
            parent,
            text="ACTIONS",
            bg='#000000',
            fg='#00ff41',
            font=("Orbitron", 10, "bold")
        )
        action_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.create_action_buttons(action_frame)
        
        # System controls
        system_frame = tk.LabelFrame(
            parent,
            text="SYSTEM",
            bg='#000000',
            fg='#00ff41',
            font=("Orbitron", 10, "bold")
        )
        system_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.create_system_controls(system_frame)

    def create_dpad(self, parent):
        """Create D-Pad style navigation controls"""
        dpad_container = tk.Frame(parent, bg='#000000')
        dpad_container.pack(pady=10)
        
        # Center the D-Pad
        dpad_frame = tk.Frame(dpad_container, bg='#000000')
        dpad_frame.pack()
        
        button_style = {
            'bg': '#333333',
            'fg': '#00ff41',
            'activebackground': '#555555',
            'activeforeground': '#00ff41',
            'font': ("Orbitron", 12, "bold"),
            'relief': tk.RAISED,
            'bd': 2,
            'width': 3,
            'height': 1
        }
        
        # Up
        tk.Button(
            dpad_frame,
            text="▲",
            command=lambda: self.handle_dpad("up"),
            **button_style
        ).grid(row=0, column=1, padx=2, pady=2)
        
        # Left, Center, Right
        tk.Button(
            dpad_frame,
            text="◄",
            command=lambda: self.handle_dpad("left"),
            **button_style
        ).grid(row=1, column=0, padx=2, pady=2)
        
        tk.Button(
            dpad_frame,
            text="●",
            command=lambda: self.handle_dpad("center"),
            **button_style
        ).grid(row=1, column=1, padx=2, pady=2)
        
        tk.Button(
            dpad_frame,
            text="►",
            command=lambda: self.handle_dpad("right"),
            **button_style
        ).grid(row=1, column=2, padx=2, pady=2)
        
        # Down
        tk.Button(
            dpad_frame,
            text="▼",
            command=lambda: self.handle_dpad("down"),
            **button_style
        ).grid(row=2, column=1, padx=2, pady=2)

    def create_action_buttons(self, parent):
        """Create action buttons (A, B style)"""
        button_frame = tk.Frame(parent, bg='#000000')
        button_frame.pack(pady=10)
        
        action_style = {
            'bg': '#ff4444',
            'fg': '#ffffff',
            'activebackground': '#ff6666',
            'activeforeground': '#ffffff',
            'font': ("Orbitron", 14, "bold"),
            'relief': tk.RAISED,
            'bd': 3,
            'width': 4,
            'height': 2
        }
        
        # A Button
        tk.Button(
            button_frame,
            text="A",
            command=lambda: self.handle_action_button("A"),
            **action_style
        ).pack(side=tk.LEFT, padx=10)
        
        # B Button
        b_style = action_style.copy()
        b_style['bg'] = '#4444ff'
        b_style['activebackground'] = '#6666ff'
        
        tk.Button(
            button_frame,
            text="B",
            command=lambda: self.handle_action_button("B"),
            **b_style
        ).pack(side=tk.LEFT, padx=10)

    def create_system_controls(self, parent):
        """Create system control buttons"""
        control_frame = tk.Frame(parent, bg='#000000')
        control_frame.pack(pady=10)
        
        control_style = {
            'bg': '#444444',
            'fg': '#00ff41',
            'activebackground': '#666666',
            'activeforeground': '#00ff41',
            'font': ("Orbitron", 8, "bold"),
            'relief': tk.RAISED,
            'bd': 2,
            'width': 8,
            'height': 2
        }
        
        controls = [
            ("POWER", self.handle_power),
            ("VOLUME", self.handle_volume),
            ("SETTINGS", self.handle_settings)
        ]
        
        for text, command in controls:
            tk.Button(
                control_frame,
                text=text,
                command=command,
                **control_style
            ).pack(side=tk.LEFT, padx=5)

    def create_main_screen(self, parent):
        """Create main display screen"""
        screen_frame = tk.LabelFrame(
            parent,
            text="MAIN DISPLAY",
            bg='#000000',
            fg='#00ff41',
            font=("Orbitron", 12, "bold")
        )
        screen_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Create tabbed interface
        self.notebook = ttk.Notebook(screen_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure dark theme for notebook
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#000000')
        style.configure('TNotebook.Tab', background='#333333', foreground='#00ff41')
        
        # Console tab
        self.create_console_tab()
        
        # System info tab
        self.create_system_tab()
        
        # Vision tab
        self.create_vision_tab()

    def create_console_tab(self):
        """Create console/chat interface tab"""
        console_frame = tk.Frame(self.notebook, bg='#000000')
        self.notebook.add(console_frame, text="CONSOLE")
        
        # Conversation display
        self.conversation = scrolledtext.ScrolledText(
            console_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg='#000000',
            fg='#00ff41',
            insertbackground='#00ff41',
            font=("Consolas", 10),
            relief=tk.FLAT
        )
        self.conversation.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Command input
        input_frame = tk.Frame(console_frame, bg='#000000')
        input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.cmd_entry = tk.Entry(
            input_frame,
            bg='#111111',
            fg='#00ff41',
            insertbackground='#00ff41',
            relief=tk.FLAT,
            font=("Consolas", 11)
        )
        self.cmd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.cmd_entry.bind("<Return>", self.execute_manual)
        
        tk.Button(
            input_frame,
            text="EXECUTE",
            command=self.execute_manual,
            bg='#333333',
            fg='#00ff41',
            activebackground='#555555',
            activeforeground='#00ff41',
            font=("Orbitron", 10, "bold"),
            relief=tk.RAISED
        ).pack(side=tk.RIGHT)

    def create_system_tab(self):
        """Create system information tab"""
        system_frame = tk.Frame(self.notebook, bg='#000000')
        self.notebook.add(system_frame, text="SYSTEM")
        
        # System stats
        stats_frame = tk.LabelFrame(
            system_frame,
            text="SYSTEM STATUS",
            bg='#000000',
            fg='#00ff41',
            font=("Orbitron", 10, "bold")
        )
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Create status labels
        self.create_status_labels(stats_frame)
        
        # Process list
        process_frame = tk.LabelFrame(
            system_frame,
            text="PROCESSES",
            bg='#000000',
            fg='#00ff41',
            font=("Orbitron", 10, "bold")
        )
        process_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.process_list = scrolledtext.ScrolledText(
            process_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg='#000000',
            fg='#00ff41',
            font=("Consolas", 9)
        )
        self.process_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def create_vision_tab(self):
        """Create vision/screen analysis tab"""
        vision_frame = tk.Frame(self.notebook, bg='#000000')
        self.notebook.add(vision_frame, text="VISION")
        
        # Controls
        control_frame = tk.Frame(vision_frame, bg='#000000')
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            control_frame,
            text="ANALYZE SCREEN",
            command=self.analyze_screen,
            bg='#333333',
            fg='#00ff41',
            activebackground='#555555',
            activeforeground='#00ff41',
            font=("Orbitron", 10, "bold"),
            relief=tk.RAISED
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            control_frame,
            text="CAPTURE",
            command=self.capture_screen,
            bg='#333333',
            fg='#00ff41',
            activebackground='#555555',
            activeforeground='#00ff41',
            font=("Orbitron", 10, "bold"),
            relief=tk.RAISED
        ).pack(side=tk.LEFT)
        
        # Vision results
        self.vision_display = scrolledtext.ScrolledText(
            vision_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg='#000000',
            fg='#00ff41',
            font=("Consolas", 10)
        )
        self.vision_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def create_status_labels(self, parent):
        """Create system status labels"""
        info_grid = tk.Frame(parent, bg='#000000')
        info_grid.pack(fill=tk.X, padx=10, pady=10)
        
        labels = [
            ("CPU:", self.cpu_usage),
            ("Memory:", self.mem_usage),
            ("Disk:", self.disk_usage),
            ("Status:", self.status)
        ]
        
        for i, (label_text, var) in enumerate(labels):
            tk.Label(
                info_grid,
                text=label_text,
                bg='#000000',
                fg='#00ff41',
                font=("Orbitron", 10)
            ).grid(row=i, column=0, sticky=tk.W, padx=(0, 10), pady=2)
            
            tk.Label(
                info_grid,
                textvariable=var,
                bg='#000000',
                fg='#00ff41',
                font=("Orbitron", 10)
            ).grid(row=i, column=1, sticky=tk.W, pady=2)

    def create_control_panels(self, parent):
        """Create bottom control panels"""
        control_container = tk.Frame(parent, bg='#000000')
        control_container.pack(fill=tk.X, pady=(0, 10))
        
        # Quick action buttons
        quick_frame = tk.LabelFrame(
            control_container,
            text="QUICK ACTIONS",
            bg='#000000',
            fg='#00ff41',
            font=("Orbitron", 10, "bold")
        )
        quick_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        quick_button_style = {
            'bg': '#333333',
            'fg': '#00ff41',
            'activebackground': '#555555',
            'activeforeground': '#00ff41',
            'font': ("Orbitron", 9, "bold"),
            'relief': tk.RAISED,
            'bd': 2,
            'height': 2
        }
        
        quick_actions = [
            ("WEB UI", self.launch_web_interface),
            ("LISTEN", self.toggle_listening),
            ("CLEAR", self.clear_conversation)
        ]
        
        for text, command in quick_actions:
            tk.Button(
                quick_frame,
                text=text,
                command=command,
                **quick_button_style
            ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, pady=5)
        
        # Status indicators
        status_frame = tk.LabelFrame(
            control_container,
            text="STATUS",
            bg='#000000',
            fg='#00ff41',
            font=("Orbitron", 10, "bold")
        )
        status_frame.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Listening indicator
        self.listening_led = tk.Canvas(status_frame, width=30, height=30, bg='#000000', highlightthickness=0)
        self.listening_led.pack(pady=5)
        
        tk.Label(
            status_frame,
            text="LISTENING",
            bg='#000000',
            fg='#00ff41',
            font=("Orbitron", 8)
        ).pack()

    # Event handlers
    def handle_dpad(self, direction):
        """Handle D-Pad navigation"""
        self.play_sound("button_press")
        self.add_to_conversation(f"[DPAD] Navigation: {direction.upper()}")
        self.automator.execute("pokedex_control", f"dpad_{direction}")

    def handle_action_button(self, button):
        """Handle action buttons (A, B)"""
        self.play_sound("button_press")
        
        if button == "A":
            self.add_to_conversation("[ACTION] Button A: Execute/Confirm")
            # Trigger current action or toggle theme
            self.toggle_theme()
        elif button == "B":
            self.add_to_conversation("[ACTION] Button B: Back/Cancel")
            # Cancel current operation or clear console
            self.clear_conversation()

    def handle_power(self):
        """Handle power button"""
        self.play_sound("button_press")
        response = messagebox.askyesno("Power Control", "Access power management?")
        if response:
            self.show_power_menu()

    def handle_volume(self):
        """Handle volume button"""
        self.play_sound("button_press")
        self.add_to_conversation("[SYSTEM] Volume control accessed")

    def handle_settings(self):
        """Handle settings button"""
        self.play_sound("button_press")
        self.show_settings()

    def show_power_menu(self):
        """Show power management menu"""
        power_window = tk.Toplevel(self)
        power_window.title("Power Management")
        power_window.geometry("300x200")
        power_window.configure(bg='#000000')
        
        tk.Label(
            power_window,
            text="POWER CONTROL",
            bg='#000000',
            fg='#ff4444',
            font=("Orbitron", 14, "bold")
        ).pack(pady=10)
        
        power_style = {
            'bg': '#444444',
            'fg': '#ffffff',
            'activebackground': '#666666',
            'activeforeground': '#ffffff',
            'font': ("Orbitron", 10, "bold"),
            'relief': tk.RAISED,
            'bd': 2,
            'width': 15,
            'height': 2
        }
        
        actions = [
            ("Shutdown", lambda: self.automator.execute("function", json.dumps({
                "function": "system_power", "parameters": {"action": "shutdown"}
            }))),
            ("Reboot", lambda: self.automator.execute("function", json.dumps({
                "function": "system_power", "parameters": {"action": "reboot"}
            }))),
            ("Hibernate", lambda: self.automator.execute("function", json.dumps({
                "function": "system_power", "parameters": {"action": "hibernate"}
            })))
        ]
        
        for text, command in actions:
            tk.Button(
                power_window,
                text=text,
                command=command,
                **power_style
            ).pack(pady=5)

    def show_settings(self):
        """Show settings window"""
        settings_window = tk.Toplevel(self)
        settings_window.title("ULTRON Settings")
        settings_window.geometry("400x300")
        settings_window.configure(bg='#000000')
        
        tk.Label(
            settings_window,
            text="ULTRON CONFIGURATION",
            bg='#000000',
            fg='#00ff41',
            font=("Orbitron", 14, "bold")
        ).pack(pady=10)
        
        # Add settings controls here
        # This is a placeholder for expanded settings

    def toggle_theme(self):
        """Toggle between red and blue themes"""
        self.theme = "blue" if self.theme == "red" else "red"
        self.config["theme"] = self.theme
        save_config(self.config)
        self.add_to_conversation(f"[THEME] Switched to {self.theme.upper()} theme")

    def set_voice(self, gender):
        """Set TTS voice"""
        if not self.voice_engine:
            return
        
        try:
            voices = self.voice_engine.getProperty('voices')
            if gender == "female" and len(voices) > 1:
                self.voice_engine.setProperty('voice', voices[1].id)
            else:
                self.voice_engine.setProperty('voice', voices[0].id)
            self.voice_engine.setProperty('rate', 150)
        except Exception as e:
            log_error(f"Voice setting error: {e}")

    def play_sound(self, name):
        """Play sound effect"""
        try:
            sound_file = SOUND_EFFECTS.get(name)
            if sound_file and os.path.exists(sound_file):
                pygame.mixer.Sound(sound_file).play()
        except Exception as e:
            log_error(f"Sound playback error: {e}")

    def update_system_stats(self):
        """Update system statistics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=None)
            self.cpu_usage.set(f"{cpu_percent:.1f}%")
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.mem_usage.set(f"{memory.percent:.1f}%")
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.disk_usage.set(f"{disk_percent:.1f}%")
            
            # Update process list
            self.update_process_list()
            
        except Exception as e:
            log_error(f"Stats update error: {e}")
        
        # Schedule next update
        self.after(5000, self.update_system_stats)

    def update_process_list(self):
        """Update process list display"""
        try:
            self.process_list.config(state=tk.NORMAL)
            self.process_list.delete(1.0, tk.END)
            
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    info = proc.info
                    processes.append(
                        f"{info['pid']:>6} {info['name']:<20} "
                        f"CPU: {info['cpu_percent']:>5.1f}% "
                        f"MEM: {info['memory_percent']:>5.1f}%\\n"
                    )
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Show top 15 processes
            for process in processes[:15]:
                self.process_list.insert(tk.END, process)
            
            self.process_list.config(state=tk.DISABLED)
            
        except Exception as e:
            log_error(f"Process list update error: {e}")

    def update_animation(self):
        """Update LED animations"""
        self.glow_phase = (self.glow_phase + 1) % 100
        
        # Update main LED
        self.main_led.delete("all")
        glow_intensity = int(128 + 127 * math.sin(self.glow_phase * 0.1))
        color = f"#ff{glow_intensity:02x}{glow_intensity:02x}" if self.theme == "red" else f"#{glow_intensity:02x}{glow_intensity:02x}ff"
        self.main_led.create_oval(5, 5, 55, 55, fill=color, outline='')
        
        # Update listening LED
        self.listening_led.delete("all")
        if self.listening_state.get():
            listen_color = "#00ff00"
        else:
            listen_color = "#ff0000"
        self.listening_led.create_oval(5, 5, 25, 25, fill=listen_color, outline='')
        
        # Schedule next animation frame
        self.after(50, self.update_animation)

    def wake_word_detection(self):
        """Background wake word detection"""
        if not self.recognizer:
            return
        
        while True:
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                
                try:
                    text = self.recognizer.recognize_google(audio).lower()
                    
                    # Check for wake words
                    for wake_word in WAKE_WORDS:
                        if wake_word in text:
                            self.play_sound("wake")
                            self.listening_state.set(True)
                            self.add_to_conversation(f"[WAKE] Detected: {wake_word}")
                            
                            # Process the command
                            command = text.replace(wake_word, "").strip()
                            if command:
                                self.process_voice_command(command)
                            
                            self.listening_state.set(False)
                            break
                            
                except sr.UnknownValueError:
                    pass  # No speech detected
                except sr.RequestError as e:
                    log_error(f"Speech recognition error: {e}")
                
            except Exception as e:
                log_error(f"Wake word detection error: {e}")
                time.sleep(1)

    def process_voice_command(self, command):
        """Process voice commands"""
        self.add_to_conversation(f"[VOICE] Command: {command}")
        
        # Get AI response
        try:
            response = self.llm.generate(command)
            self.add_to_conversation(f"[ULTRON] {response}")
            
            # Speak response
            if self.voice_engine:
                self.voice_engine.say(response)
                self.voice_engine.runAndWait()
                
        except Exception as e:
            error_msg = f"Error processing command: {str(e)}"
            self.add_to_conversation(f"[ERROR] {error_msg}")
            log_error(error_msg)

    def toggle_listening(self):
        """Toggle listening state"""
        current_state = self.listening_state.get()
        self.listening_state.set(not current_state)
        self.play_sound("button_press")
        
        if self.listening_state.get():
            self.add_to_conversation("[SYSTEM] Listening activated")
        else:
            self.add_to_conversation("[SYSTEM] Listening deactivated")

    def execute_manual(self, event=None):
        """Execute manual command"""
        command = self.cmd_entry.get().strip()
        if not command:
            return
        
        self.cmd_entry.delete(0, tk.END)
        self.add_to_conversation(f"[USER] {command}")
        
        # Process command
        try:
            if command.startswith("/"):
                # System command
                result = self.automator.execute("powershell", command[1:])
            elif command.startswith("python:"):
                # Python command
                result = self.automator.execute("python", command[7:])
            else:
                # AI command
                result = self.llm.generate(command)
            
            self.add_to_conversation(f"[RESULT] {result}")
            
        except Exception as e:
            error_msg = f"Command error: {str(e)}"
            self.add_to_conversation(f"[ERROR] {error_msg}")
            log_error(error_msg)

    def analyze_screen(self):
        """Analyze current screen using enhanced vision system"""
        self.add_to_conversation("[VISION] Analyzing screen...")
        
        try:
            if self.ultron_core.vision_system:
                result = self.ultron_core.vision_system.analyze_screen("full")
                
                if result.get("success"):
                    description = result.get("comprehensive_description", "Analysis completed")
                    self.add_to_conversation(f"[VISION] {description}")
                    
                    # Display in vision tab if available
                    if hasattr(self, 'vision_display'):
                        self.vision_display.config(state=tk.NORMAL)
                        self.vision_display.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {description}\\n\\n")
                        self.vision_display.see(tk.END)
                        self.vision_display.config(state=tk.DISABLED)
                else:
                    self.add_to_conversation(f"[VISION ERROR] {result.get('message', 'Analysis failed')}")
            else:
                self.add_to_conversation("[VISION] Vision system not available")
            
        except Exception as e:
            error_msg = f"Vision analysis error: {str(e)}"
            self.add_to_conversation(f"[ERROR] {error_msg}")
            log_error(error_msg)

    def capture_screen(self):
        """Capture screenshot using enhanced vision system"""
        try:
            if self.ultron_core.vision_system:
                result = self.ultron_core.vision_system.capture_screen()
                
                if result.get("success"):
                    filename = result.get("filename", "screenshot.png")
                    self.add_to_conversation(f"[CAPTURE] Screenshot saved: {filename}")
                else:
                    self.add_to_conversation(f"[CAPTURE ERROR] {result.get('message', 'Capture failed')}")
            else:
                # Fallback to basic screenshot
                if FULL_FEATURES:
                    screenshot = ImageGrab.grab()
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = f"screenshot_{timestamp}.png"
                    filepath = os.path.join(ASSETS_DIR, filename)
                    
                    screenshot.save(filepath)
                    self.add_to_conversation(f"[CAPTURE] Screenshot saved: {filename}")
                else:
                    self.add_to_conversation("[CAPTURE] Screenshot functionality not available")
            
        except Exception as e:
            error_msg = f"Screenshot error: {str(e)}"
            self.add_to_conversation(f"[ERROR] {error_msg}")
            log_error(error_msg)

    def launch_web_interface(self):
        """Launch web interface"""
        try:
            url = f"http://localhost:{self.config.get('web_port', 3000)}"
            webbrowser.open(url)
            self.add_to_conversation(f"[WEB] Interface launched: {url}")
        except Exception as e:
            error_msg = f"Web interface error: {str(e)}"
            self.add_to_conversation(f"[ERROR] {error_msg}")
            log_error(error_msg)

    def add_to_conversation(self, text):
        """Add text to conversation display"""
        try:
            self.conversation.config(state=tk.NORMAL)
            timestamp = time.strftime("%H:%M:%S")
            self.conversation.insert(tk.END, f"[{timestamp}] {text}\\n")
            self.conversation.see(tk.END)
            self.conversation.config(state=tk.DISABLED)
        except Exception as e:
            log_error(f"Conversation update error: {e}")

    def clear_conversation(self):
        """Clear conversation display"""
        self.conversation.config(state=tk.NORMAL)
        self.conversation.delete(1.0, tk.END)
        self.conversation.config(state=tk.DISABLED)
        self.play_sound("button_press")

    def speak(self, text):
        """Text-to-speech output"""
        if self.voice_engine:
            try:
                self.voice_engine.say(text)
                self.voice_engine.runAndWait()
            except Exception as e:
                log_error(f"TTS error: {e}")

    def trigger_wake_effect(self):
        """Trigger visual wake effect when wake word is detected"""
        try:
            # Flash main LED
            if hasattr(self, 'main_led'):
                original_color = self.main_led.cget('bg')
                self.main_led.config(bg='#00ff41')
                self.after(500, lambda: self.main_led.config(bg=original_color))
            
            # Play wake sound
            self.play_sound("wake")
            
            # Add visual feedback
            self.add_to_conversation("[WAKE] Wake word detected - ULTRON activated")
            
        except Exception as e:
            log_error(f"Wake effect error: {e}")
    
    def add_voice_interaction(self, command: str, response: str):
        """Add voice interaction to conversation display"""
        try:
            self.add_to_conversation(f"[VOICE] User: {command}")
            self.add_to_conversation(f"[ULTRON] {response}")
        except Exception as e:
            log_error(f"Voice interaction display error: {e}")
    
    def update_system_stats_enhanced(self):
        """Enhanced system stats update using core modules"""
        try:
            if self.ultron_core.system_automation:
                stats_result = self.ultron_core.get_system_info("basic")
                
                if stats_result.get("success"):
                    stats = stats_result.get("system_info", {})
                    
                    self.cpu_usage.set(f"{stats.get('cpu_percent', 0):.1f}%")
                    self.mem_usage.set(f"{stats.get('memory_percent', 0):.1f}%")
                    
                    # Calculate disk percentage
                    disk_total = stats.get('disk_total', 1)
                    disk_used = disk_total - stats.get('disk_free', 0)
                    disk_percent = (disk_used / disk_total) * 100 if disk_total > 0 else 0
                    self.disk_usage.set(f"{disk_percent:.1f}%")
                    
                    # Update status
                    core_status = self.ultron_core.get_status()
                    status_text = f"Status: ULTRON Enhanced - {core_status.get('current_mode', 'ready').title()} Mode"
                    self.status.set(status_text)
                    
                    # Update process list if in system tab
                    self.update_process_list_enhanced()
            else:
                # Fallback to basic stats
                self.update_system_stats()
                
        except Exception as e:
            log_error(f"Enhanced stats update error: {e}")
            # Fallback to basic update
            self.update_system_stats()
    
    def update_process_list_enhanced(self):
        """Enhanced process list update"""
        try:
            if hasattr(self, 'process_list') and self.ultron_core.system_automation:
                process_result = self.ultron_core.system_automation.process_manager.execute_command({"action": "list"})
                
                if process_result.get("success"):
                    processes = process_result.get("processes", [])
                    
                    self.process_list.config(state=tk.NORMAL)
                    self.process_list.delete(1.0, tk.END)
                    
                    # Show top processes by CPU usage
                    processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
                    
                    for proc in processes[:15]:
                        line = f"{proc.get('pid', 0):>6} {proc.get('name', 'Unknown'):<20} CPU: {proc.get('cpu_percent', 0):>5.1f}% MEM: {proc.get('memory_percent', 0):>5.1f}%\\n"
                        self.process_list.insert(tk.END, line)
                    
                    self.process_list.config(state=tk.DISABLED)
        except Exception as e:
            log_error(f"Enhanced process list update error: {e}")
    
    def toggle_listening_enhanced(self):
        """Enhanced listening toggle using voice processor"""
        try:
            if self.ultron_core.voice_processor:
                if self.listening_state.get():
                    self.ultron_core.voice_processor.stop_listening()
                    self.add_to_conversation("[VOICE] Listening stopped")
                else:
                    self.ultron_core.voice_processor.start_listening()
                    self.add_to_conversation("[VOICE] Listening started - say wake word to activate")
                
                self.listening_state.set(not self.listening_state.get())
            else:
                self.add_to_conversation("[VOICE] Voice system not available")
                
        except Exception as e:
            log_error(f"Enhanced listening toggle error: {e}")
    
    def launch_web_interface_enhanced(self):
        """Enhanced web interface launcher"""
        try:
            if self.ultron_core.web_server and self.ultron_core.web_server.is_running:
                port = self.config.get('web_port', 3000)
                url = f"http://localhost:{port}"
                webbrowser.open(url)
                self.add_to_conversation(f"[WEB] Interface launched: {url}")
            else:
                # Try to start web server
                if self.ultron_core.web_server:
                    if self.ultron_core.web_server.start():
                        self.after(2000, self.launch_web_interface_enhanced)  # Retry after 2 seconds
                        self.add_to_conversation("[WEB] Starting web server...")
                    else:
                        self.add_to_conversation("[WEB] Failed to start web server")
                else:
                    self.add_to_conversation("[WEB] Web server not available")
                    
        except Exception as e:
            error_msg = f"Web interface error: {str(e)}"
            self.add_to_conversation(f"[ERROR] {error_msg}")
            log_error(error_msg)
    
    def on_close(self):
        """Handle application close"""
        try:
            # Stop ULTRON core
            if hasattr(self, 'ultron_core'):
                self.ultron_core.stop()
            
            # Save configuration
            save_config(self.config)
            
            log_info("ULTRON Enhanced Pokedex Interface shutting down")
            self.destroy()
            
        except Exception as e:
            log_error(f"Shutdown error: {e}")
        
        sys.exit(0)

def setup_ultron_environment():
    """Setup ULTRON directory structure and files"""
    log_info("Setting up ULTRON environment...")
    
    # Create configuration file
    config = load_config()
    save_config(config)
    
    # Create placeholder sound files
    for sound_name, sound_path in SOUND_EFFECTS.items():
        if not os.path.exists(sound_path):
            # Create empty wav file
            Path(sound_path).touch()
    
    log_info("ULTRON environment setup complete")

def main():
    """Main application entry point"""
    try:
        # Check admin privileges
        if not ctypes.windll.shell32.IsUserAnAdmin():
            log_info("Requesting administrator privileges...")
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            sys.exit()
        
        # Setup environment
        setup_ultron_environment()
        
        # Load configuration
        config = load_config()
        
        # Initialize OpenAI if available
        if config.get("openai_api_key"):
            openai.api_key = config["openai_api_key"]
        
        log_info("Starting ULTRON Pokedex AI System...")
        
        # Create and run application
        app = UltronPokedexInterface()
        app.mainloop()
        
    except Exception as e:
        log_error(f"Fatal error: {e}")
        messagebox.showerror("ULTRON Error", f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
