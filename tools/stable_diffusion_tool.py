"""
Stable Diffusion Tool for ULTRON Agent

Integrates Stable Diffusion image generation capabilities
"""

import os
import subprocess
import time
from typing import Dict, Any, Optional
from utils.ultron_logger import log_info, log_error, log_ai_decision, log_file_operation


class StableDiffusionTool:
    """
    Tool for generating images using Stable Diffusion
    """

    name = "Stable Diffusion Image Generator"
    description = "Generate images using Stable Diffusion models"

    def __init__(self, config=None):
        self.config = config or {}
        # Paths from user configuration
        self.sd_webui_path = r"C:\Projects\stable-diffusion-webui"
        self.sd_cli_path = r"C:\Projects\stable-diffusion-3.5-large"
        self.models_path = r"D:\models\hub"
        self.output_dir = r"C:\Users\ultro\OneDrive\Pictures\STABLED"
        os.makedirs(self.output_dir, exist_ok=True)

        log_info("stable_diffusion_tool", "Stable Diffusion tool initialized")

    def match(self, command: str) -> bool:
        """Check if command matches image generation"""
        command_lower = command.lower()
        return any(keyword in command_lower for keyword in [
            "generate image", "create image", "stable diffusion",
            "sd generate", "make picture", "draw image", "ai image"
        ])

    def execute(self, command: str) -> str:
        """Execute image generation"""
        try:
            # Parse command for parameters
            params = self._parse_command(command)

            if not params.get('prompt'):
                return ("Please provide a prompt for image generation. "
                        "Example: 'generate image of a futuristic city'")

            # Log AI decision to generate image
            log_ai_decision(
                "stable_diffusion_tool",
                f"Generating image with prompt: {params['prompt']}",
                ai_model="stable_diffusion",
                confidence_score=0.9
            )

            # Try webui first, fallback to CLI
            result = self._generate_with_webui(params)
            if not result:
                result = self._generate_with_cli(params)

            if result:
                log_info("stable_diffusion_tool", f"Image generated: {result}")
                return f"Image generated successfully: {result}"
            else:
                return "Failed to generate image. Check logs for details."

        except Exception as e:
            log_error("stable_diffusion_tool", f"Generation failed: {e}")
            return f"Image generation failed: {str(e)}"

    def _parse_command(self, command: str) -> Dict[str, Any]:
        """Parse command for generation parameters"""
        params = {
            'prompt': '',
            'negative_prompt': '',
            'steps': 20,
            'width': 512,
            'height': 512,
            'guidance_scale': 7.5,
            'seed': None
        }

        # Simple parsing - can be enhanced
        if 'generate image' in command.lower():
            # Extract prompt after "generate image of" or similar
            prompt_start = command.lower().find('generate image')
            if prompt_start != -1:
                params['prompt'] = command[
                    prompt_start + len('generate image'):].strip()

        return params

    def _generate_with_webui(self, params: Dict[str, Any]) -> Optional[str]:
        """Generate using Automatic1111 WebUI"""
        try:
            # Check if webui is running (simplified check)
            import requests
            response = requests.get(
                'http://127.0.0.1:7860/sdapi/v1/sd-models', timeout=5)
            if response.status_code != 200:
                return None

            # Use WebUI API
            api_url = 'http://127.0.0.1:7860/sdapi/v1/txt2img'

            payload = {
                'prompt': params['prompt'],
                'negative_prompt': params.get('negative_prompt', ''),
                'steps': params['steps'],
                'width': params['width'],
                'height': params['height'],
                'cfg_scale': params['guidance_scale'],
                'seed': params.get('seed', -1),
                'sampler_name': 'Euler a'
            }

            response = requests.post(api_url, json=payload, timeout=60)
            if response.status_code == 200:
                result = response.json()
                # Save image
                import base64
                image_data = base64.b64decode(result['images'][0])
                filename = f"sd_webui_{int(time.time())}.png"
                filepath = os.path.join(self.output_dir, filename)

                with open(filepath, 'wb') as f:
                    f.write(image_data)

                # Log file operation
                log_file_operation(
                    "stable_diffusion_tool",
                    f"Saved generated image to {filepath}",
                    filepath,
                    "create"
                )

                return filepath

        except Exception as e:
            log_error("stable_diffusion_tool", f"WebUI generation failed: {e}")

        return None

    def _generate_with_cli(self, params: Dict[str, Any]) -> Optional[str]:
        """Generate using CLI version"""
        try:
            if not os.path.exists(self.sd_cli_path):
                return None

            # Construct command
            cmd = [
                'python', 'scripts/txt2img.py',
                '--prompt', params['prompt'],
                '--steps', str(params['steps']),
                '--W', str(params['width']),
                '--H', str(params['height']),
                '--output', self.output_dir
            ]

            if params.get('negative_prompt'):
                cmd.extend(['--negative_prompt', params['negative_prompt']])

            if params.get('seed'):
                cmd.extend(['--seed', str(params['seed'])])

            # Run command
            result = subprocess.run(
                cmd, cwd=self.sd_cli_path, capture_output=True,
                text=True, timeout=120)

            if result.returncode == 0:
                # Find generated file
                files = os.listdir(self.output_dir)
                if files:
                    latest = max(
                        files,
                        key=lambda x: os.path.getctime(
                            os.path.join(self.output_dir, x)))
                    filepath = os.path.join(self.output_dir, latest)

                    # Log file operation
                    log_file_operation(
                        "stable_diffusion_tool",
                        f"Saved generated image to {filepath}",
                        filepath,
                        "create"
                    )

                    return filepath

        except Exception as e:
            log_error("stable_diffusion_tool", f"CLI generation failed: {e}")

        return None

    @classmethod
    def schema(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Image generation command with prompt"
                    }
                },
                "required": ["command"]
            }
        }
