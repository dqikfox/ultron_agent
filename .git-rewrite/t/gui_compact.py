import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import tkinter as tk
import threading
import time
import os
import sys
import webbrowser
import psutil
import platform
import subprocess
from PIL import Image, ImageTk, ImageGrab, ImageDraw
import asyncio
from pathlib import Path
import logging
import math

# Enhanced voice system
try:
    from voice_manager import get_voice_manager, speak as voice_speak, test_voice_system
    VOICE_MANAGER_AVAILABLE = True
except ImportError:
    VOICE_MANAGER_AVAILABLE = False

# Ollama manager
try:
    from ollama_manager import get_ollama_manager, test_ollama_connection
    OLLAMA_MANAGER_AVAILABLE = True
except ImportError:
    OLLAMA_MANAGER_AVAILABLE = False

# Ultron theme system
try:
    from gui_ultron_theme import (
        UltronTheme, UltronStatusPanel, UltronParticleSystem,
        apply_ultron_theme_to_gui, create_ultron_button, 
        create_ultron_label, create_ultron_frame
    )
    ULTRON_THEME_AVAILABLE = True
except ImportError:
    ULTRON_THEME_AVAILABLE = False

# GPU monitoring
try:
    import gpustat
    import pynvml
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

# POCHI integration
try:
    from tools.pochi_tool import get_pochi_manager, create_pochi_tool
    POCHI_AVAILABLE = True
except ImportError:
    POCHI_AVAILABLE = False

# Network monitoring
try:
    import netifaces
    import subprocess
    NETWORK_AVAILABLE = True
except ImportError:
    NETWORK_AVAILABLE = False

class AgentGUI:
    def __init__(self, agent, log_queue):
        self.agent = agent
        self.log_queue = log_queue
        self.listening = False
        self.recording = False  # New: for push-to-talk functionality
        self.conversation_history = []
        
        # Enhanced status tracking with detailed indicators
        self.status_lights = {
            'ollama': 'orange',      # loading/connecting
            'modelname': 'orange',   # loading/connecting  
            'voice': 'orange',       # loading/connecting
            'brain': 'orange',       # loading/connecting
            'pochi': 'orange',       # loading/connecting
            'tools': 'orange'        # loading/connecting
        }
        
        # Live STT display
        self.current_stt_text = None  # Will be initialized after root window
        self.is_processing = False
        
        # Protective method for setting STT text
    def set_stt_text(self, text):
        """Safely set STT text"""
        if self.current_stt_text:
            self.current_stt_text.set(text)
        
        self._last_net_io = None
        
        # Setup logging
        self.setup_logging()
        self.log_action("GUI initialization started")
        
        # Initialize Ultron theme system
        if ULTRON_THEME_AVAILABLE:
            self.ultron_theme = UltronTheme()
            self.status_panel_system = None
            self.particle_system = None
            self.glow_phase = 0  # Initialize animation phase
            self.log_action("🎨 Ultron theme system initialized")
        else:
            self.ultron_theme = None
            self.glow_phase = 0  # Initialize even without theme
            self.log_action("⚠️ Ultron theme system not available")
        
        # Initialize enhanced voice system
        if VOICE_MANAGER_AVAILABLE:
            self.voice_manager = get_voice_manager(self.agent.config if hasattr(self.agent, 'config') else None)
            self.log_action("Enhanced voice manager initialized")
        else:
            self.voice_manager = None
            self.log_action("Voice manager not available")
        
        # Initialize Ollama manager and update status
        if OLLAMA_MANAGER_AVAILABLE:
            self.status_lights['ollama'] = 'orange'  # connecting
            self.ollama_manager = get_ollama_manager(self.agent.config if hasattr(self.agent, 'config') else None)
            self.log_action("Ollama manager initialized")
            
            # Test connection and update status
            if self.ollama_manager and self.ollama_manager.check_connection():
                self.status_lights['ollama'] = 'green'  # connected
                self.status_lights['modelname'] = 'green'  # model available
                self.log_action("✅ Ollama connected successfully")
                
                # Ensure default model is loaded
                if self.ollama_manager.ensure_default_model():
                    self.log_action("Default model qwen2.5vl confirmed loaded")
                else:
                    self.status_lights['modelname'] = 'red'  # model failed
                    self.log_action("⚠️ Could not load default model")
            else:
                self.status_lights['ollama'] = 'red'  # failed
                self.status_lights['modelname'] = 'red'  # failed
                self.log_action("❌ Ollama connection failed")
        else:
            self.ollama_manager = None
            self.status_lights['ollama'] = 'red'  # not available
            self.status_lights['modelname'] = 'red'  # not available
            self.log_action("Ollama manager not available")
        
        # Initialize POCHI and update status
        if POCHI_AVAILABLE and hasattr(self.agent, 'pochi'):
            self.status_lights['pochi'] = 'orange'  # connecting
            try:
                if self.agent.pochi.is_available():
                    self.status_lights['pochi'] = 'green'  # connected
                    self.log_action("✅ POCHI available")
                else:
                    self.status_lights['pochi'] = 'red'  # failed
                    self.log_action("❌ POCHI not available")
            except:
                self.status_lights['pochi'] = 'red'  # error
                self.log_action("❌ POCHI error")
        else:
            self.status_lights['pochi'] = 'red'  # not available
            self.log_action("POCHI not available")
        
        # Initialize brain/memory and tools status
        self.status_lights['brain'] = 'green' if hasattr(self.agent, 'brain') else 'red'
        self.status_lights['tools'] = 'green' if hasattr(self.agent, 'tools') else 'red'
        
        # Test voice system and update status
        if self.voice_manager:
            self.status_lights['voice'] = 'green'  # available
            self.log_action("✅ Voice system ready")
        elif hasattr(self.agent, 'voice') and self.agent.voice:
            self.status_lights['voice'] = 'orange'  # fallback available
            self.log_action("⚠️ Voice system fallback mode")
        else:
            self.status_lights['voice'] = 'red'  # not available
            self.log_action("❌ Voice system not available")
        
        # Initialize main window with proper size
        self.root = tk.Tk()
        self.root.title("ULTRON Agent 2.0 - Compact Interface")
        self.root.geometry("1200x700")  # Smaller, more manageable size
        self.root.configure(bg='#0a0a0a')
        self.root.resizable(True, True)
        
        # Set minimum size to prevent it from being too small
        self.root.minsize(800, 600)
        
        # Initialize STT display after root window creation
        self.current_stt_text = tk.StringVar(value="🎤 Click Voice to start speaking...")
        
        # Load images
        self.load_images()
        
        # Create the enhanced Ultron UI
        self.create_ultron_ui()
        self.start_background_tasks()
        
        # Apply Ultron theme if available
        if ULTRON_THEME_AVAILABLE and self.ultron_theme:
            apply_ultron_theme_to_gui(self)
            self.log_action("🎨 Ultron visual theme applied successfully")
        
        # Add initial welcome message
        self.add_to_conversation("ULTRON", "🤖 ULTRON AI Assistant initialized. Neural networks online. Ready for commands.")
        self.log_action("GUI initialization completed")

    def setup_logging(self):
        """Setup logging for all actions"""
        log_path = Path("ultron_gui.log")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("ULTRON_GUI")

    def log_action(self, action):
        """Log all actions with timestamp"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {action}"
        self.logger.info(log_message)
        print(f"GUI LOG: {log_message} - gui_compact.py:227")

    def load_images(self):
        """Load and prepare images for the interface"""
        self.images = {}
        image_path = Path("resources/images")
        
        try:
            # Load ULTRON logo
            if (image_path / "ultron.jpg").exists():
                img = Image.open(image_path / "ultron.jpg")
                img = img.resize((80, 80), Image.Resampling.LANCZOS)
                self.images['ultron_logo'] = ImageTk.PhotoImage(img)
                self.log_action("ULTRON logo loaded successfully")
            
            # Load cyberpunk background (smaller and more transparent)
            cyberpunk_images = [
                "20250731_0131_Cyberpunk AI Interface_remix_01k1dz2gamf9xs8rtesb3nm7kw - Copy.png",
                "20250731_0131_Cyberpunk AI Interface_remix_01k1dz2ganefabrhpm3vdr2nt2 (1) - Copy.png",
                "2d6cde57-74ee-404e-acf2-91fb1db9eb8e - Copy.png",
                "backgroundDefault.jpg"
            ]
            
            for bg_name in cyberpunk_images:
                if (image_path / bg_name).exists():
                    bg_img = Image.open(image_path / bg_name)
                    bg_img = bg_img.resize((1200, 700), Image.Resampling.LANCZOS)
                    bg_img = bg_img.convert("RGBA")
                    bg_img.putalpha(20)  # Very transparent
                    self.images['background'] = ImageTk.PhotoImage(bg_img)
                    self.log_action(f"Background image loaded: {bg_name}")
                    break
            
            # Create enhanced status lights
            self.create_status_lights()
            
        except Exception as e:
            self.log_action(f"Error loading images: {e}")
            self.images = {}

    def create_status_lights(self):
        """Create Pokedex-style status lights"""
        for status in ['online', 'warning', 'error', 'offline']:
            colors = {
                'online': '#00ff41',    # Green
                'warning': '#ffaa00',   # Orange  
                'error': '#ff4444',     # Red
                'offline': '#666666'    # Gray
            }
            
            # Create status light
            img = Image.new('RGBA', (20, 20), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Outer glow (using valid RGB colors only)
            draw.ellipse([2, 2, 18, 18], fill=colors[status], outline=None)
            # Inner bright circle
            draw.ellipse([4, 4, 16, 16], fill=colors[status], outline='#ffffff', width=1)
            
            self.images[f'status_{status}'] = ImageTk.PhotoImage(img)

    def create_ultron_ui(self):
        """Create stunning Ultron-style interface with cyberpunk aesthetics"""
        self.log_action("🎨 Creating Ultron visual interface")
        
        # Configure main window with Ultron theme
        self.root.configure(bg='#0a0a0f')  # Deep space black
        self.root.attributes('-alpha', 0.98)  # Slight transparency for futuristic effect
        
        # Main container with Ultron styling
        main_container = create_ultron_frame(self.root, self.ultron_theme) if ULTRON_THEME_AVAILABLE else tk.Frame(self.root, bg='#0a0a0f')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Enhanced header with glowing effects
        header_frame = self.create_ultron_header(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Main content area with cyberpunk layout
        content_frame = create_ultron_frame(main_container, self.ultron_theme) if ULTRON_THEME_AVAILABLE else tk.Frame(main_container, bg='#16213e')
        content_frame.configure(relief=tk.SUNKEN, bd=2)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Left panel - Enhanced status with neural networks
        left_panel = self.create_ultron_status_panel(content_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 2), pady=5)
        
        # Center panel - Conversation with cyberpunk styling
        center_panel = self.create_ultron_conversation_panel(content_frame)
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2, pady=5)
        
        # Right panel - Controls with Ultron buttons
        right_panel = self.create_ultron_control_panel(content_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(2, 5), pady=5)
        
        # Enhanced command input with glowing effects
        self.create_ultron_command_panel(main_container)
        
        self.log_action("🎨 Ultron interface creation completed")

    def create_ultron_header(self, parent):
        """Create stunning Ultron-style header with animations"""
        header_frame = create_ultron_frame(parent, self.ultron_theme) if ULTRON_THEME_AVAILABLE else tk.Frame(parent, bg='#1a1a2e')
        header_frame.configure(relief=tk.RAISED, bd=2, height=100)
        header_frame.pack_propagate(False)
        
        # Header content with glow effects
        header_content = create_ultron_frame(header_frame, self.ultron_theme) if ULTRON_THEME_AVAILABLE else tk.Frame(header_frame, bg='#1a1a2e')
        header_content.pack(expand=True, fill=tk.BOTH, padx=20, pady=15)
        
        # Ultron logo with glow
        if 'ultron_logo' in self.images:
            logo_label = tk.Label(header_content, image=self.images['ultron_logo'], bg='#1a1a2e')
            logo_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Title section with cyberpunk fonts
        title_frame = create_ultron_frame(header_content, self.ultron_theme) if ULTRON_THEME_AVAILABLE else tk.Frame(header_content, bg='#1a1a2e')
        title_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Main title with glowing effect
        title_label = tk.Label(
            title_frame,
            text="◆ ULTRON v2.0 ◆",
            font=("Orbitron", 24, "bold"),
            fg='#ff0040',  # Ultron red
            bg='#1a1a2e'
        )
        title_label.pack(anchor='w')
        
        # Subtitle with cyberpunk style
        subtitle_label = tk.Label(
            title_frame,
            text="🤖 AI Assistant - Neural Network Online",
            font=("Consolas", 12, "bold"),
            fg='#00d4ff',  # Cyberpunk blue
            bg='#1a1a2e'
        )
        subtitle_label.pack(anchor='w')
        
        # System status indicator
        status_label = tk.Label(
            title_frame,
            text="● STATUS: FULLY OPERATIONAL",
            font=("Consolas", 10, "bold"),
            fg='#00ff88',  # Matrix green
            bg='#1a1a2e'
        )
        status_label.pack(anchor='w')
        
        # Add pulsing animation to title
        self.animate_title_glow(title_label)
        
        return header_frame

    def create_ultron_status_panel(self, parent):
        """Create enhanced status panel with neural network visualization"""
        panel = create_ultron_frame(parent, self.ultron_theme) if ULTRON_THEME_AVAILABLE else tk.Frame(parent, bg='#2c3e50')
        panel.configure(width=280, relief=tk.RAISED, bd=2)
        panel.pack_propagate(False)
        
        # Status panel header
        header = create_ultron_label(panel, "🔋 SYSTEM STATUS", self.ultron_theme) if ULTRON_THEME_AVAILABLE else tk.Label(panel, text="🔋 SYSTEM STATUS", bg='#2c3e50', fg='#ffffff')
        header.configure(font=("Consolas", 12, "bold"), fg='#ff0040')
        header.pack(pady=(10, 5))
        
        # Enhanced status panel with animations
        if ULTRON_THEME_AVAILABLE and self.ultron_theme:
            self.status_panel_system = UltronStatusPanel(panel, self.ultron_theme)
            status_frame = self.status_panel_system.create_status_panel()
        else:
            # Fallback status panel
            status_frame = tk.Frame(panel, bg='#1a1a2e', height=150)
            status_frame.pack(fill='x', padx=10, pady=5)
            status_frame.pack_propagate(False)
        
        # System metrics
        self.create_status_panel_metrics(panel)
        
        return panel

    def create_status_panel_metrics(self, panel):
        """Create enhanced system metrics display with specific status indicators"""
        metrics_frame = create_ultron_frame(panel, self.ultron_theme) if ULTRON_THEME_AVAILABLE else tk.Frame(panel, bg='#1a1a2e')
        metrics_frame.pack(fill='x', padx=10, pady=5)
        
        # System metrics header
        tk.Label(
            metrics_frame,
            text="⚡ ULTRON NEURAL STATUS",
            font=("Consolas", 10, "bold"),
            fg='#00d4ff',
            bg='#1a1a2e'
        ).pack(anchor='w')
        
        # Create enhanced status indicators for requested components
        self.status_labels = {}
        self.status_light_widgets = {}
        
        # Define status components with specific colors and meanings
        status_components = [
            ('ollama', '🤖 Ollama Engine'),
            ('modelname', '🧠 AI Model'),
            ('voice', '🎤 Voice System'),
            ('brain', '💭 Brain/Memory'),
            ('pochi', '🤖 POCHI Claude'),
            ('tools', '🔧 Tool System')
        ]
        
        for component_id, display_name in status_components:
            # Component frame
            comp_frame = tk.Frame(metrics_frame, bg='#1a1a2e')
            comp_frame.pack(fill='x', pady=2)
            
            # Status light (actual colored circle)
            light_frame = tk.Frame(comp_frame, bg='#1a1a2e', width=20, height=20)
            light_frame.pack(side='left', padx=(0, 8))
            light_frame.pack_propagate(False)
            
            # Create status light canvas
            light_canvas = tk.Canvas(light_frame, width=16, height=16, bg='#1a1a2e', highlightthickness=0)
            light_canvas.pack(expand=True)
            
            # Draw initial status light
            self.update_status_light(light_canvas, self.status_lights.get(component_id, 'red'))
            self.status_light_widgets[component_id] = light_canvas
            
            # Status label
            status_text = self.get_status_text(component_id)
            label = tk.Label(
                comp_frame,
                text=f"{display_name}: {status_text}",
                font=("Consolas", 9),
                fg=self.get_status_color(component_id),
                bg='#1a1a2e'
            )
            label.pack(side='left', anchor='w')
            self.status_labels[component_id] = label
        
        # Add live STT display
        stt_frame = tk.Frame(metrics_frame, bg='#16213e', relief=tk.SUNKEN, bd=1)
        stt_frame.pack(fill='x', pady=(10, 0))
        
        tk.Label(
            stt_frame,
            text="🎧 LIVE SPEECH RECOGNITION:",
            font=("Consolas", 9, "bold"),
            fg='#ff6b35',
            bg='#16213e'
        ).pack(anchor='w', padx=5, pady=(5, 0))
        
        # Live STT text display
        if self.current_stt_text:
            self.stt_display = tk.Label(
                stt_frame,
                textvariable=self.current_stt_text,
                font=("Consolas", 8),
                fg='#00ff88',
                bg='#16213e',
                wraplength=250,
                justify='left'
            )
        else:
            # Fallback if StringVar not ready
            self.stt_display = tk.Label(
                stt_frame,
                text="🎤 Click Voice to start speaking...",
                font=("Consolas", 8),
                fg='#00ff88',
                bg='#16213e',
                wraplength=250,
                justify='left'
            )
        self.stt_display.pack(anchor='w', padx=10, pady=5)

    def update_status_light(self, canvas, status):
        """Update visual status light with proper colors"""
        canvas.delete("all")
        
        # Define colors based on status
        colors = {
            'green': '#00ff41',    # Connected/Online
            'orange': '#ffaa00',   # Loading/Connecting  
            'red': '#ff4444'       # Error/Failed
        }
        
        color = colors.get(status, '#666666')
        
        # Draw filled circle
        canvas.create_oval(2, 2, 14, 14, fill=color, outline='#ffffff', width=1)
        
        # Add glow effect for online status
        if status == 'green':
            canvas.create_oval(4, 4, 12, 12, fill='#ffffff', outline='')

    def get_status_text(self, component_id):
        """Get human-readable status text"""
        status = self.status_lights.get(component_id, 'red')
        
        if status == 'green':
            if component_id == 'ollama':
                return "Connected"
            elif component_id == 'modelname':
                model = self.ollama_manager.current_model if self.ollama_manager else "Unknown"
                return f"Loaded: {model}"
            elif component_id == 'voice':
                return "Ready"
            elif component_id == 'brain':
                return "Active"
            elif component_id == 'pochi':
                return "Ready"
            elif component_id == 'tools':
                return "Available"
        elif status == 'orange':
            return "Connecting..."
        else:  # red
            return "Offline"

    def get_status_color(self, component_id):
        """Get text color based on status"""
        status = self.status_lights.get(component_id, 'red')
        colors = {
            'green': '#00ff88',
            'orange': '#ffaa00',
            'red': '#ff4444'
        }
        return colors.get(status, '#666666')

    def update_component_status(self, component_id, new_status):
        """Update a specific component's status"""
        self.status_lights[component_id] = new_status
        
        # Update visual light
        if component_id in self.status_light_widgets:
            self.update_status_light(self.status_light_widgets[component_id], new_status)
        
        # Update text
        if component_id in self.status_labels:
            status_text = self.get_status_text(component_id)
            color = self.get_status_color(component_id)
            
            components = {
                'ollama': '🤖 Ollama Engine',
                'modelname': '🧠 AI Model', 
                'voice': '🎤 Voice System',
                'brain': '💭 Brain/Memory',
                'pochi': '🤖 POCHI Claude',
                'tools': '🔧 Tool System'
            }
            
            display_name = components.get(component_id, component_id)
            self.status_labels[component_id].configure(
                text=f"{display_name}: {status_text}",
                fg=color
            )

    def create_ultron_conversation_panel(self, parent):
        """Create cyberpunk-style conversation panel"""
        panel = create_ultron_frame(parent, self.ultron_theme) if ULTRON_THEME_AVAILABLE else tk.Frame(parent, bg='#34495e')
        panel.configure(relief=tk.SUNKEN, bd=2)
        
        # Conversation header
        header = create_ultron_label(panel, "💬 NEURAL CONVERSATION LOG", self.ultron_theme) if ULTRON_THEME_AVAILABLE else tk.Label(panel, text="💬 CONVERSATION", bg='#34495e', fg='#ffffff')
        header.configure(font=("Consolas", 12, "bold"), fg='#00d4ff')
        header.pack(pady=(10, 5))
        
        # Enhanced conversation display
        self.conversation_frame = tk.Frame(panel, bg='#16213e')
        self.conversation_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Scrollable conversation area with cyberpunk styling
        self.conversation_text = scrolledtext.ScrolledText(
            self.conversation_frame,
            bg='#0a0a0f',
            fg='#00ff88',
            font=("Consolas", 10),
            insertbackground='#ff0040',
            selectbackground='#ff0040',
            selectforeground='#ffffff',
            relief='flat',
            bd=2,
            state='disabled',
            wrap='word'
        )
        self.conversation_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for different message types
        self.setup_conversation_tags()
        
        return panel

    def create_ultron_control_panel(self, parent):
        """Create Ultron-style control panel with glowing buttons"""
        panel = create_ultron_frame(parent, self.ultron_theme) if ULTRON_THEME_AVAILABLE else tk.Frame(parent, bg='#2c3e50')
        panel.configure(width=280, relief=tk.RAISED, bd=2)
        panel.pack_propagate(False)
        
        # Control panel header
        header = create_ultron_label(panel, "⚡ CONTROL MATRIX", self.ultron_theme) if ULTRON_THEME_AVAILABLE else tk.Label(panel, text="⚡ CONTROLS", bg='#2c3e50', fg='#ffffff')
        header.configure(font=("Consolas", 12, "bold"), fg='#ff0040')
        header.pack(pady=(10, 5))
        
        # Control sections - use existing control panel method
        self.create_control_panel_content(panel)
        
        return panel

    def create_control_panel_content(self, panel):
        """Create enhanced control panel content with push-to-talk voice control"""
        
        # Enhanced Voice Control Section
        voice_section = create_ultron_frame(panel, self.ultron_theme) if ULTRON_THEME_AVAILABLE else tk.Frame(panel, bg='#2c3e50')
        voice_section.pack(fill='x', padx=10, pady=5)
        
        # Voice section header
        voice_header = create_ultron_label(voice_section, "🎤 VOICE INTERFACE", self.ultron_theme) if ULTRON_THEME_AVAILABLE else tk.Label(voice_section, text="🎤 VOICE INTERFACE", bg='#2c3e50', fg='#ffffff')
        voice_header.configure(font=("Consolas", 10, "bold"), fg='#00d4ff')
        voice_header.pack(pady=(5, 5))
        
        # Push-to-talk voice button (main feature)
        self.voice_control_btn = tk.Button(
            voice_section,
            text="🎤 Voice",
            command=self.toggle_voice_recording,
            bg='#00ff88',  # Green when ready
            fg='#000000',
            font=("Consolas", 12, "bold"),
            relief='raised',
            bd=3,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        self.voice_control_btn.pack(fill='x', pady=5)
        
        # Voice test button (smaller, secondary)
        voice_test_button = create_ultron_button(
            voice_section, 
            "🔊 Test Voice", 
            self.test_voice_output, 
            self.ultron_theme
        ) if ULTRON_THEME_AVAILABLE else tk.Button(
            voice_section,
            text="🔊 Test Voice",
            command=self.test_voice_output,
            bg='#ff0040',
            fg='#ffffff',
            font=("Consolas", 9, "bold")
        )
        voice_test_button.pack(fill='x', padx=10, pady=2)
        
        # Separator
        tk.Frame(panel, height=2, bg='#ff0040').pack(fill='x', padx=10, pady=10)
        
        # Quick Actions Section
        actions_label = create_ultron_label(panel, "⚡ QUICK ACTIONS", self.ultron_theme) if ULTRON_THEME_AVAILABLE else tk.Label(panel, text="⚡ QUICK ACTIONS", bg='#2c3e50', fg='#ffffff')
        actions_label.configure(font=("Consolas", 10, "bold"), fg='#00d4ff')
        actions_label.pack(pady=(10, 5))
        
        # Action buttons
        actions = [
            ("🤖 Test Ollama", self.test_ollama_connection, '#00ff88'),
            ("🎯 Test POCHI", self.test_pochi_integration, '#ff6b35'),
            ("📸 Screenshot", self.take_screenshot, '#3498db'),
            ("💻 System Info", self.show_system_info, '#9b59b6'),
            ("📁 File Manager", self.open_file_manager, '#27ae60'),
            ("🔄 Refresh Status", self.force_status_update, '#e74c3c')
        ]
        
        for text, command, color in actions:
            btn = create_ultron_button(
                panel, 
                text, 
                command, 
                self.ultron_theme
            ) if ULTRON_THEME_AVAILABLE else tk.Button(
                panel,
                text=text,
                command=command,
                bg=color,
                fg='white',
                font=("Consolas", 9, "bold")
            )
            btn.pack(fill='x', padx=10, pady=1)
        
        # Model dropdown (enhanced)
        model_frame = create_ultron_frame(panel, self.ultron_theme) if ULTRON_THEME_AVAILABLE else tk.Frame(panel, bg='#2c3e50')
        model_frame.pack(fill='x', padx=10, pady=10)
        
        model_label = create_ultron_label(model_frame, "🤖 AI Model:", self.ultron_theme) if ULTRON_THEME_AVAILABLE else tk.Label(model_frame, text="🤖 AI Model:", bg='#2c3e50', fg='#ffffff')
        model_label.pack(anchor='w')
        
        # Get ALL available models (not just +8 more)
        available_models = self.get_all_available_models()
        
        self.model_var = tk.StringVar(value=available_models[0] if available_models else "qwen2.5vl:latest")
        self.model_dropdown = ttk.Combobox(model_frame, textvariable=self.model_var, state="readonly")
        self.model_dropdown['values'] = tuple(available_models)
        self.model_dropdown.pack(fill='x', pady=2)
        self.model_dropdown.bind('<<ComboboxSelected>>', self.update_llm_model)
        
        # POCHI Controls (if available)
        if POCHI_AVAILABLE and hasattr(self.agent, 'pochi') and self.agent.pochi:
            pochi_frame = create_ultron_frame(panel, self.ultron_theme) if ULTRON_THEME_AVAILABLE else tk.Frame(panel, bg='#2c3e50')
            pochi_frame.pack(fill='x', padx=10, pady=5)
            
            pochi_label = create_ultron_label(pochi_frame, "🤖 POCHI (Claude):", self.ultron_theme) if ULTRON_THEME_AVAILABLE else tk.Label(pochi_frame, text="🤖 POCHI:", bg='#2c3e50', fg='#ffffff')
            pochi_label.pack(anchor='w')
            
            # POCHI model selector
            pochi_models = []
            for model in self.agent.pochi.get_available_models():
                name = model.get('name', model.get('model', 'Claude'))
                pochi_models.append(name)
            
            if pochi_models:
                self.pochi_model_var = tk.StringVar(value=pochi_models[0])
                pochi_combo = ttk.Combobox(pochi_frame, textvariable=self.pochi_model_var, state="readonly")
                pochi_combo['values'] = tuple(pochi_models)
                pochi_combo.pack(fill='x', pady=2)
                pochi_combo.bind("<<ComboboxSelected>>", self.update_pochi_model)
                
                # POCHI status indicator
                pochi_status = "🟢 Ready" if self.agent.pochi.is_available() else "🔴 Not Available"
                status_label = tk.Label(pochi_frame, text=pochi_status, font=("Consolas", 8), 
                                      fg='#00ff88' if self.agent.pochi.is_available() else '#ff0040',
                                      bg='#2c3e50')
                status_label.pack(anchor='w')

    def toggle_voice_recording(self):
        """Enhanced push-to-talk voice recording with visual feedback"""
        if not self.voice_manager and not (hasattr(self.agent, 'voice') and self.agent.voice):
            self.add_to_conversation("SYSTEM", "❌ Voice system not available")
            self.update_component_status('voice', 'red')
            return
        
        if not self.recording:
            # Start recording
            self.recording = True
            self.voice_control_btn.configure(
                text="🛑 End Dialogue",
                bg='#ff4444',  # Red when recording
                fg='#ffffff'
            )
            self.set_stt_text("🎤 Listening... Speak now!")
            self.update_component_status('voice', 'orange')  # Show active listening
            
            self.add_to_conversation("SYSTEM", "🎤 Voice recording started - speak now!")
            self.log_action("Voice recording started")
            
            # Start recording in background thread
            threading.Thread(target=self.record_voice_command, daemon=True).start()
            
        else:
            # Stop recording
            self.recording = False
            self.voice_control_btn.configure(
                text="🎤 Voice",
                bg='#00ff88',  # Green when ready
                fg='#000000'
            )
            self.set_stt_text("🔄 Processing speech...")
            self.log_action("Voice recording stopped")

    def record_voice_command(self):
        """Record voice command with live STT feedback"""
        try:
            collected_text = ""
            
            while self.recording:
                try:
                    # Use a simpler approach with available voice methods
                    if hasattr(self.agent, 'voice') and self.agent.voice:
                        # Fallback to original voice system with short timeout
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        
                        # Try to get speech with short timeout for responsiveness
                        text = loop.run_until_complete(self.agent.voice.listen(timeout=1))
                        loop.close()
                        
                        if text and text.strip():
                            collected_text += text + " "
                            self.root.after(0, self.set_stt_text, f"🎤 Hearing: {collected_text}")
                    else:
                        # If no voice system available, break
                        break
                        
                except Exception as e:
                    self.log_action(f"Voice recording error: {e}")
                    time.sleep(0.1)
                    
                time.sleep(0.1)  # Small delay for responsiveness
            
            # Process the collected text when recording stops
            if collected_text.strip():
                final_text = collected_text.strip()
                self.root.after(0, self.process_voice_command_smooth, final_text)
            else:
                self.root.after(0, self.set_stt_text, "🎤 No speech detected. Click Voice to try again.")
                self.root.after(0, self.update_component_status, 'voice', 'green')
                
        except Exception as e:
            self.log_action(f"Voice recording failed: {e}")
            self.root.after(0, self.add_to_conversation, "SYSTEM", f"❌ Voice recording error: {e}")
            self.root.after(0, self.set_stt_text, "❌ Recording failed")
            self.root.after(0, self.update_component_status, 'voice', 'red')

    def process_voice_command_smooth(self, command):
        """Process voice command with smooth, responsive UI updates"""
        self.set_stt_text(f"✅ Heard: {command}")
        self.add_to_conversation("USER", f"🎤 {command}")
        self.update_component_status('voice', 'green')  # Back to ready
        
        # Show processing indicator
        self.is_processing = True
        self.set_stt_text("🤖 ULTRON is thinking...")
        self.update_component_status('brain', 'orange')
        
        # Process in background to keep UI responsive
        def process_in_background():
            try:
                # Update model status to show it's working
                self.root.after(0, self.update_component_status, 'modelname', 'orange')
                
                # Process with agent (non-blocking)
                response = self.agent.handle_text(command)
                
                # Update UI with response
                self.root.after(0, self.add_to_conversation, "ULTRON", response)
                self.root.after(0, self.set_stt_text, "🎤 Click Voice to speak again...")
                self.root.after(0, self.update_component_status, 'brain', 'green')
                self.root.after(0, self.update_component_status, 'modelname', 'green')
                
                # Trigger voice output if enabled
                if self.voice_manager or (hasattr(self.agent, 'voice') and self.agent.voice):
                    threading.Thread(target=self.speak_response_smooth, args=(response,), daemon=True).start()
                
                self.is_processing = False
                
            except Exception as e:
                error_msg = f"Error processing command: {str(e)}"
                self.root.after(0, self.add_to_conversation, "SYSTEM", f"❌ {error_msg}")
                self.root.after(0, self.set_stt_text, "❌ Processing failed")
                self.root.after(0, self.update_component_status, 'brain', 'red')
                self.root.after(0, self.update_component_status, 'modelname', 'red')
                self.log_action(f"Command error: {str(e)}")
                self.is_processing = False
        
        threading.Thread(target=process_in_background, daemon=True).start()

    def speak_response_smooth(self, text):
        """Enhanced smooth voice response with status updates"""
        try:
            self.root.after(0, self.update_component_status, 'voice', 'orange')  # Speaking
            self.log_action(f"Speaking response: {text[:30]}...")
            
            if self.voice_manager and hasattr(self.voice_manager, 'speak'):
                self.voice_manager.speak(text)
            elif hasattr(self.agent, 'voice') and self.agent.voice:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.agent.voice.speak(text))
                loop.close()
            else:
                # Fallback TTS
                try:
                    import pyttsx3
                    engine = pyttsx3.init()
                    engine.say(text)
                    engine.runAndWait()
                except:
                    pass
            
            self.root.after(0, self.update_component_status, 'voice', 'green')  # Ready
            self.log_action("Voice response completed")
            
        except Exception as e:
            self.log_action(f"Voice response error: {e}")
            self.root.after(0, self.update_component_status, 'voice', 'red')

    def get_all_available_models(self):
        """Get ALL available Ollama models (not truncated)"""
        models = ["qwen2.5vl:latest"]  # Primary model first
        
        try:
            if self.ollama_manager:
                # Refresh connection to get latest models
                self.ollama_manager.check_connection()
                if hasattr(self.ollama_manager, 'available_models') and self.ollama_manager.available_models:
                    # Add all models, ensuring primary is first
                    for model in self.ollama_manager.available_models:
                        if model not in models:
                            models.append(model)
                else:
                    # Fallback list if API call fails
                    fallback_models = [
                        "qwen2.5:latest", "llama3.2:latest", "hermes3:latest", 
                        "phi3:latest", "codellama:latest", "mistral:latest",
                        "neural-chat:latest", "starling-lm:latest"
                    ]
                    models.extend([m for m in fallback_models if m not in models])
            else:
                # Default models if ollama manager not available
                models.extend([
                    "qwen2.5:latest", "llama3.2:latest", "hermes3:latest", "phi3:latest"
                ])
                
        except Exception as e:
            self.log_action(f"Error getting models: {e}")
            
        return models

    def force_status_update(self):
        """Force refresh of all status information and update visual indicators"""
        self.add_to_conversation("SYSTEM", "🔄 Refreshing system status...")
        
        # Update Ollama status
        if self.ollama_manager:
            self.update_component_status('ollama', 'orange')  # connecting
            if self.ollama_manager.check_connection():
                self.update_component_status('ollama', 'green')  # connected
                self.update_component_status('modelname', 'green')  # model ready
            else:
                self.update_component_status('ollama', 'red')  # failed
                self.update_component_status('modelname', 'red')  # model failed
        
        # Update POCHI status
        if POCHI_AVAILABLE and hasattr(self.agent, 'pochi'):
            try:
                if self.agent.pochi.is_available():
                    self.update_component_status('pochi', 'green')
                else:
                    self.update_component_status('pochi', 'red')
            except:
                self.update_component_status('pochi', 'red')
        
        # Update voice status
        if self.voice_manager:
            self.update_component_status('voice', 'green')
        elif hasattr(self.agent, 'voice') and self.agent.voice:
            self.update_component_status('voice', 'orange')
        else:
            self.update_component_status('voice', 'red')
        
        # Update brain/memory status
        self.update_component_status('brain', 'green' if hasattr(self.agent, 'brain') else 'red')
        
        # Update tools status
        self.update_component_status('tools', 'green' if hasattr(self.agent, 'tools') else 'red')
        
        # Refresh Ollama models
        models = self.get_all_available_models()
        if hasattr(self, 'model_dropdown'):
            self.model_dropdown['values'] = tuple(models)
        
        self.add_to_conversation("SYSTEM", "✅ Status refresh completed")
        self.set_stt_text("🎤 Click Voice to speak to ULTRON...")

    def test_pochi_integration(self):
        """Test POCHI integration and interaction"""
        if not POCHI_AVAILABLE or not hasattr(self.agent, 'pochi'):
            self.add_to_conversation("SYSTEM", "❌ POCHI not available")
            return
            
        self.add_to_conversation("SYSTEM", "🤖 Testing POCHI integration...")
        
        try:
            # Test POCHI availability
            if self.agent.pochi.is_available():
                # Send test message to POCHI
                test_msg = "Hello POCHI! Please introduce yourself briefly."
                
                # Use threading to avoid blocking GUI
                def test_pochi():
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        response = loop.run_until_complete(self.agent.pochi.chat_with_pochi(test_msg))
                        loop.close()
                        
                        self.root.after(0, self.add_to_conversation, "POCHI", response)
                        self.root.after(0, self.add_to_conversation, "SYSTEM", "✅ POCHI test successful!")
                    except Exception as e:
                        self.root.after(0, self.add_to_conversation, "SYSTEM", f"❌ POCHI test failed: {e}")
                
                threading.Thread(target=test_pochi, daemon=True).start()
                
            else:
                self.add_to_conversation("SYSTEM", "❌ POCHI not properly configured")
                
        except Exception as e:
            self.add_to_conversation("SYSTEM", f"❌ POCHI test error: {e}")

    def take_screenshot(self):
        """Take a screenshot and save it"""
        try:
            import pyautogui
            import os
            from datetime import datetime
            
            # Create screenshots directory if it doesn't exist
            screenshot_dir = os.path.join(os.getcwd(), "screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)
            
            # Take screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = os.path.join(screenshot_dir, filename)
            
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            
            self.add_to_conversation("SYSTEM", f"📸 Screenshot saved: {filename}")
            self.log_action(f"Screenshot saved: {filepath}")
            
            # If vision system available, analyze the screenshot
            if hasattr(self.agent, 'vision') and self.agent.vision:
                threading.Thread(target=self.analyze_screenshot, args=(filepath,), daemon=True).start()
                
        except ImportError:
            self.add_to_conversation("SYSTEM", "❌ PyAutoGUI not installed. Install with: pip install pyautogui")
        except Exception as e:
            self.add_to_conversation("SYSTEM", f"❌ Screenshot failed: {e}")

    def analyze_screenshot(self, filepath):
        """Analyze screenshot with vision system"""
        try:
            if hasattr(self.agent, 'vision') and self.agent.vision:
                # Analyze the screenshot
                description = self.agent.vision.analyze_image(filepath)
                if description:
                    self.root.after(0, self.add_to_conversation, "VISION", f"📸 Screenshot analysis: {description}")
        except Exception as e:
            self.root.after(0, self.add_to_conversation, "SYSTEM", f"⚠️ Screenshot analysis failed: {e}")

    def show_system_info(self):
        """Display comprehensive system information"""
        try:
            import platform
            import psutil
            import os
            
            # Collect system info
            info = []
            info.append(f"🖥️ System: {platform.system()} {platform.release()}")
            info.append(f"💻 Machine: {platform.machine()}")
            info.append(f"🔧 Processor: {platform.processor()}")
            info.append(f"🐍 Python: {platform.python_version()}")
            
            # Memory info
            memory = psutil.virtual_memory()
            info.append(f"💾 RAM: {memory.total // (1024**3)}GB total, {memory.available // (1024**3)}GB available")
            
            # CPU info
            info.append(f"⚡ CPU: {psutil.cpu_count(logical=False)} cores, {psutil.cpu_count()} threads")
            info.append(f"📊 CPU Usage: {psutil.cpu_percent()}%")
            
            # Disk info
            disk = psutil.disk_usage('/')
            info.append(f"💽 Disk: {disk.total // (1024**3)}GB total, {disk.free // (1024**3)}GB free")
            
            # Network info
            try:
                network = psutil.net_io_counters()
                info.append(f"🌐 Network: {network.bytes_sent // (1024**2)}MB sent, {network.bytes_recv // (1024**2)}MB received")
            except:
                info.append("🌐 Network: Info not available")
            
            # Ollama status
            if self.ollama_manager:
                if self.ollama_manager.is_connected:
                    info.append(f"🤖 Ollama: Connected ({len(self.ollama_manager.available_models)} models)")
                    info.append(f"📝 Current Model: {self.ollama_manager.current_model or 'None'}")
                else:
                    info.append("🤖 Ollama: Not connected")
            
            # POCHI status
            if POCHI_AVAILABLE and hasattr(self.agent, 'pochi'):
                pochi_status = "Available" if self.agent.pochi.is_available() else "Not Available"
                info.append(f"🤖 POCHI: {pochi_status}")
            
            # Voice system status
            voice_status = "Available" if (self.voice_manager or (hasattr(self.agent, 'voice') and self.agent.voice)) else "Not Available"
            info.append(f"🎤 Voice System: {voice_status}")
            
            # Display info
            system_info = "\n".join(info)
            self.add_to_conversation("SYSTEM", f"💻 SYSTEM INFORMATION:\n{system_info}")
            
        except ImportError as e:
            self.add_to_conversation("SYSTEM", f"❌ Missing dependency for system info: {e}")
        except Exception as e:
            self.add_to_conversation("SYSTEM", f"❌ System info error: {e}")

    def open_file_manager(self):
        """Open file manager in current directory"""
        try:
            import subprocess
            import os
            import platform
            
            current_dir = os.getcwd()
            system = platform.system()
            
            if system == "Windows":
                subprocess.run(['explorer', current_dir])
                self.add_to_conversation("SYSTEM", f"📁 Opened file manager: {current_dir}")
            elif system == "Darwin":  # macOS
                subprocess.run(['open', current_dir])
                self.add_to_conversation("SYSTEM", f"📁 Opened file manager: {current_dir}")
            elif system == "Linux":
                # Try common Linux file managers
                for fm in ['nautilus', 'dolphin', 'thunar', 'pcmanfm', 'nemo']:
                    try:
                        subprocess.run([fm, current_dir])
                        self.add_to_conversation("SYSTEM", f"📁 Opened file manager: {current_dir}")
                        break
                    except FileNotFoundError:
                        continue
                else:
                    self.add_to_conversation("SYSTEM", "❌ No suitable file manager found")
            else:
                self.add_to_conversation("SYSTEM", f"❌ Unsupported system: {system}")
                
        except Exception as e:
            self.add_to_conversation("SYSTEM", f"❌ File manager error: {e}")

    def update_pochi_model(self, event=None):
        """Update selected POCHI model"""
        try:
            if hasattr(self, 'pochi_model_var') and hasattr(self.agent, 'pochi'):
                selected_model = self.pochi_model_var.get()
                if selected_model and self.agent.pochi:
                    # Switch POCHI model
                    self.agent.pochi.switch_model(selected_model)
                    self.add_to_conversation("SYSTEM", f"🤖 POCHI model switched to: {selected_model}")
                    self.log_action(f"POCHI model changed to: {selected_model}")
        except Exception as e:
            self.add_to_conversation("SYSTEM", f"❌ POCHI model switch failed: {e}")
            self.log_action(f"POCHI model switch error: {e}")

    def create_ultron_command_panel(self, parent):
        """Create enhanced command input with cyberpunk styling"""
        command_frame = create_ultron_frame(parent, self.ultron_theme) if ULTRON_THEME_AVAILABLE else tk.Frame(parent, bg='#2c3e50')
        command_frame.configure(relief=tk.RAISED, bd=2, height=80)
        command_frame.pack(fill=tk.X)
        command_frame.pack_propagate(False)
        
        # Command header
        header_frame = create_ultron_frame(command_frame, self.ultron_theme) if ULTRON_THEME_AVAILABLE else tk.Frame(command_frame, bg='#2c3e50')
        header_frame.pack(fill='x', padx=15, pady=(10, 5))
        
        command_label = create_ultron_label(header_frame, "⌨️ NEURAL COMMAND INTERFACE", self.ultron_theme) if ULTRON_THEME_AVAILABLE else tk.Label(header_frame, text="⌨️ COMMAND", bg='#2c3e50', fg='#ffffff')
        command_label.configure(font=("Consolas", 11, "bold"), fg='#00d4ff')
        command_label.pack(side='left')
        
        # Input area
        input_frame = create_ultron_frame(command_frame, self.ultron_theme) if ULTRON_THEME_AVAILABLE else tk.Frame(command_frame, bg='#2c3e50')
        input_frame.pack(fill='x', padx=15, pady=(0, 10))
        
        # Enhanced command entry
        self.command_entry = tk.Entry(
            input_frame,
            bg='#16213e',
            fg='#ffffff',
            insertbackground='#ff0040',
            font=("Consolas", 11),
            relief='flat',
            bd=3,
            highlightbackground='#ff0040',
            highlightcolor='#ff0040',
            highlightthickness=2
        )
        self.command_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.command_entry.bind('<Return>', self.process_text_command)
        
        # Enhanced send button
        send_button = create_ultron_button(
            input_frame, 
            "🚀 EXECUTE", 
            self.process_text_command, 
            self.ultron_theme
        ) if ULTRON_THEME_AVAILABLE else tk.Button(
            input_frame,
            text="🚀 SEND",
            command=self.process_text_command,
            bg='#ff0040',
            fg='#ffffff',
            font=("Consolas", 10, "bold")
        )
        send_button.pack(side='right')
        
        return command_frame

    def animate_title_glow(self, label):
        """Animate glowing effect on title"""
        def update_glow():
            if hasattr(self, 'glow_phase'):
                self.glow_phase += 0.1
            else:
                self.glow_phase = 0
                
            # Calculate glow intensity
            intensity = abs(math.sin(self.glow_phase)) * 0.5 + 0.5
            
            # Create glow color
            red_component = int(255 * intensity)
            glow_color = f"#{red_component:02x}0040"
            
            try:
                label.configure(fg=glow_color)
                self.root.after(50, update_glow)
            except:
                pass  # Widget may be destroyed
                
        update_glow()

    def setup_conversation_tags(self):
        """Setup text tags for different message types"""
        # ULTRON messages - red theme
        self.conversation_text.tag_configure(
            "ultron",
            foreground="#ff0040",
            font=("Consolas", 10, "bold")
        )
        
        # User messages - blue theme
        self.conversation_text.tag_configure(
            "user",
            foreground="#00d4ff",
            font=("Consolas", 10)
        )
        
        # System messages - green theme
        self.conversation_text.tag_configure(
            "system",
            foreground="#00ff88",
            font=("Consolas", 9)
        )
        
        # Error messages - orange theme
        self.conversation_text.tag_configure(
            "error",
            foreground="#ff6b35",
            font=("Consolas", 9, "bold")
        )

    def create_status_panel(self, parent):
        """Create compact status panel"""
        # Header
        tk.Label(
            parent,
            text="⚡ SYSTEM STATUS",
            font=("Orbitron", 10, "bold"),
            fg='#00ff41',
            bg='#2c3e50'
        ).pack(pady=(10, 5))
        
        # Status variables
        self.status_vars = {
            'cpu': tk.StringVar(value="CPU: 0%"),
            'memory': tk.StringVar(value="Memory: 0%"),
            'disk': tk.StringVar(value="Disk: 0%"),
            'gpu0': tk.StringVar(value="GPU 0: N/A"),
            'gpu1': tk.StringVar(value="GPU 1: N/A"),
            'network': tk.StringVar(value="Network: 0 KB/s"),
            'voice': tk.StringVar(value="Voice: Ready"),
            'ai': tk.StringVar(value="AI: Online"),
            'ollama': tk.StringVar(value="Ollama: Checking...")
        }
        
        self.progress_bars = {}
        self.status_light_labels = {}
        
        # Scrollable status frame
        status_canvas = tk.Canvas(parent, bg='#2c3e50', highlightthickness=0, height=350)
        status_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=status_canvas.yview)
        status_frame = tk.Frame(status_canvas, bg='#2c3e50')
        
        status_frame.bind(
            "<Configure>",
            lambda e: status_canvas.configure(scrollregion=status_canvas.bbox("all"))
        )
        
        status_canvas.create_window((0, 0), window=status_frame, anchor="nw")
        status_canvas.configure(yscrollcommand=status_scrollbar.set)
        
        status_canvas.pack(side="left", fill="both", expand=True, padx=5)
        status_scrollbar.pack(side="right", fill="y")
        
        # Create status items
        for key, var in self.status_vars.items():
            item_frame = tk.Frame(status_frame, bg='#2c3e50')
            item_frame.pack(fill=tk.X, pady=2, padx=5)
            
            # Status light and label
            light_frame = tk.Frame(item_frame, bg='#2c3e50')
            light_frame.pack(fill=tk.X)
            
            # Status light
            status_light = tk.Label(
                light_frame,
                image=self.images.get('status_online', ''),
                bg='#2c3e50'
            )
            status_light.pack(side=tk.LEFT, padx=(0, 5))
            self.status_light_labels[key] = status_light
            
            # Status text
            tk.Label(
                light_frame,
                textvariable=var,
                font=("Courier New", 8),
                fg='#ecf0f1',
                bg='#2c3e50',
                anchor='w'
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Progress bar for numeric metrics
            if key in ['cpu', 'memory', 'disk', 'gpu0', 'gpu1']:
                progress = ttk.Progressbar(
                    item_frame,
                    mode='determinate',
                    length=200,
                    style='Compact.Horizontal.TProgressbar'
                )
                progress.pack(fill=tk.X, pady=(2, 0))
                self.progress_bars[key] = progress
        
        # Configure compact progress bar style
        style = ttk.Style()
        style.configure('Compact.Horizontal.TProgressbar',
                       background='#00ff41',
                       troughcolor='#34495e',
                       borderwidth=1,
                       relief='flat')

    def create_conversation_panel(self, parent):
        """Create conversation panel"""
        # Header
        tk.Label(
            parent,
            text="💬 CONVERSATION LOG",
            font=("Orbitron", 10, "bold"),
            fg='#00ff41',
            bg='#34495e'
        ).pack(pady=(10, 5))
        
        # Conversation display
        conv_frame = tk.Frame(parent, bg='#2c3e50', relief=tk.SUNKEN, bd=1)
        conv_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.conversation_text = scrolledtext.ScrolledText(
            conv_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg='#2c3e50',
            fg='#ecf0f1',
            font=("Consolas", 9),
            insertbackground='#00ff41',
            selectbackground='#3498db',
            selectforeground='white',
            relief=tk.FLAT,
            padx=5,
            pady=5
        )
        self.conversation_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Text tags
        self.conversation_text.tag_configure("user", foreground="#3498db", font=("Consolas", 9, "bold"))
        self.conversation_text.tag_configure("ultron", foreground="#00ff41", font=("Consolas", 9, "bold"))
        self.conversation_text.tag_configure("system", foreground="#e67e22", font=("Consolas", 8, "italic"))
        self.conversation_text.tag_configure("timestamp", foreground="#95a5a6", font=("Consolas", 8))

    def create_control_panel(self, parent):
        """Create compact control panel"""
        # Voice controls
        tk.Label(
            parent,
            text="🎤 VOICE CONTROLS",
            font=("Orbitron", 10, "bold"),
            fg='#00ff41',
            bg='#2c3e50'
        ).pack(pady=(10, 5))
        
        # Voice button
        self.voice_btn = tk.Button(
            parent,
            text="🎤 Start Listening",
            command=self.toggle_listening,
            bg='#27ae60',
            fg='white',
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=10,
            pady=8,
            cursor='hand2'
        )
        self.voice_btn.pack(fill=tk.X, padx=5, pady=5)
        
        # Test voice button
        test_btn = tk.Button(
            parent,
            text="🔊 Test Voice",
            command=self.test_voice_output,
            bg='#8e44ad',
            fg='white',
            font=("Segoe UI", 8, "bold"),
            relief=tk.FLAT,
            padx=10,
            pady=5,
            cursor='hand2'
        )
        test_btn.pack(fill=tk.X, padx=5, pady=(0, 10))
        
        # Configuration
        tk.Label(
            parent,
            text="⚙️ CONFIGURATION",
            font=("Orbitron", 10, "bold"),
            fg='#00ff41',
            bg='#2c3e50'
        ).pack(pady=(10, 5))
        
        # Compact config frame
        config_frame = tk.Frame(parent, bg='#2c3e50')
        config_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Voice engine
        tk.Label(config_frame, text="Voice Engine:", bg='#2c3e50', fg='#ecf0f1', 
                font=("Segoe UI", 8)).pack(anchor='w')
        
        self.voice_engine_var = tk.StringVar(value=self.agent.config.data.get("voice_engine", "pyttsx3"))
        voice_combo = ttk.Combobox(config_frame, textvariable=self.voice_engine_var, 
                                  state="readonly", font=("Segoe UI", 8), height=3)
        voice_combo['values'] = ("pyttsx3", "elevenlabs", "openai")
        voice_combo.pack(fill=tk.X, pady=(0, 5))
        voice_combo.bind("<<ComboboxSelected>>", self.update_voice_engine)
        
        # LLM model
        tk.Label(config_frame, text="LLM Model:", bg='#2c3e50', fg='#ecf0f1',
                font=("Segoe UI", 8)).pack(anchor='w')
        
        # Get available models from Ollama
        available_models = ["qwen2.5:latest", "llama3.2:latest", "hermes3:latest", "phi3:latest"]
        if self.ollama_manager and self.ollama_manager.available_models:
            available_models = self.ollama_manager.available_models + available_models
            # Remove duplicates while preserving order
            seen = set()
            available_models = [x for x in available_models if not (x in seen or seen.add(x))]
        
        current_model = "qwen2.5:latest"
        if self.ollama_manager and self.ollama_manager.current_model:
            current_model = self.ollama_manager.current_model
        elif hasattr(self.agent, 'config'):
            current_model = self.agent.config.data.get("llm_model", "qwen2.5:latest")
        
        self.llm_model_var = tk.StringVar(value=current_model)
        llm_combo = ttk.Combobox(config_frame, textvariable=self.llm_model_var, 
                               state="readonly", font=("Segoe UI", 8), height=5)
        llm_combo['values'] = tuple(available_models)
        llm_combo.pack(fill=tk.X, pady=(0, 5))
        llm_combo.bind("<<ComboboxSelected>>", self.update_llm_model)
        
        # POCHI Controls
        if POCHI_AVAILABLE and hasattr(self.agent, 'pochi') and self.agent.pochi:
            tk.Label(
                config_frame,
                text="🤖 POCHI (Claude)",
                font=("Orbitron", 8, "bold"),
                fg='#ff6b35',
                bg='#2c3e50'
            ).pack(anchor='w', pady=(10, 2))
            
            pochi_frame = tk.Frame(config_frame, bg='#2c3e50')
            pochi_frame.pack(fill=tk.X, pady=(0, 5))
            
            # POCHI model selector
            pochi_models = []
            for model in self.agent.pochi.get_available_models():
                name = model.get('name', model.get('model', 'Claude'))
                pochi_models.append(name)
            
            self.pochi_model_var = tk.StringVar(value=pochi_models[0] if pochi_models else "Claude")
            pochi_combo = ttk.Combobox(pochi_frame, textvariable=self.pochi_model_var,
                                     state="readonly", font=("Segoe UI", 8), height=3)
            pochi_combo['values'] = tuple(pochi_models)
            pochi_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
            pochi_combo.bind("<<ComboboxSelected>>", self.update_pochi_model)
            
            # POCHI status
            pochi_status = "🟢 Ready" if self.agent.pochi.is_available() else "🔴 Not Available"
            tk.Label(pochi_frame, text=pochi_status, font=("Segoe UI", 7), 
                    fg='#00ff41' if self.agent.pochi.is_available() else '#ff4757',
                    bg='#2c3e50').pack(side=tk.RIGHT, padx=(5, 0))
        
        # Quick actions
        tk.Label(
            parent,
            text="⚙️ QUICK ACTIONS",
            font=("Orbitron", 9, "bold"),
            fg='#00ff41',
            bg='#2c3e50'
        ).pack(pady=(10, 5))
        
        actions = [
            ("📸 Screenshot", self.take_screenshot, '#3498db'),
            ("💻 System Info", self.show_system_info, '#9b59b6'),
            ("📁 Files", self.open_file_manager, '#27ae60'),
            ("🤖 Test Ollama", self.test_ollama_connection, '#e74c3c')
        ]
        
        for text, command, color in actions:
            btn = tk.Button(
                parent,
                text=text,
                command=command,
                bg=color,
                fg='white',
                font=("Segoe UI", 8, "bold"),
                relief=tk.FLAT,
                padx=5,
                pady=3,
                cursor='hand2'
            )
            btn.pack(fill=tk.X, padx=5, pady=1)

    def create_command_panel(self, parent):
        """Create compact command input panel"""
        command_frame = tk.Frame(parent, bg='#e67e22', relief=tk.RAISED, bd=2, height=60)
        command_frame.pack(fill=tk.X)
        command_frame.pack_propagate(False)
        
        # Command input
        input_frame = tk.Frame(command_frame, bg='#e67e22')
        input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(
            input_frame,
            text="⌨️ COMMAND:",
            font=("Orbitron", 9, "bold"),
            bg='#e67e22',
            fg='white'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        entry_frame = tk.Frame(input_frame, bg='#2c3e50', relief=tk.SUNKEN, bd=1)
        entry_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.command_entry = tk.Entry(
            entry_frame,
            font=("Consolas", 10),
            bg='#2c3e50',
            fg='#ecf0f1',
            insertbackground='#00ff41',
            relief=tk.FLAT,
            bd=0
        )
        self.command_entry.pack(fill=tk.BOTH, expand=True, padx=5, pady=3)
        self.command_entry.bind('<Return>', self.process_text_command)
        
        execute_btn = tk.Button(
            input_frame,
            text="▶ EXECUTE",
            command=self.process_text_command,
            bg='#27ae60',
            fg='white',
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor='hand2'
        )
        execute_btn.pack(side=tk.RIGHT)

    def add_to_conversation(self, speaker, message):
        """Add message to conversation log"""
        self.conversation_text.config(state=tk.NORMAL)
        
        timestamp = time.strftime("%H:%M:%S")
        
        # Add timestamp
        self.conversation_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # Add speaker
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
        self.conversation_text.insert(tk.END, f"{icon}{message}\n")
        self.conversation_text.config(state=tk.DISABLED)
        self.conversation_text.see(tk.END)
        
        # Log the conversation
        self.log_action(f"Conversation - {speaker}: {message[:50]}...")
        
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
        
        self.log_action(f"Processing command: {command}")
        self.add_to_conversation("USER", command)
        self.command_entry.delete(0, tk.END)
        
        # Process with agent
        try:
            response = self.agent.handle_text(command)
            self.add_to_conversation("ULTRON", response)
            
            # Trigger voice output if enabled
            if self.agent.voice:
                threading.Thread(target=self.speak_async, args=(response,), daemon=True).start()
                
        except Exception as e:
            error_msg = f"Error processing command: {str(e)}"
            self.add_to_conversation("SYSTEM", error_msg)
            self.log_action(f"Command error: {str(e)}")

    def speak_async(self, text):
        """Enhanced async voice output using voice manager"""
        try:
            self.log_action(f"Attempting voice output: {text[:30]}...")
            
            if self.voice_manager:
                # Use enhanced voice manager
                self.voice_manager.speak(text, async_mode=True)
                self.log_action("Voice output completed successfully")
            elif hasattr(self.agent, 'voice') and self.agent.voice:
                # Fallback to original voice system
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.agent.voice.speak(text))
                loop.close()
                self.log_action("Voice output completed successfully")
            else:
                # Console fallback
                self.log_action(f"Voice fallback - Console output: {text}")
                print(f"[ULTRON VOICE]: {text} - gui_compact.py:1678")
                
        except Exception as e:
            self.log_action(f"Voice output error: {str(e)}")
            print(f"[ULTRON VOICE FALLBACK]: {text} - gui_compact.py:1682")

    def test_voice_output(self):
        """Enhanced voice test using voice manager"""
        test_message = "ULTRON voice system test. Neural networks operational. All systems ready."
        self.add_to_conversation("SYSTEM", f"🔊 Testing voice: {test_message}")
        self.log_action("Voice test initiated")
        
        try:
            if self.voice_manager and hasattr(self.voice_manager, 'speak'):
                # Test with enhanced voice manager
                threading.Thread(target=self.voice_manager.speak, args=(test_message,), daemon=True).start()
                self.add_to_conversation("SYSTEM", "✅ Voice test initiated with voice manager!")
            elif hasattr(self.agent, 'voice') and self.agent.voice:
                # Fallback to agent voice system
                def test_voice():
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(self.agent.voice.speak(test_message))
                        loop.close()
                        self.root.after(0, self.add_to_conversation, "SYSTEM", "✅ Voice test successful!")
                    except Exception as e:
                        self.root.after(0, self.add_to_conversation, "SYSTEM", f"❌ Voice test failed: {e}")
                
                threading.Thread(target=test_voice, daemon=True).start()
                self.add_to_conversation("SYSTEM", "🔊 Voice test initiated...")
            else:
                # Try system TTS as last resort
                try:
                    import pyttsx3
                    engine = pyttsx3.init()
                    engine.say(test_message)
                    engine.runAndWait()
                    self.add_to_conversation("SYSTEM", "✅ Voice test completed (system TTS)")
                except ImportError:
                    self.add_to_conversation("SYSTEM", "❌ No voice system available. Install pyttsx3: pip install pyttsx3")
                except Exception as e:
                    self.add_to_conversation("SYSTEM", f"❌ System TTS failed: {e}")
                    
        except Exception as e:
            self.add_to_conversation("SYSTEM", f"❌ Voice test failed: {e}")
            self.log_action(f"Voice test error: {e}")

    def toggle_listening(self):
        """Enhanced voice listening toggle"""
        if not self.voice_manager and not (hasattr(self.agent, 'voice') and self.agent.voice):
            messagebox.showwarning("Voice", "Voice system is not available.")
            self.log_action("Voice listening failed - voice not enabled")
            return
            
        if not self.listening:
            self.listening = True
            self.voice_btn.config(text="🛑 Stop Listening", bg='#e74c3c')
            self.log_action("Voice listening started")
            threading.Thread(target=self.listen_for_voice, daemon=True).start()
        else:
            self.listening = False
            self.voice_btn.config(text="🎤 Start Listening", bg='#27ae60')
            self.log_action("Voice listening stopped")

    def listen_for_voice(self):
        """Listen for voice commands"""
        while self.listening:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                text = loop.run_until_complete(self.agent.voice.listen(timeout=3))
                loop.close()
                
                if text:
                    self.log_action(f"Voice command received: {text}")
                    self.root.after(0, self.process_voice_command, text)
                    
            except Exception as e:
                self.log_action(f"Voice recognition error: {e}")
            
            time.sleep(0.5)

    def process_voice_command(self, command):
        """Process voice command"""
        self.add_to_conversation("USER", f"🎤 {command}")
        
        try:
            response = self.agent.handle_text(command)
            self.add_to_conversation("ULTRON", response)
            
            # Voice response
            if self.agent.voice:
                threading.Thread(target=self.speak_async, args=(response,), daemon=True).start()
                
        except Exception as e:
            error_msg = f"Error processing voice command: {str(e)}"
            self.add_to_conversation("SYSTEM", error_msg)
            self.log_action(f"Voice command error: {str(e)}")

    def update_system_status(self):
        """Update system status with monitoring"""
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
            
            # Ollama monitoring
            if self.ollama_manager:
                status = self.ollama_manager.get_status()
                if status['connected'] and status['current_model']:
                    model_name = status['current_model'].split(':')[0]  # Get model name without tag
                    running_count = len(status.get('running_models', []))
                    if running_count > 0:
                        self.status_vars['ollama'].set(f"Ollama: {model_name} ✓ ({running_count} running)")
                        self.update_status_light('ollama', 'online')
                    else:
                        self.status_vars['ollama'].set(f"Ollama: {model_name} (idle)")
                        self.update_status_light('ollama', 'warning')
                elif status['connected']:
                    self.status_vars['ollama'].set(f"Ollama: Connected ({status['model_count']} models)")
                    self.update_status_light('ollama', 'warning')
                else:
                    self.status_vars['ollama'].set("Ollama: Offline")
                    self.update_status_light('ollama', 'error')
            else:
                self.status_vars['ollama'].set("Ollama: N/A")
                self.update_status_light('ollama', 'offline')
            
            # GPU monitoring
            if GPU_AVAILABLE:
                try:
                    pynvml.nvmlInit()
                    device_count = pynvml.nvmlDeviceGetCount()
                    
                    for i in range(min(2, device_count)):
                        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                        mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                        temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                        
                        usage = int(mem_info.used) / int(mem_info.total) * 100
                        self.status_vars[f'gpu{i}'].set(f"GPU {i}: {usage:.1f}% | {temp}°C")
                        
                        if f'gpu{i}' in self.progress_bars:
                            self.progress_bars[f'gpu{i}']['value'] = usage
                        
                        # Update status light
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
                if hasattr(self, '_last_net_io') and self._last_net_io:
                    bytes_sent = net_io.bytes_sent - self._last_net_io.bytes_sent
                    bytes_recv = net_io.bytes_recv - self._last_net_io.bytes_recv
                    total_bytes = bytes_sent + bytes_recv
                    
                    speed_kbs = total_bytes / 1024 / 2
                    self.status_vars['network'].set(f"Network: {speed_kbs:.1f} KB/s")
                    
                    if speed_kbs > 1000:
                        self.update_status_light('network', 'online')
                    elif speed_kbs > 100:
                        self.update_status_light('network', 'warning')
                    else:
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
                if 'cpu' in self.progress_bars:
                    self.progress_bars['cpu']['value'] = cpu
                if 'memory' in self.progress_bars:
                    self.progress_bars['memory']['value'] = memory
                if 'disk' in self.progress_bars:
                    self.progress_bars['disk']['value'] = disk
            
            # Update status lights
            self.update_status_light('cpu', 'error' if cpu > 90 else 'warning' if cpu > 75 else 'online')
            self.update_status_light('memory', 'error' if memory > 90 else 'warning' if memory > 75 else 'online')
            self.update_status_light('voice', 'online' if self.listening else 'offline')
            self.update_status_light('ai', 'online' if hasattr(self.agent, 'brain') else 'error')
            
        except Exception as e:
            self.log_action(f"Status update error: {e}")

    def update_status_light(self, component, status):
        """Update status light for component"""
        try:
            if hasattr(self, 'status_light_labels') and component in self.status_light_labels:
                status_image = self.images.get(f'status_{status}')
                if status_image:
                    self.status_light_labels[component].configure(image=status_image)
                    self.status_lights[component] = status
        except Exception as e:
            self.log_action(f"Status light update error: {e}")

    def start_background_tasks(self):
        """Start background monitoring"""
        def update_loop():
            while True:
                self.root.after(0, self.update_system_status)
                time.sleep(2)
        
        threading.Thread(target=update_loop, daemon=True).start()
        self.root.after(500, self._poll_log_queue)
        self.log_action("Background tasks started")

    def update_llm_model(self, event=None):
        """Enhanced LLM model update with Ollama switching and status updates"""
        new_model = self.model_var.get()
        
        try:
            self.update_component_status('modelname', 'orange')  # switching
            
            if self.ollama_manager:
                self.add_to_conversation("SYSTEM", f"🤖 Switching to model: {new_model}")
                self.log_action(f"Attempting to switch to model: {new_model}")
                
                # Use Ollama manager to switch model
                success = self.ollama_manager.switch_model(new_model)
                
                if success:
                    self.update_component_status('modelname', 'green')  # success
                    if hasattr(self.agent, 'config'):
                        self.agent.config.data["llm_model"] = new_model
                    
                    msg = f"✅ Model switched successfully to {new_model}"
                    self.add_to_conversation("SYSTEM", msg)
                    self.log_action(f"Model switched successfully to: {new_model}")
                else:
                    self.update_component_status('modelname', 'red')  # failed
                    msg = f"❌ Failed to switch to model {new_model}"
                    self.add_to_conversation("SYSTEM", msg)
                    self.log_action(f"Model switch failed: {new_model}")
                    
                    # Revert to previous model
                    if self.ollama_manager.current_model:
                        self.model_var.set(self.ollama_manager.current_model)
            else:
                # Fallback to basic config update
                if hasattr(self.agent, 'config'):
                    self.agent.config.data["llm_model"] = new_model
                self.update_component_status('modelname', 'orange')  # needs restart
                msg = f"🧠 LLM model set to {new_model} (restart required)"
                self.add_to_conversation("SYSTEM", msg)
                self.log_action(f"LLM model changed to: {new_model}")
                
        except Exception as e:
            self.update_component_status('modelname', 'red')  # error
            error_msg = f"Error switching model: {str(e)}"
            self.add_to_conversation("SYSTEM", error_msg)
            self.log_action(f"Model switch error: {str(e)}")

    def test_ollama_connection(self):
        """Test Ollama connection with status updates"""
        try:
            self.update_component_status('ollama', 'orange')  # testing
            
            if self.ollama_manager:
                self.add_to_conversation("SYSTEM", "🤖 Testing Ollama connection...")
                self.log_action("Testing Ollama connection")
                
                # Refresh connection
                connected = self.ollama_manager.check_connection()
                
                if connected:
                    self.update_component_status('ollama', 'green')  # connected
                    status = self.ollama_manager.get_status()
                    
                    # Build status message
                    msg = "✅ Ollama Connection Status:\n"
                    if status['current_model']:
                        msg += f"📝 Active Model: {status['current_model']}\n"
                        self.update_component_status('modelname', 'green')
                    else:
                        msg += "⚠️ No model currently active\n"
                        self.update_component_status('modelname', 'orange')
                    
                    msg += f"📊 Available Models: {len(status['available_models'])}\n"
                    for model_name in status['available_models'][:3]:
                        msg += f"  • {model_name}\n"
                    if len(status['available_models']) > 3:
                        msg += f"  • (+{len(status['available_models']) - 3} more)\n"
                    
                    self.add_to_conversation("SYSTEM", msg)
                    self.log_action("Ollama test completed successfully")
                else:
                    self.update_component_status('ollama', 'red')  # failed
                    self.update_component_status('modelname', 'red')  # failed
                    error_msg = "❌ Ollama Connection Failed\n"
                    error_msg += "• Check if Ollama is running (ollama serve)\n"
                    error_msg += "• Verify Ollama is installed"
                    
                    self.add_to_conversation("SYSTEM", error_msg)
                    self.log_action("Ollama test failed - connection error")
            else:
                self.update_component_status('ollama', 'red')  # not available
                self.add_to_conversation("SYSTEM", "❌ Ollama manager not available")
                self.log_action("Ollama test failed - manager not available")
                
        except Exception as e:
            self.update_component_status('ollama', 'red')  # error
            error_msg = f"❌ Ollama test error: {str(e)}"
            self.add_to_conversation("SYSTEM", error_msg)
            self.log_action(f"Ollama test error: {str(e)}")

    def update_voice_engine(self, event=None):
        """Update voice engine with status feedback"""
        try:
            new_engine = self.voice_engine_var.get()
            if hasattr(self.agent, 'config'):
                self.agent.config.data["voice_engine"] = new_engine
                self.agent.config.data["tts_engine"] = new_engine
            
            msg = f"🎤 Voice engine set to {new_engine}"
            self.add_to_conversation("SYSTEM", msg)
            self.log_action(f"Voice engine changed to: {new_engine}")
            
            # Update voice status
            self.update_component_status('voice', 'orange')  # needs restart
            
        except Exception as e:
            self.log_action(f"Voice engine update error: {str(e)}")

    def _poll_log_queue(self):
        """Poll log queue for messages"""
        try:
            while not self.log_queue.empty():
                msg = self.log_queue.get_nowait()
                self.add_to_conversation("SYSTEM", msg)
        except:
            pass
        self.root.after(500, self._poll_log_queue)

    def run(self):
        """Start the GUI"""
        self.log_action("GUI main loop starting")
        self.root.mainloop()
        self.log_action("GUI main loop ended")
