"""
PyAutoGUI Integration Tool for ULTRON Agent
Provides screen automation and GUI control capabilities
"""

import pyautogui
import time
import os
import re
import logging
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from PIL import Image
from utils.ultron_logger import log_info, log_error
from utils.error_handlers import (
    ValidationError, FileError, ResourceError, ErrorContext
)
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

    def __init__(self, config: Optional[Any] = None) -> None:
        """Initialize PyAutoGUI Tool with proper error handling"""
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.config: Optional[Any] = config or {}
        self.screenshot_dir: str = "screenshots"

        with ErrorContext("pyautogui", logger=self.logger) as ctx:
            try:
                ctx.operation = "screenshot_directory_setup"
                os.makedirs(self.screenshot_dir, exist_ok=True)
                log_info("pyautogui", f"Screenshot directory ready: "
                         f"{self.screenshot_dir}")
            except (IOError, OSError) as e:
                log_error("pyautogui",
                         f"Failed to create screenshot directory: {e}")
                ctx.error = FileError(
                    f"Failed to create screenshot directory: {e}",
                    self.screenshot_dir,
                    "create",
                    reason="directory_creation_failed"
                )
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
        """Take a screenshot with comprehensive error handling

        Returns: str - Success message with filepath or error message
        Raises: FileError on save failures, ResourceError on screenshot failures
        """
        with ErrorContext("pyautogui", logger=self.logger) as ctx:
            try:
                ctx.operation = "take_screenshot"
                timestamp: int = int(time.time())
                filename: str = f"screenshot_{timestamp}.png"
                filepath: str = os.path.join(self.screenshot_dir, filename)

                # Attempt screenshot capture
                try:
                    screenshot: Image.Image = pyautogui.screenshot()
                except Exception as e:
                    log_error("pyautogui",
                             f"Screenshot capture failed: {e}")
                    raise ResourceError(
                        f"Failed to capture screenshot: {e}",
                        "screen",
                        "capture"
                    )

                # Attempt file save
                try:
                    screenshot.save(filepath)
                except (IOError, OSError) as e:
                    log_error("pyautogui",
                             f"Failed to save screenshot: {e}")
                    raise FileError(
                        f"Failed to save screenshot: {e}",
                        filepath,
                        "write",
                        reason="screenshot_save_failed"
                    )

                log_info("pyautogui",
                        f"Screenshot saved: {filepath}")
                return f"Screenshot saved: {filepath}"

            except (FileError, ResourceError) as e:
                log_error("pyautogui",
                         f"Screenshot operation failed: {e}")
                ctx.error = e
                return f"Screenshot error: {str(e)}"
            except Exception as e:
                log_error("pyautogui",
                         f"Unexpected screenshot error: {e}")
                ctx.error = e
                return f"Screenshot error: {str(e)}"

    def _handle_click(self, command: str) -> str:
        """Handle mouse click operations with error handling

        Args: command (str) - Click command (e.g., "click at 100,200")
        Returns: str - Success message or error message
        Raises: ValidationError on invalid coordinates
        """
        with ErrorContext("pyautogui", logger=self.logger) as ctx:
            try:
                # Extract coordinates if provided
                if "at" in command:
                    coords_part: str = command.split("at")[1].strip()
                    if "," in coords_part:
                        try:
                            x, y = map(int, coords_part.split(","))
                        except ValueError as e:
                            log_error("pyautogui",
                                     f"Invalid coordinates: {e}")
                            raise ValidationError(
                                f"Invalid coordinates: {e}",
                                "coordinates",
                                coords_part,
                                "x,y format"
                            )

                        pyautogui.click(x, y)
                        log_info("pyautogui",
                                f"Clicked at ({x}, {y})")
                        return f"Clicked at ({x}, {y})"

                # Default click at current position
                pyautogui.click()
                log_info("pyautogui", "Clicked at current position")
                return "Clicked at current mouse position"

            except ValidationError as e:
                log_error("pyautogui", f"Click validation: {e}")
                ctx.error = e
                return f"Click error: {str(e)}"
            except Exception as e:
                log_error("pyautogui", f"Click failed: {e}")
                ctx.error = e
                return f"Click error: {str(e)}"

    def _handle_type(self, command: str) -> str:
        """Handle typing operations with validation

        Args: command (str) - Type command with text to type
        Returns: str - Success message or error message
        Raises: ValidationError on invalid/missing input
        """
        with ErrorContext("pyautogui", logger=self.logger) as ctx:
            try:
                # Extract text to type
                if "type" not in command:
                    raise ValidationError(
                        "No text specified for typing",
                        "text_input",
                        "",
                        "non-empty string"
                    )

                text_part: str = command.split("type")[1].strip()
                if text_part.startswith('"') and \
                        text_part.endswith('"'):
                    text_part = text_part[1:-1]

                # Validate text input
                if not text_part:
                    raise ValidationError(
                        "Cannot type empty string",
                        "text_input",
                        text_part,
                        "non-empty string"
                    )

                # Sanitize input to prevent injection
                text_part_safe: str = \
                    self._sanitize_input(text_part)
                pyautogui.typewrite(text_part_safe)
                log_info("pyautogui",
                        f"Typed: {text_part_safe[:30]}")
                output_msg: str = \
                    f"Typed: {text_part_safe[:50]}"
                if len(text_part_safe) > 50:
                    output_msg += "..."
                return output_msg

            except ValidationError as e:
                log_error("pyautogui", f"Type validation: {e}")
                ctx.error = e
                return f"Type error: {str(e)}"
            except Exception as e:
                log_error("pyautogui", f"Type failed: {e}")
                ctx.error = e
                return f"Type error: {str(e)}"

    def _handle_mouse_move(self, command: str) -> str:
        """Handle mouse movement with coordinate validation

        Args: command (str) - Move command with target coordinates
        Returns: str - Success message or error message
        Raises: ValidationError on invalid coordinates
        """
        with ErrorContext("pyautogui", logger=self.logger) as ctx:
            try:
                if "to" not in command:
                    raise ValidationError(
                        "No target coordinates specified",
                        "coordinates",
                        "",
                        "x,y format"
                    )

                coords_part: str = command.split("to")[1].strip()
                if "," not in coords_part:
                    raise ValidationError(
                        "Invalid coordinate format",
                        "coordinates",
                        coords_part,
                        "x,y format"
                    )

                try:
                    x, y = map(int, coords_part.split(","))
                except ValueError as e:
                    log_error("pyautogui",
                             f"Coordinate parse error: {e}")
                    raise ValidationError(
                        f"Invalid coordinates: {e}",
                        "coordinates",
                        coords_part,
                        "x,y format"
                    )

                pyautogui.moveTo(x, y)
                log_info("pyautogui",
                        f"Moved mouse to ({x}, {y})")
                return f"Moved mouse to ({x}, {y})"

            except ValidationError as e:
                log_error("pyautogui",
                         f"Mouse move validation: {e}")
                ctx.error = e
                return f"Move error: {str(e)}"
            except Exception as e:
                log_error("pyautogui", f"Mouse move failed: {e}")
                ctx.error = e
                return f"Move error: {str(e)}"

    def _handle_scroll(self, command: str) -> str:
        """Handle scroll operations with error handling

        Args: command (str) - Scroll command (up/down)
        Returns: str - Success message or error message
        """
        with ErrorContext("pyautogui", logger=self.logger) as ctx:
            try:
                if "up" in command.lower():
                    pyautogui.scroll(3)
                    log_info("pyautogui", "Scrolled up")
                    return "Scrolled up"
                elif "down" in command.lower():
                    pyautogui.scroll(-3)
                    log_info("pyautogui", "Scrolled down")
                    return "Scrolled down"
                else:
                    pyautogui.scroll(1)
                    log_info("pyautogui", "Scrolled")
                    return "Scrolled"

            except Exception as e:
                log_error("pyautogui", f"Scroll failed: {e}")
                ctx.error = e
                return f"Scroll error: {str(e)}"

    def _handle_key_press(self, command: str) -> str:
        """Handle key press operations with validation

        Args: command (str) - Key press command
        Returns: str - Success message or error message
        Raises: ValidationError on unsupported keys
        """
        with ErrorContext("pyautogui", logger=self.logger) as ctx:
            try:
                key_part: str = command.lower()
                if "enter" in key_part:
                    pyautogui.press('enter')
                    log_info("pyautogui", "Pressed Enter")
                    return "Pressed Enter"
                elif "space" in key_part:
                    pyautogui.press('space')
                    log_info("pyautogui", "Pressed Space")
                    return "Pressed Space"
                elif "tab" in key_part:
                    pyautogui.press('tab')
                    log_info("pyautogui", "Pressed Tab")
                    return "Pressed Tab"
                elif "escape" in key_part or "esc" in \
                        key_part:
                    pyautogui.press('escape')
                    log_info("pyautogui", "Pressed Escape")
                    return "Pressed Escape"
                else:
                    raise ValidationError(
                        f"Unsupported key: {key_part}",
                        "key_name",
                        key_part,
                        "enter/space/tab/escape"
                    )

            except ValidationError as e:
                log_error("pyautogui",
                         f"Key press validation: {e}")
                ctx.error = e
                return f"Key error: {str(e)}"
            except Exception as e:
                log_error("pyautogui", f"Key press failed: {e}")
                ctx.error = e
                return f"Key error: {str(e)}"

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

    def _handle_drag(self, command: str) -> str:
        """Handle drag operations with coordinate validation

        Args: command (str) - Drag command with coordinates
        Returns: str - Success message or error message
        Raises: ValidationError on invalid format
        """
        with ErrorContext("pyautogui", logger=self.logger) as ctx:
            try:
                if "from" not in command or "to" not in \
                        command:
                    raise ValidationError(
                        "Drag requires 'from' and 'to'",
                        "drag_format",
                        command,
                        "from x1,y1 to x2,y2"
                    )

                parts: list = command.split("from")[1].split(
                    "to")
                start_coords: list = parts[0].strip().split(
                    ",")
                end_coords: list = parts[1].strip().split(",")

                try:
                    x1: int = int(start_coords[0])
                    y1: int = int(start_coords[1])
                    x2: int = int(end_coords[0])
                    y2: int = int(end_coords[1])
                except (ValueError, IndexError) as e:
                    log_error("pyautogui",
                             f"Drag coordinate parse: {e}")
                    raise ValidationError(
                        f"Invalid drag coordinates: {e}",
                        "coordinates",
                        command,
                        "from x1,y1 to x2,y2"
                    )

                pyautogui.drag(x2-x1, y2-y1, duration=1,
                              button='left')
                log_info("pyautogui",
                        f"Dragged ({x1},{y1})->({x2},{y2})")
                return f"Dragged from ({x1},{y1}) to ({x2},{y2})"

            except ValidationError as e:
                log_error("pyautogui", f"Drag validation: {e}")
                ctx.error = e
                return f"Drag error: {str(e)}"
            except Exception as e:
                log_error("pyautogui", f"Drag failed: {e}")
                ctx.error = e
                return f"Drag error: {str(e)}"

    def _handle_locate(self, command: str) -> str:
        """Handle image location with file validation

        Args: command (str) - Locate command with image path
        Returns: str - Location message or error
        Raises: FileError on invalid/missing file,
                ValidationError on bad format
        """
        with ErrorContext("pyautogui", logger=self.logger) as ctx:
            try:
                if "image" not in command:
                    raise ValidationError(
                        "No image path specified",
                        "image_path",
                        "",
                        "locate image 'path'"
                    )

                image_path: str = command.split("image")[1]. \
                    strip().strip('"')
                safe_path: Optional[str] = \
                    self._validate_file_path(image_path)

                if not safe_path:
                    raise FileError(
                        "Invalid or unsafe file path",
                        image_path,
                        "read"
                    )

                if not os.path.exists(safe_path):
                    raise FileError(
                        f"Image file not found: {safe_path}",
                        safe_path,
                        "read",
                        reason="file_not_found"
                    )

                location: Any = \
                    pyautogui.locateOnScreen(safe_path)
                if location:
                    log_info("pyautogui",
                            f"Image found at: {location}")
                    return f"Image found at: {location}"
                else:
                    log_info("pyautogui",
                            "Image not on screen")
                    return "Image not found on screen"

            except (FileError, ValidationError) as e:
                log_error("pyautogui",
                         f"Locate validation: {e}")
                ctx.error = e
                return f"Locate error: {str(e)}"
            except Exception as e:
                log_error("pyautogui", f"Locate failed: {e}")
                ctx.error = e
                return f"Locate error: {str(e)}"

    def _handle_pixel(self, command: str) -> str:
        """Handle pixel color detection with validation

        Args: command (str) - Pixel command with coordinates
        Returns: str - RGB color tuple or error message
        Raises: ValidationError on invalid coordinates
        """
        with ErrorContext("pyautogui", logger=self.logger) as ctx:
            try:
                if "at" not in command:
                    raise ValidationError(
                        "No coordinates specified",
                        "coordinates",
                        "",
                        "pixel at x,y"
                    )

                coords_part: str = command.split("at")[1].strip()
                if "," not in coords_part:
                    raise ValidationError(
                        "Invalid coordinate format",
                        "coordinates",
                        coords_part,
                        "x,y format"
                    )

                try:
                    x, y = map(int, coords_part.split(","))
                except ValueError as e:
                    log_error("pyautogui",
                             f"Pixel coordinate parse: {e}")
                    raise ValidationError(
                        f"Invalid coordinates: {e}",
                        "coordinates",
                        coords_part,
                        "x,y format"
                    )

                pixel: Tuple = pyautogui.pixel(x, y)
                log_info("pyautogui",
                        f"Pixel at ({x},{y}): {pixel}")
                return f"Pixel at ({x},{y}): RGB{pixel}"

            except ValidationError as e:
                log_error("pyautogui",
                         f"Pixel validation: {e}")
                ctx.error = e
                return f"Pixel error: {str(e)}"
            except Exception as e:
                log_error("pyautogui", f"Pixel failed: {e}")
                ctx.error = e
                return f"Pixel error: {str(e)}"

    def _handle_hotkey(self, command: str) -> str:
        """Handle hotkey combinations with validation

        Args: command (str) - Hotkey command
        Returns: str - Success message or error message
        Raises: ValidationError on unsupported hotkey
        """
        with ErrorContext("pyautogui", logger=self.logger) as ctx:
            try:
                cmd_lower: str = command.lower()
                if "ctrl+c" in cmd_lower:
                    pyautogui.hotkey('ctrl', 'c')
                    log_info("pyautogui", "Pressed Ctrl+C")
                    return "Pressed Ctrl+C"
                elif "ctrl+v" in cmd_lower:
                    pyautogui.hotkey('ctrl', 'v')
                    log_info("pyautogui", "Pressed Ctrl+V")
                    return "Pressed Ctrl+V"
                elif "alt+tab" in cmd_lower:
                    pyautogui.hotkey('alt', 'tab')
                    log_info("pyautogui", "Pressed Alt+Tab")
                    return "Pressed Alt+Tab"
                elif "ctrl+z" in cmd_lower:
                    pyautogui.hotkey('ctrl', 'z')
                    log_info("pyautogui", "Pressed Ctrl+Z")
                    return "Pressed Ctrl+Z"
                else:
                    raise ValidationError(
                        f"Unsupported hotkey: {cmd_lower}",
                        "hotkey",
                        cmd_lower,
                        "ctrl+c/ctrl+v/alt+tab/ctrl+z"
                    )

            except ValidationError as e:
                log_error("pyautogui",
                         f"Hotkey validation: {e}")
                ctx.error = e
                return f"Hotkey error: {str(e)}"
            except Exception as e:
                log_error("pyautogui", f"Hotkey failed: {e}")
                ctx.error = e
                return f"Hotkey error: {str(e)}"

    def _handle_failsafe(self, command: str) -> str:
        """Handle failsafe settings with validation

        Args: command (str) - Failsafe control command
        Returns: str - Status message or error
        """
        with ErrorContext("pyautogui", logger=self.logger) as ctx:
            try:
                if "enable" in command.lower():
                    pyautogui.FAILSAFE = True
                    log_info("pyautogui", "Failsafe enabled")
                    return (
                        "Failsafe enabled "
                        "(move mouse to corner to stop)"
                    )
                elif "disable" in command.lower():
                    pyautogui.FAILSAFE = False
                    log_info("pyautogui", "Failsafe disabled")
                    return "Failsafe disabled"
                else:
                    status: str = (
                        "enabled" if pyautogui.FAILSAFE
                        else "disabled"
                    )
                    return f"Failsafe is currently {status}"

            except Exception as e:
                log_error("pyautogui", f"Failsafe failed: {e}")
                ctx.error = e
                return f"Failsafe error: {str(e)}"

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
