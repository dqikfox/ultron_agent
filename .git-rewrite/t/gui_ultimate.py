from tkinter import Tk, Canvas, BOTH, WORD, DISABLED, NORMAL, END, X, LEFT, RIGHT, FLAT
from tkinter.ttk import Combobox, Checkbutton, Style, Treeview, Scrollbar
from tkinter.scrolledtext import ScrolledText
from tkinter import Toplevel, Frame, Label, Button, Entry
from PIL.Image import open as pil_open, Resampling
from PIL.ImageTk import PhotoImage
from threading import Thread
from psutil import cpu_percent, virtual_memory, NoSuchProcess, AccessDenied
from time import sleep
from os import path as os_path, listdir, getcwd
from os.path import isdir, isfile, join as path_join, dirname, basename
from logging import getLogger, info, warning, error
from security_utils import sanitize_log_input, sanitize_html_output, validate_file_path, secure_filename, SecurityConfig

class UltimateAgentGUI:
    def _apply_voice_setting(self):
        try:
            if hasattr(self.agent_handle, 'config') and self.agent_handle.config:
                self.agent_handle.config.set('use_voice', self.voice_var.get())
                self.agent_handle.config.save_config()
                self.add_message("System", f"Voice output {'enabled' if self.voice_var.get() else 'disabled'}.")
            else:
                self.add_message("System", f"Voice setting updated to {'enabled' if self.voice_var.get() else 'disabled'} (demo mode).")
        except Exception as e:
            error(f"Could not apply voice setting: {sanitize_log_input(str(e))}")
            self.add_message("System", f"Could not apply voice setting: {str(e)}")

    def _apply_settings(self, new_model):
        try:
            if hasattr(self.agent_handle, 'config') and self.agent_handle.config:
                self.agent_handle.config.set('llm_model', new_model)
                self.agent_handle.config.save_config()
                self.add_message("System", f"LLM model switched to: {sanitize_html_output(new_model)}")
            else:
                self.add_message("System", f"Model setting updated to: {sanitize_html_output(new_model)} (demo mode)")
        except Exception as e:
            error(f"Failed to apply settings: {sanitize_log_input(str(e))}")
            self.add_message("System", f"Error switching model: {str(e)}")

    def __init__(self, agent_handle, test_mode=False):
        self.agent_handle = agent_handle
        self.test_mode = test_mode
        self.theme = 'cyberpunk'
        if not self.test_mode:
            self.root = Tk()
            self.root.title("ULTRON 3.0 - Ultimate Cyberpunk Interface")
            self.root.geometry("1280x720")
            self.root.minsize(1024, 600)
            self.root.configure(bg='#000000')
            self.image_cache = {}
            self._load_images()
            self._create_main_layout()
            self._start_monitoring()
        else:
            self.root = None
            self.image_cache = {}

    def _load_images(self):
        image_paths = {
            "background": "resources/images/image-15-1280x717.png",
            "avatar": "resources/images/ChatGPT Image Jul 29, 2025, 02_32_42 AM.png",
            "tools_bg": "resources/images/PDA-1280x1280.png",
            "file_browser_bg": "resources/images/JussiK_point_and_click_game_user_interface_7449bd55-0ef8-482c-ad72-10aebcf8e773-1320x880.png.webp"
        }
        for name, image_path in image_paths.items():
            try:
                if os_path.exists(image_path) and SecurityConfig.is_safe_file_extension(image_path):
                    img = pil_open(image_path)
                    self.image_cache[name] = img
                else:
                    warning(f"Image not found or unsafe: {sanitize_log_input(image_path)}")
                    self.image_cache[name] = None
            except Exception as e:
                error(f"Failed to load image {name}: {sanitize_log_input(str(e))}")
                self.image_cache[name] = None

    def _create_main_layout(self):
        # Background Canvas
        self.bg_canvas = Canvas(self.root, highlightthickness=0)
        self.bg_canvas.pack(fill=BOTH, expand=True)

        if self.image_cache.get("background"):
            # Cache resized image to avoid repeated operations
            if not hasattr(self, '_cached_bg_photo'):
                bg_img_pil = self.image_cache["background"].resize((1280, 720), Resampling.LANCZOS)
                self._cached_bg_photo = PhotoImage(bg_img_pil)
            self.bg_canvas.create_image(0, 0, image=self._cached_bg_photo, anchor="nw")
        else:
             self.bg_canvas.configure(bg='#0a0a2a')

        # --- Main Content Area ---
        # This frame will hold the chat, input, and avatar
        content_frame = Frame(self.bg_canvas, bg='#000000', bd=0, highlightthickness=0)
        content_frame.place(relx=0.5, rely=0.5, relwidth=0.7, relheight=0.8, anchor='center')

        # Avatar with caching
        if self.image_cache.get("avatar"):
            if not hasattr(self, '_cached_avatar_photo'):
                avatar_img_pil = self.image_cache["avatar"].resize((100, 100), Resampling.LANCZOS)
                self._cached_avatar_photo = PhotoImage(avatar_img_pil)
            avatar_label = Label(content_frame, image=self._cached_avatar_photo, bg='#000000')
            avatar_label.pack(pady=10)

        # Chat History
        self.chat_history = ScrolledText(content_frame, wrap=WORD, bg='#0a0a1a', fg='#00ff00', font=("Consolas", 11), relief=FLAT, borderwidth=1, insertbackground='white')
        self.chat_history.pack(padx=20, pady=10, fill=BOTH, expand=True)
        self.chat_history.config(state=DISABLED)

        # --- User Input with Transparent Look ---
        # A frame provides the visible border for our input area.
        input_area_frame = Frame(content_frame, bg='#00ff00', bd=1, relief='sunken')
        input_area_frame.pack(padx=20, pady=10, fill=X, ipady=1)

        # The actual Entry widget has no border and a background matching the content frame,
        # giving the illusion of typing directly onto the surface.
        self.user_input = Entry(
            input_area_frame,
            bg='#0a0a1a',          # Matches the chat history background for a seamless look
            fg='#00ff00',          # Bright green text
            font=("Consolas", 12),
            relief='flat',         # No 3D border on the entry itself
            borderwidth=0,
            highlightthickness=0,  # No focus highlight
            insertbackground='white' # A visible cursor
        )
        self.user_input.pack(fill=X, expand=True, ipady=8, padx=2, pady=2)
        self.user_input.bind("<Return>", self.send_message)

        # --- Bottom Buttons ---
        button_frame = Frame(self.bg_canvas, bg='#000000', bd=0, highlightthickness=0)
        button_frame.place(relx=0.5, rely=0.95, anchor='center')

        Button(button_frame, text="Tools Menu", command=self._open_tools_menu, bg='#1a1a1a', fg='#00ff00', relief=FLAT).pack(side=LEFT, padx=10)
        Button(button_frame, text="File Browser", command=self._open_file_browser, bg='#1a1a1a', fg='#00ff00', relief=FLAT).pack(side=LEFT, padx=10)
        Button(button_frame, text="Settings", command=self._open_settings_panel, bg='#1a1a1a', fg='#00ff00', relief=FLAT).pack(side=LEFT, padx=10)

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
        tools_window.geometry("450x600")
        tools_window.configure(bg="#000000")
        tools_window.transient(self.root)

        bg_image_pil = self.image_cache.get("tools_bg")
        if bg_image_pil:
            bg_image_pil = bg_image_pil.resize((450, 600), Resampling.LANCZOS)
            bg_photo = PhotoImage(bg_image_pil)
            bg_label = Label(tools_window, image=bg_photo)
            bg_label.image = bg_photo
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        Label(tools_window, text="[ AGENT TOOLKIT ]", fg="#28ff28", bg="#000000", font=("Consolas", 16, "bold")).pack(pady=15)

        # Refresh button for tools
        refresh_btn = Button(tools_window, text="Refresh", command=lambda: self._refresh_tools_menu(tools_window), bg="#1a1a1a", fg="#00ff00", relief=FLAT)
        refresh_btn.pack(pady=5)

        self._populate_tools_menu(tools_window)

    def _refresh_tools_menu(self, tools_window):
        # More efficient refresh - only update the tools canvas
        for widget in tools_window.winfo_children():
            if isinstance(widget, Canvas):
                widget.destroy()
        self._populate_tools_menu(tools_window)

    def _populate_tools_menu(self, tools_window):
        canvas = Canvas(tools_window, bg="#000000", highlightthickness=0)
        canvas.pack(fill='both', expand=True, padx=20, pady=10)
        tools_frame = Frame(canvas, bg='#051005', bd=1, relief='solid')
        canvas.create_window((0, 0), window=tools_frame, anchor='nw')
        try:
            tools = self.agent_handle.list_tools() if hasattr(self.agent_handle, 'list_tools') else []
            if not tools:
                tools = [{'name': 'screenshot', 'description': 'Take a screenshot.'}, {'name': 'list_files', 'description': 'List files in a directory.'}]
        except Exception as e:
            tools = []
            error(f"Could not fetch tools from agent: {sanitize_log_input(str(e))}")
        for i, tool in enumerate(tools):
            tool_name = tool.get('name', 'Unknown Tool')
            tool_desc = tool.get('description', 'No description available.')
            tool_button = Button(tools_frame, text=tool_name,
                                 bg='#102010', fg='#33ff33',
                                 relief='raised', borderwidth=1,
                                 font=("Consolas", 10, "bold"),
                                 command=lambda t=tool_name: self._run_tool_command(t))
            tool_button.grid(row=i, column=0, sticky='ew', padx=10, pady=5)
            desc_label = Label(tools_frame, text=tool_desc,
                               wraplength=280, justify='left',
                               bg='#051005', fg='#77ff77',
                               font=("Consolas", 9))
            desc_label.grid(row=i, column=1, sticky='w', padx=10)
        tools_frame.columnconfigure(1, weight=1)

    def _run_tool_command(self, tool_name: str):
        command = f"execute the {tool_name} tool"
        self.add_message("User (Tool)", command)
        threading.Thread(target=self._get_agent_response, args=(command,), daemon=True).start()

    def _open_settings_panel(self):
        settings_window = Toplevel(self.root)
        settings_window.title("Agent Settings")
        settings_window.geometry("500x500")
        settings_window.configure(bg="#0a0a2a")
        settings_window.transient(self.root)

        Label(settings_window, text="[ AGENT SETTINGS ]", fg="#ff00ff", bg="#0a0a2a", font=("Consolas", 14, "bold")).pack(pady=20)

        # Model Switching
        model_frame = Frame(settings_window, bg='#0a0a2a')
        model_frame.pack(pady=10, padx=20, fill='x')
        Label(model_frame, text="Active LLM Model:", bg='#0a0a2a', fg='#00ff00').pack(side=tk.LEFT, padx=5)
        try:
            if hasattr(self.agent_handle, 'config'):
                models = list(self.agent_handle.config.get('ollama_models', ['qwen2.5:latest', 'llama3.2:latest']))
                current_model = self.agent_handle.config.get('llm_model', models[0])
            else:
                models = ['qwen2.5:latest', 'llama3.2:latest', 'hermes3:latest', 'phi-3-mini']
                current_model = models[0]
        except Exception as e:
            error(f"Could not get models from agent config: {sanitize_log_input(str(e))}")
            models = ['qwen2.5:latest', 'llama3.2:latest']
            current_model = models[0]
        self.model_var = tk.StringVar(value=current_model)
        model_dropdown = Combobox(model_frame, textvariable=self.model_var, values=models, state='readonly')
        model_dropdown.pack(side=tk.LEFT, padx=5, fill='x', expand=True)
        Button(settings_window, text="Apply & Save Settings",
               command=lambda: self._apply_settings(self.model_var.get()),
               bg='#1f1f7a', fg='#ffffff', relief='flat').pack(pady=20)

        # Theme toggle
        theme_frame = Frame(settings_window, bg='#0a0a2a')
        theme_frame.pack(pady=10, padx=20, fill='x')
        Label(theme_frame, text="Theme:", bg='#0a0a2a', fg='#00ff00').pack(side=tk.LEFT, padx=5)
        self.theme_var = tk.StringVar(value=self.theme)
        theme_dropdown = Combobox(theme_frame, textvariable=self.theme_var, values=['cyberpunk', 'dark'], state='readonly')
        theme_dropdown.pack(side=tk.LEFT, padx=5, fill='x', expand=True)
        Button(settings_window, text="Apply Theme", command=self._apply_theme, bg='#1f1f7a', fg='#ffffff', relief='flat').pack(pady=10)

        # Voice toggle
        voice_frame = Frame(settings_window, bg='#0a0a2a')
        voice_frame.pack(pady=10, padx=20, fill='x')
        Label(voice_frame, text="Voice Output:", bg='#0a0a2a', fg='#00ff00').pack(side=tk.LEFT, padx=5)
        try:
            voice_enabled = self.agent_handle.config.get('use_voice', False) if hasattr(self.agent_handle, 'config') else False
        except:
            voice_enabled = False
        self.voice_var = tk.BooleanVar(value=voice_enabled)
        voice_checkbox = Checkbutton(voice_frame, variable=self.voice_var, text="Enabled")
        voice_checkbox.pack(side=tk.LEFT, padx=5)
        Button(settings_window, text="Apply Voice Setting", command=self._apply_voice_setting, bg='#1f1f7a', fg='#ffffff', relief='flat').pack(pady=10)

    def _apply_theme(self):
        self.theme = self.theme_var.get()
        # You can expand this to actually change colors dynamically
        self.add_message("System", f"Theme set to: {self.theme}")

    def _apply_voice_setting(self):
        self.agent_handle.config.set('use_voice', self.voice_var.get())
        self.agent_handle.config.save_config()
        self.add_message("System", f"Voice output {'enabled' if self.voice_var.get() else 'disabled'}.")

    def _apply_settings(self, new_model):
        try:
            if hasattr(self.agent_handle, 'config') and self.agent_handle.config:
                self.agent_handle.config.set('llm_model', new_model)
                self.agent_handle.config.save_config()
                self.add_message("System", f"LLM model switched to: {sanitize_html_output(new_model)}")
        except Exception as e:
            error(f"Failed to apply settings: {sanitize_log_input(str(e))}")
            self.add_message("System", f"Error switching model: {str(e)}")

    def _open_file_browser(self):
        browser_window = Toplevel(self.root)
        browser_window.title("File System Navigator")
        browser_window.geometry("800x600")
        browser_window.configure(bg="#0a0a2a")

        tree_frame = Frame(browser_window)
        tree_frame.pack(pady=10, padx=10, fill='both', expand=True)

        style = Style()
        style.configure("Treeview", background="#0a0a2a", foreground="#00ff00", fieldbackground="#0a0a2a", rowheight=25)
        style.map('Treeview', background=[('selected', '#1f1f7a')])

        self.file_tree = Treeview(tree_frame)
        self.file_tree.pack(side='left', fill='both', expand=True)

        scrollbar = Scrollbar(tree_frame, orient="vertical", command=self.file_tree.yview)
        scrollbar.pack(side=RIGHT, fill='y')
        self.file_tree.configure(yscrollcommand=scrollbar.set)

        self._populate_file_tree(self.file_tree, getcwd())

        self.file_tree.bind("<Double-1>", self._on_file_tree_double_click)
        self.file_tree.bind('<<TreeviewOpen>>', self._on_node_expand)

    def _populate_file_tree(self, tree, path):
        for i in tree.get_children():
            tree.delete(i)

        parent_path = dirname(path)
        self._insert_node(tree, '', f'.. ({basename(parent_path)})', parent_path)
        self._populate_file_tree_branch(tree, '', path)

    def _populate_file_tree_branch(self, tree, parent_id, file_path):
        try:
            # Validate path to prevent traversal attacks
            if not validate_file_path(file_path) or not isdir(file_path):
                return

            try:
                items = sorted(listdir(file_path), key=lambda s: s.lower())
                dirs = [i for i in items if isdir(path_join(file_path, i))]
                files = [i for i in items if isfile(path_join(file_path, i))]

                for item in dirs + files:
                    try:
                        secure_item = secure_filename(item)
                        abspath = path_join(file_path, secure_item)
                        if validate_file_path(abspath):
                            self._insert_node(tree, parent_id, secure_item, abspath)
                    except (OSError, PermissionError) as e:
                        warning(f"Could not access {sanitize_log_input(item)}: {sanitize_log_input(str(e))}")
            except PermissionError:
                self._insert_node(tree, parent_id, f"[Access Denied] {basename(file_path)}", file_path)
        except (OSError, ValueError) as e:
            error(f"Error reading path: {sanitize_log_input(str(e))}", exc_info=True)
            self._insert_node(tree, parent_id, f"[Error] {basename(file_path)}", file_path)

    def _insert_node(self, tree, parent, text, abspath):
        # Sanitize text for display
        safe_text = sanitize_html_output(text)
        node = tree.insert(parent, 'end', text=safe_text, open=False, values=[abspath])
        if isdir(abspath):
            tree.insert(node, 'end')

    def _on_node_expand(self, event):
        try:
            node_id = self.file_tree.focus()
            if not node_id:
                return

            node_path = self.file_tree.item(node_id)['values'][0]

            # Validate path before expanding
            if not validate_file_path(node_path):
                warning(f"Invalid path for expansion: {sanitize_log_input(node_path)}")
                return

            children = self.file_tree.get_children(node_id)
            if children and self.file_tree.item(children[0])['text'] == '':
                self.file_tree.delete(*children)
                self._populate_file_tree_branch(self.file_tree, node_id, node_path)
        except Exception as e:
            error(f"Error expanding node: {sanitize_log_input(str(e))}")

    def _on_file_tree_double_click(self, event):
        item_id = self.file_tree.identify_row(event.y)
        if not item_id:
            return

        file_path = self.file_tree.item(item_id)['values'][0]

        # Validate path and check security
        if not validate_file_path(file_path):
            warning(f"Invalid file path: {sanitize_log_input(file_path)}")
            return

        if isdir(file_path):
            self._populate_file_tree(self.file_tree, file_path)
        elif isfile(file_path) and SecurityConfig.is_safe_file_extension(file_path) and SecurityConfig.is_safe_file_size(file_path):
            safe_path = sanitize_html_output(file_path)
            command = f"read the file at \"{safe_path}\""
            self.add_message("User (File Browser)", command)
            Thread(target=self._get_agent_response, args=(command,), daemon=True).start()
        else:
            self.add_message("System", "File type not allowed or file too large")

    def send_message(self, event=None):
        message = self.user_input.get()
        if message.strip():
            self.add_message("User", message)
            self.user_input.delete(0, tk.END)
            Thread(target=self._get_agent_response, args=(message,), daemon=True).start()

    def _get_agent_response(self, message):
        response = self.agent_handle.handle_text(message)
        self.root.after(0, self.add_message, "Ultron", response)

    def add_message(self, sender, message):
        # Sanitize message content for display
        safe_sender = sanitize_html_output(str(sender))
        safe_message = sanitize_html_output(str(message))

        self.chat_history.config(state=NORMAL)
        self.chat_history.insert(END, f"{safe_sender} > {safe_message}\n{'-'*90}\n")
        self.chat_history.config(state=DISABLED)
        self.chat_history.yview(END)

    def _start_monitoring(self):
        def update_stats():
            while True:
                try:
                    cpu = cpu_percent()
                    ram = virtual_memory().percent
                    self.root.after(0, self.cpu_label.config, {'text': f"CPU: {cpu:.1f}%"})
                    self.root.after(0, self.ram_label.config, {'text': f"RAM: {ram:.1f}%"})
                except (NoSuchProcess, AccessDenied):
                    pass # Ignore errors if process closes during monitoring
                except Exception as e:
                    error(f"GUI monitoring error: {sanitize_log_input(str(e))}")
                sleep(2)

        monitor_thread = Thread(target=update_stats, daemon=True)
        monitor_thread.start()

    def run(self):
        if not self.test_mode:
            self.root.mainloop()

# Example for testing
if __name__ == '__main__':
    class MockAgent:
        def handle_text(self, text):
            sleep(0.5)  # Reduced delay for better responsiveness
            return f"SYSTEM COMMAND RECEIVED: '{text}'. Executing..."

    # Make sure to have the image files in a 'resources/images' directory
    if not os_path.exists("resources/images"):
        from os import makedirs
        makedirs("resources/images")
        print("Created 'resources/images' directory. Please add your GUI images there.")

    from logging import basicConfig, INFO
    basicConfig(level=INFO)
    gui = UltimateAgentGUI(MockAgent())
    gui.run()
