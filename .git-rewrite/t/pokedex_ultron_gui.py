import tkinter as tk
from tkinter import ttk, scrolledtext, Toplevel, Frame, Label, Button, Entry, messagebox
from PIL import Image, ImageTk
import threading
import psutil
import time
import os
import logging
import webbrowser
from pathlib import Path

class PokedexUltronGUI:
    """Pokedex-style GUI with full ULTRON Agent functionality"""
    
    def __init__(self, agent_handle, test_mode=False):
        self.agent_handle = agent_handle
        self.test_mode = test_mode
        self.listening = False
        self.conversation_history = []
        
        if not self.test_mode:
            self.root = tk.Tk()
            self.root.title("ULTRON Agent 3.0 - Pokedex Interface")
            self.root.geometry("1400x900")
            self.root.minsize(1200, 800)
            self.root.configure(bg='#1a1a2e')
            
            self.image_cache = {}
            self._load_images()
            self._create_pokedex_ui()
            self._start_monitoring()
            
            # Add welcome message
            self.add_message("ULTRON", "ULTRON AI Assistant initialized. Ready for commands.")
        else:
            self.root = None
            self.image_cache = {}

    def _load_images(self):
        """Load GUI images if available"""
        image_paths = {
            "background": "resources/images/image-15-1280x717.png",
            "avatar": "resources/images/ChatGPT Image Jul 29, 2025, 02_32_42 AM.png",
            "tools_bg": "resources/images/PDA-1280x1280.png",
        }
        
        for name, path in image_paths.items():
            try:
                if os.path.exists(path):
                    img = Image.open(path)
                    self.image_cache[name] = img
                else:
                    logging.warning(f"Image not found: {path}")
                    self.image_cache[name] = None
            except Exception as e:
                logging.error(f"Failed to load image {name}: {e}")
                self.image_cache[name] = None

    def _create_pokedex_ui(self):
        """Create Pokedex-style interface with ULTRON functionality"""
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top section - Pokedex header with ULTRON branding
        top_frame = tk.Frame(main_frame, bg='#e74c3c', relief=tk.RAISED, bd=3)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # ULTRON title with glow effect
        title_frame = tk.Frame(top_frame, bg='#2c3e50')
        title_frame.pack(fill=tk.X, padx=5, pady=5)
        
        title_label = tk.Label(
            title_frame, 
            text="ULTRON v3.0", 
            font=("Orbitron", 24, "bold"),
            fg='#00ff41', 
            bg='#2c3e50'
        )
        title_label.pack()
        
        status_label = tk.Label(
            title_frame,
            text="Advanced AI Assistant - Online",
            font=("Courier", 12),
            fg='#3498db',
            bg='#2c3e50'
        )
        status_label.pack()
        
        # Middle section - Main display
        middle_frame = tk.Frame(main_frame, bg='#16213e')
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Left panel - System status
        left_panel = tk.Frame(middle_frame, bg='#2c3e50', width=320)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        self._create_status_panel(left_panel)
        
        # Center panel - Conversation
        center_panel = tk.Frame(middle_frame, bg='#34495e')
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self._create_conversation_panel(center_panel)
        
        # Right panel - Controls
        right_panel = tk.Frame(middle_frame, bg='#2c3e50', width=320)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)
        
        self._create_control_panel(right_panel)
        
        # Bottom section - Command input
        bottom_frame = tk.Frame(main_frame, bg='#e67e22', relief=tk.RAISED, bd=3)
        bottom_frame.pack(fill=tk.X)
        
        self._create_input_panel(bottom_frame)

    def _create_status_panel(self, parent):
        """Create system status panel with real-time monitoring"""
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
        
        # ULTRON tools section
        tk.Label(
            parent, 
            text="ULTRON TOOLS", 
            font=("Orbitron", 12, "bold"),
            fg='#00ff41', 
            bg='#2c3e50'
        ).pack(pady=(20, 10))
        
        # Tools container with scrolling
        tools_container = tk.Frame(parent, bg='#2c3e50')
        tools_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create scrollable frame for tools
        canvas = tk.Canvas(tools_container, bg='#2c3e50', highlightthickness=0)
        scrollbar = ttk.Scrollbar(tools_container, orient="vertical", command=canvas.yview)
        self.tools_frame = tk.Frame(canvas, bg='#2c3e50')
        
        self.tools_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.tools_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Populate tools
        self._populate_tools()

    def _populate_tools(self):
        """Populate the tools panel with available ULTRON tools"""
        try:
            tools = self.agent_handle.list_tools() if hasattr(self.agent_handle, 'list_tools') else []
            if not tools:
                # Default tools if none available
                tools = [
                    {'name': 'screenshot', 'description': 'Take a screenshot'},
                    {'name': 'system_info', 'description': 'Get system information'},
                    {'name': 'file_browser', 'description': 'Browse files'},
                    {'name': 'web_search', 'description': 'Search the web'},
                    {'name': 'voice_control', 'description': 'Voice commands'}
                ]
        except Exception as e:
            logging.error(f"Could not fetch tools: {e}")
            tools = []
        
        # Clear existing tools
        for widget in self.tools_frame.winfo_children():
            widget.destroy()
        
        # Add tools
        for i, tool in enumerate(tools):
            tool_name = tool.get('name', 'Unknown Tool')
            tool_desc = tool.get('description', 'No description')
            
            tool_btn = tk.Button(
                self.tools_frame,
                text=tool_name.replace('_', ' ').title(),
                command=lambda t=tool_name: self._execute_tool(t),
                bg='#3498db',
                fg='white',
                font=("Courier", 9, "bold"),
                relief=tk.FLAT,
                padx=5,
                pady=3
            )
            tool_btn.pack(fill=tk.X, pady=2)

    def _execute_tool(self, tool_name):
        """Execute a selected tool"""
        command = f"execute the {tool_name} tool"
        self.add_message("User (Tool)", command)
        threading.Thread(target=self._get_agent_response, args=(command,), daemon=True).start()

    def _create_conversation_panel(self, parent):
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
            font=("Consolas", 11),
            insertbackground='#3498db'
        )
        self.conversation_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure text tags for styling
        self.conversation_text.tag_configure("user", foreground="#3498db")
        self.conversation_text.tag_configure("ultron", foreground="#00ff41")
        self.conversation_text.tag_configure("system", foreground="#e67e22")
        self.conversation_text.tag_configure("tool", foreground="#f39c12")

    def _create_control_panel(self, parent):
        """Create control panel with ULTRON settings"""
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
            command=self._toggle_listening,
            bg='#27ae60',
            fg='white',
            font=("Courier", 12, "bold"),
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.voice_btn.pack(fill=tk.X, padx=10, pady=5)
        
        # Agent configuration
        tk.Label(
            parent, 
            text="AGENT CONFIG", 
            font=("Orbitron", 12, "bold"),
            fg='#00ff41', 
            bg='#2c3e50'
        ).pack(pady=(20, 10))
        
        # LLM model selection
        llm_frame = tk.Frame(parent, bg='#2c3e50')
        llm_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(llm_frame, text="LLM Model:", bg='#2c3e50', fg='#ecf0f1', font=("Courier", 9)).pack(anchor='w')
        
        try:
            if hasattr(self.agent_handle, 'config'):
                models = list(self.agent_handle.config.get('ollama_models', ['qwen2.5:latest', 'llama3.2:latest']))
                current_model = self.agent_handle.config.get('llm_model', models[0])
            else:
                models = ['qwen2.5:latest', 'llama3.2:latest', 'hermes3:latest', 'phi-3-mini']
                current_model = models[0]
        except Exception as e:
            logging.error(f"Could not get models: {e}")
            models = ['qwen2.5:latest', 'llama3.2:latest']
            current_model = models[0]
            
        self.llm_model_var = tk.StringVar(value=current_model)
        llm_combo = ttk.Combobox(llm_frame, textvariable=self.llm_model_var, values=models, state="readonly")
        llm_combo.pack(fill=tk.X, pady=2)
        llm_combo.bind("<<ComboboxSelected>>", self._update_llm_model)
        
        # Voice engine selection
        voice_frame = tk.Frame(parent, bg='#2c3e50')
        voice_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(voice_frame, text="Voice Engine:", bg='#2c3e50', fg='#ecf0f1', font=("Courier", 9)).pack(anchor='w')
        
        try:
            current_voice = self.agent_handle.config.get("voice_engine", "pyttsx3") if hasattr(self.agent_handle, 'config') else "pyttsx3"
        except:
            current_voice = "pyttsx3"
            
        self.voice_engine_var = tk.StringVar(value=current_voice)
        voice_combo = ttk.Combobox(voice_frame, textvariable=self.voice_engine_var, state="readonly")
        voice_combo['values'] = ("pyttsx3", "elevenlabs", "openai", "enhanced")
        voice_combo.pack(fill=tk.X, pady=2)
        voice_combo.bind("<<ComboboxSelected>>", self._update_voice_engine)
        
        # Feature toggles
        toggles_frame = tk.Frame(parent, bg='#2c3e50')
        toggles_frame.pack(fill=tk.X, padx=10, pady=10)
        
        try:
            voice_enabled = self.agent_handle.config.get("use_voice", True) if hasattr(self.agent_handle, 'config') else True
            vision_enabled = self.agent_handle.config.get("use_vision", True) if hasattr(self.agent_handle, 'config') else True
        except:
            voice_enabled = True
            vision_enabled = True
            
        self.voice_enabled = tk.BooleanVar(value=voice_enabled)
        self.vision_enabled = tk.BooleanVar(value=vision_enabled)
        
        tk.Checkbutton(toggles_frame, text="Voice Output", variable=self.voice_enabled, 
                      bg='#2c3e50', fg='#ecf0f1', selectcolor='#34495e',
                      command=self._update_voice_setting).pack(anchor='w')
        tk.Checkbutton(toggles_frame, text="Vision System", variable=self.vision_enabled, 
                      bg='#2c3e50', fg='#ecf0f1', selectcolor='#34495e',
                      command=self._update_vision_setting).pack(anchor='w')
        
        # Quick actions
        tk.Label(
            parent, 
            text="QUICK ACTIONS", 
            font=("Orbitron", 12, "bold"),
            fg='#00ff41', 
            bg='#2c3e50'
        ).pack(pady=(20, 10))
        
        actions = [
            ("📸 Screenshot", self._take_screenshot),
            ("📁 File Browser", self._open_file_browser),
            ("⚙️ Advanced Settings", self._open_advanced_settings),
            ("🌐 Web Browser", lambda: webbrowser.open("https://google.com")),
            ("📊 System Info", self._show_system_info)
        ]
        
        for text, command in actions:
            btn = tk.Button(
                parent,
                text=text,
                command=command,
                bg='#3498db',
                fg='white',
                font=("Courier", 9, "bold"),
                relief=tk.FLAT,
                padx=5,
                pady=3
            )
            btn.pack(fill=tk.X, padx=10, pady=2)

    def _create_input_panel(self, bottom_frame):
        """Create command input panel"""
        input_container = tk.Frame(bottom_frame, bg='#e67e22')
        input_container.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            input_container,
            text="COMMAND INPUT:",
            font=("Orbitron", 12, "bold"),
            fg='#2c3e50',
            bg='#e67e22'
        ).pack(anchor='w', pady=(0, 5))
        
        input_frame = tk.Frame(input_container, bg='#2c3e50', relief=tk.SUNKEN, bd=2)
        input_frame.pack(fill=tk.X, pady=5)
        
        self.user_input = tk.Entry(
            input_frame,
            bg='#34495e',
            fg='#ecf0f1',
            font=("Consolas", 12),
            relief=tk.FLAT,
            borderwidth=0,
            insertbackground='#3498db'
        )
        self.user_input.pack(fill=tk.X, padx=5, pady=5, ipady=8)
        self.user_input.bind("<Return>", self.send_message)
        self.user_input.focus_set()
        
        # Send button
        send_btn = tk.Button(
            input_container,
            text="SEND COMMAND",
            command=self.send_message,
            bg='#27ae60',
            fg='white',
            font=("Courier", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=5
        )
        send_btn.pack(side=tk.RIGHT, padx=(10, 0))

    def send_message(self, event=None):
        """Send user message to ULTRON"""
        message = self.user_input.get().strip()
        if message:
            self.add_message("User", message)
            self.user_input.delete(0, tk.END)
            threading.Thread(target=self._get_agent_response, args=(message,), daemon=True).start()

    def _get_agent_response(self, message):
        """Get response from ULTRON agent"""
        try:
            response = self.agent_handle.handle_text(message) if hasattr(self.agent_handle, 'handle_text') else f"Received: {message}"
            self.root.after(0, self.add_message, "ULTRON", response)
        except Exception as e:
            self.root.after(0, self.add_message, "System", f"Error: {e}")

    def add_message(self, sender, message):
        """Add message to conversation log"""
        self.conversation_text.config(state=tk.NORMAL)
        
        # Determine tag based on sender
        if sender == "User":
            tag = "user"
        elif sender == "ULTRON":
            tag = "ultron"
        elif "Tool" in sender:
            tag = "tool"
        else:
            tag = "system"
        
        # Add timestamp
        timestamp = time.strftime("%H:%M:%S")
        self.conversation_text.insert(tk.END, f"[{timestamp}] ", "system")
        self.conversation_text.insert(tk.END, f"{sender}: ", tag)
        self.conversation_text.insert(tk.END, f"{message}\n\n")
        
        self.conversation_text.config(state=tk.DISABLED)
        self.conversation_text.yview(tk.END)

    def _toggle_listening(self):
        """Toggle voice listening"""
        self.listening = not self.listening
        if self.listening:
            self.voice_btn.config(text="🔴 Stop Listening", bg='#e74c3c')
            self.add_message("System", "Voice listening activated")
            # Here you would start voice recognition
        else:
            self.voice_btn.config(text="🎤 Start Listening", bg='#27ae60')
            self.add_message("System", "Voice listening deactivated")

    def _update_llm_model(self, event=None):
        """Update LLM model"""
        new_model = self.llm_model_var.get()
        try:
            if hasattr(self.agent_handle, 'config'):
                self.agent_handle.config.set('llm_model', new_model)
                if hasattr(self.agent_handle.config, 'save_config'):
                    self.agent_handle.config.save_config()
            self.add_message("System", f"LLM model changed to: {new_model}")
        except Exception as e:
            self.add_message("System", f"Error changing model: {e}")

    def _update_voice_engine(self, event=None):
        """Update voice engine"""
        new_engine = self.voice_engine_var.get()
        try:
            if hasattr(self.agent_handle, 'config'):
                self.agent_handle.config.set('voice_engine', new_engine)
                if hasattr(self.agent_handle.config, 'save_config'):
                    self.agent_handle.config.save_config()
            self.add_message("System", f"Voice engine changed to: {new_engine}")
        except Exception as e:
            self.add_message("System", f"Error changing voice engine: {e}")

    def _update_voice_setting(self):
        """Update voice setting"""
        try:
            if hasattr(self.agent_handle, 'config'):
                self.agent_handle.config.set('use_voice', self.voice_enabled.get())
                if hasattr(self.agent_handle.config, 'save_config'):
                    self.agent_handle.config.save_config()
            status = "enabled" if self.voice_enabled.get() else "disabled"
            self.add_message("System", f"Voice output {status}")
        except Exception as e:
            self.add_message("System", f"Error updating voice setting: {e}")

    def _update_vision_setting(self):
        """Update vision setting"""
        try:
            if hasattr(self.agent_handle, 'config'):
                self.agent_handle.config.set('use_vision', self.vision_enabled.get())
                if hasattr(self.agent_handle.config, 'save_config'):
                    self.agent_handle.config.save_config()
            status = "enabled" if self.vision_enabled.get() else "disabled"
            self.add_message("System", f"Vision system {status}")
        except Exception as e:
            self.add_message("System", f"Error updating vision setting: {e}")

    def _take_screenshot(self):
        """Take a screenshot"""
        self.add_message("User (Screenshot)", "Take a screenshot")
        threading.Thread(target=self._get_agent_response, args=("take a screenshot",), daemon=True).start()

    def _open_file_browser(self):
        """Open file browser"""
        try:
            from tkinter import filedialog
            filename = filedialog.askopenfilename(
                title="Select File",
                filetypes=[("All files", "*.*"), ("Python files", "*.py"), ("Text files", "*.txt")]
            )
            if filename:
                self.add_message("User (File Browser)", f"Selected file: {filename}")
                command = f"read the file: {filename}"
                threading.Thread(target=self._get_agent_response, args=(command,), daemon=True).start()
        except Exception as e:
            self.add_message("System", f"File browser error: {e}")

    def _open_advanced_settings(self):
        """Open advanced settings window"""
        settings_window = Toplevel(self.root)
        settings_window.title("Advanced ULTRON Settings")
        settings_window.geometry("600x500")
        settings_window.configure(bg="#2c3e50")
        settings_window.transient(self.root)
        
        tk.Label(
            settings_window,
            text="ADVANCED SETTINGS",
            font=("Orbitron", 16, "bold"),
            fg="#00ff41",
            bg="#2c3e50"
        ).pack(pady=20)
        
        # Add more advanced settings here
        settings_text = scrolledtext.ScrolledText(
            settings_window,
            wrap=tk.WORD,
            bg='#34495e',
            fg='#ecf0f1',
            font=("Consolas", 10)
        )
        settings_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        settings_info = """
ULTRON Agent 3.0 Advanced Configuration

Current Configuration:
- Voice Engine: {voice_engine}
- LLM Model: {llm_model}
- Voice Output: {voice_enabled}
- Vision System: {vision_enabled}

Available Features:
✓ Real-time voice recognition
✓ Multi-modal AI responses
✓ File system integration
✓ Web browsing capabilities
✓ Screenshot and vision analysis
✓ System monitoring
✓ Tool execution framework

Configuration is automatically saved when changes are made.
        """.format(
            voice_engine=self.voice_engine_var.get(),
            llm_model=self.llm_model_var.get(),
            voice_enabled="Enabled" if self.voice_enabled.get() else "Disabled",
            vision_enabled="Enabled" if self.vision_enabled.get() else "Disabled"
        )
        
        settings_text.insert(tk.END, settings_info)
        settings_text.config(state=tk.DISABLED)

    def _show_system_info(self):
        """Show system information"""
        self.add_message("User (System Info)", "Get system information")
        threading.Thread(target=self._get_agent_response, args=("show system information",), daemon=True).start()

    def _start_monitoring(self):
        """Start system monitoring"""
        def update_stats():
            while True:
                try:
                    cpu = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory().percent
                    disk = psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:\\').percent
                    
                    self.root.after(0, self.status_vars['cpu'].set, f"CPU: {cpu:.1f}%")
                    self.root.after(0, self.status_vars['memory'].set, f"Memory: {memory:.1f}%")
                    self.root.after(0, self.status_vars['disk'].set, f"Disk: {disk:.1f}%")
                    
                    # Update AI status based on agent availability
                    try:
                        if hasattr(self.agent_handle, 'handle_text'):
                            self.root.after(0, self.status_vars['ai'].set, "AI: Online")
                        else:
                            self.root.after(0, self.status_vars['ai'].set, "AI: Demo Mode")
                    except:
                        self.root.after(0, self.status_vars['ai'].set, "AI: Offline")
                        
                except Exception as e:
                    logging.error(f"Monitoring error: {e}")
                    
                time.sleep(2)
        
        monitor_thread = threading.Thread(target=update_stats, daemon=True)
        monitor_thread.start()

    def run(self):
        """Start the GUI"""
        if not self.test_mode and self.root:
            self.root.mainloop()

# Example for testing
if __name__ == '__main__':
    class MockAgent:
        def __init__(self):
            self.config = MockConfig()
        
        def handle_text(self, text):
            time.sleep(1)
            return f"ULTRON RESPONSE: Processing '{text}' - Demo mode active"
        
        def list_tools(self):
            return [
                {'name': 'screenshot', 'description': 'Take a screenshot'},
                {'name': 'system_info', 'description': 'Get system information'},
                {'name': 'web_search', 'description': 'Search the internet'},
                {'name': 'file_operations', 'description': 'File system operations'},
                {'name': 'voice_control', 'description': 'Voice commands'}
            ]
    
    class MockConfig:
        def __init__(self):
            self.data = {
                'llm_model': 'qwen2.5:latest',
                'voice_engine': 'pyttsx3',
                'use_voice': True,
                'use_vision': True,
                'ollama_models': ['qwen2.5:latest', 'llama3.2:latest', 'hermes3:latest']
            }
        
        def get(self, key, default=None):
            return self.data.get(key, default)
        
        def set(self, key, value):
            self.data[key] = value
        
        def save_config(self):
            pass  # Mock save

    # Ensure images directory exists
    if not os.path.exists("resources/images"):
        os.makedirs("resources/images")
        print("Created 'resources/images' directory. Add your GUI images there.")

    logging.basicConfig(level=logging.INFO)
    gui = PokedexUltronGUI(MockAgent())
    gui.run()
