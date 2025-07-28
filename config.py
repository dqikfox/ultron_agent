import os
import json
import logging
import uuid
from cryptography.fernet import Fernet

class Config:
    def __init__(self, path: str = "ultron_config.json"):
        self.data = {}
        self.load_config(path)
        self.load_env_variables()
        logging.info("Configuration loaded and logging initialized.")

    def load_config(self, path: str):
        if os.path.exists(path):
            with open(path, 'r') as f:
                self.data = json.load(f)
        else:
            logging.error(f"Configuration file {path} not found.")
            raise FileNotFoundError(f"Configuration file {path} not found.")

    def load_env_variables(self):
        """Load configuration from environment variables."""
        # OpenAI
        if os.getenv("OPENAI_API_KEY"):
            self.data["openai_api_key"] = os.getenv("OPENAI_API_KEY")
            
        # Ollama
        if os.getenv("OLLAMA_API_KEY"):
            self.data["ollama_api_key"] = os.getenv("OLLAMA_API_KEY")
            
        # ElevenLabs
        if os.getenv("ELEVENLABS_API_KEY"):
            self.data["elevenlabs_api_key"] = os.getenv("ELEVENLABS_API_KEY")
            
        # Google Cloud / Gemini
        if os.getenv("GEMINI_API_KEY"):
            self.data["gemini_api_key"] = os.getenv("GEMINI_API_KEY")
            
        # Set Google Application Credentials env var if provided
        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            
        # Logging
        if os.getenv("LOGFLARE_LOGGER_BACKEND_API_KEY"):
            self.data["logflare_logger_backend_api_key"] = os.getenv("LOGFLARE_LOGGER_BACKEND_API_KEY")
        if os.getenv("LOGFLARE_API_KEY"):
            self.data["logflare_api_key"] = os.getenv("LOGFLARE_API_KEY")
            
        logging.info("Environment variables loaded into configuration.")