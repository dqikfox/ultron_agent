"""
Smart Screenshot Tool for ULTRON Agent
OCR-based screenshot analysis integrated with PyAutoGUI
"""

import os
import time
import pyautogui
import pytesseract
from PIL import Image
from utils.ultron_logger import log_info, log_error
from .tool_interface import ToolInterface
from .image_description_tool import ImageDescriptionTool

class SmartScreenshotTool(ToolInterface):
    """Smart screenshot tool with OCR analysis"""
    
    @property
    def name(self) -> str:
        return "Smart Screenshot Tool"
    
    @property
    def description(self) -> str:
        return "Takes screenshots with OCR analysis of actual content"
    
    def match(self, command: str) -> bool:
        return any(keyword in command.lower() for keyword in [
            "smart screenshot", "analyze screen", "ocr screenshot", 
            "screenshot analyze", "screen analysis"
        ])
    
    def execute(self, command: str, **kwargs) -> str:
        try:
            # Use Pictures/Screenshots folder
            pictures_path = os.path.join(os.path.expanduser("~"), "OneDrive", "Pictures", "Screenshots")
            description_path = os.path.join(pictures_path, "descriptions")
            
            os.makedirs(pictures_path, exist_ok=True)
            os.makedirs(description_path, exist_ok=True)
            
            # Take screenshot
            timestamp = int(time.time())
            screenshot_filename = f"screenshot_{timestamp}.png"
            screenshot_file = os.path.join(pictures_path, screenshot_filename)
            
            screenshot = pyautogui.screenshot()
            screenshot.save(screenshot_file)
            log_info("smart_screenshot", f"Screenshot saved: {screenshot_file}")
            
            # OCR analysis
            ocr_analysis = self._analyze_with_ocr(screenshot_file)
            
            # Image description analysis
            image_tool = ImageDescriptionTool()
            image_analysis = image_tool.analyze_screenshot(screenshot_file)
            
            analysis = f"{ocr_analysis}\n\nIMAGE VISUAL ANALYSIS:\n{image_analysis}"
            
            # Save description
            description_filename = f"screenshot_{timestamp}.txt"
            description_file = os.path.join(description_path, description_filename)
            
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            width, height = screenshot.size
            
            full_description = f"""ULTRON Agent Smart Screenshot Analysis
Generated: {current_time}
Screenshot: {screenshot_filename} ({width}x{height})

{analysis}

Technical Info:
- File: {screenshot_file}
- Size: {os.path.getsize(screenshot_file)} bytes
- Timestamp: {timestamp}"""
            
            with open(description_file, 'w', encoding='utf-8') as f:
                f.write(full_description)
            
            log_info("smart_screenshot", f"Description saved: {description_file}")
            
            return f"Smart screenshot with image analysis complete!\nImage: {screenshot_file}\nDescription: {description_file}\n\n{ocr_analysis}"
            
        except Exception as e:
            log_error("smart_screenshot", f"Screenshot failed: {e}")
            return f"Screenshot error: {str(e)}"
    
    def _analyze_with_ocr(self, image_path: str) -> str:
        """Analyze screenshot with OCR"""
        try:
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            
            extracted_text = pytesseract.image_to_string(Image.open(image_path))
            lines = [line.strip() for line in extracted_text.split('\n') if line.strip()]
            
            analysis = self._analyze_content(lines)
            
            return f"""WHAT'S ACTUALLY ON SCREEN:
{analysis}

RAW TEXT DETECTED ({len(lines)} lines):
{chr(10).join(lines[:20])}

OCR Engine: Tesseract"""
            
        except Exception as e:
            return f"OCR analysis failed: {str(e)}"
    
    def _analyze_content(self, lines):
        """Analyze OCR text to understand screen content"""
        text = ' '.join(lines).lower()
        analysis = []
        
        if 'vs code' in text or 'visual studio code' in text:
            analysis.append("- VS Code editor is open")
        if 'terminal' in text or 'powershell' in text or 'pwsh' in text:
            analysis.append("- Terminal/PowerShell window active")
        if 'browser' in text or 'http://' in text or 'localhost' in text:
            analysis.append("- Web browser with localhost development server")
        if 'amazon q' in text:
            analysis.append("- Amazon Q AI assistant interface visible")
        if 'ultron' in text:
            analysis.append("- ULTRON Agent project files/interface")
        if 'error' in text or 'exception' in text:
            analysis.append("- Error messages or debugging information")
        if 'test' in text or 'testing' in text:
            analysis.append("- Testing or development output")
        if 'screenshot' in text:
            analysis.append("- Screenshot-related content or tools")
        if 'code issues' in text:
            analysis.append("- Code analysis or issue tracking panel")
        if '.py' in text:
            analysis.append("- Python files visible")
        if '.html' in text or '.js' in text:
            analysis.append("- Web development files")
        if 'debug' in text or 'console' in text:
            analysis.append("- Debug console or development tools")
        
        if not analysis:
            analysis.append("- General desktop/application interface")
        
        return '\n'.join(analysis)
    
    @classmethod
    def schema(cls):
        return {
            "name": "Smart Screenshot Tool",
            "description": "Takes screenshots with OCR analysis of actual content",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Screenshot command"
                    }
                },
                "required": ["command"]
            }
        }