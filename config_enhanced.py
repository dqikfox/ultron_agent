"""
Enhanced Configuration Management for ULTRON Agent 3.0
Provides secure, environment-based configuration with validation
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseSettings, validator, Field
from pydantic_settings import BaseSettings as PydanticSettings
from dotenv import load_dotenv
import json
import logging

logger = logging.getLogger(__name__)

class SecurityConfig(BaseSettings):
    """Security-related configuration"""
    require_admin_confirmation: bool = Field(True, env='REQUIRE_ADMIN_CONFIRMATION')
    log_all_commands: bool = Field(True, env='LOG_ALL_COMMANDS')
    dangerous_commands_enabled: bool = Field(False, env='DANGEROUS_COMMANDS_ENABLED')
    whitelist_mode: bool = Field(False, env='WHITELIST_MODE')
    max_file_size_mb: int = Field(100, env='MAX_FILE_SIZE_MB')

class APIConfig(BaseSettings):
    """API keys and endpoints configuration"""
    openai_api_key: Optional[str] = Field(None, env='OPENAI_API_KEY')
    nvidia_api_key: Optional[str] = Field(None, env='NVIDIA_API_KEY')
    nvidia_api_keys: Optional[str] = Field(None, env='NVIDIA_API_KEYS')  # comma-separated
    elevenlabs_api_key: Optional[str] = Field(None, env='ELEVENLABS_API_KEY')
    deepseek_api_key: Optional[str] = Field(None, env='DEEPSEEK_API_KEY')
    google_api_key: Optional[str] = Field(None, env='GOOGLE_API_KEY')
    
    # API endpoints
    ollama_endpoint: str = Field('http://localhost:11434', env='OLLAMA_ENDPOINT')
    openai_base_url: Optional[str] = Field(None, env='OPENAI_BASE_URL')
    
    @validator('nvidia_api_keys')
    def parse_nvidia_keys(cls, v):
        """Parse comma-separated NVIDIA API keys"""
        if v:
            return [key.strip() for key in v.split(',') if key.strip()]
        return []
    
    def get_nvidia_keys(self) -> List[str]:
        """Get all NVIDIA API keys as a list"""
        keys = []
        if self.nvidia_api_key:
            keys.append(self.nvidia_api_key)
        if self.nvidia_api_keys:
            keys.extend(self.nvidia_api_keys)
        return list(set(keys))  # Remove duplicates

class AIConfig(BaseSettings):
    """AI model configuration"""
    primary_model: str = Field('gpt-4', env='PRIMARY_MODEL')
    fallback_models: str = Field('deepseek,phi-3', env='FALLBACK_MODELS')
    temperature: float = Field(0.7, env='AI_TEMPERATURE')
    max_tokens: int = Field(2048, env='MAX_TOKENS')
    context_window: int = Field(8192, env='CONTEXT_WINDOW')
    
    @validator('fallback_models')
    def parse_fallback_models(cls, v):
        """Parse comma-separated fallback models"""
        if isinstance(v, str):
            return [model.strip() for model in v.split(',') if model.strip()]
        return v

class VoiceConfig(BaseSettings):
    """Voice system configuration"""
    enabled: bool = Field(True, env='VOICE_ENABLED')
    engine: str = Field('enhanced', env='VOICE_ENGINE')  # enhanced, pyttsx3, openai, console
    rate: int = Field(200, env='VOICE_RATE')
    volume: float = Field(0.9, env='VOICE_VOLUME')
    voice_id: Optional[str] = Field(None, env='VOICE_ID')

class GUIConfig(BaseSettings):
    """GUI configuration"""
    theme: str = Field('ultron', env='GUI_THEME')
    window_width: int = Field(1200, env='GUI_WIDTH')
    window_height: int = Field(800, env='GUI_HEIGHT')
    always_on_top: bool = Field(False, env='GUI_ALWAYS_ON_TOP')
    show_chatlog: bool = Field(True, env='GUI_SHOW_CHATLOG')
    show_system_info: bool = Field(True, env='GUI_SHOW_SYSTEM_INFO')

class LoggingConfig(BaseSettings):
    """Logging configuration"""
    level: str = Field('INFO', env='LOG_LEVEL')
    file_enabled: bool = Field(True, env='LOG_FILE_ENABLED')
    console_enabled: bool = Field(True, env='LOG_CONSOLE_ENABLED')
    max_file_size_mb: int = Field(10, env='LOG_MAX_SIZE_MB')
    backup_count: int = Field(5, env='LOG_BACKUP_COUNT')
    json_format: bool = Field(False, env='LOG_JSON_FORMAT')

class UltronConfig:
    """Main configuration class that combines all configuration sections"""
    
    def __init__(self, config_file: Optional[str] = None, load_env: bool = True):
        """
        Initialize configuration
        
        Args:
            config_file: Path to JSON config file (optional)
            load_env: Whether to load from environment variables
        """
        if load_env:
            # Load from .env file if it exists
            env_file = Path('.env')
            if env_file.exists():
                load_dotenv(env_file)
        
        # Initialize configuration sections
        self.security = SecurityConfig()
        self.api = APIConfig()
        self.ai = AIConfig()
        self.voice = VoiceConfig()
        self.gui = GUIConfig()
        self.logging = LoggingConfig()
        
        # Load from JSON config file if provided
        if config_file and Path(config_file).exists():
            self._load_from_json(config_file)
        
        # Validate configuration
        self._validate_config()
        
        logger.info("Configuration loaded successfully")
    
    def _load_from_json(self, config_file: str) -> None:
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            # Update each section with JSON data
            for section_name, section_obj in [
                ('security', self.security),
                ('api', self.api), 
                ('ai', self.ai),
                ('voice', self.voice),
                ('gui', self.gui),
                ('logging', self.logging)
            ]:
                if section_name in config_data:
                    for key, value in config_data[section_name].items():
                        if hasattr(section_obj, key):
                            setattr(section_obj, key, value)
            
            logger.info(f"Configuration loaded from {config_file}")
        
        except Exception as e:
            logger.error(f"Failed to load configuration from {config_file}: {e}")
    
    def _validate_config(self) -> None:
        """Validate configuration values"""
        issues = []
        
        # Check for API keys if AI features are enabled
        if not self.api.openai_api_key and not self.api.get_nvidia_keys():
            issues.append("No AI API keys configured - AI features may not work")
        
        # Validate voice settings
        if self.voice.enabled and self.voice.engine not in ['enhanced', 'pyttsx3', 'openai', 'console']:
            issues.append(f"Invalid voice engine: {self.voice.engine}")
        
        # Validate logging level
        if self.logging.level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            issues.append(f"Invalid log level: {self.logging.level}")
        
        if issues:
            logger.warning("Configuration validation issues found:")
            for issue in issues:
                logger.warning(f"  - {issue}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'security': self.security.dict(),
            'api': self.api.dict(exclude={'openai_api_key', 'nvidia_api_key', 'nvidia_api_keys', 'elevenlabs_api_key'}),
            'ai': self.ai.dict(),
            'voice': self.voice.dict(),
            'gui': self.gui.dict(),
            'logging': self.logging.dict()
        }
    
    def save_to_json(self, config_file: str) -> None:
        """Save configuration to JSON file (excluding sensitive data)"""
        try:
            config_dict = self.to_dict()
            with open(config_file, 'w') as f:
                json.dump(config_dict, f, indent=2)
            logger.info(f"Configuration saved to {config_file}")
        except Exception as e:
            logger.error(f"Failed to save configuration to {config_file}: {e}")

# Global configuration instance
config = UltronConfig()

# Legacy compatibility - provide Config class for backward compatibility
class Config:
    """Legacy configuration class for backward compatibility"""
    
    def __init__(self):
        self._config = config
    
    def __getattr__(self, name):
        # Map legacy attribute names to new structure
        if name == 'api_key':
            return self._config.api.openai_api_key
        elif name == 'nvidia_api_key':
            return self._config.api.nvidia_api_key
        elif name == 'voice_enabled':
            return self._config.voice.enabled
        else:
            return getattr(self._config, name, None)