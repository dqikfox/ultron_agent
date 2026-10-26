import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import os
import sys
import webbrowser
import psutil
from PIL import Image, ImageTk, ImageGrab
import asyncio
from pathlib import Path

class AgentGUI:
    def __init__(self, agent, log_queue):
        self.agent = agent
        self.log_queue = log_queue
        self.listening = False
        self.conversation_history = []
        
        # Initialize main window
        self.root = tk.Tk()
        self.root.title("ULTRON Agent 2.0 - Pokedex Interface")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a2e')
        
        # Create the Pokedex-style UI
        self.create_pokedex_ui()
        self.start_background_tasks()
        
        # Add initial welcome message
        self.add_to_conversation("ULTRON", "ULTRON AI Assistant initialized. Ready for commands.")

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
            ("File Manager", self.open_file_manager),
            ("Tools Explorer", self.show_tools_explorer)
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
        
        # Agent configuration
        tk.Label(
            parent, 
            text="AGENT CONFIG", 
            font=("Orbitron", 12, "bold"),
            fg='#00ff41', 
            bg='#2c3e50'
        ).pack(pady=(20, 10))
        
        # Voice engine selection
        voice_frame = tk.Frame(parent, bg='#2c3e50')
        voice_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(voice_frame, text="Voice Engine:", bg='#2c3e50', fg='#ecf0f1').pack(anchor='w')
        self.voice_engine_var = tk.StringVar(value=self.agent.config.data.get("voice_engine", "pyttsx3"))
        voice_combo = ttk.Combobox(voice_frame, textvariable=self.voice_engine_var, state="readonly")
        voice_combo['values'] = ("pyttsx3", "elevenlabs", "openai")
        voice_combo.pack(fill=tk.X, pady=2)
        voice_combo.bind("<<ComboboxSelected>>", self.update_voice_engine)
        
        # LLM model selection
        llm_frame = tk.Frame(parent, bg='#2c3e50')
        llm_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(llm_frame, text="LLM Model:", bg='#2c3e50', fg='#ecf0f1').pack(anchor='w')
        self.llm_model_var = tk.StringVar(value=self.agent.config.data.get("llm_model", "llama3.2:latest"))
        llm_combo = ttk.Combobox(llm_frame, textvariable=self.llm_model_var, state="readonly")
        llm_combo['values'] = ("llama3.2:latest", "qwen2.5:latest", "hermes3:latest")
        llm_combo.pack(fill=tk.X, pady=2)
        llm_combo.bind("<<ComboboxSelected>>", self.update_llm_model)
        
        # Enable/disable toggles
        toggles_frame = tk.Frame(parent, bg='#2c3e50')
        toggles_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.voice_enabled = tk.BooleanVar(value=self.agent.config.data.get("use_voice", True))
        self.vision_enabled = tk.BooleanVar(value=self.agent.config.data.get("use_vision", True))
        self.api_enabled = tk.BooleanVar(value=self.agent.config.data.get("use_api", True))
        
        tk.Checkbutton(toggles_frame, text="Voice", variable=self.voice_enabled, 
                      bg='#2c3e50', fg='#ecf0f1', selectcolor='#34495e').pack(anchor='w')
        tk.Checkbutton(toggles_frame, text="Vision", variable=self.vision_enabled,
                      bg='#2c3e50', fg='#ecf0f1', selectcolor='#34495e').pack(anchor='w')
        tk.Checkbutton(toggles_frame, text="API", variable=self.api_enabled,
                      bg='#2c3e50', fg='#ecf0f1', selectcolor='#34495e').pack(anchor='w')

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
        
        # Process with agent
        try:
            response = self.agent.handle_text(command)
            self.add_to_conversation("ULTRON", response)
        except Exception as e:
            self.add_to_conversation("SYSTEM", f"Error processing command: {str(e)}")

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
                print(f"Voice recognition error: {e}")
            
            time.sleep(0.5)

    def process_voice_command(self, command):
        """Process voice command"""
        self.add_to_conversation("USER", f"🎤 {command}")
        
        try:
            response = self.agent.handle_text(command)
            self.add_to_conversation("ULTRON", response)
        except Exception as e:
            self.add_to_conversation("SYSTEM", f"Error processing voice command: {str(e)}")

    def update_system_status(self):
        """Update system status display"""
        try:
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage('C:').percent if os.name == 'nt' else psutil.disk_usage('/').percent
            
            self.status_vars['cpu'].set(f"CPU: {cpu:.1f}%")
            self.status_vars['memory'].set(f"Memory: {memory:.1f}%")
            self.status_vars['disk'].set(f"Disk: {disk:.1f}%")
            self.status_vars['voice'].set(f"Voice: {'Listening' if self.listening else 'Ready'}")
            self.status_vars['ai'].set(f"AI: {'Online' if hasattr(self.agent, 'brain') else 'Offline'}")
            
        except Exception as e:
            print(f"Status update error: {e}")

    def take_screenshot(self):
        """Take screenshot"""
        try:
            screenshot = ImageGrab.grab()
            timestamp = int(time.time())
            screenshot_path = Path(f"screenshot_{timestamp}.png")
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
                os.startfile(os.getcwd())
            else:
                import subprocess
                subprocess.Popen(['xdg-open', os.getcwd()])
            self.add_to_conversation("SYSTEM", f"File manager opened: {os.getcwd()}")
        except Exception as e:
            self.add_to_conversation("SYSTEM", f"Failed to open file manager: {str(e)}")

    def show_tools_explorer(self):
        """Show tools explorer popup"""
        popup = tk.Toplevel(self.root)
        popup.title("Tools Explorer")
        popup.geometry("600x400")
        popup.configure(bg='#2c3e50')
        
        # Tools list
        tools_frame = tk.Frame(popup, bg='#2c3e50')
        tools_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(tools_frame, text="Available Tools:", font=("Orbitron", 14, "bold"),
                fg='#00ff41', bg='#2c3e50').pack(anchor='w')
        
        tools_listbox = tk.Listbox(tools_frame, bg='#34495e', fg='#ecf0f1', font=("Courier", 10))
        tools_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Populate tools
        for tool in self.agent.tools:
            tools_listbox.insert(tk.END, f"{tool.name} - {tool.description}")
        
        tk.Button(popup, text="Close", command=popup.destroy,
                 bg='#e74c3c', fg='white', font=("Courier", 10, "bold")).pack(pady=5)

    def update_voice_engine(self, event=None):
        """Update voice engine"""
        new_engine = self.voice_engine_var.get()
        self.agent.config.data["voice_engine"] = new_engine
        self.agent.config.data["tts_engine"] = new_engine
        self.add_to_conversation("SYSTEM", f"Voice engine set to {new_engine}")

    def update_llm_model(self, event=None):
        """Update LLM model"""
        new_model = self.llm_model_var.get()
        self.agent.config.data["llm_model"] = new_model
        self.add_to_conversation("SYSTEM", f"LLM model set to {new_model}")

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
