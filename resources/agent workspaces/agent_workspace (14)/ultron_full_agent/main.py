#!/usr/bin/env python3
"""
ULTRON - Complete AI Agent with Full PC Control
Real-time audio + Advanced system automation + File management + App control
"""

import os
import sys
import json
import time
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import queue
import psutil
import numpy as np
import sounddevice as sd
import speech_recognition as sr
import pyttsx3
import pyautogui
import pyperclip
from PIL import Image, ImageTk, ImageGrab
import logging
import webbrowser
from pathlib import Path
import asyncio
import ctypes
import webrtcvad
import collections
import wave
import io
import shutil
import glob
import zipfile
import platform

# Enhanced configuration for D:\ULTRON structure
ULTRON_ROOT = r"D:\ULTRON"
CONFIG_PATH = os.path.join(ULTRON_ROOT, "config.json")
MODEL_DIR = os.path.join(ULTRON_ROOT, "models")
CORE_DIR = os.path.join(ULTRON_ROOT, "core")
ASSETS_DIR = os.path.join(ULTRON_ROOT, "assets")
LOG_DIR = os.path.join(ULTRON_ROOT, "logs")
WEB_DIR = os.path.join(ULTRON_ROOT, "web")
SCRIPTS_DIR = os.path.join(ULTRON_ROOT, "scripts")

# Real-time audio settings
SAMPLE_RATE = 16000
CHUNK_DURATION_MS = 30
CHUNK_SIZE = int(SAMPLE_RATE * CHUNK_DURATION_MS / 1000)
WAKE_WORDS = ["ultron", "hello ultron", "hey ultron", "speak", "ultra"]

# Create directories if missing
for directory in [ULTRON_ROOT, MODEL_DIR, CORE_DIR, ASSETS_DIR, LOG_DIR, WEB_DIR, SCRIPTS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Setup logging
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "ultron_agent.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_info(message):
    logging.info(message)
    print(f"[ULTRON] {message}")

def log_error(message):
    logging.error(message)
    print(f"[ERROR] {message}")

class RealTimeAudioProcessor:
    """Real-time audio processing with voice activity detection"""
    
    def __init__(self, callback=None):
        self.callback = callback
        self.is_running = False
        self.audio_queue = queue.Queue()
        self.vad = webrtcvad.Vad(2)
        self.sample_rate = SAMPLE_RATE
        self.frame_duration = CHUNK_DURATION_MS
        self.frame_size = CHUNK_SIZE
        
        # Voice activity detection
        self.ring_buffer = collections.deque(maxlen=50)
        self.triggered = False
        self.voiced_frames = []
        self.silence_threshold = 20
        
        # Speech recognition
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
    def start_stream(self):
        """Start real-time audio stream"""
        self.is_running = True
        
        def audio_callback(indata, frames, time, status):
            if status:
                log_error(f"Audio callback status: {status}")
            
            audio_data = (indata[:, 0] * 32767).astype(np.int16)
            self.audio_queue.put(audio_data.tobytes())
        
        try:
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.float32,
                blocksize=self.frame_size,
                callback=audio_callback
            )
            self.stream.start()
            
            self.processing_thread = threading.Thread(target=self._process_audio_stream, daemon=True)
            self.processing_thread.start()
            
            log_info("Real-time audio stream started")
            return True
            
        except Exception as e:
            log_error(f"Failed to start audio stream: {e}")
            return False
    
    def stop_stream(self):
        """Stop audio stream"""
        self.is_running = False
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
        log_info("Audio stream stopped")
    
    def _process_audio_stream(self):
        """Process incoming audio stream for voice activity"""
        while self.is_running:
            try:
                if not self.audio_queue.empty():
                    audio_chunk = self.audio_queue.get()
                    
                    is_speech = self.vad.is_speech(audio_chunk, self.sample_rate)
                    
                    self.ring_buffer.append((audio_chunk, is_speech))
                    
                    if not self.triggered:
                        num_voiced = len([f for f, speech in self.ring_buffer if speech])
                        if num_voiced > 0.5 * self.ring_buffer.maxlen:
                            self.triggered = True
                            self.voiced_frames = [f for f, s in self.ring_buffer]
                            self.ring_buffer.clear()
                            if self.callback:
                                self.callback("voice_detected", None)
                    else:
                        self.voiced_frames.append(audio_chunk)
                        
                        if not is_speech:
                            self.silence_threshold -= 1
                        else:
                            self.silence_threshold = 20
                        
                        if self.silence_threshold <= 0:
                            self._process_voice_command()
                            self.triggered = False
                            self.silence_threshold = 20
                            self.voiced_frames = []
                
                time.sleep(0.01)
                
            except Exception as e:
                log_error(f"Audio processing error: {e}")
    
    def _process_voice_command(self):
        """Process collected voice frames as a command"""
        try:
            audio_data = b''.join(self.voiced_frames)
            
            audio_io = io.BytesIO()
            with wave.open(audio_io, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(audio_data)
            
            audio_io.seek(0)
            
            with sr.AudioFile(audio_io) as source:
                audio = self.recognizer.record(source)
            
            try:
                command = self.recognizer.recognize_google(audio, language='en-US')
                log_info(f"Voice command detected: {command}")
                
                if self.callback:
                    self.callback("command_recognized", command)
                    
            except sr.UnknownValueError:
                log_info("Voice detected but no speech recognized")
            except sr.RequestError as e:
                log_error(f"Speech recognition error: {e}")
                
        except Exception as e:
            log_error(f"Voice command processing error: {e}")

class AdvancedSystemController:
    """Advanced system control with full PC automation"""
    
    def __init__(self):
        # Set up PyAutoGUI
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
        # Common application paths
        self.app_paths = {
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'paint': 'mspaint.exe',
            'cmd': 'cmd.exe',
            'powershell': 'powershell.exe',
            'explorer': 'explorer.exe',
            'chrome': self._find_chrome_path(),
            'firefox': self._find_firefox_path(),
            'vscode': self._find_vscode_path(),
            'word': self._find_office_app('WINWORD.EXE'),
            'excel': self._find_office_app('EXCEL.EXE'),
            'powerpoint': self._find_office_app('POWERPNT.EXE')
        }
        
    def _find_chrome_path(self):
        """Find Chrome installation path"""
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERNAME'))
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None
    
    def _find_firefox_path(self):
        """Find Firefox installation path"""
        possible_paths = [
            r"C:\Program Files\Mozilla Firefox\firefox.exe",
            r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None
    
    def _find_vscode_path(self):
        """Find VS Code installation path"""
        possible_paths = [
            r"C:\Users\{}\AppData\Local\Programs\Microsoft VS Code\Code.exe".format(os.getenv('USERNAME')),
            r"C:\Program Files\Microsoft VS Code\Code.exe",
            r"C:\Program Files (x86)\Microsoft VS Code\Code.exe"
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None
    
    def _find_office_app(self, app_name):
        """Find Microsoft Office application"""
        possible_paths = [
            f"C:\\Program Files\\Microsoft Office\\root\\Office16\\{app_name}",
            f"C:\\Program Files (x86)\\Microsoft Office\\root\\Office16\\{app_name}",
            f"C:\\Program Files\\Microsoft Office\\Office16\\{app_name}",
            f"C:\\Program Files (x86)\\Microsoft Office\\Office16\\{app_name}"
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None
    
    def open_application(self, app_name, *args):
        """Open an application with optional arguments"""
        try:
            app_name = app_name.lower()
            
            if app_name in self.app_paths and self.app_paths[app_name]:
                if args:
                    subprocess.Popen([self.app_paths[app_name]] + list(args))
                else:
                    subprocess.Popen(self.app_paths[app_name])
                return f"Opened {app_name}"
            else:
                # Try to open by name directly
                subprocess.Popen(app_name)
                return f"Opened {app_name}"
                
        except Exception as e:
            return f"Failed to open {app_name}: {str(e)}"
    
    def create_file(self, file_path, content=""):
        """Create a new file with optional content"""
        try:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"Created file: {file_path}"
        except Exception as e:
            return f"Failed to create file: {str(e)}"
    
    def edit_file(self, file_path, new_content=None, append_content=None):
        """Edit an existing file"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return f"File not found: {file_path}"
            
            if new_content is not None:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                return f"File content replaced: {file_path}"
            
            if append_content is not None:
                with open(file_path, 'a', encoding='utf-8') as f:
                    f.write(append_content)
                return f"Content appended to: {file_path}"
            
            return "No content specified for editing"
            
        except Exception as e:
            return f"Failed to edit file: {str(e)}"
    
    def read_file(self, file_path):
        """Read file content"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return f"File not found: {file_path}"
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Limit output length for display
            if len(content) > 1000:
                content = content[:1000] + "... (truncated)"
            
            return f"File content:\n{content}"
            
        except Exception as e:
            return f"Failed to read file: {str(e)}"
    
    def delete_file(self, file_path):
        """Delete a file"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return f"File not found: {file_path}"
            
            file_path.unlink()
            return f"Deleted file: {file_path}"
            
        except Exception as e:
            return f"Failed to delete file: {str(e)}"
    
    def copy_file(self, source_path, dest_path):
        """Copy a file"""
        try:
            source_path = Path(source_path)
            dest_path = Path(dest_path)
            
            if not source_path.exists():
                return f"Source file not found: {source_path}"
            
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, dest_path)
            
            return f"Copied {source_path} to {dest_path}"
            
        except Exception as e:
            return f"Failed to copy file: {str(e)}"
    
    def move_file(self, source_path, dest_path):
        """Move a file"""
        try:
            source_path = Path(source_path)
            dest_path = Path(dest_path)
            
            if not source_path.exists():
                return f"Source file not found: {source_path}"
            
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source_path), str(dest_path))
            
            return f"Moved {source_path} to {dest_path}"
            
        except Exception as e:
            return f"Failed to move file: {str(e)}"
    
    def list_files(self, directory_path, pattern="*"):
        """List files in a directory"""
        try:
            directory_path = Path(directory_path)
            
            if not directory_path.exists():
                return f"Directory not found: {directory_path}"
            
            files = list(directory_path.glob(pattern))
            files.sort()
            
            if not files:
                return f"No files found matching '{pattern}' in {directory_path}"
            
            file_list = "\n".join([f"  {f.name}" for f in files[:20]])  # Limit to 20 files
            
            if len(files) > 20:
                file_list += f"\n  ... and {len(files) - 20} more files"
            
            return f"Files in {directory_path}:\n{file_list}"
            
        except Exception as e:
            return f"Failed to list files: {str(e)}"
    
    def create_folder(self, folder_path):
        """Create a new folder"""
        try:
            folder_path = Path(folder_path)
            folder_path.mkdir(parents=True, exist_ok=True)
            return f"Created folder: {folder_path}"
        except Exception as e:
            return f"Failed to create folder: {str(e)}"
    
    def type_text(self, text):
        """Type text using keyboard automation"""
        try:
            pyautogui.write(text)
            return f"Typed: {text}"
        except Exception as e:
            return f"Failed to type text: {str(e)}"
    
    def press_key(self, key):
        """Press a keyboard key"""
        try:
            pyautogui.press(key)
            return f"Pressed key: {key}"
        except Exception as e:
            return f"Failed to press key: {str(e)}"
    
    def key_combination(self, *keys):
        """Press a combination of keys"""
        try:
            pyautogui.hotkey(*keys)
            return f"Pressed key combination: {'+'.join(keys)}"
        except Exception as e:
            return f"Failed to press key combination: {str(e)}"
    
    def click_mouse(self, x=None, y=None, button='left'):
        """Click mouse at position or current position"""
        try:
            if x is not None and y is not None:
                pyautogui.click(x, y, button=button)
                return f"Clicked {button} mouse button at ({x}, {y})"
            else:
                pyautogui.click(button=button)
                return f"Clicked {button} mouse button at current position"
        except Exception as e:
            return f"Failed to click mouse: {str(e)}"
    
    def get_mouse_position(self):
        """Get current mouse position"""
        try:
            x, y = pyautogui.position()
            return f"Mouse position: ({x}, {y})"
        except Exception as e:
            return f"Failed to get mouse position: {str(e)}"
    
    def take_screenshot(self, save_path=None):
        """Take a screenshot"""
        try:
            screenshot = pyautogui.screenshot()
            
            if save_path is None:
                timestamp = int(time.time())
                save_path = os.path.join(ASSETS_DIR, f"screenshot_{timestamp}.png")
            
            screenshot.save(save_path)
            return f"Screenshot saved to: {save_path}"
        except Exception as e:
            return f"Failed to take screenshot: {str(e)}"
    
    def run_command(self, command):
        """Run a system command"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if len(output) > 500:
                    output = output[:500] + "... (truncated)"
                return f"Command executed successfully:\n{output}"
            else:
                error = result.stderr.strip()
                return f"Command failed: {error}"
                
        except subprocess.TimeoutExpired:
            return "Command timed out after 30 seconds"
        except Exception as e:
            return f"Failed to run command: {str(e)}"
    
    def get_clipboard(self):
        """Get clipboard content"""
        try:
            content = pyperclip.paste()
            if len(content) > 500:
                content = content[:500] + "... (truncated)"
            return f"Clipboard content: {content}"
        except Exception as e:
            return f"Failed to get clipboard: {str(e)}"
    
    def set_clipboard(self, text):
        """Set clipboard content"""
        try:
            pyperclip.copy(text)
            return f"Clipboard set to: {text}"
        except Exception as e:
            return f"Failed to set clipboard: {str(e)}"

class AdvancedAIBrain:
    """Advanced AI brain with full system control capabilities"""
    
    def __init__(self, config):
        self.config = config
        self.conversation_context = []
        self.system_controller = AdvancedSystemController()
        
        # Enhanced command patterns
        self.command_patterns = {
            'app_control': {
                'open': ['open', 'launch', 'start', 'run'],
                'close': ['close', 'exit', 'quit'],
                'apps': ['notepad', 'calculator', 'paint', 'cmd', 'powershell', 'explorer', 
                        'chrome', 'firefox', 'vscode', 'word', 'excel', 'powerpoint', 'browser']
            },
            'file_operations': {
                'create': ['create', 'make', 'new'],
                'edit': ['edit', 'modify', 'change', 'update'],
                'read': ['read', 'show', 'display', 'open'],
                'delete': ['delete', 'remove', 'erase'],
                'copy': ['copy', 'duplicate'],
                'move': ['move', 'relocate'],
                'list': ['list', 'show files', 'directory'],
                'folder': ['folder', 'directory', 'create folder']
            },
            'keyboard_mouse': {
                'type': ['type', 'write', 'input'],
                'press': ['press', 'key', 'hit'],
                'click': ['click', 'mouse'],
                'position': ['mouse position', 'cursor position'],
                'copy_text': ['copy', 'ctrl c'],
                'paste_text': ['paste', 'ctrl v'],
                'save': ['save', 'ctrl s'],
                'undo': ['undo', 'ctrl z']
            },
            'system_info': {
                'status': ['status', 'report', 'health', 'system info'],
                'processes': ['processes', 'tasks', 'running'],
                'memory': ['memory', 'ram'],
                'cpu': ['cpu', 'processor'],
                'disk': ['disk', 'storage', 'space']
            }
        }
        
        self.responses = {
            "greeting": [
                "ULTRON advanced AI agent online. Full system control ready.",
                "AI agent initialized. I can control your PC, manage files, and automate tasks.",
                "ULTRON here with complete system access. What would you like me to do?",
                "Advanced automation ready. I can open apps, manage files, and control your system."
            ],
            "success": [
                "Task completed successfully.",
                "Operation finished.",
                "Done as requested.",
                "Task executed successfully."
            ],
            "error": [
                "I encountered an issue with that command.",
                "Something went wrong. Please try rephrasing.",
                "Command execution failed.",
                "I couldn't complete that task."
            ]
        }
    
    def process_command(self, command):
        """Process voice/text commands with advanced system control"""
        original_command = command
        command = command.lower().strip()
        
        # Add to conversation context
        self.conversation_context.append(command)
        if len(self.conversation_context) > 10:
            self.conversation_context.pop(0)
        
        # Remove wake words
        for wake_word in WAKE_WORDS:
            if wake_word in command:
                command = command.replace(wake_word, "").strip()
                break
        
        if not command:
            return np.random.choice(self.responses["greeting"])
        
        try:
            # App control commands
            if self._matches_pattern(command, self.command_patterns['app_control']['open']):
                return self._handle_app_open(command)
            
            # File operations
            if self._matches_pattern(command, ['create file', 'new file', 'make file']):
                return self._handle_file_create(command)
            
            if self._matches_pattern(command, ['edit file', 'modify file', 'change file']):
                return self._handle_file_edit(command)
            
            if self._matches_pattern(command, ['read file', 'show file', 'display file']):
                return self._handle_file_read(command)
            
            if self._matches_pattern(command, ['delete file', 'remove file']):
                return self._handle_file_delete(command)
            
            if self._matches_pattern(command, ['copy file']):
                return self._handle_file_copy(command)
            
            if self._matches_pattern(command, ['move file']):
                return self._handle_file_move(command)
            
            if self._matches_pattern(command, ['list files', 'show files', 'directory']):
                return self._handle_file_list(command)
            
            if self._matches_pattern(command, ['create folder', 'make folder', 'new folder']):
                return self._handle_folder_create(command)
            
            # Keyboard and mouse control
            if self._matches_pattern(command, ['type', 'write']):
                return self._handle_type_text(command)
            
            if self._matches_pattern(command, ['press key', 'press', 'hit key']):
                return self._handle_key_press(command)
            
            if self._matches_pattern(command, ['click', 'mouse click']):
                return self._handle_mouse_click(command)
            
            if self._matches_pattern(command, ['copy text', 'ctrl c']):
                return self.system_controller.key_combination('ctrl', 'c')
            
            if self._matches_pattern(command, ['paste', 'ctrl v']):
                return self.system_controller.key_combination('ctrl', 'v')
            
            if self._matches_pattern(command, ['save', 'ctrl s']):
                return self.system_controller.key_combination('ctrl', 's')
            
            if self._matches_pattern(command, ['undo', 'ctrl z']):
                return self.system_controller.key_combination('ctrl', 'z')
            
            # System information
            if self._matches_pattern(command, ['status', 'system info', 'health']):
                return self._handle_system_status()
            
            if self._matches_pattern(command, ['screenshot', 'capture screen']):
                return self.system_controller.take_screenshot()
            
            if self._matches_pattern(command, ['clipboard', 'show clipboard']):
                return self.system_controller.get_clipboard()
            
            if self._matches_pattern(command, ['mouse position', 'cursor position']):
                return self.system_controller.get_mouse_position()
            
            # Time and basic queries
            if any(word in command for word in ["time", "date", "clock"]):
                current_time = time.strftime('%Y-%m-%d %H:%M:%S')
                return f"Current time: {current_time}"
            
            # Web search
            if "search" in command:
                search_term = command.replace("search", "").replace("for", "").strip()
                if search_term:
                    webbrowser.open(f"https://google.com/search?q={search_term}")
                    return f"Searching for: {search_term}"
                else:
                    return "What would you like me to search for?"
            
            # Greetings
            if any(word in command for word in ["hello", "hi", "hey", "greetings"]):
                return np.random.choice(self.responses["greeting"])
            
            # Default response
            return f"I understand you want to: '{original_command}'. Please be more specific about the action and target."
            
        except Exception as e:
            log_error(f"Command processing error: {e}")
            return f"Error processing command: {str(e)}"
    
    def _matches_pattern(self, command, patterns):
        """Check if command matches any pattern"""
        return any(pattern in command for pattern in patterns)
    
    def _handle_app_open(self, command):
        """Handle application opening commands"""
        for app in self.command_patterns['app_control']['apps']:
            if app in command:
                return self.system_controller.open_application(app)
        
        # Extract app name after "open"
        words = command.split()
        if 'open' in words:
            idx = words.index('open')
            if idx + 1 < len(words):
                app_name = words[idx + 1]
                return self.system_controller.open_application(app_name)
        
        return "Please specify which application to open."
    
    def _handle_file_create(self, command):
        """Handle file creation commands"""
        # Try to extract filename from command
        words = command.split()
        filename = None
        
        # Look for filename after common keywords
        keywords = ['create', 'make', 'new', 'file']
        for i, word in enumerate(words):
            if word in keywords and i + 1 < len(words):
                filename = words[i + 1]
                break
        
        if not filename:
            return "Please specify a filename to create."
        
        # If no extension, default to .txt
        if '.' not in filename:
            filename += '.txt'
        
        # Create in ULTRON directory by default
        file_path = os.path.join(ULTRON_ROOT, filename)
        
        return self.system_controller.create_file(file_path, "# New file created by ULTRON\n")
    
    def _handle_file_edit(self, command):
        """Handle file editing commands"""
        return "File editing requires specific filename and content. Use: 'edit file filename.txt with content'"
    
    def _handle_file_read(self, command):
        """Handle file reading commands"""
        words = command.split()
        filename = None
        
        keywords = ['read', 'show', 'display', 'file']
        for i, word in enumerate(words):
            if word in keywords and i + 1 < len(words):
                filename = words[i + 1]
                break
        
        if not filename:
            return "Please specify a filename to read."
        
        file_path = os.path.join(ULTRON_ROOT, filename)
        return self.system_controller.read_file(file_path)
    
    def _handle_file_delete(self, command):
        """Handle file deletion commands"""
        words = command.split()
        filename = None
        
        keywords = ['delete', 'remove', 'file']
        for i, word in enumerate(words):
            if word in keywords and i + 1 < len(words):
                filename = words[i + 1]
                break
        
        if not filename:
            return "Please specify a filename to delete."
        
        file_path = os.path.join(ULTRON_ROOT, filename)
        return self.system_controller.delete_file(file_path)
    
    def _handle_file_copy(self, command):
        """Handle file copying commands"""
        return "File copying requires source and destination. Use: 'copy file source.txt to destination.txt'"
    
    def _handle_file_move(self, command):
        """Handle file moving commands"""
        return "File moving requires source and destination. Use: 'move file source.txt to destination.txt'"
    
    def _handle_file_list(self, command):
        """Handle file listing commands"""
        directory = ULTRON_ROOT
        
        # Check if specific directory mentioned
        if 'in' in command:
            words = command.split()
            try:
                idx = words.index('in')
                if idx + 1 < len(words):
                    directory = words[idx + 1]
            except ValueError:
                pass
        
        return self.system_controller.list_files(directory)
    
    def _handle_folder_create(self, command):
        """Handle folder creation commands"""
        words = command.split()
        foldername = None
        
        keywords = ['create', 'make', 'new', 'folder', 'directory']
        for i, word in enumerate(words):
            if word in keywords and i + 1 < len(words):
                foldername = words[i + 1]
                break
        
        if not foldername:
            return "Please specify a folder name to create."
        
        folder_path = os.path.join(ULTRON_ROOT, foldername)
        return self.system_controller.create_folder(folder_path)
    
    def _handle_type_text(self, command):
        """Handle text typing commands"""
        # Extract text after "type" or "write"
        keywords = ['type', 'write']
        for keyword in keywords:
            if keyword in command:
                text = command.split(keyword, 1)[1].strip()
                if text:
                    return self.system_controller.type_text(text)
        
        return "Please specify what text to type."
    
    def _handle_key_press(self, command):
        """Handle key press commands"""
        # Extract key name
        words = command.split()
        key = None
        
        keywords = ['press', 'key', 'hit']
        for i, word in enumerate(words):
            if word in keywords and i + 1 < len(words):
                key = words[i + 1]
                break
        
        if not key:
            return "Please specify which key to press."
        
        return self.system_controller.press_key(key)
    
    def _handle_mouse_click(self, command):
        """Handle mouse click commands"""
        return self.system_controller.click_mouse()
    
    def _handle_system_status(self):
        """Handle system status requests"""
        try:
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage('C:' if os.name == 'nt' else '/').percent
            
            return f"System Status - CPU: {cpu}%, Memory: {memory}%, Disk: {disk}%"
        except Exception as e:
            return f"Failed to get system status: {str(e)}"

class FullAgentUltronUI:
    """Complete AI Agent UI with full PC control capabilities"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ULTRON - Complete AI Agent")
        self.root.geometry("1600x1000")
        self.root.configure(bg='#0a0a0a')
        
        # Initialize components
        self.config = self.load_config()
        self.ai_brain = AdvancedAIBrain(self.config)
        self.voice_engine = self.init_voice()
        self.audio_processor = RealTimeAudioProcessor(callback=self.audio_callback)
        
        # UI State
        self.conversation_history = []
        self.is_listening = False
        self.command_count = 0
        
        self.create_agent_ui()
        self.start_background_tasks()
        
    def load_config(self):
        """Load or create configuration"""
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                return json.load(f)
        
        default_config = {
            "voice": {"enabled": True, "rate": 180, "volume": 0.9},
            "audio": {"real_time": True, "sensitivity": 0.5, "auto_respond": True},
            "ai": {"local_mode": True, "context_memory": 10},
            "automation": {"safe_mode": True, "confirm_actions": False},
            "interface": {"theme": "agent", "animations": True}
        }
        
        with open(CONFIG_PATH, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def init_voice(self):
        """Initialize text-to-speech"""
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', self.config.get('voice', {}).get('rate', 180))
            engine.setProperty('volume', self.config.get('voice', {}).get('volume', 0.9))
            return engine
        except Exception as e:
            log_error(f"Voice engine init failed: {e}")
            return None
    
    def create_agent_ui(self):
        """Create AI agent interface"""
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#0a0a0a')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Top section - Agent status
        top_frame = tk.Frame(main_frame, bg='#1a1a2e', relief=tk.RAISED, bd=2)
        top_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title and status
        title_frame = tk.Frame(top_frame, bg='#16213e')
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            title_frame, 
            text="ULTRON - COMPLETE AI AGENT", 
            font=("Orbitron", 32, "bold"),
            fg='#00ff41', 
            bg='#16213e'
        ).pack()
        
        status_frame = tk.Frame(title_frame, bg='#16213e')
        status_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            status_frame,
            text="🤖 FULL PC CONTROL ENABLED",
            font=("Courier", 16, "bold"),
            fg='#f39c12',
            bg='#16213e'
        ).pack(side=tk.LEFT)
        
        self.agent_status = tk.Label(
            status_frame,
            text="🎤 Real-Time Audio Ready",
            font=("Courier", 14),
            fg='#27ae60',
            bg='#16213e'
        )
        self.agent_status.pack(side=tk.RIGHT)
        
        # Middle section - Four panels
        middle_frame = tk.Frame(main_frame, bg='#0a0a0a')
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Left panel - System control
        left_panel = tk.Frame(middle_frame, bg='#1a1a2e', width=350)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        left_panel.pack_propagate(False)
        
        self.create_system_control_panel(left_panel)
        
        # Center-left panel - Conversation
        center_left_panel = tk.Frame(middle_frame, bg='#16213e')
        center_left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        self.create_conversation_panel(center_left_panel)
        
        # Center-right panel - File operations
        center_right_panel = tk.Frame(middle_frame, bg='#1a1a2e', width=350)
        center_right_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        center_right_panel.pack_propagate(False)
        
        self.create_file_operations_panel(center_right_panel)
        
        # Right panel - Automation controls
        right_panel = tk.Frame(middle_frame, bg='#16213e', width=350)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)
        
        self.create_automation_panel(right_panel)
        
        # Bottom section - Command input
        bottom_frame = tk.Frame(main_frame, bg='#e67e22', relief=tk.RAISED, bd=2)
        bottom_frame.pack(fill=tk.X)
        
        self.create_command_input_panel(bottom_frame)
    
    def create_system_control_panel(self, parent):
        """Create system control panel"""
        tk.Label(
            parent, 
            text="🖥️ SYSTEM CONTROL", 
            font=("Orbitron", 16, "bold"),
            fg='#00ff41', 
            bg='#1a1a2e'
        ).pack(pady=15)
        
        # System status
        self.status_vars = {
            'cpu': tk.StringVar(value="CPU: ---%"),
            'memory': tk.StringVar(value="Memory: ---%"),
            'disk': tk.StringVar(value="Disk: ---%"),
            'audio': tk.StringVar(value="Audio: Ready"),
            'commands': tk.StringVar(value="Commands: 0")
        }
        
        for key, var in self.status_vars.items():
            frame = tk.Frame(parent, bg='#1a1a2e')
            frame.pack(fill=tk.X, padx=15, pady=2)
            
            tk.Label(
                frame,
                text="●",
                font=("Arial", 12),
                fg='#00ff41',
                bg='#1a1a2e'
            ).pack(side=tk.LEFT, padx=(0, 10))
            
            tk.Label(
                frame,
                textvariable=var,
                font=("Courier", 11),
                fg='#ecf0f1',
                bg='#1a1a2e',
                anchor='w'
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Quick system actions
        tk.Label(
            parent, 
            text="⚡ QUICK ACTIONS", 
            font=("Orbitron", 14, "bold"),
            fg='#00ff41', 
            bg='#1a1a2e'
        ).pack(pady=(20, 10))
        
        system_actions = [
            ("📸 Screenshot", lambda: self.execute_command("take screenshot")),
            ("📁 Open Explorer", lambda: self.execute_command("open explorer")),
            ("🌐 Open Browser", lambda: self.execute_command("open chrome")),
            ("📝 Open Notepad", lambda: self.execute_command("open notepad")),
            ("🧮 Calculator", lambda: self.execute_command("open calculator")),
            ("💻 Command Prompt", lambda: self.execute_command("open cmd"))
        ]
        
        for text, command in system_actions:
            btn = tk.Button(
                parent,
                text=text,
                command=command,
                bg='#3498db',
                fg='white',
                font=("Courier", 10, "bold"),
                relief=tk.FLAT,
                padx=10,
                pady=5
            )
            btn.pack(fill=tk.X, padx=15, pady=2)
    
    def create_conversation_panel(self, parent):
        """Create conversation panel"""
        header_frame = tk.Frame(parent, bg='#16213e')
        header_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            header_frame, 
            text="💬 AI CONVERSATION", 
            font=("Orbitron", 16, "bold"),
            fg='#00ff41', 
            bg='#16213e'
        ).pack()
        
        # Voice activity indicator
        self.voice_activity = tk.Label(
            header_frame,
            text="🎤 Ready for commands...",
            font=("Courier", 12),
            fg='#27ae60',
            bg='#16213e'
        )
        self.voice_activity.pack(pady=5)
        
        # Conversation display
        self.conversation_text = scrolledtext.ScrolledText(
            parent,
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg='#2c3e50',
            fg='#ecf0f1',
            font=("Consolas", 11),
            insertbackground='#3498db'
        )
        self.conversation_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Configure tags
        self.conversation_text.tag_configure("user", foreground="#3498db", font=("Consolas", 11, "bold"))
        self.conversation_text.tag_configure("ultron", foreground="#00ff41", font=("Consolas", 11, "bold"))
        self.conversation_text.tag_configure("system", foreground="#e67e22", font=("Consolas", 10, "italic"))
        self.conversation_text.tag_configure("voice", foreground="#f39c12", font=("Consolas", 11, "bold"))
        
        self.add_to_conversation("ULTRON", "Complete AI Agent online. I can control your PC, manage files, and automate tasks. What would you like me to do?", "ultron")
    
    def create_file_operations_panel(self, parent):
        """Create file operations panel"""
        tk.Label(
            parent, 
            text="📁 FILE OPERATIONS", 
            font=("Orbitron", 16, "bold"),
            fg='#00ff41', 
            bg='#1a1a2e'
        ).pack(pady=15)
        
        # File operation buttons
        file_operations = [
            ("📄 Create File", lambda: self.show_file_dialog("create")),
            ("✏️ Edit File", lambda: self.show_file_dialog("edit")),
            ("👁️ Read File", lambda: self.show_file_dialog("read")),
            ("🗑️ Delete File", lambda: self.show_file_dialog("delete")),
            ("📋 Copy File", lambda: self.show_file_dialog("copy")),
            ("📦 Move File", lambda: self.show_file_dialog("move")),
            ("📂 List Files", lambda: self.execute_command("list files")),
            ("📁 New Folder", lambda: self.show_file_dialog("folder"))
        ]
        
        for text, command in file_operations:
            btn = tk.Button(
                parent,
                text=text,
                command=command,
                bg='#9b59b6',
                fg='white',
                font=("Courier", 10, "bold"),
                relief=tk.FLAT,
                padx=10,
                pady=5
            )
            btn.pack(fill=tk.X, padx=15, pady=2)
        
        # File browser
        tk.Label(
            parent, 
            text="📂 QUICK BROWSE", 
            font=("Orbitron", 12, "bold"),
            fg='#00ff41', 
            bg='#1a1a2e'
        ).pack(pady=(15, 5))
        
        self.file_listbox = tk.Listbox(
            parent,
            bg='#2c3e50',
            fg='#ecf0f1',
            font=("Courier", 9),
            height=8
        )
        self.file_listbox.pack(fill=tk.X, padx=15, pady=5)
        
        # Refresh file list
        self.refresh_file_list()
    
    def create_automation_panel(self, parent):
        """Create automation control panel"""
        tk.Label(
            parent, 
            text="🤖 AUTOMATION", 
            font=("Orbitron", 16, "bold"),
            fg='#00ff41', 
            bg='#16213e'
        ).pack(pady=15)
        
        # Audio controls
        self.audio_toggle_btn = tk.Button(
            parent,
            text="🎤 START LISTENING",
            command=self.toggle_realtime_audio,
            bg='#27ae60',
            fg='white',
            font=("Courier", 14, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=15
        )
        self.audio_toggle_btn.pack(fill=tk.X, padx=15, pady=10)
        
        # Keyboard automation
        tk.Label(
            parent, 
            text="⌨️ KEYBOARD CONTROL", 
            font=("Orbitron", 12, "bold"),
            fg='#00ff41', 
            bg='#16213e'
        ).pack(pady=(15, 5))
        
        keyboard_actions = [
            ("📝 Type Text", lambda: self.show_type_dialog()),
            ("🔑 Press Key", lambda: self.show_key_dialog()),
            ("📋 Copy (Ctrl+C)", lambda: self.execute_command("copy text")),
            ("📄 Paste (Ctrl+V)", lambda: self.execute_command("paste")),
            ("💾 Save (Ctrl+S)", lambda: self.execute_command("save")),
            ("↶ Undo (Ctrl+Z)", lambda: self.execute_command("undo"))
        ]
        
        for text, command in keyboard_actions:
            btn = tk.Button(
                parent,
                text=text,
                command=command,
                bg='#e74c3c',
                fg='white',
                font=("Courier", 9, "bold"),
                relief=tk.FLAT,
                padx=8,
                pady=3
            )
            btn.pack(fill=tk.X, padx=15, pady=1)
        
        # Mouse control
        tk.Label(
            parent, 
            text="🖱️ MOUSE CONTROL", 
            font=("Orbitron", 12, "bold"),
            fg='#00ff41', 
            bg='#16213e'
        ).pack(pady=(15, 5))
        
        mouse_actions = [
            ("👆 Click", lambda: self.execute_command("click")),
            ("📍 Get Position", lambda: self.execute_command("mouse position")),
            ("📋 Clipboard", lambda: self.execute_command("show clipboard"))
        ]
        
        for text, command in mouse_actions:
            btn = tk.Button(
                parent,
                text=text,
                command=command,
                bg='#f39c12',
                fg='white',
                font=("Courier", 9, "bold"),
                relief=tk.FLAT,
                padx=8,
                pady=3
            )
            btn.pack(fill=tk.X, padx=15, pady=1)
    
    def create_command_input_panel(self, parent):
        """Create command input panel"""
        input_frame = tk.Frame(parent, bg='#e67e22')
        input_frame.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(
            input_frame,
            text="🗣️ Voice Commands or ⌨️ Type Commands:",
            font=("Orbitron", 14, "bold"),
            bg='#e67e22',
            fg='white'
        ).pack(anchor='w', pady=(0, 5))
        
        entry_frame = tk.Frame(input_frame, bg='#e67e22')
        entry_frame.pack(fill=tk.X, pady=5)
        
        self.command_entry = tk.Entry(
            entry_frame,
            font=("Consolas", 14),
            bg='#2c3e50',
            fg='#ecf0f1',
            insertbackground='#3498db',
            relief=tk.FLAT,
            bd=5
        )
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))
        self.command_entry.bind('<Return>', self.process_text_command)
        
        tk.Button(
            entry_frame,
            text="🚀 EXECUTE",
            command=self.process_text_command,
            bg='#27ae60',
            fg='white',
            font=("Courier", 12, "bold"),
            relief=tk.FLAT,
            padx=25,
            pady=8
        ).pack(side=tk.RIGHT)
    
    def audio_callback(self, event_type, data):
        """Handle real-time audio events"""
        if event_type == "voice_detected":
            self.root.after(0, self.on_voice_detected)
        elif event_type == "command_recognized":
            self.root.after(0, self.on_command_recognized, data)
    
    def on_voice_detected(self):
        """Handle voice detection"""
        self.voice_activity.config(text="🗣️ Voice detected!", fg='#f39c12')
        self.agent_status.config(text="🎤 Processing Voice...", fg='#e74c3c')
    
    def on_command_recognized(self, command):
        """Handle recognized voice command"""
        self.voice_activity.config(text="🎤 Executing command...", fg='#e74c3c')
        
        self.add_to_conversation("USER", f"🎤 {command}", "voice")
        
        response = self.ai_brain.process_command(command)
        self.add_to_conversation("ULTRON", response, "ultron")
        
        if self.voice_engine:
            threading.Thread(target=self.speak_response, args=(response,), daemon=True).start()
        
        # Update command counter
        self.command_count += 1
        self.status_vars['commands'].set(f"Commands: {self.command_count}")
        
        # Reset status
        self.root.after(2000, lambda: self.voice_activity.config(text="🎤 Ready for commands...", fg='#27ae60'))
        self.root.after(2000, lambda: self.agent_status.config(text="🎤 Real-Time Audio Ready", fg='#27ae60'))
    
    def execute_command(self, command):
        """Execute a command programmatically"""
        self.add_to_conversation("USER", command, "user")
        
        response = self.ai_brain.process_command(command)
        self.add_to_conversation("ULTRON", response, "ultron")
        
        self.command_count += 1
        self.status_vars['commands'].set(f"Commands: {self.command_count}")
        
        # Refresh file list if file operation
        if any(word in command.lower() for word in ['create', 'delete', 'file', 'folder']):
            self.refresh_file_list()
    
    def process_text_command(self, event=None):
        """Process manual text command"""
        command = self.command_entry.get().strip()
        if not command:
            return
        
        self.command_entry.delete(0, tk.END)
        self.execute_command(command)
    
    def toggle_realtime_audio(self):
        """Toggle real-time audio processing"""
        if not self.is_listening:
            if self.audio_processor.start_stream():
                self.is_listening = True
                self.audio_toggle_btn.config(
                    text="🛑 STOP LISTENING",
                    bg='#e74c3c'
                )
                self.add_to_conversation("SYSTEM", "Real-time audio processing started", "system")
            else:
                self.add_to_conversation("SYSTEM", "Failed to start audio processing", "system")
        else:
            self.audio_processor.stop_stream()
            self.is_listening = False
            self.audio_toggle_btn.config(
                text="🎤 START LISTENING",
                bg='#27ae60'
            )
            self.add_to_conversation("SYSTEM", "Real-time audio processing stopped", "system")
    
    def show_file_dialog(self, operation):
        """Show file operation dialog"""
        if operation == "create":
            filename = tk.simpledialog.askstring("Create File", "Enter filename:")
            if filename:
                self.execute_command(f"create file {filename}")
        
        elif operation == "read":
            filename = filedialog.askopenfilename(title="Select file to read")
            if filename:
                self.execute_command(f"read file {filename}")
        
        elif operation == "delete":
            filename = filedialog.askopenfilename(title="Select file to delete")
            if filename:
                self.execute_command(f"delete file {filename}")
        
        elif operation == "folder":
            foldername = tk.simpledialog.askstring("Create Folder", "Enter folder name:")
            if foldername:
                self.execute_command(f"create folder {foldername}")
    
    def show_type_dialog(self):
        """Show text typing dialog"""
        text = tk.simpledialog.askstring("Type Text", "Enter text to type:")
        if text:
            self.execute_command(f"type {text}")
    
    def show_key_dialog(self):
        """Show key press dialog"""
        key = tk.simpledialog.askstring("Press Key", "Enter key to press (e.g., enter, space, tab):")
        if key:
            self.execute_command(f"press {key}")
    
    def refresh_file_list(self):
        """Refresh the file list display"""
        try:
            self.file_listbox.delete(0, tk.END)
            
            files = list(Path(ULTRON_ROOT).glob("*"))
            files.sort()
            
            for file_path in files[:20]:  # Show first 20 files
                if file_path.is_file():
                    self.file_listbox.insert(tk.END, f"📄 {file_path.name}")
                else:
                    self.file_listbox.insert(tk.END, f"📁 {file_path.name}")
                    
        except Exception as e:
            log_error(f"Failed to refresh file list: {e}")
    
    def speak_response(self, text):
        """Speak response"""
        if self.voice_engine:
            try:
                self.voice_engine.say(text)
                self.voice_engine.runAndWait()
            except Exception as e:
                log_error(f"Speech error: {e}")
    
    def add_to_conversation(self, speaker, message, tag=""):
        """Add message to conversation log"""
        self.conversation_text.config(state=tk.NORMAL)
        
        timestamp = time.strftime("%H:%M:%S")
        
        self.conversation_text.insert(tk.END, f"[{timestamp}] ")
        self.conversation_text.insert(tk.END, f"{speaker}: ", tag if tag else speaker.lower())
        self.conversation_text.insert(tk.END, f"{message}\n\n")
        
        self.conversation_text.config(state=tk.DISABLED)
        self.conversation_text.see(tk.END)
    
    def update_system_status(self):
        """Update system status"""
        try:
            cpu = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage('C:' if os.name == 'nt' else '/').percent
            
            self.status_vars['cpu'].set(f"CPU: {cpu:.1f}%")
            self.status_vars['memory'].set(f"Memory: {memory:.1f}%")
            self.status_vars['disk'].set(f"Disk: {disk:.1f}%")
            self.status_vars['audio'].set(f"Audio: {'Active' if self.is_listening else 'Ready'}")
            
        except Exception as e:
            log_error(f"Status update error: {e}")
    
    def start_background_tasks(self):
        """Start background monitoring"""
        def update_loop():
            while True:
                self.root.after(0, self.update_system_status)
                time.sleep(2)
        
        threading.Thread(target=update_loop, daemon=True).start()
    
    def run(self):
        """Start the application"""
        log_info("ULTRON Complete AI Agent starting...")
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except KeyboardInterrupt:
            log_info("ULTRON shutting down...")
        except Exception as e:
            log_error(f"Application error: {e}")
    
    def on_closing(self):
        """Handle application closing"""
        if self.is_listening:
            self.audio_processor.stop_stream()
        self.root.destroy()

def main():
    """Main entry point"""
    print("🤖 ULTRON - Complete AI Agent with Full PC Control")
    print("=" * 60)
    
    try:
        app = FullAgentUltronUI()
        app.run()
    except Exception as e:
        log_error(f"Startup error: {e}")
        print(f"Error starting ULTRON: {e}")

if __name__ == "__main__":
    main()
