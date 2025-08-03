import tkinter as tk
from tkinter import ttk, scrolledtext, Toplevel, Frame, Label, Button, Entry
from PIL import Image, ImageTk
import threading
import psutil
import time
import os
import logging

class UltimateAgentGUI:
    def __init__(self, agent_handle):
        self.agent_handle = agent_handle
        self.root = tk.Tk()
        self.root.title("ULTRON 3.0 - Ultimate Cyberpunk Interface")
        self.root.geometry("1280x720")
        self.root.minsize(1024, 600)
        self.root.configure(bg='#000000')

        self.image_cache = {}
        self._load_images()
        
        self._create_main_layout()
        self._start_monitoring()

    def _load_images(self):
        image_paths = {
            "background": "resources/images/image-15-1280x717.png",
            "avatar": "resources/images/ChatGPT Image Jul 29, 2025, 02_32_42 AM.png",
            "tools_bg": "resources/images/PDA-1280x1280.png",
            "file_browser_bg": "resources/images/JussiK_point_and_click_game_user_interface_7449bd55-0ef8-482c-ad72-10aebcf8e773-1320x880.png.webp"
        }
        for name, path in image_paths.items():
            try:
                if os.path.exists(path):
                    img = Image.open(path)
                    self.image_cache[name] = img
                else:
                    logging.warning(f"Image not found at path: {path} - gui_ultimate.py:38")
                    self.image_cache[name] = None
            except Exception as e:
                logging.error(f"Failed to load image {name} from {path}: {e} - gui_ultimate.py:41")
                self.image_cache[name] = None

    def _create_main_layout(self):
        # Background Canvas
        self.bg_canvas = tk.Canvas(self.root, highlightthickness=0)
        self.bg_canvas.pack(fill="both", expand=True)

        if self.image_cache.get("background"):
            bg_img_pil = self.image_cache["background"].resize((1280, 720), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(bg_img_pil)
            self.bg_canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
        else:
             self.bg_canvas.configure(bg='#0a0a2a')

        # --- Main Content Area ---
        # This frame will hold the chat, input, and avatar
        content_frame = Frame(self.bg_canvas, bg='#000000', bd=0, highlightthickness=0)
        content_frame.place(relx=0.5, rely=0.5, relwidth=0.7, relheight=0.8, anchor='center')

        # Avatar
        if self.image_cache.get("avatar"):
            avatar_img_pil = self.image_cache["avatar"].resize((100, 100), Image.Resampling.LANCZOS)
            self.avatar_photo = ImageTk.PhotoImage(avatar_img_pil)
            avatar_label = Label(content_frame, image=self.avatar_photo, bg='#000000')
            avatar_label.pack(pady=10)

        # Chat History
        self.chat_history = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD, bg='#0a0a1a', fg='#00ff00', font=("Consolas", 11), relief='flat', borderwidth=1, insertbackground='white')
        self.chat_history.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        self.chat_history.config(state=tk.DISABLED)

        # User Input
        self.user_input = Entry(content_frame, bg='#0a0a1a', fg='#ffffff', font=("Consolas", 12), relief='flat', insertbackground='white')
        self.user_input.pack(padx=20, pady=10, fill=tk.X, ipady=8)
        self.user_input.bind("<Return>", self.send_message)

        # --- Bottom Buttons ---
        button_frame = Frame(self.bg_canvas, bg='#000000', bd=0, highlightthickness=0)
        button_frame.place(relx=0.5, rely=0.95, anchor='center')

        Button(button_frame, text="Tools Menu", command=self._open_tools_menu, bg='#1a1a1a', fg='#00ff00', relief='flat').pack(side=tk.LEFT, padx=10)
        Button(button_frame, text="File Browser", command=self._open_file_browser, bg='#1a1a1a', fg='#00ff00', relief='flat').pack(side=tk.LEFT, padx=10)
        
        # --- System Stats ---
        stats_frame = Frame(self.bg_canvas, bg='#000000', bd=0, highlightthickness=0)
        stats_frame.place(relx=0.01, rely=0.02, anchor='nw')
        self.cpu_label = Label(stats_frame, text="CPU: 0.0%", bg='#000000', fg='#ff00ff', font=("Consolas", 10))
        self.cpu_label.pack(anchor='w')
        self.ram_label = Label(stats_frame, text="RAM: 0.0%", bg='#000000', fg='#ff00ff', font=("Consolas", 10))
        self.ram_label.pack(anchor='w')

    def _open_tools_menu(self):
        tools_window = Toplevel(self.root)
        tools_window.title("Agent Tools")
        tools_window.geometry("400x550")
        tools_window.configure(bg="#000000")
        tools_window.transient(self.root)

        bg_image_pil = self.image_cache.get("tools_bg")
        if bg_image_pil:
            bg_image_pil = bg_image_pil.resize((400, 550), Image.Resampling.LANCZOS)
            bg_photo = ImageTk.PhotoImage(bg_image_pil)
            bg_label = Label(tools_window, image=bg_photo)
            bg_label.image = bg_photo
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        Label(tools_window, text="[ SYSTEM TOOLS ]", fg="#22ff22", bg="#1a1a1a", font=("Consolas", 14, "bold")).pack(pady=20)

        tools_frame = Frame(tools_window, bg='#111111', bd=2, relief='groove')
        tools_frame.pack(pady=10, padx=20, fill='both', expand=True)

        try:
            tools = self.agent_handle.list_tools() if hasattr(self.agent_handle, 'list_tools') else []
            if not tools:
                tools = [{'name': 'screenshot', 'description': 'Take a screenshot'}, {'name': 'list_files', 'description': 'List files in a directory'}]
        except Exception as e:
            tools = []
            logging.error(f"Could not fetch tools from agent: {e} - gui_ultimate.py:119")

        for tool in tools:
            tool_name = tool.get('name', 'Unknown Tool')
            btn = Button(tools_frame, text=tool_name, bg='#1a1a1a', fg='#22ff22', relief='flat', 
                         command=lambda t=tool_name: self._run_tool_command(t))
            btn.pack(fill='x', padx=10, pady=5)

    def _run_tool_command(self, tool_name: str):
        command = f"execute the {tool_name} tool"
        self.add_message("User (Tool)", command)
        threading.Thread(target=self._get_agent_response, args=(command,), daemon=True).start()

    def _open_file_browser(self):
        browser_window = Toplevel(self.root)
        browser_window.title("File System Navigator")
        browser_window.geometry("800x600")
        browser_window.configure(bg="#0a0a2a")

        tree_frame = Frame(browser_window)
        tree_frame.pack(pady=10, padx=10, fill='both', expand=True)

        style = ttk.Style()
        style.configure("Treeview", background="#0a0a2a", foreground="#00ff00", fieldbackground="#0a0a2a", rowheight=25)
        style.map('Treeview', background=[('selected', '#1f1f7a')])
        
        self.file_tree = ttk.Treeview(tree_frame)
        self.file_tree.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.file_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.file_tree.configure(yscrollcommand=scrollbar.set)
        
        self._populate_file_tree(self.file_tree, os.getcwd())

        self.file_tree.bind("<Double-1>", self._on_file_tree_double_click)
        self.file_tree.bind('<<TreeviewOpen>>', self._on_node_expand)

    def _populate_file_tree(self, tree, path):
        for i in tree.get_children():
            tree.delete(i)
        
        parent_path = os.path.dirname(path)
        self._insert_node(tree, '', f'.. ({os.path.basename(parent_path)})', parent_path)
        self._populate_file_tree_branch(tree, '', path)

    def _populate_file_tree_branch(self, tree, parent_id, path):
        try:
            items = sorted(os.listdir(path), key=lambda s: s.lower())
            dirs = [i for i in items if os.path.isdir(os.path.join(path, i))]
            files = [i for i in items if os.path.isfile(os.path.join(path, i))]
            for item in dirs + files:
                self._insert_node(tree, parent_id, item, os.path.join(path, item))
        except OSError as e:
            logging.error(f"Error reading path {path}: {e} - gui_ultimate.py:173")
            self._insert_node(tree, parent_id, f"Error: {e.strerror}", path)

    def _insert_node(self, tree, parent, text, abspath):
        node = tree.insert(parent, 'end', text=text, open=False, values=[abspath])
        if os.path.isdir(abspath):
            tree.insert(node, 'end')

    def _on_node_expand(self, event):
        node_id = self.file_tree.focus()
        if not node_id: return
        node_path = self.file_tree.item(node_id)['values'][0]
        
        children = self.file_tree.get_children(node_id)
        if children and self.file_tree.item(children[0])['text'] == '':
             self.file_tree.delete(*children)
             self._populate_file_tree_branch(self.file_tree, node_id, node_path)

    def _on_file_tree_double_click(self, event):
        item_id = self.file_tree.identify_row(event.y)
        if not item_id: return
            
        path = self.file_tree.item(item_id)['values'][0]
        
        if os.path.isdir(path):
            self._populate_file_tree(self.file_tree, path)
        else:
            command = f"read the file at \"{path}\""
            self.add_message("User (File Browser)", command)
            threading.Thread(target=self._get_agent_response, args=(command,), daemon=True).start()

    def send_message(self, event=None):
        message = self.user_input.get()
        if message.strip():
            self.add_message("User", message)
            self.user_input.delete(0, tk.END)
            threading.Thread(target=self._get_agent_response, args=(message,), daemon=True).start()

    def _get_agent_response(self, message):
        response = self.agent_handle.handle_text(message)
        self.root.after(0, self.add_message, "Ultron", response)

    def add_message(self, sender, message):
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.END, f"{sender} > {message}\n{'-'*90}\n")
        self.chat_history.config(state=tk.DISABLED)
        self.chat_history.yview(tk.END)

    def _start_monitoring(self):
        def update_stats():
            while True:
                try:
                    cpu = psutil.cpu_percent()
                    ram = psutil.virtual_memory().percent
                    self.root.after(0, self.cpu_label.config, {'text': f"CPU: {cpu:.1f}%"})
                    self.root.after(0, self.ram_label.config, {'text': f"RAM: {ram:.1f}%"})
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass # Ignore errors if process closes during monitoring
                except Exception as e:
                    logging.error(f"GUI monitoring error: {e} - gui_ultimate.py:232")
                time.sleep(2)
        
        monitor_thread = threading.Thread(target=update_stats, daemon=True)
        monitor_thread.start()

    def run(self):
        self.root.mainloop()

# Example for testing
if __name__ == '__main__':
    class MockAgent:
        def handle_text(self, text):
            time.sleep(1)
            return f"SYSTEM COMMAND RECEIVED: '{text}'. Executing..."

    # Make sure to have the image files in a 'resources/images' directory
    if not os.path.exists("resources/images"):
        os.makedirs("resources/images")
        print("Created 'resources/images' directory. Please add your GUI images there. - gui_ultimate.py:251")

    logging.basicConfig(level=logging.INFO)
    gui = UltimateAgentGUI(MockAgent())
    gui.run()
