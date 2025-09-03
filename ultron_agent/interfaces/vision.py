"""
Vision interface for ULTRON Agent 3.0
Handles screen capture and optical character recognition
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Tuple, Union

try:
    from PIL import Image, ImageGrab
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

from ..config import UltronConfig
from ..errors import UltronError, ErrorCategory, ErrorSeverity

logger = logging.getLogger(__name__)


class VisionManager:
    """Manages vision capabilities including screen capture and OCR."""

    def __init__(self, config: Optional[UltronConfig] = None) -> None:
        """Initialize vision manager with configuration."""
        self.config = config or UltronConfig()
        self._check_dependencies()
        logger.info("Vision subsystem initialized")

    def _check_dependencies(self) -> None:
        """Check if required dependencies are available."""
        if not PIL_AVAILABLE:
            logger.warning("PIL/Pillow not available - screen capture disabled")
        if not PYTESSERACT_AVAILABLE:
            logger.warning("pytesseract not available - OCR disabled")

    def capture_screen(
        self,
        region: Optional[Tuple[int, int, int, int]] = None
    ) -> Image.Image:
        """
        Capture screen or a region of the screen.
        
        Args:
            region: Optional tuple of (left, top, right, bottom) for partial capture
            
        Returns:
            PIL Image object of the captured screen
        """
        if not PIL_AVAILABLE:
            raise UltronError(
                "PIL/Pillow not available for screen capture",
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.HIGH,
                recovery_suggestion="Install Pillow: pip install Pillow"
            )

        try:
            logger.info(f"Capturing screen{' region' if region else ''}...")
            if region:
                screen = ImageGrab.grab(bbox=region)
            else:
                screen = ImageGrab.grab()
            
            logger.info(f"Screen captured: {screen.size[0]}x{screen.size[1]}")
            return screen
            
        except Exception as e:
            raise UltronError(
                f"Failed to capture screen: {e}",
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.HIGH,
                recovery_suggestion="Check display permissions and screen access",
                original_error=e
            )

    def perform_ocr(
        self,
        image: Union[Image.Image, str],
        language: str = "eng"
    ) -> str:
        """
        Perform OCR on an image to extract text.
        
        Args:
            image: PIL Image object or path to image file
            language: Language for OCR (default: "eng")
            
        Returns:
            Extracted text from the image
        """
        if not PYTESSERACT_AVAILABLE:
            raise UltronError(
                "pytesseract not available for OCR",
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.HIGH,
                recovery_suggestion="Install pytesseract: pip install pytesseract"
            )

        try:
            logger.info("Performing OCR on image...")
            
            # Handle file path input
            if isinstance(image, str):
                if not PIL_AVAILABLE:
                    raise UltronError(
                        "PIL/Pillow required to load image files",
                        category=ErrorCategory.SYSTEM,
                        severity=ErrorSeverity.HIGH
                    )
                image = Image.open(image)
            
            # Configure OCR
            config = '--psm 6'  # Assume single uniform block of text
            text = pytesseract.image_to_string(image, lang=language, config=config)
            
            # Clean up the text
            text = text.strip()
            
            logger.info(f"OCR completed: extracted {len(text)} characters")
            return text
            
        except Exception as e:
            raise UltronError(
                f"OCR failed: {e}",
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.MEDIUM,
                recovery_suggestion="Check image quality and pytesseract installation",
                original_error=e
            )

    def capture_and_ocr(
        self,
        region: Optional[Tuple[int, int, int, int]] = None,
        language: str = "eng"
    ) -> str:
        """
        Capture screen and perform OCR in one operation.
        
        Args:
            region: Optional screen region to capture
            language: Language for OCR
            
        Returns:
            Text extracted from the screen capture
        """
        try:
            screen = self.capture_screen(region)
            text = self.perform_ocr(screen, language)
            logger.info("Screen capture and OCR completed successfully")
            return text
        except UltronError:
            raise  # Re-raise UltronErrors as-is
        except Exception as e:
            raise UltronError(
                f"Screen capture and OCR failed: {e}",
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.MEDIUM,
                original_error=e
            )

    def save_screenshot(
        self,
        filepath: str,
        region: Optional[Tuple[int, int, int, int]] = None,
        format: str = "PNG"
    ) -> str:
        """
        Capture and save a screenshot.
        
        Args:
            filepath: Path to save the screenshot
            region: Optional screen region to capture
            format: Image format (PNG, JPEG, etc.)
            
        Returns:
            Path to the saved screenshot
        """
        try:
            screen = self.capture_screen(region)
            screen.save(filepath, format=format)
            logger.info(f"Screenshot saved to: {filepath}")
            return filepath
        except Exception as e:
            raise UltronError(
                f"Failed to save screenshot: {e}",
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.MEDIUM,
                original_error=e
            )

    def get_screen_size(self) -> Tuple[int, int]:
        """
        Get the size of the primary screen.
        
        Returns:
            Tuple of (width, height)
        """
        try:
            # Capture a 1x1 pixel to get screen info without full capture
            test_capture = self.capture_screen((0, 0, 1, 1))
            # Use ImageGrab to get full screen size
            full_screen = ImageGrab.grab()
            return full_screen.size
        except Exception as e:
            logger.warning(f"Could not determine screen size: {e}")
            return (1920, 1080)  # Default fallback

    def get_status(self) -> Dict[str, Any]:
        """Get vision system status."""
        status: Dict[str, Any] = {
            "pil_available": PIL_AVAILABLE,
            "pytesseract_available": PYTESSERACT_AVAILABLE,
            "screen_capture_enabled": PIL_AVAILABLE,
            "ocr_enabled": PYTESSERACT_AVAILABLE
        }
        
        if PIL_AVAILABLE:
            try:
                screen_size = self.get_screen_size()
                status["screen_size"] = screen_size
            except Exception:
                pass
                
        return status


# Backward compatibility class
class Vision(VisionManager):
    """Legacy Vision class for backward compatibility."""
    
    def __init__(self):
        super().__init__()
        logger.warning("Using deprecated Vision class, use VisionManager instead")