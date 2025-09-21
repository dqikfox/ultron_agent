#!/usr/bin/env python3
"""
Vision Tool - Multimodal Image Understanding with CLIP + Llama 3
Provides image analysis, description, and understanding capabilities
"""

import os
import logging
from typing import Dict, Optional, Any
from io import BytesIO

# Import vision dependencies
try:
    from transformers import CLIPProcessor, CLIPModel
    from PIL import Image
    import torch
    import requests
    VISION_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Vision dependencies not available: {e}")
    VISION_AVAILABLE = False

from tools.base import Tool

logger = logging.getLogger(__name__)


class VisionTool(Tool):
    """Multimodal vision tool with CLIP and Llama 3 integration"""

    name = "vision"
    description = ("Analyze images, describe scenes, and understand "
                   "visual content using CLIP and Llama 3")
    parameters = {
        "action": {
            "type": "string",
            "description": ("Action to perform: 'describe', 'analyze', "
                           "'classify', 'search', 'compare'"),
            "enum": ["describe", "analyze", "classify", "search", "compare"]
        },
        "image_path": {
            "type": "string",
            "description": "Path to the image file or URL"
        },
        "query": {
            "type": "string",
            "description": ("Optional query for analysis "
                           "(e.g., 'what color is the car?')")
        },
        "model": {
            "type": "string",
            "description": "Model to use for analysis",
            "default": "clip",
            "enum": ["clip", "llama3"]
        }
    }

    def __init__(self, ultron_config=None):
        super().__init__()
        self.ultron_config = ultron_config
        self.clip_model = None
        self.clip_processor = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._initialize_clip()

    def _initialize_clip(self):
        """Initialize CLIP model and processor"""
        if not VISION_AVAILABLE:
            logger.error("Vision dependencies not available")
            return

        try:
            logger.info("Initializing CLIP model...")

            # Get model configuration from centralized config
            model_name = "openai/clip-vit-base-patch32"
            if self.ultron_config:
                # Allow config override for different CLIP models
                vision_config = self.ultron_config.get("vision", {})
                config_model = vision_config.get("clip_model")
                if config_model:
                    model_name = config_model

            # Try to load CLIP model with error handling for torch.load issues
            try:
                self.clip_model = CLIPModel.from_pretrained(model_name)
                self.clip_processor = CLIPProcessor.from_pretrained(model_name)
                self.clip_model.to(self.device)
                self.clip_model.eval()
                logger.info("CLIP model initialized successfully")
            except Exception as clip_error:
                logger.warning(f"CLIP model loading failed: {clip_error}")
                logger.info("Vision tool will operate without CLIP model")
                self.clip_model = None
                self.clip_processor = None

        except Exception as e:
            logger.error(f"Failed to initialize CLIP model: {e}")
            self.clip_model = None
            self.clip_processor = None

    def match(self, command: str) -> bool:
        """Check if command matches vision-related queries"""
        vision_keywords = [
            "analyze image", "describe image", "what do you see",
            "image analysis", "vision", "picture", "photo",
            "look at", "examine image", "image classification",
            "scene description", "visual analysis"
        ]

        command_lower = command.lower()
        return any(keyword in command_lower for keyword in vision_keywords)

    def execute(self, command: str) -> str:
        """Execute vision analysis command"""
        if not VISION_AVAILABLE:
            msg = ("Vision capabilities not available. Please install "
                   "required dependencies: transformers, torch, "
                   "torchvision, Pillow")
            return msg

        try:
            # Parse command to extract parameters
            params = self._parse_command(command)

            if not params.get("image_path"):
                return "Please provide an image path or URL to analyze"

            action = params.get("action", "describe")
            image_path = params["image_path"]
            query = params.get("query", "")

            # Load and process image
            image = self._load_image(image_path)
            if image is None:
                return f"Could not load image from: {image_path}"

            # Perform requested action
            if action == "describe":
                return self._describe_image(image, query)
            elif action == "analyze":
                return self._analyze_image(image, query)
            elif action == "classify":
                return self._classify_image(image)
            elif action == "search":
                return self._search_similar(image, query)
            elif action == "compare":
                return self._compare_images(image, query)
            else:
                msg = (f"Unknown action: {action}. Supported actions: "
                       "describe, analyze, classify, search, compare")
                return msg

        except Exception as e:
            logger.error(f"Vision tool execution error: {e}")
            return f"Error analyzing image: {str(e)}"

    def _parse_command(self, command: str) -> Dict[str, Any]:
        """Parse natural language command into structured parameters"""
        params = {}
        command_lower = command.lower()

        # Extract image path/URL
        if "http" in command:
            # Extract URL
            import re
            url_match = re.search(r'https?://[^\s]+', command)
            if url_match:
                params["image_path"] = url_match.group(0)
        else:
            # Look for file path
            words = command.split()
            for word in words:
                extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
                if os.path.exists(word) or word.endswith(extensions):
                    params["image_path"] = word
                    break

        # Determine action
        if "describe" in command_lower or "what do you see" in command_lower:
            params["action"] = "describe"
        elif "analyze" in command_lower or "examine" in command_lower:
            params["action"] = "analyze"
        elif "classify" in command_lower or "what is this" in command_lower:
            params["action"] = "classify"
        elif "search" in command_lower or "find similar" in command_lower:
            params["action"] = "search"
        elif "compare" in command_lower:
            params["action"] = "compare"
        else:
            params["action"] = "describe"

        # Extract query
        indicators = ["about", "regarding", "concerning", "with", "showing"]
        for indicator in indicators:
            if indicator in command_lower:
                idx = command_lower.find(indicator)
                params["query"] = command[idx + len(indicator):].strip()
                break

        return params

    def _load_image(self, image_path: str) -> Optional[Image.Image]:
        """Load image from file path or URL"""
        try:
            # Get timeout from config or use default
            timeout = 10
            if self.ultron_config:
                vision_config = self.ultron_config.get("vision", {})
                config_timeout = vision_config.get("request_timeout", 10)
                timeout = config_timeout

            if image_path.startswith("http"):
                # Load from URL
                response = requests.get(image_path, timeout=timeout)
                response.raise_for_status()
                image = Image.open(BytesIO(response.content))
            else:
                # Load from file
                if not os.path.exists(image_path):
                    return None
                image = Image.open(image_path)

            # Convert to RGB if necessary
            if image.mode != "RGB":
                image = image.convert("RGB")

            return image
        except Exception as e:
            logger.error(f"Error loading image {image_path}: {e}")
            return None

    def _describe_image(self, image: Image.Image, query: str = "") -> str:
        """Generate natural language description of image"""
        if not self.clip_model or not self.clip_processor:
            return ("CLIP model not available for image description. "
                    "This may be due to PyTorch version compatibility issues. "
                    "Please check the logs for more details.")

        try:
            # Use CLIP to understand image content
            text_prompts = ["a photo of", "an image of", "a picture of",
                            "a scene of"]
            inputs = self.clip_processor(
                text=text_prompts,
                images=image,
                return_tensors="pt",
                padding=True
            ).to(self.device)

            with torch.no_grad():
                outputs = self.clip_model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)

            # Get most likely description
            best_idx = torch.argmax(probs[0]).item()
            desc_list = ["a photo of", "an image of", "a picture of",
                         "a scene of"]
            base_description = desc_list[best_idx]

            # Use additional text prompts for more detailed description
            detail_prompts = [
                "people", "animals", "buildings", "nature", "food",
                "vehicles", "technology", "art", "sports", "indoor",
                "outdoor", "daytime", "nighttime"
            ]

            detail_inputs = self.clip_processor(
                text=detail_prompts,
                images=image,
                return_tensors="pt",
                padding=True
            ).to(self.device)

            with torch.no_grad():
                detail_outputs = self.clip_model(**detail_inputs)
                detail_probs = detail_outputs.logits_per_image.softmax(dim=1)

            # Get top 3 details
            top_indices = torch.topk(detail_probs[0], 3).indices
            details = [detail_prompts[idx] for idx in top_indices.tolist()]

            description = (f"This appears to be {base_description} "
                           f"{', '.join(details)}.")

            if query:
                desc_add = (f" Regarding your question '{query}', the image "
                            f"shows elements related to {', '.join(details)}.")
                description += desc_add

            return description

        except Exception as e:
            logger.error(f"Error describing image: {e}")
            return f"Could not generate image description: {str(e)}"

    def _analyze_image(self, image: Image.Image, query: str = "") -> str:
        """Perform detailed image analysis"""
        if not self.clip_model or not self.clip_processor:
            return ("CLIP model not available for image analysis. "
                    "Basic image information only.")

        try:
            # Analyze various aspects of the image
            analysis = {
                "dimensions": f"{image.width}x{image.height}",
                "format": image.format or "Unknown",
                "mode": image.mode
            }

            # CLIP-based content analysis
            content_categories = [
                "landscape", "portrait", "cityscape", "nature", "people",
                "animals", "food", "technology", "art", "sports",
                "architecture", "vehicles", "indoor scene", "outdoor scene",
                "daytime", "nighttime"
            ]

            inputs = self.clip_processor(
                text=content_categories,
                images=image,
                return_tensors="pt",
                padding=True
            ).to(self.device)

            with torch.no_grad():
                outputs = self.clip_model(**inputs)
                probs = outputs.logits_per_image.softmax(dim=1)

            # Get top categories
            top_indices = torch.topk(probs[0], 5).indices
            indices_list = top_indices.tolist()
            top_categories = [content_categories[idx] for idx in indices_list]
            top_scores = [probs[0][idx].item() for idx in indices_list]

            analysis["content_categories"] = [
                {"category": cat, "confidence": f"{score:.2%}"}
                for cat, score in zip(top_categories, top_scores)
            ]

            # Format analysis result
            result = "Image Analysis:\n"
            result += f"- Dimensions: {analysis['dimensions']}\n"
            result += f"- Format: {analysis['format']}\n"
            result += f"- Color Mode: {analysis['mode']}\n\n"
            result += "Content Analysis:\n"
            for cat_info in analysis["content_categories"]:
                cat_name = cat_info['category']
                conf = cat_info['confidence']
                cat_line = f"- {cat_name}: {conf}\n"
                result += cat_line

            if query:
                result += f"\nQuery Analysis: {query}\n"
                # Simple query processing
                if "color" in query.lower():
                    msg = ("Color analysis would require additional "
                           "image processing.\n")
                    result += msg
                elif "text" in query.lower():
                    msg = ("Text detection would require "
                           "OCR capabilities.\n")
                    result += msg

            return result

        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return f"Could not analyze image: {str(e)}"

    def _classify_image(self, image: Image.Image) -> str:
        """Classify image into categories"""
        if not self.clip_model or not self.clip_processor:
            return ("CLIP model not available for image classification. "
                    "Basic image information: "
                    f"{image.width}x{image.height}, {image.format or 'Unknown'}")

        try:
            # Use predefined categories for classification
            categories = [
                "photograph", "diagram", "chart", "screenshot", "meme",
                "painting", "drawing", "icon", "logo", "document"
            ]

            inputs = self.clip_processor(
                text=categories,
                images=image,
                return_tensors="pt",
                padding=True
            ).to(self.device)

            with torch.no_grad():
                outputs = self.clip_model(**inputs)
                probs = outputs.logits_per_image.softmax(dim=1)

            # Get best classification
            best_idx = torch.argmax(probs[0]).item()
            best_category = categories[best_idx]
            confidence = probs[0][best_idx].item()

            msg = (f"Image Classification: {best_category} "
                   f"(confidence: {confidence:.2%})")
            return msg

        except Exception as e:
            logger.error(f"Error classifying image: {e}")
            return f"Could not classify image: {str(e)}"

    def _search_similar(self, image: Image.Image, query: str = "") -> str:
        """Search for similar images or content"""
        msg = ("Image similarity search requires a database of "
               "reference images. This feature is not yet implemented.")
        return msg

    def _compare_images(self, image: Image.Image, query: str = "") -> str:
        """Compare this image with another"""
        msg = ("Image comparison requires a second image for reference. "
               "Please provide two image paths.")
        return msg

    @classmethod
    def schema(cls):
        """Return tool schema for API documentation"""
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": cls.parameters
        }


# Global vision tool instance - will be initialized with config when needed
vision_tool = None


def get_vision_tool(ultron_config=None):
    """Get or create vision tool instance with configuration"""
    global vision_tool
    if vision_tool is None:
        vision_tool = VisionTool(ultron_config)
    elif ultron_config and vision_tool.ultron_config != ultron_config:
        # Reinitialize with new config if different
        vision_tool = VisionTool(ultron_config)
    return vision_tool


def analyze_image(image_path: str, action: str = "describe",
                  query: str = "", ultron_config=None) -> str:
    """Convenience function for image analysis"""
    tool = get_vision_tool(ultron_config)
    command = f"{action} image {image_path}"
    if query:
        command += f" about {query}"
    return tool.execute(command)


def describe_image(image_path: str, ultron_config=None) -> str:
    """Convenience function for image description"""
    tool = get_vision_tool(ultron_config)
    return tool.execute(f"describe image {image_path}")


def classify_image(image_path: str, ultron_config=None) -> str:
    """Convenience function for image classification"""
    tool = get_vision_tool(ultron_config)
    return tool.execute(f"classify image {image_path}")


if __name__ == "__main__":
    # Test the vision tool
    if VISION_AVAILABLE:
        print("Vision tool initialized successfully")
        tool = get_vision_tool()
        print(f"CLIP model available: {tool.clip_model is not None}")
        print(f"Device: {tool.device}")
    else:
        print("Vision dependencies not available")
