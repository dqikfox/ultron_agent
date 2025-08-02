"""
ULTRON Agent 2.0 - Stunning Visual Theme System
Cyberpunk/Ultron-inspired GUI with advanced visual effects
"""

import tkinter as tk
from tkinter import ttk
import math
import time
import threading
from PIL import Image, ImageTk, ImageDraw, ImageFilter

class UltronTheme:
    """Advanced Ultron-style theme with cyberpunk visual effects"""
    
    def __init__(self):
        # Ultron Color Palette
        self.colors = {
            'bg_primary': '#0a0a0f',           # Deep space black
            'bg_secondary': '#1a1a2e',         # Dark navy
            'bg_tertiary': '#16213e',          # Ultron panel blue
            'accent_red': '#ff0040',           # Ultron red (primary)
            'accent_blue': '#00d4ff',          # Cyberpunk blue
            'accent_purple': '#a855f7',        # Neural purple
            'accent_green': '#00ff88',         # Matrix green
            'accent_orange': '#ff6b35',        # Warning orange
            'text_primary': '#ffffff',         # Pure white
            'text_secondary': '#b4c6d9',       # Light blue-gray
            'text_muted': '#6b7280',           # Muted gray
            'glow_red': '#ff0040',             # Red without alpha (Tkinter compatible)
            'glow_blue': '#00d4ff',            # Blue without alpha (Tkinter compatible)
            'border_active': '#ff0040',        # Active red border
            'border_inactive': '#374151',      # Inactive gray border
        }
        
        # Animation states
        self.glow_intensity = 0
        self.pulse_phase = 0
        self.neural_network_points = []
        self.particle_systems = []
        
    def apply_ultron_style(self, widget):
        """Apply Ultron theme to any tkinter widget"""
        if isinstance(widget, tk.Tk) or isinstance(widget, tk.Toplevel):
            self._style_window(widget)
        elif isinstance(widget, tk.Frame):
            self._style_frame(widget)
        elif isinstance(widget, tk.Button):
            self._style_button(widget)
        elif isinstance(widget, tk.Label):
            self._style_label(widget)
        elif isinstance(widget, tk.Entry):
            self._style_entry(widget)
        elif isinstance(widget, ttk.Combobox):
            self._style_combobox(widget)
            
    def _style_window(self, window):
        """Style main window with Ultron aesthetics"""
        window.configure(bg=self.colors['bg_primary'])
        window.attributes('-alpha', 0.98)  # Slight transparency
        
        # Custom window border effect
        self._add_border_glow(window)
        
    def _style_frame(self, frame):
        """Style frame with cyberpunk look"""
        frame.configure(
            bg=self.colors['bg_secondary'],
            relief='flat',
            bd=1,
            highlightbackground=self.colors['border_inactive'],
            highlightcolor=self.colors['border_active'],
            highlightthickness=1
        )
        
    def _style_button(self, button):
        """Style button with Ultron red theme"""
        button.configure(
            bg=self.colors['bg_tertiary'],
            fg=self.colors['text_primary'],
            activebackground=self.colors['accent_red'],
            activeforeground=self.colors['text_primary'],
            relief='flat',
            bd=2,
            font=('Consolas', 10, 'bold'),
            cursor='hand2',
            highlightbackground=self.colors['border_active'],
            highlightcolor=self.colors['accent_red'],
            highlightthickness=2
        )
        
        # Add hover effects
        self._add_button_hover_effects(button)
        
    def _style_label(self, label):
        """Style label with futuristic font"""
        label.configure(
            bg=self.colors['bg_primary'],
            fg=self.colors['text_primary'],
            font=('Consolas', 9, 'normal')
        )
        
    def _style_entry(self, entry):
        """Style entry with cyberpunk input field"""
        entry.configure(
            bg=self.colors['bg_tertiary'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['accent_red'],
            relief='flat',
            bd=2,
            font=('Consolas', 10),
            highlightbackground=self.colors['border_inactive'],
            highlightcolor=self.colors['accent_red'],
            highlightthickness=2
        )
        
    def _style_combobox(self, combobox):
        """Style combobox with Ultron theme"""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Ultron.TCombobox',
            fieldbackground=self.colors['bg_tertiary'],
            background=self.colors['bg_secondary'],
            foreground=self.colors['text_primary'],
            arrowcolor=self.colors['accent_red'],
            bordercolor=self.colors['border_inactive'],
            lightcolor=self.colors['accent_red'],
            darkcolor=self.colors['accent_red']
        )
        
        combobox.configure(style='Ultron.TCombobox')
        
    def _add_button_hover_effects(self, button):
        """Add glowing hover effects to buttons"""
        original_bg = button.cget('bg')
        
        def on_enter(event):
            button.configure(
                bg=self.colors['accent_red'],
                relief='raised',
                bd=3
            )
            self._start_glow_animation(button)
            
        def on_leave(event):
            button.configure(
                bg=original_bg,
                relief='flat',
                bd=2
            )
            self._stop_glow_animation(button)
            
        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)
        
    def _add_border_glow(self, window):
        """Add glowing border effect to window"""
        # This would require custom drawing - placeholder for now
        pass
        
    def _start_glow_animation(self, widget):
        """Start glowing animation for widget"""
        # Placeholder for glow animation
        pass
        
    def _stop_glow_animation(self, widget):
        """Stop glowing animation for widget"""
        # Placeholder for glow animation
        pass

class UltronStatusPanel:
    """Advanced status panel with cyberpunk elements"""
    
    def __init__(self, parent, theme):
        self.parent = parent
        self.theme = theme
        self.canvas = None
        self.animation_running = False
        
    def create_status_panel(self):
        """Create animated status panel"""
        # Main status frame
        status_frame = tk.Frame(self.parent, bg=self.theme.colors['bg_secondary'])
        status_frame.pack(fill='x', padx=5, pady=2)
        
        # Create canvas for custom graphics
        self.canvas = tk.Canvas(
            status_frame,
            bg=self.theme.colors['bg_primary'],
            height=100,
            highlightthickness=0
        )
        self.canvas.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Start animations
        self.start_animations()
        
        return status_frame
        
    def start_animations(self):
        """Start all status panel animations"""
        self.animation_running = True
        self.animate_neural_network()
        self.animate_system_stats()
        
    def animate_neural_network(self):
        """Animate neural network background"""
        if not self.animation_running:
            return
            
        self.canvas.delete('neural')
        
        # Draw animated neural network
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width > 1 and height > 1:
            # Generate neural nodes
            nodes = []
            for i in range(8):
                x = (i * width // 7) + (math.sin(time.time() + i) * 10)
                y = height // 2 + (math.cos(time.time() * 0.5 + i) * 20)
                nodes.append((x, y))
                
                # Draw pulsing nodes
                pulse = abs(math.sin(time.time() * 2 + i)) * 5 + 3
                self.canvas.create_oval(
                    x - pulse, y - pulse, x + pulse, y + pulse,
                    fill=self.theme.colors['accent_red'],
                    outline=self.theme.colors['glow_red'],
                    width=2,
                    tags='neural'
                )
            
            # Draw connecting lines
            for i in range(len(nodes) - 1):
                x1, y1 = nodes[i]
                x2, y2 = nodes[i + 1]
                
                # Animated line opacity
                alpha = abs(math.sin(time.time() + i * 0.5)) * 0.8 + 0.2
                color = self.theme.colors['accent_blue']
                
                self.canvas.create_line(
                    x1, y1, x2, y2,
                    fill=color,
                    width=2,
                    tags='neural'
                )
        
        # Schedule next frame
        self.parent.after(50, self.animate_neural_network)
        
    def animate_system_stats(self):
        """Animate system statistics display"""
        if not self.animation_running:
            return
            
        self.canvas.delete('stats')
        
        # Add system stats with glowing text
        stats_text = [
            "● NEURAL NETWORKS: ONLINE",
            "● VOICE SYSTEMS: OPERATIONAL", 
            "● AI MODELS: 10 DETECTED",
            "● STATUS: FULLY OPERATIONAL"
        ]
        
        y_offset = 10
        for i, text in enumerate(stats_text):
            # Pulsing text effect
            alpha = abs(math.sin(time.time() * 1.5 + i * 0.3)) * 0.5 + 0.5
            
            self.canvas.create_text(
                10, y_offset + (i * 20),
                text=text,
                fill=self.theme.colors['accent_green'],
                font=('Consolas', 8, 'bold'),
                anchor='w',
                tags='stats'
            )
        
        # Schedule next frame
        self.parent.after(100, self.animate_system_stats)

class UltronParticleSystem:
    """Advanced particle system for visual effects"""
    
    def __init__(self, canvas, theme):
        self.canvas = canvas
        self.theme = theme
        self.particles = []
        self.running = False
        
    def start(self):
        """Start particle system"""
        self.running = True
        self.update_particles()
        
    def stop(self):
        """Stop particle system"""
        self.running = False
        
    def add_particle(self, x, y, vx=0, vy=0, life=100, color=None):
        """Add a new particle"""
        if color is None:
            color = self.theme.colors['accent_red']
            
        particle = {
            'x': x, 'y': y, 'vx': vx, 'vy': vy,
            'life': life, 'max_life': life,
            'color': color, 'size': 2
        }
        self.particles.append(particle)
        
    def update_particles(self):
        """Update and render all particles"""
        if not self.running:
            return
            
        self.canvas.delete('particles')
        
        # Update particles
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            
            # Calculate alpha based on life
            alpha = particle['life'] / particle['max_life']
            size = particle['size'] * alpha
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
            else:
                # Draw particle
                self.canvas.create_oval(
                    particle['x'] - size, particle['y'] - size,
                    particle['x'] + size, particle['y'] + size,
                    fill=particle['color'],
                    outline='',
                    tags='particles'
                )
        
        # Add random particles
        if len(self.particles) < 50:
            import random
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
            
            if width > 1 and height > 1:
                self.add_particle(
                    random.randint(0, width),
                    random.randint(0, height),
                    random.uniform(-1, 1),
                    random.uniform(-1, 1),
                    random.randint(50, 150)
                )
        
        # Schedule next frame
        self.canvas.after(30, self.update_particles)

def apply_ultron_theme_to_gui(gui_instance):
    """Apply complete Ultron theme to existing GUI"""
    theme = UltronTheme()
    
    # Apply theme to main window
    if hasattr(gui_instance, 'root'):
        theme.apply_ultron_style(gui_instance.root)
        
        # Style all child widgets
        for widget in gui_instance.root.winfo_children():
            apply_theme_recursive(widget, theme)
            
    return theme

def apply_theme_recursive(widget, theme):
    """Recursively apply theme to all widgets"""
    theme.apply_ultron_style(widget)
    
    # Apply to all children
    try:
        for child in widget.winfo_children():
            apply_theme_recursive(child, theme)
    except:
        pass  # Some widgets don't have children

# Enhanced styling functions
def create_ultron_button(parent, text, command=None, theme=None):
    """Create a stylized Ultron button"""
    if theme is None:
        theme = UltronTheme()
        
    button = tk.Button(
        parent,
        text=text,
        command=command,
        bg=theme.colors['bg_tertiary'],
        fg=theme.colors['text_primary'],
        activebackground=theme.colors['accent_red'],
        activeforeground=theme.colors['text_primary'],
        relief='flat',
        bd=2,
        font=('Consolas', 10, 'bold'),
        cursor='hand2'
    )
    
    theme.apply_ultron_style(button)
    return button

def create_ultron_label(parent, text, theme=None):
    """Create a stylized Ultron label"""
    if theme is None:
        theme = UltronTheme()
        
    label = tk.Label(
        parent,
        text=text,
        bg=theme.colors['bg_primary'],
        fg=theme.colors['text_primary'],
        font=('Consolas', 9, 'normal')
    )
    
    theme.apply_ultron_style(label)
    return label

def create_ultron_frame(parent, theme=None):
    """Create a stylized Ultron frame"""
    if theme is None:
        theme = UltronTheme()
        
    frame = tk.Frame(
        parent,
        bg=theme.colors['bg_secondary'],
        relief='flat',
        bd=1
    )
    
    theme.apply_ultron_style(frame)
    return frame
