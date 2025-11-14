"""
Simple OCR Test
"""
import pytesseract
from PIL import Image, ImageDraw
from pathlib import Path

# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

print("Testing OCR...")

# Create test image
img = Image.new('RGB', (300, 100), color='white')
draw = ImageDraw.Draw(img)
draw.text((20, 30), "ULTRON TEST", fill='black')

# Save
test_path = "test_ocr_image.png"
img.save(test_path)
print(f"Created: {test_path}")

# OCR
try:
    text = pytesseract.image_to_string(img)
    print(f"OCR Result: '{text.strip()}'")
    
    if "ULTRON" in text or "TEST" in text:
        print("SUCCESS: OCR working!")
    else:
        print(f"WARNING: Expected 'ULTRON TEST', got '{text.strip()}'")
        
except Exception as e:
    print(f"FAILED: {e}")
