"""Configuration models and validation for Ultron Agent."""
from __future__ import annotations

import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator, root_validator
from enum import Enum

logger = logging.getLogger(__name__)


class LogLevel(str, Enum):
    """Supported logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class VoiceEngine(str, Enum):
    """Supported voice engines in priority order."""
    ELEVENLABS = "elevenlabs"
    PYTTSX3 = "pyttsx3"
    OPENAI = "openai"
    CONSOLE = "console"


class ModelProvider(str, Enum):
    """Supported AI model providers."""
    OLLAMA = "ollama"
    OPENAI = "openai"
    NVIDIA = "nvidia"
    TOGETHER = "together"


class UltronConfig(BaseModel):
    """Main configuration model for Ultron Agent."""

    # Core settings
    app_name: str = Field(default="Ultron Agent", description="Application name")
    version: str = Field(default="3.0.0", description="Application version")
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")

    # API server settings
    api_host: str = Field(default="127.0.0.1", description="API server host")
    api_port: int = Field(default=5000, ge=1024, le=65535, description="API server port")
    api_reload: bool = Field(default=False, description="Auto-reload API server")

    # Voice settings
    voice_engine: VoiceEngine = Field(default=VoiceEngine.ELEVENLABS, description="Primary voice engine")
    voice_fallback_chain: List[VoiceEngine] = Field(
        default_factory=lambda: [VoiceEngine.ELEVENLABS, VoiceEngine.PYTTSX3, VoiceEngine.CONSOLE],
        description="Voice engine fallback order"
    )
    voice_rate: int = Field(default=180, ge=50, le=400, description="Speech rate (words per minute)")
    voice_volume: float = Field(default=0.9, ge=0.0, le=1.0, description="Speech volume")
    listen_timeout: int = Field(default=10, ge=1, le=60, description="Voice listen timeout (seconds)")

    # AI model settings
    default_model_provider: ModelProvider = Field(default=ModelProvider.OLLAMA, description="Default AI provider")
    default_model_name: str = Field(default="qwen2.5-coder:latest", description="Default model name")
    ollama_base_url: str = Field(default="http://localhost:11434", description="Ollama server URL")
    model_switch_timeout: int = Field(default=30, ge=5, le=120, description="Model switch timeout")
    max_context_length: int = Field(default=4096, ge=512, le=32768, description="Max context tokens")

    # GUI settings
    gui_enabled: bool = Field(default=True, description="Enable GUI")
    gui_theme: str = Field(default="cyberpunk", description="GUI theme")
    gui_width: int = Field(default=1200, ge=800, le=2560, description="GUI window width")
    gui_height: int = Field(default=800, ge=600, le=1440, description="GUI window height")

    # Security settings
    enable_api_auth: bool = Field(default=False, description="Enable API authentication")
    enable_audit_logging: bool = Field(default=True, description="Enable audit logging")
    offline_mode: bool = Field(default=False, description="Offline mode (no external network)")
    telemetry_enabled: bool = Field(default=False, description="Enable telemetry collection")

    # Performance settings
    max_concurrent_requests: int = Field(default=10, ge=1, le=100, description="Max concurrent API requests")
    vram_safety_margin_gb: float = Field(default=1.0, ge=0.5, le=4.0, description="VRAM safety margin")
    circuit_breaker_threshold: int = Field(default=5, ge=3, le=20, description="Failure threshold for circuit breaker")

    # Agent component settings
    voice_enabled: bool = Field(default=True, description="Enable voice system")
    vision_enabled: bool = Field(default=True, description="Enable vision system")
    memory_enabled: bool = Field(default=True, description="Enable memory system")
    tools_enabled: bool = Field(default=True, description="Enable tools system")
    
    # Maverick auto-improvement settings
    enable_maverick: bool = Field(default=True, description="Enable Maverick auto-improvement")
    maverick_analysis_interval: int = Field(default=30, ge=5, le=600, description="Maverick analysis interval (minutes)")
    maverick_auto_apply: bool = Field(default=False, description="Auto-apply Maverick suggestions")
    
    # POCHI integration settings
    use_pochi: bool = Field(default=False, description="Enable POCHI integration")
    
    # Voice boot message
    voice_boot_message: str = Field(default="There's No Strings On Me", description="Boot message for voice system")

    # API Keys (loaded from environment)
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    elevenlabs_api_key: Optional[str] = Field(default=None, description="ElevenLabs API key")
    elevenlabs_agent_id: Optional[str] = Field(default=None, description="ElevenLabs agent/voice ID")
    nvidia_api_key: Optional[str] = Field(default=None, description="NVIDIA NIM API key")
    together_api_key: Optional[str] = Field(default=None, description="Together.xyz API key")

    # File paths
    log_directory: Path = Field(default=Path("logs"), description="Log files directory")
    config_file: Path = Field(default=Path("ultron_config.json"), description="Config file path")
    cache_directory: Path = Field(default=Path(".cache"), description="Cache directory")

    class Config:
        """Pydantic config."""
        use_enum_values = True
        validate_assignment = True
        extra = "ignore"  # Ignore extra fields for backward compatibility

    @validator('voice_fallback_chain')
    def validate_fallback_chain(cls, v, values):
        """Ensure fallback chain contains console as final fallback."""
        if VoiceEngine.CONSOLE not in v:
            v.append(VoiceEngine.CONSOLE)
        return v

    @validator('log_directory', 'cache_directory', pre=True)
    def ensure_path(cls, v):
        """Convert string to Path and ensure it's absolute."""
        if isinstance(v, str):
            v = Path(v)
        if not v.is_absolute():
            v = Path.cwd() / v
        return v

    @root_validator(skip_on_failure=True)
    def validate_api_keys(cls, values):
        """Load API keys from environment if not provided."""
        # Map of config field to environment variable
        env_mapping = {
            'openai_api_key': 'OPENAI_API_KEY',
            'elevenlabs_api_key': 'ELEVENLABS_API_KEY',
            'elevenlabs_agent_id': 'ELEVENLABS_AGENT_ID',
            'nvidia_api_key': 'NVIDIA_API_KEY',
            'together_api_key': 'TOGETHER_API_KEY',
        }

        for field, env_var in env_mapping.items():
            if not values.get(field) and os.getenv(env_var):
                values[field] = os.getenv(env_var)
                logger.debug(f"Loaded {field} from environment")

        return values

    def create_directories(self) -> None:
        """Create necessary directories."""
        for directory in [self.log_directory, self.cache_directory]:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created directory: {directory}")

    def sanitized_dict(self) -> Dict[str, Any]:
        """Get config as dict with sensitive values redacted."""
        data = self.dict()
        sensitive_keys = {
            'openai_api_key', 'elevenlabs_api_key', 'nvidia_api_key', 'together_api_key'
        }

        for key in sensitive_keys:
            if data.get(key):
                data[key] = f"{data[key][:8]}...{data[key][-4:]}" if len(data[key]) > 12 else "[REDACTED]"

        return data


def load_config(config_path: Optional[Path] = None) -> UltronConfig:
    """
    Load configuration from file and environment.

    Args:
        config_path: Path to config file (defaults to ultron_config.json)

    Returns:
        Loaded and validated configuration

    Raises:
        ValueError: If configuration is invalid
        FileNotFoundError: If config file is required but missing
    """
    if config_path is None:
        config_path = Path("ultron_config.json")

    config_data = {}

    # Load from file if it exists
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            logger.info(f"Loaded configuration from {config_path}")
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            raise ValueError(f"Invalid configuration file: {e}")
    else:
        logger.info(f"Config file {config_path} not found, using defaults")

    try:
        config = UltronConfig(**config_data)
        config.create_directories()
        logger.info("Configuration validated successfully")
        return config
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        raise ValueError(f"Invalid configuration: {e}")


def save_config(config: UltronConfig, config_path: Optional[Path] = None) -> None:
    """
    Save configuration to file (excluding sensitive values).

    Args:
        config: Configuration to save
        config_path: Path to save to (defaults to config.config_file)
    """
    if config_path is None:
        config_path = config.config_file

    # Create a safe version without API keys
    safe_data = config.dict(exclude={
        'openai_api_key', 'elevenlabs_api_key', 'nvidia_api_key', 'together_api_key'
    })

    try:
        with open(config_path, 'w') as f:
            json.dump(safe_data, f, indent=2, default=str)
        logger.info(f"Configuration saved to {config_path}")
    except IOError as e:
        logger.error(f"Failed to save config to {config_path}: {e}")
        raise


# Global config instance
_config: Optional[UltronConfig] = None


def get_config() -> UltronConfig:
    """Get global configuration instance."""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reload_config(config_path: Optional[Path] = None) -> UltronConfig:
    """Reload configuration from file."""
    global _config
    _config = load_config(config_path)
    return _config
