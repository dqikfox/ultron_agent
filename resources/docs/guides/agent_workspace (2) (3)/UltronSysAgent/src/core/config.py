"""
Configuration Manager for UltronSysAgent
Handles loading and managing configuration from multiple sources
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

class ConfigManager:
    """Manages configuration for UltronSysAgent"""
    
    def __init__(self):
        self.config: Dict[str, Any] = {}
        self.config_dir = Path(__file__).parent.parent.parent / "config"
        self.config_file = self.config_dir / "config.json"
        self.env_file = self.config_dir / ".env"
        self.logger = logging.getLogger(__name__)
        
        # Default configuration
        self._load_defaults()
    
    def _load_defaults(self):
        """Load default configuration values"""
        self.config = {
            # System settings
            "system": {
                "admin_mode": False,
                "auto_start": True,
                "debug_mode": False,
                "log_level": "INFO"
            },
            
            # Voice engine settings
            "voice": {
                "always_listening": True,
                "wake_word_enabled": False,
                "wake_word": "ultron",
                "vad_threshold": 0.3,
                "stt_provider": "whisper",  # whisper, deepseek
                "tts_provider": "pyttsx3",  # pyttsx3, elevenlabs
                "streaming_tts": True,
                "voice_id": "default",
                "speech_rate": 200,
                "speech_volume": 0.8
            },
            
            # AI Brain settings
            "ai": {
                "primary_model": "gpt-4",  # gpt-4, deepseek, phi-3
                "fallback_models": ["deepseek", "phi-3"],
                "local_models_enabled": True,
                "temperature": 0.7,
                "max_tokens": 2048,
                "memory_enabled": True,
                "context_window": 8192
            },
            
            # API Keys and endpoints
            "api": {
                "openai_api_key": "",
                "deepseek_api_key": "",
                "elevenlabs_api_key": "",
                "offline_mode": False
            },
            
            # Security settings
            "security": {
                "require_admin_confirmation": True,
                "log_all_commands": True,
                "dangerous_commands_enabled": False,
                "whitelist_mode": False
            },
            
            # GUI settings
            "gui": {
                "theme": "ultron",
                "window_size": [1200, 800],
                "always_on_top": False,
                "show_chatlog": True,
                "show_system_info": True
            },
            
            # Hardware settings
            "hardware": {
                "gpu_acceleration": True,
                "cuda_enabled": True,
                "audio_device": "default",
                "camera_enabled": False,
                "camera_device": 0
            },
            
            # Plugin settings
            "plugins": {
                "enabled": True,
                "auto_load": True,
                "plugin_dir": "plugins"
            },
            
            # Memory settings
            "memory": {
                "short_term_limit": 100,
                "long_term_enabled": True,
                "vector_db_enabled": True,
                "auto_save_interval": 300  # seconds
            },
            
            # Startup settings
            "startup": {
                "greeting": "UltronSysAgent online. I am ready to assist you.",
                "check_updates": True,
                "load_previous_session": True
            }
        }
    
    def load(self):
        """Load configuration from all sources"""
        self.logger.info("Loading configuration...")
        
        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)
        
        # Load from environment variables
        self._load_from_env()
        
        # Load from .env file
        self._load_from_env_file()
        
        # Load from config.json
        self._load_from_json()
        
        # Validate configuration
        self._validate_config()
        
        self.logger.info("✅ Configuration loaded successfully")
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        env_mappings = {
            'ULTRON_ADMIN_MODE': ('system', 'admin_mode'),
            'ULTRON_DEBUG': ('system', 'debug_mode'),
            'OPENAI_API_KEY': ('api', 'openai_api_key'),
            'DEEPSEEK_API_KEY': ('api', 'deepseek_api_key'),
            'ELEVENLABS_API_KEY': ('api', 'elevenlabs_api_key'),
            'ULTRON_OFFLINE_MODE': ('api', 'offline_mode'),
            'ULTRON_GPU_ENABLED': ('hardware', 'gpu_acceleration'),
            'ULTRON_CUDA_ENABLED': ('hardware', 'cuda_enabled')
        }
        
        for env_var, (section, key) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert boolean strings
                if value.lower() in ('true', 'false'):
                    value = value.lower() == 'true'
                self.config[section][key] = value
    
    def _load_from_env_file(self):
        """Load configuration from .env file"""
        if self.env_file.exists():
            try:
                with open(self.env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()
                self._load_from_env()  # Re-process with new env vars
            except Exception as e:
                self.logger.warning(f"Failed to load .env file: {e}")
    
    def _load_from_json(self):
        """Load configuration from config.json"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    json_config = json.load(f)
                    self._merge_config(self.config, json_config)
            except Exception as e:
                self.logger.warning(f"Failed to load config.json: {e}")
    
    def _merge_config(self, base: Dict, override: Dict):
        """Recursively merge configuration dictionaries"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def _validate_config(self):
        """Validate configuration values"""
        # Ensure required API keys are present if not in offline mode
        if not self.config['api']['offline_mode']:
            if not self.config['api'].get('openai_api_key') and self.config['ai']['primary_model'].startswith('gpt'):
                self.logger.warning("OpenAI API key not found, switching to offline mode")
                self.config['api']['offline_mode'] = True
        
        # Validate file paths
        plugin_dir = Path(self.config['plugins']['plugin_dir'])
        if not plugin_dir.is_absolute():
            self.config['plugins']['plugin_dir'] = str(Path(__file__).parent.parent.parent / plugin_dir)
    
    def save(self):
        """Save current configuration to config.json"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            self.logger.info("Configuration saved successfully")
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def is_admin_mode(self) -> bool:
        """Check if admin mode is enabled"""
        return self.config.get('system', {}).get('admin_mode', False)
    
    def is_offline_mode(self) -> bool:
        """Check if offline mode is enabled"""
        return self.config.get('api', {}).get('offline_mode', False)
