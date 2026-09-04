"""
Image Generation Tool - Multi-provider support
"""
import os
from typing import Optional

class ImageGenerationTool:
    name = "Image Generation"
    description = "Generate images using AI (DALL-E, Stability AI)"
    
    def __init__(self, config=None, memory=None):
        self.config = config
        self.memory = memory
    
    def match(self, command: str) -> bool:
        keywords = ['generate image', 'create image', 'draw', 'picture of', 'image of']
        return any(k in command.lower() for k in keywords)
    
    def execute(self, command: str) -> str:
        # Extract prompt
        prompt = self._extract_prompt(command)
        if not prompt:
            return "Please specify what image to generate"
        
        # Try providers in order
        providers = [
            ('DALL-E', self._dalle),
            ('Stability AI', self._stability),
        ]
        
        for name, func in providers:
            try:
                result = func(prompt)
                if result:
                    return f"Generated with {name}: {result}"
            except Exception:
                continue
        
        return "Image generation failed - check API keys"
    
    def _extract_prompt(self, command: str) -> Optional[str]:
        """Extract image prompt from command"""
        triggers = ['generate image', 'create image', 'draw', 'picture of', 'image of']
        for trigger in triggers:
            if trigger in command.lower():
                return command.lower().split(trigger, 1)[1].strip()
        return None
    
    def _dalle(self, prompt: str) -> Optional[str]:
        """Generate with DALL-E"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None
        
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        url = response.data[0].url
        
        # Download
        import requests
        img_data = requests.get(url).content
        filename = f"generated_{hash(prompt)}.png"
        with open(filename, 'wb') as f:
            f.write(img_data)
        
        return filename
    
    def _stability(self, prompt: str) -> Optional[str]:
        """Generate with Stability AI"""
        api_key = os.getenv("STABILITY_API_KEY")
        if not api_key:
            return None
        
        import requests
        import base64
        
        url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        
        response = requests.post(url,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "text_prompts": [{"text": prompt}],
                "cfg_scale": 7,
                "height": 1024,
                "width": 1024,
                "samples": 1,
                "steps": 30,
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            filename = f"generated_{hash(prompt)}.png"
            with open(filename, "wb") as f:
                f.write(base64.b64decode(data["artifacts"][0]["base64"]))
            return filename
        
        return None
    
    @classmethod
    def schema(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "prompt": {"type": "string", "description": "Image description"}
            }
        }
