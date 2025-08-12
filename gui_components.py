import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class CustomButton(tk.Button):
    def __init__(self, master=None, **kwargs):
        # Custom styling for our buttons
        style_options = {
            'background': "#1a1a1a",
            'foreground': "#00ff00",
            'activebackground': "#2a2a2a",
            'activeforeground': "#ffffff",
            'relief': 'flat',
            'font': ('Consolas', 10, 'bold'),
            'borderwidth': 1,
            'highlightthickness': 1,
            'highlightbackground': '#00ff00'
        }
        style_options.update(kwargs)
        super().__init__(master, **style_options)

class CustomFrame(tk.Frame):
    def __init__(self, master=None, **kwargs):
        # Custom styling for frames
        style_options = {
            'background': "#0a0a0a",
            'bd': 1,
            'relief': 'solid',
            'highlightbackground': '#00ff00',
            'highlightcolor': '#00ff00',
            'highlightthickness': 1
        }
        style_options.update(kwargs)
        super().__init__(master, **style_options)

class CustomLabel(tk.Label):
    def __init__(self, master=None, **kwargs):
        # Custom styling for labels
        style_options = {
            'background': "#0a0a0a",
            'foreground': "#00ff00",
            'font': ('Consolas', 11)
        }
        style_options.update(kwargs)
        super().__init__(master, **style_options)

class ImageLabel(CustomLabel):
    def __init__(self, master=None, image_path=None, size=(100, 100), **kwargs):
        super().__init__(master, **kwargs)
        self.image_path = image_path
        self.size = size
        self.photo_image = None
        self._load_image()

    def _load_image(self):
        if self.image_path and os.path.exists(self.image_path):
            try:
                pil_image = Image.open(self.image_path).resize(self.size, Image.Resampling.LANCZOS)
                self.photo_image = ImageTk.PhotoImage(pil_image)
                self.config(image=self.photo_image)
            except Exception as e:
                self.config(text=f"Img Err: {e}")
        else:
            self.config(text="No Img")

