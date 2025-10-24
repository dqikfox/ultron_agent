"""
Screenshot Analyzer Tool for ULTRON Agent
Takes screenshots, analyzes them with AI, and saves descriptions
"""

import os
import time
import requests
import json
import base64
from PIL import Image
import pyautogui
from utils.ultron_logger import log_info, log_error

class ScreenshotAnalyzerTool:
    """Tool for taking screenshots and AI analysis"""
    
    name = "Screenshot Analyzer Tool"
    description = "Takes screenshots, analyzes with AI vision, saves descriptions"
    
    def __init__(self, config=None):
        self.config = config or {}
        self.screenshot_dir = "screenshots"
        self.description_dir = os.path.join(self.screenshot_dir, "descriptions")
        os.makedirs(self.screenshot_dir, exist_ok=True)
        os.makedirs(self.description_dir, exist_ok=True)
    
    def match(self, command: str) -> bool:
        """Check if command matches screenshot analysis"""
        return any(keyword in command.lower() for keyword in [
            "screenshot analyze", "analyze screen", "describe screen", 
            "screenshot description", "screen analysis"
        ])
    
    def execute(self, command: str) -> str:
        """Execute screenshot analysis"""
        try:
            # Take screenshot
            timestamp = int(time.time())
            screenshot_filename = f"screenshot_{timestamp}.png"
            screenshot_path = os.path.join(self.screenshot_dir, screenshot_filename)
            
            screenshot = pyautogui.screenshot()
            screenshot.save(screenshot_path)
            log_info("screenshot_analyzer", f"Screenshot saved: {screenshot_path}")
            
            # Analyze with AI
            description = self._analyze_screenshot(screenshot_path)
            
            # Save description
            description_filename = f"screenshot_{timestamp}.txt"
            description_path = os.path.join(self.description_dir, description_filename)
            
            with open(description_path, 'w', encoding='utf-8') as f:
                f.write(description)
            
            log_info("screenshot_analyzer", f"Description saved: {description_path}")
            
            return f"Screenshot analyzed successfully!\nImage: {screenshot_path}\nDescription: {description_path}\n\nAI Description:\n{description}"
            
        except Exception as e:
            log_error("screenshot_analyzer", f"Analysis failed: {e}")
            return f"Screenshot analysis error: {str(e)}"
    
    def _analyze_screenshot(self, image_path: str) -> str:
        """Analyze screenshot with AI vision model"""
        try:
            # Try Ollama vision model first
            description = self._analyze_with_ollama(image_path)
            if description:
                return description
            
            # Fallback to basic description
            return self._basic_description(image_path)
            
        except Exception as e:
            log_error("screenshot_analyzer", f"AI analysis failed: {e}")
            return f"AI analysis failed: {str(e)}"
    
    def _analyze_with_ollama(self, image_path: str) -> str:
        """Analyze with Ollama vision model"""
        try:
            # Encode image to base64
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Prepare request for Ollama vision model
            payload = {
                "model": "llava:7b",
                "prompt": "Describe this screenshot in detail. What applications, windows, or content do you see? What is the user doing? Be specific and comprehensive.",
                "images": [image_data],
                "stream": False
            }
            
            response = requests.post("http://localhost:11434/api/generate", 
                                   json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                description = result.get("response", "")
                log_info("screenshot_analyzer", "AI vision analysis completed")
                return description
            else:
                log_error("screenshot_analyzer", f"Ollama API error: {response.status_code}")
                return None
                
        except Exception as e:
            log_error("screenshot_analyzer", f"Ollama analysis error: {e}")
            return None
    
    def _basic_description(self, image_path: str) -> str:
        """Basic description when AI analysis fails"""
        try:
            # Get image info
            with Image.open(image_path) as img:
                width, height = img.size
                mode = img.mode
            
            # Get file info
            file_size = os.path.getsize(image_path)
            timestamp = time.ctime(os.path.getctime(image_path))
            
            description = f"""Screenshot Analysis (Basic Mode)
Timestamp: {timestamp}
Image Size: {width}x{height} pixels
Color Mode: {mode}
File Size: {file_size} bytes
Location: {image_path}

Note: AI vision analysis was not available. This is a basic technical description of the screenshot file."""
            
            return description
            
        except Exception as e:
            return f"Basic analysis failed: {str(e)}"
    
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
                        "description": "Screenshot analysis command"
                    }
                },
                "required": ["command"]
            }
        }