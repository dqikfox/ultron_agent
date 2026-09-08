"""
Vision System for UltronSysAgent
Handles camera input, image processing, and computer vision tasks
"""

import asyncio
import logging
import cv2
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import threading
import queue
from datetime import datetime

try:
    import pytesseract
    from PIL import Image
    VISION_DEPS_AVAILABLE = True
except ImportError:
    VISION_DEPS_AVAILABLE = False
    print("⚠️  Vision dependencies not available")

from ...core.event_bus import EventBus, EventTypes

class VisionSystem:
    """Computer vision and camera processing module"""
    
    def __init__(self, config, event_bus: EventBus):
        self.config = config
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)
        
        # Camera settings
        self.camera_enabled = config.get('hardware.camera_enabled', False)
        self.camera_device = config.get('hardware.camera_device', 0)
        
        # Camera state
        self.camera = None
        self.is_capturing = False
        self.capture_thread = None
        self.frame_queue = queue.Queue(maxsize=10)
        
        # Processing capabilities
        self.ocr_enabled = VISION_DEPS_AVAILABLE
        self.face_detection_enabled = VISION_DEPS_AVAILABLE
        
        # Frame processing
        self.last_frame = None
        self.frame_count = 0
        
        # Setup event handlers
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """Setup event bus handlers"""
        pass  # Vision system is primarily reactive
    
    async def start(self):
        """Start the vision system"""
        self.logger.info("👁️ Starting Vision System...")
        
        if self.camera_enabled and VISION_DEPS_AVAILABLE:
            await self.start_camera()
        
        await self.event_bus.publish(EventTypes.MODULE_STARTED, 
                                    {"module": "vision_system"}, 
                                    source="vision_system")
    
    async def stop(self):
        """Stop the vision system"""
        self.logger.info("👁️ Stopping Vision System...")
        
        await self.stop_camera()
        
        await self.event_bus.publish(EventTypes.MODULE_STOPPED, 
                                    {"module": "vision_system"}, 
                                    source="vision_system")
    
    async def start_camera(self):
        """Start camera capture"""
        if not VISION_DEPS_AVAILABLE:
            self.logger.warning("Camera cannot start - vision dependencies missing")
            return
        
        try:
            # Initialize camera
            self.camera = cv2.VideoCapture(self.camera_device)
            
            if not self.camera.isOpened():
                raise Exception(f"Cannot open camera device {self.camera_device}")
            
            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            # Start capture thread
            self.is_capturing = True
            self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.capture_thread.start()
            
            self.logger.info("📷 Camera started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start camera: {e}")
            self.camera_enabled = False
    
    async def stop_camera(self):
        """Stop camera capture"""
        if not self.is_capturing:
            return
        
        try:
            self.is_capturing = False
            
            if self.capture_thread and self.capture_thread.is_alive():
                self.capture_thread.join(timeout=2.0)
            
            if self.camera:
                self.camera.release()
                self.camera = None
            
            self.logger.info("📷 Camera stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping camera: {e}")
    
    def _capture_loop(self):
        """Main camera capture loop"""
        try:
            while self.is_capturing and self.camera:
                ret, frame = self.camera.read()
                
                if not ret:
                    self.logger.warning("Failed to read camera frame")
                    continue
                
                # Store latest frame
                self.last_frame = frame.copy()
                self.frame_count += 1
                
                # Add to processing queue if not full
                try:
                    self.frame_queue.put_nowait(frame)
                except queue.Full:
                    # Skip frame if queue is full
                    try:
                        self.frame_queue.get_nowait()  # Remove oldest frame
                        self.frame_queue.put_nowait(frame)  # Add new frame
                    except queue.Empty:
                        pass
                
                # Process frame periodically
                if self.frame_count % 30 == 0:  # Process every 30 frames (~1 second at 30fps)
                    asyncio.run_coroutine_threadsafe(
                        self._process_frame_async(frame),
                        asyncio.get_event_loop()
                    )
                
        except Exception as e:
            self.logger.error(f"Error in camera capture loop: {e}")
    
    async def _process_frame_async(self, frame):
        """Process camera frame asynchronously"""
        try:
            # Basic frame analysis
            analysis = await self.analyze_frame(frame)
            
            if analysis.get('interesting', False):
                # Publish interesting frame event
                await self.event_bus.publish(EventTypes.SYSTEM_RESPONSE, 
                                           {
                                               "type": "vision_analysis",
                                               "analysis": analysis
                                           }, 
                                           source="vision_system")
                
        except Exception as e:
            self.logger.error(f"Error processing frame: {e}")
    
    async def capture_image(self) -> Optional[np.ndarray]:
        """Capture a single image from camera"""
        if not self.camera or not self.is_capturing:
            return None
        
        try:
            # Get latest frame
            if self.last_frame is not None:
                return self.last_frame.copy()
            
            # Fallback: capture directly
            ret, frame = self.camera.read()
            if ret:
                return frame
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error capturing image: {e}")
            return None
    
    async def analyze_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """Analyze a camera frame for interesting content"""
        try:
            analysis = {
                'timestamp': datetime.now().isoformat(),
                'frame_shape': frame.shape,
                'interesting': False,
                'features': []
            }
            
            # Basic motion detection (if we had previous frame)
            # This is a simplified implementation
            
            # Face detection
            if self.face_detection_enabled:
                faces = await self.detect_faces(frame)
                if faces:
                    analysis['faces'] = len(faces)
                    analysis['interesting'] = True
                    analysis['features'].append('faces_detected')
            
            # Edge detection for general activity
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.mean(edges) / 255.0
            
            analysis['edge_density'] = edge_density
            
            # Consider frame interesting if high edge density
            if edge_density > 0.1:
                analysis['interesting'] = True
                analysis['features'].append('high_activity')
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing frame: {e}")
            return {'error': str(e)}
    
    async def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect faces in frame"""
        try:
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Load face cascade classifier
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Detect faces
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            return [(x, y, w, h) for (x, y, w, h) in faces]
            
        except Exception as e:
            self.logger.error(f"Error detecting faces: {e}")
            return []
    
    async def perform_ocr(self, frame: np.ndarray) -> str:
        """Perform OCR on frame to extract text"""
        if not self.ocr_enabled:
            return "OCR not available"
        
        try:
            # Convert frame to PIL Image
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            
            # Perform OCR
            text = pytesseract.image_to_string(pil_image)
            
            return text.strip() if text.strip() else "No text detected"
            
        except Exception as e:
            self.logger.error(f"Error performing OCR: {e}")
            return f"OCR error: {e}"
    
    async def process_image_file(self, image_path: str) -> Dict[str, Any]:
        """Process an image file for analysis"""
        try:
            # Load image
            frame = cv2.imread(image_path)
            
            if frame is None:
                raise Exception(f"Could not load image: {image_path}")
            
            # Analyze the image
            analysis = await self.analyze_frame(frame)
            
            # Perform OCR if requested
            if self.ocr_enabled:
                ocr_text = await self.perform_ocr(frame)
                analysis['ocr_text'] = ocr_text
            
            # Get image info
            height, width, channels = frame.shape
            analysis['image_info'] = {
                'width': width,
                'height': height,
                'channels': channels,
                'path': image_path
            }
            
            self.logger.info(f"✅ Processed image: {image_path}")
            
            return {
                'success': True,
                'analysis': analysis
            }
            
        except Exception as e:
            self.logger.error(f"Error processing image {image_path}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def take_screenshot(self) -> Optional[str]:
        """Take a screenshot of the current screen"""
        try:
            import pyautogui
            
            # Take screenshot
            screenshot = pyautogui.screenshot()
            
            # Save to temporary file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"data/screenshots/screenshot_{timestamp}.png"
            
            # Create directory if needed
            import os
            os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
            
            # Save screenshot
            screenshot.save(screenshot_path)
            
            self.logger.info(f"📸 Screenshot saved: {screenshot_path}")
            
            return screenshot_path
            
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {e}")
            return None
    
    async def find_objects_on_screen(self, template_path: str) -> List[Tuple[int, int]]:
        """Find objects on screen using template matching"""
        try:
            # Take screenshot
            screenshot_path = await self.take_screenshot()
            if not screenshot_path:
                return []
            
            # Load screenshot and template
            screenshot = cv2.imread(screenshot_path)
            template = cv2.imread(template_path)
            
            if screenshot is None or template is None:
                return []
            
            # Convert to grayscale
            screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            
            # Template matching
            result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
            
            # Find locations with high correlation
            threshold = 0.8
            locations = np.where(result >= threshold)
            
            # Convert to list of coordinates
            matches = []
            for pt in zip(*locations[::-1]):
                matches.append((pt[0], pt[1]))
            
            return matches
            
        except Exception as e:
            self.logger.error(f"Error finding objects on screen: {e}")
            return []
    
    def get_camera_status(self) -> Dict[str, Any]:
        """Get camera status information"""
        return {
            'enabled': self.camera_enabled,
            'capturing': self.is_capturing,
            'device': self.camera_device,
            'frame_count': self.frame_count,
            'dependencies_available': VISION_DEPS_AVAILABLE
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get vision system status"""
        return {
            'camera': self.get_camera_status(),
            'ocr_enabled': self.ocr_enabled,
            'face_detection_enabled': self.face_detection_enabled,
            'last_frame_available': self.last_frame is not None
        }
