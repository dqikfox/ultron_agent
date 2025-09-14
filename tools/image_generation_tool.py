"""
ULTRON Agent - Enhanced Stable Diffusion Tool
Advanced image generation with multiple backends and Colab integration
"""

from .base import Tool
import logging
import requests
import json
import time
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import uuid
from datetime import datetime
import base64
import io
from PIL import Image


class ImageGenerationTool(Tool):
    """Enhanced Stable Diffusion tool with Colab notebook integration"""
    
    def __init__(self, config):
        self.name = "ImageGenerationTool"
        self.description = "Generate high-quality images using Stable Diffusion with multiple backends"
        self.config = config
        super().__init__()
        
        # Configuration
        self.colab_endpoint = None  # Will be set when Colab notebook is running
        self.local_endpoint = "http://localhost:8000"  # Local Stable Diffusion server
        self.backup_endpoints = [
            "http://localhost:7860",  # Gradio interface
            "http://127.0.0.1:8000",  # Alternative local
        ]
        
        # Image storage
        self.images_dir = Path("generated_images")
        self.images_dir.mkdir(exist_ok=True)
        
        # Generation history
        self.generation_history = []
        self.session_id = str(uuid.uuid4())[:8]
        
        # Default parameters
        self.default_params = {
            "negative_prompt": "ugly, blurry, poor quality, distorted, deformed, bad anatomy",
            "width": 512,
            "height": 512,
            "steps": 20,
            "guidance_scale": 7.5,
            "num_images": 1
        }
        
        logging.info(f"🎨 Stable Diffusion Tool initialized with session: {self.session_id}")
    
    @staticmethod
    def schema() -> Dict[str, Any]:
        """Return tool schema for discovery"""
        return {
            "name": "ImageGenerationTool",
            "description": "Generate high-quality images using Stable Diffusion AI",
            "parameters": {
                "prompt": {"type": "string", "description": "Description of the image to generate"},
                "negative_prompt": {"type": "string", "description": "Things to avoid in the image"},
                "width": {"type": "integer", "description": "Image width (default: 512)"},
                "height": {"type": "integer", "description": "Image height (default: 512)"},
                "steps": {"type": "integer", "description": "Number of inference steps (default: 20)"},
                "guidance_scale": {"type": "float", "description": "How closely to follow prompt (default: 7.5)"},
                "num_images": {"type": "integer", "description": "Number of images to generate (default: 1)"},
                "style": {"type": "string", "description": "Art style (realistic, anime, cyberpunk, etc.)"},
                "quality": {"type": "string", "description": "Quality level (fast, balanced, high)"}
            },
            "capabilities": [
                "Text-to-image generation",
                "Multiple art styles",
                "Batch generation",
                "Quality control",
                "History tracking",
                "Colab integration"
            ]
        }
    
    def match(self, command: str) -> bool:
        """Check if command matches this tool"""
        cmd = command.lower()
        keywords = [
            "generate image", "create image", "make image", "draw image",
            "stable diffusion", "diffusion", "ai art", "generate art",
            "create picture", "make picture", "draw picture", "make a picture",
            "image generation", "art generation", "stable diff", "generate photo",
            "create photo", "make photo", "draw art", "create art", "make art"
        ]
        return any(keyword in cmd for keyword in keywords)
    
    def set_colab_endpoint(self, endpoint: str) -> bool:
        """Set Colab notebook endpoint"""
        try:
            # Test the endpoint
            response = requests.get(f"{endpoint}/health", timeout=5)
            if response.status_code == 200:
                self.colab_endpoint = endpoint
                logging.info(f"🌐 Colab endpoint set: {endpoint}")
                return True
            else:
                logging.warning(f"⚠️ Colab endpoint test failed: {response.status_code}")
                return False
        except Exception as e:
            logging.error(f"❌ Failed to set Colab endpoint: {e}")
            return False
    
    def get_available_endpoint(self) -> Optional[str]:
        """Find the first available Stable Diffusion endpoint"""
        endpoints_to_try = []
        
        # Prioritize Colab endpoint if available
        if self.colab_endpoint:
            endpoints_to_try.append(self.colab_endpoint)
        
        # Add local and backup endpoints
        endpoints_to_try.extend([self.local_endpoint] + self.backup_endpoints)
        
        for endpoint in endpoints_to_try:
            try:
                response = requests.get(f"{endpoint}/health", timeout=3)
                if response.status_code == 200:
                    logging.info(f"✅ Using endpoint: {endpoint}")
                    return endpoint
            except Exception:
                continue
        
        return None
    
    def parse_parameters(self, command: str) -> Dict[str, Any]:
        """Parse generation parameters from command"""
        params = self.default_params.copy()
        cmd_lower = command.lower()
        
        # Extract prompt (everything after the command trigger)
        prompt_start_phrases = [
            "generate image of", "generate image", "create image of", "create image", 
            "make image of", "make image", "draw image of", "draw image",
            "stable diffusion", "generate art of", "generate art", 
            "create picture of", "create picture", "make a picture of"
        ]
        
        prompt = command
        for phrase in prompt_start_phrases:
            if phrase in cmd_lower:
                prompt = command[cmd_lower.find(phrase) + len(phrase):].strip()
                break
        
        # Remove parameter keywords from prompt and extract them
        param_keywords = {
            "width": ["width:", "w:", "width="],
            "height": ["height:", "h:", "height="],
            "steps": ["steps:", "iterations:", "steps="],
            "guidance": ["guidance:", "cfg:", "guidance_scale:", "guidance="],
            "negative": ["negative:", "avoid:", "not:", "negative_prompt:"],
            "count": ["count:", "number:", "num:", "images:"],
            "style": ["style:", "art_style:", "type:"],
            "quality": ["quality:", "qual:", "speed:"]
        }
        
        # Extract parameters
        for param, keywords in param_keywords.items():
            for keyword in keywords:
                if keyword in cmd_lower:
                    try:
                        # Find the parameter value
                        start_idx = cmd_lower.find(keyword) + len(keyword)
                        # Extract until next space or end
                        param_text = command[start_idx:].split()[0] if command[start_idx:].split() else ""
                        
                        # Clean the parameter from prompt
                        full_param = keyword + param_text
                        prompt = prompt.replace(full_param, "").strip()
                        
                        # Parse the value
                        if param == "width":
                            params["width"] = max(256, min(1024, int(param_text)))
                        elif param == "height":
                            params["height"] = max(256, min(1024, int(param_text)))
                        elif param == "steps":
                            params["steps"] = max(1, min(50, int(param_text)))
                        elif param == "guidance":
                            params["guidance_scale"] = max(1.0, min(20.0, float(param_text)))
                        elif param == "count":
                            params["num_images"] = max(1, min(4, int(param_text)))
                        elif param == "negative":
                            # Extract negative prompt until next parameter or end
                            remaining = command[start_idx:].strip()
                            next_param_idx = len(remaining)
                            for other_keywords in param_keywords.values():
                                for other_kw in other_keywords:
                                    idx = remaining.lower().find(other_kw)
                                    if idx > 0:
                                        next_param_idx = min(next_param_idx, idx)
                            
                            negative_text = remaining[:next_param_idx].strip()
                            if negative_text:
                                params["negative_prompt"] = negative_text
                                prompt = prompt.replace(keyword + negative_text, "").strip()
                        
                    except (ValueError, IndexError):
                        continue
        
        # Apply style presets
        style_presets = {
            "realistic": {
                "negative_prompt": "cartoon, anime, painting, drawing, sketch, unrealistic",
                "guidance_scale": 8.0
            },
            "anime": {
                "negative_prompt": "realistic, photography, 3d render",
                "guidance_scale": 7.0
            },
            "cyberpunk": {
                "prompt_suffix": ", cyberpunk style, neon lights, futuristic",
                "negative_prompt": "medieval, ancient, natural"
            },
            "fantasy": {
                "prompt_suffix": ", fantasy art, magical, mystical",
                "negative_prompt": "modern, realistic, photography"
            }
        }
        
        # Check for style in command
        for style, style_params in style_presets.items():
            if style in cmd_lower:
                if "prompt_suffix" in style_params:
                    prompt += style_params["prompt_suffix"]
                if "negative_prompt" in style_params:
                    params["negative_prompt"] = style_params["negative_prompt"]
                if "guidance_scale" in style_params:
                    params["guidance_scale"] = style_params["guidance_scale"]
                break
        
        # Quality presets
        if "fast" in cmd_lower or "quick" in cmd_lower:
            params["steps"] = 10
            params["guidance_scale"] = 6.0
        elif "high quality" in cmd_lower or "detailed" in cmd_lower:
            params["steps"] = 30
            params["guidance_scale"] = 8.5
        
        # Clean and set final prompt
        prompt = " ".join(prompt.split())  # Remove extra whitespace
        if not prompt or len(prompt.strip()) < 3:
            prompt = "a beautiful landscape"
        
        params["prompt"] = prompt
        return params
    
    def generate_image(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate image using the specified endpoint"""
        try:
            logging.info(f"🎨 Generating image with prompt: '{params['prompt'][:50]}...'")
            
            response = requests.post(
                f"{endpoint}/generate",
                json=params,
                timeout=120  # 2 minutes timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return result
                else:
                    return {"error": result.get("error", "Unknown error")}
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
                
        except requests.Timeout:
            return {"error": "Request timeout - image generation took too long"}
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def save_images_locally(self, images_data: List[Dict]) -> List[str]:
        """Save generated images locally and return file paths"""
        saved_paths = []
        
        for i, img_data in enumerate(images_data):
            try:
                # Decode base64 image
                if "base64" in img_data:
                    img_bytes = base64.b64decode(img_data["base64"])
                    img = Image.open(io.BytesIO(img_bytes))
                    
                    # Create filename
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"ultron_sd_{timestamp}_{self.session_id}_{i:02d}.png"
                    filepath = self.images_dir / filename
                    
                    # Save image
                    img.save(filepath)
                    saved_paths.append(str(filepath))
                    
                    # Update generation history
                    history_entry = {
                        "filename": filename,
                        "filepath": str(filepath),
                        "prompt": img_data.get("prompt", ""),
                        "timestamp": timestamp,
                        "session": self.session_id,
                        "parameters": {
                            k: v for k, v in img_data.items() 
                            if k not in ["base64", "filepath"]
                        }
                    }
                    self.generation_history.append(history_entry)
                    
            except Exception as e:
                logging.error(f"❌ Failed to save image {i}: {e}")
                
        return saved_paths
    
    def execute(self, command: str) -> str:
        """Execute the Stable Diffusion generation command"""
        try:
            # Find available endpoint
            endpoint = self.get_available_endpoint()
            if not endpoint:
                return ("❌ No Stable Diffusion server available. Please:\n"
                       "1. Run the Colab notebook\n"
                       "2. Start a local Stable Diffusion server\n"
                       "3. Use the web interface at localhost:7860")
            
            # Parse parameters from command
            params = self.parse_parameters(command)
            
            # Generate image
            result = self.generate_image(endpoint, params)
            
            if "error" in result:
                return f"❌ Generation failed: {result['error']}"
            
            # Process successful result
            images = result.get("images", [])
            if not images:
                return "❌ No images generated"
            
            # Save images locally
            saved_paths = self.save_images_locally(images)
            
            # Create response
            response_parts = [
                f"🎨 Successfully generated {len(images)} image(s)!",
                f"📝 Prompt: {params['prompt']}",
                f"⚙️ Parameters: {params['width']}x{params['height']}, {params['steps']} steps",
                f"📁 Saved to: {', '.join([Path(p).name for p in saved_paths])}"
            ]
            
            # Add endpoint info
            if endpoint == self.colab_endpoint:
                response_parts.append("🌐 Generated using Colab notebook")
            else:
                response_parts.append(f"💻 Generated using local server: {endpoint}")
            
            # Add history count
            response_parts.append(f"📊 Total generated this session: {len(self.generation_history)}")
            
            # Add quick access info
            response_parts.append("\n💡 Use 'show last image' to view the latest generation")
            response_parts.append("💡 Use 'stable diffusion history' to see all generations")
            
            return "\n".join(response_parts)
            
        except Exception as e:
            logging.error(f"❌ Stable Diffusion execution error: {e}")
            return f"❌ Error: {str(e)}"
    
    def get_generation_history(self, limit: int = 10) -> List[Dict]:
        """Get recent generation history"""
        return self.generation_history[-limit:]
    
    def get_last_image_path(self) -> Optional[str]:
        """Get path to the most recently generated image"""
        if self.generation_history:
            return self.generation_history[-1]["filepath"]
        return None
    
    def clear_history(self):
        """Clear generation history"""
        self.generation_history.clear()
        logging.info("🗑️ Stable Diffusion history cleared")