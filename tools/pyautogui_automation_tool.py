"""
Enhanced PyAutoGUI Automation Tool for ULTRON Agent 3.0
Comprehensive desktop automation with image recognition, screen capture, and advanced control
"""

import logging
import os
import time
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import base64
from io import BytesIO

try:
    # Set display environment for headless systems
    if 'DISPLAY' not in os.environ:
        os.environ['DISPLAY'] = ':99'
    
    import pyautogui
    # Disable failsafe for automation (can be re-enabled if needed)
    pyautogui.FAILSAFE = False
    PYAUTOGUI_AVAILABLE = True
except (ImportError, Exception) as e:
    PYAUTOGUI_AVAILABLE = False
    _pyautogui_error = str(e)

from .base import Tool

logger = logging.getLogger(__name__)

class PyAutoGUIAutomationTool(Tool):
    """
    Comprehensive PyAutoGUI automation tool providing complete desktop control capabilities.
    Supports all PyAutoGUI functions for mouse, keyboard, screen capture, and image recognition.
    """

    def __init__(self, agent=None):
        self.name = "pyautogui_automation" 
        self.description = "Advanced desktop automation tool with screen capture, image recognition, mouse/keyboard control, and window management"
        self.parameters = {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "The automation action to perform",
                    "enum": [
                        # Mouse actions
                        "click", "double_click", "right_click", "middle_click",
                        "move_to", "move_rel", "drag", "scroll",
                        "get_mouse_position", 
                        
                        # Keyboard actions  
                        "type_text", "press_key", "hotkey", "key_down", "key_up",
                        
                        # Screen capture
                        "screenshot", "screenshot_region",
                        
                        # Image recognition
                        "locate_image", "locate_center", "locate_all",
                        "pixel_match_color", "get_pixel_color",
                        
                        # Window management
                        "get_active_window", "get_window_list", "get_screen_size",
                        
                        # Dialog automation
                        "alert", "confirm", "prompt", "password",
                        
                        # Advanced automation
                        "wait_for_image", "click_image", "type_in_field"
                    ]
                },
                "x": {"type": "integer", "description": "X coordinate for mouse actions"},
                "y": {"type": "integer", "description": "Y coordinate for mouse actions"},
                "button": {"type": "string", "description": "Mouse button: left, right, middle", "default": "left"},
                "clicks": {"type": "integer", "description": "Number of clicks", "default": 1},
                "interval": {"type": "number", "description": "Interval between clicks", "default": 0.0},
                "text": {"type": "string", "description": "Text to type or search for"},
                "key": {"type": "string", "description": "Key to press (e.g., 'enter', 'ctrl', 'alt')"},
                "keys": {"type": "array", "items": {"type": "string"}, "description": "Keys for hotkey combination"},
                "filename": {"type": "string", "description": "Filename for screenshot or image"},
                "region": {"type": "array", "items": {"type": "integer"}, "description": "Region as [left, top, width, height]"},
                "confidence": {"type": "number", "description": "Image recognition confidence (0.0-1.0)", "default": 0.8},
                "timeout": {"type": "number", "description": "Timeout in seconds", "default": 10.0},
                "duration": {"type": "number", "description": "Duration for drag operations", "default": 1.0},
                "dx": {"type": "integer", "description": "Relative X movement"},
                "dy": {"type": "integer", "description": "Relative Y movement"},
                "color": {"type": "array", "items": {"type": "integer"}, "description": "RGB color values [r, g, b]"},
                "title": {"type": "string", "description": "Dialog title"},
                "message": {"type": "string", "description": "Dialog message"},
                "default": {"type": "string", "description": "Default dialog response"}
            },
            "required": ["action"]
        }
        self.agent = agent
        self.screenshots_dir = Path("screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)

    def match(self, user_input: str) -> bool:
        """Check if user input matches automation commands"""
        keywords = [
            "automate", "click", "type", "screenshot", "mouse", "keyboard", 
            "capture", "find image", "press key", "drag", "scroll",
            "window", "desktop", "automation", "pyautogui"
        ]
        return any(keyword in user_input.lower() for keyword in keywords)

    @staticmethod
    def schema() -> Dict[str, Any]:
        """Return the tool schema for agent discovery"""
        return {
            "type": "function",
            "function": {
                "name": "pyautogui_automation",
                "description": "Advanced desktop automation with PyAutoGUI - screen capture, image recognition, mouse/keyboard control",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "Automation action to perform",
                            "enum": ["click", "type_text", "screenshot", "locate_image", "press_key", "hotkey", "drag", "scroll"]
                        },
                        "x": {"type": "integer", "description": "X coordinate"},
                        "y": {"type": "integer", "description": "Y coordinate"},
                        "text": {"type": "string", "description": "Text to type"},
                        "filename": {"type": "string", "description": "Screenshot filename"}
                    },
                    "required": ["action"]
                }
            }
        }

    def execute(self, action: str, **kwargs) -> str:
        """Execute PyAutoGUI automation action"""
        if not PYAUTOGUI_AVAILABLE:
            error_msg = getattr(self, '_pyautogui_error', 'PyAutoGUI is not available')
            return f"Error: PyAutoGUI is not available. {error_msg}. Note: PyAutoGUI requires a display environment."
        
        # Handle headless environment gracefully
        try:
            screen_size = pyautogui.size()
        except Exception as e:
            logger.warning(f"PyAutoGUI may not work in headless environment: {e}")
            if "display" in str(e).lower() or "x11" in str(e).lower():
                return f"PyAutoGUI requires a display environment. Tool configured but not functional in headless mode: {e}"
            return f"Warning: PyAutoGUI functionality limited in current environment: {e}"

        logger.info(f"Executing PyAutoGUI action: {action} with args: {kwargs}")
        
        try:
            if action == "click":
                return self._handle_click(**kwargs)
            elif action == "double_click":
                return self._handle_double_click(**kwargs)
            elif action == "right_click":
                return self._handle_right_click(**kwargs)
            elif action == "middle_click":
                return self._handle_middle_click(**kwargs)
            elif action == "move_to":
                return self._handle_move_to(**kwargs)
            elif action == "move_rel":
                return self._handle_move_rel(**kwargs)
            elif action == "drag":
                return self._handle_drag(**kwargs)
            elif action == "scroll":
                return self._handle_scroll(**kwargs)
            elif action == "get_mouse_position":
                return self._handle_get_mouse_position()
            elif action == "type_text":
                return self._handle_type_text(**kwargs)
            elif action == "press_key":
                return self._handle_press_key(**kwargs)
            elif action == "hotkey":
                return self._handle_hotkey(**kwargs)
            elif action == "key_down":
                return self._handle_key_down(**kwargs)
            elif action == "key_up":
                return self._handle_key_up(**kwargs)
            elif action == "screenshot":
                return self._handle_screenshot(**kwargs)
            elif action == "screenshot_region":
                return self._handle_screenshot_region(**kwargs)
            elif action == "locate_image":
                return self._handle_locate_image(**kwargs)
            elif action == "locate_center":
                return self._handle_locate_center(**kwargs)
            elif action == "locate_all":
                return self._handle_locate_all(**kwargs)
            elif action == "pixel_match_color":
                return self._handle_pixel_match_color(**kwargs)
            elif action == "get_pixel_color":
                return self._handle_get_pixel_color(**kwargs)
            elif action == "get_active_window":
                return self._handle_get_active_window()
            elif action == "get_screen_size":
                return self._handle_get_screen_size()
            elif action == "alert":
                return self._handle_alert(**kwargs)
            elif action == "confirm":
                return self._handle_confirm(**kwargs)
            elif action == "prompt":
                return self._handle_prompt(**kwargs)
            elif action == "password":
                return self._handle_password(**kwargs)
            elif action == "wait_for_image":
                return self._handle_wait_for_image(**kwargs)
            elif action == "click_image":
                return self._handle_click_image(**kwargs)
            else:
                return f"Error: Unknown PyAutoGUI action '{action}'"
                
        except Exception as e:
            error_msg = f"Error executing PyAutoGUI action '{action}': {str(e)}"
            logger.error(error_msg, exc_info=True)
            return error_msg

    # Mouse action handlers
    def _handle_click(self, x: Optional[int] = None, y: Optional[int] = None, 
                     button: str = "left", clicks: int = 1, interval: float = 0.0, **kwargs) -> str:
        if x is not None and y is not None:
            pyautogui.click(x, y, clicks=clicks, interval=interval, button=button)
            return f"Clicked {button} button {clicks} time(s) at ({x}, {y})"
        else:
            pyautogui.click(clicks=clicks, interval=interval, button=button)
            return f"Clicked {button} button {clicks} time(s) at current position"

    def _handle_double_click(self, x: Optional[int] = None, y: Optional[int] = None, **kwargs) -> str:
        if x is not None and y is not None:
            pyautogui.doubleClick(x, y)
            return f"Double-clicked at ({x}, {y})"
        else:
            pyautogui.doubleClick()
            return "Double-clicked at current position"

    def _handle_right_click(self, x: Optional[int] = None, y: Optional[int] = None, **kwargs) -> str:
        if x is not None and y is not None:
            pyautogui.rightClick(x, y)
            return f"Right-clicked at ({x}, {y})"
        else:
            pyautogui.rightClick()
            return "Right-clicked at current position"

    def _handle_middle_click(self, x: Optional[int] = None, y: Optional[int] = None, **kwargs) -> str:
        if x is not None and y is not None:
            pyautogui.middleClick(x, y)
            return f"Middle-clicked at ({x}, {y})"
        else:
            pyautogui.middleClick()
            return "Middle-clicked at current position"

    def _handle_move_to(self, x: int, y: int, duration: float = 1.0, **kwargs) -> str:
        pyautogui.moveTo(x, y, duration=duration)
        return f"Moved mouse to ({x}, {y}) in {duration}s"

    def _handle_move_rel(self, dx: int, dy: int, duration: float = 1.0, **kwargs) -> str:
        pyautogui.moveRel(dx, dy, duration=duration)
        return f"Moved mouse by ({dx}, {dy}) in {duration}s"

    def _handle_drag(self, x: int, y: int, duration: float = 1.0, button: str = "left", **kwargs) -> str:
        pyautogui.drag(x, y, duration=duration, button=button)
        return f"Dragged to ({x}, {y}) with {button} button in {duration}s"

    def _handle_scroll(self, clicks: int = 1, x: Optional[int] = None, y: Optional[int] = None, **kwargs) -> str:
        if x is not None and y is not None:
            pyautogui.scroll(clicks, x=x, y=y)
            return f"Scrolled {clicks} clicks at ({x}, {y})"
        else:
            pyautogui.scroll(clicks)
            return f"Scrolled {clicks} clicks"

    def _handle_get_mouse_position(self, **kwargs) -> str:
        pos = pyautogui.position()
        return f"Mouse position: ({pos.x}, {pos.y})"

    # Keyboard action handlers
    def _handle_type_text(self, text: str, interval: float = 0.0, **kwargs) -> str:
        pyautogui.typewrite(text, interval=interval)
        return f"Typed text: '{text}'"

    def _handle_press_key(self, key: str, **kwargs) -> str:
        pyautogui.press(key)
        return f"Pressed key: '{key}'"

    def _handle_hotkey(self, keys: List[str], **kwargs) -> str:
        pyautogui.hotkey(*keys)
        return f"Pressed hotkey combination: {'+'.join(keys)}"

    def _handle_key_down(self, key: str, **kwargs) -> str:
        pyautogui.keyDown(key)
        return f"Key down: '{key}'"

    def _handle_key_up(self, key: str, **kwargs) -> str:
        pyautogui.keyUp(key)
        return f"Key up: '{key}'"

    # Screen capture handlers
    def _handle_screenshot(self, filename: Optional[str] = None, **kwargs) -> str:
        if filename is None:
            timestamp = int(time.time())
            filename = f"screenshot_{timestamp}.png"
        
        filepath = self.screenshots_dir / filename
        screenshot = pyautogui.screenshot()
        screenshot.save(str(filepath))
        return f"Screenshot saved to: {filepath}"

    def _handle_screenshot_region(self, region: List[int], filename: Optional[str] = None, **kwargs) -> str:
        if len(region) != 4:
            return "Error: Region must be [left, top, width, height]"
        
        if filename is None:
            timestamp = int(time.time())
            filename = f"screenshot_region_{timestamp}.png"
            
        filepath = self.screenshots_dir / filename
        left, top, width, height = region
        screenshot = pyautogui.screenshot(region=(left, top, width, height))
        screenshot.save(str(filepath))
        return f"Region screenshot saved to: {filepath}"

    # Image recognition handlers
    def _handle_locate_image(self, filename: str, confidence: float = 0.8, **kwargs) -> str:
        try:
            location = pyautogui.locateOnScreen(filename, confidence=confidence)
            if location:
                return f"Image found at: {location}"
            else:
                return f"Image '{filename}' not found on screen"
        except pyautogui.ImageNotFoundException:
            return f"Image '{filename}' not found on screen"

    def _handle_locate_center(self, filename: str, confidence: float = 0.8, **kwargs) -> str:
        try:
            center = pyautogui.locateCenterOnScreen(filename, confidence=confidence)
            if center:
                return f"Image center found at: {center}"
            else:
                return f"Image '{filename}' not found on screen"
        except pyautogui.ImageNotFoundException:
            return f"Image '{filename}' not found on screen"

    def _handle_locate_all(self, filename: str, confidence: float = 0.8, **kwargs) -> str:
        try:
            locations = list(pyautogui.locateAllOnScreen(filename, confidence=confidence))
            if locations:
                return f"Image found {len(locations)} times at: {locations}"
            else:
                return f"Image '{filename}' not found on screen"
        except pyautogui.ImageNotFoundException:
            return f"Image '{filename}' not found on screen"

    def _handle_pixel_match_color(self, x: int, y: int, color: List[int], **kwargs) -> str:
        if len(color) != 3:
            return "Error: Color must be [r, g, b]"
        
        matches = pyautogui.pixelMatchesColor(x, y, tuple(color))
        return f"Pixel at ({x}, {y}) {'matches' if matches else 'does not match'} color {color}"

    def _handle_get_pixel_color(self, x: int, y: int, **kwargs) -> str:
        color = pyautogui.pixel(x, y)
        return f"Pixel color at ({x}, {y}): {color}"

    # Window management handlers
    def _handle_get_active_window(self, **kwargs) -> str:
        try:
            window = pyautogui.getActiveWindow()
            return f"Active window: {window.title} at {window.topleft} size {window.size}"
        except:
            return "Unable to get active window information"

    def _handle_get_screen_size(self, **kwargs) -> str:
        size = pyautogui.size()
        return f"Screen size: {size.width} x {size.height}"

    # Dialog automation handlers
    def _handle_alert(self, text: str = "Alert", title: str = "Alert", **kwargs) -> str:
        pyautogui.alert(text=text, title=title)
        return f"Showed alert: '{title}' - '{text}'"

    def _handle_confirm(self, text: str = "Confirm?", title: str = "Confirm", **kwargs) -> str:
        result = pyautogui.confirm(text=text, title=title)
        return f"Confirmation result: {result}"

    def _handle_prompt(self, text: str = "Please enter:", title: str = "Input", default: str = "", **kwargs) -> str:
        result = pyautogui.prompt(text=text, title=title, default=default)
        return f"User input: '{result}'"

    def _handle_password(self, text: str = "Enter password:", title: str = "Password", **kwargs) -> str:
        result = pyautogui.password(text=text, title=title)
        return "Password entered successfully" if result else "Password entry cancelled"

    # Advanced automation handlers
    def _handle_wait_for_image(self, filename: str, timeout: float = 10.0, confidence: float = 0.8, **kwargs) -> str:
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                location = pyautogui.locateOnScreen(filename, confidence=confidence)
                if location:
                    return f"Image '{filename}' found at {location} after {time.time() - start_time:.2f}s"
            except pyautogui.ImageNotFoundException:
                pass
            time.sleep(0.5)
        return f"Image '{filename}' not found within {timeout}s timeout"

    def _handle_click_image(self, filename: str, confidence: float = 0.8, **kwargs) -> str:
        try:
            center = pyautogui.locateCenterOnScreen(filename, confidence=confidence)
            if center:
                pyautogui.click(center)
                return f"Clicked on image '{filename}' at {center}"
            else:
                return f"Image '{filename}' not found on screen"
        except pyautogui.ImageNotFoundException:
            return f"Image '{filename}' not found on screen"