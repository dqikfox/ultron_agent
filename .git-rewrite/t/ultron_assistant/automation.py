# automation.py
import os
import subprocess
import logging
import webbrowser
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import pyautogui and handle potential import errors
try:
    import pyautogui
    # Configure PyAutoGUI safety settings
    pyautogui.FAILSAFE = True  # Enable fail-safe (move mouse to corner to stop)
    pyautogui.PAUSE = 0.1     # Small pause between actions for safety
    PYAUTOGUI_AVAILABLE = True
    logger.info("PyAutoGUI loaded successfully with safety settings")
except ImportError:
    logger.warning("pyautogui not available. Some automation features will be disabled.")
    PYAUTOGUI_AVAILABLE = False

def run_command(command: str) -> str:
    """
    Enhanced natural-language parser for automation commands.
    Returns a short status string that will be spoken back to the user.
    
    Args:
        command: Natural language command string
        
    Returns:
        str: Status message describing the action taken
    """
    cmd = command.lower().strip()
    logger.info(f"Processing automation command: {cmd}")

    # ---------- Application Opening ----------
    if cmd.startswith("open "):
        app = cmd[5:].strip()
        return open_application(app)

    # ---------- Text Input ----------
    if cmd.startswith("type "):
        text = cmd[5:].strip()
        return type_text(text)

    # ---------- Screenshot ----------
    if any(keyword in cmd for keyword in ["screenshot", "screen shot", "capture screen"]):
        if "region" in cmd:
            # Extract region coordinates from command like "screenshot region 100,100,500,400"
            parts = cmd.split("region")
            if len(parts) > 1:
                coords = parts[1].strip()
                return take_screenshot_region(coords)
        return take_screenshot()
    
    # ---------- Pixel Analysis ----------
    if cmd.startswith("get pixel color ") or cmd.startswith("pixel color "):
        coords = cmd.split("color ", 1)[1].strip()
        return get_pixel_color(coords)
    
    if cmd.startswith("check pixel "):
        # Command like "check pixel 100,200 red" or "check pixel 100,200 255,0,0"
        parts = cmd[12:].strip().split()
        if len(parts) >= 2:
            coords = parts[0]
            color = " ".join(parts[1:])
            return check_pixel_color(coords, color)
        return "Invalid format. Use: 'check pixel 100,200 red' or 'check pixel 100,200 255,0,0'"

    # ---------- Web Search ----------
    if cmd.startswith("search for ") or cmd.startswith("google "):
        query = cmd[11:].strip() if cmd.startswith("search for ") else cmd[7:].strip()
        return web_search(query)

    # ---------- System Volume Control ----------
    if "volume up" in cmd or "increase volume" in cmd:
        return adjust_volume("up")
    if "volume down" in cmd or "decrease volume" in cmd:
        return adjust_volume("down")
    if "mute" in cmd or "unmute" in cmd:
        return toggle_mute()

    # ---------- Mouse Control ----------
    if cmd.startswith("click "):
        target = cmd[6:].strip()
        return mouse_click(target)
    
    if cmd.startswith("move mouse to "):
        coords = cmd[14:].strip()
        # Check for easing function in command
        if " with " in coords:
            coord_part, easing = coords.split(" with ", 1)
            return move_mouse_with_easing(coord_part, easing.strip())
        return move_mouse(coords)
    
    if cmd.startswith("move smooth to "):
        coords = cmd[15:].strip()
        return move_mouse_smooth(coords)
    
    if cmd.startswith("drag to "):
        coords = cmd[8:].strip()
        return drag_mouse(coords)
    
    if "right click" in cmd:
        return right_click()
    
    if "double click" in cmd:
        return double_click()
    
    if "scroll up" in cmd:
        clicks = extract_number_from_command(cmd)
        return scroll("up", clicks)
    if "scroll down" in cmd:
        clicks = extract_number_from_command(cmd)
        return scroll("down", clicks)
    if "scroll left" in cmd:
        clicks = extract_number_from_command(cmd)
        return scroll("left", clicks)
    if "scroll right" in cmd:
        clicks = extract_number_from_command(cmd)
        return scroll("right", clicks)

    # ---------- Image Recognition ----------
    if cmd.startswith("find image ") or cmd.startswith("locate "):
        image_name = cmd.split(" ", 2)[2].strip() if cmd.startswith("find image ") else cmd[7:].strip()
        return find_image_on_screen(image_name)
    
    if cmd.startswith("click image "):
        image_name = cmd[12:].strip()
        return click_image_on_screen(image_name)
    
    if cmd.startswith("find all "):
        image_name = cmd[9:].strip()
        return find_all_images_on_screen(image_name)
    
    if cmd.startswith("locate center "):
        image_name = cmd[14:].strip()
        return locate_center_on_screen(image_name)

    # ---------- Advanced Keyboard Shortcuts ----------
    if cmd.startswith("press "):
        keys = cmd[6:].strip()
        return press_keys(keys)
    
    if cmd.startswith("hotkey "):
        hotkey_combo = cmd[7:].strip()
        return press_hotkey(hotkey_combo)
    
    if cmd.startswith("write "):
        text = cmd[6:].strip()
        # Check for interval specification
        if " interval " in text:
            text_part, interval_part = text.split(" interval ", 1)
            try:
                interval = float(interval_part.strip())
                return write_text_with_interval(text_part.strip(), interval)
            except ValueError:
                return "Invalid interval. Use format: 'write hello interval 0.1'"
        return write_text(text)
    
    if cmd.startswith("hold ") and " and " in cmd:
        # Command like "hold ctrl and type hello"
        parts = cmd.split(" and ", 1)
        hold_key = parts[0][5:].strip()  # Remove "hold "
        action = parts[1].strip()
        return hold_key_and_action(hold_key, action)

    # ---------- System Information ----------
    if "mouse position" in cmd or "cursor position" in cmd:
        return get_mouse_position()
    
    if "screen size" in cmd or "resolution" in cmd:
        return get_screen_size()

    # ---------- Message Boxes ----------
    if cmd.startswith("show alert "):
        message = cmd[11:].strip()
        return show_alert(message)
    
    if cmd.startswith("ask question "):
        question = cmd[13:].strip()
        return ask_question(question)
    
    if cmd.startswith("ask input ") or cmd.startswith("prompt "):
        prompt_text = cmd[10:].strip() if cmd.startswith("ask input ") else cmd[7:].strip()
        return ask_input(prompt_text)
    
    if cmd.startswith("ask password"):
        prompt_text = cmd[12:].strip() if len(cmd) > 12 else "Enter password:"
        return ask_password(prompt_text)

    # ---------- Help and Information ----------
    if "help" in cmd or "commands" in cmd or "what can you do" in cmd:
        return """🤖 Ultron Assistant Enhanced Automation Commands:

📱 APPLICATIONS:
• open [app] - Opens applications (notepad, calculator, chrome, etc.)

⌨️ TEXT & KEYBOARD:
• type [text] - Types text quickly
• write [text] - Types text using write() function
• write [text] interval [seconds] - Types with custom interval (e.g., 'write hello interval 0.1')
• press [key] - Single key press (enter, space, etc.)
• hotkey [combo] - Key combinations (ctrl+c, alt+tab, ctrl+shift+s)
• hold [key] and [action] - Hold key while performing action (e.g., 'hold ctrl and type hello')

🖱️ ADVANCED MOUSE CONTROL:
• click - Left click at current position
• right click - Right click at current position  
• double click - Double click at current position
• move mouse to [x,y] - Move mouse to coordinates
• move mouse to [x,y] with [easing] - Move with easing (easeInQuad, easeOutBounce, etc.)
• move smooth to [x,y] - Move with smooth easing
• drag to [x,y] - Drag from current position to coordinates
• scroll up/down [number] - Scroll vertically (e.g., 'scroll up 5')
• scroll left/right [number] - Scroll horizontally

🖼️ ENHANCED IMAGE RECOGNITION:
• find image [name] - Locate image on screen
• click image [name] - Find and click on image
• find all [name] - Find all instances of image
• locate center [name] - Get center coordinates of image

� ADVANCED SCREENSHOTS:
• screenshot/take screenshot - Capture full screen
• screenshot region [left,top,width,height] - Capture specific region

🎨 PIXEL ANALYSIS:
• get pixel color [x,y] - Get RGB color of pixel
• check pixel [x,y] [color] - Check if pixel matches color (e.g., 'check pixel 100,200 red')

�📱 SYSTEM INFO:
• mouse position - Get current mouse coordinates
• screen size - Get screen resolution
• what time - Current time
• system info - Computer information

🪟 WINDOW MANAGEMENT:
• minimize/maximize/close window - Window controls

🔊 VOLUME CONTROL:
• volume up/down - Adjust system volume
• mute - Toggle mute

🌐 WEB SEARCH:
• search for [query] - Google search

💬 ENHANCED DIALOGS:
• show alert [message] - Show alert dialog
• ask question [text] - Ask yes/no question
• ask input [prompt] - Ask for text input
• ask password [prompt] - Ask for password input

📁 FILES:
• create folder [name] - Create new folder

🎛️ EASING FUNCTIONS:
Available easing types for smooth mouse movement:
• linear, easeInQuad, easeOutQuad, easeInOutQuad
• easeInCubic, easeOutCubic, easeInOutCubic
• easeInQuart, easeOutQuart, easeInOutQuart
• easeInSine, easeOutSine, easeInOutSine
• easeInExpo, easeOutExpo, easeInOutExpo
• easeInCirc, easeOutCirc, easeInOutCirc
• easeInElastic, easeOutElastic, easeInOutElastic
• easeInBack, easeOutBack, easeInOutBack
• easeInBounce, easeOutBounce, easeInOutBounce

💡 SAFETY: Move mouse to screen corner to emergency stop any automation!
💡 EXAMPLES: 
  - 'move mouse to 500,300 with easeInBounce'
  - 'write Hello World interval 0.2'
  - 'screenshot region 100,100,800,600'
  - 'hold shift and click'
  - 'scroll up 10'"""

    # ---------- Keyboard Shortcuts ----------
    if cmd.startswith("press "):
        keys = cmd[6:].strip()
        return press_keys(keys)

    # ---------- Window Management ----------
    if "minimize window" in cmd or "minimize" in cmd:
        return minimize_window()
    if "maximize window" in cmd or "maximize" in cmd:
        return maximize_window()
    if "close window" in cmd or "close app" in cmd:
        return close_window()

    # ---------- System Information ----------
    if "what time" in cmd or "current time" in cmd:
        return get_current_time()
    
    if "system info" in cmd or "computer info" in cmd:
        return get_system_info()

    # ---------- File Operations ----------
    if cmd.startswith("create folder ") or cmd.startswith("make folder "):
        folder_name = cmd.split("folder ", 1)[1].strip()
        return create_folder(folder_name)

    # ---------- Fallback ----------
    return f"""Sorry, I didn't understand the automation command: '{command}'. 

🚀 ENHANCED AUTOMATION COMMANDS:

📱 Apps: 'open notepad', 'open calculator'
⌨️ Text: 'type hello', 'write text interval 0.1', 'hold ctrl and type hello'
📸 Screenshots: 'screenshot', 'screenshot region 100,100,500,400'
🌐 Web: 'search for python'
🖱️ Mouse: 'click', 'move mouse to 100,200 with easeInBounce', 'scroll up 5'
🖼️ Images: 'find image button.png', 'click image submit.png', 'find all icons.png'
⌨️ Keyboard: 'press enter', 'hotkey ctrl+c', 'hotkey alt+tab'
🎨 Pixels: 'get pixel color 100,200', 'check pixel 100,200 red'
📱 System: 'mouse position', 'screen size'
🪟 Windows: 'minimize', 'maximize', 'close window'
💬 Messages: 'show alert Hello!', 'ask question Save?', 'ask input Your name?', 'ask password'
🔊 Volume: 'volume up', 'volume down', 'mute'

Type 'help' for complete command list with examples!"""

def open_application(app_name: str) -> str:
    """Open an application by name."""
    try:
        # Enhanced application mapping
        app_mapping = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "paint": "mspaint.exe",
            "explorer": "explorer.exe",
            "cmd": "cmd.exe",
            "command prompt": "cmd.exe",
            "powershell": "powershell.exe",
            "task manager": "taskmgr.exe",
            "control panel": "control.exe",
            "registry": "regedit.exe",
            "chrome": find_chrome_path(),
            "firefox": find_firefox_path(),
            "edge": "msedge.exe",
            "vscode": find_vscode_path(),
            "visual studio code": find_vscode_path(),
        }
        
        exe_path = app_mapping.get(app_name.lower())
        if exe_path:
            if exe_path and os.path.exists(exe_path) or not exe_path.startswith("C:"):
                subprocess.Popen(exe_path, shell=True)
                return f"Opening {app_name.title()}"
            else:
                return f"{app_name.title()} not found on this system"
        else:
            # Try to run it directly as a command
            subprocess.Popen(app_name, shell=True)
            return f"Attempting to open {app_name}"
            
    except Exception as e:
        logger.error(f"Error opening application {app_name}: {e}")
        return f"Failed to open {app_name}: {str(e)}"

def find_chrome_path() -> Optional[str]:
    """Find Chrome installation path."""
    common_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    for path in common_paths:
        if os.path.exists(path):
            return path
    return None

def find_firefox_path() -> Optional[str]:
    """Find Firefox installation path."""
    common_paths = [
        r"C:\Program Files\Mozilla Firefox\firefox.exe",
        r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
    ]
    for path in common_paths:
        if os.path.exists(path):
            return path
    return None

def find_vscode_path() -> Optional[str]:
    """Find VS Code installation path."""
    common_paths = [
        r"C:\Users\{}\AppData\Local\Programs\Microsoft VS Code\Code.exe".format(os.getenv("USERNAME")),
        r"C:\Program Files\Microsoft VS Code\Code.exe",
        r"C:\Program Files (x86)\Microsoft VS Code\Code.exe",
    ]
    for path in common_paths:
        if os.path.exists(path):
            return path
    return "code"  # Fallback to PATH

def type_text(text: str) -> str:
    """Type text using pyautogui."""
    if not PYAUTOGUI_AVAILABLE:
        return "Text typing not available - pyautogui not installed"
    
    try:
        # Add a small delay to allow user to position cursor
        time.sleep(1)
        pyautogui.write(text, interval=0.05)
        return f"Typed: {text[:50]}{'...' if len(text) > 50 else ''}"
    except Exception as e:
        logger.error(f"Error typing text: {e}")
        return f"Failed to type text: {str(e)}"

def take_screenshot() -> str:
    """Take a screenshot and save it."""
    if not PYAUTOGUI_AVAILABLE:
        return "Screenshot not available - pyautogui not installed"
    
    try:
        # Create screenshots directory
        screenshots_dir = Path.home() / "Pictures" / "UltronScreenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        # Take screenshot
        img = pyautogui.screenshot()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = screenshots_dir / f"ultron_screenshot_{timestamp}.png"
        img.save(filename)
        
        logger.info(f"Screenshot saved to {filename}")
        return f"Screenshot saved to {filename.name}"
    except Exception as e:
        logger.error(f"Error taking screenshot: {e}")
        return f"Failed to take screenshot: {str(e)}"

def web_search(query: str) -> str:
    """Perform a web search."""
    try:
        # URL encode the query
        import urllib.parse
        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://www.google.com/search?q={encoded_query}"
        webbrowser.open(url)
        return f"Searching Google for: {query}"
    except Exception as e:
        logger.error(f"Error performing web search: {e}")
        return f"Failed to search: {str(e)}"

def adjust_volume(direction: str) -> str:
    """Adjust system volume."""
    if not PYAUTOGUI_AVAILABLE:
        return "Volume control not available - pyautogui not installed"
    
    try:
        if direction.lower() == "up":
            pyautogui.press("volumeup")
            return "Volume increased"
        elif direction.lower() == "down":
            pyautogui.press("volumedown")
            return "Volume decreased"
        else:
            return "Invalid volume direction"
    except Exception as e:
        logger.error(f"Error adjusting volume: {e}")
        return f"Failed to adjust volume: {str(e)}"

def toggle_mute() -> str:
    """Toggle system mute."""
    if not PYAUTOGUI_AVAILABLE:
        return "Mute control not available - pyautogui not installed"
    
    try:
        pyautogui.press("volumemute")
        return "Toggled mute"
    except Exception as e:
        logger.error(f"Error toggling mute: {e}")
        return f"Failed to toggle mute: {str(e)}"

def mouse_click(target: str) -> str:
    """Perform mouse click."""
    if not PYAUTOGUI_AVAILABLE:
        return "Mouse control not available - pyautogui not installed"
    
    try:
        if target.lower() == "center" or target.lower() == "middle":
            screen_width, screen_height = pyautogui.size()
            pyautogui.click(screen_width // 2, screen_height // 2)
            return "Clicked center of screen"
        else:
            # For now, just click current mouse position
            pyautogui.click()
            return "Clicked current mouse position"
    except Exception as e:
        logger.error(f"Error clicking: {e}")
        return f"Failed to click: {str(e)}"

def scroll(direction: str) -> str:
    """Scroll in specified direction."""
    if not PYAUTOGUI_AVAILABLE:
        return "Scrolling not available - pyautogui not installed"
    
    try:
        if direction.lower() == "up":
            pyautogui.scroll(3)
            return "Scrolled up"
        elif direction.lower() == "down":
            pyautogui.scroll(-3)
            return "Scrolled down"
        else:
            return "Invalid scroll direction"
    except Exception as e:
        logger.error(f"Error scrolling: {e}")
        return f"Failed to scroll: {str(e)}"

def press_keys(keys: str) -> str:
    """Press keyboard keys."""
    if not PYAUTOGUI_AVAILABLE:
        return "Key pressing not available - pyautogui not installed"
    
    try:
        # Handle common key combinations
        keys = keys.lower().strip()
        if "ctrl+c" in keys or "copy" in keys:
            pyautogui.hotkey('ctrl', 'c')
            return "Pressed Ctrl+C (Copy)"
        elif "ctrl+v" in keys or "paste" in keys:
            pyautogui.hotkey('ctrl', 'v')
            return "Pressed Ctrl+V (Paste)"
        elif "alt+tab" in keys:
            pyautogui.hotkey('alt', 'tab')
            return "Pressed Alt+Tab"
        elif "enter" in keys:
            pyautogui.press('enter')
            return "Pressed Enter"
        elif "escape" in keys or "esc" in keys:
            pyautogui.press('escape')
            return "Pressed Escape"
        else:
            # Try to press the key directly
            pyautogui.press(keys)
            return f"Pressed {keys}"
    except Exception as e:
        logger.error(f"Error pressing keys: {e}")
        return f"Failed to press keys: {str(e)}"

def minimize_window() -> str:
    """Minimize current window."""
    if not PYAUTOGUI_AVAILABLE:
        return "Window control not available - pyautogui not installed"
    
    try:
        pyautogui.hotkey('alt', 'f9')
        return "Minimized current window"
    except Exception as e:
        logger.error(f"Error minimizing window: {e}")
        return f"Failed to minimize window: {str(e)}"

def maximize_window() -> str:
    """Maximize current window."""
    if not PYAUTOGUI_AVAILABLE:
        return "Window control not available - pyautogui not installed"
    
    try:
        pyautogui.hotkey('alt', 'f10')
        return "Maximized current window"
    except Exception as e:
        logger.error(f"Error maximizing window: {e}")
        return f"Failed to maximize window: {str(e)}"

def close_window() -> str:
    """Close current window."""
    if not PYAUTOGUI_AVAILABLE:
        return "Window control not available - pyautogui not installed"
    
    try:
        pyautogui.hotkey('alt', 'f4')
        return "Closed current window"
    except Exception as e:
        logger.error(f"Error closing window: {e}")
        return f"Failed to close window: {str(e)}"

# ---------- Advanced Mouse Functions ----------
def move_mouse(coords: str) -> str:
    """Move mouse to specified coordinates."""
    if not PYAUTOGUI_AVAILABLE:
        return "Mouse control not available - pyautogui not installed"
    
    try:
        # Parse coordinates like "100,200" or "100 200"
        coords = coords.replace(',', ' ')
        parts = coords.split()
        if len(parts) >= 2:
            x, y = int(parts[0]), int(parts[1])
            pyautogui.moveTo(x, y, duration=0.5)
            return f"Moved mouse to ({x}, {y})"
        else:
            return "Invalid coordinates. Use format: 'move mouse to 100,200'"
    except Exception as e:
        logger.error(f"Error moving mouse: {e}")
        return f"Failed to move mouse: {str(e)}"

def drag_mouse(coords: str) -> str:
    """Drag mouse to specified coordinates."""
    if not PYAUTOGUI_AVAILABLE:
        return "Mouse control not available - pyautogui not installed"
    
    try:
        coords = coords.replace(',', ' ')
        parts = coords.split()
        if len(parts) >= 2:
            x, y = int(parts[0]), int(parts[1])
            pyautogui.dragTo(x, y, duration=1.0)
            return f"Dragged mouse to ({x}, {y})"
        else:
            return "Invalid coordinates. Use format: 'drag to 100,200'"
    except Exception as e:
        logger.error(f"Error dragging mouse: {e}")
        return f"Failed to drag mouse: {str(e)}"

def right_click() -> str:
    """Perform right click at current mouse position."""
    if not PYAUTOGUI_AVAILABLE:
        return "Mouse control not available - pyautogui not installed"
    
    try:
        pyautogui.rightClick()
        return "Right clicked"
    except Exception as e:
        logger.error(f"Error right clicking: {e}")
        return f"Failed to right click: {str(e)}"

def double_click() -> str:
    """Perform double click at current mouse position."""
    if not PYAUTOGUI_AVAILABLE:
        return "Mouse control not available - pyautogui not installed"
    
    try:
        pyautogui.doubleClick()
        return "Double clicked"
    except Exception as e:
        logger.error(f"Error double clicking: {e}")
        return f"Failed to double click: {str(e)}"

# ---------- Image Recognition Functions ----------
def find_image_on_screen(image_name: str) -> str:
    """Find an image on the screen and return its location."""
    if not PYAUTOGUI_AVAILABLE:
        return "Image recognition not available - pyautogui not installed"
    
    try:
        # Look for image file in common locations
        image_paths = [
            f"{image_name}",
            f"{image_name}.png",
            f"images/{image_name}",
            f"images/{image_name}.png",
            f"screenshots/{image_name}",
            f"screenshots/{image_name}.png"
        ]
        
        for image_path in image_paths:
            if os.path.exists(image_path):
                location = pyautogui.locateOnScreen(image_path, confidence=0.8)
                if location:
                    center = pyautogui.center(location)
                    return f"Found '{image_name}' at ({center.x}, {center.y})"
                else:
                    return f"Image '{image_name}' not found on screen"
        
        return f"Image file '{image_name}' not found. Place image in current directory or 'images/' folder"
    except Exception as e:
        logger.error(f"Error finding image: {e}")
        return f"Failed to find image: {str(e)}"

def click_image_on_screen(image_name: str) -> str:
    """Find an image on screen and click it."""
    if not PYAUTOGUI_AVAILABLE:
        return "Image recognition not available - pyautogui not installed"
    
    try:
        image_paths = [
            f"{image_name}",
            f"{image_name}.png", 
            f"images/{image_name}",
            f"images/{image_name}.png",
            f"screenshots/{image_name}",
            f"screenshots/{image_name}.png"
        ]
        
        for image_path in image_paths:
            if os.path.exists(image_path):
                location = pyautogui.locateOnScreen(image_path, confidence=0.8)
                if location:
                    center = pyautogui.center(location)
                    pyautogui.click(center)
                    return f"Clicked on '{image_name}' at ({center.x}, {center.y})"
                else:
                    return f"Image '{image_name}' not found on screen"
        
        return f"Image file '{image_name}' not found"
    except Exception as e:
        logger.error(f"Error clicking image: {e}")
        return f"Failed to click image: {str(e)}"

# ---------- Advanced Hotkey Functions ----------
def press_hotkey(hotkey_combo: str) -> str:
    """Press a combination of keys (hotkey)."""
    if not PYAUTOGUI_AVAILABLE:
        return "Keyboard control not available - pyautogui not installed"
    
    try:
        # Parse hotkey combinations like "ctrl+c", "ctrl+shift+s", "alt+tab"
        keys = [key.strip().lower() for key in hotkey_combo.replace('+', ' ').split()]
        
        # Map common key names
        key_mapping = {
            'control': 'ctrl',
            'cmd': 'ctrl',  # For cross-platform compatibility
            'command': 'ctrl',
            'windows': 'win',
            'super': 'win'
        }
        
        mapped_keys = [key_mapping.get(key, key) for key in keys]
        
        pyautogui.hotkey(*mapped_keys)
        return f"Pressed hotkey: {' + '.join(mapped_keys)}"
    except Exception as e:
        logger.error(f"Error pressing hotkey: {e}")
        return f"Failed to press hotkey: {str(e)}"

# ---------- System Information Functions ----------
def get_mouse_position() -> str:
    """Get current mouse position."""
    if not PYAUTOGUI_AVAILABLE:
        return "Mouse position not available - pyautogui not installed"
    
    try:
        x, y = pyautogui.position()
        return f"Mouse position: ({x}, {y})"
    except Exception as e:
        logger.error(f"Error getting mouse position: {e}")
        return f"Failed to get mouse position: {str(e)}"

def get_screen_size() -> str:
    """Get screen resolution."""
    if not PYAUTOGUI_AVAILABLE:
        return "Screen size not available - pyautogui not installed"
    
    try:
        width, height = pyautogui.size()
        return f"Screen resolution: {width} x {height}"
    except Exception as e:
        logger.error(f"Error getting screen size: {e}")
        return f"Failed to get screen size: {str(e)}"

# ---------- Message Box Functions ----------
def show_alert(message: str) -> str:
    """Show an alert dialog box."""
    if not PYAUTOGUI_AVAILABLE:
        return "Alert dialogs not available - pyautogui not installed"
    
    try:
        pyautogui.alert(message, title="Ultron Assistant Alert")
        return f"Showed alert: {message}"
    except Exception as e:
        logger.error(f"Error showing alert: {e}")
        return f"Failed to show alert: {str(e)}"

def ask_question(question: str) -> str:
    """Ask a yes/no question with a dialog box."""
    if not PYAUTOGUI_AVAILABLE:
        return "Question dialogs not available - pyautogui not installed"
    
    try:
        response = pyautogui.confirm(question, title="Ultron Assistant Question", buttons=['Yes', 'No'])
        return f"Question: {question} | Answer: {response}"
    except Exception as e:
        logger.error(f"Error asking question: {e}")
        return f"Failed to ask question: {str(e)}"

def get_current_time() -> str:
    """Get current time."""
    try:
        current_time = datetime.now().strftime("%I:%M %p on %B %d, %Y")
        return f"Current time is {current_time}"
    except Exception as e:
        logger.error(f"Error getting time: {e}")
        return "Failed to get current time"

def get_system_info() -> str:
    """Get basic system information."""
    try:
        import platform
        system = platform.system()
        release = platform.release()
        machine = platform.machine()
        return f"System: {system} {release}, Architecture: {machine}"
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return "Failed to get system information"

def create_folder(folder_name: str) -> str:
    """Create a new folder on desktop."""
    try:
        desktop = Path.home() / "Desktop"
        new_folder = desktop / folder_name
        new_folder.mkdir(exist_ok=True)
        return f"Created folder '{folder_name}' on desktop"
    except Exception as e:
        logger.error(f"Error creating folder: {e}")
        return f"Failed to create folder: {str(e)}"

# ---------- Enhanced Screenshot Functions ----------
def take_screenshot_region(coords: str) -> str:
    """Take a screenshot of a specific region."""
    if not PYAUTOGUI_AVAILABLE:
        return "Screenshot not available - pyautogui not installed"
    
    try:
        # Parse coordinates like "100,100,500,400" (left, top, width, height)
        coord_parts = [int(x.strip()) for x in coords.replace(',', ' ').split()]
        if len(coord_parts) != 4:
            return "Invalid region format. Use: 'screenshot region 100,100,500,400' (left,top,width,height)"
        
        left, top, width, height = coord_parts
        timestamp = int(time.time())
        filename = f"ultron_region_screenshot_{timestamp}.png"
        
        screenshot = pyautogui.screenshot(region=(left, top, width, height))
        screenshot.save(filename)
        return f"Region screenshot saved as {filename}"
    except Exception as e:
        logger.error(f"Error taking region screenshot: {e}")
        return f"Failed to take region screenshot: {str(e)}"

# ---------- Pixel Analysis Functions ----------
def get_pixel_color(coords: str) -> str:
    """Get the RGB color of a pixel at specified coordinates."""
    if not PYAUTOGUI_AVAILABLE:
        return "Pixel analysis not available - pyautogui not installed"
    
    try:
        coord_parts = [int(x.strip()) for x in coords.replace(',', ' ').split()]
        if len(coord_parts) != 2:
            return "Invalid coordinates. Use format: 'get pixel color 100,200'"
        
        x, y = coord_parts
        pixel = pyautogui.pixel(x, y)
        
        # Handle both tuple and named tuple formats
        if hasattr(pixel, 'red'):
            # Named tuple format (newer versions)
            return f"Pixel at ({x}, {y}) has RGB color: ({pixel.red}, {pixel.green}, {pixel.blue})"
        else:
            # Tuple format (older versions)
            return f"Pixel at ({x}, {y}) has RGB color: ({pixel[0]}, {pixel[1]}, {pixel[2]})"
    except Exception as e:
        logger.error(f"Error getting pixel color: {e}")
        return f"Failed to get pixel color: {str(e)}"

def check_pixel_color(coords: str, expected_color: str) -> str:
    """Check if a pixel matches an expected color."""
    if not PYAUTOGUI_AVAILABLE:
        return "Pixel analysis not available - pyautogui not installed"
    
    try:
        coord_parts = [int(x.strip()) for x in coords.replace(',', ' ').split()]
        if len(coord_parts) != 2:
            return "Invalid coordinates. Use format: 'check pixel 100,200 red'"
        
        x, y = coord_parts
        
        # Parse expected color
        color_mapping = {
            'red': (255, 0, 0),
            'green': (0, 255, 0),
            'blue': (0, 0, 255),
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'yellow': (255, 255, 0),
            'cyan': (0, 255, 255),
            'magenta': (255, 0, 255)
        }
        
        if expected_color.lower() in color_mapping:
            target_rgb = color_mapping[expected_color.lower()]
        else:
            # Try to parse RGB values like "255,0,0"
            rgb_parts = [int(x.strip()) for x in expected_color.replace(',', ' ').split()]
            if len(rgb_parts) != 3:
                return "Invalid color format. Use color name (red, blue, etc.) or RGB values (255,0,0)"
            target_rgb = tuple(rgb_parts)
        
        # Check pixel with tolerance
        matches = pyautogui.pixelMatchesColor(x, y, target_rgb, tolerance=10)
        actual_pixel = pyautogui.pixel(x, y)
        
        # Handle both tuple and named tuple formats
        if hasattr(actual_pixel, 'red'):
            actual_rgb = f"({actual_pixel.red}, {actual_pixel.green}, {actual_pixel.blue})"
        else:
            actual_rgb = f"({actual_pixel[0]}, {actual_pixel[1]}, {actual_pixel[2]})"
        
        result = "matches" if matches else "does not match"
        return f"Pixel at ({x}, {y}) {result} color {target_rgb}. Actual: {actual_rgb}"
    except Exception as e:
        logger.error(f"Error checking pixel color: {e}")
        return f"Failed to check pixel color: {str(e)}"

# ---------- Enhanced Mouse Functions ----------
def move_mouse_with_easing(coords: str, easing: str) -> str:
    """Move mouse with easing function."""
    if not PYAUTOGUI_AVAILABLE:
        return "Mouse control not available - pyautogui not installed"
    
    try:
        coord_parts = [int(x.strip()) for x in coords.replace(',', ' ').split()]
        if len(coord_parts) != 2:
            return "Invalid coordinates. Use format: 'move mouse to 100,200 with easeInQuad'"
        
        x, y = coord_parts
        
        # Map easing function names to pyautogui functions
        easing_functions = {
            'linear': pyautogui.linear,
            'easeinquad': pyautogui.easeInQuad,
            'easeoutquad': pyautogui.easeOutQuad,
            'easeinoutquad': pyautogui.easeInOutQuad,
            'easeincubic': pyautogui.easeInCubic,
            'easeoutcubic': pyautogui.easeOutCubic,
            'easeinoutcubic': pyautogui.easeInOutCubic,
            'easeinquart': pyautogui.easeInQuart,
            'easeoutquart': pyautogui.easeOutQuart,
            'easeinoutquart': pyautogui.easeInOutQuart,
            'easeinquint': pyautogui.easeInQuint,
            'easeoutquint': pyautogui.easeOutQuint,
            'easeinoutquint': pyautogui.easeInOutQuint,
            'easeinsine': pyautogui.easeInSine,
            'easeoutsine': pyautogui.easeOutSine,
            'easeinoutsine': pyautogui.easeInOutSine,
            'easeinexpo': pyautogui.easeInExpo,
            'easeoutexpo': pyautogui.easeOutExpo,
            'easeinoutexpo': pyautogui.easeInOutExpo,
            'easeincirc': pyautogui.easeInCirc,
            'easeoutcirc': pyautogui.easeOutCirc,
            'easeinoutcirc': pyautogui.easeInOutCirc,
            'easeinelastic': pyautogui.easeInElastic,
            'easeoutelastic': pyautogui.easeOutElastic,
            'easeinoutelastic': pyautogui.easeInOutElastic,
            'easeinback': pyautogui.easeInBack,
            'easeoutback': pyautogui.easeOutBack,
            'easeinoutback': pyautogui.easeInOutBack,
            'easeinbounce': pyautogui.easeInBounce,
            'easeoutbounce': pyautogui.easeOutBounce,
            'easeinoutbounce': pyautogui.easeInOutBounce
        }
        
        easing_func = easing_functions.get(easing.lower().replace('_', ''))
        if not easing_func:
            available_easings = ', '.join(list(easing_functions.keys())[:10])
            return f"Unknown easing function '{easing}'. Available: {available_easings}..."
        
        pyautogui.moveTo(x, y, duration=1.0, tween=easing_func)
        return f"Moved mouse to ({x}, {y}) with {easing} easing"
    except Exception as e:
        logger.error(f"Error moving mouse with easing: {e}")
        return f"Failed to move mouse with easing: {str(e)}"

def move_mouse_smooth(coords: str) -> str:
    """Move mouse smoothly (using easeInOutQuad)."""
    return move_mouse_with_easing(coords, "easeInOutQuad")

def extract_number_from_command(cmd: str) -> int:
    """Extract number from command for scroll operations."""
    import re
    numbers = re.findall(r'\d+', cmd)
    return int(numbers[0]) if numbers else 3  # Default to 3 scrolls

# ---------- Enhanced Image Recognition ----------
def find_all_images_on_screen(image_name: str) -> str:
    """Find all instances of an image on screen."""
    if not PYAUTOGUI_AVAILABLE:
        return "Image recognition not available - pyautogui not installed"
    
    try:
        image_paths = [
            f"{image_name}",
            f"{image_name}.png",
            f"images/{image_name}",
            f"images/{image_name}.png",
            f"screenshots/{image_name}",
            f"screenshots/{image_name}.png"
        ]
        
        for image_path in image_paths:
            if os.path.exists(image_path):
                locations = list(pyautogui.locateAllOnScreen(image_path, confidence=0.8))
                if locations:
                    centers = [pyautogui.center(loc) for loc in locations]
                    result_text = f"Found {len(locations)} instances of '{image_name}':\n"
                    for i, center in enumerate(centers, 1):
                        result_text += f"  {i}. ({center.x}, {center.y})\n"
                    return result_text.strip()
                else:
                    return f"Image '{image_name}' not found on screen"
        
        return f"Image file '{image_name}' not found"
    except Exception as e:
        logger.error(f"Error finding all images: {e}")
        return f"Failed to find all images: {str(e)}"

def locate_center_on_screen(image_name: str) -> str:
    """Find image and return center coordinates."""
    if not PYAUTOGUI_AVAILABLE:
        return "Image recognition not available - pyautogui not installed"
    
    try:
        image_paths = [
            f"{image_name}",
            f"{image_name}.png",
            f"images/{image_name}",
            f"images/{image_name}.png",
            f"screenshots/{image_name}",
            f"screenshots/{image_name}.png"
        ]
        
        for image_path in image_paths:
            if os.path.exists(image_path):
                center = pyautogui.locateCenterOnScreen(image_path, confidence=0.8)
                if center:
                    return f"Center of '{image_name}' is at ({center.x}, {center.y})"
                else:
                    return f"Image '{image_name}' not found on screen"
        
        return f"Image file '{image_name}' not found"
    except Exception as e:
        logger.error(f"Error locating image center: {e}")
        return f"Failed to locate image center: {str(e)}"

# ---------- Enhanced Keyboard Functions ----------
def write_text(text: str) -> str:
    """Write text using pyautogui.write() function."""
    if not PYAUTOGUI_AVAILABLE:
        return "Text writing not available - pyautogui not installed"
    
    try:
        time.sleep(0.5)  # Brief delay for positioning
        pyautogui.write(text)
        return f"Wrote: {text[:50]}{'...' if len(text) > 50 else ''}"
    except Exception as e:
        logger.error(f"Error writing text: {e}")
        return f"Failed to write text: {str(e)}"

def write_text_with_interval(text: str, interval: float) -> str:
    """Write text with custom interval between characters."""
    if not PYAUTOGUI_AVAILABLE:
        return "Text writing not available - pyautogui not installed"
    
    try:
        time.sleep(0.5)  # Brief delay for positioning
        pyautogui.write(text, interval=interval)
        return f"Wrote '{text[:50]}{'...' if len(text) > 50 else ''}' with {interval}s interval"
    except Exception as e:
        logger.error(f"Error writing text with interval: {e}")
        return f"Failed to write text with interval: {str(e)}"

def hold_key_and_action(hold_key: str, action: str) -> str:
    """Hold a key while performing an action."""
    if not PYAUTOGUI_AVAILABLE:
        return "Keyboard control not available - pyautogui not installed"
    
    try:
        # Use pyautogui's hold context manager
        with pyautogui.hold(hold_key):
            if action.startswith("type "):
                text = action[5:]
                pyautogui.write(text)
                return f"Held '{hold_key}' and typed '{text}'"
            elif action.startswith("press "):
                key = action[6:]
                pyautogui.press(key)
                return f"Held '{hold_key}' and pressed '{key}'"
            elif action.startswith("click"):
                pyautogui.click()
                return f"Held '{hold_key}' and clicked"
            else:
                return f"Unknown action '{action}'. Use 'type text', 'press key', or 'click'"
    except Exception as e:
        logger.error(f"Error holding key and action: {e}")
        return f"Failed to hold key and perform action: {str(e)}"

# ---------- Enhanced Message Box Functions ----------
def ask_input(prompt_text: str) -> str:
    """Ask for text input with a prompt dialog."""
    if not PYAUTOGUI_AVAILABLE:
        return "Input dialogs not available - pyautogui not installed"
    
    try:
        response = pyautogui.prompt(prompt_text, title="Ultron Assistant Input")
        if response is None:
            return f"Input canceled"
        return f"Input prompt: {prompt_text} | Response: {response}"
    except Exception as e:
        logger.error(f"Error asking for input: {e}")
        return f"Failed to ask for input: {str(e)}"

def ask_password(prompt_text: str) -> str:
    """Ask for password input with a secure dialog."""
    if not PYAUTOGUI_AVAILABLE:
        return "Password dialogs not available - pyautogui not installed"
    
    try:
        response = pyautogui.password(prompt_text, title="Ultron Assistant Password", mask='*')
        if response is None:
            return "Password input canceled"
        return f"Password entered (length: {len(response)} characters)"
    except Exception as e:
        logger.error(f"Error asking for password: {e}")
        return f"Failed to ask for password: {str(e)}"

# ---------- Enhanced Scroll Function ----------
def scroll(direction: str, clicks: int = 3) -> str:
    """Enhanced scroll function with multiple directions and click count."""
    if not PYAUTOGUI_AVAILABLE:
        return "Mouse control not available - pyautogui not installed"
    
    try:
        if direction.lower() == "up":
            pyautogui.scroll(clicks)
            return f"Scrolled up {clicks} clicks"
        elif direction.lower() == "down":
            pyautogui.scroll(-clicks)
            return f"Scrolled down {clicks} clicks"
        elif direction.lower() == "left":
            pyautogui.hscroll(-clicks)
            return f"Scrolled left {clicks} clicks"
        elif direction.lower() == "right":
            pyautogui.hscroll(clicks)
            return f"Scrolled right {clicks} clicks"
        else:
            return f"Invalid scroll direction: {direction}. Use up, down, left, or right"
    except Exception as e:
        logger.error(f"Error scrolling: {e}")
        return f"Failed to scroll: {str(e)}"

if __name__ == "__main__":
    # Test the automation system
    test_commands = [
        "open notepad",
        "take screenshot",
        "what time",
        "system info"
    ]
    
    print("Testing automation commands:")
    for cmd in test_commands:
        result = run_command(cmd)
        print(f"Command: {cmd}")
        print(f"Result: {result}")
        print("-" * 50)
