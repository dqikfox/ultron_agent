#!/usr/bin/env python3
"""
ULTRON ULTIMATE - Pokedex-Style Interface
Beautiful retro-futuristic interface inspired by the classic Pokedex
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import time
import threading
import json
import os
from pathlib import Path
import pygame
import numpy as np
from PIL import Image, ImageTk, ImageDraw, ImageFont
import math
import random

class PokedexInterface:
    """Beautiful Pokedex-style interface for ULTRON Ultimate"""
    
    def __init__(self, ultron_core=None):
        self.ultron_core = ultron_core
        self.root = tk.Tk()
        self.root.title("ULTRON Ultimate - Pokedex Interface")
        self.root.geometry("1400x900")
        self.root.configure(bg='#0a0a0a')
        self.root.resizable(False, False)
        
        # Interface state
        self.current_theme = "red"  # red, blue, yellow, green
        self.is_powered_on = True
        self.current_section = "home"
        self.animation_running = False
        self.led_state = {"main": True, "yellow": True, "green": True}
        self.button_states = {}
        
        # Audio system
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Theme colors
        self.themes = {
            "red": {
                "primary": "#dc2626",
                "secondary": "#991b1b", 
                "accent": "#fbbf24",
                "led": "#ff0000",
                "screen_bg": "#001100",
                "screen_text": "#00ff41"
            },
            "blue": {
                "primary": "#2563eb",
                "secondary": "#1d4ed8",
                "accent": "#60a5fa", 
                "led": "#0000ff",
                "screen_bg": "#000011",
                "screen_text": "#4169ff"
            },
            "yellow": {
                "primary": "#eab308",
                "secondary": "#ca8a04",
                "accent": "#fef08a",
                "led": "#ffff00", 
                "screen_bg": "#110a00",
                "screen_text": "#ffaa00"
            },
            "green": {
                "primary": "#16a34a",
                "secondary": "#15803d",
                "accent": "#86efac",
                "led": "#00ff00",
                "screen_bg": "#001100", 
                "screen_text": "#00ff88"
            }
        }
        
        # Load sound effects
        self.load_sounds()
        
        # Create the interface
        self.create_pokedex_interface()
        
        # Start animations
        self.start_animations()
        
        # Play startup sound
        self.play_sound("startup")
    
    def load_sounds(self):
        """Load Pokedex-style sound effects"""
        self.sounds = {}
        
        # Generate simple beep sounds if files don't exist
        sound_dir = Path("assets/sounds")
        sound_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Try to load existing sounds or create simple ones
            self.create_sound_effects()
        except Exception as e:
            print(f"Sound loading error: {e}")
            self.sounds = {}
    
    def create_sound_effects(self):
        """Create simple sound effects using pygame"""
        sample_rate = 22050
        
        # Startup sound - ascending beeps
        startup_sound = self.generate_beep_sequence([440, 523, 659, 880], 0.2, sample_rate)
        self.sounds["startup"] = startup_sound
        
        # Button press - quick beep
        button_sound = self.generate_beep(800, 0.1, sample_rate)
        self.sounds["button"] = button_sound
        
        # Error sound - descending beeps
        error_sound = self.generate_beep_sequence([800, 600, 400], 0.3, sample_rate)
        self.sounds["error"] = error_sound
        
        # Success sound - happy beeps
        success_sound = self.generate_beep_sequence([523, 659, 783, 1047], 0.15, sample_rate)
        self.sounds["success"] = success_sound
    
    def generate_beep(self, frequency, duration, sample_rate):
        """Generate a simple beep sound"""
        frames = int(duration * sample_rate)
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            wave = np.sin(2 * np.pi * frequency * i / sample_rate)
            envelope = np.exp(-i / (sample_rate * 0.1))  # Fade out
            arr[i] = [wave * envelope * 0.3, wave * envelope * 0.3]
        
        return pygame.sndarray.make_sound((arr * 32767).astype(np.int16))
    
    def generate_beep_sequence(self, frequencies, note_duration, sample_rate):
        """Generate a sequence of beeps"""
        total_frames = 0
        sequences = []
        
        for freq in frequencies:
            beep = self.generate_beep(freq, note_duration, sample_rate)
            sequences.append(pygame.sndarray.array(beep))
            total_frames += len(pygame.sndarray.array(beep))
        
        # Combine all beeps
        combined = np.zeros((total_frames, 2), dtype=np.int16)
        offset = 0
        
        for seq in sequences:
            combined[offset:offset + len(seq)] = seq
            offset += len(seq)
        
        return pygame.sndarray.make_sound(combined)
    
    def play_sound(self, sound_name):
        """Play a sound effect"""
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except:
                pass  # Ignore sound errors
    
    def create_pokedex_interface(self):
        """Create the main Pokedex interface"""
        # Main container
        main_frame = tk.Frame(self.root, bg='#000000')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create the Pokedex body
        self.create_pokedex_body(main_frame)
    
    def create_pokedex_body(self, parent):
        """Create the main Pokedex body with all components"""
        # Pokedex container with perspective
        pokedex_frame = tk.Frame(parent, bg='#000000')
        pokedex_frame.pack(expand=True)
        
        # Main Pokedex body
        body_frame = tk.Frame(
            pokedex_frame,
            bg=self.themes[self.current_theme]["primary"],
            relief=tk.RAISED,
            bd=8
        )
        body_frame.pack(padx=40, pady=20)
        
        # Top section with LEDs and title
        self.create_top_section(body_frame)
        
        # Main screen section
        self.create_main_screen(body_frame)
        
        # Control panel section
        self.create_control_panel(body_frame)
        
        # Bottom section with speaker
        self.create_bottom_section(body_frame)
    
    def create_top_section(self, parent):
        """Create the top section with LEDs and title"""
        top_frame = tk.Frame(parent, bg=self.themes[self.current_theme]["primary"])
        top_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # LED lights section
        led_frame = tk.Frame(top_frame, bg=self.themes[self.current_theme]["primary"])
        led_frame.pack(anchor=tk.W, pady=(0, 15))
        
        # Main LED (large)
        self.main_led = tk.Canvas(
            led_frame, 
            width=60, 
            height=60, 
            bg=self.themes[self.current_theme]["primary"],
            highlightthickness=0
        )
        self.main_led.pack(side=tk.LEFT, padx=(0, 20))
        
        # Draw main LED
        self.draw_led(self.main_led, 30, 30, 25, self.themes[self.current_theme]["led"], True)
        
        # Small LEDs
        small_leds_frame = tk.Frame(led_frame, bg=self.themes[self.current_theme]["primary"])
        small_leds_frame.pack(side=tk.LEFT)
        
        # Yellow LED
        self.yellow_led = tk.Canvas(
            small_leds_frame,
            width=30,
            height=30,
            bg=self.themes[self.current_theme]["primary"],
            highlightthickness=0
        )
        self.yellow_led.pack(side=tk.LEFT, padx=5)
        self.draw_led(self.yellow_led, 15, 15, 12, "#ffff00", True)
        
        # Green LED
        self.green_led = tk.Canvas(
            small_leds_frame,
            width=30,
            height=30,
            bg=self.themes[self.current_theme]["primary"],
            highlightthickness=0
        )
        self.green_led.pack(side=tk.LEFT, padx=5)
        self.draw_led(self.green_led, 15, 15, 12, "#00ff00", True)
        
        # Title section
        title_frame = tk.Frame(top_frame, bg=self.themes[self.current_theme]["primary"])
        title_frame.pack(fill=tk.X, pady=15)\n        \n        # Main title\n        title_label = tk.Label(\n            title_frame,\n            text=\"ULTRON ULTIMATE\",\n            font=(\"Orbitron\", 28, \"bold\"),\n            fg=self.themes[self.current_theme]["screen_text"],\n            bg=self.themes[self.current_theme]["primary"]\n        )\n        title_label.pack()\n        \n        # Subtitle\n        subtitle_label = tk.Label(\n            title_frame,\n            text=\"Advanced AI System • Pokedex Interface\",\n            font=(\"Courier\", 12, \"bold\"),\n            fg=self.themes[self.current_theme]["accent"],\n            bg=self.themes[self.current_theme]["primary"]\n        )\n        subtitle_label.pack()\n    \n    def create_main_screen(self, parent):\n        \"\"\"Create the main screen area\"\"\"\n        screen_frame = tk.Frame(\n            parent,\n            bg=self.themes[self.current_theme]["secondary"],\n            relief=tk.SUNKEN,\n            bd=8\n        )\n        screen_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)\n        \n        # Screen border\n        border_frame = tk.Frame(\n            screen_frame,\n            bg=\"#2c2c2c\",\n            relief=tk.RAISED,\n            bd=4\n        )\n        border_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)\n        \n        # Main screen content\n        self.screen_content = tk.Frame(\n            border_frame,\n            bg=self.themes[self.current_theme]["screen_bg"],\n            relief=tk.FLAT\n        )\n        self.screen_content.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)\n        \n        # Create scan lines overlay\n        self.create_scan_lines()\n        \n        # Screen content area\n        self.create_screen_content()\n    \n    def create_scan_lines(self):\n        \"\"\"Create CRT-style scan lines effect\"\"\"\n        self.scan_canvas = tk.Canvas(\n            self.screen_content,\n            bg=self.themes[self.current_theme]["screen_bg"],\n            highlightthickness=0\n        )\n        self.scan_canvas.place(relwidth=1, relheight=1)\n        \n        # Add scan lines\n        def update_scan_lines():\n            if not self.animation_running:\n                return\n            \n            self.scan_canvas.delete(\"scan_line\")\n            height = self.scan_canvas.winfo_height()\n            width = self.scan_canvas.winfo_width()\n            \n            if height > 0 and width > 0:\n                # Create moving scan line\n                y_pos = (time.time() * 100) % height\n                \n                # Main scan line\n                self.scan_canvas.create_line(\n                    0, y_pos, width, y_pos,\n                    fill=self.themes[self.current_theme][\"screen_text\"],\n                    width=2,\n                    tags=\"scan_line\"\n                )\n                \n                # Fading trail\n                for i in range(5):\n                    trail_y = (y_pos - (i + 1) * 10) % height\n                    alpha = 1.0 - (i * 0.2)\n                    if alpha > 0:\n                        color = self.hex_to_rgb(self.themes[self.current_theme][\"screen_text\"])\n                        faded_color = f\"#{int(color[0]*alpha):02x}{int(color[1]*alpha):02x}{int(color[2]*alpha):02x}\"\n                        \n                        self.scan_canvas.create_line(\n                            0, trail_y, width, trail_y,\n                            fill=faded_color,\n                            width=1,\n                            tags=\"scan_line\"\n                        )\n            \n            self.root.after(50, update_scan_lines)\n        \n        self.root.after(100, update_scan_lines)\n    \n    def create_screen_content(self):\n        \"\"\"Create the main screen content area\"\"\"\n        # Content frame over scan lines\n        content_frame = tk.Frame(\n            self.screen_content,\n            bg=self.themes[self.current_theme][\"screen_bg\"]\n        )\n        content_frame.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)\n        \n        # Status bar\n        status_frame = tk.Frame(\n            content_frame,\n            bg=self.themes[self.current_theme][\"screen_bg\"]\n        )\n        status_frame.pack(fill=tk.X, pady=(0, 10))\n        \n        # Current section indicator\n        self.section_label = tk.Label(\n            status_frame,\n            text=\"█ HOME SECTION █\",\n            font=(\"Courier\", 14, \"bold\"),\n            fg=self.themes[self.current_theme][\"screen_text\"],\n            bg=self.themes[self.current_theme][\"screen_bg\"]\n        )\n        self.section_label.pack()\n        \n        # System status\n        self.status_label = tk.Label(\n            status_frame,\n            text=\"SYSTEM: ONLINE • AI: READY • VOICE: ACTIVE\",\n            font=(\"Courier\", 10),\n            fg=self.themes[self.current_theme][\"accent\"],\n            bg=self.themes[self.current_theme][\"screen_bg\"]\n        )\n        self.status_label.pack()\n        \n        # Main content area\n        self.main_content = scrolledtext.ScrolledText(\n            content_frame,\n            wrap=tk.WORD,\n            state=tk.DISABLED,\n            bg=self.themes[self.current_theme][\"screen_bg\"],\n            fg=self.themes[self.current_theme][\"screen_text\"],\n            font=(\"Courier\", 11),\n            insertbackground=self.themes[self.current_theme][\"screen_text\"],\n            selectbackground=self.themes[self.current_theme][\"secondary\"],\n            relief=tk.FLAT,\n            bd=0\n        )\n        self.main_content.pack(fill=tk.BOTH, expand=True)\n        \n        # Configure text tags for colored output\n        self.setup_text_tags()\n        \n        # Add welcome message\n        self.add_screen_text(\"ULTRON\", \"🤖 ULTRON ULTIMATE ONLINE\", \"header\")\n        self.add_screen_text(\"SYSTEM\", \"All systems operational\", \"success\")\n        self.add_screen_text(\"AI\", \"Advanced AI brain ready for commands\", \"info\")\n        self.add_screen_text(\"VOICE\", \"Voice recognition active - say 'Hey ULTRON'\", \"voice\")\n        self.add_screen_text(\"READY\", \"Awaiting your command, trainer!\", \"ready\")\n    \n    def setup_text_tags(self):\n        \"\"\"Setup text tags for colored output\"\"\"\n        self.main_content.tag_configure(\n            \"header\",\n            foreground=self.themes[self.current_theme][\"accent\"],\n            font=(\"Courier\", 12, \"bold\")\n        )\n        \n        self.main_content.tag_configure(\n            \"success\",\n            foreground=\"#00ff88\",\n            font=(\"Courier\", 10, \"bold\")\n        )\n        \n        self.main_content.tag_configure(\n            \"error\",\n            foreground=\"#ff4444\",\n            font=(\"Courier\", 10, \"bold\")\n        )\n        \n        self.main_content.tag_configure(\n            \"info\",\n            foreground=self.themes[self.current_theme][\"screen_text\"],\n            font=(\"Courier\", 10)\n        )\n        \n        self.main_content.tag_configure(\n            \"voice\",\n            foreground=\"#ffaa00\",\n            font=(\"Courier\", 10, \"bold\")\n        )\n        \n        self.main_content.tag_configure(\n            \"ready\",\n            foreground=self.themes[self.current_theme][\"accent\"],\n            font=(\"Courier\", 11, \"bold\")\n        )\n    \n    def add_screen_text(self, prefix, message, tag=\"info\"):\n        \"\"\"Add text to the main screen with timestamp\"\"\"\n        self.main_content.config(state=tk.NORMAL)\n        \n        timestamp = time.strftime(\"%H:%M:%S\")\n        \n        # Add timestamp\n        self.main_content.insert(tk.END, f\"[{timestamp}] \")\n        \n        # Add prefix with icon\n        icons = {\n            \"ULTRON\": \"🤖\",\n            \"SYSTEM\": \"⚙️\",\n            \"AI\": \"🧠\",\n            \"VOICE\": \"🎤\",\n            \"USER\": \"👤\",\n            \"ERROR\": \"❌\",\n            \"SUCCESS\": \"✅\",\n            \"READY\": \"⚡\"\n        }\n        \n        icon = icons.get(prefix, \"💬\")\n        self.main_content.insert(tk.END, f\"{icon} {prefix}: \", tag)\n        \n        # Add message\n        self.main_content.insert(tk.END, f\"{message}\\n\")\n        \n        self.main_content.config(state=tk.DISABLED)\n        self.main_content.see(tk.END)\n    \n    def create_control_panel(self, parent):\n        \"\"\"Create the Pokedex control panel\"\"\"\n        control_frame = tk.Frame(\n            parent,\n            bg=self.themes[self.current_theme][\"secondary\"]\n        )\n        control_frame.pack(fill=tk.X, padx=20, pady=20)\n        \n        # Left controls - D-Pad\n        left_controls = tk.Frame(\n            control_frame,\n            bg=self.themes[self.current_theme][\"secondary\"]\n        )\n        left_controls.pack(side=tk.LEFT, padx=30)\n        \n        self.create_dpad(left_controls)\n        \n        # Center controls - Main buttons\n        center_controls = tk.Frame(\n            control_frame,\n            bg=self.themes[self.current_theme][\"secondary\"]\n        )\n        center_controls.pack(side=tk.LEFT, expand=True, padx=30)\n        \n        self.create_main_buttons(center_controls)\n        \n        # Right controls - Action buttons\n        right_controls = tk.Frame(\n            control_frame,\n            bg=self.themes[self.current_theme][\"secondary\"]\n        )\n        right_controls.pack(side=tk.RIGHT, padx=30)\n        \n        self.create_action_buttons(right_controls)\n    \n    def create_dpad(self, parent):\n        \"\"\"Create the D-Pad navigation control\"\"\"\n        dpad_frame = tk.Frame(parent, bg=self.themes[self.current_theme][\"secondary\"])\n        dpad_frame.pack()\n        \n        tk.Label(\n            dpad_frame,\n            text=\"NAVIGATION\",\n            font=(\"Courier\", 10, \"bold\"),\n            fg=self.themes[self.current_theme][\"accent\"],\n            bg=self.themes[self.current_theme][\"secondary\"]\n        ).pack(pady=(0, 10))\n        \n        # D-Pad container\n        dpad_container = tk.Frame(dpad_frame, bg=self.themes[self.current_theme][\"secondary\"])\n        dpad_container.pack()\n        \n        # Up button\n        self.dpad_up = tk.Button(\n            dpad_container,\n            text=\"▲\",\n            font=(\"Arial\", 16, \"bold\"),\n            bg=\"#333333\",\n            fg=\"white\",\n            activebackground=\"#555555\",\n            width=3,\n            height=1,\n            relief=tk.RAISED,\n            bd=3,\n            command=lambda: self.dpad_press(\"up\")\n        )\n        self.dpad_up.grid(row=0, column=1, padx=2, pady=2)\n        \n        # Left and Right buttons\n        self.dpad_left = tk.Button(\n            dpad_container,\n            text=\"◄\",\n            font=(\"Arial\", 16, \"bold\"),\n            bg=\"#333333\",\n            fg=\"white\",\n            activebackground=\"#555555\",\n            width=3,\n            height=1,\n            relief=tk.RAISED,\n            bd=3,\n            command=lambda: self.dpad_press(\"left\")\n        )\n        self.dpad_left.grid(row=1, column=0, padx=2, pady=2)\n        \n        # Center circle\n        dpad_center = tk.Frame(\n            dpad_container,\n            bg=\"#666666\",\n            width=40,\n            height=30,\n            relief=tk.SUNKEN,\n            bd=2\n        )\n        dpad_center.grid(row=1, column=1, padx=2, pady=2)\n        \n        self.dpad_right = tk.Button(\n            dpad_container,\n            text=\"►\",\n            font=(\"Arial\", 16, \"bold\"),\n            bg=\"#333333\",\n            fg=\"white\",\n            activebackground=\"#555555\",\n            width=3,\n            height=1,\n            relief=tk.RAISED,\n            bd=3,\n            command=lambda: self.dpad_press(\"right\")\n        )\n        self.dpad_right.grid(row=1, column=2, padx=2, pady=2)\n        \n        # Down button\n        self.dpad_down = tk.Button(\n            dpad_container,\n            text=\"▼\",\n            font=(\"Arial\", 16, \"bold\"),\n            bg=\"#333333\",\n            fg=\"white\",\n            activebackground=\"#555555\",\n            width=3,\n            height=1,\n            relief=tk.RAISED,\n            bd=3,\n            command=lambda: self.dpad_press(\"down\")\n        )\n        self.dpad_down.grid(row=2, column=1, padx=2, pady=2)\n    \n    def create_main_buttons(self, parent):\n        \"\"\"Create the main control buttons\"\"\"\n        buttons_frame = tk.Frame(parent, bg=self.themes[self.current_theme][\"secondary\"])\n        buttons_frame.pack()\n        \n        tk.Label(\n            buttons_frame,\n            text=\"MAIN CONTROLS\",\n            font=(\"Courier\", 10, \"bold\"),\n            fg=self.themes[self.current_theme][\"accent\"],\n            bg=self.themes[self.current_theme][\"secondary\"]\n        ).pack(pady=(0, 15))\n        \n        # Row 1\n        row1 = tk.Frame(buttons_frame, bg=self.themes[self.current_theme][\"secondary\"])\n        row1.pack(pady=5)\n        \n        self.create_control_button(row1, \"🎤 VOICE\", \"#27ae60\", self.toggle_voice)\n        self.create_control_button(row1, \"📸 SCREEN\", \"#3498db\", self.take_screenshot)\n        self.create_control_button(row1, \"🎨 THEME\", \"#9b59b6\", self.cycle_theme)\n        \n        # Row 2\n        row2 = tk.Frame(buttons_frame, bg=self.themes[self.current_theme][\"secondary\"])\n        row2.pack(pady=5)\n        \n        self.create_control_button(row2, \"📊 STATUS\", \"#f39c12\", self.show_system_status)\n        self.create_control_button(row2, \"🌐 WEB\", \"#e67e22\", self.open_web_interface)\n        self.create_control_button(row2, \"⚙️ SETTINGS\", \"#34495e\", self.show_settings)\n    \n    def create_action_buttons(self, parent):\n        \"\"\"Create the action buttons (A, B, START, SELECT)\"\"\"\n        action_frame = tk.Frame(parent, bg=self.themes[self.current_theme][\"secondary\"])\n        action_frame.pack()\n        \n        tk.Label(\n            action_frame,\n            text=\"ACTION BUTTONS\",\n            font=(\"Courier\", 10, \"bold\"),\n            fg=self.themes[self.current_theme][\"accent\"],\n            bg=self.themes[self.current_theme][\"secondary\"]\n        ).pack(pady=(0, 10))\n        \n        # A and B buttons\n        ab_frame = tk.Frame(action_frame, bg=self.themes[self.current_theme][\"secondary\"])\n        ab_frame.pack(pady=10)\n        \n        # B button (left)\n        self.b_button = tk.Button(\n            ab_frame,\n            text=\"B\",\n            font=(\"Arial\", 14, \"bold\"),\n            bg=\"#e74c3c\",\n            fg=\"white\",\n            activebackground=\"#c0392b\",\n            width=4,\n            height=2,\n            relief=tk.RAISED,\n            bd=4,\n            command=lambda: self.action_button_press(\"B\")\n        )\n        self.b_button.pack(side=tk.LEFT, padx=10)\n        \n        # A button (right)\n        self.a_button = tk.Button(\n            ab_frame,\n            text=\"A\",\n            font=(\"Arial\", 14, \"bold\"),\n            bg=\"#27ae60\",\n            fg=\"white\",\n            activebackground=\"#229954\",\n            width=4,\n            height=2,\n            relief=tk.RAISED,\n            bd=4,\n            command=lambda: self.action_button_press(\"A\")\n        )\n        self.a_button.pack(side=tk.LEFT, padx=10)\n        \n        # START and SELECT buttons\n        start_select_frame = tk.Frame(action_frame, bg=self.themes[self.current_theme][\"secondary\"])\n        start_select_frame.pack(pady=10)\n        \n        self.select_button = tk.Button(\n            start_select_frame,\n            text=\"SELECT\",\n            font=(\"Arial\", 8, \"bold\"),\n            bg=\"#7f8c8d\",\n            fg=\"white\",\n            activebackground=\"#95a5a6\",\n            width=8,\n            height=1,\n            relief=tk.RAISED,\n            bd=2,\n            command=lambda: self.action_button_press(\"SELECT\")\n        )\n        self.select_button.pack(side=tk.LEFT, padx=5)\n        \n        self.start_button = tk.Button(\n            start_select_frame,\n            text=\"START\",\n            font=(\"Arial\", 8, \"bold\"),\n            bg=\"#34495e\",\n            fg=\"white\",\n            activebackground=\"#2c3e50\",\n            width=8,\n            height=1,\n            relief=tk.RAISED,\n            bd=2,\n            command=lambda: self.action_button_press(\"START\")\n        )\n        self.start_button.pack(side=tk.LEFT, padx=5)\n    \n    def create_control_button(self, parent, text, color, command):\n        \"\"\"Create a styled control button\"\"\"\n        button = tk.Button(\n            parent,\n            text=text,\n            font=(\"Courier\", 9, \"bold\"),\n            bg=color,\n            fg=\"white\",\n            activebackground=self.darken_color(color),\n            width=12,\n            height=2,\n            relief=tk.RAISED,\n            bd=3,\n            command=command\n        )\n        button.pack(side=tk.LEFT, padx=5)\n        return button\n    \n    def create_bottom_section(self, parent):\n        \"\"\"Create the bottom section with speaker grille\"\"\"\n        bottom_frame = tk.Frame(\n            parent,\n            bg=self.themes[self.current_theme][\"secondary\"]\n        )\n        bottom_frame.pack(fill=tk.X, padx=20, pady=20)\n        \n        # Speaker grille\n        speaker_frame = tk.Frame(\n            bottom_frame,\n            bg=self.themes[self.current_theme][\"secondary\"]\n        )\n        speaker_frame.pack()\n        \n        tk.Label(\n            speaker_frame,\n            text=\"🔊 SPEAKER\",\n            font=(\"Courier\", 12, \"bold\"),\n            fg=self.themes[self.current_theme][\"accent\"],\n            bg=self.themes[self.current_theme][\"secondary\"]\n        ).pack(pady=(0, 10))\n        \n        # Speaker grille pattern\n        grille_canvas = tk.Canvas(\n            speaker_frame,\n            width=300,\n            height=60,\n            bg=self.themes[self.current_theme][\"secondary\"],\n            highlightthickness=0\n        )\n        grille_canvas.pack()\n        \n        # Draw speaker holes\n        self.draw_speaker_grille(grille_canvas)\n    \n    def draw_led(self, canvas, x, y, radius, color, is_on):\n        \"\"\"Draw an LED light with glow effect\"\"\"\n        if is_on:\n            # Outer glow\n            canvas.create_oval(\n                x - radius - 5, y - radius - 5,\n                x + radius + 5, y + radius + 5,\n                fill=color, outline=\"\", width=0\n            )\n            \n            # Inner LED\n            canvas.create_oval(\n                x - radius, y - radius,\n                x + radius, y + radius,\n                fill=color, outline=\"white\", width=2\n            )\n            \n            # Highlight\n            canvas.create_oval(\n                x - radius//2, y - radius//2,\n                x + radius//2, y + radius//2,\n                fill=\"white\", outline=\"\", width=0\n            )\n        else:\n            # Off LED\n            canvas.create_oval(\n                x - radius, y - radius,\n                x + radius, y + radius,\n                fill=\"#333333\", outline=\"#666666\", width=2\n            )\n    \n    def draw_speaker_grille(self, canvas):\n        \"\"\"Draw the speaker grille pattern\"\"\"\n        width = 300\n        height = 60\n        \n        # Draw holes in a grid pattern\n        for row in range(6):\n            for col in range(25):\n                x = 15 + col * 11\n                y = 10 + row * 8\n                \n                if x < width - 10 and y < height - 5:\n                    canvas.create_oval(\n                        x - 2, y - 2, x + 2, y + 2,\n                        fill=\"#1a1a1a\", outline=\"\", width=0\n                    )\n    \n    def start_animations(self):\n        \"\"\"Start LED and other animations\"\"\"\n        self.animation_running = True\n        self.animate_leds()\n    \n    def animate_leds(self):\n        \"\"\"Animate LED blinking and glowing\"\"\"\n        if not self.animation_running:\n            return\n        \n        # Animate main LED with breathing effect\n        current_time = time.time()\n        brightness = (math.sin(current_time * 2) + 1) / 2  # 0 to 1\n        \n        # Update main LED\n        self.main_led.delete(\"all\")\n        color = self.themes[self.current_theme][\"led\"]\n        if self.led_state[\"main\"]:\n            alpha = 0.5 + brightness * 0.5\n            glow_color = self.adjust_color_brightness(color, alpha)\n            self.draw_led(self.main_led, 30, 30, 25, glow_color, True)\n        else:\n            self.draw_led(self.main_led, 30, 30, 25, color, False)\n        \n        # Small LEDs blink occasionally\n        if random.random() < 0.1:  # 10% chance to blink\n            self.led_state[\"yellow\"] = not self.led_state[\"yellow\"]\n            self.yellow_led.delete(\"all\")\n            self.draw_led(self.yellow_led, 15, 15, 12, \"#ffff00\", self.led_state[\"yellow\"])\n        \n        if random.random() < 0.05:  # 5% chance to blink\n            self.led_state[\"green\"] = not self.led_state[\"green\"]\n            self.green_led.delete(\"all\")\n            self.draw_led(self.green_led, 15, 15, 12, \"#00ff00\", self.led_state[\"green\"])\n        \n        # Continue animation\n        self.root.after(100, self.animate_leds)\n    \n    # Button handlers\n    def dpad_press(self, direction):\n        \"\"\"Handle D-Pad button presses\"\"\"\n        self.play_sound(\"button\")\n        self.add_screen_text(\"INPUT\", f\"D-Pad {direction.upper()} pressed\", \"info\")\n        \n        if direction == \"up\":\n            self.scroll_content(-5)\n        elif direction == \"down\":\n            self.scroll_content(5)\n        elif direction == \"left\":\n            self.previous_section()\n        elif direction == \"right\":\n            self.next_section()\n    \n    def action_button_press(self, button):\n        \"\"\"Handle action button presses\"\"\"\n        self.play_sound(\"button\")\n        self.add_screen_text(\"INPUT\", f\"Button {button} pressed\", \"info\")\n        \n        if button == \"A\":\n            self.execute_primary_action()\n        elif button == \"B\":\n            self.execute_secondary_action()\n        elif button == \"START\":\n            self.show_main_menu()\n        elif button == \"SELECT\":\n            self.show_settings()\n    \n    def toggle_voice(self):\n        \"\"\"Toggle voice recognition\"\"\"\n        self.play_sound(\"button\")\n        if self.ultron_core:\n            # Toggle voice in main system\n            self.add_screen_text(\"VOICE\", \"Voice system toggled\", \"success\")\n        else:\n            self.add_screen_text(\"VOICE\", \"Voice system ready (demo mode)\", \"info\")\n    \n    def take_screenshot(self):\n        \"\"\"Take a screenshot\"\"\"\n        self.play_sound(\"button\")\n        try:\n            import pyautogui\n            screenshot = pyautogui.screenshot()\n            timestamp = time.strftime(\"%Y%m%d_%H%M%S\")\n            filename = f\"screenshot_{timestamp}.png\"\n            screenshot.save(filename)\n            self.add_screen_text(\"SYSTEM\", f\"Screenshot saved: {filename}\", \"success\")\n            self.play_sound(\"success\")\n        except Exception as e:\n            self.add_screen_text(\"ERROR\", f\"Screenshot failed: {str(e)}\", \"error\")\n            self.play_sound(\"error\")\n    \n    def cycle_theme(self):\n        \"\"\"Cycle through available themes\"\"\"\n        self.play_sound(\"button\")\n        themes = list(self.themes.keys())\n        current_index = themes.index(self.current_theme)\n        next_index = (current_index + 1) % len(themes)\n        self.current_theme = themes[next_index]\n        \n        self.add_screen_text(\"THEME\", f\"Theme changed to {self.current_theme.upper()}\", \"success\")\n        \n        # Note: Full theme update would require recreating the interface\n        # For now, just update text colors\n        self.update_theme_colors()\n    \n    def show_system_status(self):\n        \"\"\"Show comprehensive system status\"\"\"\n        self.play_sound(\"button\")\n        try:\n            import psutil\n            \n            cpu = psutil.cpu_percent(interval=1)\n            memory = psutil.virtual_memory()\n            disk = psutil.disk_usage('.')\n            \n            self.add_screen_text(\"STATUS\", \"=== SYSTEM STATUS ===\", \"header\")\n            self.add_screen_text(\"CPU\", f\"Usage: {cpu:.1f}%\", \"info\")\n            self.add_screen_text(\"MEMORY\", f\"Usage: {memory.percent:.1f}% ({memory.used//1024//1024} MB)\", \"info\")\n            self.add_screen_text(\"DISK\", f\"Usage: {disk.percent:.1f}%\", \"info\")\n            self.add_screen_text(\"STATUS\", \"All systems operational\", \"success\")\n            \n        except ImportError:\n            self.add_screen_text(\"STATUS\", \"System monitoring not available\", \"error\")\n    \n    def open_web_interface(self):\n        \"\"\"Open the web interface\"\"\"\n        self.play_sound(\"button\")\n        try:\n            import webbrowser\n            webbrowser.open(\"http://localhost:8080\")\n            self.add_screen_text(\"WEB\", \"Web interface opened in browser\", \"success\")\n        except Exception as e:\n            self.add_screen_text(\"WEB\", f\"Failed to open web interface: {str(e)}\", \"error\")\n    \n    def show_settings(self):\n        \"\"\"Show settings menu\"\"\"\n        self.play_sound(\"button\")\n        self.add_screen_text(\"SETTINGS\", \"=== SETTINGS MENU ===\", \"header\")\n        self.add_screen_text(\"THEME\", f\"Current theme: {self.current_theme.upper()}\", \"info\")\n        self.add_screen_text(\"VOICE\", \"Voice recognition: ENABLED\", \"success\")\n        self.add_screen_text(\"AUDIO\", \"Sound effects: ENABLED\", \"success\")\n        self.add_screen_text(\"DISPLAY\", \"Scan lines: ENABLED\", \"success\")\n        self.add_screen_text(\"HELP\", \"Use D-Pad and buttons to navigate\", \"info\")\n    \n    def show_main_menu(self):\n        \"\"\"Show main menu\"\"\"\n        self.play_sound(\"button\")\n        self.add_screen_text(\"MENU\", \"=== MAIN MENU ===\", \"header\")\n        self.add_screen_text(\"SYSTEM\", \"1. System Control\", \"info\")\n        self.add_screen_text(\"AI\", \"2. AI Commands\", \"info\")\n        self.add_screen_text(\"AUTOMATION\", \"3. Automation\", \"info\")\n        self.add_screen_text(\"FILES\", \"4. File Management\", \"info\")\n        self.add_screen_text(\"WEB\", \"5. Web Tools\", \"info\")\n        self.add_screen_text(\"GAMES\", \"6. Gaming\", \"info\")\n        self.add_screen_text(\"HELP\", \"Use A/B buttons to select\", \"ready\")\n    \n    def execute_primary_action(self):\n        \"\"\"Execute primary action (A button)\"\"\"\n        self.add_screen_text(\"ACTION\", \"Primary action executed\", \"success\")\n        \n        # Example: If in menu, select item\n        # Example: If in normal mode, execute command\n        if hasattr(self, 'ultron_core') and self.ultron_core:\n            # Send command to main ULTRON system\n            pass\n    \n    def execute_secondary_action(self):\n        \"\"\"Execute secondary action (B button)\"\"\"\n        self.add_screen_text(\"ACTION\", \"Secondary action executed\", \"info\")\n        \n        # Example: Go back, cancel, etc.\n    \n    def scroll_content(self, delta):\n        \"\"\"Scroll the main content\"\"\"\n        try:\n            self.main_content.yview_scroll(delta, \"units\")\n        except:\n            pass\n    \n    def previous_section(self):\n        \"\"\"Navigate to previous section\"\"\"\n        sections = [\"home\", \"system\", \"ai\", \"automation\", \"files\", \"web\", \"games\"]\n        current_index = sections.index(self.current_section)\n        prev_index = (current_index - 1) % len(sections)\n        self.current_section = sections[prev_index]\n        self.section_label.config(text=f\"█ {self.current_section.upper()} SECTION █\")\n        self.add_screen_text(\"NAV\", f\"Switched to {self.current_section.upper()} section\", \"info\")\n    \n    def next_section(self):\n        \"\"\"Navigate to next section\"\"\"\n        sections = [\"home\", \"system\", \"ai\", \"automation\", \"files\", \"web\", \"games\"]\n        current_index = sections.index(self.current_section)\n        next_index = (current_index + 1) % len(sections)\n        self.current_section = sections[next_index]\n        self.section_label.config(text=f\"█ {self.current_section.upper()} SECTION █\")\n        self.add_screen_text(\"NAV\", f\"Switched to {self.current_section.upper()} section\", \"info\")\n    \n    # Utility methods\n    def hex_to_rgb(self, hex_color):\n        \"\"\"Convert hex color to RGB tuple\"\"\"\n        hex_color = hex_color.lstrip('#')\n        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))\n    \n    def adjust_color_brightness(self, color, factor):\n        \"\"\"Adjust color brightness\"\"\"\n        r, g, b = self.hex_to_rgb(color)\n        r = int(r * factor)\n        g = int(g * factor)\n        b = int(b * factor)\n        return f\"#{r:02x}{g:02x}{b:02x}\"\n    \n    def darken_color(self, color):\n        \"\"\"Darken a color for button active state\"\"\"\n        return self.adjust_color_brightness(color, 0.8)\n    \n    def update_theme_colors(self):\n        \"\"\"Update theme colors for existing elements\"\"\"\n        # Update screen text colors\n        self.setup_text_tags()\n        \n        # Update status labels\n        self.section_label.config(fg=self.themes[self.current_theme][\"screen_text\"])\n        self.status_label.config(fg=self.themes[self.current_theme][\"accent\"])\n    \n    def set_ultron_core(self, ultron_core):\n        \"\"\"Set reference to main ULTRON system\"\"\"\n        self.ultron_core = ultron_core\n        self.add_screen_text(\"CORE\", \"Connected to ULTRON Ultimate core system\", \"success\")\n    \n    def run(self):\n        \"\"\"Start the Pokedex interface\"\"\"\n        try:\n            self.root.protocol(\"WM_DELETE_WINDOW\", self.on_close)\n            self.root.mainloop()\n        except KeyboardInterrupt:\n            self.on_close()\n    \n    def on_close(self):\n        \"\"\"Handle application close\"\"\"\n        self.animation_running = False\n        pygame.mixer.quit()\n        self.root.destroy()\n\ndef main():\n    \"\"\"Main entry point for Pokedex interface demo\"\"\"\n    print(\"🤖 Starting ULTRON Ultimate Pokedex Interface...\")\n    \n    try:\n        interface = PokedexInterface()\n        interface.run()\n    except Exception as e:\n        print(f\"Error starting Pokedex interface: {e}\")\n\nif __name__ == \"__main__\":\n    main()\n"