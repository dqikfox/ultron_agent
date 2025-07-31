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

# Setup logging for all actions
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ultron_gui.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('UltronGUI')

# GPU monitoring
try:
    import pynvml
    GPU_AVAILABLE = True
    logger.info("GPU monitoring available")
except ImportError:
    GPU_AVAILABLE = False
    logger.warning("GPU monitoring not available")

class AgentGUI:
    def __init__(self, agent, log_queue):
        logger.info("Initializing ULTRON GUI")
        self.agent = agent
        self.log_queue = log_queue
        self.listening = False
        self.conversation_history = []
        self.status_lights = {'cpu': 'green', 'memory': 'green', 'gpu0': 'green', 'gpu1': 'green', 'network': 'green', 'ai': 'green'}
        self._last_net_io = None
        
        # Initialize main window with smaller size
        self.root = tk.Tk()
        self.root.title("ULTRON Agent 2.0 - Enhanced Interface")
        self.root.geometry("1200x800")  # Smaller size
        self.root.configure(bg='#0a0a0a')
        self.root.resizable(True, True)
        
        # Load images
        self.load_images()
        
        # Create the enhanced UI
        self.create_enhanced_ui()
        self.start_background_tasks()
        
        # Add initial welcome message
        self.add_to_conversation("ULTRON", "ULTRON AI Assistant initialized. Neural networks online. Ready for commands.")
        logger.info("ULTRON GUI initialization completed")

    def load_images(self):
        """Load and prepare images for the interface"""
        logger.info("Loading GUI images")
        self.images = {}
        image_path = Path("resources/images")
        
        try:
            # Load cyberpunk interface images for background
            cyberpunk_images = [
                "20250731_0131_Cyberpunk AI Interface_remix_01k1dz2gamf9xs8rtesb3nm7kw - Copy.png",
                "20250731_0131_Cyberpunk AI Interface_remix_01k1dz2ganefabrhpm3vdr2nt2 (1) - Copy.png",
                "2d6cde57-74ee-404e-acf2-91fb1db9eb8e - Copy.png",
                "5a42650e-c233-4dfd-a604-bdb8b7f1b77a - Copy.png"
            ]
            
            # Try to load a cyberpunk background
            for img_name in cyberpunk_images:
                if (image_path / img_name).exists():
                    try:
                        bg_img = Image.open(image_path / img_name)
                        bg_img = bg_img.resize((1200, 800), Image.Resampling.LANCZOS)
                        bg_img = bg_img.convert("RGBA")
                        bg_img.putalpha(30)  # Very transparent
                        self.images['background'] = ImageTk.PhotoImage(bg_img)
                        logger.info(f"Loaded background image: {img_name}")
                        break
                    except Exception as e:
                        logger.warning(f"Failed to load background {img_name}: {e}")
            
            # Load ULTRON logo
            if (image_path / "ultron.jpg").exists():
                try:
                    img = Image.open(image_path / "ultron.jpg")
                    img = img.resize((120, 120), Image.Resampling.LANCZOS)
                    self.images['ultron_logo'] = ImageTk.PhotoImage(img)
                    logger.info("Loaded ULTRON logo")
                except Exception as e:
                    logger.warning(f"Failed to load ULTRON logo: {e}")
            
            # Load AI assistant images
            ai_images = ["UltronPrestige - Copy.webp", "Ultron_29_from_Marvel_Future_Revolution_001 - Copy.webp"]
            for ai_img in ai_images:
                if (image_path / ai_img).exists():
                    try:
                        img = Image.open(image_path / ai_img)
                        img = img.resize((80, 80), Image.Resampling.LANCZOS)
                        self.images['ai_avatar'] = ImageTk.PhotoImage(img)
                        logger.info(f"Loaded AI avatar: {ai_img}")
                        break
                    except Exception as e:
                        logger.warning(f"Failed to load AI avatar {ai_img}: {e}")
            
            # Create enhanced status lights
            self.create_status_lights()
            
        except Exception as e:
            logger.error(f"Error loading images: {e}")
            self.images = {}

    def create_status_lights(self):
        """Create enhanced Pokedex-style status lights"""
        logger.info("Creating status indicator lights")
        for status in ['online', 'warning', 'error', 'offline']:
            colors = {
                'online': '#00ff41',    # Bright green
                'warning': '#ffaa00',   # Orange  
                'error': '#ff4444',     # Red
                'offline': '#666666'    # Gray
            }
            
            # Create status lights with glow effect
            img = Image.new('RGBA', (24, 24), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Outer glow
            draw.ellipse([2, 2, 22, 22], fill=colors[status] + '40', outline=None)
            # Inner bright circle
            draw.ellipse([6, 6, 18, 18], fill=colors[status], outline='#ffffff', width=1)
            # Highlight for 3D effect
            draw.ellipse([8, 8, 14, 14], fill=colors[status] + 'aa', outline=None)
            
            self.images[f'status_{status}'] = ImageTk.PhotoImage(img)

    def create_enhanced_ui(self):
        """Create enhanced interface"""
        logger.info("Creating enhanced UI layout")
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#0a0a0a')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header with ULTRON logo and title
        self.create_header(main_frame)
        
        # Main content area
        content_frame = tk.Frame(main_frame, bg='#16213e', relief=tk.SUNKEN, bd=2)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create layout
        self.create_main_layout(content_frame)
        
        # Command input at bottom
        self.create_command_panel(main_frame)

    def create_header(self, parent):
        """Create header with logo and title"""
        header_frame = tk.Frame(parent, bg='#1a1a2e', relief=tk.RAISED, bd=2, height=100)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)
        
        # ULTRON logo
        if 'ultron_logo' in self.images:
            logo_label = tk.Label(header_frame, image=self.images['ultron_logo'], bg='#1a1a2e')
            logo_label.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Title section
        title_frame = tk.Frame(header_frame, bg='#1a1a2e')
        title_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15)
        
        # Main title
        title_label = tk.Label(
            title_frame, 
            text="◆ ULTRON v2.0 ◆", 
            font=("Orbitron", 24, "bold"),
            fg='#00ff41', 
            bg='#1a1a2e'
        )
        title_label.pack(pady=(20, 5))
        
        # Subtitle
        subtitle = tk.Label(
            title_frame,
            text="AI Assistant - Neural Network Online",
            font=("Courier New", 12, "bold"),
            fg='#3498db',
            bg='#1a1a2e'
        )
        subtitle.pack()
        
        # AI Avatar
        if 'ai_avatar' in self.images:
            avatar_label = tk.Label(header_frame, image=self.images['ai_avatar'], bg='#1a1a2e')
            avatar_label.pack(side=tk.RIGHT, padx=15, pady=10)

    def create_main_layout(self, parent):
        """Create main three-panel layout"""
        
        # Left panel - System status (smaller)
        left_panel = tk.Frame(parent, bg='#2c3e50', width=280, relief=tk.RAISED, bd=2)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 5), pady=10)
        left_panel.pack_propagate(False)
        
        self.create_status_panel(left_panel)
        
        # Center panel - Conversation (larger)
        center_panel = tk.Frame(parent, bg='#34495e', relief=tk.SUNKEN, bd=2)
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=10)
        
        self.create_conversation_panel(center_panel)
        
        # Right panel - Controls (smaller)
        right_panel = tk.Frame(parent, bg='#2c3e50', width=280, relief=tk.RAISED, bd=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 10), pady=10)
        right_panel.pack_propagate(False)
        
        self.create_control_panel(right_panel)

    def create_status_panel(self, parent):
        """Create system status panel"""
        # Header
        tk.Label(
            parent, 
            text="⚡ SYSTEM STATUS ⚡", 
            font=("Orbitron", 12, "bold"),
            fg='#00ff41', 
            bg='#2c3e50'
        ).pack(pady=10)
        
        # Status metrics
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
            metric_frame.pack(fill=tk.X, pady=2)
            
            # Status container
            status_container = tk.Frame(metric_frame, bg='#2c3e50')
            status_container.pack(fill=tk.X)
            
            # Status light
            status_light = tk.Label(
                status_container,
                image=self.images.get('status_online', ''),
                bg='#2c3e50'
            )
            status_light.pack(side=tk.LEFT, padx=(0, 8))
            self.status_light_labels[key] = status_light
            
            # Label
            tk.Label(
                status_container,
                textvariable=var,
                font=("Courier New", 9, "bold"),
                fg='#ecf0f1',
                bg='#2c3e50',
                anchor='w'
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Progress bar for numeric metrics
            if key in ['cpu', 'memory', 'disk', 'gpu0', 'gpu1']:
                progress = ttk.Progressbar(
                    metric_frame, 
                    mode='determinate',
                    length=220,
                    style='Custom.Horizontal.TProgressbar'
                )
                progress.pack(fill=tk.X, pady=(1, 0))
                self.progress_bars[key] = progress
        
        # Configure progress bar style
        style = ttk.Style()
        style.configure('Custom.Horizontal.TProgressbar',
                       background='#00ff41',
                       troughcolor='#34495e',
                       borderwidth=1,
                       relief='flat')

    def create_conversation_panel(self, parent):
        """Create conversation panel"""
        # Header
        tk.Label(
            parent, 
            text="💬 CONVERSATION LOG 💬", 
            font=("Orbitron", 12, "bold"),
            fg='#00ff41', 
            bg='#34495e'
        ).pack(pady=10)
        
        # Conversation display
        conv_container = tk.Frame(parent, bg='#2c3e50', relief=tk.SUNKEN, bd=2)
        conv_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.conversation_text = scrolledtext.ScrolledText(
            conv_container,
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg='#2c3e50',
            fg='#ecf0f1',
            font=("Consolas", 10),
            insertbackground='#00ff41',
            selectbackground='#3498db',
            selectforeground='white',
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.conversation_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Text formatting tags
        self.conversation_text.tag_configure("user", foreground="#3498db", font=("Consolas", 10, "bold"))
        self.conversation_text.tag_configure("ultron", foreground="#00ff41", font=("Consolas", 10, "bold"))
        self.conversation_text.tag_configure("system", foreground="#e67e22", font=("Consolas", 9, "italic"))
        self.conversation_text.tag_configure("timestamp", foreground="#95a5a6", font=("Consolas", 8))

    def create_control_panel(self, parent):
        """Create control panel"""
        # Voice controls
        tk.Label(
            parent, 
            text="🎤 VOICE CONTROLS 🎤", 
            font=("Orbitron", 12, "bold"),
            fg='#00ff41', 
            bg='#2c3e50'
        ).pack(pady=10)
        
        # Voice button
        self.voice_btn = tk.Button(
            parent,
            text="🎤 Start Listening",
            command=self.toggle_listening,
            bg='#27ae60',
            fg='white',
            font=("Segoe UI", 11, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=10,
            cursor='hand2'
        )
        self.voice_btn.pack(fill=tk.X, padx=10, pady=5)
        
        # Test voice button
        test_voice_btn = tk.Button(
            parent,
            text="🔊 Test Voice",
            command=self.test_voice_output,
            bg='#8e44ad',
            fg='white',
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        test_voice_btn.pack(fill=tk.X, padx=10, pady=5)
        
        # Configuration
        tk.Label(
            parent, 
            text="⚙️ CONFIGURATION ⚙️", 
            font=("Orbitron", 11, "bold"),
            fg='#00ff41', 
            bg='#2c3e50'
        ).pack(pady=(20, 10))
        
        config_frame = tk.Frame(parent, bg='#2c3e50')
        config_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Voice engine
        tk.Label(config_frame, text="Voice Engine:", bg='#2c3e50', fg='#ecf0f1', 
                font=("Segoe UI", 9, "bold")).pack(anchor='w', pady=(0,2))
        
        self.voice_engine_var = tk.StringVar(value=self.agent.config.data.get("voice_engine", "pyttsx3"))
        voice_combo = ttk.Combobox(config_frame, textvariable=self.voice_engine_var, 
                                  state="readonly", font=("Segoe UI", 9), width=25)
        voice_combo['values'] = ("pyttsx3", "elevenlabs", "openai")
        voice_combo.pack(fill=tk.X, pady=(0,10))
        voice_combo.bind("<<ComboboxSelected>>", self.update_voice_engine)
        
        # Quick actions
        actions_frame = tk.Frame(parent, bg='#2c3e50')
        actions_frame.pack(fill=tk.X, padx=10, pady=10)
        
        actions = [
            ("📸 Screenshot", self.take_screenshot, '#3498db'),
            ("💻 System Info", self.show_system_info, '#9b59b6'),
            ("🔧 Tools", self.show_tools_explorer, '#f39c12')
        ]
        
        for text, command, color in actions:
            btn = tk.Button(
                actions_frame,
                text=text,
                command=command,
                bg=color,
                fg='white',
                font=("Segoe UI", 9, "bold"),
                relief=tk.FLAT,
                padx=10,
                pady=6,
                cursor='hand2'
            )
            btn.pack(fill=tk.X, pady=2)

    def create_command_panel(self, parent):
        """Create command input panel - FIXED to be visible"""
        logger.info("Creating command input panel")
        command_frame = tk.Frame(parent, bg='#e67e22', relief=tk.RAISED, bd=2, height=80)
        command_frame.pack(fill=tk.X, pady=(10, 0))
        command_frame.pack_propagate(False)
        
        # Command header
        tk.Label(
            command_frame,
            text="⌨️ COMMAND INTERFACE ⌨️",
            font=("Orbitron", 11, "bold"),
            bg='#e67e22',
            fg='white'
        ).pack(pady=(8, 0))
        
        # Input area
        input_container = tk.Frame(command_frame, bg='#e67e22')
        input_container.pack(fill=tk.X, padx=10, pady=(0, 8))
        
        entry_frame = tk.Frame(input_container, bg='#2c3e50', relief=tk.SUNKEN, bd=1)
        entry_frame.pack(fill=tk.X)
        
        self.command_entry = tk.Entry(
            entry_frame,
            font=("Consolas", 11),
            bg='#2c3e50',
            fg='#ecf0f1',
            insertbackground='#00ff41',
            relief=tk.FLAT,
            bd=0
        )
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8, pady=6)
        self.command_entry.bind('<Return>', self.process_text_command)
        
        execute_btn = tk.Button(
            entry_frame,
            text="▶ EXECUTE",
            command=self.process_text_command,
            bg='#27ae60',
            fg='white',
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=6,
            cursor='hand2'
        )
        execute_btn.pack(side=tk.RIGHT, padx=(0, 8))

    def add_to_conversation(self, speaker, message):
        """Add message to conversation with logging"""
        logger.info(f"Conversation - {speaker}: {message}")
        self.conversation_text.config(state=tk.NORMAL)
        
        timestamp = time.strftime("%H:%M:%S")
        
        # Add timestamp
        self.conversation_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # Add speaker with styling
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
        """Process text command with logging"""
        command = self.command_entry.get().strip()
        if not command:
            return
        
        logger.info(f"Processing text command: {command}")
        self.add_to_conversation("USER", command)
        self.command_entry.delete(0, tk.END)
        
        try:
            response = self.agent.handle_text(command)
            self.add_to_conversation("ULTRON", response)
            
            # Trigger voice output if enabled
            if self.agent.voice:
                logger.info("Triggering voice response")
                threading.Thread(target=self.speak_async, args=(response,), daemon=True).start()
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            self.add_to_conversation("SYSTEM", f"Error processing command: {str(e)}")

    def speak_async(self, text):
        """Async wrapper for voice output with enhanced logging"""
        try:
            logger.info(f"Starting voice output: {text[:50]}...")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.agent.voice.speak(text))
            loop.close()
            logger.info("Voice output completed successfully")
        except Exception as e:
            logger.error(f"Voice output error: {e}")
            self.add_to_conversation("SYSTEM", f"Voice output failed: {str(e)}")

    def test_voice_output(self):
        """Test voice output with logging"""
        logger.info("Testing voice output")
        test_message = "Voice test: ULTRON systems operational. Neural networks online."
        self.add_to_conversation("SYSTEM", f"🔊 Testing voice: {test_message}")
        
        if self.agent.voice:
            threading.Thread(target=self.speak_async, args=(test_message,), daemon=True).start()
        else:
            logger.warning("Voice system not available")
            self.add_to_conversation("SYSTEM", "❌ Voice system not available")

    def toggle_listening(self):
        """Toggle voice listening with logging"""
        if not self.agent.voice:
            logger.warning("Voice not enabled for listening")
            messagebox.showwarning("Voice", "Voice is not enabled.")
            return
            
        if not self.listening:
            logger.info("Starting voice listening")
            self.listening = True
            self.voice_btn.config(text="🛑 Stop Listening", bg='#e74c3c')
            threading.Thread(target=self.listen_for_voice, daemon=True).start()
        else:
            logger.info("Stopping voice listening")
            self.listening = False
            self.voice_btn.config(text="🎤 Start Listening", bg='#27ae60')

    def listen_for_voice(self):
        """Listen for voice commands with logging"""
        logger.info("Voice listening loop started")
        while self.listening:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                text = loop.run_until_complete(self.agent.voice.listen(timeout=3))
                loop.close()
                
                if text:
                    logger.info(f"Voice command received: {text}")
                    self.root.after(0, self.process_voice_command, text)
                    
            except Exception as e:
                logger.error(f"Voice recognition error: {e}")
            
            time.sleep(0.5)
        logger.info("Voice listening loop ended")

    def process_voice_command(self, command):
        """Process voice command with logging"""
        logger.info(f"Processing voice command: {command}")
        self.add_to_conversation("USER", f"🎤 {command}")
        
        try:
            response = self.agent.handle_text(command)
            self.add_to_conversation("ULTRON", response)
            
            # Voice response
            if self.agent.voice:
                threading.Thread(target=self.speak_async, args=(response,), daemon=True).start()
        except Exception as e:
            logger.error(f"Error processing voice command: {e}")
            self.add_to_conversation("SYSTEM", f"Error processing voice command: {str(e)}")

    def update_system_status(self):
        """Update system status with GPU/network monitoring and logging"""
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
                    self.status_vars[f'gpu{i}'].set(f"GPU {i}: N/A")
                    self.update_status_light(f'gpu{i}', 'offline')
            
            # Network monitoring
            try:
                net_io = psutil.net_io_counters()
                if self._last_net_io:
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
                self.progress_bars['cpu']['value'] = cpu
                self.progress_bars['memory']['value'] = memory
                self.progress_bars['disk']['value'] = disk
            
            # Update status lights
            self.update_status_light('cpu', 'error' if cpu > 90 else 'warning' if cpu > 75 else 'online')
            self.update_status_light('memory', 'error' if memory > 90 else 'warning' if memory > 75 else 'online')
            self.update_status_light('voice', 'online' if self.listening else 'offline')
            self.update_status_light('ai', 'online' if hasattr(self.agent, 'brain') else 'error')
            
        except Exception as e:
            logger.error(f"Status update error: {e}")

    def update_status_light(self, component, status):
        """Update status light for a component"""
        try:
            if hasattr(self, 'status_light_labels') and component in self.status_light_labels:
                status_image = self.images.get(f'status_{status}')
                if status_image:
                    self.status_light_labels[component].configure(image=status_image)
                    self.status_lights[component] = status
        except Exception as e:
            logger.error(f"Status light update error: {e}")

    def take_screenshot(self):
        """Take screenshot with logging"""
        logger.info("Taking screenshot")
        try:
            screenshot = ImageGrab.grab()
            timestamp = int(time.time())
            screenshot_path = Path(f"screenshot_{timestamp}.png")
            screenshot.save(screenshot_path)
            self.add_to_conversation("SYSTEM", f"📸 Screenshot saved: {screenshot_path}")
            logger.info(f"Screenshot saved: {screenshot_path}")
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            self.add_to_conversation("SYSTEM", f"Screenshot failed: {str(e)}")

    def show_system_info(self):
        """Show system information with logging"""
        logger.info("Displaying system information")
        info = {
            "Platform": os.name,
            "CPU Count": psutil.cpu_count(),
            "Total Memory": f"{psutil.virtual_memory().total / (1024**3):.1f} GB",
            "Python Version": sys.version.split()[0],
            "ULTRON Version": "2.0"
        }
        
        info_text = "\n".join([f"{k}: {v}" for k, v in info.items()])
        self.add_to_conversation("SYSTEM", f"💻 System Information:\n{info_text}")

    def show_tools_explorer(self):
        """Show tools explorer with logging"""
        logger.info("Opening tools explorer")
        popup = tk.Toplevel(self.root)
        popup.title("🔧 Tools Explorer")
        popup.geometry("600x400")
        popup.configure(bg='#2c3e50')
        
        tk.Label(popup, text="🔧 Available Tools", font=("Orbitron", 14, "bold"),
                fg='#00ff41', bg='#2c3e50').pack(pady=15)
        
        tools_frame = tk.Frame(popup, bg='#2c3e50')
        tools_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        tools_listbox = tk.Listbox(tools_frame, bg='#34495e', fg='#ecf0f1', 
                                  font=("Courier New", 10), selectbackground='#3498db')
        tools_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        for tool in self.agent.tools:
            tools_listbox.insert(tk.END, f"🔧 {tool.name} - {tool.description}")
        
        tk.Button(popup, text="Close", command=popup.destroy,
                 bg='#e74c3c', fg='white', font=("Segoe UI", 11, "bold"),
                 relief=tk.FLAT, padx=25, pady=8).pack(pady=(0, 15))

    def update_voice_engine(self, event=None):
        """Update voice engine with logging"""
        new_engine = self.voice_engine_var.get()
        logger.info(f"Voice engine changed to: {new_engine}")
        self.agent.config.data["voice_engine"] = new_engine
        self.agent.config.data["tts_engine"] = new_engine
        self.add_to_conversation("SYSTEM", f"🎤 Voice engine set to {new_engine}")

    def start_background_tasks(self):
        """Start background monitoring tasks"""
        logger.info("Starting background monitoring tasks")
        def update_loop():
            while True:
                self.root.after(0, self.update_system_status)
                time.sleep(2)
        
        threading.Thread(target=update_loop, daemon=True).start()
        self.root.after(500, self._poll_log_queue)

    def _poll_log_queue(self):
        """Poll log queue for messages"""
        while not self.log_queue.empty():
            msg = self.log_queue.get_nowait()
            self.add_to_conversation("SYSTEM", msg)
        self.root.after(500, self._poll_log_queue)

    def run(self):
        """Start the GUI with logging"""
        logger.info("Starting ULTRON GUI main loop")
        self.root.mainloop()
        logger.info("ULTRON GUI closed")
