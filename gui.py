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

        # Status indicators
        status_frame = tk.LabelFrame(main_frame, text="Subsystem Status")
        status_frame.pack(fill=tk.X, pady=5)
        self.indicators = {}
        subsystems = [("Voice", self.agent.config.data.get("use_voice")),
                      ("Vision", self.agent.config.data.get("use_vision")),
                      ("Memory", True), ("Tools", True), ("API", self.agent.config.data.get("use_api"))]
        for name, active in subsystems:
            frame = tk.Frame(status_frame, padx=5)
            canvas = tk.Canvas(frame, width=20, height=20)
            oval = canvas.create_oval(2, 2, 14, 14, fill="green" if active else "gray")
            canvas.pack(side=tk.LEFT)
            tk.Label(frame, text=name).pack(side=tk.LEFT)
            frame.pack(side=tk.LEFT)
            self.indicators[name] = (canvas, oval)

        # Command input
        input_frame = tk.LabelFrame(main_frame, text="Command Input")
        input_frame.pack(fill=tk.X, pady=5)
        self.command_entry = tk.Entry(input_frame)
        self.command_entry.pack(fill=tk.X, padx=5, pady=5)
        self.command_entry.bind("<Return>", self.send_command)
        tk.Button(input_frame, text="Send", command=self.send_command).pack(pady=5)

        # Response display
        response_frame = tk.LabelFrame(main_frame, text="Agent Response")
        response_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.response_text = tk.Text(response_frame, height=10, state=tk.DISABLED)
        self.response_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar = tk.Scrollbar(response_frame, command=self.response_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.response_text.config(yscrollcommand=scrollbar.set)

        # Settings panel
        settings_frame = tk.LabelFrame(main_frame, text="Settings")
        settings_frame.pack(fill=tk.X, pady=5)
        self.settings = {
            "Voice": tk.BooleanVar(value=self.agent.config.data.get("use_voice")),
            "Vision": tk.BooleanVar(value=self.agent.config.data.get("use_vision")),
            "API": tk.BooleanVar(value=self.agent.config.data.get("use_api"))
        }
        for name, var in self.settings.items():
            tk.Checkbutton(settings_frame, text=name, variable=var, command=self.update_settings).pack(side=tk.LEFT)
        tk.Button(settings_frame, text="Apply", command=self.apply_settings).pack(side=tk.RIGHT)

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
            self.agent.vision = Vision(self.agent.config)

    def run(self):
        self.root.mainloop()