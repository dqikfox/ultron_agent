#!/usr/bin/env python3
"""
ULTRON - Complete AI Assistant with Pokedex-Style Interface
Combined system with your original script + Pokedex styling + Local AI
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
import speech_recognition as sr
import pyttsx3
import pygame
from PIL import Image, ImageTk, ImageGrab
import numpy as np
import logging
import webbrowser
from pathlib import Path
import asyncio
import ctypes

# Enhanced configuration for D:\ULTRON structure
ULTRON_ROOT = r"D:\ULTRON"
CONFIG_PATH = os.path.join(ULTRON_ROOT, "config.json")
MODEL_DIR = os.path.join(ULTRON_ROOT, "models")
CORE_DIR = os.path.join(ULTRON_ROOT, "core")
ASSETS_DIR = os.path.join(ULTRON_ROOT, "assets")
LOG_DIR = os.path.join(ULTRON_ROOT, "logs")
WEB_DIR = os.path.join(ULTRON_ROOT, "web")
WAKE_WORDS = ["ultron", "hello", "speak", "ultra"]

# Create directories if missing
for directory in [ULTRON_ROOT, MODEL_DIR, CORE_DIR, ASSETS_DIR, LOG_DIR, WEB_DIR]:
    os.makedirs(directory, exist_ok=True)

# Setup logging
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "ultron.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_info(message):
    logging.info(message)
    print(f"[ULTRON] {message}")

def log_error(message):
    logging.error(message)
    print(f"[ERROR] {message}")

class LocalAIBrain:
    """Local AI processing with fallback responses"""
    
    def __init__(self, config):
        self.config = config
        self.responses = {
            "greeting": ["Hello! ULTRON systems online.", "Systems ready for commands.", "ULTRON at your service."],
            "status": ["All systems operational.", "Running optimally.", "Systems green across the board."],
            "error": ["Command not recognized.", "Unable to process request.", "Please rephrase command."],
            "shutdown": ["Initiating shutdown sequence.", "Powering down systems.", "ULTRON offline."]
        }
        
    def process_command(self, command):
        """Process voice/text commands with local intelligence"""
        command = command.lower().strip()
        
        if any(word in command for word in ["hello", "hi", "hey", "wake"]):
            return np.random.choice(self.responses["greeting"])
        
        elif any(word in command for word in ["status", "report", "health"]):
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            return f"System status: CPU {cpu}%, Memory {memory}%. {np.random.choice(self.responses['status'])}"
        
        elif any(word in command for word in ["shutdown", "power off", "exit"]):
            return np.random.choice(self.responses["shutdown"])
        
        elif "screenshot" in command:
            return self.take_screenshot()
        
        elif "open browser" in command:
            webbrowser.open("https://google.com")
            return "Browser opened."
        
        elif any(word in command for word in ["time", "date"]):
            return f"Current time: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        
        else:
            return f"Processing: {command}. {np.random.choice(self.responses['error'])}"
    
    def take_screenshot(self):
        """Take and save screenshot"""
        try:
            screenshot = ImageGrab.grab()
            screenshot_path = os.path.join(ASSETS_DIR, f"screenshot_{int(time.time())}.png")
            screenshot.save(screenshot_path)
            return f"Screenshot saved to {screenshot_path}"
        except Exception as e:
            return f"Screenshot failed: {str(e)}"

class PokedexStyleUI:
    """Pokedex-inspired UI for ULTRON"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ULTRON - AI Assistant")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a2e')
        
        # Initialize components
        self.config = self.load_config()
        self.ai_brain = LocalAIBrain(self.config)
        self.voice_engine = self.init_voice()
        self.listening = False
        
        # Initialize voice recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # UI State
        self.conversation_history = []
        
        self.create_pokedex_ui()
        self.start_background_tasks()
        
    def load_config(self):
        """Load or create configuration"""
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                return json.load(f)
        
        default_config = {
            "voice": {"enabled": True, "rate": 150, "volume": 0.9},
            "ai": {"local_mode": True, "api_key": ""},
            "interface": {"theme": "pokedex", "animations": True},
            "system": {"auto_screenshot": False, "log_conversations": True}
        }
        
        with open(CONFIG_PATH, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def init_voice(self):
        """Initialize text-to-speech"""
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', self.config.get('voice', {}).get('rate', 150))
            engine.setProperty('volume', self.config.get('voice', {}).get('volume', 0.9))
            return engine
        except Exception as e:
            log_error(f"Voice engine init failed: {e}")
            return None
    
    def create_pokedex_ui(self):
        """Create Pokedex-style interface"""
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top section - Pokedex screen style
        top_frame = tk.Frame(main_frame, bg='#e74c3c', relief=tk.RAISED, bd=3)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # ULTRON title with glow effect
        title_frame = tk.Frame(top_frame, bg='#2c3e50')
        title_frame.pack(fill=tk.X, padx=5, pady=5)
        
        title_label = tk.Label(
            title_frame, 
            text="ULTRON v2.0", 
            font=("Orbitron", 24, "bold"),
            fg='#00ff41', 
            bg='#2c3e50'
        )
        title_label.pack()
        
        status_label = tk.Label(
            title_frame,
            text="AI Assistant - Online",
            font=("Courier", 12),
            fg='#3498db',
            bg='#2c3e50'
        )
        status_label.pack()
        
        # Middle section - Main display
        middle_frame = tk.Frame(main_frame, bg='#16213e')
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Left panel - System status
        left_panel = tk.Frame(middle_frame, bg='#2c3e50', width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        self.create_status_panel(left_panel)
        
        # Center panel - Conversation
        center_panel = tk.Frame(middle_frame, bg='#34495e')
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.create_conversation_panel(center_panel)
        
        # Right panel - Controls
        right_panel = tk.Frame(middle_frame, bg='#2c3e50', width=300)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)
        
        self.create_control_panel(right_panel)
        
        # Bottom section - Command input
        bottom_frame = tk.Frame(main_frame, bg='#e67e22', relief=tk.RAISED, bd=3)
        bottom_frame.pack(fill=tk.X)
        
        self.create_input_panel(bottom_frame)
    
    def create_status_panel(self, parent):
        """Create system status panel"""
        tk.Label(
            parent, 
            text="SYSTEM STATUS", 
            font=("Orbitron", 14, "bold"),
            fg='#00ff41', 
            bg='#2c3e50'
        ).pack(pady=10)
        
        # Status indicators
        self.status_vars = {
            'cpu': tk.StringVar(value="CPU: 0%"),
            'memory': tk.StringVar(value="Memory: 0%"),
            'disk': tk.StringVar(value="Disk: 0%"),
            'voice': tk.StringVar(value="Voice: Ready"),
            'ai': tk.StringVar(value="AI: Online")
        }
        
        for key, var in self.status_vars.items():
            frame = tk.Frame(parent, bg='#2c3e50')
            frame.pack(fill=tk.X, padx=10, pady=2)
            
            tk.Label(
                frame,
                textvariable=var,
                font=("Courier", 10),
                fg='#3498db',
                bg='#2c3e50',
                anchor='w'
            ).pack(side=tk.LEFT)
        
        # System controls
        tk.Label(
            parent, 
            text="QUICK ACTIONS", 
            font=("Orbitron", 12, "bold"),
            fg='#00ff41', 
            bg='#2c3e50'
        ).pack(pady=(20, 10))
        
        actions = [
            ("Screenshot", self.take_screenshot),
            ("System Info", self.show_system_info),
            ("Open Browser", lambda: webbrowser.open("https://google.com")),
            ("File Manager", self.open_file_manager)
        ]
        
        for text, command in actions:
            btn = tk.Button(
                parent,
                text=text,
                command=command,
                bg='#3498db',
                fg='white',
                font=("Courier", 10, "bold"),
                relief=tk.FLAT,
                padx=10,
                pady=5
            )
            btn.pack(fill=tk.X, padx=10, pady=2)
    
    def create_conversation_panel(self, parent):
        """Create conversation display panel"""
        tk.Label(
            parent, 
            text="CONVERSATION LOG", 
            font=("Orbitron", 14, "bold"),
            fg='#00ff41', 
            bg='#34495e'
        ).pack(pady=10)
        
        # Conversation display
        self.conversation_text = scrolledtext.ScrolledText(
            parent,
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg='#2c3e50',
            fg='#ecf0f1',
            font=("Courier", 11),
            insertbackground='#3498db'
        )
        self.conversation_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure text tags for styling
        self.conversation_text.tag_configure("user", foreground="#3498db")
        self.conversation_text.tag_configure("ultron", foreground="#00ff41")
        self.conversation_text.tag_configure("system", foreground="#e67e22")
        
        self.add_to_conversation("ULTRON", "ULTRON AI Assistant initialized. Ready for commands.")
    
    def create_control_panel(self, parent):
        """Create control panel"""
        tk.Label(
            parent, 
            text="VOICE CONTROLS", 
            font=("Orbitron", 14, "bold"),
            fg='#00ff41', 
            bg='#2c3e50'
        ).pack(pady=10)
        
        # Voice control buttons
        self.voice_btn = tk.Button(
            parent,
            text="🎤 Start Listening",
            command=self.toggle_listening,
            bg='#27ae60',
            fg='white',
            font=("Courier", 12, "bold"),
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.voice_btn.pack(fill=tk.X, padx=10, pady=5)
        
        # Configuration
        tk.Label(
            parent, 
            text="CONFIGURATION", 
            font=("Orbitron", 12, "bold"),
            fg='#00ff41', 
            bg='#2c3e50'
        ).pack(pady=(20, 10))
        
        # Voice settings
        voice_frame = tk.Frame(parent, bg='#2c3e50')
        voice_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(voice_frame, text="Voice Rate:", bg='#2c3e50', fg='#ecf0f1').pack(anchor='w')
        self.voice_rate = tk.Scale(
            voice_frame, 
            from_=50, to=300, 
            orient=tk.HORIZONTAL,
            bg='#2c3e50', 
            fg='#ecf0f1',
            highlightthickness=0
        )
        self.voice_rate.set(150)
        self.voice_rate.pack(fill=tk.X)
        
        # Save config button
        tk.Button(
            parent,
            text="Save Config",
            command=self.save_config,
            bg='#8e44ad',
            fg='white',
            font=("Courier", 10, "bold"),
            relief=tk.FLAT
        ).pack(fill=tk.X, padx=10, pady=10)
    
    def create_input_panel(self, parent):
        """Create command input panel"""
        input_frame = tk.Frame(parent, bg='#e67e22')
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            input_frame,
            text="Command Input:",
            font=("Orbitron", 12, "bold"),
            bg='#e67e22',
            fg='white'
        ).pack(anchor='w')
        
        entry_frame = tk.Frame(input_frame, bg='#e67e22')
        entry_frame.pack(fill=tk.X, pady=5)
        
        self.command_entry = tk.Entry(
            entry_frame,
            font=("Courier", 12),
            bg='#2c3e50',
            fg='#ecf0f1',
            insertbackground='#3498db',
            relief=tk.FLAT
        )
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.command_entry.bind('<Return>', self.process_text_command)
        
        tk.Button(
            entry_frame,
            text="Execute",
            command=self.process_text_command,
            bg='#27ae60',
            fg='white',
            font=("Courier", 10, "bold"),
            relief=tk.FLAT,
            padx=20
        ).pack(side=tk.RIGHT)
    
    def add_to_conversation(self, speaker, message):
        """Add message to conversation log"""
        self.conversation_text.config(state=tk.NORMAL)
        
        timestamp = time.strftime("%H:%M:%S")
        
        if speaker == "ULTRON":
            tag = "ultron"
        elif speaker == "USER":
            tag = "user"
        else:
            tag = "system"
        
        self.conversation_text.insert(tk.END, f"[{timestamp}] {speaker}: ", tag)
        self.conversation_text.insert(tk.END, f"{message}\n\n")
        self.conversation_text.config(state=tk.DISABLED)
        self.conversation_text.see(tk.END)
        
        # Save to history
        self.conversation_history.append({
            'timestamp': timestamp,
            'speaker': speaker,
            'message': message
        })
    
    def process_text_command(self, event=None):
        """Process text command"""
        command = self.command_entry.get().strip()
        if not command:
            return
        
        self.add_to_conversation("USER", command)
        self.command_entry.delete(0, tk.END)
        
        # Process with AI brain
        response = self.ai_brain.process_command(command)
        self.add_to_conversation("ULTRON", response)
        
        # Speak response if voice enabled
        if self.voice_engine and self.config.get('voice', {}).get('enabled', True):
            threading.Thread(target=self.speak, args=(response,), daemon=True).start()
    
    def toggle_listening(self):
        """Toggle voice listening"""
        if not self.listening:
            self.listening = True
            self.voice_btn.config(text="🛑 Stop Listening", bg='#e74c3c')
            threading.Thread(target=self.listen_for_voice, daemon=True).start()
        else:
            self.listening = False
            self.voice_btn.config(text="🎤 Start Listening", bg='#27ae60')
    
    def listen_for_voice(self):
        """Listen for voice commands"""
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            while self.listening:
                try:
                    with self.microphone as source:
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    
                    command = self.recognizer.recognize_google(audio)
                    
                    if any(wake_word in command.lower() for wake_word in WAKE_WORDS):
                        self.root.after(0, self.process_voice_command, command)
                        
                except sr.WaitTimeoutError:
                    pass
                except sr.UnknownValueError:
                    pass
                except Exception as e:
                    log_error(f"Voice recognition error: {e}")
                    
        except Exception as e:
            log_error(f"Voice listening error: {e}")
            self.listening = False
            self.voice_btn.config(text="🎤 Start Listening", bg='#27ae60')
    
    def process_voice_command(self, command):
        """Process voice command"""
        self.add_to_conversation("USER", f"🎤 {command}")
        
        response = self.ai_brain.process_command(command)
        self.add_to_conversation("ULTRON", response)
        
        if self.voice_engine:
            threading.Thread(target=self.speak, args=(response,), daemon=True).start()
    
    def speak(self, text):
        """Text-to-speech"""
        if self.voice_engine:
            try:
                self.voice_engine.say(text)
                self.voice_engine.runAndWait()
            except Exception as e:
                log_error(f"Speech error: {e}")
    
    def update_system_status(self):
        """Update system status display"""
        try:
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent
            
            self.status_vars['cpu'].set(f"CPU: {cpu:.1f}%")
            self.status_vars['memory'].set(f"Memory: {memory:.1f}%")
            self.status_vars['disk'].set(f"Disk: {disk:.1f}%")
            self.status_vars['voice'].set(f"Voice: {'Active' if self.listening else 'Ready'}")
            
        except Exception as e:
            log_error(f"Status update error: {e}")
    
    def take_screenshot(self):
        """Take screenshot"""
        try:
            screenshot = ImageGrab.grab()
            timestamp = int(time.time())
            screenshot_path = os.path.join(ASSETS_DIR, f"screenshot_{timestamp}.png")
            screenshot.save(screenshot_path)
            self.add_to_conversation("SYSTEM", f"Screenshot saved: {screenshot_path}")
        except Exception as e:
            self.add_to_conversation("SYSTEM", f"Screenshot failed: {str(e)}")
    
    def show_system_info(self):
        """Show system information"""
        info = {
            "Platform": os.name,
            "CPU Count": psutil.cpu_count(),
            "Total Memory": f"{psutil.virtual_memory().total / (1024**3):.1f} GB",
            "Python Version": sys.version.split()[0],
            "ULTRON Version": "2.0"
        }
        
        info_text = "\n".join([f"{k}: {v}" for k, v in info.items()])
        self.add_to_conversation("SYSTEM", f"System Information:\n{info_text}")
    
    def open_file_manager(self):
        """Open file manager"""
        try:
            if os.name == 'nt':
                os.startfile(ULTRON_ROOT)
            else:
                subprocess.Popen(['xdg-open', ULTRON_ROOT])
            self.add_to_conversation("SYSTEM", f"File manager opened: {ULTRON_ROOT}")
        except Exception as e:
            self.add_to_conversation("SYSTEM", f"Failed to open file manager: {str(e)}")
    
    def save_config(self):
        """Save current configuration"""
        self.config['voice']['rate'] = self.voice_rate.get()
        
        with open(CONFIG_PATH, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        self.add_to_conversation("SYSTEM", "Configuration saved.")
        
        if self.voice_engine:
            self.voice_engine.setProperty('rate', self.config['voice']['rate'])
    
    def start_background_tasks(self):
        """Start background monitoring tasks"""
        def update_loop():
            while True:
                self.root.after(0, self.update_system_status)
                time.sleep(2)
        
        threading.Thread(target=update_loop, daemon=True).start()
    
    def run(self):
        """Start the application"""
        log_info("ULTRON Pokedex UI starting...")
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            log_info("ULTRON shutting down...")
        except Exception as e:
            log_error(f"Application error: {e}")

def check_admin():
    """Check if running with admin privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main():
    """Main entry point"""
    print("🤖 ULTRON - AI Assistant with Pokedex Interface")
    print("=" * 50)
    
    if not check_admin():
        print("⚠️ Warning: Not running with admin privileges")
        print("Some system functions may be limited")
    
    try:
        app = PokedexStyleUI()
        app.run()
    except Exception as e:
        log_error(f"Startup error: {e}")
        print(f"Error starting ULTRON: {e}")

if __name__ == "__main__":
    main()
