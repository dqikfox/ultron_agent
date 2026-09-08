#!/usr/bin/env python3
"""
ULTRON Agent 3.0 - Integrated Pokédex-Style GUI
Modern cyberpunk interface integrated with existing agent infrastructure

Features:
- Thread-safe communication with agent components
- Real-time system monitoring with GPU support
- Voice integration with existing VoiceAssistant
- Cyberpunk Ultron aesthetics
- Tool integration and command interface
"""

import os
import sys
import json
import time
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import psutil
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
import asyncio
import queue

# Import existing agent components
try:
    from brain import UltronBrain
    from voice import VoiceAssistant
    from memory import Memory
    from security_utils import sanitize_log_input
    AGENT_COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Agent components not available: {e}")
    AGENT_COMPONENTS_AVAILABLE = False

# GPU monitoring
try:
    import pynvml
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

class IntegratedPokedexGUI:
    """
    Modern Pokédex-style GUI integrated with ULTRON Agent 3.0

    This GUI replaces the problematic gui_ultimate.py with a modern,
    thread-safe interface that properly integrates with the agent infrastructure.
    """

    def __init__(self, agent_ref=None):
        """Initialize GUI with agent reference"""
        self.agent_ref = agent_ref
        self.root = None
        self.running = False

        # Communication queues for thread safety
        self.command_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self.status_queue = queue.Queue()

        # UI State
        self.conversation_history = []
        self.listening = False
        self.status_vars = {}
        self.progress_bars = {}

        # Configuration
        self.config = self.load_gui_config()

        # Setup logging
        self.setup_logging()

        # Start time for uptime calculation
        self.start_time = time.time()

    def setup_logging(self):
        """Setup GUI-specific logging"""
        self.logger = logging.getLogger("pokedex_gui")
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def load_gui_config(self):
        """Load GUI-specific configuration"""
        default_config = {
            "theme": {
                "primary_bg": "#1a1a2e",
                "secondary_bg": "#2c3e50",
                "accent_color": "#00ff41",
                "text_color": "#ecf0f1",
                "warning_color": "#e67e22",
                "error_color": "#e74c3c",
                "success_color": "#27ae60"
            },
            "window": {
                "width": 1400,
                "height": 900,
                "title": "ULTRON Agent 3.0 - AI Assistant"
            },
            "monitoring": {
                "update_interval": 2000,  # ms
                "show_gpu": True,
                "show_network": True
            },
            "voice": {
                "show_waveform": True,
                "visual_feedback": True
            }
        }

        # Try to load from config file
        config_path = Path("pokedex_gui_config.json")
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    default_config.update(loaded_config)
            except Exception as e:
                self.logger.warning(f"Failed to load GUI config: {e}")

        return default_config

    def save_gui_config(self):
        """Save current GUI configuration"""
        try:
            with open("pokedex_gui_config.json", 'w') as f:
                json.dump(self.config, f, indent=2)
            self.logger.info("GUI configuration saved")
        except Exception as e:
            self.logger.error(f"Failed to save GUI config: {e}")

    def initialize_gui(self):
        """Initialize the GUI in main thread - THIS MUST BE CALLED FROM MAIN THREAD"""
        if self.root is not None:
            return  # Already initialized

        self.logger.info("🎨 Initializing Pokédex-style GUI...")

        # Create main window
        self.root = tk.Tk()
        self.root.title(self.config["window"]["title"])
        self.root.geometry(f"{self.config['window']['width']}x{self.config['window']['height']}")
        self.root.configure(bg=self.config["theme"]["primary_bg"])

        # Window settings
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.attributes('-alpha', 0.98)  # Slight transparency for futuristic effect

        # Create the interface
        self.create_pokedex_interface()

        # Start background tasks
        self.start_background_tasks()

        # Mark as initialized
        self.running = True
        self.logger.info("✅ Pokédex GUI initialized successfully")

    def create_pokedex_interface(self):
        """Create the main Pokédex-style interface"""
        # Main container
        main_frame = tk.Frame(self.root, bg=self.config["theme"]["primary_bg"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header - Ultron branding
        self.create_header(main_frame)

        # Main content area
        content_frame = tk.Frame(main_frame, bg=self.config["theme"]["primary_bg"])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Left panel - System status and monitoring
        left_panel = tk.Frame(content_frame, bg=self.config["theme"]["secondary_bg"], width=350)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)

        self.create_system_status_panel(left_panel)

        # Center panel - Conversation and main display
        center_panel = tk.Frame(content_frame, bg=self.config["theme"]["secondary_bg"])
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.create_conversation_panel(center_panel)

        # Right panel - Controls and tools
        right_panel = tk.Frame(content_frame, bg=self.config["theme"]["secondary_bg"], width=350)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)

        self.create_control_panel(right_panel)

        # Bottom panel - Command input
        self.create_command_input_panel(main_frame)

    def create_header(self, parent):
        """Create header with Ultron branding"""
        header_frame = tk.Frame(parent, bg=self.config["theme"]["error_color"], relief=tk.RAISED, bd=3)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        # Title section
        title_section = tk.Frame(header_frame, bg=self.config["theme"]["secondary_bg"])
        title_section.pack(fill=tk.X, padx=5, pady=5)

        # Main title
        title_label = tk.Label(
            title_section,
            text="ULTRON AGENT 3.0",
            font=("Orbitron", 28, "bold"),
            fg=self.config["theme"]["accent_color"],
            bg=self.config["theme"]["secondary_bg"]
        )
        title_label.pack()

        # Status subtitle
        status_text = "AI Assistant - Integrated System"
        if self.agent_ref and hasattr(self.agent_ref, 'status'):
            status_text = f"AI Assistant - {self.agent_ref.status} Status"

        status_label = tk.Label(
            title_section,
            text=status_text,
            font=("Courier", 14),
            fg="#3498db",
            bg=self.config["theme"]["secondary_bg"]
        )
        status_label.pack()

        # System time and uptime
        time_frame = tk.Frame(title_section, bg=self.config["theme"]["secondary_bg"])
        time_frame.pack(fill=tk.X, pady=5)

        self.time_var = tk.StringVar()
        self.uptime_var = tk.StringVar()

        time_label = tk.Label(
            time_frame,
            textvariable=self.time_var,
            font=("Courier", 12),
            fg=self.config["theme"]["text_color"],
            bg=self.config["theme"]["secondary_bg"]
        )
        time_label.pack(side=tk.LEFT)

        uptime_label = tk.Label(
            time_frame,
            textvariable=self.uptime_var,
            font=("Courier", 12),
            fg=self.config["theme"]["text_color"],
            bg=self.config["theme"]["secondary_bg"]
        )
        uptime_label.pack(side=tk.RIGHT)

    def create_system_status_panel(self, parent):
        """Create comprehensive system status panel"""
        # Panel title
        title_label = tk.Label(
            parent,
            text="🖥️ SYSTEM MONITORING",
            font=("Orbitron", 14, "bold"),
            fg=self.config["theme"]["accent_color"],
            bg=self.config["theme"]["secondary_bg"]
        )
        title_label.pack(pady=10)

        # Create scrollable frame for status items
        canvas = tk.Canvas(parent, bg=self.config["theme"]["secondary_bg"], highlightthickness=0, height=400)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.config["theme"]["secondary_bg"])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=10)
        scrollbar.pack(side="right", fill="y")

        # Basic system metrics
        self.create_basic_metrics(scrollable_frame)

        # GPU metrics (if available)
        if GPU_AVAILABLE:
            self.create_gpu_metrics(scrollable_frame)

        # Agent component status
        self.create_agent_status(scrollable_frame)

        # Quick actions
        self.create_quick_actions(scrollable_frame)

    def create_basic_metrics(self, parent):
        """Create basic system metrics display"""
        metrics_frame = tk.LabelFrame(
            parent,
            text="Basic Metrics",
            font=("Orbitron", 11, "bold"),
            fg=self.config["theme"]["accent_color"],
            bg=self.config["theme"]["secondary_bg"]
        )
        metrics_frame.pack(fill=tk.X, padx=5, pady=5)

        # Initialize status variables
        metrics = ['cpu', 'memory', 'disk', 'network']

        for metric in metrics:
            self.status_vars[metric] = tk.StringVar(value=f"{metric.upper()}: 0%")

            frame = tk.Frame(metrics_frame, bg=self.config["theme"]["secondary_bg"])
            frame.pack(fill=tk.X, padx=5, pady=2)

            # Label
            label = tk.Label(
                frame,
                textvariable=self.status_vars[metric],
                font=("Courier", 9),
                fg=self.config["theme"]["text_color"],
                bg=self.config["theme"]["secondary_bg"],
                anchor='w'
            )
            label.pack(side=tk.TOP, anchor='w')

            # Progress bar
            progress = ttk.Progressbar(
                frame,
                length=200,
                mode='determinate'
            )
            progress.pack(side=tk.TOP, fill=tk.X, pady=1)
            self.progress_bars[metric] = progress

    def create_gpu_metrics(self, parent):
        """Create GPU monitoring section"""
        gpu_frame = tk.LabelFrame(
            parent,
            text="GPU Metrics",
            font=("Orbitron", 11, "bold"),
            fg=self.config["theme"]["accent_color"],
            bg=self.config["theme"]["secondary_bg"]
        )
        gpu_frame.pack(fill=tk.X, padx=5, pady=5)

        # Initialize GPU status variables
        for i in range(2):  # Support up to 2 GPUs
            gpu_key = f"gpu{i}"
            self.status_vars[gpu_key] = tk.StringVar(value=f"GPU {i}: N/A")

            frame = tk.Frame(gpu_frame, bg=self.config["theme"]["secondary_bg"])
            frame.pack(fill=tk.X, padx=5, pady=2)

            label = tk.Label(
                frame,
                textvariable=self.status_vars[gpu_key],
                font=("Courier", 9),
                fg=self.config["theme"]["text_color"],
                bg=self.config["theme"]["secondary_bg"],
                anchor='w'
            )
            label.pack(side=tk.TOP, anchor='w')

            progress = ttk.Progressbar(
                frame,
                length=200,
                mode='determinate'
            )
            progress.pack(side=tk.TOP, fill=tk.X, pady=1)
            self.progress_bars[gpu_key] = progress

    def create_agent_status(self, parent):
        """Create agent component status display"""
        agent_frame = tk.LabelFrame(
            parent,
            text="Agent Components",
            font=("Orbitron", 11, "bold"),
            fg=self.config["theme"]["accent_color"],
            bg=self.config["theme"]["secondary_bg"]
        )
        agent_frame.pack(fill=tk.X, padx=5, pady=5)

        components = ['brain', 'voice', 'memory', 'tools', 'maverick']

        for component in components:
            self.status_vars[component] = tk.StringVar(value=f"{component.title()}: Unknown")

            frame = tk.Frame(agent_frame, bg=self.config["theme"]["secondary_bg"])
            frame.pack(fill=tk.X, padx=5, pady=2)

            # Status indicator (colored dot)
            status_dot = tk.Label(
                frame,
                text="●",
                font=("Arial", 12),
                fg="#666666",  # Default gray
                bg=self.config["theme"]["secondary_bg"]
            )
            status_dot.pack(side=tk.LEFT)

            # Component status label
            label = tk.Label(
                frame,
                textvariable=self.status_vars[component],
                font=("Courier", 9),
                fg=self.config["theme"]["text_color"],
                bg=self.config["theme"]["secondary_bg"],
                anchor='w'
            )
            label.pack(side=tk.LEFT, padx=(5, 0))

            # Store dot reference for color updates
            setattr(self, f"{component}_dot", status_dot)

    def create_quick_actions(self, parent):
        """Create quick action buttons"""
        actions_frame = tk.LabelFrame(
            parent,
            text="Quick Actions",
            font=("Orbitron", 11, "bold"),
            fg=self.config["theme"]["accent_color"],
            bg=self.config["theme"]["secondary_bg"]
        )
        actions_frame.pack(fill=tk.X, padx=5, pady=5)

        actions = [
            ("📸 Screenshot", self.take_screenshot),
            ("🌐 Browser", lambda: self.execute_command("open browser")),
            ("📊 System Info", self.show_system_info),
            ("⚙️ Settings", self.show_settings)
        ]

        for text, command in actions:
            btn = tk.Button(
                actions_frame,
                text=text,
                command=command,
                bg=self.config["theme"]["success_color"],
                fg="white",
                font=("Courier", 9, "bold"),
                relief=tk.FLAT,
                padx=8,
                pady=3,
                cursor="hand2"
            )
            btn.pack(fill=tk.X, padx=2, pady=1)

    def create_conversation_panel(self, parent):
        """Create conversation display panel"""
        # Panel title
        title_label = tk.Label(
            parent,
            text="💬 CONVERSATION LOG",
            font=("Orbitron", 14, "bold"),
            fg=self.config["theme"]["accent_color"],
            bg=self.config["theme"]["secondary_bg"]
        )
        title_label.pack(pady=10)

        # Conversation display
        self.conversation_text = scrolledtext.ScrolledText(
            parent,
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg="#2c3e50",
            fg=self.config["theme"]["text_color"],
            font=("Courier", 11),
            insertbackground="#3498db",
            relief=tk.FLAT,
            borderwidth=0
        )
        self.conversation_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Configure text tags for styling
        self.conversation_text.tag_configure("user", foreground="#3498db", font=("Courier", 11, "bold"))
        self.conversation_text.tag_configure("ultron", foreground=self.config["theme"]["accent_color"], font=("Courier", 11, "bold"))
        self.conversation_text.tag_configure("system", foreground=self.config["theme"]["warning_color"], font=("Courier", 11, "italic"))
        self.conversation_text.tag_configure("error", foreground=self.config["theme"]["error_color"], font=("Courier", 11, "bold"))

        # Welcome message
        self.add_to_conversation("ULTRON", "🤖 ULTRON Agent 3.0 initialized. Ready for commands.")

        if self.agent_ref:
            brain_status = "✅ Connected" if hasattr(self.agent_ref, 'brain') and self.agent_ref.brain else "❌ Not Available"
            voice_status = "✅ Connected" if hasattr(self.agent_ref, 'voice') and self.agent_ref.voice else "❌ Not Available"
            tools_count = len(getattr(self.agent_ref, 'tools', [])) if hasattr(self.agent_ref, 'tools') else 0

            self.add_to_conversation("SYSTEM", f"🧠 Brain: {brain_status}")
            self.add_to_conversation("SYSTEM", f"🎤 Voice: {voice_status}")
            self.add_to_conversation("SYSTEM", f"🔧 Tools: {tools_count} loaded")

    def create_control_panel(self, parent):
        """Create control panel with voice and tool controls"""
        # Panel title
        title_label = tk.Label(
            parent,
            text="🎛️ CONTROL PANEL",
            font=("Orbitron", 14, "bold"),
            fg=self.config["theme"]["accent_color"],
            bg=self.config["theme"]["secondary_bg"]
        )
        title_label.pack(pady=10)

        # Voice controls section
        voice_frame = tk.LabelFrame(
            parent,
            text="Voice Controls",
            font=("Orbitron", 11, "bold"),
            fg=self.config["theme"]["accent_color"],
            bg=self.config["theme"]["secondary_bg"]
        )
        voice_frame.pack(fill=tk.X, padx=10, pady=5)

        # Voice control button
        self.voice_btn = tk.Button(
            voice_frame,
            text="🎤 Start Listening",
            command=self.toggle_voice_listening,
            bg=self.config["theme"]["success_color"],
            fg="white",
            font=("Courier", 11, "bold"),
            relief=tk.FLAT,
            padx=10,
            pady=8,
            cursor="hand2"
        )
        self.voice_btn.pack(fill=tk.X, padx=5, pady=5)

        # Voice status
        self.voice_status_var = tk.StringVar(value="Voice: Ready")
        voice_status_label = tk.Label(
            voice_frame,
            textvariable=self.voice_status_var,
            font=("Courier", 10),
            fg=self.config["theme"]["text_color"],
            bg=self.config["theme"]["secondary_bg"]
        )
        voice_status_label.pack(pady=5)

        # Tools section
        if self.agent_ref and hasattr(self.agent_ref, 'tools'):
            self.create_tools_section(parent)

    def create_tools_section(self, parent):
        """Create tools control section"""
        tools_frame = tk.LabelFrame(
            parent,
            text="Available Tools",
            font=("Orbitron", 11, "bold"),
            fg=self.config["theme"]["accent_color"],
            bg=self.config["theme"]["secondary_bg"]
        )
        tools_frame.pack(fill=tk.X, padx=10, pady=5)

        # Create scrollable tools list
        tools_canvas = tk.Canvas(tools_frame, bg=self.config["theme"]["secondary_bg"], height=150, highlightthickness=0)
        tools_scrollbar = ttk.Scrollbar(tools_frame, orient="vertical", command=tools_canvas.yview)
        tools_scroll_frame = tk.Frame(tools_canvas, bg=self.config["theme"]["secondary_bg"])

        tools_scroll_frame.bind(
            "<Configure>",
            lambda e: tools_canvas.configure(scrollregion=tools_canvas.bbox("all"))
        )

        tools_canvas.create_window((0, 0), window=tools_scroll_frame, anchor="nw")
        tools_canvas.configure(yscrollcommand=tools_scrollbar.set)

        tools_canvas.pack(side="left", fill="both", expand=True, padx=5)
        tools_scrollbar.pack(side="right", fill="y")

        # Add tool buttons
        if self.agent_ref and hasattr(self.agent_ref, 'tools'):
            for tool in self.agent_ref.tools:
                tool_name = getattr(tool, '__class__', type(tool)).__name__
                tool_btn = tk.Button(
                    tools_scroll_frame,
                    text=f"🔧 {tool_name}",
                    command=lambda t=tool_name: self.execute_tool_command(t),
                    bg="#3498db",
                    fg="white",
                    font=("Courier", 9),
                    relief=tk.FLAT,
                    padx=5,
                    pady=2,
                    cursor="hand2"
                )
                tool_btn.pack(fill=tk.X, padx=2, pady=1)

    def create_command_input_panel(self, parent):
        """Create command input panel"""
        input_frame = tk.Frame(parent, bg=self.config["theme"]["warning_color"], relief=tk.RAISED, bd=3)
        input_frame.pack(fill=tk.X, pady=(10, 0))

        # Input container
        input_container = tk.Frame(input_frame, bg=self.config["theme"]["warning_color"])
        input_container.pack(fill=tk.X, padx=15, pady=10)

        # Input label
        input_label = tk.Label(
            input_container,
            text="💻 Command Input:",
            font=("Orbitron", 12, "bold"),
            bg=self.config["theme"]["warning_color"],
            fg="white"
        )
        input_label.pack(anchor='w', pady=(0, 5))

        # Entry frame
        entry_frame = tk.Frame(input_container, bg=self.config["theme"]["warning_color"])
        entry_frame.pack(fill=tk.X, pady=5)

        # Command entry
        self.command_entry = tk.Entry(
            entry_frame,
            font=("Courier", 12),
            bg=self.config["theme"]["secondary_bg"],
            fg=self.config["theme"]["text_color"],
            insertbackground="#3498db",
            relief=tk.FLAT,
            borderwidth=5
        )
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.command_entry.bind('<Return>', self.process_command_input)

        # Execute button
        execute_btn = tk.Button(
            entry_frame,
            text="▶ Execute",
            command=self.process_command_input,
            bg=self.config["theme"]["success_color"],
            fg="white",
            font=("Courier", 11, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        execute_btn.pack(side=tk.RIGHT)

        # Quick commands row
        quick_frame = tk.Frame(input_container, bg=self.config["theme"]["warning_color"])
        quick_frame.pack(fill=tk.X, pady=(5, 0))

        quick_commands = [
            ("Status", "system status"),
            ("Help", "help"),
            ("Tools", "list tools"),
            ("Screenshot", "take screenshot")
        ]

        for label, command in quick_commands:
            btn = tk.Button(
                quick_frame,
                text=label,
                command=lambda cmd=command: self.quick_command(cmd),
                bg="#34495e",
                fg="white",
                font=("Courier", 9),
                relief=tk.FLAT,
                padx=6,
                pady=2,
                cursor="hand2"
            )
            btn.pack(side=tk.LEFT, padx=2)

    def add_to_conversation(self, speaker: str, message: str):
        """Thread-safe method to add message to conversation"""
        if not self.root or not hasattr(self, 'conversation_text'):
            return

        def _add_message():
            try:
                self.conversation_text.config(state=tk.NORMAL)

                timestamp = time.strftime("%H:%M:%S")

                # Determine tag based on speaker
                if speaker == "ULTRON":
                    tag = "ultron"
                elif speaker == "USER":
                    tag = "user"
                elif speaker == "SYSTEM":
                    tag = "system"
                else:
                    tag = "error"

                # Insert message with proper formatting
                self.conversation_text.insert(tk.END, f"[{timestamp}] {speaker}: ", tag)
                self.conversation_text.insert(tk.END, f"{message}\\n\\n")
                self.conversation_text.config(state=tk.DISABLED)
                self.conversation_text.see(tk.END)

                # Add to history
                self.conversation_history.append({
                    'timestamp': timestamp,
                    'speaker': speaker,
                    'message': message
                })

                # Limit history size
                if len(self.conversation_history) > 1000:
                    self.conversation_history = self.conversation_history[-800:]

            except Exception as e:
                self.logger.error(f"Error adding conversation message: {e}")

        # Schedule on main thread
        if self.root:
            self.root.after(0, _add_message)

    def process_command_input(self, event=None):
        """Process command input from entry field"""
        command = self.command_entry.get().strip()
        if not command:
            return

        self.command_entry.delete(0, tk.END)
        self.execute_command(command)

    def quick_command(self, command: str):
        """Execute a quick command"""
        self.execute_command(command)

    def execute_command(self, command: str):
        """Execute command through agent (thread-safe)"""
        self.add_to_conversation("USER", command)

        # Send command to agent if available
        if self.agent_ref and hasattr(self.agent_ref, 'process_command'):
            try:
                # Queue command for background processing
                threading.Thread(target=self._execute_agent_command, args=(command,), daemon=True).start()

            except Exception as e:
                self.add_to_conversation("ERROR", f"Command processing failed: {str(e)}")
        else:
            # Fallback for basic commands
            response = self._handle_basic_command(command)
            if response:
                self.add_to_conversation("ULTRON", response)

    def execute_tool_command(self, tool_name: str):
        """Execute a specific tool command"""
        command = f"use tool {tool_name}"
        self.execute_command(command)

    def _execute_agent_command(self, command: str):
        """Execute command through agent in background thread"""
        try:
            if hasattr(self.agent_ref, 'process_command'):
                response = self.agent_ref.process_command(command)
                if response:
                    self.add_to_conversation("ULTRON", response)
        except Exception as e:
            self.add_to_conversation("ERROR", f"Agent command error: {str(e)}")

    def _handle_basic_command(self, command: str) -> str:
        """Handle basic commands when agent is not available"""
        command = command.lower().strip()

        if any(word in command for word in ["hello", "hi", "hey"]):
            return "Hello! ULTRON systems online and ready."

        elif "status" in command:
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            return f"System Status: CPU {cpu:.1f}%, Memory {memory:.1f}%"

        elif "time" in command:
            return f"Current time: {time.strftime('%Y-%m-%d %H:%M:%S')}"

        elif "screenshot" in command:
            return self.take_screenshot()

        elif "help" in command:
            return ("Available commands: hello, status, time, screenshot, help, "
                   "system info, open browser, settings")

        elif "tools" in command:
            if self.agent_ref and hasattr(self.agent_ref, 'tools'):
                tools = [tool.__class__.__name__ for tool in self.agent_ref.tools]
                return f"Available tools: {', '.join(tools)}"
            else:
                return "No tools available (agent not connected)"

        else:
            return f"Processing command: {command}. Use 'help' for available commands."

    def toggle_voice_listening(self):
        """Toggle voice listening mode"""
        if not self.agent_ref or not hasattr(self.agent_ref, 'voice'):
            self.add_to_conversation("ERROR", "Voice system not available")
            return

        if not self.listening:
            self.listening = True
            self.voice_btn.config(
                text="🛑 Stop Listening",
                bg=self.config["theme"]["error_color"]
            )
            self.voice_status_var.set("Voice: Listening...")
            self.add_to_conversation("SYSTEM", "Voice listening activated")
        else:
            self.listening = False
            self.voice_btn.config(
                text="🎤 Start Listening",
                bg=self.config["theme"]["success_color"]
            )
            self.voice_status_var.set("Voice: Ready")
            self.add_to_conversation("SYSTEM", "Voice listening deactivated")

    def take_screenshot(self) -> str:
        """Take screenshot and save to assets"""
        try:
            from PIL import ImageGrab
            screenshot = ImageGrab.grab()

            # Create assets directory if it doesn't exist
            assets_dir = Path("assets")
            assets_dir.mkdir(exist_ok=True)

            # Save screenshot
            timestamp = int(time.time())
            screenshot_path = assets_dir / f"ultron_screenshot_{timestamp}.png"
            screenshot.save(screenshot_path)

            return f"📸 Screenshot saved: {screenshot_path}"

        except Exception as e:
            return f"❌ Screenshot failed: {str(e)}"

    def show_system_info(self):
        """Display comprehensive system information"""
        try:
            # Gather system info
            info = {
                "Platform": sys.platform,
                "CPU Cores": psutil.cpu_count(),
                "Total Memory": f"{psutil.virtual_memory().total / (1024**3):.1f} GB",
                "Python Version": sys.version.split()[0],
                "ULTRON Version": "3.0"
            }

            # Add GPU info if available
            if GPU_AVAILABLE:
                try:
                    pynvml.nvmlInit()
                    device_count = pynvml.nvmlDeviceGetCount()
                    info["GPU Count"] = device_count

                    if device_count > 0:
                        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                        name = pynvml.nvmlDeviceGetName(handle).decode('utf-8')
                        info["Primary GPU"] = name

                except Exception:
                    info["GPU Status"] = "NVIDIA GPU monitoring unavailable"

            # Format info
            info_text = "\\n".join([f"{k}: {v}" for k, v in info.items()])
            self.add_to_conversation("SYSTEM", f"🖥️ System Information:\\n{info_text}")

        except Exception as e:
            self.add_to_conversation("ERROR", f"Failed to get system info: {str(e)}")

    def show_settings(self):
        """Show settings dialog"""
        try:
            settings_window = tk.Toplevel(self.root)
            settings_window.title("ULTRON Settings")
            settings_window.geometry("500x400")
            settings_window.configure(bg=self.config["theme"]["secondary_bg"])
            settings_window.grab_set()  # Make modal

            # Settings content
            tk.Label(
                settings_window,
                text="⚙️ ULTRON Settings",
                font=("Orbitron", 18, "bold"),
                fg=self.config["theme"]["accent_color"],
                bg=self.config["theme"]["secondary_bg"]
            ).pack(pady=20)

            # Theme settings
            theme_frame = tk.LabelFrame(
                settings_window,
                text="GUI Settings",
                font=("Orbitron", 12),
                fg=self.config["theme"]["accent_color"],
                bg=self.config["theme"]["secondary_bg"]
            )
            theme_frame.pack(fill=tk.X, padx=20, pady=10)

            tk.Label(
                theme_frame,
                text="Theme and display settings coming soon...",
                bg=self.config["theme"]["secondary_bg"],
                fg=self.config["theme"]["text_color"]
            ).pack(pady=10)

            # Close button
            tk.Button(
                settings_window,
                text="Close",
                command=settings_window.destroy,
                bg=self.config["theme"]["success_color"],
                fg="white",
                font=("Courier", 11, "bold")
            ).pack(pady=20)

        except Exception as e:
            self.add_to_conversation("ERROR", f"Settings error: {str(e)}")

    def update_system_status(self):
        """Update system status display"""
        if not self.running or not self.root:
            return

        try:
            # Basic system metrics
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent

            # Update status variables
            self.status_vars['cpu'].set(f"CPU: {cpu:.1f}%")
            self.status_vars['memory'].set(f"Memory: {memory:.1f}%")
            self.status_vars['disk'].set(f"Disk: {disk:.1f}%")

            # Update progress bars
            if 'cpu' in self.progress_bars:
                self.progress_bars['cpu']['value'] = cpu
            if 'memory' in self.progress_bars:
                self.progress_bars['memory']['value'] = memory
            if 'disk' in self.progress_bars:
                self.progress_bars['disk']['value'] = disk

            # Update network status
            try:
                net_io = psutil.net_io_counters()
                self.status_vars['network'].set("Network: Active")
                if 'network' in self.progress_bars:
                    self.progress_bars['network']['value'] = 50  # Placeholder
            except:
                self.status_vars['network'].set("Network: Unknown")

            # GPU status update
            if GPU_AVAILABLE:
                self.update_gpu_status()

            # Agent component status update
            self.update_agent_component_status()

            # Update time display
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            self.time_var.set(f"Time: {current_time}")

            # Update uptime
            uptime = time.time() - self.start_time
            uptime_str = time.strftime("%H:%M:%S", time.gmtime(uptime))
            self.uptime_var.set(f"Uptime: {uptime_str}")

        except Exception as e:
            self.logger.error(f"Status update error: {e}")

    def update_gpu_status(self):
        """Update GPU status information"""
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

            # Mark unused GPU slots
            for i in range(device_count, 2):
                self.status_vars[f'gpu{i}'].set(f"GPU {i}: N/A")
                if f'gpu{i}' in self.progress_bars:
                    self.progress_bars[f'gpu{i}']['value'] = 0

        except Exception:
            # GPU monitoring failed
            for i in range(2):
                self.status_vars[f'gpu{i}'].set(f"GPU {i}: Error")
                if f'gpu{i}' in self.progress_bars:
                    self.progress_bars[f'gpu{i}']['value'] = 0

    def update_agent_component_status(self):
        """Update agent component status indicators"""
        if not self.agent_ref:
            return

        try:
            # Brain status
            if hasattr(self.agent_ref, 'brain') and self.agent_ref.brain:
                self.status_vars['brain'].set("Brain: ✅ Online")
                self.brain_dot.config(fg=self.config["theme"]["success_color"])
            else:
                self.status_vars['brain'].set("Brain: ❌ Offline")
                self.brain_dot.config(fg=self.config["theme"]["error_color"])

            # Voice status
            if hasattr(self.agent_ref, 'voice') and self.agent_ref.voice:
                status = "Listening" if self.listening else "Ready"
                self.status_vars['voice'].set(f"Voice: ✅ {status}")
                self.voice_dot.config(fg=self.config["theme"]["success_color"])
            else:
                self.status_vars['voice'].set("Voice: ❌ Offline")
                self.voice_dot.config(fg=self.config["theme"]["error_color"])

            # Memory status
            if hasattr(self.agent_ref, 'memory') and self.agent_ref.memory:
                self.status_vars['memory'].set("Memory: ✅ Active")
                self.memory_dot.config(fg=self.config["theme"]["success_color"])
            else:
                self.status_vars['memory'].set("Memory: ❌ Offline")
                self.memory_dot.config(fg=self.config["theme"]["error_color"])

            # Tools status
            if hasattr(self.agent_ref, 'tools'):
                tool_count = len(self.agent_ref.tools)
                self.status_vars['tools'].set(f"Tools: ✅ {tool_count} loaded")
                self.tools_dot.config(fg=self.config["theme"]["success_color"])
            else:
                self.status_vars['tools'].set("Tools: ❌ None")
                self.tools_dot.config(fg=self.config["theme"]["error_color"])

            # Maverick status
            if hasattr(self.agent_ref, 'maverick_engine'):
                self.status_vars['maverick'].set("Maverick: ✅ Active")
                self.maverick_dot.config(fg=self.config["theme"]["success_color"])
            else:
                self.status_vars['maverick'].set("Maverick: ❌ Inactive")
                self.maverick_dot.config(fg=self.config["theme"]["error_color"])

        except Exception as e:
            self.logger.error(f"Agent status update error: {e}")

    def start_background_tasks(self):
        """Start background monitoring and update tasks"""
        def status_update_loop():
            while self.running and self.root:
                try:
                    self.root.after(0, self.update_system_status)
                    time.sleep(2)  # Update every 2 seconds
                except Exception as e:
                    self.logger.error(f"Background task error: {e}")
                    break

        # Start background thread for status updates
        self.status_thread = threading.Thread(target=status_update_loop, daemon=True)
        self.status_thread.start()
        self.logger.info("Background monitoring tasks started")

    def on_closing(self):
        """Handle window closing"""
        self.logger.info("🔴 Shutting down Pokédex GUI...")
        self.running = False

        # Save configuration
        self.save_gui_config()

        # Stop listening if active
        if self.listening:
            self.listening = False

        # Clean up
        if hasattr(self, 'status_thread'):
            self.status_thread = None

        # Close GUI
        if self.root:
            self.root.quit()
            self.root.destroy()
            self.root = None

        self.logger.info("Pokédex GUI shutdown complete")

    def run_gui(self):
        """Main GUI execution method (call from main thread)"""
        try:
            self.initialize_gui()
            if self.root:
                self.logger.info("🚀 Starting Pokédex GUI main loop...")
                self.root.mainloop()
        except Exception as e:
            self.logger.error(f"GUI execution error: {e}")
            raise


# Factory function for creating GUI instances
def create_pokedex_gui(agent_ref=None) -> IntegratedPokedexGUI:
    """Factory function to create Pokédx GUI instance"""
    return IntegratedPokedexGUI(agent_ref)


# For standalone testing
if __name__ == "__main__":
    print("🤖 ULTRON Agent 3.0 - Pokédex GUI Test Mode")
    print("=" * 50)

    gui = create_pokedex_gui()
    gui.run_gui()
