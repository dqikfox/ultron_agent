"""
Enhanced Accessible GUI for ULTRON Agent 2 - Pokédx Integration
Incorporates high-contrast design, large fonts, and voice integration
Based on advanced accessibility patterns for disabled users
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import threading
import queue
import time
from typing import Optional, Callable, Dict, Any
import logging

logger = logging.getLogger(__name__)

class UltronAccessibleGUI:
    """High-contrast, voice-controlled GUI optimized for disabled users"""
    
    # Accessibility color schemes
    HIGH_CONTRAST_DARK = {
        'bg': '#000000',           # Pure black background
        'fg': '#00FF00',           # Bright green text
        'accent': '#FFFF00',       # Yellow accents
        'error': '#FF0000',        # Red for errors
        'success': '#00FFFF'       # Cyan for success
    }
    
    HIGH_CONTRAST_LIGHT = {
        'bg': '#FFFFFF',           # Pure white background
        'fg': '#000000',           # Black text
        'accent': '#0000FF',       # Blue accents
        'error': '#FF0000',        # Red for errors
        'success': '#008000'       # Green for success
    }
    
    def __init__(self, root, voice_manager=None, agent_core=None):
        """Initialize accessible GUI with voice integration"""
        self.root = root
        self.voice_manager = voice_manager
        self.agent_core = agent_core
        
        # Accessibility settings
        self.contrast_mode = 'dark'  # 'dark' or 'light'
        self.font_size = 20  # Large fonts for visual impairments
        self.colors = self.HIGH_CONTRAST_DARK
        
        # Communication queue for thread safety
        self.message_queue = queue.Queue()
        
        # Setup GUI
        self._setup_window()
        self._create_widgets()
        self._setup_voice_integration()
        
        # Start message processing
        self.root.after(100, self._process_message_queue)
        
        logger.info("ULTRON Accessible GUI initialized")
    
    def _setup_window(self):
        """Configure main window for accessibility"""
        self.root.title("🔴 ULTRON SOLUTIONS - Voice Assistant")
        self.root.geometry("900x700")
        self.root.configure(bg=self.colors['bg'])
        
        # Make window always on top for visibility
        self.root.attributes('-topmost', True)
        
        # Configure for high DPI displays
        try:
            self.root.tk.call('tk', 'scaling', 2.0)
        except:
            pass  # Ignore if not supported
    
    def _create_widgets(self):
        """Create accessible GUI widgets"""
        
        # Title with ULTRON SOLUTIONS branding
        title_frame = tk.Frame(self.root, bg=self.colors['bg'])
        title_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.title_label = tk.Label(
            title_frame,
            text="🔴 ULTRON SOLUTIONS 🔴",
            font=("Helvetica", 28, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['accent']
        )
        self.title_label.pack()
        
        # Status indicator
        self.status_label = tk.Label(
            title_frame,
            text="🎤 Say 'ultron' to activate voice control",
            font=("Helvetica", 14),
            bg=self.colors['bg'],
            fg=self.colors['fg']
        )
        self.status_label.pack(pady=2)
        
        # Main conversation area with high contrast
        self.conversation_area = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            font=("Helvetica", self.font_size),
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            insertbackground=self.colors['fg'],
            selectbackground=self.colors['accent'],
            selectforeground=self.colors['bg'],
            state=tk.DISABLED,
            spacing1=3,  # Line spacing for readability
            spacing2=2,
            spacing3=3
        )
        self.conversation_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control buttons with large, accessible design
        button_frame = tk.Frame(self.root, bg=self.colors['bg'])
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Emergency stop button (highly visible)
        self.stop_button = tk.Button(
            button_frame,
            text="🚨 EMERGENCY STOP",
            font=("Helvetica", 16, "bold"),
            bg=self.colors['error'],
            fg='white',
            activebackground='#CC0000',
            activeforeground='white',
            relief=tk.RAISED,
            bd=3,
            command=self._emergency_stop
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Voice toggle button
        self.voice_button = tk.Button(
            button_frame,
            text="🎤 START VOICE",
            font=("Helvetica", 16),
            bg=self.colors['success'],
            fg='white',
            activebackground='#006600',
            activeforeground='white',
            relief=tk.RAISED,
            bd=3,
            command=self._toggle_voice
        )
        self.voice_button.pack(side=tk.LEFT, padx=5)
        
        # Accessibility options
        self.contrast_button = tk.Button(
            button_frame,
            text="🌓 CONTRAST",
            font=("Helvetica", 16),
            bg=self.colors['accent'],
            fg=self.colors['bg'],
            activebackground='#CCCC00',
            activeforeground=self.colors['bg'],
            relief=tk.RAISED,
            bd=3,
            command=self._toggle_contrast
        )
        self.contrast_button.pack(side=tk.RIGHT, padx=5)
        
        # Font size controls
        font_frame = tk.Frame(button_frame, bg=self.colors['bg'])
        font_frame.pack(side=tk.RIGHT, padx=10)
        
        tk.Button(
            font_frame,
            text="🔍+",
            font=("Helvetica", 14),
            bg=self.colors['fg'],
            fg=self.colors['bg'],
            command=lambda: self._adjust_font_size(2)
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            font_frame,
            text="🔍-",
            font=("Helvetica", 14),
            bg=self.colors['fg'],
            fg=self.colors['bg'],
            command=lambda: self._adjust_font_size(-2)
        ).pack(side=tk.LEFT, padx=2)
        
        # Initialize with welcome message
        self._add_system_message("ULTRON SOLUTIONS voice assistant ready")
        self._add_system_message("🎤 Say 'ultron' to activate voice control")
        self._add_system_message("🚨 Use EMERGENCY STOP button if needed")
    
    def _setup_voice_integration(self):
        """Setup integration with voice manager"""
        if self.voice_manager:
            # Setup callbacks for voice events
            def on_voice_wake():
                self.message_queue.put(('system', '🔴 ULTRON activated - Listening...'))
                self.message_queue.put(('status', 'Voice control active'))
            
            def on_voice_command(command):
                self.message_queue.put(('user', command))
                
                # Process command if agent_core is available
                if self.agent_core:
                    threading.Thread(
                        target=self._process_agent_command,
                        args=(command,),
                        daemon=True
                    ).start()
            
            def on_voice_stop():
                self.message_queue.put(('system', '🔴 ULTRON deactivated - Say "ultron" to reactivate'))
                self.message_queue.put(('status', 'Voice control inactive'))
            
            # Set callbacks
            if hasattr(self.voice_manager, 'set_wake_callback'):
                self.voice_manager.set_wake_callback(on_voice_wake)
            if hasattr(self.voice_manager, 'set_command_callback'):
                self.voice_manager.set_command_callback(on_voice_command)
            if hasattr(self.voice_manager, 'set_stop_callback'):
                self.voice_manager.set_stop_callback(on_voice_stop)
    
    def _process_agent_command(self, command):
        """Process command through agent_core"""
        try:
            if hasattr(self.agent_core, 'process_command'):
                response = self.agent_core.process_command(command)
                self.message_queue.put(('assistant', response))
            else:
                # Fallback response
                response = f"ULTRON received: {command}"
                self.message_queue.put(('assistant', response))
                
        except Exception as e:
            error_msg = f"Error processing command: {str(e)}"
            self.message_queue.put(('error', error_msg))
    
    def _process_message_queue(self):
        """Process messages from voice system (thread-safe)"""
        try:
            while True:
                msg_type, content = self.message_queue.get_nowait()
                
                if msg_type == 'system':
                    self._add_system_message(content)
                elif msg_type == 'user':
                    self._add_user_message(content)
                elif msg_type == 'assistant':
                    self._add_assistant_message(content)
                elif msg_type == 'error':
                    self._add_error_message(content)
                elif msg_type == 'status':
                    self._update_status(content)
                    
        except queue.Empty:
            pass
        
        # Continue processing
        self.root.after(100, self._process_message_queue)
    
    def _add_message(self, speaker, message, color):
        """Add message to conversation area"""
        self.conversation_area.configure(state=tk.NORMAL)
        
        # Add timestamp
        timestamp = time.strftime("%H:%M:%S")
        
        # Insert message with color coding
        self.conversation_area.insert(tk.END, f"[{timestamp}] {speaker}: ", 'speaker')
        self.conversation_area.insert(tk.END, f"{message}\n", 'message')
        
        # Configure tags for coloring
        self.conversation_area.tag_config('speaker', foreground=self.colors['accent'])
        self.conversation_area.tag_config('message', foreground=color)
        
        # Auto-scroll to bottom
        self.conversation_area.see(tk.END)
        self.conversation_area.configure(state=tk.DISABLED)
    
    def _add_system_message(self, message):
        """Add system message"""
        self._add_message("SYSTEM", message, self.colors['success'])
    
    def _add_user_message(self, message):
        """Add user message"""
        self._add_message("YOU", message, self.colors['fg'])
    
    def _add_assistant_message(self, message):
        """Add assistant response"""
        self._add_message("ULTRON", message, self.colors['accent'])
    
    def _add_error_message(self, message):
        """Add error message"""
        self._add_message("ERROR", message, self.colors['error'])
    
    def _update_status(self, status):
        """Update status label"""
        self.status_label.config(text=f"🎤 {status}")
    
    def _emergency_stop(self):
        """Emergency stop all operations"""
        logger.warning("Emergency stop activated")
        
        # Stop voice manager
        if self.voice_manager and hasattr(self.voice_manager, 'emergency_stop'):
            self.voice_manager.emergency_stop()
        
        # Add emergency message
        self._add_system_message("🚨 EMERGENCY STOP ACTIVATED - All systems halted")
        
        # Show confirmation dialog
        messagebox.showwarning(
            "Emergency Stop",
            "ULTRON systems have been halted.\nClick START VOICE to reactivate."
        )
    
    def _toggle_voice(self):
        """Toggle voice recognition on/off"""
        if self.voice_manager:
            if hasattr(self.voice_manager, 'is_listening') and self.voice_manager.is_listening():
                # Stop voice
                self.voice_manager.stop_listening()
                self.voice_button.config(text="🎤 START VOICE", bg=self.colors['success'])
                self._add_system_message("Voice control stopped")
            else:
                # Start voice
                self.voice_manager.start_listening()
                self.voice_button.config(text="🔇 STOP VOICE", bg=self.colors['error'])
                self._add_system_message("Voice control started")
    
    def _toggle_contrast(self):
        """Toggle between dark and light contrast modes"""
        if self.contrast_mode == 'dark':
            self.contrast_mode = 'light'
            self.colors = self.HIGH_CONTRAST_LIGHT
        else:
            self.contrast_mode = 'dark'
            self.colors = self.HIGH_CONTRAST_DARK
        
        # Update all widget colors
        self._update_colors()
        self._add_system_message(f"Switched to {self.contrast_mode} contrast mode")
    
    def _adjust_font_size(self, delta):
        """Adjust font size for accessibility"""
        self.font_size = max(12, min(36, self.font_size + delta))
        
        # Update conversation area font
        self.conversation_area.configure(font=("Helvetica", self.font_size))
        
        self._add_system_message(f"Font size adjusted to {self.font_size}pt")
    
    def _update_colors(self):
        """Update all widget colors after contrast change"""
        # Update main window
        self.root.configure(bg=self.colors['bg'])
        
        # Update all widgets
        widgets_to_update = [
            (self.title_label, {'bg': self.colors['bg'], 'fg': self.colors['accent']}),
            (self.status_label, {'bg': self.colors['bg'], 'fg': self.colors['fg']}),
            (self.conversation_area, {'bg': self.colors['bg'], 'fg': self.colors['fg']})
        ]
        
        for widget, config in widgets_to_update:
            try:
                widget.configure(**config)
            except Exception as e:
                logger.error(f"Error updating widget colors: {e}")


# Integration function for ULTRON Agent 2
def create_ultron_accessible_gui(agent_core=None, voice_manager=None):
    """Create ULTRON accessible GUI with voice integration"""
    
    root = tk.Tk()
    
    # Create GUI
    gui = UltronAccessibleGUI(root, voice_manager, agent_core)
    
    # Setup window closing behavior
    def on_closing():
        if voice_manager:
            voice_manager.stop_listening()
        root.quit()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    return root, gui


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create accessible GUI
    root, gui = create_ultron_accessible_gui()
    
    try:
        # Start GUI
        root.mainloop()
    except KeyboardInterrupt:
        print("Shutting down ULTRON GUI...")
