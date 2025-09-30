import logging
import pytesseract
from PIL import ImageGrab
import os
from datetime import datetime

class Vision:
    def __init__(self):
        self.screenshots_dir = "screenshots"
        os.makedirs(self.screenshots_dir, exist_ok=True)
        logging.info("Vision subsystem initialized.")

    def capture_screen(self):
        logging.info("Capturing screen...")
        screen = ImageGrab.grab()
        
        # Save screenshot with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = os.path.join(self.screenshots_dir, filename)
        screen.save(filepath)
        
        logging.info(f"Screenshot saved: {filepath}")
        return screen, filepath

    def perform_ocr(self, image):
        logging.info("Performing OCR on the captured image...")
        text = pytesseract.image_to_string(image)
        return text

    def capture_and_ocr(self):
        screen, filepath = self.capture_screen()
        text = self.perform_ocr(screen)
        return {"text": text, "screenshot_path": filepath}