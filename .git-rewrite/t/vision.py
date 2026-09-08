import logging
import pytesseract
from PIL import ImageGrab

class Vision:
    def __init__(self):
        logging.info("Vision subsystem initialized.")

    def capture_screen(self):
        logging.info("Capturing screen...")
        screen = ImageGrab.grab()
        return screen

    def perform_ocr(self, image):
        logging.info("Performing OCR on the captured image...")
        text = pytesseract.image_to_string(image)
        return text

    def capture_and_ocr(self):
        screen = self.capture_screen()
        text = self.perform_ocr(screen)
        return text