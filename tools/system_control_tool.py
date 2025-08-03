import logging
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController
from .base import Tool
from typing import Optional

logger = logging.getLogger(__name__)

class SystemControlTool(Tool):
    """A tool for controlling the user's mouse and keyboard."""

    def __init__(self, agent):
        self.name = "system_control"
        self.description = "Perform system-level actions like moving the mouse, clicking, and typing."
        self.parameters = {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "The action to perform: 'move_mouse', 'click', 'type', 'press_key'.",
                    "enum": ["move_mouse", "click", "type", "press_key"]
                },
                "x": {"type": "integer", "description": "The x-coordinate for mouse movement."},
                "y": {"type": "integer", "description": "The y-coordinate for mouse movement."},
                "button": {"type": "string", "description": "The mouse button to click ('left', 'right', 'middle')."},
                "text": {"type": "string", "description": "The text to type."},
                "key": {"type": "string", "description": "The special key to press (e.g., 'enter', 'ctrl', 'shift')."}
            },
            "required": ["action"]
        }
        self.agent = agent
        self.mouse = MouseController()
        self.keyboard = KeyboardController()

    def match(self, user_input: str) -> bool:
        return any(keyword in user_input.lower() for keyword in ["mouse", "click", "type", "press key"])

    def execute(self, action: str, **kwargs) -> str:
        logger.info(f"Executing system control action: {action} with args {kwargs}")
        try:
            if action == "move_mouse":
                x = kwargs.get("x")
                y = kwargs.get("y")
                if x is None or y is None:
                    return "Error: x and y coordinates are required for move_mouse."
                self._move_mouse(x, y)
                return f"Mouse moved to ({x}, {y})."

            elif action == "click":
                button_str = kwargs.get("button", "left")
                self._click(button_str)
                return f"{button_str.capitalize()} mouse button clicked."

            elif action == "type":
                text = kwargs.get("text")
                if text is None:
                    return "Error: text is required for type action."
                self._type(text)
                return f"Typed text: '{text}'"

            elif action == "press_key":
                key_str = kwargs.get("key")
                if key_str is None:
                    return "Error: key is required for press_key action."
                self._press_key(key_str)
                return f"Pressed key: '{key_str}'"

            else:
                return f"Error: Unknown system control action '{action}'."

        except Exception as e:
            logger.error(f"Error executing system control action '{action}': {e}", exc_info=True)
            return f"Error performing system control action: {e}"

    def _move_mouse(self, x: int, y: int):
        self.mouse.position = (x, y)

    def _click(self, button_str: str):
        button = getattr(Button, button_str.lower(), Button.left)
        self.mouse.click(button, 1)

    def _type(self, text: str):
        self.keyboard.type(text)

    def _press_key(self, key_str: str):
        # Map string to pynput Key object
        key = getattr(Key, key_str.lower(), None)
        if key:
            self.keyboard.press(key)
            self.keyboard.release(key)
        else:
            # Handle single characters like 'a', 'b', etc.
            self.keyboard.press(key_str)
            self.keyboard.release(key_str)
