#!/usr/bin/env python3
"""
ULTRON THEME VISUAL DEMONSTRATION
=================================
A showcase of the stunning Ultron-style theme with cyberpunk visuals

Features demonstrated:
- Cyberpunk color schemes (#ff0040 red, #00d4ff blue, #0a0a0f dark)
- Neural network animations
- Particle systems
- Glowing UI elements
- Professional Ultron aesthetics
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
import math
import random

try:
    from gui_ultron_theme import UltronTheme, create_ultron_frame, create_ultron_button, create_ultron_label
    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False

class UltronThemeDemo:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🤖 ULTRON THEME DEMONSTRATION - Stunning Visuals")
        self.root.geometry("800x600")
        self.root.configure(bg='#0a0a0f')
        
        # Initialize animation variables first
        self.glow_phase = 0
        
        if THEME_AVAILABLE:
            self.theme = UltronTheme()
            self.setup_ultron_demo()
        else:
            self.setup_fallback_demo()
        
        self.start_animations()
    
    def setup_ultron_demo(self):
        """Setup stunning Ultron-themed demonstration"""
        # Main title with glowing effect
        title_frame = create_ultron_frame(self.root, self.theme)
        title_frame.pack(fill='x', padx=20, pady=10)
        
        self.title_label = create_ultron_label(
            title_frame, 
            "🤖 ULTRON AGENT - STUNNING VISUALS ACTIVATED", 
            self.theme
        )
        self.title_label.configure(font=("Orbitron", 16, "bold"))
        self.title_label.pack(pady=10)
        
        # Status panel demonstration
        status_frame = create_ultron_frame(self.root, self.theme)
        status_frame.pack(fill='x', padx=20, pady=10)
        
        status_title = create_ultron_label(status_frame, "🎯 SYSTEM STATUS", self.theme)
        status_title.pack(anchor='w')
        
        # Create status indicators
        self.status_indicators = []
        systems = ["Neural Network", "Visual Engine", "Particle System", "Animation Core"]
        
        for system in systems:
            indicator_frame = tk.Frame(status_frame, bg=self.theme.colors['bg_primary'])
            indicator_frame.pack(fill='x', pady=2)
            
            # Status light
            light = tk.Label(
                indicator_frame,
                text="●",
                fg=self.theme.colors['accent_red'],
                bg=self.theme.colors['bg_primary'],
                font=("Consolas", 16, "bold")
            )
            light.pack(side='left')
            
            # System name
            name_label = create_ultron_label(indicator_frame, f"{system}: ONLINE", self.theme)
            name_label.pack(side='left', padx=(10, 0))
            
            self.status_indicators.append(light)
        
        # Interactive buttons demonstration
        button_frame = create_ultron_frame(self.root, self.theme)
        button_frame.pack(fill='x', padx=20, pady=10)
        
        button_title = create_ultron_label(button_frame, "🚀 INTERACTIVE CONTROLS", self.theme)
        button_title.pack(anchor='w', pady=(0, 10))
        
        # Create demonstration buttons
        buttons_row = tk.Frame(button_frame, bg=self.theme.colors['bg_primary'])
        buttons_row.pack(fill='x')
        
        test_btn = create_ultron_button(buttons_row, "🔥 ACTIVATE", self.pulse_effect, self.theme)
        test_btn.pack(side='left', padx=5)
        
        neural_btn = create_ultron_button(buttons_row, "🧠 NEURAL SCAN", self.neural_effect, self.theme)
        neural_btn.pack(side='left', padx=5)
        
        particle_btn = create_ultron_button(buttons_row, "✨ PARTICLE BURST", self.particle_effect, self.theme)
        particle_btn.pack(side='left', padx=5)
        
        # Visual effects area
        effects_frame = create_ultron_frame(self.root, self.theme)
        effects_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        effects_title = create_ultron_label(effects_frame, "🎨 VISUAL EFFECTS SHOWCASE", self.theme)
        effects_title.pack(anchor='w')
        
        # Canvas for particle effects
        self.canvas = tk.Canvas(
            effects_frame,
            bg='#0a0a0f',
            highlightthickness=2,
            highlightbackground=self.theme.colors['accent_blue']
        )
        self.canvas.pack(fill='both', expand=True, pady=(10, 0))
        
        # Draw initial neural network pattern
        self.draw_neural_network()
    
    def setup_fallback_demo(self):
        """Fallback demo if theme system unavailable"""
        label = tk.Label(
            self.root,
            text="⚠️ Ultron Theme System Not Available\nBut the core system is ready!",
            bg='#2c3e50',
            fg='#ffffff',
            font=("Consolas", 14)
        )
        label.pack(expand=True)
    
    def draw_neural_network(self):
        """Draw animated neural network pattern"""
        self.canvas.delete("neural")
        width = self.canvas.winfo_width() or 400
        height = self.canvas.winfo_height() or 200
        
        # Create nodes
        nodes = []
        for i in range(8):
            x = random.randint(50, width - 50) if width > 100 else 50
            y = random.randint(50, height - 50) if height > 100 else 50
            nodes.append((x, y))
        
        # Draw connections
        for i, (x1, y1) in enumerate(nodes):
            for j, (x2, y2) in enumerate(nodes[i+1:], i+1):
                if random.random() < 0.3:  # 30% connection probability
                    intensity = abs(math.sin(self.glow_phase + i * 0.5)) * 0.5 + 0.5
                    color = f"#{int(255*intensity):02x}0040"
                    self.canvas.create_line(
                        x1, y1, x2, y2,
                        fill=color,
                        width=2,
                        tags="neural"
                    )
        
        # Draw nodes
        for i, (x, y) in enumerate(nodes):
            intensity = abs(math.sin(self.glow_phase + i * 0.3)) * 0.5 + 0.5
            color = f"#00{int(212*intensity):02x}ff"
            self.canvas.create_oval(
                x-8, y-8, x+8, y+8,
                fill=color,
                outline="#ffffff",
                width=2,
                tags="neural"
            )
    
    def pulse_effect(self):
        """Create pulsing glow effect"""
        for indicator in self.status_indicators:
            indicator.configure(fg=self.theme.colors['accent_blue'] if THEME_AVAILABLE else '#00d4ff')
            self.root.after(500, lambda: indicator.configure(
                fg=self.theme.colors['accent_red'] if THEME_AVAILABLE else '#ff0040'
            ))
    
    def neural_effect(self):
        """Trigger neural network animation"""
        self.draw_neural_network()
    
    def particle_effect(self):
        """Create particle burst effect"""
        self.canvas.delete("particles")
        center_x = (self.canvas.winfo_width() or 400) // 2
        center_y = (self.canvas.winfo_height() or 200) // 2
        
        for i in range(20):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(20, 100)
            x = center_x + math.cos(angle) * distance
            y = center_y + math.sin(angle) * distance
            
            self.canvas.create_oval(
                x-3, y-3, x+3, y+3,
                fill='#ff0040',
                outline='#ffffff',
                tags="particles"
            )
        
        # Clear particles after animation
        self.root.after(1000, lambda: self.canvas.delete("particles"))
    
    def animate_glow(self):
        """Continuous glow animation"""
        self.glow_phase += 0.1
        if self.glow_phase > 2 * math.pi:
            self.glow_phase = 0
        
        # Animate title glow
        if hasattr(self, 'title_label'):
            intensity = abs(math.sin(self.glow_phase)) * 0.3 + 0.7
            if THEME_AVAILABLE:
                color = f"#{int(255*intensity):02x}{int(212*intensity):02x}ff"
                self.title_label.configure(fg=color)
        
        # Redraw neural network
        if hasattr(self, 'canvas'):
            self.draw_neural_network()
        
        # Schedule next animation frame
        self.root.after(50, self.animate_glow)
    
    def start_animations(self):
        """Start all animation systems"""
        self.animate_glow()
    
    def run(self):
        """Start the demonstration"""
        print("🤖 Launching ULTRON Theme Demonstration...")
        print("✨ Featuring stunning cyberpunk visuals")
        print("🎯 Interactive controls and effects")
        print("🧠 Neural network animations")
        print("🔥 Real-time particle systems")
        print("\n" + "="*50)
        self.root.mainloop()

if __name__ == "__main__":
    demo = UltronThemeDemo()
    demo.run()
