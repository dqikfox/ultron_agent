"""Stable Diffusion Image Generation Tool"""

from typing import Any, Dict
import subprocess
import os

from tools.tool_interface import ToolInterface
from utils.ultron_logger import log_info, log_error


class StableDiffusionTool(ToolInterface):
    """GPU-accelerated Stable Diffusion image generation"""

    def __init__(self):
        self.sd_path = "C:\\Projects\\stable-diffusion"
        self.output_dir = "outputs"
        log_info("stable_diffusion", "Initialized Stable Diffusion Tool")

    @property
    def name(self) -> str:
        return "Stable Diffusion"

    @property
    def description(self) -> str:
        return "GPU-accelerated image generation with Stable Diffusion"

    def match(self, command: str) -> bool:
        keywords = ["generate image", "create image", "stable diffusion", 
                   "txt2img", "image generation", "draw", "picture"]
        return any(kw in command.lower() for kw in keywords)

    def execute(self, command: str, **kwargs: Any) -> str:
        log_info("stable_diffusion", f"Generating image: {command}")
        
        try:
            prompt = self._extract_prompt(command)
            if not prompt:
                return "Please provide an image prompt. Example: generate image of a cat"
            
            # Check if SD is installed
            if not os.path.exists(self.sd_path):
                return self._install_instructions()
            
            # Generate image
            output_file = self._generate_image(prompt, **kwargs)
            
            return f"Image generated: {output_file}\nPrompt: {prompt}"
            
        except Exception as e:
            log_error("stable_diffusion", f"Error: {e}", exception=e)
            return f"Error generating image: {str(e)}"

    def _extract_prompt(self, command: str) -> str:
        """Extract prompt from command"""
        keywords = ["generate image", "create image", "draw", "picture of"]
        for kw in keywords:
            if kw in command.lower():
                return command.lower().split(kw)[-1].strip()
        return command

    def _generate_image(self, prompt: str, **kwargs) -> str:
        """Generate image using Stable Diffusion"""
        width = kwargs.get("width", 512)
        height = kwargs.get("height", 512)
        steps = kwargs.get("steps", 50)
        
        cmd = [
            "python", "scripts/txt2img.py",
            "--prompt", prompt,
            "--W", str(width),
            "--H", str(height),
            "--n_samples", "1",
            "--n_iter", "1",
            "--ddim_steps", str(steps),
            "--outdir", self.output_dir
        ]
        
        result = subprocess.run(
            cmd,
            cwd=self.sd_path,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            # Find generated image
            output_path = os.path.join(self.sd_path, self.output_dir)
            files = os.listdir(output_path)
            if files:
                return os.path.join(output_path, files[-1])
        
        raise Exception(f"Generation failed: {result.stderr}")

    def _install_instructions(self) -> str:
        return """Stable Diffusion not installed.

Run: .\\setup_stable_diffusion.ps1

Or manually:
1. git clone https://github.com/basujindal/stable-diffusion.git C:\\Projects\\stable-diffusion
2. cd C:\\Projects\\stable-diffusion
3. pip install -r requirements.txt
4. Download model: python -c "from diffusers import StableDiffusionPipeline; StableDiffusionPipeline.from_pretrained('runwayml/stable-diffusion-v1-5')"
"""

    @staticmethod
    def schema() -> Dict[str, Any]:
        return {
            "name": "stable_diffusion",
            "description": "Generate images from text prompts using Stable Diffusion",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Image description"},
                    "width": {"type": "integer", "default": 512},
                    "height": {"type": "integer", "default": 512},
                    "steps": {"type": "integer", "default": 50}
                },
                "required": ["prompt"]
            }
        }
