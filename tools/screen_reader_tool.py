from .base import Tool
import logging
import pytesseract
from PIL import ImageGrab

class ScreenReaderTool(Tool):
    def __init__(self):
        self.name = "ScreenReaderTool"
        self.description = "Performs screen OCR operations."
        super().__init__()

    def match(self, command: str) -> bool:
        cmd = command.lower()
        return "read screen" in cmd or "ocr" in cmd

    def execute(self, command: str) -> str:
        try:
            # Capture the screen
            screenshot = ImageGrab.grab()
            screenshot.save("screenshot.png")

            # Perform OCR on the captured image
            text = pytesseract.image_to_string(screenshot)
            logging.info("OCR performed successfully.")
            return text if text else "No text found on the screen."
        except Exception as e:
            logging.error(f"Screen reading error: {e}")
            return f"Error: {e}"