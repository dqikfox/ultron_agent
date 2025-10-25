#!/usr/bin/env python3
"""
Smart Screenshot Analyzer - OCR + AI Analysis of actual content
"""

import os
import time
import pyautogui
import pytesseract
from datetime import datetime

def smart_analyze_screenshot():
    pictures_path = os.path.join(os.path.expanduser("~"), "OneDrive", "Pictures", "Screenshots")
    description_path = os.path.join(pictures_path, "descriptions")
    
    os.makedirs(pictures_path, exist_ok=True)
    os.makedirs(description_path, exist_ok=True)
    
    print("Taking screenshot and analyzing actual content...")
    
    # Take screenshot
    timestamp = int(time.time())
    screenshot_filename = f"screenshot_{timestamp}.png"
    screenshot_file = os.path.join(pictures_path, screenshot_filename)
    
    screenshot = pyautogui.screenshot()
    screenshot.save(screenshot_file)
    
    # Extract and analyze text
    try:
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        extracted_text = pytesseract.image_to_string(screenshot)
        lines = [line.strip() for line in extracted_text.split('\n') if line.strip()]
        
        # Analyze content
        analysis = analyze_content(lines)
        
    except Exception as e:
        lines = []
        analysis = f"OCR failed: {e}"
    
    # Create smart description
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    width, height = screenshot.size
    
    description = f"""ULTRON Agent Smart Screenshot Analysis
Generated: {current_time}
Screenshot: {screenshot_filename} ({width}x{height})

WHAT'S ACTUALLY ON SCREEN:
{analysis}

RAW TEXT DETECTED ({len(lines)} lines):
{chr(10).join(lines[:30])}

Technical Info:
- File: {screenshot_file}
- Size: {os.path.getsize(screenshot_file)} bytes
- Timestamp: {timestamp}
"""
    
    # Save description
    description_filename = f"screenshot_{timestamp}.txt"
    description_file = os.path.join(description_path, description_filename)
    
    with open(description_file, 'w', encoding='utf-8') as f:
        f.write(description)
    
    print(f"Smart analysis complete!")
    print(f"Image: {screenshot_file}")
    print(f"Description: {description_file}")
    print(f"\nWhat's on screen:\n{analysis}")
    
    return screenshot_file, description_file

def analyze_content(lines):
    """Analyze OCR text to understand what's actually on screen"""
    text = ' '.join(lines).lower()
    
    analysis = []
    
    # Check for applications
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
    
    # Check for specific content
    if 'error' in text or 'exception' in text:
        analysis.append("- Error messages or debugging information")
    if 'test' in text or 'testing' in text:
        analysis.append("- Testing or development output")
    if 'screenshot' in text:
        analysis.append("- Screenshot-related content or tools")
    if 'code issues' in text:
        analysis.append("- Code analysis or issue tracking panel")
    
    # Check for file types
    if '.py' in text:
        analysis.append("- Python files visible")
    if '.html' in text or '.js' in text:
        analysis.append("- Web development files")
    if '.md' in text:
        analysis.append("- Markdown documentation")
    
    # Check for development activity
    if 'debug' in text or 'console' in text:
        analysis.append("- Debug console or development tools")
    if 'git' in text or 'commit' in text:
        analysis.append("- Version control (Git) activity")
    
    if not analysis:
        analysis.append("- General desktop/application interface")
    
    return '\n'.join(analysis)

if __name__ == "__main__":
    smart_analyze_screenshot()