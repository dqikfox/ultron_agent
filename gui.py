import tkinter as tk
from tkinter import ttk, messagebox


class AgentGUI:
    def __init__(self, agent, log_queue):
        self.agent = agent
        self.log_queue = log_queue
        self.root = tk.Tk()
        self.root.title("Ultron Agent 2.0")
        self.root.geometry("800x600")

        # Main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Settings panel
        self.settings_frame = tk.LabelFrame(main_frame, text="Settings")
        self.settings_frame.pack(fill=tk.X, pady=5)
        self.settings = {
            "Voice": tk.BooleanVar(value=self.agent.config.data.get("use_voice")),
            "Vision": tk.BooleanVar(value=self.agent.config.data.get("use_vision")),
            "API": tk.BooleanVar(value=self.agent.config.data.get("use_api"))
        }
        for name, var in self.settings.items():
            cb = tk.Checkbutton(self.settings_frame, text=name, variable=var, command=self.update_settings)
            cb.pack(side=tk.LEFT)

        # Voice enable/disable button
        self.voice_enabled = tk.BooleanVar(value=self.agent.config.data.get("use_voice", True))
        self.voice_button = tk.Button(self.settings_frame, text="Enable Voice" if not self.voice_enabled.get() else "Disable Voice", command=self.toggle_voice)
        self.voice_button.pack(side=tk.LEFT, padx=(10,0))

        # Voice engine dropdown
        tk.Label(self.settings_frame, text="Voice Engine:").pack(side=tk.LEFT, padx=(20,0))
        self.voice_engine_var = tk.StringVar(value=self.agent.config.data.get("voice_engine", "pyttsx3"))
        self.voice_engine_menu = ttk.Combobox(self.settings_frame, textvariable=self.voice_engine_var, state="readonly", width=12)
        self.voice_engine_menu['values'] = ("pyttsx3", "elevenlabs")
        self.voice_engine_menu.pack(side=tk.LEFT)

        # LLM model dropdown
        tk.Label(self.settings_frame, text="LLM Model:").pack(side=tk.LEFT, padx=(20,0))
        self.llm_model_var = tk.StringVar(value=self.agent.config.data.get("llm_model", "llama3.2:latest"))
        self.llm_model_menu = ttk.Combobox(self.settings_frame, textvariable=self.llm_model_var, state="readonly", width=32)
        self.llm_model_menu['values'] = (
            "qwen3:0.6b",
            "qikfox/Eleven:latest",
            "llama3.2:latest",
            "qwen2.5:latest",
            "mxbai-embed-large:latest",
            "Qwen2.5-7B-Mini.Q5_K_S:latest",
            "phi-3-mini-128k-instruct.Q5_K_M:latest",
            "hermes3:latest",
            "hermes3:8b"
        )
        self.llm_model_menu.pack(side=tk.LEFT)
        self.llm_model_menu.bind("<<ComboboxSelected>>", self.update_llm_model)

        tk.Button(self.settings_frame, text="Apply", command=self.apply_settings).pack(side=tk.RIGHT)

        # --- Voice Input Controls ---
        self.voice_controls_frame = tk.Frame(self.settings_frame)
        self.voice_controls_frame.pack(side=tk.LEFT, padx=(10,0))
        self.listen_button = tk.Button(self.voice_controls_frame, text="Listen", command=self.listen_once)
        self.listen_button.pack(side=tk.LEFT)
        self.always_listen_var = tk.BooleanVar(value=False)
        self.always_listen_check = tk.Checkbutton(self.voice_controls_frame, text="Always Listen", variable=self.always_listen_var, command=self.toggle_always_listen)
        self.always_listen_check.pack(side=tk.LEFT)
        self.listening_thread = None
        self._stop_listening = False

        # --- Command Entry ---
        self.entry_frame = tk.Frame(main_frame)
        self.entry_frame.pack(fill=tk.X, pady=(10, 0))
        tk.Label(self.entry_frame, text="Command:").pack(side=tk.LEFT, padx=(0, 5))
        self.command_entry = tk.Entry(self.entry_frame, width=60)
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.command_entry.bind("<Return>", self.send_command)
        tk.Button(self.entry_frame, text="Send", command=self.send_command).pack(side=tk.LEFT, padx=(5, 0))

        # --- Response Text ---
        self.response_text = tk.Text(main_frame, height=12, wrap=tk.WORD, state=tk.DISABLED)
        self.response_text.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # --- Indicators ---
        self.indicators = {}
        self.indicator_frame = tk.Frame(self.settings_frame)
        self.indicator_frame.pack(side=tk.RIGHT, padx=(10, 0))
        for name in self.settings:
            canvas = tk.Canvas(self.indicator_frame, width=16, height=16, highlightthickness=0)
            oval = canvas.create_oval(2, 2, 14, 14, fill="green" if self.settings[name].get() else "gray")
            canvas.pack(side=tk.LEFT, padx=2)
            self.indicators[name] = (canvas, oval)

        # --- Tool Explorer Panel ---
        tool_explorer = tk.LabelFrame(main_frame, text="Tool Explorer")
        tool_explorer.pack(fill=tk.BOTH, expand=False, pady=10)
        self.tool_listbox = tk.Listbox(tool_explorer, width=40, height=6)
        self.tool_listbox.pack(side=tk.LEFT, fill=tk.Y, padx=(5,0), pady=5)
        self.tool_details = tk.Text(tool_explorer, width=60, height=6, state=tk.DISABLED)
        self.tool_details.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.tool_invoke_frame = tk.Frame(tool_explorer)
        self.tool_invoke_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.tool_param_entries = {}
        tk.Button(self.tool_invoke_frame, text="Invoke Tool", command=self.invoke_selected_tool).pack(pady=(0,5))
        self.populate_tool_list()
        self.tool_listbox.bind("<<ListboxSelect>>", self.show_tool_details)

    def listen_once(self):
        if not self.agent.voice:
            messagebox.showwarning("Voice", "Voice is not enabled.")
            return
        self.listen_button.config(state=tk.DISABLED)
        self.root.after(100, self._do_listen_once)

    def _do_listen_once(self):
        try:
            # Release mic from other processes before listening
            import subprocess
            subprocess.run([sys.executable, "mic_release.py"], cwd=os.path.dirname(__file__), timeout=5)
            text = self.agent.voice.listen()
            if text:
                self.command_entry.delete(0, tk.END)
                self.command_entry.insert(0, text)
                self.send_command()
            else:
                messagebox.showinfo("Voice", "No speech detected.")
        except Exception as e:
            messagebox.showerror("Voice", f"Voice input error: {e}")
        finally:
            self.listen_button.config(state=tk.NORMAL)

    def toggle_always_listen(self):
        if self.always_listen_var.get():
            self._stop_listening = False
            import threading
            self.listening_thread = threading.Thread(target=self._background_listen, daemon=True)
            self.listening_thread.start()
        else:
            self._stop_listening = True

    def _background_listen(self):
        import time
        while not self._stop_listening:
            if self.agent.voice:
                try:
                    text = self.agent.voice.listen()
                    if text:
                        self.root.after(0, self._handle_voice_command, text)
                except Exception as e:
                    print(f"Voice listen error: {e} - gui.py:148")
            time.sleep(1)

    def _handle_voice_command(self, text):
        self.command_entry.delete(0, tk.END)
        self.command_entry.insert(0, text)
        self.send_command()

    # ...existing code...

    def listen_once(self):
        if not self.agent.voice:
            messagebox.showwarning("Voice", "Voice is not enabled.")
            return
        self.listen_button.config(state=tk.DISABLED)
        self.root.after(100, self._do_listen_once)

    def _do_listen_once(self):
        try:
            text = self.agent.voice.listen()
            if text:
                self.command_entry.delete(0, tk.END)
                self.command_entry.insert(0, text)
                self.send_command()
            else:
                messagebox.showinfo("Voice", "No speech detected.")
        except Exception as e:
            messagebox.showerror("Voice", f"Voice input error: {e}")
        finally:
            self.listen_button.config(state=tk.NORMAL)

    def toggle_always_listen(self):
        if self.always_listen_var.get():
            self._stop_listening = False
            import threading
            self.listening_thread = threading.Thread(target=self._background_listen, daemon=True)
            self.listening_thread.start()
        else:
            self._stop_listening = True

    def _background_listen(self):
        import time
        import subprocess
        while not self._stop_listening:
            if self.agent.voice:
                try:
                    # Release mic from other processes before listening
                    subprocess.run([sys.executable, "mic_release.py"], cwd=os.path.dirname(__file__), timeout=5)
                    text = self.agent.voice.listen()
                    if text:
                        self.root.after(0, self._handle_voice_command, text)
                except Exception as e:
                    print(f"Voice listen error: {e} - gui.py:197")
            time.sleep(1)

    def _handle_voice_command(self, text):
        self.command_entry.delete(0, tk.END)
        self.command_entry.insert(0, text)
        self.send_command()
    def __init__(self, agent, log_queue):
        self.agent = agent
        self.log_queue = log_queue
        self.root = tk.Tk()
        self.root.title("Ultron Agent 2.0")
        self.root.geometry("800x600")

        # Main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Settings panel
        self.settings_frame = tk.LabelFrame(main_frame, text="Settings")
        self.settings_frame.pack(fill=tk.X, pady=5)
        self.settings = {
            "Voice": tk.BooleanVar(value=self.agent.config.data.get("use_voice")),
            "Vision": tk.BooleanVar(value=self.agent.config.data.get("use_vision")),
            "API": tk.BooleanVar(value=self.agent.config.data.get("use_api"))
        }
        for name, var in self.settings.items():
            cb = tk.Checkbutton(self.settings_frame, text=name, variable=var, command=self.update_settings)
            cb.pack(side=tk.LEFT)

        # Voice enable/disable button
        self.voice_enabled = tk.BooleanVar(value=self.agent.config.data.get("use_voice", True))
        self.voice_button = tk.Button(self.settings_frame, text="Enable Voice" if not self.voice_enabled.get() else "Disable Voice", command=self.toggle_voice)
        self.voice_button.pack(side=tk.LEFT, padx=(10,0))

        # Voice engine dropdown
        tk.Label(self.settings_frame, text="Voice Engine:").pack(side=tk.LEFT, padx=(20,0))
        self.voice_engine_var = tk.StringVar(value=self.agent.config.data.get("voice_engine", "pyttsx3"))
        self.voice_engine_menu = ttk.Combobox(self.settings_frame, textvariable=self.voice_engine_var, state="readonly", width=12)
        self.voice_engine_menu['values'] = ("pyttsx3", "elevenlabs")
        self.voice_engine_menu.pack(side=tk.LEFT)

        # LLM model dropdown
        tk.Label(self.settings_frame, text="LLM Model:").pack(side=tk.LEFT, padx=(20,0))
        self.llm_model_var = tk.StringVar(value=self.agent.config.data.get("llm_model", "llama3.2:latest"))
        self.llm_model_menu = ttk.Combobox(self.settings_frame, textvariable=self.llm_model_var, state="readonly", width=32)
        self.llm_model_menu['values'] = (
            "qwen3:0.6b",
            "qikfox/Eleven:latest",
            "llama3.2:latest",
            "qwen2.5:latest",
            "mxbai-embed-large:latest",
            "Qwen2.5-7B-Mini.Q5_K_S:latest",
            "phi-3-mini-128k-instruct.Q5_K_M:latest",
            "hermes3:latest",
            "hermes3:8b"
        )
        self.llm_model_menu.pack(side=tk.LEFT)
        self.llm_model_menu.bind("<<ComboboxSelected>>", self.update_llm_model)

        tk.Button(self.settings_frame, text="Apply", command=self.apply_settings).pack(side=tk.RIGHT)

        # --- Command Entry ---
        self.entry_frame = tk.Frame(main_frame)
        self.entry_frame.pack(fill=tk.X, pady=(10, 0))
        tk.Label(self.entry_frame, text="Command:").pack(side=tk.LEFT, padx=(0, 5))
        self.command_entry = tk.Entry(self.entry_frame, width=60)
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.command_entry.bind("<Return>", self.send_command)
        tk.Button(self.entry_frame, text="Send", command=self.send_command).pack(side=tk.LEFT, padx=(5, 0))

        # --- Response Text ---
        self.response_text = tk.Text(main_frame, height=12, wrap=tk.WORD, state=tk.DISABLED)
        self.response_text.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # --- Indicators ---
        self.indicators = {}
        self.indicator_frame = tk.Frame(self.settings_frame)
        self.indicator_frame.pack(side=tk.RIGHT, padx=(10, 0))
        for name in self.settings:
            canvas = tk.Canvas(self.indicator_frame, width=16, height=16, highlightthickness=0)
            oval = canvas.create_oval(2, 2, 14, 14, fill="green" if self.settings[name].get() else "gray")
            canvas.pack(side=tk.LEFT, padx=2)
            self.indicators[name] = (canvas, oval)

        # --- Tool Explorer Panel ---
        tool_explorer = tk.LabelFrame(main_frame, text="Tool Explorer")
        tool_explorer.pack(fill=tk.BOTH, expand=False, pady=10)
        self.tool_listbox = tk.Listbox(tool_explorer, width=40, height=6)
        self.tool_listbox.pack(side=tk.LEFT, fill=tk.Y, padx=(5,0), pady=5)
        self.tool_details = tk.Text(tool_explorer, width=60, height=6, state=tk.DISABLED)
        self.tool_details.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.tool_invoke_frame = tk.Frame(tool_explorer)
        self.tool_invoke_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.tool_param_entries = {}
        tk.Button(self.tool_invoke_frame, text="Invoke Tool", command=self.invoke_selected_tool).pack(pady=(0,5))
        self.populate_tool_list()
        self.tool_listbox.bind("<<ListboxSelect>>", self.show_tool_details)

    def populate_tool_list(self):
        self.tool_listbox.delete(0, tk.END)
        self.tools = self.agent.tools
        for tool in self.tools:
            self.tool_listbox.insert(tk.END, tool.name)

    def show_tool_details(self, event=None):
        selection = self.tool_listbox.curselection()
        if not selection:
            return
        idx = selection[0]
        tool = self.tools[idx]
        self.tool_details.config(state=tk.NORMAL)
        self.tool_details.delete(1.0, tk.END)
        self.tool_details.insert(tk.END, f"Name: {tool.name}\nDescription: {tool.description}\nParameters: {getattr(tool, 'parameters', {})}\n")
        self.tool_details.config(state=tk.DISABLED)
        # Show parameter entry fields
        for widget in self.tool_invoke_frame.winfo_children():
            if isinstance(widget, tk.Entry) or isinstance(widget, tk.Label):
                widget.destroy()
        self.tool_param_entries = {}
        params = getattr(tool, 'parameters', {}).get('properties', {})
        for pname, pinfo in params.items():
            tk.Label(self.tool_invoke_frame, text=pname+':').pack()
            entry = tk.Entry(self.tool_invoke_frame, width=20)
            entry.pack()
            self.tool_param_entries[pname] = entry

    def invoke_selected_tool(self):
        selection = self.tool_listbox.curselection()
        if not selection:
            messagebox.showwarning("Tool", "No tool selected.")
            return
        idx = selection[0]
        tool = self.tools[idx]
        params = {}
        for pname, entry in self.tool_param_entries.items():
            params[pname] = entry.get()
        try:
            result = tool.execute(**params)
        except Exception as e:
            result = f"Error: {e}"
        self.show_tool_result(tool.name, result)

    def run(self):
        self.root.mainloop()

    def run_tool_from_gui(self, tool):
        user_input = tool.name  # or prompt for args if needed
        try:
            result = tool.execute(user_input)
        except Exception as e:
            result = f"Error: {e}"
        self.show_tool_result(tool.name, result)

    def show_tool_result(self, tool_name, result):
        popup = tk.Toplevel(self.root)
        popup.title(f"Result: {tool_name}")
        tk.Label(popup, text=result, wraplength=400, justify="left").pack(padx=20, pady=20)
        tk.Button(popup, text="Close", command=popup.destroy).pack(pady=(0,10))

    def toggle_voice(self):
        current = self.voice_enabled.get()
        self.voice_enabled.set(not current)
        self.agent.config.data["use_voice"] = not current
        try:
            if not current:
                from voice import VoiceAssistant
                self.agent.voice = VoiceAssistant(self.agent.config)
                self.voice_button.config(text="Disable Voice")
                messagebox.showinfo("Voice", "Voice enabled.")
            else:
                self.agent.voice = None
                self.voice_button.config(text="Enable Voice")
                messagebox.showinfo("Voice", "Voice disabled.")
        except Exception as e:
            self.agent.voice = None
            self.voice_button.config(text="Enable Voice")
            messagebox.showerror("Voice Error", f"Failed to toggle voice: {e}")

    def update_voice_engine(self, event=None):
        new_engine = self.voice_engine_var.get()
        self.agent.config.data["voice_engine"] = new_engine
        self.agent.config.data["tts_engine"] = new_engine
        # Re-initialize voice assistant if enabled
        if self.agent.config.data.get("use_voice"):
            from voice import VoiceAssistant
            self.agent.voice = VoiceAssistant(self.agent.config)
        messagebox.showinfo("Voice Engine", f"Voice engine set to {new_engine}.")

    def update_llm_model(self, event=None):
        new_model = self.llm_model_var.get()
        self.agent.config.data["llm_model"] = new_model
        # Attempt to switch Ollama model for new requests
        try:
            import requests
            # This will not interrupt a running model, but will set for next request
            # Optionally, you could send a dummy request to preload the model
            requests.post(
                "http://localhost:11434/api/chat",
                json={"model": new_model, "messages": [{"role": "user", "content": "Hello"}]},
                timeout=5
            )
        except Exception as e:
            messagebox.showwarning("LLM Model", f"Model set to {new_model}, but could not preload: {e}")
        else:
            messagebox.showinfo("LLM Model", f"LLM model set to {new_model}.")

        # Start polling log queue
        self.root.after(500, self._poll_log_queue)

    def send_command(self, event=None):
        command = self.command_entry.get()
        if command:
            self.command_entry.delete(0, tk.END)
            response = self.agent.handle_text(command)
            self.response_text.config(state=tk.NORMAL)
            self.response_text.insert(tk.END, f"User: {command}\nUltron: {response}\n\n")
            self.response_text.config(state=tk.DISABLED)
            self.response_text.see(tk.END)

    def _poll_log_queue(self):
        while not self.log_queue.empty():
            msg = self.log_queue.get_nowait()
            self.response_text.config(state=tk.NORMAL)
            self.response_text.insert(tk.END, msg + "\n")
            self.response_text.config(state=tk.DISABLED)
            self.response_text.see(tk.END)
        self.root.after(500, self._poll_log_queue)

    def update_settings(self):
        for name, var in self.settings.items():
            self.indicators[name][0].itemconfig(self.indicators[name][1], fill="green" if var.get() else "gray")

    def apply_settings(self):
        self.agent.config.data["use_voice"] = self.settings["Voice"].get()
        self.agent.config.data["use_vision"] = self.settings["Vision"].get()
        self.agent.config.data["use_api"] = self.settings["API"].get()
        messagebox.showinfo("Settings", "Settings applied. Restart may be required for some changes.")
        if self.agent.config.data["use_voice"] and not hasattr(self.agent, "voice"):
            from voice import VoiceAssistant
            self.agent.voice = VoiceAssistant(self.agent.config)
        if self.agent.config.data["use_vision"] and not hasattr(self.agent, "vision"):
            from vision import Vision
            self.agent.vision = Vision()