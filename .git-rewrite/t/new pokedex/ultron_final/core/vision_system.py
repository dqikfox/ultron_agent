"""Computer vision and OCR system"""
import cv2
import pytesseract
import numpy as np
from PIL import Image, ImageGrab
from pathlib import Path
import logging
from datetime import datetime

class VisionSystem:
    def __init__(self, config):
        self.config = config['vision']
        self.screenshots_dir = Path("screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
        self.available = False
        self.setup()
    
    def setup(self):
        try:
            # Test OCR availability
            pytesseract.get_tesseract_version()
            self.available = True
            logging.info("Vision system initialized")
        except Exception as e:
            logging.error(f"Vision system init failed: {e}")
    
    async def take_screenshot(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.screenshots_dir / f"screenshot_{timestamp}.png"
            
            screenshot = ImageGrab.grab()
            screenshot.save(filename)
            
            return {"success": True, "path": str(filename)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def extract_text(self, image_path):
        try:
            image = cv2.imread(str(image_path))
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            if self.config.get('auto_enhance', True):
                gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
            
            text = pytesseract.image_to_string(gray, lang=self.config.get('ocr_language', 'eng'))
            return text.strip()
        except Exception as e:
            logging.error(f"OCR error: {e}")
            return ""
    
    def is_available(self):
        return self.available
