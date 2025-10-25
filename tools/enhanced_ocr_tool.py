"""
ULTRON Agent - Enhanced OCR Tool with MCP Integration
Fixed OCR processing with comprehensive text extraction and analysis.
"""

import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from utils.ultron_logger import log_info, log_error


class EnhancedOCRTool:
    """Enhanced OCR with preprocessing and MCP integration"""
    
    name = "enhanced_ocr"
    description = "Advanced OCR with image preprocessing and text analysis"
    
    def __init__(self):
        self.tesseract_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\Users\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
        ]
        self._setup_tesseract()
    
    def _setup_tesseract(self):
        """Setup Tesseract OCR engine"""
        for path in self.tesseract_paths:
            if Path(path).exists():
                pytesseract.pytesseract.tesseract_cmd = path
                log_info("enhanced_ocr", f"Tesseract found at: {path}")
                return
        
        log_error("enhanced_ocr", "Tesseract not found in standard locations")
    
    def match(self, command: str) -> bool:
        """Match OCR-related commands"""
        keywords = ["ocr", "read", "text", "extract", "scan", "screenshot", "image"]
        return any(keyword in command.lower() for keyword in keywords)
    
    def execute(self, command: str, **kwargs) -> str:
        """Execute OCR command"""
        try:
            image_path = kwargs.get("image_path")
            if not image_path:
                # Take screenshot if no image provided
                image_path = self._take_screenshot()
            
            # Process image and extract text
            result = self._process_image(image_path)
            
            # Analyze extracted text
            analysis = self._analyze_text(result["text"])
            
            return json.dumps({
                "status": "success",
                "image_path": str(image_path),
                "raw_text": result["text"],
                "confidence": result["confidence"],
                "analysis": analysis,
                "word_count": len(result["text"].split()),
                "processing_time": result.get("processing_time", 0)
            }, indent=2)
            
        except Exception as e:
            log_error("enhanced_ocr", f"OCR failed: {str(e)}")
            return json.dumps({
                "status": "error",
                "error": str(e)
            })
    
    def _take_screenshot(self) -> Path:
        """Take screenshot for OCR processing"""
        try:
            import pyautogui
            
            screenshot_dir = Path("screenshots")
            screenshot_dir.mkdir(exist_ok=True)
            
            screenshot_path = screenshot_dir / "ocr_screenshot.png"
            screenshot = pyautogui.screenshot()
            screenshot.save(screenshot_path)
            
            log_info("enhanced_ocr", f"Screenshot saved: {screenshot_path}")
            return screenshot_path
            
        except Exception as e:
            log_error("enhanced_ocr", f"Screenshot failed: {str(e)}")
            raise
    
    def _process_image(self, image_path: Path) -> Dict:
        """Process image with advanced preprocessing"""
        try:
            # Load image
            image = cv2.imread(str(image_path))
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Preprocessing pipeline
            processed_image = self._preprocess_image(image)
            
            # OCR with multiple configurations
            results = []
            
            # Configuration 1: Standard
            text1 = pytesseract.image_to_string(processed_image, config='--psm 6')
            confidence1 = self._get_confidence(processed_image, '--psm 6')
            results.append({"text": text1, "confidence": confidence1, "config": "standard"})
            
            # Configuration 2: Single text block
            text2 = pytesseract.image_to_string(processed_image, config='--psm 8')
            confidence2 = self._get_confidence(processed_image, '--psm 8')
            results.append({"text": text2, "confidence": confidence2, "config": "single_block"})
            
            # Configuration 3: Single word
            text3 = pytesseract.image_to_string(processed_image, config='--psm 7')
            confidence3 = self._get_confidence(processed_image, '--psm 7')
            results.append({"text": text3, "confidence": confidence3, "config": "single_word"})
            
            # Select best result
            best_result = max(results, key=lambda x: x["confidence"])
            
            log_info("enhanced_ocr", f"OCR completed with {best_result['confidence']}% confidence")
            
            return {
                "text": best_result["text"].strip(),
                "confidence": best_result["confidence"],
                "config_used": best_result["config"],
                "all_results": results
            }
            
        except Exception as e:
            log_error("enhanced_ocr", f"Image processing failed: {str(e)}")
            raise
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Advanced image preprocessing for better OCR"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Noise reduction
        denoised = cv2.medianBlur(gray, 3)
        
        # Contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)
        
        # Adaptive thresholding
        binary = cv2.adaptiveThreshold(
            enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Morphological operations to clean up
        kernel = np.ones((2,2), np.uint8)
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
    
    def _get_confidence(self, image: np.ndarray, config: str) -> float:
        """Get OCR confidence score"""
        try:
            data = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            
            if confidences:
                return sum(confidences) / len(confidences)
            else:
                return 0.0
                
        except Exception:
            return 0.0
    
    def _analyze_text(self, text: str) -> Dict:
        """Analyze extracted text for insights"""
        if not text.strip():
            return {"type": "empty", "insights": []}
        
        analysis = {
            "type": "unknown",
            "insights": [],
            "entities": [],
            "keywords": []
        }
        
        text_lower = text.lower()
        
        # Detect content type
        if any(word in text_lower for word in ["http", "www", ".com", ".org"]):
            analysis["type"] = "web_content"
            analysis["insights"].append("Contains web URLs or domains")
        
        if any(word in text_lower for word in ["@", "email", "gmail", "outlook"]):
            analysis["type"] = "email_content"
            analysis["insights"].append("Contains email addresses or references")
        
        if any(word in text_lower for word in ["$", "price", "cost", "total", "amount"]):
            analysis["type"] = "financial_content"
            analysis["insights"].append("Contains financial information")
        
        if any(word in text_lower for word in ["date", "time", "schedule", "meeting"]):
            analysis["type"] = "calendar_content"
            analysis["insights"].append("Contains date/time information")
        
        # Extract potential entities
        words = text.split()
        for word in words:
            if word.isupper() and len(word) > 2:
                analysis["entities"].append(word)
            if word.startswith("#"):
                analysis["keywords"].append(word)
        
        # Content quality assessment
        if len(text.split()) > 10:
            analysis["insights"].append("Substantial text content detected")
        else:
            analysis["insights"].append("Limited text content")
        
        return analysis
    
    @staticmethod
    def schema():
        return {
            "name": "enhanced_ocr",
            "description": "Advanced OCR with image preprocessing and text analysis",
            "parameters": {
                "command": {"type": "string", "description": "OCR command"},
                "image_path": {"type": "string", "description": "Path to image file (optional)"}
            }
        }