"""ULTRON GUI Interface"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import asyncio
import logging
from datetime import datetime

class UltronGUI:
    def __init__(self, ultron_core):
        self.ultron = ultron_core
        self.root = tk.Tk()
        self.root.title("ULTRON AI Assistant")
        self.root.geometry("1000x700")
        self.root.configure(bg='#0a0a0a')
        
        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('Dark.TFrame', background='#0a0a0a')
        self.style.configure('Dark.TLabel', background='#0a0a0a', foreground='#00ff00')
        self.style.configure('Dark.TButton', background='#1a1a1a', foreground='#00ff00')
        
        self.setup_gui()
        
        # Update system info periodically
        self.update_system_info()
        
    def setup_gui(self):
        """Setup GUI components"""
        # Title
        title_frame = tk.Frame(self.root, bg='#0a0a0a')
        title_frame.pack(fill=tk.X, pady=10)
        
        title_label = tk.Label(title_frame, 
                              text="🔴 ULTRON AI ASSISTANT 🔴", 
                              font=("Arial", 20, "bold"), 
                              fg="#ff0000", 
                              bg="#0a0a0a")
        title_label.pack()
        
        # Status frame
        status_frame = tk.Frame(self.root, bg='#0a0a0a')
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_label = tk.Label(status_frame, 
                                   text="Status: Ready", 
                                   font=("Arial", 12),
                                   fg="#00ff00", 
                                   bg="#0a0a0a")
        self.status_label.pack(side=tk.LEFT)
        
        self.listening_indicator = tk.Label(status_frame,
                                          text="●",
                                          font=("Arial", 16),
                                          fg="#ff0000",
                                          bg="#0a0a0a")
        self.listening_indicator.pack(side=tk.RIGHT)
        
        # Command input frame
        cmd_frame = tk.Frame(self.root, bg='#0a0a0a')
        cmd_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(cmd_frame, 
                text="Command:", 
                font=("Arial", 12),
                fg="#00ff00", 
                bg="#0a0a0a").pack(side=tk.LEFT)
        
        self.cmd_entry = tk.Entry(cmd_frame, 
                                width=60, 
                                font=("Arial", 12),
                                bg="#1a1a1a", 
                                fg="#00ff00",
                                insertbackground="#00ff00")
        self.cmd_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.cmd_entry.bind("<Return>", self.process_text_command)
        
        execute_btn = tk.Button(cmd_frame,
                              text="Execute",
                              font=("Arial", 10),
                              bg="#1a1a1a",
                              fg="#00ff00",
                              command=self.process_text_command)
        execute_btn.pack(side=tk.RIGHT, padx=5)
        
        # Control buttons frame
        btn_frame = tk.Frame(self.root, bg='#0a0a0a')
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Control buttons
        self.voice_btn = tk.Button(btn_frame, 
                                 text="Start Voice", 
                                 font=("Arial", 10),
                                 bg="#1a4a1a", 
                                 fg="#00ff00",
                                 command=self.toggle_voice)
        self.voice_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, 
                 text="Screenshot", 
                 font=("Arial", 10),
                 bg="#1a1a4a", 
                 fg="#00ff00",
                 command=self.take_screenshot).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, 
                 text="System Info", 
                 font=("Arial", 10),
                 bg="#4a1a1a", 
                 fg="#00ff00",
                 command=self.show_system_info).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, 
                 text="Sort Files", 
                 font=("Arial", 10),
                 bg="#4a4a1a", 
                 fg="#00ff00",
                 command=self.sort_files).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, 
                 text="Clear Log", 
                 font=("Arial", 10),
                 bg="#4a1a4a", 
                 fg="#00ff00",
                 command=self.clear_log).pack(side=tk.RIGHT, padx=5)
        
        # Main content area
        content_frame = tk.Frame(self.root, bg='#0a0a0a')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Log area
        log_frame = tk.LabelFrame(content_frame,
                                text="Activity Log",
                                font=("Arial", 12),
                                fg="#00ff00",
                                bg="#0a0a0a")
        log_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.log_area = scrolledtext.ScrolledText(log_frame,
                                                height=25,
                                                font=("Consolas", 10),
                                                bg="#0f0f0f",
                                                fg="#00ff00",
                                                insertbackground="#00ff00",
                                                wrap=tk.WORD)
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # System info panel
        info_frame = tk.LabelFrame(content_frame,
                                 text="System Monitor",
                                 font=("Arial", 12),
                                 fg="#00ff00",
                                 bg="#0a0a0a",
                                 width=250)
        info_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        info_frame.pack_propagate(False)
        
        # System metrics
        self.cpu_var = tk.StringVar(value="CPU: ---%")
        self.mem_var = tk.StringVar(value="Memory: ---%")
        self.disk_var = tk.StringVar(value="Disk: ---%")
        self.admin_var = tk.StringVar(value="Admin: ---")
        
        for i, var in enumerate([self.cpu_var, self.mem_var, self.disk_var, self.admin_var]):
            label = tk.Label(info_frame,
                           textvariable=var,
                           font=("Arial", 11),
                           fg="#00ffff",
                           bg="#0a0a0a",
                           anchor='w')
            label.pack(fill=tk.X, padx=10, pady=5)
        
        # Component status
        tk.Label(info_frame,
                text="Component Status:",
                font=("Arial", 11, "bold"),
                fg="#ffff00",
                bg="#0a0a0a").pack(pady=(20, 5))
        
        self.component_labels = {}
        components = ['voice', 'vision', 'ai', 'system', 'files', 'web']
        
        for component in components:
            var = tk.StringVar(value=f"{component.capitalize()}: ---")
            label = tk.Label(info_frame,
                           textvariable=var,
                           font=("Arial", 10),
                           fg="#ffffff",
                           bg="#0a0a0a",
                           anchor='w')
            label.pack(fill=tk.X, padx=10, pady=2)
            self.component_labels[component] = var
        
        # Footer
        footer_frame = tk.Frame(self.root, bg='#0a0a0a')
        footer_frame.pack(fill=tk.X, pady=5)
        
        self.footer_label = tk.Label(footer_frame,
                                   text="ULTRON - Fully Automated AI Assistant",
                                   font=("Arial", 10),
                                   fg="#666666",
                                   bg="#0a0a0a")
        self.footer_label.pack()
        
        # Initial log message
        self.log_message("ULTRON GUI initialized successfully")
        self.log_message("Ready for commands...")
    
    def log_message(self, message, level="INFO"):
        """Add message to log area"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        color_map = {
            "INFO": "#00ff00",
            "ERROR": "#ff0000",
            "WARNING": "#ffff00",
            "SUCCESS": "#00ffff"
        }
        
        self.log_area.insert(tk.END, f"[{timestamp}] {level}: {message}\n")
        self.log_area.see(tk.END)
        
        # Color coding (simplified)
        if level == "ERROR":
            self.status_label.config(text=f"Status: Error - {message[:30]}...", fg="#ff0000")
        elif level == "SUCCESS":
            self.status_label.config(text=f"Status: {message[:40]}...", fg="#00ffff")
        else:
            self.status_label.config(text=f"Status: {message[:40]}...", fg="#00ff00")
    
    def clear_log(self):
        """Clear log area"""
        self.log_area.delete(1.0, tk.END)
        self.log_message("Log cleared")
    
    def toggle_voice(self):
        """Toggle voice listening"""
        if not self.ultron.listening:
            self.ultron.start_listening()
            self.voice_btn.config(text="Stop Voice", bg="#4a1a1a")
            self.listening_indicator.config(fg="#00ff00")
            self.log_message("Voice listening started", "SUCCESS")
        else:
            self.ultron.stop_listening()
            self.voice_btn.config(text="Start Voice", bg="#1a4a1a")
            self.listening_indicator.config(fg="#ff0000")
            self.log_message("Voice listening stopped", "INFO")
    
    def process_text_command(self, event=None):
        """Process text command from entry"""
        command = self.cmd_entry.get().strip()
        if not command:
            return
        
        self.cmd_entry.delete(0, tk.END)
        self.log_message(f"User: {command}")
        
        # Process command in background thread
        def run_command():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    self.ultron.process_command(command, source="gui")
                )
                loop.close()
                
                if result['success']:
                    self.root.after(0, lambda: self.log_message(f"ULTRON: {result['response']}", "SUCCESS"))
                else:
                    self.root.after(0, lambda: self.log_message(f"Error: {result['error']}", "ERROR"))
                    
            except Exception as e:
                self.root.after(0, lambda: self.log_message(f"Command error: {e}", "ERROR"))
        
        threading.Thread(target=run_command, daemon=True).start()
    
    def take_screenshot(self):
        """Take screenshot"""
        self.log_message("Taking screenshot...", "INFO")
        
        def run_screenshot():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(self.ultron.vision.take_screenshot())
                loop.close()
                
                if result['success']:
                    self.root.after(0, lambda: self.log_message(f"Screenshot saved: {result['path']}", "SUCCESS"))
                else:
                    self.root.after(0, lambda: self.log_message(f"Screenshot failed: {result['error']}", "ERROR"))
                    
            except Exception as e:
                self.root.after(0, lambda: self.log_message(f"Screenshot error: {e}", "ERROR"))
        
        threading.Thread(target=run_screenshot, daemon=True).start()
    
    def show_system_info(self):
        """Show detailed system information"""
        def run_system_info():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                info = loop.run_until_complete(self.ultron.system.get_status())
                loop.close()
                
                message = f"CPU: {info.get('cpu', 0):.1f}%, Memory: {info.get('memory', 0):.1f}%, Admin: {info.get('admin', False)}"
                self.root.after(0, lambda: self.log_message(message, "INFO"))
                
            except Exception as e:
                self.root.after(0, lambda: self.log_message(f"System info error: {e}", "ERROR"))
        
        threading.Thread(target=run_system_info, daemon=True).start()
    
    def sort_files(self):
        """Sort files with directory selection"""
        directory = filedialog.askdirectory(title="Select directory to sort")
        if not directory:
            return
        
        self.log_message(f"Sorting files in: {directory}", "INFO")
        
        def run_sort():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(self.ultron.files.auto_sort(directory))
                loop.close()
                
                if 'error' not in result:
                    message = f"Sorted {result.get('total', 0)} files, {result.get('duplicates', 0)} duplicates"
                    self.root.after(0, lambda: self.log_message(message, "SUCCESS"))
                else:
                    self.root.after(0, lambda: self.log_message(f"Sort failed: {result['error']}", "ERROR"))
                    
            except Exception as e:
                self.root.after(0, lambda: self.log_message(f"Sort error: {e}", "ERROR"))
        
        threading.Thread(target=run_sort, daemon=True).start()
    
    def update_system_info(self):
        """Update system information display"""
        def run_update():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                info = loop.run_until_complete(self.ultron.system.get_status())
                loop.close()
                
                # Update system metrics
                self.root.after(0, lambda: self.cpu_var.set(f"CPU: {info.get('cpu', 0):.1f}%"))
                self.root.after(0, lambda: self.mem_var.set(f"Memory: {info.get('memory', 0):.1f}%"))
                self.root.after(0, lambda: self.disk_var.set(f"Disk: {info.get('disk', 0):.1f}%"))
                self.root.after(0, lambda: self.admin_var.set(f"Admin: {info.get('admin', False)}"))
                
                # Update component status
                status = self.ultron.get_status()
                components = status.get('components', {})
                
                for component, var in self.component_labels.items():
                    status_text = "✓" if components.get(component, False) else "✗"
                    self.root.after(0, lambda c=component, v=var, s=status_text: v.set(f"{c.capitalize()}: {s}"))
                
            except Exception as e:
                logging.error(f"GUI update error: {e}")
        
        threading.Thread(target=run_update, daemon=True).start()
        
        # Schedule next update
        self.root.after(5000, self.update_system_info)
    
    def run(self):
        """Run GUI main loop"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except Exception as e:
            logging.error(f"GUI runtime error: {e}")
    
    def on_closing(self):
        """Handle window closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit ULTRON?"):
            self.ultron.running = False
            self.root.destroy()
