"""
ULTRON Agent - Stable Diffusion GUI Interface (Minimal Version)
Advanced interface for image generation and management with headless support
"""

import os
import sys
from pathlib import Path

# Check for GUI availability
GUI_AVAILABLE = True
try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext, messagebox, filedialog
except ImportError:
    GUI_AVAILABLE = False
    print("⚠️  tkinter not available - GUI features disabled")
    # Create minimal mock classes for headless operation
    tk = type('tk', (), {})()
    ttk = type('ttk', (), {})()
    scrolledtext = type('scrolledtext', (), {})()
    messagebox = type('messagebox', (), {
        'showinfo': lambda *a, **k: print(f"INFO: {a[1] if len(a) > 1 else a[0]}"),
        'showerror': lambda *a, **k: print(f"ERROR: {a[1] if len(a) > 1 else a[0]}"),
        'askyesno': lambda *a, **k: True
    })()
    filedialog = type('filedialog', (), {
        'asksaveasfilename': lambda *a, **k: None,
        'askdirectory': lambda *a, **k: None,
        'askopenfilename': lambda *a, **k: None
    })()

import threading
import time
import webbrowser
import requests
import json
import base64
import io
from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime
import logging

# PIL availability check
PIL_AVAILABLE = True
try:
    from PIL import Image, ImageTk
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️  PIL not available - image processing disabled")
    # Mock PIL classes
    class MockImage:
        @staticmethod
        def open(*args): return MockImage()
        def copy(self): return self
        def thumbnail(self, *args): pass
        def save(self, *args): pass
        @property  
        def Resampling(self): return type('Resampling', (), {'LANCZOS': None})()
    
    Image = MockImage()
    ImageTk = type('ImageTk', (), {'PhotoImage': lambda *a: None})()


class StableDiffusionGUI:
    """Advanced Stable Diffusion GUI interface with headless support"""
    
    def __init__(self, agent_ref=None):
        self.agent = agent_ref
        self.root = None
        self.is_running = False
        self.gui_available = GUI_AVAILABLE
        self.pil_available = PIL_AVAILABLE
        
        # Configuration
        self.colab_endpoints = []
        self.local_endpoint = "http://localhost:8000"
        self.current_endpoint = None
        
        # Image storage
        self.images_dir = Path("generated_images")
        self.images_dir.mkdir(exist_ok=True)
        
        # Generation history
        self.generation_history = []
        self.current_images = []
        
        # UI References (only create if GUI available)
        if self.gui_available:
            self.param_vars = {}
            self.prompt_text = None
            self.negative_prompt_text = None
            self.status_label = None
            self.progress_bar = None
        
        logging.info(f"🎨 Stable Diffusion GUI initialized (GUI: {self.gui_available}, PIL: {self.pil_available})")
    
    def create_main_window(self):
        """Create the main window"""
        if not self.gui_available:
            print("⚠️  Cannot create GUI - tkinter not available")
            return
        
        self.root = tk.Tk()
        self.root.title("🎨 ULTRON Stable Diffusion Studio")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a1a')
        
        # Create parameter variables
        self.param_vars = {
            'width': tk.IntVar(value=512),
            'height': tk.IntVar(value=512), 
            'steps': tk.IntVar(value=20),
            'guidance_scale': tk.DoubleVar(value=7.5),
            'num_images': tk.IntVar(value=1)
        }
        
        # Create basic layout
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="🎨 Stable Diffusion Controls")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Basic prompt input
        ttk.Label(control_frame, text="Prompt:").pack(anchor='w', padx=5, pady=2)
        self.prompt_text = scrolledtext.ScrolledText(control_frame, height=3)
        self.prompt_text.pack(fill=tk.X, padx=5, pady=2)
        
        # Generate button
        generate_btn = ttk.Button(control_frame, text="🎨 Generate Images", 
                                 command=self.generate_images)
        generate_btn.pack(pady=5)
        
        # Status
        self.status_label = ttk.Label(control_frame, text="Ready to generate")
        self.status_label.pack(pady=2)
        
        # Results area
        results_frame = ttk.LabelFrame(main_frame, text="📸 Generated Images")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=10)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        logging.info("🎨 Main window created successfully")
    
    def generate_images(self):
        """Generate images (placeholder for now)"""
        if not self.gui_available:
            print("🎨 Generating images (headless mode)")
            return
            
        prompt = self.prompt_text.get('1.0', tk.END).strip() if self.prompt_text else "test prompt"
        
        self.status_label.config(text="🎨 Generating...")
        self.results_text.insert(tk.END, f"🎨 Generating: {prompt}\n")
        
        # Simulate generation
        def simulate_generation():
            time.sleep(2)
            if self.gui_available and self.status_label:
                self.root.after(0, lambda: self.status_label.config(text="✅ Generation complete"))
                self.root.after(0, lambda: self.results_text.insert(tk.END, "✅ Images generated successfully\n"))
        
        threading.Thread(target=simulate_generation, daemon=True).start()
    
    def run_gui(self):
        """Run the GUI with headless fallback"""
        if not self.gui_available:
            print("⚠️  GUI not available in this environment")
            print("💡 To use the GUI, ensure tkinter is installed")
            print("   • pip install pillow (for image support)")
            print("   • tkinter usually comes with Python")
            print("   • On Ubuntu: sudo apt-get install python3-tk")
            return None
            
        if not self.root:
            self.create_main_window()
        
        self.is_running = True
        logging.info("🎨 Starting Stable Diffusion GUI...")
        
        try:
            self.root.mainloop()
        except Exception as e:
            logging.error(f"❌ GUI error: {e}")
        finally:
            self.is_running = False
    
    def on_closing(self):
        """Handle window closing"""
        self.is_running = False
        if self.root:
            self.root.quit()
            self.root.destroy()
        logging.info("🎨 Stable Diffusion GUI closed")


def launch_stable_diffusion_gui(agent_ref=None):
    """Launch the Stable Diffusion GUI"""
    gui = StableDiffusionGUI(agent_ref)
    gui.run_gui()
    return gui


if __name__ == "__main__":
    # Test run
    launch_stable_diffusion_gui()