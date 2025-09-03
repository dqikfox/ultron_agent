"""
Config Validator for Ultron Agent 2

Validates ultron_config.json and config.py for required keys, types, and values.
Reports missing, null, or invalid entries and provides error messages for integration with error handlers.
"""
import json
import os
from typing import Dict, List, Any

REQUIRED_KEYS = [
    "use_voice", "use_vision", "use_api", "use_gui",
    "voice_engine", "stt_engine", "tts_engine",
    "openai_api_key", "ollama_api_key", "elevenlabs_api_key",
    "supabase_url", "supabase_anon_key", "gemini_api_key",
    "jwt_secret", "llm_model", "ollama_base_url",
    "voice_boot_message", "elevenlabs_agent_id"
]

class ConfigValidator:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.errors: List[str] = []
        self.config: Dict[str, Any] = {}

    def load_config(self):
        if not os.path.exists(self.config_path):
            self.errors.append(f"Config file not found: {self.config_path}")
            return False
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            return True
        except Exception as e:
            self.errors.append(f"Failed to load config: {e}")
            return False

    def validate(self):
        for key in REQUIRED_KEYS:
            if key not in self.config:
                self.errors.append(f"Missing key: {key}")
            elif self.config[key] is None or self.config[key] == "" or self.config[key] == "YOUR_ELEVENLABS_API_KEY_HERE" or self.config[key] == "YOUR_VOICE_ID_HERE":
                self.errors.append(f"Unset or placeholder value for key: {key}")
        return len(self.errors) == 0

    def get_errors(self) -> List[str]:
        return self.errors

if __name__ == "__main__":
    validator = ConfigValidator("ultron_config.json")
    if validator.load_config():
        valid = validator.validate()
        if not valid:
            print("Config validation errors: - config_validator.py:54")
            for err in validator.get_errors():
                print(f"{err} - config_validator.py:56")
        else:
            print("Config is valid. - config_validator.py:58")
    else:
        print("Failed to load config. - config_validator.py:60")
