"""
ULTRON Vision System - Advanced OCR and Screen Analysis
Implements OCR accuracy enhancement strategies from the developer guide.
"""

import os
import time
import logging
import asyncio
from typing import Optional, Dict, List, Tuple, Any
from pathlib import Path
import math

import numpy as np
from PIL import Image, ImageGrab, ImageEnhance, ImageFilter
import pyautogui

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    logging.warning("OpenCV not available")

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logging.warning("Tesseract not available")

try:
    import torch
    from transformers import AutoProcessor, AutoModelForCausalLM
    VISION_AI_AVAILABLE = True
except ImportError:
    VISION_AI_AVAILABLE = False
    logging.warning("Vision AI models not available")

class VisionSystem:
    """Advanced vision processing with OCR optimization"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger("VisionSystem")
        self.screenshots_dir = Path("D:/ULTRON/screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
        
        # OCR Configuration
        self.tesseract_config = {
            'default': "--oem 3 --psm 6",  # LSTM engine, uniform text block
            'single_line': "--oem 3 --psm 7",  # Single text line
            'single_word': "--oem 3 --psm 8",  # Single word
            'single_char': "--oem 3 --psm 10"  # Single character
        }
        
        # Vision AI Model (if available)
        self.vision_model = None
        self.vision_processor = None
        
        if VISION_AI_AVAILABLE and config.vision_enabled:
            self._initialize_vision_ai()
        
        # Performance metrics
        self.ocr_times = []
        self.screenshot_count = 0
        
        self.logger.info("Vision system initialized")
    
    def _initialize_vision_ai(self):
        """Initialize vision AI model for advanced analysis"""
        try:
            # Use a lightweight vision model for local processing
            model_name = "microsoft/git-base"  # Git model for image captioning
            
            self.logger.info(f"Loading vision AI model: {model_name}")
            self.vision_processor = AutoProcessor.from_pretrained(model_name)
            self.vision_model = AutoModelForCausalLM.from_pretrained(model_name)
            
            self.logger.info("Vision AI model loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load vision AI model: {e}")
            self.vision_model = None
            self.vision_processor = None
    
    async def take_screenshot(self, region: Optional[Tuple[int, int, int, int]] = None) -> str:
        """Take screenshot and save to file"""
        try:
            timestamp = int(time.time())
            filename = f"screenshot_{timestamp}.png"
            filepath = self.screenshots_dir / filename
            
            if region:
                # Capture specific region
                screenshot = pyautogui.screenshot(region=region)
            else:
                # Capture full screen
                screenshot = pyautogui.screenshot()
            
            screenshot.save(filepath)
            self.screenshot_count += 1
            
            self.logger.info(f"Screenshot saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Screenshot error: {e}")
            return ""
    
    async def analyze_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> Dict[str, Any]:
        """Analyze screen content using OCR and AI"""
        try:
            # Take screenshot
            screenshot_path = await self.take_screenshot(region)
            if not screenshot_path:
                return {"error": "Failed to capture screenshot"}
            
            # Load image
            image = Image.open(screenshot_path)
            
            # Perform OCR
            ocr_result = await self.extract_text_from_image(image)
            
            # Perform AI analysis if available
            ai_analysis = ""
            if self.vision_model and self.vision_processor:
                ai_analysis = await self._analyze_with_ai(image)
            
            result = {
                "screenshot_path": screenshot_path,
                "ocr_text": ocr_result.get("text", ""),
                "ocr_confidence": ocr_result.get("confidence", 0),
                "ai_analysis": ai_analysis,
                "processing_time": ocr_result.get("processing_time", 0),
                "image_size": image.size
            }
            
            self.logger.info(f"Screen analysis completed: {len(ocr_result.get('text', ''))} chars extracted")
            return result
            
        except Exception as e:
            self.logger.error(f"Screen analysis error: {e}")
            return {"error": str(e)}
    
    async def extract_text_from_image(self, image: Image.Image, 
                                    config_type: str = "default") -> Dict[str, Any]:
        """Extract text from image using optimized OCR"""
        if not TESSERACT_AVAILABLE:
            return {"error": "Tesseract not available", "text": "", "confidence": 0}
        
        try:
            start_time = time.time()
            
            # Preprocess image for better OCR
            processed_image = self._preprocess_image_for_ocr(image)
            
            # Perform OCR with specified configuration
            config = self.tesseract_config.get(config_type, self.tesseract_config["default"])
            
            # Extract text
            text = pytesseract.image_to_string(processed_image, config=config, lang="eng")
            
            # Get confidence data
            confidence_data = pytesseract.image_to_data(processed_image, config=config, output_type=pytesseract.Output.DICT)
            
            # Calculate average confidence
            confidences = [int(conf) for conf in confidence_data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            processing_time = time.time() - start_time
            self.ocr_times.append(processing_time)
            
            result = {
                "text": text.strip(),
                "confidence": round(avg_confidence, 2),
                "processing_time": round(processing_time, 2),
                "word_count": len(text.split()),
                "config_used": config_type
            }
            
            self.logger.info(f"OCR completed: {len(text)} chars, {avg_confidence}% confidence, {processing_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"OCR error: {e}")
            return {"error": str(e), "text": "", "confidence": 0}
    
    def _preprocess_image_for_ocr(self, image: Image.Image) -> Image.Image:
        """Preprocess image to improve OCR accuracy"""
        try:
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Apply preprocessing steps from the guide
            
            # 1. Increase resolution (DPI optimization)
            width, height = image.size
            if width < 1024:  # Scale up small images
                scale_factor = 1024 / width
                new_size = (int(width * scale_factor), int(height * scale_factor))
                image = image.resize(new_size, Image.LANCZOS)
            
            # 2. Convert to grayscale
            gray_image = image.convert('L')
            
            # 3. Enhance contrast
            enhancer = ImageEnhance.Contrast(gray_image)
            enhanced_image = enhancer.enhance(1.5)
            
            # 4. Apply slight gaussian blur to reduce noise
            blurred_image = enhanced_image.filter(ImageFilter.GaussianBlur(radius=0.5))
            
            # 5. Convert to numpy for advanced processing
            if OPENCV_AVAILABLE:
                img_array = np.array(blurred_image)
                processed_array = self._advanced_preprocessing(img_array)
                return Image.fromarray(processed_array)
            else:
                return blurred_image
                
        except Exception as e:
            self.logger.error(f"Image preprocessing error: {e}")
            return image  # Return original image if preprocessing fails
    
    def _advanced_preprocessing(self, img_array: np.ndarray) -> np.ndarray:
        """Advanced image preprocessing using OpenCV"""
        try:
            # Apply adaptive threshold for better binarization
            adaptive_thresh = cv2.adaptiveThreshold(
                img_array, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 11
            )
            
            # Noise removal using morphological operations
            kernel = np.ones((2, 2), np.uint8)
            cleaned = cv2.morphologyEx(adaptive_thresh, cv2.MORPH_CLOSE, kernel)
            
            # Deskew correction
            deskewed = self._correct_skew(cleaned)
            
            return deskewed
            
        except Exception as e:
            self.logger.error(f"Advanced preprocessing error: {e}")
            return img_array
    
    def _correct_skew(self, image: np.ndarray) -> np.ndarray:
        """Correct image skew for better OCR"""
        try:
            # Find contours
            contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return image
            
            # Find the largest contour (assumed to be text)
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Get minimum area rectangle
            rect = cv2.minAreaRect(largest_contour)
            angle = rect[-1]
            
            # Correct angle
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
            
            # Only correct if angle is significant
            if abs(angle) > 0.5:
                (h, w) = image.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderValue=255)
                return rotated
            
            return image
            
        except Exception as e:
            self.logger.error(f"Skew correction error: {e}")
            return image
    
    async def _analyze_with_ai(self, image: Image.Image) -> str:
        """Analyze image using AI vision model"""
        try:
            if not self.vision_model or not self.vision_processor:
                return ""
            
            # Prepare image for the model
            inputs = self.vision_processor(images=image, return_tensors="pt")
            
            # Generate description
            with torch.no_grad():
                generated_ids = self.vision_model.generate(**inputs, max_length=100)
            
            # Decode the generated text
            generated_text = self.vision_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            return generated_text.strip()
            
        except Exception as e:
            self.logger.error(f"AI vision analysis error: {e}")
            return "AI analysis failed"
    
    async def read_text_at_coordinates(self, x: int, y: int, width: int = 200, height: int = 50) -> str:
        """Read text at specific screen coordinates"""
        try:
            # Define region around coordinates
            region = (x - width//2, y - height//2, width, height)
            
            # Take screenshot of region
            screenshot = pyautogui.screenshot(region=region)
            
            # Extract text
            result = await self.extract_text_from_image(screenshot, "single_line")
            return result.get("text", "")
            
        except Exception as e:
            self.logger.error(f"Coordinate text reading error: {e}")
            return ""
    
    async def find_text_on_screen(self, target_text: str) -> List[Dict[str, Any]]:
        """Find occurrences of text on screen"""
        try:
            # Take full screenshot
            screenshot = pyautogui.screenshot()
            
            # Extract text with detailed data
            if not TESSERACT_AVAILABLE:
                return []
            
            # Get detailed OCR data
            data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)
            
            matches = []
            n_boxes = len(data['level'])
            
            for i in range(n_boxes):
                text = data['text'][i].strip()
                if target_text.lower() in text.lower() and int(data['conf'][i]) > 30:
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    matches.append({
                        'text': text,
                        'confidence': data['conf'][i],
                        'position': {'x': x, 'y': y, 'width': w, 'height': h},
                        'center': {'x': x + w//2, 'y': y + h//2}
                    })
            
            self.logger.info(f"Found {len(matches)} matches for '{target_text}'")
            return matches
            
        except Exception as e:
            self.logger.error(f"Text search error: {e}")
            return []
    
    async def click_on_text(self, target_text: str) -> bool:
        """Find and click on text element"""
        try:
            matches = await self.find_text_on_screen(target_text)
            
            if matches:
                # Click on the first match
                best_match = max(matches, key=lambda x: x['confidence'])
                center = best_match['center']
                
                pyautogui.click(center['x'], center['y'])
                self.logger.info(f"Clicked on '{target_text}' at ({center['x']}, {center['y']})")
                return True
            else:
                self.logger.warning(f"Text '{target_text}' not found on screen")
                return False
                
        except Exception as e:
            self.logger.error(f"Click on text error: {e}")
            return False
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get vision system performance metrics"""
        if self.ocr_times:
            avg_time = sum(self.ocr_times) / len(self.ocr_times)
            max_time = max(self.ocr_times)
            min_time = min(self.ocr_times)
        else:
            avg_time = max_time = min_time = 0
        
        return {
            'screenshots_taken': self.screenshot_count,
            'ocr_operations': len(self.ocr_times),
            'avg_ocr_time': round(avg_time, 2),
            'max_ocr_time': round(max_time, 2),
            'min_ocr_time': round(min_time, 2),
            'tesseract_available': TESSERACT_AVAILABLE,
            'opencv_available': OPENCV_AVAILABLE,
            'vision_ai_available': self.vision_model is not None,
            'screenshots_dir': str(self.screenshots_dir)
        }
    
    async def monitor_screen_changes(self, callback, threshold: float = 0.1, interval: float = 1.0):
        """Monitor screen for changes and trigger callback"""
        try:
            previous_screenshot = None
            
            while True:
                # Take screenshot
                current_screenshot = pyautogui.screenshot()
                
                if previous_screenshot:
                    # Calculate difference
                    diff = self._calculate_image_difference(previous_screenshot, current_screenshot)
                    
                    if diff > threshold:
                        await callback(current_screenshot, diff)
                
                previous_screenshot = current_screenshot
                await asyncio.sleep(interval)
                
        except Exception as e:
            self.logger.error(f"Screen monitoring error: {e}")
    
    def _calculate_image_difference(self, img1: Image.Image, img2: Image.Image) -> float:
        """Calculate percentage difference between two images"""
        try:
            # Convert to grayscale and same size
            img1_gray = img1.convert('L').resize((100, 100))
            img2_gray = img2.convert('L').resize((100, 100))
            
            # Convert to numpy arrays
            arr1 = np.array(img1_gray)
            arr2 = np.array(img2_gray)
            
            # Calculate difference
            diff = np.abs(arr1 - arr2)
            diff_percentage = np.mean(diff) / 255.0
            
            return diff_percentage
            
        except Exception as e:
            self.logger.error(f"Image difference calculation error: {e}")
            return 0.0
    
    async def extract_table_data(self, image: Image.Image) -> List[List[str]]:
        """Extract table data from image"""
        try:
            if not OPENCV_AVAILABLE:
                return []
            
            # Convert image to grayscale
            gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
            
            # Detect horizontal and vertical lines
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
            
            horizontal_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, horizontal_kernel)
            vertical_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, vertical_kernel)
            
            # Combine lines
            table_mask = cv2.addWeighted(horizontal_lines, 0.5, vertical_lines, 0.5, 0.0)
            
            # Find contours (table cells)
            contours, _ = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Extract text from each cell
            table_data = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Extract cell image
                cell_image = image.crop((x, y, x + w, y + h))
                
                # OCR on cell
                cell_result = await self.extract_text_from_image(cell_image, "single_line")
                cell_text = cell_result.get("text", "").strip()
                
                if cell_text:
                    table_data.append([cell_text])
            
            return table_data
            
        except Exception as e:
            self.logger.error(f"Table extraction error: {e}")
            return []
