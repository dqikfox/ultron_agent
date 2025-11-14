"""
Ollama PyAutoGUI Bridge Tool
Enables local Ollama model to use PyAutoGUI functions
"""

import json
from tools.pyautogui_tool import PyAutoGUITool
from utils.ultron_logger import log_info, log_error

class OllamaPyAutoGUIBridge:
    """Bridge between Ollama and PyAutoGUI for automation"""
    
    name = "Ollama PyAutoGUI Bridge"
    description = "Enables Ollama model to control screen and GUI via PyAutoGUI"
    
    def __init__(self, config=None):
        self.config = config or {}
        self.pyautogui_tool = PyAutoGUITool()
        self.function_registry = self._build_function_registry()
    
    def _build_function_registry(self):
        """Build function registry for Ollama"""
        return {
            "take_screenshot": {
                "description": "Take a screenshot of the current screen",
                "parameters": {"type": "object", "properties": {}},
                "function": lambda: self.pyautogui_tool.execute("screenshot")
            },
            "click_at": {
                "description": "Click at specific coordinates",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "x": {"type": "integer", "description": "X coordinate"},
                        "y": {"type": "integer", "description": "Y coordinate"}
                    },
                    "required": ["x", "y"]
                },
                "function": lambda x, y: self.pyautogui_tool.execute(f"click at {x},{y}")
            },
            "type_text": {
                "description": "Type text on the screen",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Text to type"}
                    },
                    "required": ["text"]
                },
                "function": lambda text: self.pyautogui_tool.execute(f'type "{text}"')
            },
            "move_mouse": {
                "description": "Move mouse to coordinates",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "x": {"type": "integer", "description": "X coordinate"},
                        "y": {"type": "integer", "description": "Y coordinate"}
                    },
                    "required": ["x", "y"]
                },
                "function": lambda x, y: self.pyautogui_tool.execute(f"move mouse to {x},{y}")
            },
            "scroll": {
                "description": "Scroll up or down",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "direction": {"type": "string", "enum": ["up", "down"], "description": "Scroll direction"}
                    },
                    "required": ["direction"]
                },
                "function": lambda direction: self.pyautogui_tool.execute(f"scroll {direction}")
            },
            "press_key": {
                "description": "Press a key",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "key": {"type": "string", "enum": ["enter", "space", "tab", "escape"], "description": "Key to press"}
                    },
                    "required": ["key"]
                },
                "function": lambda key: self.pyautogui_tool.execute(f"press key {key}")
            },
            "get_screen_info": {
                "description": "Get screen size and mouse position",
                "parameters": {"type": "object", "properties": {}},
                "function": lambda: f"{self.pyautogui_tool.execute('screen size')} | {self.pyautogui_tool.execute('mouse position')}"
            }
        }
    
    def match(self, command: str) -> bool:
        """Check if command is for Ollama automation"""
        return any(keyword in command.lower() for keyword in [
            "ollama automation", "ai control", "model control", "automation bridge"
        ])
    
    def execute(self, command: str) -> str:
        """Execute Ollama automation commands"""
        try:
            if "functions" in command.lower():
                return self._list_functions()
            elif "schema" in command.lower():
                return self._get_function_schema()
            else:
                return "Use 'functions' to list available automation functions or 'schema' for function definitions"
        except Exception as e:
            log_error("ollama_bridge", f"Bridge execution failed: {e}")
            return f"Bridge error: {str(e)}"
    
    def _list_functions(self) -> str:
        """List available functions for Ollama"""
        functions = list(self.function_registry.keys())
        return f"Available PyAutoGUI functions for Ollama: {', '.join(functions)}"
    
    def _get_function_schema(self) -> str:
        """Get function schema for Ollama integration"""
        schema = {}
        for name, func_info in self.function_registry.items():
            schema[name] = {
                "description": func_info["description"],
                "parameters": func_info["parameters"]
            }
        return json.dumps(schema, indent=2)
    
    def call_function(self, function_name: str, **kwargs) -> str:
        """Call a PyAutoGUI function from Ollama"""
        try:
            if function_name not in self.function_registry:
                return f"Function '{function_name}' not found"
            
            func_info = self.function_registry[function_name]
            result = func_info["function"](**kwargs)
            
            log_info("ollama_bridge", f"Executed {function_name} with args {kwargs}")
            return result
        except Exception as e:
            log_error("ollama_bridge", f"Function call failed: {e}")
            return f"Function error: {str(e)}"
    
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
                        "description": "Bridge command (functions, schema, etc.)"
                    }
                },
                "required": ["command"]
            }
        }