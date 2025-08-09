CYBERPUNK = {
    "bg": "#000000",
    "panel": "#0a0a1a",
    "fg": "#00ff00",
    "accent": "#ff00ff",
    "accent2": "#28ff28",
    "button_bg": "#1a1a1a",
    "warn": "#ffaa00",
    "error": "#ff4444",
}

def apply_ttk_theme(ttk):
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass
    style.configure("TButton", background=CYBERPUNK["button_bg"], foreground=CYBERPUNK["fg"])
    style.configure("TLabel", background=CYBERPUNK["bg"], foreground=CYBERPUNK["fg"])
    style.configure("Treeview", background=CYBERPUNK["panel"], foreground=CYBERPUNK["fg"], fieldbackground=CYBERPUNK["panel"])