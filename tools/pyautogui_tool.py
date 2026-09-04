"""
PyAutoGUI Integration Tool for ULTRON Agent
Provides screen automation and GUI control capabilities
"""

import pyautogui
import time
import os
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
        os.makedirs(self.screenshot_dir, exist_ok=True)
    
    def match(self, command: str) -> bool:
        """Check if command matches PyAutoGUI operations"""
        return any(keyword in command.lower() for keyword in [
            "click", "type", "screenshot", "move mouse", "scroll", 
            "press key", "automation", "gui", "screen", "mouse", "keyboard"
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
            elif "screen size" in cmd:
                return self._get_screen_info()
            elif "mouse position" in cmd:
                return self._get_mouse_position()
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
                
                pyautogui.typewrite(text_part)
                return f"Typed: {text_part}"
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
    
    def _show_help(self) -> str:
        """Show available commands"""
        return """PyAutoGUI Commands:
- screenshot: Take a screenshot
- click at x,y: Click at coordinates
- type "text": Type text
- move mouse to x,y: Move mouse
- scroll up/down: Scroll
- press key enter/space/tab/escape: Press key
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
            }
        }