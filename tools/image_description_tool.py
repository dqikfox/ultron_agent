"""
Image Description Tool for ULTRON Agent
Provides detailed visual analysis of images using AI vision models
"""

import os
from PIL import Image
from utils.ultron_logger import log_info, log_error
from utils.ollama_vision import analyze_image_with_ollama, DEFAULT_VISION_MODELS
from .tool_interface import ToolInterface

class ImageDescriptionTool(ToolInterface):
    """Tool for detailed image description and analysis"""
    
    @property
    def name(self) -> str:
        return "Image Description Tool"
    
    @property
    def description(self) -> str:
        return "Provides detailed visual analysis and description of images"
    
    def match(self, command: str) -> bool:
        return any(keyword in command.lower() for keyword in [
            "describe image", "analyze image", "image description", 
            "visual analysis", "what's in image", "image details"
        ])
    
    def execute(self, command: str, **kwargs) -> str:
        try:
            # Extract image path from command or kwargs
            image_path = kwargs.get('image_path')
            if not image_path and 'image' in command:
                # Try to extract path from command
                parts = command.split()
                for part in parts:
                    if part.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                        image_path = part
                        break
            
            if not image_path:
                return "Please provide an image path. Usage: describe image [path]"
            
            if not os.path.exists(image_path):
                return f"Image file not found: {image_path}"
            
            # Analyze image
            description = self._analyze_image(image_path)
            
            log_info("image_description", f"Analyzed image: {image_path}")
            return description
            
        except Exception as e:
            log_error("image_description", f"Image analysis failed: {e}")
            return f"Image analysis error: {str(e)}"
    
    def _analyze_image(self, image_path: str) -> str:
        """Analyze image with AI vision model"""
        try:
            # Try Ollama vision models first
            description = self._analyze_with_ollama(image_path)
            if description:
                return description
            
            # Fallback to basic analysis
            return self._basic_image_analysis(image_path)
            
        except Exception as e:
            log_error("image_description", f"Vision analysis failed: {e}")
            return f"Vision analysis failed: {str(e)}"
    
    _ANALYSIS_PROMPT = """Analyze this image in detail. Provide a comprehensive description covering:

Visual Details:
- Main subject and composition
- Colors, lighting, and atmosphere
- Textures, materials, and surfaces
- Architectural or design elements
- Facial expressions or body language (if applicable)

Technical Aspects:
- Art style or photographic technique
- Mood and emotional tone
- Perspective and framing
- Notable visual effects or elements

Context:
- Setting or environment
- Time period or era (if identifiable)
- Cultural or thematic elements
- Symbolic or metaphorical content

Be specific, detailed, and descriptive. Focus on what you actually see in the image."""

    def _analyze_with_ollama(self, image_path: str) -> str:
        """Analyze image with Ollama vision models."""
        return analyze_image_with_ollama(
            image_path,
            self._ANALYSIS_PROMPT,
            models=DEFAULT_VISION_MODELS,
            timeout=60,
            log_source="image_description",
        )
    
    def _basic_image_analysis(self, image_path: str) -> str:
        """Basic image analysis when AI vision is unavailable"""
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                mode = img.mode
                format_type = img.format
            
            file_size = os.path.getsize(image_path)
            filename = os.path.basename(image_path)
            
            return f"""Basic Image Analysis:

File Information:
- Filename: {filename}
- Dimensions: {width}x{height} pixels
- Color Mode: {mode}
- Format: {format_type}
- File Size: {file_size:,} bytes

Technical Details:
- Aspect Ratio: {width/height:.2f}:1
- Megapixels: {(width * height) / 1000000:.1f}MP
- Location: {image_path}

Note: AI vision analysis was not available. This is a basic technical analysis of the image file.
For detailed visual description, ensure Ollama vision models are running."""
            
        except Exception as e:
            return f"Basic image analysis failed: {str(e)}"
    
    def analyze_screenshot(self, screenshot_path: str) -> str:
        """Analyze a screenshot image"""
        return self._analyze_image(screenshot_path)
    
    @classmethod
    def schema(cls):
        return {
            "name": "Image Description Tool",
            "description": "Provides detailed visual analysis and description of images",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Image description command"
                    },
                    "image_path": {
                        "type": "string",
                        "description": "Path to image file"
                    }
                },
                "required": ["command"]
            }
        }