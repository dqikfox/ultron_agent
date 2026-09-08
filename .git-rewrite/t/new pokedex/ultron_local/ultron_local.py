#!/usr/bin/env python3
"""
ULTRON Local - Fully Offline AI Assistant
Optimized for restricted network environments
"""

import os
import sys
import json
import time
import asyncio
import threading
import logging
import subprocess
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext

# Core dependencies
import speech_recognition as sr
import pyttsx3
import cv2
import pytesseract
import numpy as np
import psutil
import pyautogui
from PIL import Image, ImageGrab
import keyboard
from flask import Flask, render_template, request, jsonify
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM

class LocalAI:
    """Local AI processing without internet dependency"""
    
    def __init__(self):
        self.nlp_pipeline = None
        self.text_generator = None
        self.initialized = False
        
    def initialize(self):
        """Initialize local AI models"""
        try:
            # Initialize lightweight text generation
            model_name = "microsoft/DialoGPT-small"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            
            # Initialize basic NLP pipeline
            self.nlp_pipeline = pipeline("text-classification", 
                                       model="distilbert-base-uncased-finetuned-sst-2-english")
            
            self.initialized = True
            logging.info("Local AI models initialized successfully")
            return True
            
        except Exception as e:
            logging.error(f"Failed to initialize local AI: {e}")
            self.initialized = False
            return False
    
    def generate_response(self, text, max_length=100):
        """Generate AI response locally"""
        if not self.initialized:
            return "AI not initialized. Using basic responses."
        
        try:
            # Encode the input
            inputs = self.tokenizer.encode(text + self.tokenizer.eos_token, return_tensors='pt')
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(inputs, max_length=max_length, 
                                            num_return_sequences=1, pad_token_id=self.tokenizer.eos_token_id)
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Clean up response
            if text in response:
                response = response.replace(text, "").strip()
            
            return response if response else "I understand. How can I help you?"
            
        except Exception as e:
            logging.error(f"AI generation error: {e}")
            return "I'm processing your request. Please try again."

class VoiceProcessor:
    """Local voice recognition and synthesis"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        self.listening = False
        
        # Configure TTS
        voices = self.tts_engine.getProperty('voices')
        if voices:
            self.tts_engine.setProperty('voice', voices[0].id)
        self.tts_engine.setProperty('rate', 150)
        
        # Calibrate microphone
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            logging.info("Microphone calibrated")
        except Exception as e:
            logging.error(f"Microphone calibration failed: {e}")
    
    def listen_once(self, timeout=5):
        """Listen for a single command"""
        try:
            with self.microphone as source:
                logging.info("Listening...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            # Try local recognition first
            try:
                text = self.recognizer.recognize_sphinx(audio)
                logging.info(f"Sphinx recognized: {text}")
                return text
            except:
                # Fallback to Google (will fail in offline mode)
                try:
                    text = self.recognizer.recognize_google(audio)
                    logging.info(f"Google recognized: {text}")
                    return text
                except:
                    logging.warning("No speech recognition available")
                    return None
                    
        except sr.WaitTimeoutError:
            return None
        except Exception as e:
            logging.error(f"Listen error: {e}")
            return None
    
    def speak(self, text):
        """Speak text using TTS"""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            logging.error(f"TTS error: {e}")

class VisionSystem:
    """Local computer vision and OCR"""
    
    def __init__(self):
        self.screenshots_dir = Path("screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
    
    def take_screenshot(self):
        """Take and save screenshot"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.screenshots_dir / f"screenshot_{timestamp}.png"
            
            screenshot = ImageGrab.grab()
            screenshot.save(filename)
            
            logging.info(f"Screenshot saved: {filename}")
            return str(filename)
            
        except Exception as e:
            logging.error(f"Screenshot error: {e}")
            return None
    
    def ocr_image(self, image_path):
        """Extract text from image using OCR"""
        try:
            image = cv2.imread(str(image_path))
            
            # Preprocess image for better OCR
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
            
            # Extract text
            text = pytesseract.image_to_string(gray)
            
            logging.info("OCR completed")
            return text.strip()
            
        except Exception as e:
            logging.error(f"OCR error: {e}")
            return ""
    
    def analyze_screen(self):
        """Take screenshot and analyze with OCR"""
        screenshot_path = self.take_screenshot()
        if screenshot_path:
            text = self.ocr_image(screenshot_path)
            return {
                "screenshot": screenshot_path,
                "text": text,
                "timestamp": datetime.now().isoformat()
            }
        return None

class SystemController:
    """System automation and control"""
    
    def __init__(self):
        self.admin_mode = self.check_admin()
    
    def check_admin(self):
        """Check if running with admin privileges"""
        try:
            if os.name == 'nt':  # Windows
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin()
            else:  # Unix-like
                return os.geteuid() == 0
        except:
            return False
    
    def get_system_info(self):
        """Get comprehensive system information"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available": memory.available,
                "disk_percent": disk.percent,
                "disk_free": disk.free,
                "timestamp": datetime.now().isoformat(),
                "admin_mode": self.admin_mode
            }
        except Exception as e:
            logging.error(f"System info error: {e}")
            return {"error": str(e)}
    
    def list_processes(self, limit=20):
        """List running processes"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            return processes[:limit]
            
        except Exception as e:
            logging.error(f"Process list error: {e}")
            return []
    
    def execute_command(self, command):
        """Execute system command safely"""
        try:
            # Basic command whitelist for security
            safe_commands = {
                "notepad": "notepad.exe",
                "calculator": "calc.exe",
                "paint": "mspaint.exe",
                "cmd": "cmd.exe"
            }
            
            if command.lower() in safe_commands:
                subprocess.Popen(safe_commands[command.lower()])
                return f"Launched {command}"
            else:
                return f"Command '{command}' not in safe list"
                
        except Exception as e:
            logging.error(f"Command execution error: {e}")
            return f"Error executing command: {e}"

class FileManager:
    """Intelligent file management and sorting"""
    
    def __init__(self):
        self.base_dir = Path("managed_files")
        self.base_dir.mkdir(exist_ok=True)
        
        # Create category directories
        self.categories = {
            "documents": ["pdf", "doc", "docx", "txt", "rtf"],
            "images": ["jpg", "jpeg", "png", "gif", "bmp", "webp"],
            "videos": ["mp4", "avi", "mkv", "mov", "wmv"],
            "audio": ["mp3", "wav", "flac", "aac"],
            "archives": ["zip", "rar", "7z", "tar", "gz"],
            "code": ["py", "js", "html", "css", "cpp", "java"],
            "executables": ["exe", "msi", "deb", "rpm"]
        }
        
        for category in self.categories:
            (self.base_dir / category).mkdir(exist_ok=True)
    
    def classify_file(self, file_path):
        """Classify file by extension"""
        extension = Path(file_path).suffix.lower().lstrip('.')
        
        for category, extensions in self.categories.items():
            if extension in extensions:
                return category
        
        return "other"
    
    def sort_directory(self, source_dir):
        """Sort files in directory by type"""
        try:
            source_path = Path(source_dir)
            if not source_path.exists():
                return {"error": "Directory not found"}
            
            sorted_files = {}
            total_files = 0
            
            for file_path in source_path.iterdir():
                if file_path.is_file():
                    category = self.classify_file(file_path)
                    
                    # Create destination path
                    dest_dir = self.base_dir / category
                    dest_path = dest_dir / file_path.name
                    
                    # Handle filename conflicts
                    counter = 1
                    original_dest = dest_path
                    while dest_path.exists():
                        stem = original_dest.stem
                        suffix = original_dest.suffix
                        dest_path = dest_dir / f"{stem}_{counter}{suffix}"
                        counter += 1
                    
                    # Move file
                    file_path.rename(dest_path)
                    
                    if category not in sorted_files:
                        sorted_files[category] = []
                    sorted_files[category].append(str(dest_path))
                    total_files += 1
            
            return {
                "sorted_files": sorted_files,
                "total_files": total_files,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"File sorting error: {e}")
            return {"error": str(e)}

class UltronGUI:
    """Local ULTRON GUI interface"""
    
    def __init__(self, ultron_core):
        self.ultron = ultron_core
        self.root = tk.Tk()
        self.root.title("ULTRON - Local AI Assistant")
        self.root.geometry("800x600")
        self.root.configure(bg='black')
        
        self.setup_gui()
    
    def setup_gui(self):
        """Setup GUI components"""
        # Title
        title_label = tk.Label(self.root, text="ULTRON - LOCAL AI", 
                              font=("Arial", 20, "bold"), 
                              fg="red", bg="black")
        title_label.pack(pady=10)
        
        # Status frame
        status_frame = tk.Frame(self.root, bg="black")
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_label = tk.Label(status_frame, text="Status: Ready", 
                                   fg="green", bg="black")
        self.status_label.pack(side=tk.LEFT)
        
        # Command frame
        cmd_frame = tk.Frame(self.root, bg="black")
        cmd_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(cmd_frame, text="Voice Command:", fg="white", bg="black").pack(side=tk.LEFT)
        
        self.cmd_entry = tk.Entry(cmd_frame, width=50, bg="gray10", fg="white")
        self.cmd_entry.pack(side=tk.LEFT, padx=5)
        self.cmd_entry.bind("<Return>", self.process_text_command)
        
        # Buttons frame
        btn_frame = tk.Frame(self.root, bg="black")
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Control buttons
        self.listen_btn = tk.Button(btn_frame, text="Listen", 
                                  command=self.toggle_listening,
                                  bg="darkgreen", fg="white")
        self.listen_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Screenshot", 
                 command=self.take_screenshot,
                 bg="darkblue", fg="white").pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="System Info", 
                 command=self.show_system_info,
                 bg="darkorange", fg="white").pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Clear Log", 
                 command=self.clear_log,
                 bg="darkred", fg="white").pack(side=tk.LEFT, padx=5)
        
        # Log area
        self.log_area = scrolledtext.ScrolledText(self.root, 
                                                height=25, 
                                                bg="gray10", 
                                                fg="white",
                                                wrap=tk.WORD)
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # System info frame
        info_frame = tk.Frame(self.root, bg="black")
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.cpu_label = tk.Label(info_frame, text="CPU: --", fg="cyan", bg="black")
        self.cpu_label.pack(side=tk.LEFT)
        
        self.mem_label = tk.Label(info_frame, text="MEM: --", fg="cyan", bg="black")
        self.mem_label.pack(side=tk.LEFT, padx=20)
        
        # Start system monitoring
        self.update_system_info()
        
    def log_message(self, message):
        """Add message to log area"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_area.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_area.see(tk.END)
        
    def clear_log(self):
        """Clear log area"""
        self.log_area.delete(1.0, tk.END)
        
    def update_status(self, status):
        """Update status label"""
        self.status_label.config(text=f"Status: {status}")
        
    def toggle_listening(self):
        """Toggle voice listening"""
        if not self.ultron.listening:
            self.ultron.start_listening()
            self.listen_btn.config(text="Stop Listening", bg="darkred")
            self.update_status("Listening...")
        else:
            self.ultron.stop_listening()
            self.listen_btn.config(text="Listen", bg="darkgreen")
            self.update_status("Ready")
    
    def process_text_command(self, event):
        """Process text command from entry"""
        command = self.cmd_entry.get().strip()
        if command:
            self.log_message(f"User: {command}")
            self.cmd_entry.delete(0, tk.END)
            
            # Process command in background
            threading.Thread(target=self.ultron.process_command, 
                           args=(command, self.command_callback), 
                           daemon=True).start()
    
    def command_callback(self, response):
        """Callback for command responses"""
        self.log_message(f"ULTRON: {response}")
        
    def take_screenshot(self):
        """Take screenshot"""
        result = self.ultron.vision.analyze_screen()
        if result:
            self.log_message(f"Screenshot saved: {result['screenshot']}")
            if result['text']:
                self.log_message(f"OCR Text: {result['text'][:200]}...")
        else:
            self.log_message("Screenshot failed")
    
    def show_system_info(self):
        """Show system information"""
        info = self.ultron.system.get_system_info()
        self.log_message(f"System Info: CPU {info.get('cpu_percent', 0):.1f}%, "
                        f"Memory {info.get('memory_percent', 0):.1f}%, "
                        f"Admin: {info.get('admin_mode', False)}")
    
    def update_system_info(self):
        """Update system info display"""
        try:
            info = self.ultron.system.get_system_info()
            self.cpu_label.config(text=f"CPU: {info.get('cpu_percent', 0):.1f}%")
            self.mem_label.config(text=f"MEM: {info.get('memory_percent', 0):.1f}%")
        except:
            pass
        
        # Schedule next update
        self.root.after(2000, self.update_system_info)
    
    def run(self):
        """Run GUI main loop"""
        self.root.mainloop()

class UltronCore:
    """Main ULTRON system coordinator"""
    
    def __init__(self):
        # Initialize logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('ultron.log'),
                logging.StreamHandler()
            ]
        )
        
        # Initialize components
        self.ai = LocalAI()
        self.voice = VoiceProcessor()
        self.vision = VisionSystem()
        self.system = SystemController()
        self.files = FileManager()
        
        # Control variables
        self.listening = False
        self.running = True
        
        # Initialize AI
        logging.info("Initializing ULTRON Local AI...")
        self.ai.initialize()
        
    def start_listening(self):
        """Start voice listening loop"""
        self.listening = True
        threading.Thread(target=self.voice_loop, daemon=True).start()
        
    def stop_listening(self):
        """Stop voice listening"""
        self.listening = False
        
    def voice_loop(self):
        """Main voice listening loop"""
        while self.listening and self.running:
            try:
                command = self.voice.listen_once(timeout=2)
                if command:
                    threading.Thread(target=self.process_command, 
                                   args=(command,), daemon=True).start()
            except Exception as e:
                logging.error(f"Voice loop error: {e}")
                time.sleep(1)
    
    def process_command(self, command, callback=None):
        """Process voice or text command"""
        try:
            command = command.lower().strip()
            response = ""
            
            # System commands
            if "screenshot" in command or "capture screen" in command:
                result = self.vision.analyze_screen()
                if result and result['text']:
                    response = f"Screenshot taken. Found text: {result['text'][:100]}..."
                else:
                    response = "Screenshot taken but no text found."
                    
            elif "system info" in command or "status" in command:
                info = self.system.get_system_info()
                response = f"CPU at {info.get('cpu_percent', 0):.1f}%, Memory at {info.get('memory_percent', 0):.1f}%"
                
            elif "processes" in command or "running" in command:
                processes = self.system.list_processes(5)
                if processes:
                    top_proc = processes[0]
                    response = f"Top process: {top_proc['name']} using {top_proc.get('cpu_percent', 0):.1f}% CPU"
                else:
                    response = "Unable to get process information"
                    
            elif "sort files" in command:
                result = self.files.sort_directory(".")
                if "error" not in result:
                    response = f"Sorted {result.get('total_files', 0)} files into categories"
                else:
                    response = f"File sorting failed: {result['error']}"
                    
            elif "open" in command:
                app_name = command.replace("open", "").strip()
                result = self.system.execute_command(app_name)
                response = result
                
            elif "time" in command:
                current_time = datetime.now().strftime("%I:%M %p")
                response = f"The current time is {current_time}"
                
            elif "date" in command:
                current_date = datetime.now().strftime("%A, %B %d, %Y")
                response = f"Today is {current_date}"
                
            else:
                # Use local AI for general conversation
                response = self.ai.generate_response(command)
            
            # Speak response
            self.voice.speak(response)
            
            # Call callback if provided (for GUI)
            if callback:
                callback(response)
                
            logging.info(f"Processed: {command} -> {response}")
            
        except Exception as e:
            error_msg = f"Error processing command: {e}"
            logging.error(error_msg)
            self.voice.speak("Sorry, I encountered an error processing your command.")
            if callback:
                callback(error_msg)
    
    def run_console(self):
        """Run console interface"""
        print("ULTRON Local AI Assistant")
        print("=" * 40)
        print("Commands: screenshot, system info, processes, sort files, open <app>, time, date")
        print("Type 'quit' to exit")
        print()
        
        while self.running:
            try:
                command = input("ULTRON> ").strip()
                
                if command.lower() in ['quit', 'exit']:
                    break
                    
                if command:
                    self.process_command(command)
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                logging.error(f"Console error: {e}")
        
        print("ULTRON shutting down...")
        self.running = False

def main():
    """Main entry point"""
    print("Starting ULTRON Local AI Assistant...")
    
    # Create ULTRON instance
    ultron = UltronCore()
    
    # Choose interface
    if len(sys.argv) > 1 and sys.argv[1] == "--console":
        ultron.run_console()
    else:
        # Launch GUI
        gui = UltronGUI(ultron)
        try:
            gui.run()
        except KeyboardInterrupt:
            pass
        finally:
            ultron.running = False

if __name__ == "__main__":
    main()
