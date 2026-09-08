"""
ULTRON Enhanced - Vision System Module
Advanced computer vision and screen analysis capabilities
"""

import os
import sys
import json
import time
import logging
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import numpy as np
from PIL import Image, ImageGrab, ImageDraw, ImageFont
import base64
import io

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logging.warning("OpenCV not available - limited vision functionality")

try:
    import torch
    TORCH_AVAILABLE = torch.cuda.is_available()
except ImportError:
    TORCH_AVAILABLE = False
    logging.warning("PyTorch not available - AI vision features disabled")

class VisionSystem:
    """Advanced computer vision system for ULTRON"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.vision_enabled = config.get('vision_enabled', True) and CV2_AVAILABLE
        self.ai_vision_enabled = config.get('ai_vision_enabled', False) and TORCH_AVAILABLE
        self.screenshot_dir = Path(config.get('screenshot_dir', './assets/screenshots'))
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        self.last_screenshot = None
        self.analysis_history = []
        
        # Initialize vision models if available
        self.vision_models = {}
        if self.ai_vision_enabled:
            self._init_ai_models()
        
        logging.info(f"Vision system initialized (CV2: {CV2_AVAILABLE}, AI: {self.ai_vision_enabled})")
    
    def _init_ai_models(self):
        """Initialize AI vision models"""
        try:
            # This would initialize actual AI models
            # For now, we'll use placeholder functionality
            self.vision_models['text_detector'] = None
            self.vision_models['object_detector'] = None
            logging.info("AI vision models initialized")
        except Exception as e:
            logging.error(f"Failed to initialize AI models: {e}")
            self.ai_vision_enabled = False
    
    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> Dict:
        """Capture screenshot with optional region"""
        try:
            # Capture screenshot
            if region:
                screenshot = ImageGrab.grab(bbox=region)
            else:
                screenshot = ImageGrab.grab()
            
            # Save screenshot
            timestamp = int(time.time())
            filename = f"screenshot_{timestamp}.png"
            filepath = self.screenshot_dir / filename
            
            screenshot.save(filepath)
            self.last_screenshot = filepath
            
            # Get basic info
            width, height = screenshot.size
            file_size = filepath.stat().st_size
            
            result = {
                "success": True,
                "message": "Screenshot captured successfully",
                "filepath": str(filepath),
                "filename": filename,
                "width": width,
                "height": height,
                "file_size": file_size,
                "timestamp": timestamp
            }
            
            logging.info(f"Screenshot captured: {filename}")
            return result
            
        except Exception as e:
            logging.error(f"Screenshot capture failed: {e}")
            return {
                "success": False,
                "message": f"Screenshot failed: {str(e)}"
            }
    
    def analyze_screen(self, analysis_type: str = "full") -> Dict:
        """Analyze current screen content"""
        try:
            # Capture current screen
            capture_result = self.capture_screen()
            if not capture_result["success"]:
                return capture_result
            
            screenshot_path = capture_result["filepath"]
            
            # Perform analysis based on type
            if analysis_type == "basic":
                result = self._basic_analysis(screenshot_path)
            elif analysis_type == "text":
                result = self._text_analysis(screenshot_path)
            elif analysis_type == "ui":
                result = self._ui_analysis(screenshot_path)
            elif analysis_type == "full":
                result = self._full_analysis(screenshot_path)
            else:
                return {
                    "success": False,
                    "message": f"Unknown analysis type: {analysis_type}"
                }
            
            # Add to history
            analysis_record = {
                "timestamp": time.time(),
                "screenshot_path": screenshot_path,
                "analysis_type": analysis_type,
                "result": result
            }
            
            self.analysis_history.append(analysis_record)
            
            # Limit history size
            if len(self.analysis_history) > 20:
                self.analysis_history.pop(0)
            
            return result
            
        except Exception as e:
            logging.error(f"Screen analysis failed: {e}")
            return {
                "success": False,
                "message": f"Analysis failed: {str(e)}"
            }
    
    def _basic_analysis(self, image_path: str) -> Dict:
        """Basic image analysis"""
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                mode = img.mode
                
                # Get color statistics
                if mode == "RGB":
                    colors = img.getcolors(maxcolors=256*256*256)
                    if colors:
                        dominant_color = max(colors, key=lambda x: x[0])[1]
                    else:
                        dominant_color = (128, 128, 128)
                else:
                    dominant_color = (128, 128, 128)
                
                # Calculate brightness
                grayscale = img.convert('L')
                brightness = np.array(grayscale).mean()
                
                return {
                    "success": True,
                    "analysis_type": "basic",
                    "image_info": {
                        "width": width,
                        "height": height,
                        "mode": mode,
                        "dominant_color": dominant_color,
                        "average_brightness": float(brightness)
                    },
                    "description": f"Image: {width}x{height} pixels, {mode} mode, brightness: {brightness:.1f}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Basic analysis failed: {str(e)}"
            }
    
    def _text_analysis(self, image_path: str) -> Dict:
        """Analyze text content in image"""
        try:
            # Placeholder for OCR functionality
            # In a real implementation, you would use libraries like:
            # - pytesseract for OCR
            # - easyocr for better accuracy
            # - paddleocr for advanced features
            
            result = {
                "success": True,
                "analysis_type": "text",
                "text_regions": [],
                "extracted_text": "",
                "confidence": 0.0
            }
            
            # Simulate text detection
            if CV2_AVAILABLE:
                img = cv2.imread(image_path)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                
                # Simple edge detection to find potential text regions
                edges = cv2.Canny(gray, 50, 150)
                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                text_regions = []
                for contour in contours:
                    x, y, w, h = cv2.boundingRect(contour)
                    # Filter by size to find potential text
                    if 10 < w < 500 and 10 < h < 100:
                        text_regions.append({
                            "x": int(x),
                            "y": int(y),
                            "width": int(w),
                            "height": int(h),
                            "confidence": 0.5
                        })
                
                result["text_regions"] = text_regions[:10]  # Limit to 10 regions
                result["extracted_text"] = f"Found {len(text_regions)} potential text regions"
                result["confidence"] = 0.5
            else:
                result["extracted_text"] = "Text analysis requires OpenCV"
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Text analysis failed: {str(e)}"
            }
    
    def _ui_analysis(self, image_path: str) -> Dict:
        """Analyze UI elements in image"""
        try:
            result = {
                "success": True,
                "analysis_type": "ui",
                "ui_elements": [],
                "layout_info": {}
            }
            
            if CV2_AVAILABLE:
                img = cv2.imread(image_path)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                height, width = gray.shape
                
                # Detect potential buttons and UI elements
                # Using simple contour detection
                edges = cv2.Canny(gray, 50, 150)
                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                ui_elements = []
                for contour in contours:
                    x, y, w, h = cv2.boundingRect(contour)
                    area = w * h
                    
                    # Classify potential UI elements by size and aspect ratio
                    aspect_ratio = w / h if h > 0 else 0
                    
                    element_type = "unknown"
                    if 100 < area < 10000:
                        if 1.5 < aspect_ratio < 4:
                            element_type = "button"
                        elif 0.8 < aspect_ratio < 1.2:
                            element_type = "icon"
                        elif aspect_ratio > 4:
                            element_type = "text_field"
                    
                    if element_type != "unknown":
                        ui_elements.append({
                            "type": element_type,
                            "x": int(x),
                            "y": int(y),
                            "width": int(w),
                            "height": int(h),
                            "area": int(area),
                            "aspect_ratio": round(aspect_ratio, 2)
                        })
                
                # Sort by area (largest first)
                ui_elements.sort(key=lambda x: x["area"], reverse=True)
                
                result["ui_elements"] = ui_elements[:20]  # Limit to 20 elements
                result["layout_info"] = {
                    "screen_width": width,
                    "screen_height": height,
                    "total_elements": len(ui_elements),
                    "buttons": len([e for e in ui_elements if e["type"] == "button"]),
                    "icons": len([e for e in ui_elements if e["type"] == "icon"]),
                    "text_fields": len([e for e in ui_elements if e["type"] == "text_field"])
                }
            else:
                result["ui_elements"] = []
                result["layout_info"] = {"error": "OpenCV not available"}
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "message": f"UI analysis failed: {str(e)}"
            }
    
    def _full_analysis(self, image_path: str) -> Dict:
        """Comprehensive image analysis"""
        try:
            # Combine all analysis types
            basic_result = self._basic_analysis(image_path)
            text_result = self._text_analysis(image_path)
            ui_result = self._ui_analysis(image_path)
            
            # Generate comprehensive description
            description_parts = []
            
            if basic_result["success"]:
                img_info = basic_result["image_info"]
                description_parts.append(
                    f"Screen resolution: {img_info['width']}x{img_info['height']}"
                )
                description_parts.append(
                    f"Average brightness: {img_info['average_brightness']:.1f}"
                )
            
            if ui_result["success"] and ui_result["ui_elements"]:
                layout = ui_result["layout_info"]
                description_parts.append(
                    f"UI elements detected: {layout.get('buttons', 0)} buttons, "
                    f"{layout.get('icons', 0)} icons, {layout.get('text_fields', 0)} text fields"
                )
            
            if text_result["success"]:
                text_regions = len(text_result.get("text_regions", []))
                if text_regions > 0:
                    description_parts.append(f"Text regions found: {text_regions}")
            
            description = ". ".join(description_parts) if description_parts else "Basic screen analysis completed"
            
            return {
                "success": True,
                "analysis_type": "full",
                "basic_analysis": basic_result,
                "text_analysis": text_result,
                "ui_analysis": ui_result,
                "comprehensive_description": description,
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Full analysis failed: {str(e)}"
            }
    
    def analyze_image_file(self, image_path: str, analysis_type: str = "full") -> Dict:
        """Analyze a specific image file"""
        try:
            if not os.path.exists(image_path):
                return {
                    "success": False,
                    "message": "Image file not found"
                }
            
            # Perform analysis based on type
            if analysis_type == "basic":
                result = self._basic_analysis(image_path)
            elif analysis_type == "text":
                result = self._text_analysis(image_path)
            elif analysis_type == "ui":
                result = self._ui_analysis(image_path)
            elif analysis_type == "full":
                result = self._full_analysis(image_path)
            else:
                return {
                    "success": False,
                    "message": f"Unknown analysis type: {analysis_type}"
                }
            
            return result
            
        except Exception as e:
            logging.error(f"Image analysis failed: {e}")
            return {
                "success": False,
                "message": f"Image analysis failed: {str(e)}"
            }
    
    def create_annotated_screenshot(self, annotations: List[Dict]) -> Dict:
        """Create annotated screenshot with overlays"""
        try:
            if not self.last_screenshot or not os.path.exists(self.last_screenshot):
                return {
                    "success": False,
                    "message": "No recent screenshot available"
                }
            
            # Load the image
            with Image.open(self.last_screenshot) as img:
                img_copy = img.copy()
                draw = ImageDraw.Draw(img_copy)
                
                # Try to load a font
                try:
                    font = ImageFont.truetype("arial.ttf", 16)
                except:
                    font = ImageFont.load_default()
                
                # Draw annotations
                for annotation in annotations:
                    ann_type = annotation.get("type", "rectangle")
                    color = annotation.get("color", "red")
                    
                    if ann_type == "rectangle":
                        x, y, w, h = annotation["x"], annotation["y"], annotation["width"], annotation["height"]
                        draw.rectangle([x, y, x + w, y + h], outline=color, width=2)
                        
                        # Add label if provided
                        if "label" in annotation:
                            draw.text((x, y - 20), annotation["label"], fill=color, font=font)
                    
                    elif ann_type == "circle":
                        x, y, r = annotation["x"], annotation["y"], annotation["radius"]
                        draw.ellipse([x - r, y - r, x + r, y + r], outline=color, width=2)
                    
                    elif ann_type == "text":
                        x, y, text = annotation["x"], annotation["y"], annotation["text"]
                        draw.text((x, y), text, fill=color, font=font)
                
                # Save annotated image
                timestamp = int(time.time())
                filename = f"annotated_{timestamp}.png"
                filepath = self.screenshot_dir / filename
                img_copy.save(filepath)
                
                return {
                    "success": True,
                    "message": "Annotated screenshot created",
                    "filepath": str(filepath),
                    "filename": filename
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Annotation failed: {str(e)}"
            }
    
    def get_analysis_history(self, limit: int = 10) -> Dict:
        """Get recent analysis history"""
        try:
            history = self.analysis_history[-limit:] if self.analysis_history else []
            
            return {
                "success": True,
                "history": history,
                "total_analyses": len(self.analysis_history)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to get history: {str(e)}"
            }
    
    def get_vision_capabilities(self) -> Dict:
        """Get information about vision system capabilities"""
        return {
            "cv2_available": CV2_AVAILABLE,
            "ai_vision_available": self.ai_vision_enabled,
            "torch_available": TORCH_AVAILABLE,
            "vision_enabled": self.vision_enabled,
            "screenshot_directory": str(self.screenshot_dir),
            "supported_analysis_types": ["basic", "text", "ui", "full"],
            "supported_formats": ["PNG", "JPEG", "BMP", "TIFF"],
            "features": {
                "screenshot_capture": True,
                "basic_analysis": True,
                "text_detection": CV2_AVAILABLE,
                "ui_element_detection": CV2_AVAILABLE,
                "annotation": True,
                "history_tracking": True,
                "ai_models": self.ai_vision_enabled
            }
        }
    
    def cleanup_old_screenshots(self, days_old: int = 7) -> Dict:
        """Clean up old screenshots"""
        try:
            cutoff_time = time.time() - (days_old * 24 * 60 * 60)
            deleted_count = 0
            
            for file_path in self.screenshot_dir.glob("*.png"):
                if file_path.stat().st_mtime < cutoff_time:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                    except:
                        pass
            
            return {
                "success": True,
                "message": f"Cleaned up {deleted_count} old screenshots",
                "deleted_count": deleted_count
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Cleanup failed: {str(e)}"
            }
    
    def export_analysis_report(self, format: str = "json") -> Dict:
        """Export analysis history as report"""
        try:
            timestamp = int(time.time())
            
            if format.lower() == "json":
                filename = f"vision_report_{timestamp}.json"
                filepath = self.screenshot_dir / filename
                
                report_data = {
                    "generated": timestamp,
                    "total_analyses": len(self.analysis_history),
                    "vision_capabilities": self.get_vision_capabilities(),
                    "analysis_history": self.analysis_history
                }
                
                with open(filepath, 'w') as f:
                    json.dump(report_data, f, indent=2)
                
                return {
                    "success": True,
                    "message": "Report exported successfully",
                    "filepath": str(filepath),
                    "format": "json"
                }
            else:
                return {
                    "success": False,
                    "message": f"Unsupported format: {format}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Export failed: {str(e)}"
            }

class VisionUtils:
    """Utility functions for vision processing"""
    
    @staticmethod
    def image_to_base64(image_path: str) -> str:
        """Convert image to base64 string"""
        try:
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
        except Exception as e:
            logging.error(f"Image to base64 conversion failed: {e}")
            return ""
    
    @staticmethod
    def base64_to_image(base64_string: str, output_path: str) -> bool:
        """Convert base64 string to image file"""
        try:
            image_data = base64.b64decode(base64_string)
            with open(output_path, "wb") as img_file:
                img_file.write(image_data)
            return True
        except Exception as e:
            logging.error(f"Base64 to image conversion failed: {e}")
            return False
    
    @staticmethod
    def resize_image(input_path: str, output_path: str, max_size: Tuple[int, int]) -> bool:
        """Resize image while maintaining aspect ratio"""
        try:
            with Image.open(input_path) as img:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                img.save(output_path)
            return True
        except Exception as e:
            logging.error(f"Image resize failed: {e}")
            return False
    
    @staticmethod
    def get_image_info(image_path: str) -> Dict:
        """Get basic image information"""
        try:
            with Image.open(image_path) as img:
                return {
                    "width": img.width,
                    "height": img.height,
                    "mode": img.mode,
                    "format": img.format,
                    "size_bytes": os.path.getsize(image_path)
                }
        except Exception as e:
            logging.error(f"Get image info failed: {e}")
            return {}
