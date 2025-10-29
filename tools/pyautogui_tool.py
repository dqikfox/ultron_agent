"""
PyAutoGUI Integration Tool for ULTRON Agent
Provides screen automation and GUI control capabilities
"""

import pyautogui
import time
import os
import re
from pathlib import Path
from PIL import Image
from utils.ultron_logger import log_info, log_error
from .tool_interface import ToolInterface

# Configure PyAutoGUI safety
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

class PyAutoGUITool(ToolInterface):
    """Tool for screen automation and GUI control"""
    
    @property
    def name(self) -> str:
        return "PyAutoGUI Tool"
    @property
    def description(self) -> str:
        return "Screen automation, mouse/keyboard control, and GUI interaction"
    
    def __init__(self, config=None):
        self.config = config or {}
        self.screenshot_dir = "screenshots"
        try:
            os.makedirs(self.screenshot_dir, exist_ok=True)
        except OSError as e:
            log_error("pyautogui", f"Failed to create screenshot directory: {e}")
            self.screenshot_dir = "."
    
    def match(self, command: str) -> bool:
        """Check if command matches PyAutoGUI operations"""
        return any(keyword in command.lower() for keyword in [
            "click", "type", "screenshot", "move mouse", "scroll", 
            "press key", "automation", "gui", "screen", "mouse", "keyboard",
            "drag", "hotkey", "alert", "locate", "pixel", "window", "failsafe"
        ])
    
    def execute(self, command: str) -> str:
        """Execute PyAutoGUI operations"""
        try:
            cmd = command.lower().strip()
            
            if "screenshot" in cmd:
                return self._take_screenshot()
            elif "click" in cmd:
                return self._handle_click(command)
            elif "type" in cmd:
                return self._handle_type(command)
            elif "move mouse" in cmd:
                return self._handle_mouse_move(command)
            elif "scroll" in cmd:
                return self._handle_scroll(command)
            elif "press key" in cmd or "key press" in cmd:
                return self._handle_key_press(command)
            elif "hotkey" in cmd:
                return self._handle_hotkey(command)
            elif "drag" in cmd:
                return self._handle_drag(command)
            elif "alert" in cmd:
                return self._handle_alert(command)
            elif "locate" in cmd:
                return self._handle_locate(command)
            elif "pixel" in cmd:
                return self._handle_pixel(command)
            elif "screen size" in cmd:
                return self._get_screen_info()
            elif "mouse position" in cmd:
                return self._get_mouse_position()
            elif "failsafe" in cmd:
                return self._handle_failsafe(command)
            else:
                return self._show_help()
                
        except Exception as e:
            log_error("pyautogui", f"Operation failed: {e}")
            return f"PyAutoGUI error: {str(e)}"
    
    def _take_screenshot(self) -> str:
        """Take a screenshot"""
        try:
            timestamp = int(time.time())
            filename = f"screenshot_{timestamp}.png"
            filepath = os.path.join(self.screenshot_dir, filename)
            
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            
            log_info("pyautogui", f"Screenshot saved: {filepath}")
            return f"Screenshot saved: {filepath}"
        except Exception as e:
            return f"Screenshot failed: {e}"
    
    def _handle_click(self, command: str) -> str:
        """Handle mouse click operations"""
        try:
            # Extract coordinates if provided
            if "at" in command:
                coords_part = command.split("at")[1].strip()
                if "," in coords_part:
                    x, y = map(int, coords_part.split(","))
                    pyautogui.click(x, y)
                    return f"Clicked at ({x}, {y})"
            
            # Default click at current position
            pyautogui.click()
            return "Clicked at current mouse position"
        except Exception as e:
            return f"Click failed: {e}"
    
    def _handle_type(self, command: str) -> str:
        """Handle typing operations"""
        try:
            # Extract text to type
            if "type" in command:
                text_part = command.split("type")[1].strip()
                if text_part.startswith('"') and text_part.endswith('"'):
                    text_part = text_part[1:-1]
                
                # Sanitize input to prevent injection
                text_part = self._sanitize_input(text_part)
                pyautogui.typewrite(text_part)
                return f"Typed: {text_part[:50]}{'...' if len(text_part) > 50 else ''}"
            return "No text specified to type"
        except Exception as e:
            return f"Type failed: {e}"
    
    def _handle_mouse_move(self, command: str) -> str:
        """Handle mouse movement"""
        try:
            if "to" in command:
                coords_part = command.split("to")[1].strip()
                if "," in coords_part:
                    x, y = map(int, coords_part.split(","))
                    pyautogui.moveTo(x, y)
                    return f"Moved mouse to ({x}, {y})"
            return "No coordinates specified"
        except Exception as e:
            return f"Mouse move failed: {e}"
    
    def _handle_scroll(self, command: str) -> str:
        """Handle scroll operations"""
        try:
            if "up" in command:
                pyautogui.scroll(3)
                return "Scrolled up"
            elif "down" in command:
                pyautogui.scroll(-3)
                return "Scrolled down"
            else:
                pyautogui.scroll(1)
                return "Scrolled"
        except Exception as e:
            return f"Scroll failed: {e}"
    
    def _handle_key_press(self, command: str) -> str:
        """Handle key press operations"""
        try:
            # Extract key name
            key_part = command.lower()
            if "enter" in key_part:
                pyautogui.press('enter')
                return "Pressed Enter"
            elif "space" in key_part:
                pyautogui.press('space')
                return "Pressed Space"
            elif "tab" in key_part:
                pyautogui.press('tab')
                return "Pressed Tab"
            elif "escape" in key_part or "esc" in key_part:
                pyautogui.press('escape')
                return "Pressed Escape"
            else:
                return "Key not recognized. Supported: enter, space, tab, escape"
        except Exception as e:
            return f"Key press failed: {e}"
    
    def _get_screen_info(self) -> str:
        """Get screen information"""
        try:
            size = pyautogui.size()
            return f"Screen size: {size.width}x{size.height}"
        except Exception as e:
            return f"Screen info failed: {e}"
    
    def _get_mouse_position(self) -> str:
        """Get current mouse position"""
        try:
            pos = pyautogui.position()
            return f"Mouse position: ({pos.x}, {pos.y})"
        except Exception as e:
            return f"Mouse position failed: {e}"
    
    def _handle_hotkey(self, command: str) -> str:
        """Handle hotkey combinations"""
        try:
            if "ctrl+c" in command.lower():
                pyautogui.hotkey('ctrl', 'c')
                return "Pressed Ctrl+C"
            elif "ctrl+v" in command.lower():
                pyautogui.hotkey('ctrl', 'v')
                return "Pressed Ctrl+V"
            elif "alt+tab" in command.lower():
                pyautogui.hotkey('alt', 'tab')
                return "Pressed Alt+Tab"
            elif "ctrl+z" in command.lower():
                pyautogui.hotkey('ctrl', 'z')
                return "Pressed Ctrl+Z"
            else:
                return "Hotkey not recognized. Supported: ctrl+c, ctrl+v, alt+tab, ctrl+z"
        except Exception as e:
            return f"Hotkey failed: {e}"
    
    def _handle_drag(self, command: str) -> str:
        """Handle drag operations"""
        try:
            if "from" in command and "to" in command:
                parts = command.split("from")[1].split("to")
                start_coords = parts[0].strip().split(",")
                end_coords = parts[1].strip().split(",")
                
                x1, y1 = int(start_coords[0]), int(start_coords[1])
                x2, y2 = int(end_coords[0]), int(end_coords[1])
                
                pyautogui.drag(x2-x1, y2-y1, duration=1, button='left')
                return f"Dragged from ({x1},{y1}) to ({x2},{y2})"
            return "Drag format: drag from x1,y1 to x2,y2"
        except Exception as e:
            return f"Drag failed: {e}"
    
    def _handle_alert(self, command: str) -> str:
        """Handle alert dialogs"""
        try:
            if "show" in command:
                text = command.split("show")[1].strip().strip('"')
                text = self._sanitize_input(text)
                pyautogui.alert(text, "ULTRON Alert")
                return f"Showed alert: {text[:50]}{'...' if len(text) > 50 else ''}"
            elif "confirm" in command:
                text = command.split("confirm")[1].strip().strip('"')
                text = self._sanitize_input(text)
                result = pyautogui.confirm(text, "ULTRON Confirm")
                return f"Confirm result: {result}"
            return "Alert format: alert show 'message' or alert confirm 'question'"
        except Exception as e:
            return f"Alert failed: {e}"
    
    def _handle_locate(self, command: str) -> str:
        """Handle image location on screen"""
        try:
            if "image" in command:
                image_path = command.split("image")[1].strip().strip('"')
                # Validate and sanitize file path
                safe_path = self._validate_file_path(image_path)
                if safe_path and os.path.exists(safe_path):
                    location = pyautogui.locateOnScreen(safe_path)
                    if location:
                        return f"Image found at: {location}"
                    else:
                        return "Image not found on screen"
                return "Invalid or non-existent image file"
            return "Locate format: locate image 'path/to/image.png'"
        except Exception as e:
            return f"Locate failed: {e}"
    
    def _handle_pixel(self, command: str) -> str:
        """Handle pixel color detection"""
        try:
            if "at" in command:
                coords_part = command.split("at")[1].strip()
                if "," in coords_part:
                    x, y = map(int, coords_part.split(","))
                    pixel = pyautogui.pixel(x, y)
                    return f"Pixel at ({x},{y}): RGB{pixel}"
            return "Pixel format: pixel at x,y"
        except Exception as e:
            return f"Pixel failed: {e}"
    
    def _handle_failsafe(self, command: str) -> str:
        """Handle failsafe settings"""
        try:
            if "enable" in command:
                pyautogui.FAILSAFE = True
                return "Failsafe enabled (move mouse to corner to stop)"
            elif "disable" in command:
                pyautogui.FAILSAFE = False
                return "Failsafe disabled"
            else:
                status = "enabled" if pyautogui.FAILSAFE else "disabled"
                return f"Failsafe is currently {status}"
        except Exception as e:
            return f"Failsafe failed: {e}"
    
    def _sanitize_input(self, text: str) -> str:
        """Sanitize input to prevent injection attacks"""
        # Remove potentially dangerous characters
        text = re.sub(r'[<>"\'\\\/]', '', text)
        # Limit length
        return text[:1000]
    
    def _validate_file_path(self, path: str) -> str:
        """Validate file path to prevent path traversal"""
        try:
            # Resolve path and check if it's within allowed directories
            resolved_path = Path(path).resolve()
            current_dir = Path.cwd()
            
            # Only allow files in current directory or subdirectories
            if current_dir in resolved_path.parents or resolved_path == current_dir:
                return str(resolved_path)
            return None
        except Exception:
            return None
    
    def _show_help(self) -> str:
        """Show available commands"""
        return """PyAutoGUI Commands:
- screenshot: Take a screenshot
- click at x,y: Click at coordinates
- type "text": Type text
- move mouse to x,y: Move mouse
- scroll up/down: Scroll
- press key enter/space/tab/escape: Press key
- hotkey ctrl+c/ctrl+v/alt+tab/ctrl+z: Key combinations
- drag from x1,y1 to x2,y2: Drag operation
- alert show "message": Show alert dialog
- alert confirm "question": Show confirm dialog
- locate image "path": Find image on screen
- pixel at x,y: Get pixel color
- failsafe enable/disable: Control failsafe
- screen size: Get screen dimensions
- mouse position: Get mouse coordinates"""
    
    @classmethod
    def schema(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "PyAutoGUI command (click, type, screenshot, etc.)"
                    }
                },
                "required": ["command"]
            },
            "examples": [
                "screenshot",
                "click at 100,200",
                "type 'Hello World'",
                "hotkey ctrl+c",
                "drag from 50,50 to 150,150",
                "locate image 'button.png'",
                "pixel at 300,400"
            ]
        }