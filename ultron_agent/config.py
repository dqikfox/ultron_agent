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

# Import secrets manager for secure API key handling
try:
    from utils.secrets_manager import SecretsManager
    SECRETS_MANAGER_AVAILABLE = True
    logger.debug("Secrets manager imported successfully")
except ImportError as e:
    logger.warning(f"Secrets manager not available: {e}. Using fallback methods.")
    SECRETS_MANAGER_AVAILABLE = False


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

    # AutoGen Studio integration settings
    autogen_studio_enabled: bool = Field(
        default=False, description="Enable AutoGen Studio integration"
    )
    autogen_studio_port: int = Field(
        default=8081, ge=1024, le=65535,
        description="AutoGen Studio server port"
    )
    autogen_studio_host: str = Field(
        default="127.0.0.1", description="AutoGen Studio server host"
    )
    autogen_studio_database_url: str = Field(
        default="sqlite:///autogen_studio.db",
        description="AutoGen Studio database URL"
    )
    autogen_studio_default_llm: str = Field(
        default="gpt-4", description="Default LLM for AutoGen Studio"
    )
    autogen_studio_max_agents: int = Field(
        default=10, ge=1, le=50,
        description="Maximum number of agents in AutoGen Studio"
    )
    autogen_studio_session_timeout: int = Field(
        default=3600, ge=300, le=86400,
        description="AutoGen Studio session timeout (seconds)"
    )

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

    def get_secure_api_key(self, key_name: str, env_var: str = None) -> Optional[str]:
        """
        Get API key securely using secrets manager, with fallback to environment.

        Args:
            key_name: Name of the secret in the secrets manager
            env_var: Environment variable name for fallback

        Returns:
            API key if found, None otherwise
        """
        if SECRETS_MANAGER_AVAILABLE:
            try:
                secrets_manager = SecretsManager()
                if secrets_manager.secret_exists(key_name):
                    return secrets_manager.get_secret(key_name)
                logger.debug(f"Secret '{key_name}' not found in secrets manager")
            except Exception as e:
                logger.warning(f"Failed to retrieve secret '{key_name}': {e}")

        # Fallback to environment variable
        if env_var:
            value = os.getenv(env_var)
            if value:
                logger.debug(f"Loaded {key_name} from environment variable {env_var}")
                return value

        return None

    def store_secure_api_key(self, key_name: str, value: str, description: str = None) -> bool:
        """
        Store API key securely using secrets manager.

        Args:
            key_name: Name of the secret
            value: API key value
            description: Optional description

        Returns:
            True if stored successfully, False otherwise
        """
        if not SECRETS_MANAGER_AVAILABLE:
            logger.warning("Secrets manager not available, cannot store secure API key")
            return False

        try:
            secrets_manager = SecretsManager()
            secrets_manager.store_secret(key_name, value, description or f"API key for {key_name}")
            logger.info(f"Successfully stored secure API key: {key_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to store secure API key '{key_name}': {e}")
            return False

    def migrate_api_keys_to_secrets(self) -> Dict[str, bool]:
        """
        Migrate existing API keys from environment/config to secrets manager.

        Returns:
            Dictionary mapping key names to migration success status
        """
        if not SECRETS_MANAGER_AVAILABLE:
            logger.warning("Secrets manager not available, cannot migrate API keys")
            return {}

        migration_results = {}
        secrets_manager = SecretsManager()

        # API key mappings
        key_mappings = {
            'openai_api_key': ('OPENAI_API_KEY', 'OpenAI API key for GPT models'),
            'elevenlabs_api_key': ('ELEVENLABS_API_KEY', 'ElevenLabs API key for voice synthesis'),
            'elevenlabs_agent_id': ('ELEVENLABS_AGENT_ID', 'ElevenLabs agent/voice ID'),
            'nvidia_api_key': ('NVIDIA_API_KEY', 'NVIDIA NIM API key'),
            'together_api_key': ('TOGETHER_API_KEY', 'Together.xyz API key'),
        }

        for config_field, (env_var, description) in key_mappings.items():
            try:
                # Check if we have the key from current config or environment
                current_value = getattr(self, config_field, None) or os.getenv(env_var)

                if current_value and not secrets_manager.secret_exists(config_field):
                    # Store in secrets manager
                    success = self.store_secure_api_key(config_field, current_value, description)
                    migration_results[config_field] = success

                    if success:
                        # Clear from current config to avoid plaintext storage
                        setattr(self, config_field, None)
                        logger.info(f"Migrated {config_field} to secrets manager")
                    else:
                        logger.error(f"Failed to migrate {config_field}")
                else:
                    migration_results[config_field] = True  # Already migrated or no value

            except Exception as e:
                logger.error(f"Error migrating {config_field}: {e}")
                migration_results[config_field] = False

        return migration_results

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
        """Load API keys from secrets manager or environment if not provided."""
        # Map of config field to environment variable and secret name
        key_mappings = {
            'openai_api_key': ('OPENAI_API_KEY', 'openai_api_key'),
            'elevenlabs_api_key': ('ELEVENLABS_API_KEY', 'elevenlabs_api_key'),
            'elevenlabs_agent_id': ('ELEVENLABS_AGENT_ID', 'elevenlabs_agent_id'),
            'nvidia_api_key': ('NVIDIA_API_KEY', 'nvidia_api_key'),
            'together_api_key': ('TOGETHER_API_KEY', 'together_api_key'),
        }

        for field, (env_var, secret_name) in key_mappings.items():
            if not values.get(field):
                # Try secrets manager first
                if SECRETS_MANAGER_AVAILABLE:
                    try:
                        secrets_manager = SecretsManager()
                        if secrets_manager.secret_exists(secret_name):
                            values[field] = secrets_manager.get_secret(secret_name)
                            logger.debug(f"Loaded {field} from secrets manager")
                            continue
                    except Exception as e:
                        logger.warning(f"Failed to load {field} from secrets manager: {e}")

                # Fallback to environment variable
                if os.getenv(env_var):
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

    # Backward compatibility methods for existing code
    def get(self, key: str, default=None):
        """Get configuration value by key (backward compatibility)."""
        return getattr(self, key, default)

    @property
    def data(self):
        """Dictionary representation for backward compatibility."""
        return self.dict()


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
    # Load environment variables from .env file
    from dotenv import load_dotenv
    load_dotenv()

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

    API keys are stored securely in the secrets manager and should not be saved
    in plaintext configuration files. Use config.store_secure_api_key() to store
    API keys securely.

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


def migrate_api_keys_to_secrets_manager(config_path: Optional[Path] = None) -> Dict[str, bool]:
    """
    Utility function to migrate existing API keys to the secrets manager.

    This function loads the current configuration, checks for API keys in environment
    variables or config file, and migrates them to the secure secrets manager.

    Args:
        config_path: Path to config file (optional)

    Returns:
        Dictionary mapping key names to migration success status
    """
    try:
        config = load_config(config_path)
        return config.migrate_api_keys_to_secrets()
    except Exception as e:
        logger.error(f"Failed to migrate API keys: {e}")
        return {}


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
