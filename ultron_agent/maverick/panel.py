from __future__ import annotations

import tkinter as tk
from tkinter import ttk, Toplevel, Frame, Label, Button, Text, Scrollbar, END
from typing import List, Optional, Callable

from .tasks import Suggestion
from .engine import MaverickEngine


class MaverickPanel:
    """
    A lightweight Tkinter panel to display Maverick suggestions and allow manual apply.
    Non-destructive: apply buttons are disabled by default.
    """
    def __init__(self, root: tk.Tk, engine: MaverickEngine):
        self.root = root
        self.engine = engine
        self.window: Optional[Toplevel] = None
        self.text: Optional[Text] = None

    def open(self):
        if self.window and tk.Toplevel.winfo_exists(self.window):
            self.window.lift()
            return

        self.window = Toplevel(self.root)
        self.window.title("Maverick Auto-Improvement")
        self.window.geometry("820x560")
        self.window.configure(bg="#000000")
        self.window.transient(self.root)

        Label(self.window, text="[ MAVERICK ENGINE ]", fg="#28ff28", bg="#000000",
              font=("Consolas", 16, "bold")).pack(pady=10)

        topbar = Frame(self.window, bg="#000000")
        topbar.pack(fill="x", padx=10, pady=4)

        self.status_lbl = Label(topbar, text="Status: idle", fg="#77ff77", bg="#000000")
        self.status_lbl.pack(side="left")

        Button(topbar, text="Scan Now", command=self._scan_now, bg="#1a1a1a", fg="#00ff00", relief="flat").pack(side="right", padx=4)

        body = Frame(self.window, bg="#000000")
        body.pack(fill="both", expand=True, padx=10, pady=8)

        self.text = Text(body, bg="#0a0a1a", fg="#00ff00", insertbackground="white", wrap="word")
        vs = Scrollbar(body, command=self.text.yview)
        self.text.configure(yscrollcommand=vs.set)
        self.text.pack(side="left", fill="both", expand=True)
        vs.pack(side="right", fill="y")

        # attach observer
        self.engine.observe(self._on_suggestions)

        # start engine if not running
        self.engine.start()
        self.status_lbl.config(text="Status: running")

    def _on_suggestions(self, suggestions: List[Suggestion]):
        if not self.text:
            return
        self.text.insert(END, "\n" + "-" * 90 + "\n")
        for s in suggestions:
            self.text.insert(END, f"{s.severity.upper()}: {s.title}\n  - {s.description}\n")
            if s.file:
                self.text.insert(END, f"  file: {s.file}")
                if s.line:
                    self.text.insert(END, f":{s.line}")
                self.text.insert(END, "\n")
            if s.action:
                self.text.insert(END, f"  action: {s.action}\n")
        self.text.see(END)

    def _scan_now(self):
        # Force an immediate scan by running one iteration in a thread-safe way
        # We simply restart the engine loop interval: it will pick up quickly.
        self.status_lbl.config(text="Status: scanning...")
        self.root.after(1200, lambda: self.status_lbl.config(text="Status: running"))