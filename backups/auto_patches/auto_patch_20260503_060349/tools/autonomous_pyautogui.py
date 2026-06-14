"""
Autonomous PyAutoGUI Tool - Lets AI models control desktop directly
"""
import re
from typing import Optional
from utils.ultron_logger import log_info, log_error

try:
    import pyautogui
    AVAILABLE = True
except ImportError:
    AVAILABLE = False

class AutonomousPyAutoGUI:
    """Tool that executes PyAutoGUI commands from AI-generated code"""
    
    name = "Autonomous PyAutoGUI"
    description = "Execute PyAutoGUI commands for desktop automation"
    
    def __init__(self, config=None, memory=None):
        self.config = config
        self.memory = memory
    
    def match(self, command: str) -> bool:
        """Match automation commands"""
        keywords = ['mouse', 'click', 'type', 'keyboard', 'screenshot', 
                   'move', 'press', 'scroll', 'automate']
        return any(k in command.lower() for k in keywords)
    
    def execute(self, command: str) -> str:
        """Execute automation command"""
        if not AVAILABLE:
            return "PyAutoGUI not installed. Run: pip install pyautogui"
        
        try:
            # Extract action from command
            cmd_lower = command.lower()
            
            if 'screenshot' in cmd_lower:
                path = 'screenshot.png'
                pyautogui.screenshot(path)
                return f"Screenshot saved to {path}"
            
            elif 'mouse' in cmd_lower and 'center' in cmd_lower:
                w, h = pyautogui.size()
                pyautogui.moveTo(w//2, h//2, duration=0.5)
                return f"Mouse moved to center ({w//2}, {h//2})"
            
            elif 'click' in cmd_lower:
                pyautogui.click()
                return "Clicked at current position"
            
            elif 'type' in cmd_lower or 'write' in cmd_lower:
                # Extract text to type
                match = re.search(r'["\'](.+?)["\']', command)
                if match:
                    text = match.group(1)
                    pyautogui.write(text, interval=0.1)
                    return f"Typed: {text}"
                return "No text found to type"
            
            elif 'position' in cmd_lower:
                pos = pyautogui.position()
                return f"Mouse position: {pos}"
            
            elif 'size' in cmd_lower or 'screen' in cmd_lower:
                size = pyautogui.size()
                return f"Screen size: {size}"
            
            return "Command not recognized. Available: screenshot, click, type, position, size"
            
        except Exception as e:
            log_error("autonomous_pyautogui", f"Execution failed: {e}")
            return f"Error: {str(e)}"
    
    @classmethod
    def schema(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "command": {
                    "type": "string",
                    "description": "Automation command to execute"
                }
            }
        }
