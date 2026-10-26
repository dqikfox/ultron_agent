import os
import sys
import ctypes
import subprocess
import urllib.request
import zipfile
import json
import time
import torch
import psutil
import win32api
import win32con
import win32gui
import win32process
import win32service
import win32security
import pyautogui
import numpy as np
import speech_recognition as sr
from PIL import Image, ImageGrab
from transformers import AutoModelForCausalLM, AutoProcessor, pipeline
from ctransformers import AutoModelForCausalLM as ctAutoModelForCausalLM
import sounddevice as sd
import soundfile as sf
import requests
from threading import Thread, Lock
from queue import Queue
import re

# ===== ULTRON CONFIGURATION =====
ULTRON_ROOT = r"D:\ULTRON"
MODEL_DIR = os.path.join(ULTRON_ROOT, "models")
CORE_DIR = os.path.join(ULTRON_ROOT, "core")
ASSETS_DIR = os.path.join(ULTRON_ROOT, "assets")
LOG_DIR = os.path.join(ULTRON_ROOT, "logs")
INTERFACE_DIR = os.path.join(ULTRON_ROOT, "interface")
VOSK_DIR = os.path.join(ULTRON_ROOT, "vosk-mod")
CHAOS_DIR = os.path.join(ULTRON_ROOT, "chaos realm")
PLUGIN_DIR = os.path.join(CORE_DIR, "plugins")

# Model URLs
PHI3_MODEL_URL = "https://huggingface.co/TheBloke/Phi-3-mini-128k-instruct-GGUF/resolve/main/phi-3-mini-128k-instruct.Q5_K_M.gguf"
VOSK_MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22-lgraph.zip"

# ===== SETUP FUNCTIONS =====
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

def create_directory_structure():
    os.makedirs(ULTRON_ROOT, exist_ok=True)
    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(CORE_DIR, exist_ok=True)
    os.makedirs(ASSETS_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(INTERFACE_DIR, exist_ok=True)
    os.makedirs(VOSK_DIR, exist_ok=True)
    os.makedirs(CHAOS_DIR, exist_ok=True)
    os.makedirs(PLUGIN_DIR, exist_ok=True)
    os.makedirs(os.path.join(INTERFACE_DIR, "html", "Max1"), exist_ok=True)
    print("Created ULTRON directory structure")

def install_dependencies():
    dependencies = [
        "torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118",
        "ctransformers>=0.2.27",
        "sounddevice>=0.4.6",
        "soundfile>=0.12.1",
        "pywin32>=306",
        "pyaudio>=0.2.14",
        "Pillow>=10.0.1",
        "transformers>=4.40.0",
        "requests>=2.31.0",
        "numpy>=1.26.4",
        "SpeechRecognition>=3.10.0",
        "pyautogui>=0.9.54",
        "selenium>=4.19.0",
        "python-dotenv>=1.0.1"
    ]
    
    print("Installing Python dependencies...")
    for dep in dependencies:
        subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
    
    print("Installing system requirements...")
    subprocess.run([
        "powershell", "-Command", 
        "Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force; "
        "Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force; "
        "Install-Module -Name DirectML -Force"
    ], shell=True)
    print("Dependencies installed")

def download_file(url, destination):
    print(f"Downloading {os.path.basename(destination)}...")
    urllib.request.urlretrieve(url, destination)
    print("Download complete")

def extract_zip(zip_path, extract_to):
    print(f"Extracting {os.path.basename(zip_path)}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    os.remove(zip_path)
    print("Extraction complete")

def setup_environment():
    run_as_admin()
    create_directory_structure()
    
    # Download models if missing
    phi3_path = os.path.join(MODEL_DIR, "phi-3-mini-128k-instruct.Q5_K_M.gguf")
    vosk_zip = os.path.join(VOSK_DIR, "vosk-model-en-us-0.22-lgraph.zip")
    
    if not os.path.exists(phi3_path):
        download_file(PHI3_MODEL_URL, phi3_path)
    
    if not os.path.exists(os.path.join(VOSK_DIR, "vosk-model-en-us-0.22")):
        if not os.path.exists(vosk_zip):
            download_file(VOSK_MODEL_URL, vosk_zip)
        extract_zip(vosk_zip, VOSK_DIR)
    
    # Install Python dependencies
    install_dependencies()
    
    # Create sample plugin
    plugin_path = os.path.join(PLUGIN_DIR, "web_automation.py")
    if not os.path.exists(plugin_path):
        with open(plugin_path, "w") as f:
            f.write("""def register(ultron):
    return {
        "browse": lambda url: ultron.automator.execute(
            "python", 
            f"import webbrowser; webbrowser.open('{url}')"
        ),
        "search": lambda query: ultron.automator.execute(
            "python",
            f"import webbrowser; webbrowser.open('https://google.com/search?q={query}')"
        )
    }""")
        print("Created sample plugin")
    
    print("ULTRON setup complete!")

# ===== ULTRON AI SYSTEM =====
class HyperVision:
    def __init__(self):
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
    
    def analyze_screen(self, prompt=""):
        screenshot = ImageGrab.grab()
        return self.analyze_image(screenshot, prompt)
    
    def analyze_image(self, image, prompt):
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

class QuantumLLM:
    def __init__(self):
        model_path = os.path.join(MODEL_DIR, "phi-3-mini-128k-instruct.Q5_K_M.gguf")
        self.model = ctAutoModelForCausalLM.from_pretrained(
            model_path,
            model_type="llama",
            gpu_layers=50,
            context_length=128000
        )
        self.system_prompt = self.load_system_prompt()
        
    def load_system_prompt(self):
        return f"""
        You are ULTRON, an autonomous AI system with full admin access on Windows 11.
        User device: MSI Thin Laptop | RTX 3050 | 64GB RAM
        Respond with JSON containing:
        {{
            "thought": "Reasoning",
            "command": {{"type": "powershell|python|function", "content": "..."}},
            "speak": "Voice response"
        }}
        """
    
    def generate(self, prompt, max_tokens=512):
        full_prompt = f"<|system|>{self.system_prompt}<|end|>\n<|user|>{prompt}<|end|>\n<|assistant|>"
        return self.model(full_prompt, max_new_tokens=max_tokens)

class CyberVoice:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        self.audio_queue = Queue()
        self.listening = False
        self.lock = Lock()
        
        # Pre-load TTS
        self.tts = pipeline(
            "text-to-speech", 
            model="suno/bark-small", 
            cache_dir=MODEL_DIR
        )
        
        # Try to load VOSK for offline recognition
        self.vosk_model = None
        vosk_model_path = os.path.join(VOSK_DIR, "vosk-model-en-us-0.22")
        if os.path.exists(vosk_model_path):
            try:
                from vosk import Model, KaldiRecognizer
                self.vosk_model = Model(vosk_model_path)
                print("Loaded VOSK for offline speech recognition")
            except ImportError:
                print("VOSK not available, using online recognition")
    
    def start_listening(self):
        self.listening = True
        Thread(target=self._listen_thread).start()
        
    def _listen_thread(self):
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while self.listening:
                audio = self.recognizer.listen(source, phrase_time_limit=5)
                self.audio_queue.put(audio)
    
    def get_command(self):
        if not self.audio_queue.empty():
            audio = self.audio_queue.get()
            try:
                # Try offline recognition first
                if self.vosk_model:
                    from vosk import KaldiRecognizer
                    recognizer = KaldiRecognizer(self.vosk_model, 16000)
                    recognizer.AcceptWaveform(audio.get_wav_data())
                    text = json.loads(recognizer.Result())["text"]
                else:
                    text = self.recognizer.recognize_google(audio).lower()
                
                if "ultron" in text:
                    return text.replace("ultron", "").strip()
            except Exception as e:
                print(f"Speech recognition error: {str(e)}")
        return None
    
    def speak(self, text):
        audio = self.tts(text, forward_params={
            "do_sample": True,
            "temperature": 0.7
        })
        sd.play(audio["audio"], samplerate=audio["sampling_rate"])
        sd.wait()

class SentinelAutomator:
    def __init__(self):
        self.admin = is_admin()
        self.vision = HyperVision() if torch.cuda.is_available() else None
        self.activity_log = []
        
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
                
            elif func_name == "vision_query" and self.vision:
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

class UltronAI:
    def __init__(self):
        self.llm = QuantumLLM()
        self.voice = CyberVoice()
        self.automator = SentinelAutomator()
        self.monitoring = True
        self.plugins = self.load_plugins()
        
        # Start background services
        self.voice.start_listening()
        Thread(target=self.system_monitor).start()
        
    def load_plugins(self):
        plugins = {}
        if os.path.exists(PLUGIN_DIR):
            sys.path.append(PLUGIN_DIR)
            for file in os.listdir(PLUGIN_DIR):
                if file.endswith(".py") and file != "__init__.py":
                    module_name = file[:-3]
                    try:
                        module = __import__(module_name)
                        if hasattr(module, "register"):
                            plugins.update(module.register(self))
                            print(f"Loaded plugin: {module_name}")
                    except Exception as e:
                        print(f"Error loading plugin {module_name}: {str(e)}")
        return plugins
    
    def system_monitor(self):
        while self.monitoring:
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory().percent
            
            if cpu > 90 or mem > 90:
                alert = f"System stress: CPU {cpu}%, Memory {mem}%"
                self.voice.speak(alert)
                
            time.sleep(30)
    
    def process_command(self, command):
        llm_response = self.llm.generate(command)
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                response_data = json.loads(json_match.group())
            else:
                return "No valid response", "LLM response format error"
        except json.JSONDecodeError:
            return "JSON parse error", "Could not parse LLM response"
        
        if "command" in response_data:
            cmd = response_data["command"]
            result = self.automator.execute(cmd["type"], cmd["content"])
        else:
            result = "No executable command"
        
        speech = response_data.get("speak", result)
        self.voice.speak(speech[:500])
        
        return result, speech
    
    def run(self):
        self.voice.speak("ULTRON system online. All systems operational.")
        print("ULTRON AI ACTIVE | AWAITING COMMANDS")
        
        while True:
            try:
                command = self.voice.get_command()
                if command:
                    print(f"\n⚡ USER: {command}")
                    result, speech = self.process_command(command)
                    print(f"🤖 RESPONSE: {speech}")
                    print(f"📊 RESULT: {result[:200]}...")
                    
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                self.shutdown()
                break
    
    def shutdown(self):
        self.monitoring = False
        self.voice.listening = False
        self.voice.speak("Initiating shutdown sequence. ULTRON signing off.")
        print("System shutdown complete")

# ===== MAIN EXECUTION =====
if __name__ == "__main__":
    # Check if setup is needed
    phi3_exists = os.path.exists(os.path.join(MODEL_DIR, "phi-3-mini-128k-instruct.Q5_K_M.gguf"))
    vosk_exists = os.path.exists(os.path.join(VOSK_DIR, "vosk-model-en-us-0.22"))
    
    if not phi3_exists or not vosk_exists:
        print("Starting ULTRON setup...")
        setup_environment()
        print("Setup complete! Please restart the script to run ULTRON AI.")
        input("Press Enter to exit...")
        sys.exit()
    
    # Run ULTRON AI
    if not is_admin():
        run_as_admin()
    else:
        ai = UltronAI()
        ai.run()