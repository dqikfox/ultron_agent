#!/usr/bin/env python3
"""
ULTRON AI Integration GUI
Unified interface for MiniMax, Claude, and project automation
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import subprocess
import json
import os
import requests
from pathlib import Path

class UltronAIGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ULTRON AI Integration Hub")
        self.root.geometry("1200x800")
        
        # Load config
        self.config = self.load_config()
        
        # Setup GUI
        self.setup_gui()
        
    def load_config(self):
        try:
            with open('ultron_config.json', 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def setup_gui(self):
        # Main notebook
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Chat Tab
        self.setup_chat_tab(notebook)
        
        # Project Automation Tab
        self.setup_automation_tab(notebook)
        
        # File Manager Tab
        self.setup_file_tab(notebook)
        
        # System Monitor Tab
        self.setup_monitor_tab(notebook)
    
    def setup_chat_tab(self, notebook):
        chat_frame = ttk.Frame(notebook)
        notebook.add(chat_frame, text="AI Chat")
        
        # Model selection
        model_frame = ttk.Frame(chat_frame)
        model_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(model_frame, text="Model:").pack(side=tk.LEFT)
        self.model_var = tk.StringVar(value="MiniMax M2.1")
        model_combo = ttk.Combobox(model_frame, textvariable=self.model_var, 
                                  values=["MiniMax M2.1", "Claude 3 Haiku", "Continue Extension"])
        model_combo.pack(side=tk.LEFT, padx=5)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(chat_frame, height=20)
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Input frame
        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.chat_input = tk.Text(input_frame, height=3)
        self.chat_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        send_btn = ttk.Button(input_frame, text="Send", command=self.send_message)
        send_btn.pack(side=tk.RIGHT, padx=5)
        
        # Bind Enter key
        self.chat_input.bind('<Control-Return>', lambda e: self.send_message())
    
    def setup_automation_tab(self, notebook):
        auto_frame = ttk.Frame(notebook)
        notebook.add(auto_frame, text="Project Automation")
        
        # Quick actions
        actions_frame = ttk.LabelFrame(auto_frame, text="Quick Actions")
        actions_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(actions_frame, text="Run Tests", command=self.run_tests).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Update Dependencies", command=self.update_deps).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Git Status", command=self.git_status).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Start ULTRON", command=self.start_ultron).pack(side=tk.LEFT, padx=5)
        
        # Automation log
        self.auto_log = scrolledtext.ScrolledText(auto_frame, height=25)
        self.auto_log.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def setup_file_tab(self, notebook):
        file_frame = ttk.Frame(notebook)
        notebook.add(file_frame, text="File Manager")
        
        # File operations
        ops_frame = ttk.Frame(file_frame)
        ops_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(ops_frame, text="Open File", command=self.open_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(ops_frame, text="Save File", command=self.save_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(ops_frame, text="AI Review", command=self.ai_review_file).pack(side=tk.LEFT, padx=5)
        
        # File editor
        self.file_editor = scrolledtext.ScrolledText(file_frame)
        self.file_editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.current_file = None
    
    def setup_monitor_tab(self, notebook):
        monitor_frame = ttk.Frame(notebook)
        notebook.add(monitor_frame, text="System Monitor")
        
        # Status indicators
        status_frame = ttk.LabelFrame(monitor_frame, text="Service Status")
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.status_labels = {}
        services = ["Ollama", "MiniMax API", "Claude API", "ULTRON Agent"]
        
        for i, service in enumerate(services):
            frame = ttk.Frame(status_frame)
            frame.grid(row=i//2, column=i%2, sticky=tk.W, padx=10, pady=5)
            
            ttk.Label(frame, text=f"{service}:").pack(side=tk.LEFT)
            label = ttk.Label(frame, text="●", foreground="gray")
            label.pack(side=tk.LEFT, padx=5)
            self.status_labels[service] = label
        
        # System info
        self.system_info = scrolledtext.ScrolledText(monitor_frame, height=20)
        self.system_info.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Auto-refresh
        self.refresh_status()
    
    def send_message(self):
        message = self.chat_input.get("1.0", tk.END).strip()
        if not message:
            return
        
        self.chat_display.insert(tk.END, f"You: {message}\n\n")
        self.chat_input.delete("1.0", tk.END)
        
        # Process in thread
        threading.Thread(target=self.process_ai_message, args=(message,), daemon=True).start()
    
    def process_ai_message(self, message):
        model = self.model_var.get()
        
        try:
            if "MiniMax" in model:
                response = self.call_minimax(message)
            elif "Claude" in model:
                response = self.call_claude(message)
            else:
                response = self.call_continue(message)
            
            self.root.after(0, lambda: self.chat_display.insert(tk.END, f"AI: {response}\n\n"))
        except Exception as e:
            self.root.after(0, lambda: self.chat_display.insert(tk.END, f"Error: {str(e)}\n\n"))
    
    def call_minimax(self, message):
        api_key = self.config.get("minimax_api_key", "")
        
        response = requests.post(
            "https://api.minimax.io/v1/text/chatcompletion",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "abab6.5s-chat",
                "messages": [{"role": "user", "content": message}],
                "stream": False
            }
        )
        
        if response.status_code == 200:
            return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response")
        else:
            return f"API Error: {response.status_code}"
    
    def call_claude(self, message):
        api_key = self.config.get("anthropic_api_key", "")
        
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            },
            json={
                "model": "claude-3-haiku-20240307",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": message}]
            }
        )
        
        if response.status_code == 200:
            return response.json().get("content", [{}])[0].get("text", "No response")
        else:
            return f"API Error: {response.status_code}"
    
    def call_continue(self, message):
        # Use Mini-Agent for Continue integration
        try:
            result = subprocess.run([
                "bash", "-c", 
                f"cd Mini-Agent && source venv/bin/activate && echo '{message}' | python -m mini_agent.cli --workspace ../workspace"
            ], capture_output=True, text=True, timeout=30)
            
            return result.stdout if result.stdout else result.stderr
        except subprocess.TimeoutExpired:
            return "Request timed out"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def run_tests(self):
        self.auto_log.insert(tk.END, "Running tests...\n")
        threading.Thread(target=self._run_command, args=("python3 -m pytest tests/ -v",), daemon=True).start()
    
    def update_deps(self):
        self.auto_log.insert(tk.END, "Updating dependencies...\n")
        threading.Thread(target=self._run_command, args=("pip install -r requirements.txt --upgrade",), daemon=True).start()
    
    def git_status(self):
        self.auto_log.insert(tk.END, "Checking git status...\n")
        threading.Thread(target=self._run_command, args=("git status",), daemon=True).start()
    
    def start_ultron(self):
        self.auto_log.insert(tk.END, "Starting ULTRON Agent...\n")
        threading.Thread(target=self._run_command, args=("python3 main.py",), daemon=True).start()
    
    def _run_command(self, command):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            output = result.stdout + result.stderr
            self.root.after(0, lambda: self.auto_log.insert(tk.END, f"{output}\n"))
        except Exception as e:
            self.root.after(0, lambda: self.auto_log.insert(tk.END, f"Error: {str(e)}\n"))
    
    def open_file(self):
        file_path = filedialog.askopenfilename(
            initialdir=".",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                self.file_editor.delete("1.0", tk.END)
                self.file_editor.insert("1.0", content)
                self.current_file = file_path
                self.root.title(f"ULTRON AI Integration Hub - {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {str(e)}")
    
    def save_file(self):
        if not self.current_file:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".py",
                filetypes=[("Python files", "*.py"), ("All files", "*.*")]
            )
            if file_path:
                self.current_file = file_path
        
        if self.current_file:
            try:
                content = self.file_editor.get("1.0", tk.END)
                with open(self.current_file, 'w') as f:
                    f.write(content)
                messagebox.showinfo("Success", "File saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")
    
    def ai_review_file(self):
        if not self.current_file:
            messagebox.showwarning("Warning", "No file open for review")
            return
        
        content = self.file_editor.get("1.0", tk.END)
        review_prompt = f"Review this code for issues and improvements:\n\n{content}"
        
        # Use current model for review
        threading.Thread(target=self.process_ai_message, args=(review_prompt,), daemon=True).start()
    
    def refresh_status(self):
        # Check service status
        services = {
            "Ollama": self.check_ollama,
            "MiniMax API": self.check_minimax,
            "Claude API": self.check_claude,
            "ULTRON Agent": self.check_ultron
        }
        
        for service, check_func in services.items():
            try:
                status = check_func()
                color = "green" if status else "red"
                self.status_labels[service].config(foreground=color)
            except:
                self.status_labels[service].config(foreground="red")
        
        # Update system info
        self.update_system_info()
        
        # Schedule next refresh
        self.root.after(10000, self.refresh_status)
    
    def check_ollama(self):
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def check_minimax(self):
        api_key = self.config.get("minimax_api_key", "")
        if not api_key:
            return False
        
        try:
            response = requests.post(
                "https://api.minimax.io/v1/text/chatcompletion",
                headers={"Authorization": f"Bearer {api_key}"},
                json={"model": "abab6.5s-chat", "messages": [{"role": "user", "content": "test"}]},
                timeout=5
            )
            return response.status_code in [200, 400]  # 400 might be quota/format issue but API is working
        except:
            return False
    
    def check_claude(self):
        api_key = self.config.get("anthropic_api_key", "")
        if not api_key:
            return False
        
        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={"x-api-key": api_key, "anthropic-version": "2023-06-01"},
                json={"model": "claude-3-haiku-20240307", "max_tokens": 10, "messages": [{"role": "user", "content": "test"}]},
                timeout=5
            )
            return response.status_code in [200, 400]
        except:
            return False
    
    def check_ultron(self):
        return os.path.exists("main.py") and os.path.exists("ultron_config.json")
    
    def update_system_info(self):
        info = []
        info.append(f"Project: {os.getcwd()}")
        info.append(f"Python: {subprocess.getoutput('python3 --version')}")
        
        # Git info
        try:
            branch = subprocess.getoutput("git branch --show-current")
            info.append(f"Git Branch: {branch}")
        except:
            pass
        
        # File counts
        py_files = len(list(Path(".").rglob("*.py")))
        info.append(f"Python Files: {py_files}")
        
        self.system_info.delete("1.0", tk.END)
        self.system_info.insert("1.0", "\n".join(info))
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = UltronAIGUI()
    app.run()