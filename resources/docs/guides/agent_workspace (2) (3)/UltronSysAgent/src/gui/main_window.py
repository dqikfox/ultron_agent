"""
Main GUI Window for UltronSysAgent
Ultron-themed interface with real-time chat, controls, and system monitoring
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any
import json

from ..core.event_bus import EventBus, EventTypes

class UltronTheme:
    """Ultron-inspired color theme and styling"""
    
    # Ultron color palette
    PRIMARY_RED = "#DC143C"  # Crimson red
    DARK_GRAY = "#1a1a1a"   # Almost black
    MEDIUM_GRAY = "#2d2d2d" # Dark gray
    LIGHT_GRAY = "#404040"  # Medium gray
    ACCENT_BLUE = "#00CED1"  # Dark turquoise
    TEXT_WHITE = "#FFFFFF"
    TEXT_GRAY = "#CCCCCC"
    WARNING_ORANGE = "#FF8C00"
    SUCCESS_GREEN = "#32CD32"
    
    @classmethod
    def configure_style(cls, root):
        """Configure ttk styles with Ultron theme"""
        style = ttk.Style()
        
        # Configure main theme
        style.theme_use('clam')
        
        # Configure colors
        style.configure('TFrame', background=cls.DARK_GRAY)
        style.configure('TLabel', background=cls.DARK_GRAY, foreground=cls.TEXT_WHITE)
        style.configure('TButton', 
                       background=cls.MEDIUM_GRAY, 
                       foreground=cls.TEXT_WHITE,
                       focuscolor='none')
        style.map('TButton',
                 background=[('active', cls.PRIMARY_RED),
                           ('pressed', cls.ACCENT_BLUE)])
        
        style.configure('TEntry', 
                       background=cls.MEDIUM_GRAY,
                       foreground=cls.TEXT_WHITE,
                       fieldbackground=cls.MEDIUM_GRAY)
        
        style.configure('TScrollbar',
                       background=cls.MEDIUM_GRAY,
                       troughcolor=cls.DARK_GRAY)

class MainWindow:
    """Main GUI window for UltronSysAgent"""
    
    def __init__(self, config, event_bus: EventBus):
        self.config = config
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)
        
        # GUI state
        self.root = None
        self.is_muted = False
        self.admin_mode = config.is_admin_mode()
        
        # Chat history
        self.chat_history = []
        
        # Initialize GUI components
        self.chat_display = None
        self.input_field = None
        self.status_label = None
        self.mute_button = None
        self.admin_button = None
        
        # Setup event handlers
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """Setup event bus handlers"""
        self.event_bus.subscribe(EventTypes.AI_RESPONSE, self._handle_ai_response)
        self.event_bus.subscribe(EventTypes.SPEECH_RECOGNIZED, self._handle_speech_recognized)
        self.event_bus.subscribe(EventTypes.TTS_START, self._handle_tts_start)
        self.event_bus.subscribe(EventTypes.TTS_COMPLETE, self._handle_tts_complete)
        self.event_bus.subscribe(EventTypes.SYSTEM_RESPONSE, self._handle_system_response)
        self.event_bus.subscribe(EventTypes.AI_THINKING, self._handle_ai_thinking)
    
    def start(self):
        """Start the GUI in the main thread"""
        self.logger.info("🖥️ Starting UltronSysAgent GUI...")
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("UltronSysAgent - AI Assistant")
        self.root.geometry("1200x800")
        self.root.configure(bg=UltronTheme.DARK_GRAY)
        
        # Set window icon (if available)
        try:
            self.root.iconbitmap(default='assets/ultron_icon.ico')
        except:
            pass  # Icon file not found
        
        # Configure Ultron theme
        UltronTheme.configure_style(self.root)
        
        # Create GUI layout
        self._create_layout()
        
        # Start async event loop in separate thread
        self.event_thread = threading.Thread(target=self._async_event_loop, daemon=True)
        self.event_thread.start()
        
        # Start GUI main loop
        self.root.mainloop()
    
    def _create_layout(self):
        """Create the main GUI layout"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self._create_header(main_frame)
        
        # Chat area
        self._create_chat_area(main_frame)
        
        # Input area
        self._create_input_area(main_frame)
        
        # Status bar
        self._create_status_bar(main_frame)
        
        # Side panel
        self._create_side_panel(main_frame)
    
    def _create_header(self, parent):
        """Create the header with title and controls"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = ttk.Label(header_frame, 
                               text="🤖 UltronSysAgent", 
                               font=("Arial", 20, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Control buttons
        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(side=tk.RIGHT)
        
        # Mute button
        self.mute_button = ttk.Button(controls_frame, 
                                     text="🔊 Unmuted", 
                                     command=self._toggle_mute)
        self.mute_button.pack(side=tk.LEFT, padx=5)
        
        # Admin mode button
        admin_text = "🔓 Admin" if self.admin_mode else "🔒 User"
        self.admin_button = ttk.Button(controls_frame, 
                                      text=admin_text, 
                                      command=self._toggle_admin_mode)
        self.admin_button.pack(side=tk.LEFT, padx=5)
        
        # Settings button
        settings_button = ttk.Button(controls_frame, 
                                   text="⚙️ Settings", 
                                   command=self._open_settings)
        settings_button.pack(side=tk.LEFT, padx=5)
    
    def _create_chat_area(self, parent):
        """Create the main chat display area"""
        chat_frame = ttk.Frame(parent)
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Chat display with custom styling
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            bg=UltronTheme.MEDIUM_GRAY,
            fg=UltronTheme.TEXT_WHITE,
            font=("Consolas", 11),
            wrap=tk.WORD,
            state=tk.DISABLED,
            insertbackground=UltronTheme.PRIMARY_RED
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for different message types
        self.chat_display.tag_configure("user", foreground=UltronTheme.ACCENT_BLUE)
        self.chat_display.tag_configure("assistant", foreground=UltronTheme.TEXT_WHITE)
        self.chat_display.tag_configure("system", foreground=UltronTheme.WARNING_ORANGE)
        self.chat_display.tag_configure("timestamp", foreground=UltronTheme.TEXT_GRAY, font=("Consolas", 9))
        self.chat_display.tag_configure("thinking", foreground=UltronTheme.PRIMARY_RED, font=("Consolas", 10, "italic"))
        
        # Add welcome message
        self._add_system_message("🤖 UltronSysAgent initialized. Ready for commands.")
        
        # File drop area
        self._setup_file_drop()
    
    def _create_input_area(self, parent):
        """Create the text input area"""
        input_frame = ttk.Frame(parent)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Input field
        self.input_field = tk.Text(
            input_frame,
            bg=UltronTheme.MEDIUM_GRAY,
            fg=UltronTheme.TEXT_WHITE,
            font=("Arial", 12),
            height=3,
            wrap=tk.WORD,
            insertbackground=UltronTheme.PRIMARY_RED
        )
        self.input_field.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Bind Enter key
        self.input_field.bind("<Control-Return>", self._send_message)
        self.input_field.bind("<Shift-Return>", lambda e: "break")  # Allow Shift+Enter for new line
        
        # Send button
        send_button = ttk.Button(input_frame, 
                               text="Send\n(Ctrl+Enter)", 
                               command=self._send_message)
        send_button.pack(side=tk.RIGHT)
        
        # File upload button
        file_button = ttk.Button(input_frame, 
                               text="📁\nFile", 
                               command=self._upload_file)
        file_button.pack(side=tk.RIGHT, padx=(0, 5))
    
    def _create_status_bar(self, parent):
        """Create the status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.status_label = ttk.Label(status_frame, 
                                     text="Status: Ready", 
                                     font=("Arial", 10))
        self.status_label.pack(side=tk.LEFT)
        
        # System info
        self.system_info_label = ttk.Label(status_frame, 
                                          text="", 
                                          font=("Arial", 9))
        self.system_info_label.pack(side=tk.RIGHT)
        
        # Start status update timer
        self._update_system_info()
    
    def _create_side_panel(self, parent):
        """Create the side panel with logs and controls"""
        # This would create a collapsible side panel for advanced features
        # For now, we'll implement this as a future enhancement
        pass
    
    def _setup_file_drop(self):
        """Setup drag and drop file functionality"""
        try:
            from tkinterdnd2 import DND_FILES, TkinterDnD
            
            # Enable drag and drop
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self._handle_file_drop)
            
        except ImportError:
            self.logger.warning("Drag and drop functionality not available")
    
    def _handle_file_drop(self, event):
        """Handle dropped files"""
        try:
            files = self.root.tk.splitlist(event.data)
            for file_path in files:
                self._process_dropped_file(file_path)
        except Exception as e:
            self.logger.error(f"Error handling file drop: {e}")
    
    def _process_dropped_file(self, file_path: str):
        """Process a dropped file"""
        try:
            # Add file to chat
            self._add_user_message(f"📁 Uploaded file: {file_path}")
            
            # Publish file drop event
            asyncio.run_coroutine_threadsafe(
                self.event_bus.publish(EventTypes.FILE_DROPPED, 
                                     {"file_path": file_path}, 
                                     source="gui"),
                self.get_event_loop()
            )
            
        except Exception as e:
            self.logger.error(f"Error processing dropped file: {e}")
    
    def _send_message(self, event=None):
        """Send user message"""
        try:
            message = self.input_field.get("1.0", tk.END).strip()
            if not message:
                return
            
            # Clear input field
            self.input_field.delete("1.0", tk.END)
            
            # Add to chat display
            self._add_user_message(message)
            
            # Publish GUI command event
            asyncio.run_coroutine_threadsafe(
                self.event_bus.publish(EventTypes.GUI_COMMAND, 
                                     {"text": message}, 
                                     source="gui"),
                self.get_event_loop()
            )
            
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
    
    def _toggle_mute(self):
        """Toggle mute state"""
        try:
            self.is_muted = not self.is_muted
            
            # Update button text
            text = "🔇 Muted" if self.is_muted else "🔊 Unmuted"
            self.mute_button.configure(text=text)
            
            # Publish mute toggle event
            asyncio.run_coroutine_threadsafe(
                self.event_bus.publish(EventTypes.MUTE_TOGGLE, 
                                     {"muted": self.is_muted}, 
                                     source="gui"),
                self.get_event_loop()
            )
            
        except Exception as e:
            self.logger.error(f"Error toggling mute: {e}")
    
    def _toggle_admin_mode(self):
        """Toggle admin mode"""
        try:
            if not self.admin_mode:
                # Request admin mode activation
                result = messagebox.askyesno(
                    "Admin Mode",
                    "Enable Admin Mode? This will allow system-level operations.",
                    icon="warning"
                )
                if result:
                    self.admin_mode = True
                    self.config.set('system.admin_mode', True)
            else:
                # Disable admin mode
                self.admin_mode = False
                self.config.set('system.admin_mode', False)
            
            # Update button
            admin_text = "🔓 Admin" if self.admin_mode else "🔒 User"
            self.admin_button.configure(text=admin_text)
            
            # Add system message
            mode = "enabled" if self.admin_mode else "disabled"
            self._add_system_message(f"Admin mode {mode}")
            
        except Exception as e:
            self.logger.error(f"Error toggling admin mode: {e}")
    
    def _open_settings(self):
        """Open settings dialog"""
        try:
            SettingsDialog(self.root, self.config)
        except Exception as e:
            self.logger.error(f"Error opening settings: {e}")
    
    def _upload_file(self):
        """Upload file dialog"""
        try:
            file_path = filedialog.askopenfilename(
                title="Select file to upload",
                filetypes=[
                    ("All files", "*.*"),
                    ("Text files", "*.txt"),
                    ("Documents", "*.pdf;*.docx;*.doc"),
                    ("Images", "*.jpg;*.jpeg;*.png;*.gif"),
                    ("Audio", "*.mp3;*.wav;*.m4a"),
                    ("Video", "*.mp4;*.avi;*.mkv")
                ]
            )
            
            if file_path:
                self._process_dropped_file(file_path)
                
        except Exception as e:
            self.logger.error(f"Error uploading file: {e}")
    
    def _add_user_message(self, message: str):
        """Add user message to chat display"""
        self._add_message("You", message, "user")
    
    def _add_assistant_message(self, message: str):
        """Add assistant message to chat display"""
        self._add_message("UltronSysAgent", message, "assistant")
    
    def _add_system_message(self, message: str):
        """Add system message to chat display"""
        self._add_message("SYSTEM", message, "system")
    
    def _add_message(self, sender: str, message: str, tag: str):
        """Add message to chat display"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Enable editing
            self.chat_display.configure(state=tk.NORMAL)
            
            # Add timestamp
            self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
            
            # Add sender
            self.chat_display.insert(tk.END, f"{sender}: ", tag)
            
            # Add message
            self.chat_display.insert(tk.END, f"{message}\n\n")
            
            # Disable editing
            self.chat_display.configure(state=tk.DISABLED)
            
            # Auto-scroll to bottom
            self.chat_display.see(tk.END)
            
            # Store in history
            self.chat_history.append({
                "timestamp": timestamp,
                "sender": sender,
                "message": message,
                "tag": tag
            })
            
        except Exception as e:
            self.logger.error(f"Error adding message to chat: {e}")
    
    def _update_status(self, status: str):
        """Update status bar"""
        try:
            if self.status_label:
                self.status_label.configure(text=f"Status: {status}")
        except Exception as e:
            self.logger.error(f"Error updating status: {e}")
    
    def _update_system_info(self):
        """Update system information display"""
        try:
            import psutil
            
            # Get system info
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            
            info_text = f"CPU: {cpu_percent:.1f}% | RAM: {memory.percent:.1f}%"
            
            if self.system_info_label:
                self.system_info_label.configure(text=info_text)
            
            # Schedule next update
            self.root.after(5000, self._update_system_info)  # Update every 5 seconds
            
        except Exception as e:
            self.logger.debug(f"Error updating system info: {e}")
    
    def _async_event_loop(self):
        """Run async event loop in separate thread"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.event_loop = loop
            loop.run_forever()
        except Exception as e:
            self.logger.error(f"Error in async event loop: {e}")
    
    def get_event_loop(self):
        """Get the event loop for this GUI"""
        return getattr(self, 'event_loop', None)
    
    # Event handlers
    async def _handle_ai_response(self, event):
        """Handle AI response events"""
        try:
            response = event.data.get('response', '')
            if response:
                self.root.after(0, lambda: self._add_assistant_message(response))
                self.root.after(0, lambda: self._update_status("Ready"))
        except Exception as e:
            self.logger.error(f"Error handling AI response: {e}")
    
    async def _handle_speech_recognized(self, event):
        """Handle speech recognition events"""
        try:
            text = event.data.get('text', '')
            if text:
                self.root.after(0, lambda: self._add_user_message(f"🎤 {text}"))
        except Exception as e:
            self.logger.error(f"Error handling speech recognition: {e}")
    
    async def _handle_tts_start(self, event):
        """Handle TTS start events"""
        try:
            self.root.after(0, lambda: self._update_status("Speaking..."))
        except Exception as e:
            self.logger.error(f"Error handling TTS start: {e}")
    
    async def _handle_tts_complete(self, event):
        """Handle TTS complete events"""
        try:
            self.root.after(0, lambda: self._update_status("Ready"))
        except Exception as e:
            self.logger.error(f"Error handling TTS complete: {e}")
    
    async def _handle_system_response(self, event):
        """Handle system response events"""
        try:
            output = event.data.get('output', '')
            error = event.data.get('error', '')
            success = event.data.get('success', False)
            
            if output:
                self.root.after(0, lambda: self._add_system_message(f"✅ {output}"))
            elif error:
                self.root.after(0, lambda: self._add_system_message(f"❌ {error}"))
                
        except Exception as e:
            self.logger.error(f"Error handling system response: {e}")
    
    async def _handle_ai_thinking(self, event):
        """Handle AI thinking events"""
        try:
            self.root.after(0, lambda: self._update_status("Thinking..."))
            
            # Add thinking indicator to chat
            self.chat_display.configure(state=tk.NORMAL)
            self.chat_display.insert(tk.END, "🤔 Thinking...\n", "thinking")
            self.chat_display.configure(state=tk.DISABLED)
            self.chat_display.see(tk.END)
            
        except Exception as e:
            self.logger.error(f"Error handling AI thinking: {e}")

class SettingsDialog:
    """Settings dialog for UltronSysAgent"""
    
    def __init__(self, parent, config):
        self.config = config
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("UltronSysAgent Settings")
        self.dialog.geometry("600x500")
        self.dialog.configure(bg=UltronTheme.DARK_GRAY)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Configure theme
        UltronTheme.configure_style(self.dialog)
        
        # Create settings interface
        self._create_settings_interface()
    
    def _create_settings_interface(self):
        """Create the settings interface"""
        # Notebook for tabbed interface
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Voice settings tab
        voice_frame = ttk.Frame(notebook)
        notebook.add(voice_frame, text="Voice")
        self._create_voice_settings(voice_frame)
        
        # AI settings tab
        ai_frame = ttk.Frame(notebook)
        notebook.add(ai_frame, text="AI Models")
        self._create_ai_settings(ai_frame)
        
        # Security settings tab
        security_frame = ttk.Frame(notebook)
        notebook.add(security_frame, text="Security")
        self._create_security_settings(security_frame)
        
        # System settings tab
        system_frame = ttk.Frame(notebook)
        notebook.add(system_frame, text="System")
        self._create_system_settings(system_frame)
        
        # Buttons
        self._create_buttons()
    
    def _create_voice_settings(self, parent):
        """Create voice settings"""
        # Always listening
        always_listening_var = tk.BooleanVar(value=self.config.get('voice.always_listening', True))
        ttk.Checkbutton(parent, text="Always listening", variable=always_listening_var).pack(anchor=tk.W, pady=5)
        
        # STT provider
        ttk.Label(parent, text="Speech-to-Text Provider:").pack(anchor=tk.W, pady=(10, 5))
        stt_var = tk.StringVar(value=self.config.get('voice.stt_provider', 'whisper'))
        ttk.Combobox(parent, textvariable=stt_var, values=['whisper', 'deepseek']).pack(anchor=tk.W, pady=5)
        
        # TTS provider
        ttk.Label(parent, text="Text-to-Speech Provider:").pack(anchor=tk.W, pady=(10, 5))
        tts_var = tk.StringVar(value=self.config.get('voice.tts_provider', 'pyttsx3'))
        ttk.Combobox(parent, textvariable=tts_var, values=['pyttsx3', 'elevenlabs']).pack(anchor=tk.W, pady=5)
    
    def _create_ai_settings(self, parent):
        """Create AI model settings"""
        # Primary model
        ttk.Label(parent, text="Primary AI Model:").pack(anchor=tk.W, pady=(10, 5))
        model_var = tk.StringVar(value=self.config.get('ai.primary_model', 'gpt-4'))
        ttk.Combobox(parent, textvariable=model_var, values=['gpt-4', 'deepseek', 'phi-3']).pack(anchor=tk.W, pady=5)
        
        # Temperature
        ttk.Label(parent, text="Temperature:").pack(anchor=tk.W, pady=(10, 5))
        temp_var = tk.DoubleVar(value=self.config.get('ai.temperature', 0.7))
        ttk.Scale(parent, from_=0.0, to=2.0, variable=temp_var, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
    
    def _create_security_settings(self, parent):
        """Create security settings"""
        # Admin confirmation
        admin_confirm_var = tk.BooleanVar(value=self.config.get('security.require_admin_confirmation', True))
        ttk.Checkbutton(parent, text="Require admin confirmation for dangerous commands", 
                       variable=admin_confirm_var).pack(anchor=tk.W, pady=5)
        
        # Command logging
        log_commands_var = tk.BooleanVar(value=self.config.get('security.log_all_commands', True))
        ttk.Checkbutton(parent, text="Log all commands", variable=log_commands_var).pack(anchor=tk.W, pady=5)
        
        # Offline mode
        offline_var = tk.BooleanVar(value=self.config.get('api.offline_mode', False))
        ttk.Checkbutton(parent, text="Offline mode (no external API calls)", 
                       variable=offline_var).pack(anchor=tk.W, pady=5)
    
    def _create_system_settings(self, parent):
        """Create system settings"""
        # Auto-start
        autostart_var = tk.BooleanVar(value=self.config.get('system.auto_start', True))
        ttk.Checkbutton(parent, text="Start with Windows", variable=autostart_var).pack(anchor=tk.W, pady=5)
        
        # GPU acceleration
        gpu_var = tk.BooleanVar(value=self.config.get('hardware.gpu_acceleration', True))
        ttk.Checkbutton(parent, text="GPU acceleration (CUDA)", variable=gpu_var).pack(anchor=tk.W, pady=5)
    
    def _create_buttons(self):
        """Create dialog buttons"""
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Save", command=self._save_settings).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT)
    
    def _save_settings(self):
        """Save settings and close dialog"""
        try:
            self.config.save()
            messagebox.showinfo("Settings", "Settings saved successfully!")
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
