from .base import Tool
import logging
import requests

class ImageGenerationTool(Tool):
    def __init__(self, config):
        self.name = "ImageGenerationTool"
        self.description = "Generate images using Google Gemini API."
        self.config = config
        super().__init__()

    def match(self, command: str) -> bool:
        cmd = command.lower()
        return "generate image" in cmd or "create image" in cmd

    def execute(self, command: str) -> str:
        prompt = command.replace("generate image", "").replace("create image", "").strip()
        if not prompt:
            return "No image prompt provided."
        try:
            api_key = self.config.data.get("gemini_api_key")
            if not api_key:
                return "Gemini API key not configured."
            response = requests.post(
                "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent",
                headers={"Authorization": f"Bearer {api_key}"},
                json={"contents": [{"parts": [{"text": f"Generate an image: {prompt}"}]}]}
            )
            response.raise_for_status()
            data = response.json()
            image_url = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text")
            logging.info(f"Generated image URL: {image_url}")
            return f"Image generated: {image_url}"
        except Exception as e:
            logging.error(f"Image generation error: {e}")
            return f"Error: {e}"