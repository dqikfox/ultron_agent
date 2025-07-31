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
import logging

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

class AgentGUI:
    def __init__(self, agent, log_queue):
        self.agent = agent
        self.log_queue = log_queue
        self.listening = False
        self.conversation_history = []
        self.status_lights = {'cpu': 'online', 'memory': 'online', 'gpu0': 'offline', 'gpu1': 'offline', 'network': 'online', 'ai': 'online'}
        self._last_net_io = None
        
        # Initialize logging first
        self.setup_logging()
        
        # Initialize enhanced voice system
        if VOICE_MANAGER_AVAILABLE:
            self.voice_manager = get_voice_manager(self.agent.config if hasattr(self.agent, 'config') else None)
            self.log_action("Enhanced voice manager initialized")
        else:
            self.voice_manager = None
            self.log_action("Voice manager not available")
        
        # Initialize Ollama manager
        if OLLAMA_MANAGER_AVAILABLE:
            self.ollama_manager = get_ollama_manager(self.agent.config if hasattr(self.agent, 'config') else None)
            self.log_action("Ollama manager initialized")
            
            # Ensure default model is loaded
            if self.ollama_manager.ensure_default_model():
                self.log_action("Default model qwen2.5 confirmed loaded")
            else:
                self.log_action("Warning: Could not load default model")
        else:
            self.ollama_manager = None
            self.log_action("Ollama manager not available")
        
        # Setup logging
        self.setup_logging()
        self.log_action("GUI initialization started")
        
        # Initialize main window with proper size
        self.root = tk.Tk()
        self.root.title("ULTRON Agent 2.0 - Compact Interface")
        self.root.geometry("1200x700")  # Smaller, more manageable size
        self.root.configure(bg='#0a0a0a')
        self.root.resizable(True, True)
        
        # Set minimum size to prevent it from being too small
        self.root.minsize(800, 600)
        
        # Load images
        self.load_images()
        
        # Create the compact UI
        self.create_compact_ui()
        self.start_background_tasks()
        
        # Add initial welcome message
        self.add_to_conversation("ULTRON", "ULTRON AI Assistant initialized. Neural networks online. Ready for commands.")
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
        print(f"GUI LOG: {log_message} - gui_compact.py:117")

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
            
            # Outer glow
            draw.ellipse([2, 2, 18, 18], fill=colors[status] + '80', outline=None)
            # Inner bright circle
            draw.ellipse([4, 4, 16, 16], fill=colors[status], outline='#ffffff', width=1)
            
            self.images[f'status_{status}'] = ImageTk.PhotoImage(img)

    def create_compact_ui(self):
        """Create compact, properly sized interface"""
        
        # Main container
        main_container = tk.Frame(self.root, bg='#0a0a0a')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header (smaller)
        header_frame = tk.Frame(main_container, bg='#1a1a2e', relief=tk.RAISED, bd=2, height=80)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)
        
        # Header content
        header_content = tk.Frame(header_frame, bg='#1a1a2e')
        header_content.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
        # Logo and title
        if 'ultron_logo' in self.images:
            logo_label = tk.Label(header_content, image=self.images['ultron_logo'], bg='#1a1a2e')
            logo_label.pack(side=tk.LEFT, padx=(0, 20))
        
        title_frame = tk.Frame(header_content, bg='#1a1a2e')
        title_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(
            title_frame,
            text="◆ ULTRON v2.0 ◆",
            font=("Orbitron", 20, "bold"),
            fg='#00ff41',
            bg='#1a1a2e'
        ).pack(anchor='w')
        
        tk.Label(
            title_frame,
            text="AI Assistant - Neural Network Online",
            font=("Courier New", 10),
            fg='#3498db',
            bg='#1a1a2e'
        ).pack(anchor='w')
        
        # Main content area (horizontal layout)
        content_frame = tk.Frame(main_container, bg='#16213e', relief=tk.SUNKEN, bd=2)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Left panel - Status (compact)
        left_panel = tk.Frame(content_frame, bg='#2c3e50', width=250, relief=tk.RAISED, bd=1)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 2), pady=5)
        left_panel.pack_propagate(False)
        
        self.create_status_panel(left_panel)
        
        # Center panel - Conversation
        center_panel = tk.Frame(content_frame, bg='#34495e', relief=tk.SUNKEN, bd=1)
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2, pady=5)
        
        self.create_conversation_panel(center_panel)
        
        # Right panel - Controls (compact)
        right_panel = tk.Frame(content_frame, bg='#2c3e50', width=250, relief=tk.RAISED, bd=1)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(2, 5), pady=5)
        right_panel.pack_propagate(False)
        
        self.create_control_panel(right_panel)
        
        # Command input at bottom (compact)
        self.create_command_panel(main_container)

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
                print(f"[ULTRON VOICE]: {text} - gui_compact.py:618")
                
        except Exception as e:
            self.log_action(f"Voice output error: {str(e)}")
            print(f"[ULTRON VOICE FALLBACK]: {text} - gui_compact.py:622")

    def test_voice_output(self):
        """Enhanced voice test using voice manager"""
        test_message = "ULTRON voice system test. Neural networks operational. All systems ready."
        self.add_to_conversation("SYSTEM", f"🔊 Testing voice: {test_message}")
        self.log_action("Voice test initiated")
        
        try:
            if self.voice_manager:
                # Test with enhanced voice manager
                success = self.voice_manager.test_voice()
                if success:
                    self.add_to_conversation("SYSTEM", "✅ Voice test successful!")
                    self.log_action("Voice test completed successfully")
                else:
                    self.add_to_conversation("SYSTEM", "⚠️ Voice test partially successful")
                    self.log_action("Voice test partially successful")
            elif hasattr(self.agent, 'voice') and self.agent.voice:
                # Fallback to original system
                threading.Thread(target=self.speak_async, args=(test_message,), daemon=True).start()
                self.add_to_conversation("SYSTEM", "✅ Voice test initiated (legacy)")
                self.log_action("Voice test using legacy system")
            else:
                self.add_to_conversation("SYSTEM", "❌ Voice system not available")
                self.log_action("Voice test failed - no voice system")
                
        except Exception as e:
            self.add_to_conversation("SYSTEM", f"❌ Voice test error: {str(e)}")
            self.log_action(f"Voice test error: {str(e)}")

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

    def take_screenshot(self):
        """Take screenshot"""
        try:
            screenshot = ImageGrab.grab()
            timestamp = int(time.time())
            screenshot_path = Path(f"screenshot_{timestamp}.png")
            screenshot.save(screenshot_path)
            msg = f"📸 Screenshot saved: {screenshot_path}"
            self.add_to_conversation("SYSTEM", msg)
            self.log_action(f"Screenshot taken: {screenshot_path}")
        except Exception as e:
            error_msg = f"Screenshot failed: {str(e)}"
            self.add_to_conversation("SYSTEM", error_msg)
            self.log_action(f"Screenshot error: {str(e)}")

    def show_system_info(self):
        """Show system information"""
        try:
            info = {
                "Platform": os.name,
                "CPU Count": psutil.cpu_count(),
                "Total Memory": f"{psutil.virtual_memory().total / (1024**3):.1f} GB",
                "Python Version": sys.version.split()[0],
                "ULTRON Version": "2.0"
            }
            
            info_text = "\n".join([f"{k}: {v}" for k, v in info.items()])
            self.add_to_conversation("SYSTEM", f"💻 System Information:\n{info_text}")
            self.log_action("System info displayed")
        except Exception as e:
            self.log_action(f"System info error: {str(e)}")

    def open_file_manager(self):
        """Open file manager"""
        try:
            if os.name == 'nt':
                os.startfile(os.getcwd())
            else:
                import subprocess
                subprocess.Popen(['xdg-open', os.getcwd()])
            msg = f"📁 File manager opened: {os.getcwd()}"
            self.add_to_conversation("SYSTEM", msg)
            self.log_action("File manager opened")
        except Exception as e:
            error_msg = f"Failed to open file manager: {str(e)}"
            self.add_to_conversation("SYSTEM", error_msg)
            self.log_action(f"File manager error: {str(e)}")

    def update_voice_engine(self, event=None):
        """Update voice engine"""
        new_engine = self.voice_engine_var.get()
        self.agent.config.data["voice_engine"] = new_engine
        self.agent.config.data["tts_engine"] = new_engine
        msg = f"🎤 Voice engine set to {new_engine}"
        self.add_to_conversation("SYSTEM", msg)
        self.log_action(f"Voice engine changed to: {new_engine}")

    def update_llm_model(self, event=None):
        """Enhanced LLM model update with Ollama switching"""
        new_model = self.llm_model_var.get()
        
        try:
            if self.ollama_manager:
                self.add_to_conversation("SYSTEM", f"🤖 Switching to model: {new_model}")
                self.log_action(f"Attempting to switch to model: {new_model}")
                
                # Use Ollama manager to switch model
                success = self.ollama_manager.switch_model(new_model)
                
                if success:
                    # Update agent config
                    if hasattr(self.agent, 'config'):
                        self.agent.config.data["llm_model"] = new_model
                    
                    msg = f"🧠 Model switched successfully to {new_model}"
                    self.add_to_conversation("SYSTEM", msg)
                    self.log_action(f"Model switched successfully to: {new_model}")
                else:
                    msg = f"❌ Failed to switch to model {new_model}"
                    self.add_to_conversation("SYSTEM", msg)
                    self.log_action(f"Model switch failed: {new_model}")
                    
                    # Revert to previous model
                    if self.ollama_manager.current_model:
                        self.llm_model_var.set(self.ollama_manager.current_model)
            else:
                # Fallback to basic config update
                if hasattr(self.agent, 'config'):
                    self.agent.config.data["llm_model"] = new_model
                msg = f"🧠 LLM model set to {new_model} (restart required)"
                self.add_to_conversation("SYSTEM", msg)
                self.log_action(f"LLM model changed to: {new_model}")
                
        except Exception as e:
            error_msg = f"Error switching model: {str(e)}"
            self.add_to_conversation("SYSTEM", error_msg)
            self.log_action(f"Model switch error: {str(e)}")

    def test_ollama_connection(self):
        """Test Ollama connection and show comprehensive status"""
        try:
            if self.ollama_manager:
                self.add_to_conversation("SYSTEM", "🤖 Testing Ollama connection...")
                self.log_action("Testing Ollama connection")
                
                # Refresh connection
                connected = self.ollama_manager.check_connection()
                
                if connected:
                    status = self.ollama_manager.get_status()
                    
                    # Build comprehensive status message
                    msg = "✅ Ollama Connection Status:\n"
                    
                    # Current model info
                    if status['current_model']:
                        model_working = status['model_working']
                        status_icon = "✅" if model_working else "⚠️"
                        msg += f"{status_icon} Active Model: {status['current_model']}\n"
                    else:
                        msg += "⚠️ No model currently active\n"
                    
                    # Running models
                    if status['running_models']:
                        msg += f"🔄 Running Models: {len(status['running_models'])}\n"
                        for model in status['running_models'][:2]:  # Show first 2
                            msg += f"  • {model['name']} ({model['size']})\n"
                    else:
                        msg += "💤 No models currently running\n"
                    
                    # Available models summary
                    msg += f"📊 Available Models: {len(status['available_models'])}\n"
                    
                    # Get model sizes
                    model_info = self.ollama_manager.get_model_sizes()
                    if model_info:
                        total_size = 0
                        for model_name in status['available_models'][:3]:  # Show first 3
                            if model_name in model_info:
                                size = model_info[model_name]['size']
                                msg += f"  • {model_name} ({size})\n"
                        if len(status['available_models']) > 3:
                            msg += f"  • (+{len(status['available_models']) - 3} more models)\n"
                    
                    # Quick recommendations
                    if not status['current_model']:
                        msg += "\n💡 Tip: Select a model from the dropdown to activate it"
                    elif not status['model_working']:
                        msg += "\n⚠️ Warning: Current model may need reloading"
                    
                    self.add_to_conversation("SYSTEM", msg)
                    self.log_action("Ollama comprehensive test completed")
                else:
                    error_msg = "❌ Ollama Connection Failed\n"
                    error_msg += "• Check if Ollama is running (ollama serve)\n"
                    error_msg += "• Verify Ollama is installed\n"
                    error_msg += "• Check if port 11434 is accessible"
                    
                    self.add_to_conversation("SYSTEM", error_msg)
                    self.log_action("Ollama test failed - connection error")
            else:
                self.add_to_conversation("SYSTEM", "❌ Ollama manager not available")
                self.log_action("Ollama test failed - manager not available")
                
        except Exception as e:
            error_msg = f"❌ Ollama test error: {str(e)}"
            self.add_to_conversation("SYSTEM", error_msg)
            self.log_action(f"Ollama test error: {str(e)}")

    def start_background_tasks(self):
        """Start background monitoring"""
        def update_loop():
            while True:
                self.root.after(0, self.update_system_status)
                time.sleep(2)
        
        threading.Thread(target=update_loop, daemon=True).start()
        self.root.after(500, self._poll_log_queue)
        self.log_action("Background tasks started")

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
