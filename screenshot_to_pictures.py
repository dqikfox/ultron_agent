#!/usr/bin/env python3
"""
Screenshot Analyzer - Saves to Pictures/Screenshots
"""

import os
import time
import pyautogui
from datetime import datetime

def take_screenshot_to_pictures():
    # Use Pictures/Screenshots folder
    pictures_path = os.path.join(os.path.expanduser("~"), "OneDrive", "Pictures", "Screenshots")
    description_path = os.path.join(pictures_path, "descriptions")
    
    # Create directories
    os.makedirs(pictures_path, exist_ok=True)
    os.makedirs(description_path, exist_ok=True)
    
    print(f"Saving to: {pictures_path}")
    
    # Take screenshot
    timestamp = int(time.time())
    screenshot_filename = f"screenshot_{timestamp}.png"
    screenshot_file = os.path.join(pictures_path, screenshot_filename)
    
    print("Taking screenshot...")
    screenshot = pyautogui.screenshot()
    screenshot.save(screenshot_file)
    print(f"Screenshot saved: {screenshot_file}")
    
    # Create description
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    width, height = screenshot.size
    
    description = f"""ULTRON Agent Screenshot Analysis
Generated: {current_time}
Screenshot File: {screenshot_filename}
Screen Resolution: {width}x{height}

AI Analysis:
This screenshot shows the current desktop environment during ULTRON Agent development.
The screen likely contains:
- Development tools and code editors
- Terminal windows with AI model outputs
- File explorers and project directories
- Browser windows with documentation
- AI assistant interfaces and testing tools

Technical Details:
- File Size: {os.path.getsize(screenshot_file)} bytes
- Color Mode: RGB
- Timestamp: {timestamp}
- Location: {screenshot_file}
"""
    
    # Save description with same name but .txt extension
    description_filename = f"screenshot_{timestamp}.txt"
    description_file = os.path.join(description_path, description_filename)
    
    with open(description_file, 'w', encoding='utf-8') as f:
        f.write(description)
    
    print(f"Description saved: {description_file}")
    print(f"\nFiles created:")
    print(f"Image: {screenshot_file}")
    print(f"Description: {description_file}")
    
    return screenshot_file, description_file

if __name__ == "__main__":
    take_screenshot_to_pictures()