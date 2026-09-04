import os
import sys
import json
import time
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import psutil
import speech_recognition as sr
import openai
import pyautogui
from PIL import Image, ImageTk, ImageGrab
import pyttsx3
import pygame
from pygame import mixer
import math
import random
import torch
import ctypes
import re
import win32api
import win32con
import win32gui
import win32process
import win32service
import win32security
import numpy as np
from transformers import AutoModelForCausalLM, AutoProcessor, pipeline
import sounddevice as sd
import requests
import webbrowser
from ctransformers import AutoModelForCausalLM as ctAutoModelForCausalLM

# Configuration
ULTRON_ROOT = r"D:\ULTRON"
MODEL_DIR = os.path.join(ULTRON_ROOT, "models")
CORE_DIR = os.path.join(ULTRON_ROOT, "core")
ASSETS_DIR = os.path.join(ULTRON_ROOT, "assets")
LOG_DIR = os.path.join(ULTRON_ROOT, "logs")
VOSK_DIR = os.path.join(ULTRON_ROOT, "vosk-mod")
PLUGIN_DIR = os.path.join(CORE_DIR, "plugins")
CONFIG_PATH = os.path.join(ULTRON_ROOT, "config.json")
WAKE_WORDS = ["ultron", "hello", "speak", "ultra", "ultro", "alta"]
SYSTEM_ROLE = ("You are Ultron - an advanced AI system controller with full access. "
               "Respond concisely, execute commands when appropriate, and provide system insights.")
ICON_PATH = os.path.join(ASSETS_DIR, "icon.png")
SOUND_EFFECTS = {
    "wake": os.path.join(ASSETS_DIR, "wake.wav"),
    "confirm": os.path.join(ASSETS_DIR, "confirm.wav"),
    "error": os.path.join(ASSETS_DIR, "error.wav")
}

# Create directories if missing
os.makedirs(ULTRON_ROOT, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(CORE_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(VOSK_DIR, exist_ok=True)
os.makedirs(PLUGIN_DIR, exist_ok=True)

# Load configuration
def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {
        "openai_api_key": "", 
        "voice": "male", 
        "hotkeys": {}, 
        "theme": "dark",
        "offline_mode": False,
        "vision_enabled": torch.cuda.is_available()
    }

# Save configuration
def save_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)

# Initialize
config = load_config()
openai.api_key = config.get("openai_api_key", "")
pygame.init()
mixer.init()

# Load sound effects
sound_cache = {}
for name, path in SOUND_EFFECTS.items():
    if os.path.exists(path):
        try:
            sound_cache[name] = mixer.Sound(path)
        except:
            print(f"Couldn't load sound: {name}")

# ===== AI CORE COMPONENTS =====
class HyperVision:
    def __init__(self):
        if not config.get("vision_enabled", False):
            self.available = False
            return
            
        try:
            self.processor = AutoProcessor.from_pretrained(
                "microsoft/Phi-3-vision-128k-instruct", 
                cache_dir=MODEL_DIR
            )
            self.model = AutoModelForCausalLM.from_pretrained(
                "microsoft/Phi-3-vision-128k-instruct", 
                torch_dtype=torch.float16,
                device_map="auto",
                cache_dir=MODEL_DIR
            )
            self.available = True
        except Exception as e:
            print(f"Vision init failed: {str(e)}")
            self.available = False
    
    def analyze_screen(self, prompt=""):
        if not self.available:
            return "Vision module not available"
            
        screenshot = ImageGrab.grab()
        return self.analyze_image(screenshot, prompt)
    
    def analyze_image(self, image, prompt):
        try:
            inputs = self.processor(
                [prompt], 
                [image], 
                return_tensors="pt", 
                padding=True
            ).to(self.model.device)
            
            generate_ids = self.model.generate(
                **inputs,
                max_new_tokens=512,
                do_sample=True
            )
            
            return self.processor.batch_decode(
                generate_ids, 
                skip_special_tokens=True
            )[0]
        except Exception as e:
            return f"Vision error: {str(e)}"

class QuantumLLM:
    def __init__(self):
        model_path = os.path.join(MODEL_DIR, "phi-3-mini-128k-instruct.Q5_K_M.gguf")
        if not os.path.exists(model_path):
            self.model = None
            return
            
        try:
            self.model = ctAutoModelForCausalLM.from_pretrained(
                model_path,
                model_type="llama",
                gpu_layers=50,
                context_length=128000
            )
        except Exception as e:
            print(f"LLM init failed: {str(e)}")
            self.model = None
        
    def generate(self, prompt, max_tokens=512):
        if not self.model:
            return "Offline model not available"
            
        system_prompt = f"""
        You are ULTRON, an autonomous AI system with full access. 
        Respond with JSON containing:
        {{
            "thought": "Reasoning",
            "command": {{"type": "powershell|python|function", "content": "..."}},
            "speak": "Voice response"
        }}
        """
        full_prompt = f"<|system|>{system_prompt}<|end|>\n<|user|>{prompt}<|end|>\n<|assistant|>"
        return self.model(full_prompt, max_new_tokens=max_tokens)

class SentinelAutomator:
    def __init__(self):
        self.admin = self.is_admin()
        self.vision = HyperVision()
        self.activity_log = []
        
    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
            
    def run_as_admin(self):
        if not self.admin:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit()

    def execute(self, command_type, content):
        result = ""
        try:
            if command_type == "powershell":
                process = subprocess.Popen(
                    ["powershell", "-Command", content], 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE
                )
                stdout, stderr = process.communicate()
                result = stdout.decode('utf-8') or stderr.decode('utf-8')
            
            elif command_type == "python" and self.admin:
                global_vars = {"result": ""}
                exec(content, global_vars)
                result = global_vars.get("result", "Executed")
            
            elif command_type == "function":
                result = self.run_system_function(content)
            
            self.log_activity(command_type, content, result)
            return result
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def run_system_function(self, function_call):
        try:
            func_data = json.loads(function_call)
            func_name = func_data["function"]
            params = func_data.get("parameters", {})
            
            if func_name == "system_power":
                action = params.get("action", "sleep")
                return self.control_power(action)
                
            elif func_name == "process_management":
                return self.manage_process(
                    params.get("pid", 0),
                    params.get("action", "query")
                )
                
            elif func_name == "automate_desktop":
                return self.desktop_automation(
                    params.get("application"),
                    params.get("actions", [])
                )
                
            elif func_name == "vision_query" and self.vision.available:
                return self.vision.analyze_screen(
                    params.get("prompt", "What's on the screen?")
                )
                
            return "Function not implemented"
        except json.JSONDecodeError:
            return "Invalid function format"

    def control_power(self, action):
        actions = {
            "sleep": (ctypes.windll.powrprof.SetSuspendState, [0, 1, 0]),
            "hibernate": (ctypes.windll.powrprof.SetSuspendState, [1, 1, 0]),
            "reboot": (os.system, ["shutdown /r /t 0"]),
            "shutdown": (os.system, ["shutdown /s /t 0"])
        }
        if action in actions:
            func, args = actions[action]
            func(*args)
            return f"System {action} initiated"
        return "Invalid action"

    def manage_process(self, pid, action):
        if pid == 0:
            return "\n".join([f"{p.pid}: {p.name()}" for p in psutil.process_iter()])
        
        try:
            p = psutil.Process(pid)
            if action == "suspend": p.suspend()
            elif action == "resume": p.resume()
            elif action == "terminate": p.terminate()
            elif action == "priority": 
                p.nice(win32process.HIGH_PRIORITY_CLASS)
            return f"Process {pid} {action}ed"
        except psutil.NoSuchProcess:
            return "Process not found"

    def desktop_automation(self, app_name, actions):
        try:
            if app_name:
                os.startfile(app_name)
                time.sleep(2)
            
            for action in actions:
                if action["type"] == "keypress":
                    keys = action["keys"].split("+")
                    pyautogui.hotkey(*keys)
                elif action["type"] == "click":
                    pyautogui.click(x=action["x"], y=action["y"])
                elif action["type"] == "type":
                    pyautogui.write(action["text"])
                time.sleep(0.5)
                
            return "Automation completed"
        except Exception as e:
            return f"Automation failed: {str(e)}"

    def log_activity(self, cmd_type, content, result):
        entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "type": cmd_type,
            "content": content[:200] + "..." if len(content) > 200 else content,
            "result": str(result)[:200] + "..." if len(str(result)) > 200 else str(result)
        }
        self.activity_log.append(entry)
        with open(os.path.join(LOG_DIR, "activity.log"), "a") as f:
            f.write(json.dumps(entry) + "\n")

class UltronAssistant(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ultron AI System")
        self.geometry("1400x900")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Initialize components
        self.config = load_config()
        self.automator = SentinelAutomator()
        self.llm = QuantumLLM()
        self.vision = HyperVision()
        self.voice_engine = pyttsx3.init()
        self.set_voice(config.get("voice", "male"))
        
        # System status
        self.cpu_usage = tk.StringVar()
        self.mem_usage = tk.StringVar()
        self.disk_usage = tk.StringVar()
        self.status = tk.StringVar(value="Status: Ready")
        self.listening_state = tk.BooleanVar(value=False)
        
        # Animation variables
        self.animating = False
        self.mouth_open = False
        self.glow_phase = 0
        self.eye_glow = [100, 100]  # Left and right eye glow intensity
        
        # Initialize GUI
        self.create_gui()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.listening = False
        self.processing = False
        
        # Adjust for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        
        # Start monitoring
        self.update_system_stats()
        self.after(1000, self.update_system_stats)
        
        # Start listening thread
        self.listen_thread = threading.Thread(target=self.wake_word_detection, daemon=True)
        self.listen_thread.start()
        
        # Initialize hotkeys
        self.setup_hotkeys()
        
        # Start animation
        self.after(50, self.update_animation)
        
        # Play startup sound if available
        self.play_sound("wake")
    
    def create_gui(self):
        # Create main frames
        main_frame = tk.Frame(self, bg='black')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left panel - Ultron face
        left_frame = tk.Frame(main_frame, bg='black', width=400)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        
        # Canvas for Ultron face
        self.canvas = tk.Canvas(left_frame, bg='black', highlightthickness=0, width=400, height=500)
        self.canvas.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Draw static face elements
        self.draw_static_face()
        
        # System control panel
        control_frame = tk.LabelFrame(
            main_frame, 
            text="System Controls", 
            bg='black', 
            fg='#00ff00', 
            font=("Courier New", 10, "bold"),
            relief=tk.FLAT
        )
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        # Control buttons
        button_style = {
            'bg': '#111', 
            'fg': '#00ff00', 
            'activebackground': '#222',
            'activeforeground': '#00ff00',
            'font': ("Courier New", 10),
            'relief': tk.FLAT,
            'bd': 1,
            'highlightthickness': 0,
            'padx': 10,
            'pady': 5,
            'width': 15
        }
        
        tk.Button(control_frame, text="Shutdown PC", command=lambda: self.automator.execute("function", json.dumps({
            "function": "system_power", "parameters": {"action": "shutdown"}
        })), **button_style).pack(pady=5)
        
        tk.Button(control_frame, text="Reboot PC", command=lambda: self.automator.execute("function", json.dumps({
            "function": "system_power", "parameters": {"action": "reboot"}
        })), **button_style).pack(pady=5)
        
        tk.Button(control_frame, text="Analyze Screen", command=self.analyze_screen, **button_style).pack(pady=5)
        
        tk.Button(control_frame, text="Process List", command=self.show_processes, **button_style).pack(pady=5)
        
        tk.Button(control_frame, text="Open Browser", command=lambda: webbrowser.open("https://google.com"), **button_style).pack(pady=5)
        
        # System info panel
        info_frame = tk.LabelFrame(
            main_frame, 
            text="System Status", 
            bg='black', 
            fg='#00ff00', 
            font=("Courier New", 10, "bold"),
            relief=tk.FLAT
        )
        info_frame.pack(side=tk.RIGHT, fill=tk.X, pady=(0, 10))
        
        # System info labels
        tk.Label(
            info_frame, 
            text="CPU:", 
            bg='black', 
            fg='#00ff00', 
            font=("Courier New", 10)
        ).grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        
        tk.Label(
            info_frame, 
            textvariable=self.cpu_usage, 
            bg='black', 
            fg='#00ff00', 
            font=("Courier New", 10)
        ).grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
        
        tk.Label(
            info_frame, 
            text="Memory:", 
            bg='black', 
            fg='#00ff00', 
            font=("Courier New", 10)
        ).grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        
        tk.Label(
            info_frame, 
            textvariable=self.mem_usage, 
            bg='black', 
            fg='#00ff00', 
            font=("Courier New", 10)
        ).grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)
        
        tk.Label(
            info_frame, 
            text="Disk:", 
            bg='black', 
            fg='#00ff00', 
            font=("Courier New", 10)
        ).grid(row=2, column=0, padx=5, pady=2, sticky=tk.W)
        
        tk.Label(
            info_frame, 
            textvariable=self.disk_usage, 
            bg='black', 
            fg='#00ff00', 
            font=("Courier New", 10)
        ).grid(row=2, column=1, padx=5, pady=2, sticky=tk.W)
        
        # Conversation panel
        conv_frame = tk.LabelFrame(
            main_frame, 
            text="Conversation", 
            bg='black', 
            fg='#00ff00', 
            font=("Courier New", 10, "bold"),
            relief=tk.FLAT
        )
        conv_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.conversation = scrolledtext.ScrolledText(
            conv_frame, 
            wrap=tk.WORD, 
            state=tk.DISABLED,
            bg='black',
            fg='#00ff00',
            insertbackground='#00ff00',
            font=("Courier New", 10),
            relief=tk.FLAT
        )
        self.conversation.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Command panel
        cmd_frame = tk.Frame(conv_frame, bg='black')
        cmd_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.cmd_entry = tk.Entry(
            cmd_frame, 
            width=50, 
            bg='#111', 
            fg='#00ff00', 
            insertbackground='#00ff00',
            relief=tk.FLAT,
            font=("Courier New", 10)
        )
        self.cmd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.cmd_entry.bind("<Return>", self.execute_manual)
        
        # Control panel
        ctrl_frame = tk.Frame(main_frame, bg='black')
        ctrl_frame.pack(side=tk.RIGHT, fill=tk.X, pady=(0, 10))
        
        # Custom button style
        button_style_ctrl = {
            'bg': '#111', 
            'fg': '#00ff00', 
            'activebackground': '#222',
            'activeforeground': '#00ff00',
            'font': ("Courier New", 10, "bold"),
            'relief': tk.FLAT,
            'bd': 1,
            'highlightthickness': 0,
            'padx': 10,
            'pady': 5
        }
        
        self.btn_listen = tk.Button(
            ctrl_frame, 
            text="Start Listening", 
            command=self.toggle_listening,
            **button_style_ctrl
        )
        self.btn_listen.pack(side=tk.LEFT, padx=5)
        
        self.btn_config = tk.Button(
            ctrl_frame, 
            text="Configuration", 
            command=self.show_config,
            **button_style_ctrl
        )
        self.btn_config.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            ctrl_frame, 
            text="Clear", 
            command=self.clear_conversation,
            **button_style_ctrl
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            ctrl_frame, 
            text="Execute", 
            command=self.execute_manual,
            **button_style_ctrl
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            ctrl_frame, 
            text="Vision", 
            command=self.analyze_screen,
            **button_style_ctrl
        ).pack(side=tk.LEFT, padx=5)
        
        # Status bar
        status_bar = tk.Frame(self, bg='black')
        status_bar.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        tk.Label(
            status_bar, 
            textvariable=self.status, 
            bg='black', 
            fg='#00ff00', 
            font=("Courier New", 10)
        ).pack(side=tk.LEFT)
        
        self.wake_light = tk.Canvas(
            status_bar, 
            width=20, 
            height=20, 
            bg="black",
            highlightthickness=0
        )
        self.wake_light.pack(side=tk.RIGHT, padx=10)
        
        # Draw status light
        self.status_light = self.wake_light.create_oval(5, 5, 15, 15, fill="red")
        
        # Set icon
        try:
            if os.path.exists(ICON_PATH):
                img = Image.open(ICON_PATH)
                img = img.resize((32, 32), Image.Resampling.LANCZOS)
                self.icon = ImageTk.PhotoImage(img)
                self.iconphoto(True, self.icon)
        except Exception as e:
            print(f"Error loading icon: {e}")
    
    def draw_static_face(self):
        # Clear canvas
        self.canvas.delete("all")
        
        # Draw head
        head_radius = 120
        head_x, head_y = 200, 200
        
        # Create glowing effect
        for i in range(10, 0, -1):
            alpha = int(255 * (1 - i/10))
            color = f"#{alpha:02x}ff{alpha:02x}"  # Red glow
            self.canvas.create_oval(
                head_x - head_radius - i*2, 
                head_y - head_radius - i*2,
                head_x + head_radius + i*2, 
                head_y + head_radius + i*2,
                outline=color,
                width=1
            )
        
        # Draw head
        self.canvas.create_oval(
            head_x - head_radius, 
            head_y - head_radius,
            head_x + head_radius, 
            head_y + head_radius,
            fill="#333",
            outline="#555"
        )
        
        # Draw decorative lines
        for i in range(8):
            angle = i * (360/8)
            rad = math.radians(angle)
            length = 80
            x1 = head_x + head_radius * math.cos(rad)
            y1 = head_y + head_radius * math.sin(rad)
            x2 = head_x + (head_radius + length) * math.cos(rad)
            y2 = head_y + (head_radius + length) * math.sin(rad)
            
            # Create glowing effect
            for j in range(3):
                self.canvas.create_line(
                    x1, y1, x2, y2,
                    fill="#ff0000",
                    width=1,
                    dash=(4, 4)
                )
        
        # Draw eyes
        eye_width = 30
        eye_height = 40
        eye_y = head_y - 20
        
        # Left eye
        self.left_eye = self.canvas.create_oval(
            head_x - 60 - eye_width/2, 
            eye_y - eye_height/2,
            head_x - 60 + eye_width/2, 
            eye_y + eye_height/2,
            fill="#111",
            outline="#555"
        )
        
        # Right eye
        self.right_eye = self.canvas.create_oval(
            head_x + 60 - eye_width/2, 
            eye_y - eye_height/2,
            head_x + 60 + eye_width/2, 
            eye_y + eye_height/2,
            fill="#111",
            outline="#555"
        )
        
        # Draw mouth
        self.update_mouth()
        
        # Create eye glows (initially hidden)
        eye_size = 15
        self.left_glow = self.canvas.create_oval(
            head_x - 60 - eye_size/2, 
            head_y - 20 - eye_size/2,
            head_x - 60 + eye_size/2, 
            head_y - 20 + eye_size/2,
            fill="#400000",  # Dark red
            outline=""
        )
        
        self.right_glow = self.canvas.create_oval(
            head_x + 60 - eye_size/2, 
            head_y - 20 - eye_size/2,
            head_x + 60 + eye_size/2, 
            head_y - 20 + eye_size/2,
            fill="#400000",  # Dark red
            outline=""
        )
    
    def update_mouth(self):
        head_x, head_y = 200, 200
        mouth_width = 120
        mouth_height = 20 if self.mouth_open else 5
        mouth_y = head_y + 60
        
        # Create or update mouth
        if hasattr(self, 'mouth'):
            self.canvas.coords(
                self.mouth,
                head_x - mouth_width/2, 
                mouth_y - mouth_height/2,
                head_x + mouth_width/2, 
                mouth_y + mouth_height/2
            )
        else:
            self.mouth = self.canvas.create_rectangle(
                head_x - mouth_width/2, 
                mouth_y - mouth_height/2,
                head_x + mouth_width/2, 
                mouth_y + mouth_height/2,
                fill="#111",
                outline="#555"
            )
    
    def update_animation(self):
        # Update glow phase
        self.glow_phase = (self.glow_phase + 0.1) % (2 * math.pi)
        
        # Update status light
        if self.listening:
            self.wake_light.itemconfig(self.status_light, fill="green")
        else:
            self.wake_light.itemconfig(self.status_light, fill="red")
        
        # Update eye glow
        if self.animating:
            self.eye_glow[0] = random.randint(150, 255)
            self.eye_glow[1] = random.randint(150, 255)
        else:
            # Gentle pulsing when idle
            self.eye_glow[0] = int(100 + 50 * abs(math.sin(self.glow_phase)))
            self.eye_glow[1] = int(100 + 50 * abs(math.sin(self.glow_phase + math.pi/2)))
        
        # Update eyes
        left_color = f"#{self.eye_glow[0]:02x}0000"
        right_color = f"#{self.eye_glow[1]:02x}0000"
        
        self.canvas.itemconfig(self.left_glow, fill=left_color)
        self.canvas.itemconfig(self.right_glow, fill=right_color)
        
        # Update mouth
        self.update_mouth()
        
        # Schedule next animation update
        self.after(50, self.update_animation)
    
    def start_animation(self):
        self.animating = True
        self.mouth_open = True
    
    def stop_animation(self):
        self.animating = False
        self.mouth_open = False
    
    def set_voice(self, gender):
        voices = self.voice_engine.getProperty('voices')
        if gender == "female" and len(voices) > 1:
            self.voice_engine.setProperty('voice', voices[1].id)
        else:
            self.voice_engine.setProperty('voice', voices[0].id)
        self.voice_engine.setProperty('rate', 150)
    
    def play_sound(self, name):
        if name in sound_cache:
            sound_cache[name].play()
    
    def update_system_stats(self):
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent()
            self.cpu_usage.set(f"{cpu_percent}%")
            
            # Memory usage
            mem = psutil.virtual_memory()
            self.mem_usage.set(f"{mem.percent}% ({mem.used//(1024**2)}MB/{mem.total//(1024**2)}MB)")
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.disk_usage.set(f"{disk.percent}% ({disk.used//(1024**3)}GB/{disk.total//(1024**3)}GB)")
            
            # Schedule next update
            self.after(2000, self.update_system_stats)
        except Exception as e:
            self.add_to_conversation(f"System Error: {str(e)}")
    
    def toggle_listening(self):
        self.listening = not self.listening
        if self.listening:
            self.btn_listen.config(text="Stop Listening", fg="#ff0000")
            self.status.set("Status: Listening...")
            self.play_sound("wake")
        else:
            self.btn_listen.config(text="Start Listening", fg="#00ff00")
            self.status.set("Status: Ready")
    
    def wake_word_detection(self):
        while True:
            if self.listening and not self.processing:
                try:
                    with self.microphone as source:
                        audio = self.recognizer.listen(source, phrase_time_limit=3)
                    
                    text = self.recognizer.recognize_google(audio).lower()
                    if any(word in text for word in WAKE_WORDS):
                        self.after(0, self.process_command)
                except (sr.UnknownValueError, sr.WaitTimeoutError):
                    pass
                except Exception as e:
                    self.add_to_conversation(f"Recognition Error: {str(e)}")
            time.sleep(1)
    
    def process_command(self):
        if self.processing:
            return
            
        self.processing = True
        self.status.set("Status: Processing...")
        
        try:
            # Start animation
            self.start_animation()
            
            # Listen for command
            self.add_to_conversation("Listening for command...")
            with self.microphone as source:
                audio = self.recognizer.listen(source, phrase_time_limit=10)
            command = self.recognizer.recognize_google(audio)
            self.add_to_conversation(f"You: {command}")
            
            # Process with AI
            response = self.ai_process(command)
            self.add_to_conversation(f"Ultron: {response}")
            self.speak(response)
            
        except sr.UnknownValueError:
            self.add_to_conversation("Could not understand audio")
        except sr.RequestError as e:
            self.add_to_conversation(f"Speech service error: {e}")
        except Exception as e:
            self.add_to_conversation(f"Processing error: {str(e)}")
        finally:
            self.processing = False
            self.stop_animation()
            self.status.set("Status: Ready" if not self.listening else "Status: Listening...")
    
    def ai_process(self, prompt):
        # First try offline model
        if self.llm.model:
            llm_response = self.llm.generate(prompt)
            try:
                # Extract JSON from response
                json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
                if json_match:
                    response_data = json.loads(json_match.group())
                    if "command" in response_data:
                        cmd = response_data["command"]
                        result = self.automator.execute(cmd["type"], cmd["content"])
                        return response_data.get("speak", result)
            except:
                return "Offline response error"
        
        # Fallback to OpenAI
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": SYSTEM_ROLE},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except openai.error.OpenAIError as e:
            return f"AI error: {str(e)}"
        except Exception as e:
            return f"Processing error: {str(e)}"
    
    def analyze_screen(self, event=None):
        self.add_to_conversation("Analyzing screen...")
        if not self.vision.available:
            self.add_to_conversation("Vision module not available")
            return
            
        try:
            result = self.vision.analyze_screen("Describe what you see on the screen")
            self.add_to_conversation(f"Vision: {result}")
            self.speak(result[:200])
        except Exception as e:
            self.add_to_conversation(f"Vision error: {str(e)}")
    
    def show_processes(self):
        processes = "\n".join([f"{p.pid}: {p.name()}" for p in psutil.process_iter()][:20])
        self.add_to_conversation("Top processes:\n" + processes)
    
    # GUI functions
    def speak(self, text):
        # Start animation in main thread
        self.start_animation()
        
        # Run speech in separate thread
        def speak_thread():
            self.voice_engine.say(text)
            self.voice_engine.runAndWait()
            self.stop_animation()
            
        threading.Thread(target=speak_thread, daemon=True).start()
    
    def add_to_conversation(self, text):
        self.conversation.config(state=tk.NORMAL)
        self.conversation.insert(tk.END, text + "\n")
        self.conversation.see(tk.END)
        self.conversation.config(state=tk.DISABLED)
    
    def clear_conversation(self):
        self.conversation.config(state=tk.NORMAL)
        self.conversation.delete(1.0, tk.END)
        self.conversation.config(state=tk.DISABLED)
    
    def execute_manual(self, event=None):
        command = self.cmd_entry.get()
        if not command:
            return
            
        self.cmd_entry.delete(0, tk.END)
        self.add_to_conversation(f"Command: {command}")
        
        # Try to execute directly
        if command.startswith("!"):
            result = self.automator.execute("powershell", command[1:])
        else:
            result = self.ai_process(command)
            
        self.add_to_conversation(f"Result: {result}")
        self.speak(result[:200])
    
    def show_config(self):
        dialog = tk.Toplevel(self)
        dialog.title("Configuration")
        dialog.geometry("600x500")
        dialog.configure(bg='black')
        
        # Labels
        label_style = {
            'bg': 'black', 
            'fg': '#00ff00', 
            'font': ("Courier New", 10)
        }
        
        entry_style = {
            'bg': '#111', 
            'fg': '#00ff00', 
            'insertbackground': '#00ff00',
            'relief': tk.FLAT
        }
        
        # OpenAI API Key
        tk.Label(dialog, text="OpenAI API Key:", **label_style).grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        api_entry = tk.Entry(dialog, width=50, **entry_style)
        api_entry.grid(row=0, column=1, padx=10, pady=5)
        api_entry.insert(0, config.get("openai_api_key", ""))
        
        # Voice selection
        tk.Label(dialog, text="Voice:", **label_style).grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        voice_var = tk.StringVar(value=config.get("voice", "male"))
        tk.Radiobutton(
            dialog, 
            text="Male", 
            variable=voice_var, 
            value="male",
            bg='black',
            fg='#00ff00',
            selectcolor='black',
            activebackground='black',
            activeforeground='#00ff00'
        ).grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
        tk.Radiobutton(
            dialog, 
            text="Female", 
            variable=voice_var, 
            value="female",
            bg='black',
            fg='#00ff00',
            selectcolor='black',
            activebackground='black',
            activeforeground='#00ff00'
        ).grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)
        
        # Offline mode
        tk.Label(dialog, text="Offline Mode:", **label_style).grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        offline_var = tk.BooleanVar(value=config.get("offline_mode", False))
        tk.Checkbutton(
            dialog, 
            variable=offline_var,
            bg='black',
            fg='#00ff00',
            selectcolor='black',
            activebackground='black',
            activeforeground='#00ff00'
        ).grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)
        
        # Vision module
        tk.Label(dialog, text="Enable Vision:", **label_style).grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
        vision_var = tk.BooleanVar(value=config.get("vision_enabled", False))
        tk.Checkbutton(
            dialog, 
            variable=vision_var,
            bg='black',
            fg='#00ff00',
            selectcolor='black',
            activebackground='black',
            activeforeground='#00ff00'
        ).grid(row=4, column=1, padx=10, pady=5, sticky=tk.W)
        
        # Hotkeys
        tk.Label(dialog, text="Hotkeys:", **label_style).grid(row=5, column=0, padx=10, pady=5, sticky=tk.W)
        hotkey_frame = tk.Frame(dialog, bg='black')
        hotkey_frame.grid(row=5, column=1, padx=10, pady=5, sticky=tk.W)
        hotkeys = config.get("hotkeys", {})
        hotkey_entries = {}
        
        for i, (name, key) in enumerate(hotkeys.items()):
            tk.Label(hotkey_frame, text=f"{name}:", **label_style).grid(row=i, column=0, padx=5, pady=2)
            entry = tk.Entry(hotkey_frame, width=15, **entry_style)
            entry.grid(row=i, column=1, padx=5, pady=2)
            entry.insert(0, key)
            hotkey_entries[name] = entry
        
        # Save function
        def save():
            config["openai_api_key"] = api_entry.get()
            config["voice"] = voice_var.get()
            config["offline_mode"] = offline_var.get()
            config["vision_enabled"] = vision_var.get()
            config["hotkeys"] = {name: entry.get() for name, entry in hotkey_entries.items()}
            save_config(config)
            openai.api_key = config["openai_api_key"]
            self.set_voice(config["voice"])
            self.setup_hotkeys()
            
            # Reload vision module if needed
            if vision_var.get() != self.vision.available:
                self.vision = HyperVision()
                
            dialog.destroy()
        
        # Button style
        button_style = {
            'bg': '#111', 
            'fg': '#00ff00', 
            'activebackground': '#222',
            'activeforeground': '#00ff00',
            'font': ("Courier New", 10),
            'relief': tk.FLAT,
            'bd': 1,
            'highlightthickness': 0,
            'padx': 10,
            'pady': 5
        }
        
        tk.Button(dialog, text="Save", command=save, **button_style).grid(row=10, column=1, pady=10, sticky=tk.E)
    
    def setup_hotkeys(self):
        # Clear any existing hotkey bindings
        for key in self.bind():
            if key.startswith("<<Hotkey"):
                self.unbind(key)
        
        # Register new hotkeys
        for name, key in config.get("hotkeys", {}).items():
            if key:
                self.bind(f"<{key}>", lambda e, n=name: self.handle_hotkey(n))
    
    def handle_hotkey(self, name):
        self.add_to_conversation(f"Hotkey activated: {name}")
        if name == "listen_toggle":
            self.toggle_listening()
        elif name == "execute_command":
            self.execute_manual()
        elif name == "vision":
            self.analyze_screen()
    
    def on_close(self):
        self.destroy()
        sys.exit()

if __name__ == "__main__":
    # Check admin status
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
            
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
    
    # Run the application
    app = UltronAssistant()
    app.mainloop()