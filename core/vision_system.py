"""
ULTRON Vision System
===================

Advanced computer vision capabilities including screen capture, OCR,
image analysis, and AI-powered visual recognition.
"""

import os
import sys
import cv2
import numpy as np
import threading
import logging
import time
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime
import base64
import io

# Image processing imports
try:
    from PIL import Image, ImageDraw, ImageFont, ImageEnhance
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("OCR capabilities limited. Install with: pip install pillow pytesseract")

# Screen capture
try:
    import pyautogui
    import mss
    SCREEN_CAPTURE_AVAILABLE = True
except ImportError:
    SCREEN_CAPTURE_AVAILABLE = False
    print("Screen capture not available. Install with: pip install pyautogui mss")

# AI Vision integration
try:
    import openai
    AI_VISION_AVAILABLE = True
except ImportError:
    AI_VISION_AVAILABLE = False


class VisionSystem:
    """Advanced computer vision and screen analysis system."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize vision system with configuration."""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Screen capture setup
        if SCREEN_CAPTURE_AVAILABLE:
            self.sct = mss.mss()
            pyautogui.FAILSAFE = True
        
        # OCR configuration
        if OCR_AVAILABLE:
            self.tesseract_config = self.config.get('tesseract_config', '--psm 6')
        
        # AI vision setup
        self.ai_client = None
        if AI_VISION_AVAILABLE and self.config.get('openai_api_key'):
            openai.api_key = self.config.get('openai_api_key')
            self.ai_client = openai
        
        # Image storage
        self.screenshots_dir = Path("screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
        
        # Performance monitoring
        self.capture_stats = {
            'total_captures': 0,
            'total_ocr_operations': 0,
            'average_capture_time': 0,
            'last_capture_time': None
        }
        
        self.logger.info("Vision system initialized")
    
    # ================================
    # Screen Capture
    # ================================
    
    def capture_screen(self, region: Tuple[int, int, int, int] = None, 
                      save_file: str = None) -> Optional[np.ndarray]:
        """Capture full screen or region."""
        if not SCREEN_CAPTURE_AVAILABLE:
            self.logger.error("Screen capture not available")
            return None
        
        start_time = time.time()
        
        try:
            if region:
                # Capture specific region (x, y, width, height)
                x, y, width, height = region
                screenshot = self.sct.grab({'top': y, 'left': x, 'width': width, 'height': height})
                img_array = np.array(screenshot)
            else:
                # Capture full screen
                screenshot = pyautogui.screenshot()
                img_array = np.array(screenshot)
            
            # Convert RGB to BGR for OpenCV
            if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            elif len(img_array.shape) == 3 and img_array.shape[2] == 4:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
            
            # Save if filename provided
            if save_file:
                save_path = self.screenshots_dir / save_file
                cv2.imwrite(str(save_path), img_array)
                self.logger.info(f"Screenshot saved: {save_path}")
            
            # Update stats
            capture_time = time.time() - start_time
            self.capture_stats['total_captures'] += 1
            self.capture_stats['last_capture_time'] = capture_time
            self.capture_stats['average_capture_time'] = (
                (self.capture_stats['average_capture_time'] * (self.capture_stats['total_captures'] - 1) + capture_time)
                / self.capture_stats['total_captures']
            )
            
            return img_array
            
        except Exception as e:
            self.logger.error(f"Screen capture error: {e}")
            return None
    
    def capture_window(self, window_title: str, save_file: str = None) -> Optional[np.ndarray]:
        """Capture specific window by title."""
        try:
            # Find window using system automation
            from .system_automation import SystemAutomation
            automation = SystemAutomation()
            window = automation.find_window(window_title)
            
            if not window:
                self.logger.warning(f"Window not found: {window_title}")
                return None
            
            # Capture window region
            return self.capture_screen(
                region=(window['x'], window['y'], window['width'], window['height']),
                save_file=save_file
            )
            
        except Exception as e:
            self.logger.error(f"Window capture error: {e}")
            return None
    
    def continuous_capture(self, interval: float = 1.0, duration: int = 60,
                          save_all: bool = False) -> List[np.ndarray]:
        """Capture screen continuously for analysis."""
        captures = []
        start_time = time.time()
        
        try:
            while time.time() - start_time < duration:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                save_file = f"continuous_{timestamp}.png" if save_all else None
                
                capture = self.capture_screen(save_file=save_file)
                if capture is not None:
                    captures.append(capture)
                
                time.sleep(interval)
            
            self.logger.info(f"Continuous capture completed: {len(captures)} frames")
            return captures
            
        except Exception as e:
            self.logger.error(f"Continuous capture error: {e}")
            return captures
    
    # ================================
    # OCR and Text Extraction
    # ================================
    
    def extract_text(self, image: Union[np.ndarray, str], region: Tuple[int, int, int, int] = None,
                    language: str = 'eng') -> Optional[str]:
        """Extract text from image using OCR."""
        if not OCR_AVAILABLE:
            self.logger.error("OCR not available")
            return None
        
        try:
            # Load image if path provided
            if isinstance(image, str):
                if os.path.exists(image):
                    image = cv2.imread(image)
                else:
                    self.logger.error(f"Image file not found: {image}")
                    return None
            
            # Extract region if specified
            if region:
                x, y, w, h = region
                image = image[y:y+h, x:x+w]
            
            # Preprocess image for better OCR
            processed_image = self._preprocess_for_ocr(image)
            
            # Convert to PIL Image for Tesseract
            pil_image = Image.fromarray(cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB))
            
            # Extract text
            text = pytesseract.image_to_string(
                pil_image,
                lang=language,
                config=self.tesseract_config
            )
            
            # Clean text
            text = text.strip()
            if text:
                self.logger.info(f"OCR extracted {len(text)} characters")
                self.capture_stats['total_ocr_operations'] += 1
            
            return text if text else None
            
        except Exception as e:
            self.logger.error(f"OCR error: {e}")
            return None
    
    def extract_text_from_screen(self, region: Tuple[int, int, int, int] = None,
                               language: str = 'eng') -> Optional[str]:
        """Extract text directly from screen."""
        screenshot = self.capture_screen(region=region)
        if screenshot is None:
            return None
        
        return self.extract_text(screenshot, language=language)
    
    def find_text_locations(self, image: Union[np.ndarray, str], target_text: str,
                          confidence: float = 0.8) -> List[Dict[str, Any]]:
        """Find locations of specific text in image."""
        if not OCR_AVAILABLE:
            return []
        
        try:
            # Load image if path provided
            if isinstance(image, str):
                image = cv2.imread(image)
            
            # Get text data with bounding boxes
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            data = pytesseract.image_to_data(pil_image, output_type=pytesseract.Output.DICT)
            
            locations = []
            for i, text in enumerate(data['text']):
                if target_text.lower() in text.lower() and int(data['conf'][i]) > confidence * 100:
                    locations.append({
                        'text': text,
                        'confidence': int(data['conf'][i]) / 100.0,
                        'x': data['left'][i],
                        'y': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i],
                        'center_x': data['left'][i] + data['width'][i] // 2,
                        'center_y': data['top'][i] + data['height'][i] // 2
                    })
            
            return locations
            
        except Exception as e:
            self.logger.error(f"Text location search error: {e}")
            return []
    
    def _preprocess_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Apply threshold to get binary image
            _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Morphological operations to clean up
            kernel = np.ones((1, 1), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            # Convert back to BGR for consistency
            return cv2.cvtColor(cleaned, cv2.COLOR_GRAY2BGR)
            
        except Exception as e:
            self.logger.error(f"Image preprocessing error: {e}")
            return image
    
    # ================================
    # Image Analysis
    # ================================
    
    def find_image_on_screen(self, template_path: str, confidence: float = 0.8,
                           region: Tuple[int, int, int, int] = None) -> Optional[Dict[str, Any]]:
        """Find template image on screen using template matching."""
        try:
            # Capture screen
            screenshot = self.capture_screen(region=region)
            if screenshot is None:
                return None
            
            # Load template
            if not os.path.exists(template_path):
                self.logger.error(f"Template image not found: {template_path}")
                return None
            
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            if template is None:
                return None
            
            # Template matching
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= confidence)
            
            if len(locations[0]) > 0:
                # Get best match
                max_val = np.max(result)
                max_loc = np.unravel_index(np.argmax(result), result.shape)
                
                h, w = template.shape[:2]
                x, y = max_loc[1], max_loc[0]
                
                if region:
                    x += region[0]
                    y += region[1]
                
                return {
                    'found': True,
                    'confidence': float(max_val),
                    'x': x,
                    'y': y,
                    'width': w,
                    'height': h,
                    'center_x': x + w // 2,
                    'center_y': y + h // 2
                }
            
            return {'found': False}
            
        except Exception as e:
            self.logger.error(f"Image search error: {e}")
            return {'found': False, 'error': str(e)}
    
    def analyze_colors(self, image: Union[np.ndarray, str], 
                      region: Tuple[int, int, int, int] = None) -> Dict[str, Any]:
        """Analyze color distribution in image."""
        try:
            # Load image if path provided
            if isinstance(image, str):
                image = cv2.imread(image)
            
            # Extract region if specified
            if region:
                x, y, w, h = region
                image = image[y:y+h, x:x+w]
            
            # Convert to RGB for color analysis
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Calculate color statistics
            mean_color = np.mean(rgb_image.reshape(-1, 3), axis=0)
            dominant_colors = self._get_dominant_colors(rgb_image, k=5)
            
            # Calculate brightness
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray)
            
            return {
                'mean_color': mean_color.tolist(),
                'dominant_colors': dominant_colors,
                'brightness': float(brightness),
                'width': image.shape[1],
                'height': image.shape[0]
            }
            
        except Exception as e:
            self.logger.error(f"Color analysis error: {e}")
            return {}
    
    def _get_dominant_colors(self, image: np.ndarray, k: int = 5) -> List[List[int]]:
        """Get dominant colors using k-means clustering."""
        try:
            # Reshape image to be a list of pixels
            pixels = image.reshape(-1, 3).astype(np.float32)
            
            # Apply k-means clustering
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
            _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # Convert centers to int and return
            return centers.astype(int).tolist()
            
        except Exception as e:
            self.logger.error(f"Dominant color analysis error: {e}")
            return []
    
    # ================================
    # AI Vision Integration
    # ================================
    
    def analyze_with_ai(self, image: Union[np.ndarray, str], prompt: str = "What do you see in this image?",
                       max_tokens: int = 500) -> Optional[str]:
        """Analyze image using AI vision models."""
        if not self.ai_client:
            self.logger.error("AI vision not available")
            return None
        
        try:
            # Convert image to base64
            if isinstance(image, str):
                with open(image, 'rb') as img_file:
                    image_data = base64.b64encode(img_file.read()).decode()
            else:
                # Convert numpy array to image
                is_success, buffer = cv2.imencode(".jpg", image)
                if not is_success:
                    return None
                image_data = base64.b64encode(buffer).decode()
            
            # Make API request to GPT-4 Vision
            response = self.ai_client.ChatCompletion.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"AI vision analysis error: {e}")
            return None
    
    def detect_ui_elements(self, image: Union[np.ndarray, str]) -> List[Dict[str, Any]]:
        """Detect UI elements like buttons, text fields, etc."""
        try:
            # Load image if path provided
            if isinstance(image, str):
                image = cv2.imread(image)
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect edges
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            elements = []
            for contour in contours:
                # Filter by area
                area = cv2.contourArea(contour)
                if area < 100:  # Skip very small elements
                    continue
                
                # Get bounding box
                x, y, w, h = cv2.boundingRect(contour)
                
                # Classify element type based on dimensions
                aspect_ratio = w / h
                element_type = "unknown"
                
                if aspect_ratio > 3 and h < 50:
                    element_type = "text_field"
                elif 0.5 < aspect_ratio < 2 and area > 1000:
                    element_type = "button"
                elif aspect_ratio > 10:
                    element_type = "line"
                
                elements.append({
                    'type': element_type,
                    'x': x,
                    'y': y,
                    'width': w,
                    'height': h,
                    'area': area,
                    'aspect_ratio': aspect_ratio,
                    'center_x': x + w // 2,
                    'center_y': y + h // 2
                })
            
            return elements
            
        except Exception as e:
            self.logger.error(f"UI element detection error: {e}")
            return []
    
    # ================================
    # Utility Functions
    # ================================
    
    def save_annotated_image(self, image: np.ndarray, annotations: List[Dict[str, Any]],
                           filename: str) -> str:
        """Save image with annotations overlaid."""
        try:
            annotated_image = image.copy()
            
            for annotation in annotations:
                if 'x' in annotation and 'y' in annotation:
                    x, y = annotation['x'], annotation['y']
                    w, h = annotation.get('width', 10), annotation.get('height', 10)
                    
                    # Draw rectangle
                    cv2.rectangle(annotated_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    
                    # Add label
                    label = annotation.get('type', 'detected')
                    cv2.putText(annotated_image, label, (x, y - 10),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Save annotated image
            save_path = self.screenshots_dir / filename
            cv2.imwrite(str(save_path), annotated_image)
            self.logger.info(f"Annotated image saved: {save_path}")
            
            return str(save_path)
            
        except Exception as e:
            self.logger.error(f"Image annotation error: {e}")
            return ""
    
    def get_status(self) -> Dict[str, Any]:
        """Get vision system status."""
        return {
            'screen_capture_available': SCREEN_CAPTURE_AVAILABLE,
            'ocr_available': OCR_AVAILABLE,
            'ai_vision_available': self.ai_client is not None,
            'total_captures': self.capture_stats['total_captures'],
            'total_ocr_operations': self.capture_stats['total_ocr_operations'],
            'average_capture_time': self.capture_stats['average_capture_time'],
            'last_capture_time': self.capture_stats['last_capture_time']
        }


def test_vision_system():
    """Test vision system functionality."""
    vision = VisionSystem()
    
    print("Testing vision system...")
    
    # Test screen capture
    screenshot = vision.capture_screen(save_file="test_screenshot.png")
    if screenshot is not None:
        print(f"Screenshot captured: {screenshot.shape}")
        
        # Test OCR
        text = vision.extract_text(screenshot)
        if text:
            print(f"OCR text extracted: {len(text)} characters")
            print(f"Sample text: {text[:100]}...")
        
        # Test color analysis
        colors = vision.analyze_colors(screenshot)
        print(f"Color analysis: {colors}")
        
        # Test UI element detection
        elements = vision.detect_ui_elements(screenshot)
        print(f"UI elements detected: {len(elements)}")
    
    print("Vision system test complete")
    return vision.get_status()


if __name__ == "__main__":
    # Run vision system test
    test_vision_system()