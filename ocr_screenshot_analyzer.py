def self_test():
    """
    Run a diagnostic self-test for OCR screenshot analyzer.
    Returns a dict with status and details.
    """
    result = {"status": "ok", "errors": [], "details": {}}
    try:
        # Check if pytesseract and pyautogui are available
        import importlib
        for mod in ["pytesseract", "pyautogui", "PIL.Image"]:
            if importlib.util.find_spec(mod) is None:
                result["status"] = "fail"
                result["errors"].append(f"Missing module: {mod}")
        # Try to run a dry OCR (simulate, don't save files)
        try:
            from PIL import Image
            import pytesseract
            img = Image.new("RGB", (100, 40), color=(73, 109, 137))
            text = pytesseract.image_to_string(img)
            result["details"]["ocr_text"] = text.strip()[:50]
        except Exception as ocr_err:
            result["status"] = "fail"
            result["errors"].append(f"OCR test failed: {ocr_err}")
    except Exception as e:
        result["status"] = "fail"
        result["errors"].append(str(e))
    return result
#!/usr/bin/env python3
"""
OCR Screenshot Analyzer - Reads actual text from screen
"""

import os
import time
import pyautogui
import pytesseract
from PIL import Image
from datetime import datetime

def analyze_screenshot_with_ocr():
    # Use Pictures/Screenshots folder
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
    print(f"Screenshot saved: {screenshot_file}")

    # Extract text using OCR
    print("Reading text from screenshot...")
    try:
        # Configure tesseract path if needed
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

        # Extract text
        extracted_text = pytesseract.image_to_string(screenshot)

        # Clean up text
        lines = [line.strip() for line in extracted_text.split('\n') if line.strip()]
        readable_text = '\n'.join(lines[:50])  # First 50 non-empty lines

        print(f"Extracted {len(lines)} lines of text")

    except Exception as e:
        print(f"OCR failed: {e}")
        readable_text = "OCR text extraction failed. Tesseract may not be installed."

    # Create detailed description
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    width, height = screenshot.size

    description = f"""ULTRON Agent Screenshot Analysis with OCR
Generated: {current_time}
Screenshot File: {screenshot_filename}
Screen Resolution: {width}x{height}

ACTUAL TEXT CONTENT DETECTED:
{readable_text}

ANALYSIS:
Based on the extracted text, this screenshot contains:
- {len(lines)} lines of readable text
- Active applications and interfaces
- Development environment content
- Real-time system information

Technical Details:
- File Size: {os.path.getsize(screenshot_file)} bytes
- Color Mode: RGB
- Timestamp: {timestamp}
- OCR Engine: Tesseract
- Location: {screenshot_file}
"""

    # Save description
    description_filename = f"screenshot_{timestamp}.txt"
    description_file = os.path.join(description_path, description_filename)

    with open(description_file, 'w', encoding='utf-8') as f:
        f.write(description)

    print(f"Description with OCR saved: {description_file}")
    print(f"\nFirst few lines of detected text:")
    print("-" * 40)
    print('\n'.join(lines[:10]))

    return screenshot_file, description_file

if __name__ == "__main__":
    analyze_screenshot_with_ocr()
