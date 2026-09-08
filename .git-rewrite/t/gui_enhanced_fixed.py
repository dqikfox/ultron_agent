import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import os
import sys
import webbrowser
import psutil
from PIL import Image, ImageTk, ImageGrab, ImageDraw
import asyncio
from pathlib import Path
import random
import cv2
import numpy as np

# GPU monitoring
try:
    import gpustat
    import pynvml
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

# Network monitoring
try:
    import netifaces
    NETWORK_AVAILABLE = True
except ImportError:
    NETWORK_AVAILABLE = False

class AgentGUI:  # Keep the original class name for compatibility
    def __init__(self, agent, log_queue):
        self.agent = agent
        self.log_queue = log_queue
        self.listening = False
        self.conversation_history = []
        self.status_lights = {'cpu': 'green', 'memory': 'green', 'gpu0': 'green', 'gpu1': 'green', 'network': 'green', 'ai': 'green'}
        self.video_frames = []
        self.current_video_frame = 0
        self.video_playing = False
        self._last_net_io = None
        
        # Initialize main window
        self.root = tk.Tk()
        self.root.title("ULTRON Agent 2.0 - Enhanced Cyberpunk Interface")
        self.root.geometry("1500x1000")
        self.root.configure(bg='#0a0a0a')
        self.root.resizable(True, True)
        
        # Load images and videos
        self.load_images()
        
        # Create the enhanced cyberpunk UI
        self.create_enhanced_pokedex_ui()
        self.start_background_tasks()
        
        # Add initial welcome message
        self.add_to_conversation("ULTRON", "ULTRON AI Assistant initialized. Neural networks online. Ready for commands.")

    def load_images(self):
        """Load and prepare images/videos for the interface"""
        self.images = {}
        self.videos = {}
        image_path = Path("resources/images")
        
        try:
            # Load cyberpunk interface images
            cyberpunk_images = [
                "20250731_0131_Cyberpunk AI Interface_remix_01k1dz2gamf9xs8rtesb3nm7kw - Copy.png",
                "20250731_0131_Cyberpunk AI Interface_remix_01k1dz2ganefabrhpm3vdr2nt2 (1) - Copy.png",
                "20250731_0131_Cyberpunk AI Interface_remix_01k1dz2ganefabrhpm3vdr2nt2 - Copy.png",
                "2d6cde57-74ee-404e-acf2-91fb1db9eb8e - Copy.png",
                "5a42650e-c233-4dfd-a604-bdb8b7f1b77a - Copy.png"
            ]
            
            # Load random cyberpunk background
            for img_name in cyberpunk_images:
                if (image_path / img_name).exists():
                    bg_img = Image.open(image_path / img_name)
                    bg_img = bg_img.resize((1500, 1000), Image.Resampling.LANCZOS)
                    bg_img = bg_img.convert("RGBA")
                    bg_img.putalpha(40)  # More transparent
                    self.images['background'] = ImageTk.PhotoImage(bg_img)
                    break
            
            # Load ULTRON logo
            if (image_path / "ultron.jpg").exists():
                img = Image.open(image_path / "ultron.jpg")
                img = img.resize((140, 140), Image.Resampling.LANCZOS)
                self.images['ultron_logo'] = ImageTk.PhotoImage(img)
            
            # Load AI assistant images
            ai_images = ["UltronPrestige - Copy.webp", "Ultron_29_from_Marvel_Future_Revolution_001 - Copy.webp"]
            for ai_img in ai_images:
                if (image_path / ai_img).exists():
                    img = Image.open(image_path / ai_img)
                    img = img.resize((100, 100), Image.Resampling.LANCZOS)
                    self.images['ai_avatar'] = ImageTk.PhotoImage(img)
                    break
            
            # Load activity videos for status indication
            video_files = [
                "20250629_224952.mp4",
                "59517dae-ac3e-4832-9bce-cbcb7af25285 - Copy.mp4",
                "898c96cd-7d81-4e95-8bc5-81632de4cb4e - Copy.mp4"
            ]
            
            for video_file in video_files:
                if (image_path / video_file).exists():
                    self.load_video_frames(image_path / video_file)
                    break
            
            # Create enhanced status lights
            self.create_enhanced_status_lights()
            
        except Exception as e:
            print(f"Error loading media: {e} - gui_enhanced_fixed.py:103")
            self.images = {}

    def load_video_frames(self, video_path):
        """Load video frames for animated status indicators"""
        try:
            cap = cv2.VideoCapture(str(video_path))
            frames = []
            
            frame_count = 0
            while True and frame_count < 30:  # Limit to 30 frames
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Resize and convert frame
                frame = cv2.resize(frame, (60, 60))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                frames.append(ImageTk.PhotoImage(img))
                frame_count += 1
            
            cap.release()
            self.video_frames = frames
            
        except Exception as e:
            print(f"Error loading video: {e}")
            self.video_frames = []

    def create_enhanced_status_lights(self):
        """Create enhanced Pokedex-style status lights"""
        for status in ['online', 'warning', 'error', 'offline']:
            colors = {
                'online': '#00ff41',    # Bright green
                'warning': '#ffaa00',   # Orange  
                'error': '#ff4444',     # Red
                'offline': '#666666'    # Gray
            }
            
            # Create larger status lights with glow effect
            img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Outer glow
            draw.ellipse([4, 4, 28, 28], fill=colors[status] + '40', outline=None)
            # Inner bright circle
            draw.ellipse([8, 8, 24, 24], fill=colors[status], outline='#ffffff', width=2)
            # Highlight for 3D effect
            draw.ellipse([10, 10, 18, 18], fill=colors[status] + 'aa', outline=None)
            
            self.images[f'status_{status}'] = ImageTk.PhotoImage(img)

    def create_enhanced_pokedex_ui(self):
        """Create enhanced Pokedex-style interface with images and effects"""
        
        # Background canvas if background image exists
        if 'background' in self.images:
            bg_canvas = tk.Canvas(self.root, highlightthickness=0)
            bg_canvas.pack(fill=tk.BOTH, expand=True)
            bg_canvas.create_image(0, 0, anchor=tk.NW, image=self.images['background'])
            main_container = bg_canvas
        else:
            main_container = self.root
        
        # Main frame with enhanced styling
        main_frame = tk.Frame(main_container, bg='#0a0a0a', relief=tk.RAISED, bd=2)
        if 'background' in self.images:
            bg_canvas.create_window(50, 50, anchor=tk.NW, window=main_frame, width=1400, height=900)
        else:
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header section with ULTRON logo and title
        header_frame = tk.Frame(main_frame, bg='#1a1a2e', relief=tk.RAISED, bd=3, height=120)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        header_frame.pack_propagate(False)
        
        # Logo and title container
        title_container = tk.Frame(header_frame, bg='#1a1a2e')
        title_container.pack(expand=True, fill=tk.BOTH)
        
        # ULTRON logo
        if 'ultron_logo' in self.images:
            logo_label = tk.Label(title_container, image=self.images['ultron_logo'], bg='#1a1a2e')
            logo_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Title and status
        title_text_frame = tk.Frame(title_container, bg='#1a1a2e')
        title_text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20)
        
        # Main title with glow effect
        title_label = tk.Label(
            title_text_frame, 
            text="◆ ULTRON v2.0 ◆", 
            font=("Orbitron", 28, "bold"),
            fg='#00ff41', 
            bg='#1a1a2e',
            relief=tk.FLAT
        )
        title_label.pack(pady=(15, 5))
        
        # Subtitle with AI model info
        subtitle = tk.Label(
            title_text_frame,
            text="◇ AI Assistant - Neural Network Online ◇",
            font=("Courier New", 14, "bold"),
            fg='#3498db',
            bg='#1a1a2e'
        )
        subtitle.pack()
        
        # Model info
        model_info = tk.Label(
            title_text_frame,
            text=f"Model: {self.agent.config.data.get('llm_model', 'Unknown')} | Engine: Ollama",
            font=("Courier New", 10),
            fg='#95a5a6',
            bg='#1a1a2e'
        )
        model_info.pack()
        
        # Status indicator in header
        if 'status_online' in self.images:
            status_label = tk.Label(title_container, image=self.images['status_online'], bg='#1a1a2e')
            status_label.pack(side=tk.RIGHT, padx=20)
        
        # AI Avatar if available
        if 'ai_avatar' in self.images:
            avatar_label = tk.Label(title_container, image=self.images['ai_avatar'], bg='#1a1a2e')
            avatar_label.pack(side=tk.RIGHT, padx=20)
        
        # Main content area
        content_frame = tk.Frame(main_frame, bg='#16213e', relief=tk.SUNKEN, bd=2)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Create three-panel layout
        self.create_enhanced_three_panel_layout(content_frame)
        
        # Enhanced footer with command input
        self.create_enhanced_command_panel(main_frame)

    def create_enhanced_three_panel_layout(self, parent):
        """Create enhanced three-panel layout"""
        
        # Left panel - Enhanced system status
        left_panel = tk.Frame(parent, bg='#2c3e50', width=360, relief=tk.RAISED, bd=2)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 5), pady=10)
        left_panel.pack_propagate(False)
        
        self.create_enhanced_status_panel(left_panel)
        
        # Center panel - Enhanced conversation
        center_panel = tk.Frame(parent, bg='#34495e', relief=tk.SUNKEN, bd=2)
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=10)
        
        self.create_enhanced_conversation_panel(center_panel)
        
        # Right panel - Enhanced controls
        right_panel = tk.Frame(parent, bg='#2c3e50', width=360, relief=tk.RAISED, bd=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 10), pady=10)
        right_panel.pack_propagate(False)
        
        self.create_enhanced_control_panel(right_panel)

    def create_enhanced_status_panel(self, parent):
        """Create enhanced system status panel with better visuals"""
        # Header with icon
        status_header = tk.Frame(parent, bg='#2c3e50', height=50)
        status_header.pack(fill=tk.X, padx=10, pady=(10, 0))
        status_header.pack_propagate(False)
        
        tk.Label(
            status_header, 
            text="⚡ SYSTEM STATUS ⚡", 
            font=("Orbitron", 14, "bold"),
            fg='#00ff41', 
            bg='#2c3e50'
        ).pack(pady=15)
        
        # System metrics with progress bars and status lights
        metrics_frame = tk.Frame(parent, bg='#2c3e50')
        metrics_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.status_vars = {
            'cpu': tk.StringVar(value="CPU: 0%"),
            'memory': tk.StringVar(value="Memory: 0%"),
            'disk': tk.StringVar(value="Disk: 0%"),
            'gpu0': tk.StringVar(value="GPU 0: N/A"),
            'gpu1': tk.StringVar(value="GPU 1: N/A"),
            'network': tk.StringVar(value="Network: 0 KB/s"),
            'voice': tk.StringVar(value="Voice: Ready"),
            'ai': tk.StringVar(value="AI: Online")
        }
        
        self.progress_bars = {}
        self.status_light_labels = {}
        
        for key, var in self.status_vars.items():
            metric_frame = tk.Frame(metrics_frame, bg='#2c3e50')
            metric_frame.pack(fill=tk.X, pady=3)
            
            # Status light and label container
            status_container = tk.Frame(metric_frame, bg='#2c3e50')
            status_container.pack(fill=tk.X)
            
            # Status light
            status_light = tk.Label(
                status_container,
                image=self.images.get('status_online', ''),
                bg='#2c3e50'
            )
            status_light.pack(side=tk.LEFT, padx=(0, 10))
            self.status_light_labels[key] = status_light
            
            # Label
            tk.Label(
                status_container,
                textvariable=var,
                font=("Courier New", 10, "bold"),
                fg='#ecf0f1',
                bg='#2c3e50',
                anchor='w'
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Progress bar for numeric metrics
            if key in ['cpu', 'memory', 'disk', 'gpu0', 'gpu1']:
                progress = ttk.Progressbar(
                    metric_frame, 
                    mode='determinate',
                    length=300,
                    style='Custom.Horizontal.TProgressbar'
                )
                progress.pack(fill=tk.X, pady=(2, 0))
                self.progress_bars[key] = progress
        
        # Configure progress bar style
        style = ttk.Style()
        style.configure('Custom.Horizontal.TProgressbar',
                       background='#00ff41',
                       troughcolor='#34495e',
                       borderwidth=1,
                       relief='flat')
        
        # Quick actions with enhanced buttons
        actions_header = tk.Frame(parent, bg='#2c3e50')
        actions_header.pack(fill=tk.X, padx=10, pady=(20, 10))
        
        tk.Label(
            actions_header, 
            text="⚙️ QUICK ACTIONS ⚙️", 
            font=("Orbitron", 12, "bold"),
            fg='#00ff41', 
            bg='#2c3e50'
        ).pack()
        
        actions_frame = tk.Frame(parent, bg='#2c3e50')
        actions_frame.pack(fill=tk.X, padx=10, pady=10)
        
        enhanced_actions = [
            ("📸 Screenshot", self.take_screenshot, '#3498db'),
            ("💻 System Info", self.show_system_info, '#9b59b6'),
            ("🌐 Browser", lambda: webbrowser.open("https://google.com"), '#e67e22'),
            ("📁 File Manager", self.open_file_manager, '#27ae60'),
            ("🔧 Tools", self.show_tools_explorer, '#f39c12')
        ]
        
        for text, command, color in enhanced_actions:
            btn = tk.Button(
                actions_frame,
                text=text,
                command=command,
                bg=color,
                fg='white',
                font=("Segoe UI", 10, "bold"),
                relief=tk.FLAT,
                padx=15,
                pady=8,
                cursor='hand2',
                activebackground=self.lighten_color(color),
                activeforeground='white'
            )
            btn.pack(fill=tk.X, pady=3)
            
            # Add hover effects
            btn.bind("<Enter>", lambda e, b=btn, c=color: b.configure(bg=self.lighten_color(c)))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.configure(bg=c))

    def lighten_color(self, color):
        """Lighten a hex color for hover effects"""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        lighter_rgb = tuple(min(255, int(c * 1.2)) for c in rgb)
        return '#{:02x}{:02x}{:02x}'.format(*lighter_rgb)

    def create_enhanced_conversation_panel(self, parent):
        """Create enhanced conversation panel with better styling"""
        # Header
        conv_header = tk.Frame(parent, bg='#34495e', height=50)
        conv_header.pack(fill=tk.X, padx=10, pady=(10, 0))
        conv_header.pack_propagate(False)
        
        tk.Label(
            conv_header, 
            text="💬 CONVERSATION LOG 💬", 
            font=("Orbitron", 14, "bold"),
            fg='#00ff41', 
            bg='#34495e'
        ).pack(pady=15)
        
        # Enhanced conversation display with border
        conv_container = tk.Frame(parent, bg='#2c3e50', relief=tk.SUNKEN, bd=2)
        conv_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.conversation_text = scrolledtext.ScrolledText(
            conv_container,
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg='#2c3e50',
            fg='#ecf0f1',
            font=("Consolas", 11),
            insertbackground='#00ff41',
            selectbackground='#3498db',
            selectforeground='white',
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.conversation_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Enhanced text tags with better colors
        self.conversation_text.tag_configure("user", foreground="#3498db", font=("Consolas", 11, "bold"))
        self.conversation_text.tag_configure("ultron", foreground="#00ff41", font=("Consolas", 11, "bold"))
        self.conversation_text.tag_configure("system", foreground="#e67e22", font=("Consolas", 10, "italic"))
        self.conversation_text.tag_configure("timestamp", foreground="#95a5a6", font=("Consolas", 9))

    def create_enhanced_control_panel(self, parent):
        """Create enhanced control panel with better organization"""
        # Voice controls section
        voice_header = tk.Frame(parent, bg='#2c3e50')
        voice_header.pack(fill=tk.X, padx=10, pady=(10, 0))
        
        tk.Label(
            voice_header, 
            text="🎤 VOICE CONTROLS 🎤", 
            font=("Orbitron", 14, "bold"),
            fg='#00ff41', 
            bg='#2c3e50'
        ).pack(pady=10)
        
        # Enhanced voice button
        self.voice_btn = tk.Button(
            parent,
            text="🎤 Start Listening",
            command=self.toggle_listening,
            bg='#27ae60',
            fg='white',
            font=("Segoe UI", 12, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=15,
            cursor='hand2',
            activebackground='#2ecc71',
            activeforeground='white'
        )
        self.voice_btn.pack(fill=tk.X, padx=10, pady=10)
        
        # Voice test button
        test_voice_btn = tk.Button(
            parent,
            text="🔊 Test Voice Output",
            command=self.test_voice_output,
            bg='#8e44ad',
            fg='white',
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2',
            activebackground='#9b59b6',
            activeforeground='white'
        )
        test_voice_btn.pack(fill=tk.X, padx=10, pady=(0,10))
        
        # Configuration section
        config_header = tk.Frame(parent, bg='#2c3e50')
        config_header.pack(fill=tk.X, padx=10, pady=(20, 0))
        
        tk.Label(
            config_header, 
            text="⚙️ CONFIGURATION ⚙️", 
            font=("Orbitron", 12, "bold"),
            fg='#00ff41', 
            bg='#2c3e50'
        ).pack(pady=10)
        
        # Enhanced dropdowns with frames
        config_frame = tk.Frame(parent, bg='#2c3e50')
        config_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Voice engine selection
        voice_frame = tk.Frame(config_frame, bg='#34495e', relief=tk.RAISED, bd=1)
        voice_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(voice_frame, text="Voice Engine:", bg='#34495e', fg='#ecf0f1', 
                font=("Segoe UI", 10, "bold")).pack(anchor='w', padx=10, pady=(5,0))
        
        self.voice_engine_var = tk.StringVar(value=self.agent.config.data.get("voice_engine", "pyttsx3"))
        voice_combo = ttk.Combobox(voice_frame, textvariable=self.voice_engine_var, 
                                  state="readonly", font=("Segoe UI", 10))
        voice_combo['values'] = ("pyttsx3", "elevenlabs", "openai")
        voice_combo.pack(fill=tk.X, padx=10, pady=(0,10))
        voice_combo.bind("<<ComboboxSelected>>", self.update_voice_engine)
        
        # LLM model selection
        llm_frame = tk.Frame(config_frame, bg='#34495e', relief=tk.RAISED, bd=1)
        llm_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(llm_frame, text="LLM Model:", bg='#34495e', fg='#ecf0f1',
                font=("Segoe UI", 10, "bold")).pack(anchor='w', padx=10, pady=(5,0))
        
        self.llm_model_var = tk.StringVar(value=self.agent.config.data.get("llm_model", "qwen2.5:latest"))
        llm_combo = ttk.Combobox(llm_frame, textvariable=self.llm_model_var, 
                               state="readonly", font=("Segoe UI", 10))
        llm_combo['values'] = ("qwen2.5:latest", "llama3.2:latest", "hermes3:latest", "phi3:latest")
        llm_combo.pack(fill=tk.X, padx=10, pady=(0,10))
        llm_combo.bind("<<ComboboxSelected>>", self.update_llm_model)
        
        # Enhanced toggles
        toggles_frame = tk.Frame(config_frame, bg='#34495e', relief=tk.RAISED, bd=1)
        toggles_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(toggles_frame, text="System Modules:", bg='#34495e', fg='#ecf0f1',
                font=("Segoe UI", 10, "bold")).pack(anchor='w', padx=10, pady=(5,0))
        
        modules_inner = tk.Frame(toggles_frame, bg='#34495e')
        modules_inner.pack(fill=tk.X, padx=10, pady=(0,10))
        
        self.voice_enabled = tk.BooleanVar(value=self.agent.config.data.get("use_voice", True))
        self.vision_enabled = tk.BooleanVar(value=self.agent.config.data.get("use_vision", True))
        self.api_enabled = tk.BooleanVar(value=self.agent.config.data.get("use_api", True))
        
        for text, var, icon in [("🎤 Voice", self.voice_enabled, "🎤"), 
                               ("👁️ Vision", self.vision_enabled, "👁️"), 
                               ("🌐 API", self.api_enabled, "🌐")]:
            tk.Checkbutton(modules_inner, text=text, variable=var, 
                          bg='#34495e', fg='#ecf0f1', selectcolor='#2c3e50',
                          font=("Segoe UI", 9), activebackground='#34495e',
                          activeforeground='#ecf0f1').pack(anchor='w', pady=2)

    def create_enhanced_command_panel(self, parent):
        """Create enhanced command input panel"""
        command_frame = tk.Frame(parent, bg='#e67e22', relief=tk.RAISED, bd=3, height=100)
        command_frame.pack(fill=tk.X)
        command_frame.pack_propagate(False)
        
        # Command header
        cmd_header = tk.Frame(command_frame, bg='#e67e22')
        cmd_header.pack(fill=tk.X, padx=15, pady=(10, 0))
        
        tk.Label(
            cmd_header,
            text="⌨️ COMMAND INTERFACE ⌨️",
            font=("Orbitron", 12, "bold"),
            bg='#e67e22',
            fg='white'
        ).pack()
        
        # Input area
        input_container = tk.Frame(command_frame, bg='#e67e22')
        input_container.pack(fill=tk.X, padx=15, pady=10)
        
        entry_frame = tk.Frame(input_container, bg='#2c3e50', relief=tk.SUNKEN, bd=2)
        entry_frame.pack(fill=tk.X)
        
        self.command_entry = tk.Entry(
            entry_frame,
            font=("Consolas", 12),
            bg='#2c3e50',
            fg='#ecf0f1',
            insertbackground='#00ff41',
            relief=tk.FLAT,
            bd=0
        )
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=8)
        self.command_entry.bind('<Return>', self.process_text_command)
        
        execute_btn = tk.Button(
            entry_frame,
            text="▶ EXECUTE",
            command=self.process_text_command,
            bg='#27ae60',
            fg='white',
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2',
            activebackground='#2ecc71'
        )
        execute_btn.pack(side=tk.RIGHT, padx=(0, 10))

    def add_to_conversation(self, speaker, message):
        """Enhanced conversation logging with better formatting"""
        self.conversation_text.config(state=tk.NORMAL)
        
        timestamp = time.strftime("%H:%M:%S")
        
        # Add timestamp
        self.conversation_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # Add speaker with appropriate styling
        if speaker == "ULTRON":
            self.conversation_text.insert(tk.END, f"{speaker}: ", "ultron")
            icon = "🤖 "
        elif speaker == "USER":
            self.conversation_text.insert(tk.END, f"{speaker}: ", "user") 
            icon = "👤 "
        else:
            self.conversation_text.insert(tk.END, f"{speaker}: ", "system")
            icon = "⚙️ "
        
        # Add message
        self.conversation_text.insert(tk.END, f"{icon}{message}\n\n")
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
        
        # Process with agent
        try:
            response = self.agent.handle_text(command)
            self.add_to_conversation("ULTRON", response)
            
            # Trigger voice output if enabled
            if self.agent.voice and self.voice_enabled.get():
                threading.Thread(target=self.speak_async, args=(response,), daemon=True).start()
        except Exception as e:
            self.add_to_conversation("SYSTEM", f"Error processing command: {str(e)}")

    def speak_async(self, text):
        """Async wrapper for voice output"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.agent.voice.speak(text))
            loop.close()
        except Exception as e:
            print(f"Voice output error: {e}")

    def test_voice_output(self):
        """Test voice output functionality"""
        test_message = "Voice output is working correctly. ULTRON systems online."
        self.add_to_conversation("SYSTEM", f"🔊 Testing voice output: {test_message}")
        
        if self.agent.voice:
            threading.Thread(target=self.speak_async, args=(test_message,), daemon=True).start()
        else:
            self.add_to_conversation("SYSTEM", "❌ Voice system not available")

    def toggle_listening(self):
        """Toggle voice listening"""
        if not self.agent.voice:
            messagebox.showwarning("Voice", "Voice is not enabled.")
            return
            
        if not self.listening:
            self.listening = True
            self.voice_btn.config(text="🛑 Stop Listening", bg='#e74c3c')
            threading.Thread(target=self.listen_for_voice, daemon=True).start()
        else:
            self.listening = False
            self.voice_btn.config(text="🎤 Start Listening", bg='#27ae60')

    def listen_for_voice(self):
        """Listen for voice commands"""
        while self.listening:
            try:
                # Use asyncio to handle the async voice.listen method
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                text = loop.run_until_complete(self.agent.voice.listen(timeout=3))
                loop.close()
                
                if text:
                    self.root.after(0, self.process_voice_command, text)
                    
            except Exception as e:
                print(f"Voice recognition error: {e} - gui_enhanced_fixed.py:650")
            
            time.sleep(0.5)

    def process_voice_command(self, command):
        """Process voice command"""
        self.add_to_conversation("USER", f"🎤 {command}")
        
        try:
            response = self.agent.handle_text(command)
            self.add_to_conversation("ULTRON", response)
            
            # Trigger voice output if enabled
            if self.agent.voice and self.voice_enabled.get():
                threading.Thread(target=self.speak_async, args=(response,), daemon=True).start()
        except Exception as e:
            self.add_to_conversation("SYSTEM", f"Error processing voice command: {str(e)}")

    def update_system_status(self):
        """Update system status display with enhanced visuals and GPU/network monitoring"""
        try:
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage('C:').percent if os.name == 'nt' else psutil.disk_usage('/').percent
            
            # Update basic metrics
            self.status_vars['cpu'].set(f"CPU: {cpu:.1f}%")
            self.status_vars['memory'].set(f"Memory: {memory:.1f}%")
            self.status_vars['disk'].set(f"Disk: {disk:.1f}%")
            self.status_vars['voice'].set(f"Voice: {'Listening' if self.listening else 'Ready'}")
            self.status_vars['ai'].set(f"AI: {'Online' if hasattr(self.agent, 'brain') else 'Offline'}")
            
            # GPU monitoring
            if GPU_AVAILABLE:
                try:
                    pynvml.nvmlInit()
                    device_count = pynvml.nvmlDeviceGetCount()
                    
                    for i in range(min(2, device_count)):  # Only show GPU 0 and 1
                        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                        mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                        util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                        temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                        
                        usage = int(mem_info.used) / int(mem_info.total) * 100
                        self.status_vars[f'gpu{i}'].set(f"GPU {i}: {usage:.1f}% | {temp}°C")
                        
                        if hasattr(self, 'progress_bars') and f'gpu{i}' in self.progress_bars:
                            self.progress_bars[f'gpu{i}']['value'] = usage
                        
                        # Update status light based on temperature and usage
                        if temp > 80 or usage > 90:
                            self.update_status_light(f'gpu{i}', 'error')
                        elif temp > 70 or usage > 75:
                            self.update_status_light(f'gpu{i}', 'warning')
                        else:
                            self.update_status_light(f'gpu{i}', 'online')
                    
                    # Fill missing GPUs
                    for i in range(device_count, 2):
                        self.status_vars[f'gpu{i}'].set(f"GPU {i}: Not Available")
                        self.update_status_light(f'gpu{i}', 'offline')
                        
                except Exception as e:
                    for i in range(2):
                        self.status_vars[f'gpu{i}'].set(f"GPU {i}: Error")
                        self.update_status_light(f'gpu{i}', 'error')
            else:
                for i in range(2):
                    self.status_vars[f'gpu{i}'].set(f"GPU {i}: Not Available")
                    self.update_status_light(f'gpu{i}', 'offline')
            
            # Network monitoring
            try:
                net_io = psutil.net_io_counters()
                if hasattr(self, '_last_net_io'):
                    bytes_sent = net_io.bytes_sent - self._last_net_io.bytes_sent
                    bytes_recv = net_io.bytes_recv - self._last_net_io.bytes_recv
                    total_bytes = bytes_sent + bytes_recv
                    
                    # Convert to KB/s (assuming 2-second update interval)
                    speed_kbs = total_bytes / 1024 / 2
                    self.status_vars['network'].set(f"Network: {speed_kbs:.1f} KB/s")
                    
                    # Update network status light
                    if speed_kbs > 1000:  # High activity
                        self.update_status_light('network', 'online')
                    elif speed_kbs > 100:  # Medium activity
                        self.update_status_light('network', 'warning')
                    else:  # Low activity
                        self.update_status_light('network', 'offline')
                else:
                    self.status_vars['network'].set("Network: Initializing...")
                    self.update_status_light('network', 'warning')
                
                self._last_net_io = net_io
                
            except Exception as e:
                self.status_vars['network'].set("Network: Error")
                self.update_status_light('network', 'error')
            
            # Update progress bars
            if hasattr(self, 'progress_bars'):
                self.progress_bars['cpu']['value'] = cpu
                self.progress_bars['memory']['value'] = memory
                self.progress_bars['disk']['value'] = disk
            
            # Update status lights for basic metrics
            self.update_status_light('cpu', 'error' if cpu > 90 else 'warning' if cpu > 75 else 'online')
            self.update_status_light('memory', 'error' if memory > 90 else 'warning' if memory > 75 else 'online')
            self.update_status_light('voice', 'online' if self.listening else 'offline')
            self.update_status_light('ai', 'online' if hasattr(self.agent, 'brain') else 'error')
            
        except Exception as e:
            print(f"Status update error: {e} - gui_enhanced_fixed.py:760")

    def update_status_light(self, component, status):
        """Update status light for a component"""
        try:
            if hasattr(self, 'status_light_labels') and component in self.status_light_labels:
                status_image = self.images.get(f'status_{status}')
                if status_image:
                    self.status_light_labels[component].configure(image=status_image)
                    self.status_lights[component] = status
        except Exception as e:
            print(f"Status light update error: {e}")

    def take_screenshot(self):
        """Take screenshot"""
        try:
            screenshot = ImageGrab.grab()
            timestamp = int(time.time())
            screenshot_path = Path(f"screenshot_{timestamp}.png")
            screenshot.save(screenshot_path)
            self.add_to_conversation("SYSTEM", f"📸 Screenshot saved: {screenshot_path}")
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
        self.add_to_conversation("SYSTEM", f"💻 System Information:\n{info_text}")

    def open_file_manager(self):
        """Open file manager"""
        try:
            if os.name == 'nt':
                os.startfile(os.getcwd())
            else:
                import subprocess
                subprocess.Popen(['xdg-open', os.getcwd()])
            self.add_to_conversation("SYSTEM", f"📁 File manager opened: {os.getcwd()}")
        except Exception as e:
            self.add_to_conversation("SYSTEM", f"Failed to open file manager: {str(e)}")

    def show_tools_explorer(self):
        """Show tools explorer popup"""
        popup = tk.Toplevel(self.root)
        popup.title("🔧 Tools Explorer")
        popup.geometry("700x500")
        popup.configure(bg='#2c3e50')
        
        # Header
        header = tk.Frame(popup, bg='#1a1a2e', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="🔧 Available Tools", font=("Orbitron", 16, "bold"),
                fg='#00ff41', bg='#1a1a2e').pack(pady=20)
        
        # Tools list with enhanced styling
        tools_frame = tk.Frame(popup, bg='#2c3e50')
        tools_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tools_listbox = tk.Listbox(tools_frame, bg='#34495e', fg='#ecf0f1', 
                                  font=("Courier New", 11), selectbackground='#3498db')
        tools_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Populate tools
        for tool in self.agent.tools:
            tools_listbox.insert(tk.END, f"🔧 {tool.name} - {tool.description}")
        
        tk.Button(popup, text="Close", command=popup.destroy,
                 bg='#e74c3c', fg='white', font=("Segoe UI", 12, "bold"),
                 relief=tk.FLAT, padx=30, pady=10).pack(pady=(0, 20))

    def update_voice_engine(self, event=None):
        """Update voice engine"""
        new_engine = self.voice_engine_var.get()
        self.agent.config.data["voice_engine"] = new_engine
        self.agent.config.data["tts_engine"] = new_engine
        self.add_to_conversation("SYSTEM", f"🎤 Voice engine set to {new_engine}")

    def update_llm_model(self, event=None):
        """Update LLM model"""
        new_model = self.llm_model_var.get()
        self.agent.config.data["llm_model"] = new_model
        self.add_to_conversation("SYSTEM", f"🧠 LLM model set to {new_model}")

    def start_background_tasks(self):
        """Start background monitoring tasks"""
        def update_loop():
            while True:
                self.root.after(0, self.update_system_status)
                time.sleep(2)
        
        threading.Thread(target=update_loop, daemon=True).start()
        
        # Start log queue polling
        self.root.after(500, self._poll_log_queue)

    def _poll_log_queue(self):
        """Poll log queue for messages"""
        while not self.log_queue.empty():
            msg = self.log_queue.get_nowait()
            self.add_to_conversation("SYSTEM", msg)
        self.root.after(500, self._poll_log_queue)

    def run(self):
        """Start the GUI"""
        self.root.mainloop()
