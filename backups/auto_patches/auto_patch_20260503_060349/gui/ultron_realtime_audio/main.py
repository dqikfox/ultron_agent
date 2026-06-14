#!/usr/bin/env python3
"""
ULTRON - Real-Time Audio AI Assistant
Enhanced with continuous audio streaming and instant voice response
"""

import os
import sys
import json
import time
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import queue
import psutil
import numpy as np
import sounddevice as sd
import speech_recognition as sr
import pyttsx3
import pygame
from PIL import Image, ImageTk, ImageGrab
import logging
import webbrowser
from pathlib import Path
import asyncio
import ctypes
import webrtcvad
import collections
import wave
import io

# Enhanced configuration for D:\ULTRON structure
ULTRON_ROOT = r"D:\ULTRON"
CONFIG_PATH = os.path.join(ULTRON_ROOT, "config.json")
MODEL_DIR = os.path.join(ULTRON_ROOT, "models")
CORE_DIR = os.path.join(ULTRON_ROOT, "core")
ASSETS_DIR = os.path.join(ULTRON_ROOT, "assets")
LOG_DIR = os.path.join(ULTRON_ROOT, "logs")
WEB_DIR = os.path.join(ULTRON_ROOT, "web")

# Real-time audio settings
SAMPLE_RATE = 16000
CHUNK_DURATION_MS = 30  # Duration of each audio chunk in ms
CHUNK_SIZE = int(SAMPLE_RATE * CHUNK_DURATION_MS / 1000)
WAKE_WORDS = ["ultron", "hello", "speak", "ultra", "hey ultron"]

# Create directories if missing
for directory in [ULTRON_ROOT, MODEL_DIR, CORE_DIR, ASSETS_DIR, LOG_DIR, WEB_DIR]:
    os.makedirs(directory, exist_ok=True)

# Setup logging
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "ultron_realtime.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_info(message):
    logging.info(message)
    print(f"[ULTRON] {message}")

def log_error(message):
    logging.error(message)
    print(f"[ERROR] {message}")

class RealTimeAudioProcessor:
    """Real-time audio processing with voice activity detection"""
    
    def __init__(self, callback=None):
        self.callback = callback
        self.is_running = False
        self.audio_queue = queue.Queue()
        self.vad = webrtcvad.Vad(2)  # Aggressiveness level 0-3
        self.sample_rate = SAMPLE_RATE
        self.frame_duration = CHUNK_DURATION_MS
        self.frame_size = CHUNK_SIZE
        
        # Voice activity detection
        self.ring_buffer = collections.deque(maxlen=50)  # Buffer for voice detection
        self.triggered = False
        self.voiced_frames = []
        self.silence_threshold = 20  # Frames of silence before stopping
        
        # Speech recognition
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
    def start_stream(self):
        """Start real-time audio stream"""
        self.is_running = True
        
        def audio_callback(indata, frames, time, status):
            if status:
                log_error(f"Audio callback status: {status}")
            
            # Convert to int16 and add to queue
            audio_data = (indata[:, 0] * 32767).astype(np.int16)
            self.audio_queue.put(audio_data.tobytes())
        
        try:
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.float32,
                blocksize=self.frame_size,
                callback=audio_callback
            )
            self.stream.start()
            
            # Start processing thread
            self.processing_thread = threading.Thread(target=self._process_audio_stream, daemon=True)
            self.processing_thread.start()
            
            log_info("Real-time audio stream started")
            return True
            
        except Exception as e:
            log_error(f"Failed to start audio stream: {e}")
            return False
    
    def stop_stream(self):
        """Stop audio stream"""
        self.is_running = False
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
        log_info("Audio stream stopped")
    
    def _process_audio_stream(self):
        """Process incoming audio stream for voice activity"""
        while self.is_running:
            try:
                if not self.audio_queue.empty():
                    audio_chunk = self.audio_queue.get()
                    
                    # Voice activity detection
                    is_speech = self.vad.is_speech(audio_chunk, self.sample_rate)
                    
                    self.ring_buffer.append((audio_chunk, is_speech))
                    
                    if not self.triggered:
                        # Check if we should start recording
                        num_voiced = len([f for f, speech in self.ring_buffer if speech])
                        if num_voiced > 0.5 * self.ring_buffer.maxlen:
                            self.triggered = True
                            self.voiced_frames = [f for f, s in self.ring_buffer]
                            self.ring_buffer.clear()
                            if self.callback:
                                self.callback("voice_detected", None)
                    else:
                        # We're recording, collect frames
                        self.voiced_frames.append(audio_chunk)
                        
                        # Check if we should stop recording
                        if not is_speech:
                            self.silence_threshold -= 1
                        else:
                            self.silence_threshold = 20
                        
                        if self.silence_threshold <= 0:
                            # Process the collected audio
                            self._process_voice_command()
                            self.triggered = False
                            self.silence_threshold = 20
                            self.voiced_frames = []
                
                time.sleep(0.01)  # Small delay to prevent excessive CPU usage
                
            except Exception as e:
                log_error(f"Audio processing error: {e}")
    
    def _process_voice_command(self):
        """Process collected voice frames as a command"""
        try:
            # Combine all voice frames
            audio_data = b''.join(self.voiced_frames)
            
            # Convert to AudioData for speech recognition
            audio_io = io.BytesIO()
            with wave.open(audio_io, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(audio_data)
            
            audio_io.seek(0)
            
            # Create AudioData object
            with sr.AudioFile(audio_io) as source:
                audio = self.recognizer.record(source)
            
            # Recognize speech
            try:
                command = self.recognizer.recognize_google(audio, language='en-US')
                log_info(f"Voice command detected: {command}")
                
                if self.callback:
                    self.callback("command_recognized", command)
                    
            except sr.UnknownValueError:
                log_info("Voice detected but no speech recognized")
            except sr.RequestError as e:
                log_error(f"Speech recognition error: {e}")
                
        except Exception as e:
            log_error(f"Voice command processing error: {e}")

class EnhancedLocalAI:
    """Enhanced local AI with better response patterns"""
    
    def __init__(self, config):
        self.config = config
        self.conversation_context = []
        self.responses = {
            "greeting": [
                "Hello! ULTRON real-time systems online and ready.",
                "ULTRON here. All systems operational. How can I assist?",
                "Real-time audio processing active. What do you need?",
                "ULTRON AI ready. Voice recognition working perfectly."
            ],
            "status": [
                "All systems green. Real-time audio operational.",
                "Running optimally with live voice processing.",
                "Systems nominal. Voice recognition active.",
                "Operating at full capacity with real-time capabilities."
            ],
            "voice_confirmed": [
                "Voice command received and processed.",
                "I hear you clearly.",
                "Real-time audio processing working.",
                "Voice input confirmed."
            ],
            "error": [
                "Command not fully recognized. Please repeat.",
                "Audio unclear. Could you say that again?",
                "Please rephrase your command.",
                "I didn't catch that clearly."
            ]
        }
        
    def process_command(self, command):
        """Process voice/text commands with context awareness"""
        command = command.lower().strip()
        
        # Add to conversation context
        self.conversation_context.append(command)
        if len(self.conversation_context) > 10:
            self.conversation_context.pop(0)
        
        # Wake word detection
        if any(wake_word in command for wake_word in WAKE_WORDS):
            # Extract command after wake word
            for wake_word in WAKE_WORDS:
                if wake_word in command:
                    command = command.replace(wake_word, "").strip()
                    break
            
            if not command:
                return np.random.choice(self.responses["greeting"])
        
        # Command processing
        if any(word in command for word in ["hello", "hi", "hey", "greetings"]):
            return np.random.choice(self.responses["greeting"])
        
        elif any(word in command for word in ["status", "report", "health", "how are you"]):
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            return f"System status: CPU {cpu}%, Memory {memory}%. {np.random.choice(self.responses['status'])}"
        
        elif any(word in command for word in ["can you hear me", "voice test", "audio test"]):
            return np.random.choice(self.responses["voice_confirmed"])
        
        elif "screenshot" in command or "capture screen" in command:
            return self.take_screenshot()
        
        elif "open browser" in command or "web browser" in command:
            webbrowser.open("https://google.com")
            return "Opening web browser now."
        
        elif any(word in command for word in ["time", "date", "clock"]):
            current_time = time.strftime('%Y-%m-%d %H:%M:%S')
            return f"Current time: {current_time}"
        
        elif any(word in command for word in ["shutdown", "power off", "exit", "quit"]):
            return "Initiating shutdown sequence. ULTRON systems powering down."
        
        elif "search" in command:
            search_term = command.replace("search", "").replace("for", "").strip()
            if search_term:
                webbrowser.open(f"https://google.com/search?q={search_term}")
                return f"Searching for: {search_term}"
            else:
                return "What would you like me to search for?"
        
        elif any(word in command for word in ["weather", "temperature"]):
            return "I don't have weather data access yet, but I can open a weather website for you."
        
        elif "play music" in command or "music" in command:
            return "I don't have music playback capability yet, but I can open a music website."
        
        else:
            return f"Processing command: '{command}'. {np.random.choice(self.responses['error'])}"
    
    def take_screenshot(self):
        """Take and save screenshot"""
        try:
            screenshot = ImageGrab.grab()
            timestamp = int(time.time())
            screenshot_path = os.path.join(ASSETS_DIR, f"screenshot_{timestamp}.png")
            screenshot.save(screenshot_path)
            return f"Screenshot captured and saved to {screenshot_path}"
        except Exception as e:
            return f"Screenshot failed: {str(e)}"

class RealTimeUltronUI:
    """Real-time ULTRON UI with live audio visualization"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ULTRON - Real-Time AI Assistant")
        self.root.geometry("1400x900")
        self.root.configure(bg='#0a0a0a')
        
        # Initialize components
        self.config = self.load_config()
        self.ai_brain = EnhancedLocalAI(self.config)
        self.voice_engine = self.init_voice()
        self.audio_processor = RealTimeAudioProcessor(callback=self.audio_callback)
        
        # UI State
        self.conversation_history = []
        self.is_listening = False
        self.audio_level = 0
        self.voice_detected = False
        
        self.create_realtime_ui()
        self.start_background_tasks()
        
    def load_config(self):
        """Load or create configuration"""
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                return json.load(f)
        
        default_config = {
            "voice": {"enabled": True, "rate": 180, "volume": 0.9},
            "audio": {"real_time": True, "sensitivity": 0.5, "auto_respond": True},
            "ai": {"local_mode": True, "context_memory": 10},
            "interface": {"theme": "realtime", "animations": True, "audio_viz": True}
        }
        
        with open(CONFIG_PATH, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def init_voice(self):
        """Initialize text-to-speech with faster settings"""
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', self.config.get('voice', {}).get('rate', 180))
            engine.setProperty('volume', self.config.get('voice', {}).get('volume', 0.9))
            return engine
        except Exception as e:
            log_error(f"Voice engine init failed: {e}")
            return None
    
    def create_realtime_ui(self):
        """Create real-time interface with audio visualization"""
        
        # Main container with dark theme
        main_frame = tk.Frame(self.root, bg='#0a0a0a')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Top section - Real-time status
        top_frame = tk.Frame(main_frame, bg='#1a1a2e', relief=tk.RAISED, bd=2)
        top_frame.pack(fill=tk.X, pady=(0, 15))
        
        # ULTRON title with live indicator
        title_frame = tk.Frame(top_frame, bg='#16213e')
        title_frame.pack(fill=tk.X, padx=8, pady=8)
        
        title_label = tk.Label(
            title_frame, 
            text="ULTRON REAL-TIME", 
            font=("Orbitron", 28, "bold"),
            fg='#00ff41', 
            bg='#16213e'
        )
        title_label.pack()
        
        # Live status indicators
        status_frame = tk.Frame(title_frame, bg='#16213e')
        status_frame.pack(fill=tk.X, pady=5)
        
        self.live_indicator = tk.Label(
            status_frame,
            text="● LIVE",
            font=("Courier", 14, "bold"),
            fg='#ff4444',
            bg='#16213e'
        )
        self.live_indicator.pack(side=tk.LEFT)
        
        self.audio_status = tk.Label(
            status_frame,
            text="🎤 Real-Time Audio Processing",
            font=("Courier", 12),
            fg='#3498db',
            bg='#16213e'
        )
        self.audio_status.pack(side=tk.RIGHT)
        
        # Audio visualization bar
        self.audio_viz_frame = tk.Frame(title_frame, bg='#16213e', height=20)
        self.audio_viz_frame.pack(fill=tk.X, pady=5)
        
        self.audio_canvas = tk.Canvas(
            self.audio_viz_frame, 
            bg='#2c3e50', 
            height=15, 
            highlightthickness=0
        )
        self.audio_canvas.pack(fill=tk.X, padx=10)
        
        # Middle section - Three panels
        middle_frame = tk.Frame(main_frame, bg='#0a0a0a')
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Left panel - Real-time system monitoring
        left_panel = tk.Frame(middle_frame, bg='#1a1a2e', width=320)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        left_panel.pack_propagate(False)
        
        self.create_realtime_status_panel(left_panel)
        
        # Center panel - Live conversation
        center_panel = tk.Frame(middle_frame, bg='#16213e')
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        self.create_live_conversation_panel(center_panel)
        
        # Right panel - Audio controls
        right_panel = tk.Frame(middle_frame, bg='#1a1a2e', width=320)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)
        
        self.create_audio_control_panel(right_panel)
        
        # Bottom section - Live command input
        bottom_frame = tk.Frame(main_frame, bg='#e67e22', relief=tk.RAISED, bd=2)
        bottom_frame.pack(fill=tk.X)
        
        self.create_live_input_panel(bottom_frame)
    
    def create_realtime_status_panel(self, parent):
        """Create real-time system status panel"""
        tk.Label(
            parent, 
            text="⚡ REAL-TIME STATUS", 
            font=("Orbitron", 16, "bold"),
            fg='#00ff41', 
            bg='#1a1a2e'
        ).pack(pady=15)
        
        # Live system metrics
        self.status_vars = {
            'cpu': tk.StringVar(value="CPU: ---%"),
            'memory': tk.StringVar(value="Memory: ---%"),
            'audio': tk.StringVar(value="Audio: Initializing"),
            'voice': tk.StringVar(value="Voice: Ready"),
            'commands': tk.StringVar(value="Commands: 0")
        }
        
        for key, var in self.status_vars.items():
            frame = tk.Frame(parent, bg='#1a1a2e')
            frame.pack(fill=tk.X, padx=15, pady=3)
            
            # Status indicator dot
            dot_color = '#00ff41' if key in ['voice', 'audio'] else '#3498db'
            tk.Label(
                frame,
                text="●",
                font=("Arial", 12),
                fg=dot_color,
                bg='#1a1a2e'
            ).pack(side=tk.LEFT, padx=(0, 10))
            
            tk.Label(
                frame,
                textvariable=var,
                font=("Courier", 11, "bold"),
                fg='#ecf0f1',
                bg='#1a1a2e',
                anchor='w'
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Real-time controls
        tk.Label(
            parent, 
            text="🚀 INSTANT ACTIONS", 
            font=("Orbitron", 14, "bold"),
            fg='#00ff41', 
            bg='#1a1a2e'
        ).pack(pady=(25, 15))
        
        actions = [
            ("📸 Quick Screenshot", self.instant_screenshot, '#e74c3c'),
            ("💻 System Report", self.instant_system_info, '#3498db'),
            ("🌐 Open Browser", lambda: webbrowser.open("https://google.com"), '#9b59b6'),
            ("📁 File Manager", self.open_file_manager, '#f39c12')
        ]
        
        for text, command, color in actions:
            btn = tk.Button(
                parent,
                text=text,
                command=command,
                bg=color,
                fg='white',
                font=("Courier", 10, "bold"),
                relief=tk.FLAT,
                padx=15,
                pady=8,
                cursor='hand2'
            )
            btn.pack(fill=tk.X, padx=15, pady=3)
    
    def create_live_conversation_panel(self, parent):
        """Create live conversation panel with real-time updates"""
        header_frame = tk.Frame(parent, bg='#16213e')
        header_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            header_frame, 
            text="🗣️ LIVE CONVERSATION", 
            font=("Orbitron", 16, "bold"),
            fg='#00ff41', 
            bg='#16213e'
        ).pack()
        
        # Voice activity indicator
        self.voice_activity = tk.Label(
            header_frame,
            text="🎤 Listening...",
            font=("Courier", 12, "bold"),
            fg='#27ae60',
            bg='#16213e'
        )
        self.voice_activity.pack(pady=5)
        
        # Real-time conversation display
        self.conversation_text = scrolledtext.ScrolledText(
            parent,
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg='#2c3e50',
            fg='#ecf0f1',
            font=("Consolas", 12),
            insertbackground='#3498db',
            selectbackground='#34495e'
        )
        self.conversation_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Configure conversation tags
        self.conversation_text.tag_configure("user", foreground="#3498db", font=("Consolas", 12, "bold"))
        self.conversation_text.tag_configure("ultron", foreground="#00ff41", font=("Consolas", 12, "bold"))
        self.conversation_text.tag_configure("system", foreground="#e67e22", font=("Consolas", 11, "italic"))
        self.conversation_text.tag_configure("voice", foreground="#f39c12", font=("Consolas", 12, "bold"))
        
        self.add_to_conversation("ULTRON", "Real-time audio processing initialized. Voice commands ready.", "ultron")
    
    def create_audio_control_panel(self, parent):
        """Create audio control panel"""
        tk.Label(
            parent, 
            text="🎛️ AUDIO CONTROLS", 
            font=("Orbitron", 16, "bold"),
            fg='#00ff41', 
            bg='#1a1a2e'
        ).pack(pady=15)
        
        # Main audio toggle
        self.audio_toggle_btn = tk.Button(
            parent,
            text="🎤 START REAL-TIME",
            command=self.toggle_realtime_audio,
            bg='#27ae60',
            fg='white',
            font=("Courier", 14, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=15,
            cursor='hand2'
        )
        self.audio_toggle_btn.pack(fill=tk.X, padx=15, pady=10)
        
        # Audio sensitivity
        tk.Label(
            parent,
            text="🔊 Audio Sensitivity",
            font=("Orbitron", 12, "bold"),
            fg='#ecf0f1',
            bg='#1a1a2e'
        ).pack(pady=(20, 5))
        
        self.sensitivity_scale = tk.Scale(
            parent,
            from_=0.1, to=1.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            bg='#2c3e50',
            fg='#ecf0f1',
            highlightthickness=0,
            font=("Courier", 10)
        )
        self.sensitivity_scale.set(0.5)
        self.sensitivity_scale.pack(fill=tk.X, padx=15, pady=5)
        
        # Voice response speed
        tk.Label(
            parent,
            text="⚡ Response Speed",
            font=("Orbitron", 12, "bold"),
            fg='#ecf0f1',
            bg='#1a1a2e'
        ).pack(pady=(15, 5))
        
        self.speed_scale = tk.Scale(
            parent,
            from_=100, to=250,
            resolution=10,
            orient=tk.HORIZONTAL,
            bg='#2c3e50',
            fg='#ecf0f1',
            highlightthickness=0,
            font=("Courier", 10)
        )
        self.speed_scale.set(180)
        self.speed_scale.pack(fill=tk.X, padx=15, pady=5)
        
        # Audio test buttons
        tk.Label(
            parent,
            text="🧪 AUDIO TESTS",
            font=("Orbitron", 12, "bold"),
            fg='#00ff41',
            bg='#1a1a2e'
        ).pack(pady=(20, 10))
        
        test_buttons = [
            ("🎵 Voice Test", self.test_voice),
            ("🎤 Mic Test", self.test_microphone),
            ("🔊 Speaker Test", self.test_speakers)
        ]
        
        for text, command in test_buttons:
            btn = tk.Button(
                parent,
                text=text,
                command=command,
                bg='#34495e',
                fg='white',
                font=("Courier", 10, "bold"),
                relief=tk.FLAT,
                padx=10,
                pady=5
            )
            btn.pack(fill=tk.X, padx=15, pady=2)
        
        # Save settings
        tk.Button(
            parent,
            text="💾 Save Settings",
            command=self.save_audio_settings,
            bg='#8e44ad',
            fg='white',
            font=("Courier", 12, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=10
        ).pack(fill=tk.X, padx=15, pady=(20, 10))
    
    def create_live_input_panel(self, parent):
        """Create live command input panel"""
        input_frame = tk.Frame(parent, bg='#e67e22')
        input_frame.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(
            input_frame,
            text="⌨️ Manual Command Input:",
            font=("Orbitron", 14, "bold"),
            bg='#e67e22',
            fg='white'
        ).pack(anchor='w', pady=(0, 5))
        
        entry_frame = tk.Frame(input_frame, bg='#e67e22')
        entry_frame.pack(fill=tk.X, pady=5)
        
        self.command_entry = tk.Entry(
            entry_frame,
            font=("Consolas", 14),
            bg='#2c3e50',
            fg='#ecf0f1',
            insertbackground='#3498db',
            relief=tk.FLAT,
            bd=5
        )
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))
        self.command_entry.bind('<Return>', self.process_text_command)
        
        tk.Button(
            entry_frame,
            text="⚡ EXECUTE",
            command=self.process_text_command,
            bg='#27ae60',
            fg='white',
            font=("Courier", 12, "bold"),
            relief=tk.FLAT,
            padx=25,
            pady=8,
            cursor='hand2'
        ).pack(side=tk.RIGHT)
    
    def audio_callback(self, event_type, data):
        """Handle real-time audio events"""
        if event_type == "voice_detected":
            self.root.after(0, self.on_voice_detected)
        elif event_type == "command_recognized":
            self.root.after(0, self.on_command_recognized, data)
    
    def on_voice_detected(self):
        """Handle voice detection"""
        self.voice_detected = True
        self.voice_activity.config(text="🗣️ Voice Detected!", fg='#f39c12')
        self.update_audio_visualization(high_activity=True)
    
    def on_command_recognized(self, command):
        """Handle recognized voice command"""
        self.voice_detected = False
        self.voice_activity.config(text="🎤 Processing...", fg='#e74c3c')
        
        # Add to conversation
        self.add_to_conversation("USER", f"🎤 {command}", "voice")
        
        # Process command
        response = self.ai_brain.process_command(command)
        self.add_to_conversation("ULTRON", response, "ultron")
        
        # Speak response
        if self.voice_engine:
            threading.Thread(target=self.speak_response, args=(response,), daemon=True).start()
        
        # Reset voice activity indicator
        self.root.after(2000, lambda: self.voice_activity.config(text="🎤 Listening...", fg='#27ae60'))
    
    def toggle_realtime_audio(self):
        """Toggle real-time audio processing"""
        if not self.is_listening:
            if self.audio_processor.start_stream():
                self.is_listening = True
                self.audio_toggle_btn.config(
                    text="🛑 STOP LISTENING",
                    bg='#e74c3c'
                )
                self.add_to_conversation("SYSTEM", "Real-time audio processing started", "system")
            else:
                self.add_to_conversation("SYSTEM", "Failed to start audio processing", "system")
        else:
            self.audio_processor.stop_stream()
            self.is_listening = False
            self.audio_toggle_btn.config(
                text="🎤 START REAL-TIME",
                bg='#27ae60'
            )
            self.add_to_conversation("SYSTEM", "Real-time audio processing stopped", "system")
    
    def update_audio_visualization(self, high_activity=False):
        """Update audio visualization bar"""
        try:
            self.audio_canvas.delete("all")
            width = self.audio_canvas.winfo_width()
            height = self.audio_canvas.winfo_height()
            
            if width > 1:  # Make sure canvas is initialized
                # Create audio level bars
                num_bars = 20
                bar_width = width // num_bars
                
                for i in range(num_bars):
                    if high_activity:
                        bar_height = np.random.randint(5, height-2)
                        color = '#00ff41' if i < 15 else '#f39c12'
                    else:
                        bar_height = np.random.randint(2, height//3)
                        color = '#3498db'
                    
                    x1 = i * bar_width
                    y1 = height - bar_height
                    x2 = x1 + bar_width - 1
                    y2 = height
                    
                    self.audio_canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
        except:
            pass  # Ignore canvas errors during initialization
    
    def add_to_conversation(self, speaker, message, tag=""):
        """Add message to conversation log"""
        self.conversation_text.config(state=tk.NORMAL)
        
        timestamp = time.strftime("%H:%M:%S")
        
        # Insert timestamp
        self.conversation_text.insert(tk.END, f"[{timestamp}] ")
        
        # Insert speaker name with tag
        self.conversation_text.insert(tk.END, f"{speaker}: ", tag if tag else speaker.lower())
        
        # Insert message
        self.conversation_text.insert(tk.END, f"{message}\n\n")
        
        self.conversation_text.config(state=tk.DISABLED)
        self.conversation_text.see(tk.END)
        
        # Update command counter
        if speaker == "USER":
            current = self.status_vars['commands'].get()
            count = int(current.split(': ')[1]) + 1
            self.status_vars['commands'].set(f"Commands: {count}")
    
    def process_text_command(self, event=None):
        """Process manual text command"""
        command = self.command_entry.get().strip()
        if not command:
            return
        
        self.add_to_conversation("USER", command, "user")
        self.command_entry.delete(0, tk.END)
        
        response = self.ai_brain.process_command(command)
        self.add_to_conversation("ULTRON", response, "ultron")
        
        if self.voice_engine:
            threading.Thread(target=self.speak_response, args=(response,), daemon=True).start()
    
    def speak_response(self, text):
        """Speak response with real-time settings"""
        if self.voice_engine:
            try:
                # Update voice settings
                rate = self.speed_scale.get()
                self.voice_engine.setProperty('rate', rate)
                
                self.voice_engine.say(text)
                self.voice_engine.runAndWait()
            except Exception as e:
                log_error(f"Speech error: {e}")
    
    def instant_screenshot(self):
        """Take instant screenshot"""
        try:
            screenshot = ImageGrab.grab()
            timestamp = int(time.time())
            screenshot_path = os.path.join(ASSETS_DIR, f"instant_screenshot_{timestamp}.png")
            screenshot.save(screenshot_path)
            self.add_to_conversation("SYSTEM", f"📸 Instant screenshot: {screenshot_path}", "system")
        except Exception as e:
            self.add_to_conversation("SYSTEM", f"Screenshot failed: {str(e)}", "system")
    
    def instant_system_info(self):
        """Show instant system information"""
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage('C:' if os.name == 'nt' else '/').percent
        
        info = f"💻 System Info - CPU: {cpu}%, Memory: {memory}%, Disk: {disk}%"
        self.add_to_conversation("SYSTEM", info, "system")
    
    def open_file_manager(self):
        """Open file manager"""
        try:
            if os.name == 'nt':
                os.startfile(ULTRON_ROOT)
            else:
                subprocess.Popen(['xdg-open', ULTRON_ROOT])
            self.add_to_conversation("SYSTEM", f"📁 File manager: {ULTRON_ROOT}", "system")
        except Exception as e:
            self.add_to_conversation("SYSTEM", f"File manager error: {str(e)}", "system")
    
    def test_voice(self):
        """Test voice output"""
        test_message = "ULTRON real-time voice test. Audio output working correctly."
        self.add_to_conversation("SYSTEM", "🎵 Voice test initiated", "system")
        if self.voice_engine:
            threading.Thread(target=self.speak_response, args=(test_message,), daemon=True).start()
    
    def test_microphone(self):
        """Test microphone input"""
        self.add_to_conversation("SYSTEM", "🎤 Microphone test - Say something now", "system")
        # Microphone test is handled by the real-time audio processor
    
    def test_speakers(self):
        """Test speaker output"""
        self.add_to_conversation("SYSTEM", "🔊 Speaker test - You should hear this", "system")
        test_message = "Speaker test successful. Audio output is working."
        if self.voice_engine:
            threading.Thread(target=self.speak_response, args=(test_message,), daemon=True).start()
    
    def save_audio_settings(self):
        """Save current audio settings"""
        self.config['audio']['sensitivity'] = self.sensitivity_scale.get()
        self.config['voice']['rate'] = self.speed_scale.get()
        
        with open(CONFIG_PATH, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        self.add_to_conversation("SYSTEM", "💾 Audio settings saved", "system")
    
    def update_system_status(self):
        """Update real-time system status"""
        try:
            cpu = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory().percent
            
            self.status_vars['cpu'].set(f"CPU: {cpu:.1f}%")
            self.status_vars['memory'].set(f"Memory: {memory:.1f}%")
            self.status_vars['audio'].set(f"Audio: {'Active' if self.is_listening else 'Standby'}")
            
            # Update live indicator
            if self.is_listening:
                self.live_indicator.config(fg='#00ff41')
                self.audio_status.config(text="🎤 Real-Time Processing Active")
            else:
                self.live_indicator.config(fg='#ff4444')
                self.audio_status.config(text="🎤 Real-Time Processing Standby")
                
        except Exception as e:
            log_error(f"Status update error: {e}")
    
    def start_background_tasks(self):
        """Start background monitoring and visualization"""
        def update_loop():
            while True:
                self.root.after(0, self.update_system_status)
                self.root.after(0, self.update_audio_visualization)
                time.sleep(0.5)  # Update twice per second for real-time feel
        
        threading.Thread(target=update_loop, daemon=True).start()
    
    def run(self):
        """Start the real-time application"""
        log_info("ULTRON Real-Time UI starting...")
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except KeyboardInterrupt:
            log_info("ULTRON shutting down...")
        except Exception as e:
            log_error(f"Application error: {e}")
    
    def on_closing(self):
        """Handle application closing"""
        if self.is_listening:
            self.audio_processor.stop_stream()
        self.root.destroy()

def check_audio_dependencies():
    """Check if audio dependencies are available"""
    try:
        import sounddevice
        import webrtcvad
        return True
    except ImportError:
        return False

def main():
    """Main entry point"""
    print("🤖 ULTRON - Real-Time AI Assistant")
    print("=" * 50)
    
    if not check_audio_dependencies():
        print("⚠️ Installing additional audio dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "sounddevice", "webrtcvad"])
            print("✅ Audio dependencies installed")
        except:
            print("❌ Failed to install audio dependencies")
            print("Please run: pip install sounddevice webrtcvad")
            return
    
    try:
        app = RealTimeUltronUI()
        app.run()
    except Exception as e:
        log_error(f"Startup error: {e}")
        print(f"Error starting ULTRON: {e}")

if __name__ == "__main__":
    main()
