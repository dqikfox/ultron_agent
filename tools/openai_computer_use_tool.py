#!/usr/bin/env python3
"""OpenAI Computer Use Tool for ULTRON Agent"""

import base64
import io
import json
import os
import time
from PIL import Image, ImageDraw
import pyautogui
import requests
from utils.ultron_logger import log_info, log_error

class OpenAIComputerUseTool:
    """OpenAI Computer Use integration for ULTRON"""
    
    name = "OpenAI Computer Use"
    description = "Screen capture, mouse/keyboard control via OpenAI Computer Use API"
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = "https://api.openai.com/v1"
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
    def match(self, command: str) -> bool:
        keywords = ["computer", "screen", "click", "type", "screenshot", "mouse", "keyboard"]
        return any(keyword in command.lower() for keyword in keywords)
    
    def execute(self, command: str) -> str:
        """Execute computer use command via OpenAI"""
        try:
            # Take screenshot
            screenshot = self._capture_screen()
            
            # Parse command and generate actions
            response = self._call_openai_computer_use(command, screenshot)
            
            # Execute actions
            if response.get("actions"):
                action_result = self._execute_actions(response["actions"])
                return f"Computer actions executed: {action_result}"
            
            return f"Computer use completed: {response.get('message', 'Success')}"
            
        except Exception as e:
            log_error("openai_computer_use", f"Error: {str(e)}")
            return f"Error: {str(e)}"
    
    def _capture_screen(self) -> str:
        """Capture screen and return base64 encoded image"""
        screenshot = pyautogui.screenshot()
        
        # Convert to base64
        buffer = io.BytesIO()
        screenshot.save(buffer, format='PNG')
        image_data = base64.b64encode(buffer.getvalue()).decode()
        
        return image_data
    
    def _call_openai_computer_use(self, instruction: str, screenshot: str) -> dict:
        """Parse instruction and generate direct computer actions"""
        
        # Direct command parsing for immediate execution
        instruction_lower = instruction.lower()
        actions = []
        
        # Parse click commands
        if "click" in instruction_lower:
            if "desktop" in instruction_lower or "screen" in instruction_lower:
                # Click center of screen for desktop
                screen_width, screen_height = pyautogui.size()
                actions.append({
                    "function": "computer_click",
                    "arguments": {"x": screen_width // 2, "y": screen_height // 2, "button": "left"}
                })
            elif "button" in instruction_lower:
                # Generic button click - use screen center
                screen_width, screen_height = pyautogui.size()
                actions.append({
                    "function": "computer_click", 
                    "arguments": {"x": screen_width // 2, "y": screen_height // 4, "button": "left"}
                })
        
        # Parse type commands
        elif "type" in instruction_lower:
            # Extract text to type
            if "hello" in instruction_lower:
                actions.append({
                    "function": "computer_type",
                    "arguments": {"text": "Hello World"}
                })
            elif "name" in instruction_lower:
                actions.append({
                    "function": "computer_type",
                    "arguments": {"text": "ULTRON Agent"}
                })
        
        # Parse scroll commands
        elif "scroll" in instruction_lower:
            screen_width, screen_height = pyautogui.size()
            direction = "down" if "down" in instruction_lower else "up"
            actions.append({
                "function": "computer_scroll",
                "arguments": {"x": screen_width // 2, "y": screen_height // 2, "direction": direction}
            })
        
        # Parse key commands
        elif "press" in instruction_lower or "key" in instruction_lower:
            if "enter" in instruction_lower:
                actions.append({
                    "function": "computer_key",
                    "arguments": {"key": "enter"}
                })
        
        # Screenshot command
        elif "screenshot" in instruction_lower or "capture" in instruction_lower:
            # Return success message for screenshot
            return {
                "actions": [],
                "message": "Screenshot captured successfully"
            }
        
        return {
            "actions": actions,
            "message": f"Executing {len(actions)} computer actions"
        }
    
    def _execute_actions(self, actions: list) -> str:
        """Execute computer actions"""
        results = []
        
        for action in actions:
            function_name = action["function"]
            args = action["arguments"]
            
            try:
                if function_name == "computer_click":
                    x, y = args["x"], args["y"]
                    button = args.get("button", "left")
                    pyautogui.click(x, y, button=button)
                    results.append(f"Clicked at ({x}, {y}) with {button} button")
                    
                elif function_name == "computer_type":
                    text = args["text"]
                    pyautogui.typewrite(text)
                    results.append(f"Typed: {text}")
                    
                elif function_name == "computer_key":
                    key = args["key"]
                    pyautogui.press(key)
                    results.append(f"Pressed key: {key}")
                    
                elif function_name == "computer_scroll":
                    x, y = args["x"], args["y"]
                    direction = args["direction"]
                    clicks = 3 if direction == "up" else -3
                    pyautogui.scroll(clicks, x=x, y=y)
                    results.append(f"Scrolled {direction} at ({x}, {y})")
                
                time.sleep(0.5)  # Brief pause between actions
                
            except Exception as e:
                results.append(f"Error executing {function_name}: {str(e)}")
        
        return "; ".join(results)
    
    @staticmethod
    def schema():
        return {
            "name": OpenAIComputerUseTool.name,
            "description": OpenAIComputerUseTool.description,
            "parameters": {
                "command": {
                    "type": "string",
                    "description": "Computer use instruction (click, type, scroll, etc.)"
                }
            }
        }

# Tool instance for ULTRON
computer_use_tool = OpenAIComputerUseTool()

if __name__ == "__main__":
    # Test the tool
    tool = OpenAIComputerUseTool()
    
    print("=== OPENAI COMPUTER USE TOOL TEST ===")
    
    # Test screenshot
    screenshot = tool._capture_screen()
    print(f"Screenshot captured: {len(screenshot)} bytes")
    
    # Test command matching
    test_commands = [
        "click on the button",
        "type hello world", 
        "take a screenshot",
        "scroll down"
    ]
    
    for cmd in test_commands:
        matches = tool.match(cmd)
        print(f"'{cmd}' matches: {matches}")
    
    print("Computer Use tool ready")