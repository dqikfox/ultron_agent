import os
from pathlib import Path
from typing import Dict, Any, Optional
from json import loads as json_loads, dumps as json_dumps, JSONDecodeError
from logging import getLogger, info, error, warning
from uuid import uuid4
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from security_utils import sanitize_log_input, validate_api_key

class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    pass

class Config:
    """Enhanced configuration manager with validation and security features."""

    # Define required and optional configuration keys
    REQUIRED_KEYS = {
        "use_voice": bool,
        "use_vision": bool,
        "use_api": bool,
        "use_gui": bool,
        "llm_model": str
    }

    OPTIONAL_KEYS = {
        "use_pochi": bool,
        "voice_engine": str,
        "stt_engine": str,
        "tts_engine": str,
        "openai_api_key": (str, type(None)),
        "openai_organization": (str, type(None)),
        "openai_project": (str, type(None)),
        "ollama_api_key": (str, type(None)),
        "ollama_base_url": str,
        "elevenlabs_api_key": (str, type(None)),
        "supabase_url": (str, type(None)),
        "supabase_anon_key": (str, type(None)),
        "gemini_api_key": (str, type(None)),
        "jwt_secret": (str, type(None)),
        "elevenlabs_agent_id": (str, type(None)),
        "pochi_config_path": str,
        "anthropic_api_key": (str, type(None)),
        "voice_boot_message": str,
        "log_level": str,
        "cache_enabled": bool,
        "max_cache_size": int,
        "session_timeout": int
    }

    DEFAULT_VALUES = {
        "ollama_base_url": "http://localhost:11434",
        "voice_boot_message": "There's No Strings On Me",
        "log_level": "INFO",
        "cache_enabled": True,
        "max_cache_size": 1000,
        "session_timeout": 3600,
        "pochi_config_path": "pochi_config.yaml"
    }

    def __init__(self, path: str = "ultron_config.json"):
        self.config_path = Path(path)
        self.data: Dict[str, Any] = {}
        self._sensitive_keys = {
            "openai_api_key", "ollama_api_key", "elevenlabs_api_key",
            "supabase_anon_key", "gemini_api_key", "jwt_secret",
            "anthropic_api_key", "logflare_api_key", "logflare_logger_backend_api_key"
        }

        try:
            # Load environment variables first
            load_dotenv()

            # Load configuration file
            self.load_config()

            # Load environment variables (they override config file)
            self.load_env_variables()

            # Apply default values for missing optional keys
            self.apply_defaults()

            # Validate configuration
            self.validate_config()

            info(f"Configuration loaded successfully from {sanitize_log_input(str(self.config_path))}")

        except (FileNotFoundError, JSONDecodeError, PermissionError) as e:
            error(f"Configuration initialization failed: {sanitize_log_input(str(e))}")
            raise ConfigValidationError(f"Configuration initialization failed: {e}")
        except Exception as e:
            error(f"Unexpected configuration error: {sanitize_log_input(str(e))}")
            raise

    def load_config(self) -> None:
        """Load configuration from JSON file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.data = json_loads(f.read())
                info(f"Configuration file loaded: {sanitize_log_input(str(self.config_path))}")
            except JSONDecodeError as e:
                error_msg = f"Invalid JSON in configuration file {self.config_path}: {e}"
                error(sanitize_log_input(error_msg))
                raise ConfigValidationError(error_msg)
            except (PermissionError, OSError) as e:
                error_msg = f"Cannot access configuration file {self.config_path}: {e}"
                error(sanitize_log_input(error_msg))
                raise ConfigValidationError(error_msg)
        else:
            # Create default config if it doesn't exist
            warning(f"Configuration file {sanitize_log_input(str(self.config_path))} not found, creating default")
            self.create_default_config()

    def create_default_config(self) -> None:
        """Create a default configuration file."""
        default_config = {
            "use_voice": True,
            "use_vision": True,
            "use_api": True,
            "use_gui": True,
            "use_pochi": False,
            "voice_engine": "pyttsx3",
            "stt_engine": "whisper",
            "tts_engine": "pyttsx3",
            "llm_model": "llama3.2:latest",
            **self.DEFAULT_VALUES
        }

        # Add null values for API keys (to be filled by user)
        for key in self.OPTIONAL_KEYS:
            if key.endswith('_key') or key.endswith('_secret'):
                default_config[key] = None

        self.data = default_config
        self.save_config()

    def save_config(self) -> None:
        """Save current configuration to file with proper error handling."""
        backup_path = None
        try:
            # Create backup of existing config
            if self.config_path.exists():
                backup_path = self.config_path.with_suffix('.json.bak')
                self.config_path.rename(backup_path)

            # Write new config
            with open(self.config_path, 'w', encoding='utf-8') as f:
                f.write(json_dumps(self.data, indent=2, ensure_ascii=False))

            info(f"Configuration saved to {sanitize_log_input(str(self.config_path))}")

            # Remove backup if successful
            if backup_path and backup_path.exists():
                backup_path.unlink()

        except (PermissionError, OSError) as e:
            # Restore backup if write failed
            if backup_path and backup_path.exists():
                try:
                    backup_path.rename(self.config_path)
                except OSError:
                    pass
            error_msg = f"Failed to save configuration: {e}"
            error(sanitize_log_input(error_msg))
            raise ConfigValidationError(error_msg)

    def load_env_variables(self) -> None:
        """Load configuration from environment variables with enhanced security."""
        env_mappings = {
            "OPENAI_API_KEY": "openai_api_key",
            "OPENAI_ORGANIZATION": "openai_organization",
            "OPENAI_PROJECT": "openai_project",
            "OLLAMA_API_KEY": "ollama_api_key",
            "OLLAMA_BASE_URL": "ollama_base_url",
            "ELEVENLABS_API_KEY": "elevenlabs_api_key",
            "ELEVENLABS_AGENT_ID": "elevenlabs_agent_id",
            "GEMINI_API_KEY": "gemini_api_key",
            "SUPABASE_URL": "supabase_url",
            "SUPABASE_ANON_KEY": "supabase_anon_key",
            "JWT_SECRET": "jwt_secret",
            "ANTHROPIC_API_KEY": "anthropic_api_key",
            "LOGFLARE_LOGGER_BACKEND_API_KEY": "logflare_logger_backend_api_key",
            "LOGFLARE_API_KEY": "logflare_api_key",
            "GOOGLE_APPLICATION_CREDENTIALS": "google_application_credentials",
            "POCHI_CONFIG_PATH": "pochi_config_path",
            "VOICE_BOOT_MESSAGE": "voice_boot_message",
            "LOG_LEVEL": "log_level"
        }

        loaded_count = 0
        for env_key, config_key in env_mappings.items():
            if value := os.getenv(env_key):
                # Validate sensitive keys
                if config_key in self._sensitive_keys and not validate_api_key(value):
                    warning(f"Invalid or suspicious value for {sanitize_log_input(config_key)}")

                self.data[config_key] = value.strip()
                loaded_count += 1

                # Special handling for Google credentials
                if env_key == "GOOGLE_APPLICATION_CREDENTIALS":
                    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = value

        info(f"Loaded {loaded_count} environment variables into configuration")

    def apply_defaults(self) -> None:
        """Apply default values for missing optional configuration keys."""
        from logging import debug
        for key, default_value in self.DEFAULT_VALUES.items():
            if key not in self.data or self.data[key] is None:
                self.data[key] = default_value
                debug(f"Applied default value for {key}: {default_value}")

    def validate_config(self) -> None:
        """Validate configuration against schema."""
        errors = []

        # Check required keys
        for key, expected_type in self.REQUIRED_KEYS.items():
            if key not in self.data:
                errors.append(f"Missing required key: {key}")
            elif not isinstance(self.data[key], expected_type):
                errors.append(f"Invalid type for {key}: expected {expected_type.__name__}, got {type(self.data[key]).__name__}")

        # Check optional keys
        for key, expected_types in self.OPTIONAL_KEYS.items():
            if key in self.data and self.data[key] is not None:
                if isinstance(expected_types, tuple):
                    if not isinstance(self.data[key], expected_types):
                        type_names = [t.__name__ for t in expected_types]
                        errors.append(f"Invalid type for {key}: expected {' or '.join(type_names)}, got {type(self.data[key]).__name__}")
                else:
                    if not isinstance(self.data[key], expected_types):
                        errors.append(f"Invalid type for {key}: expected {expected_types.__name__}, got {type(self.data[key]).__name__}")

        # Specific validations
        if self.data.get("max_cache_size", 0) <= 0:
            errors.append("max_cache_size must be positive")

        if self.data.get("session_timeout", 0) <= 0:
            errors.append("session_timeout must be positive")

        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
            error(f"{error_msg}")
            raise ConfigValidationError(error_msg)

        info("Configuration validation passed")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with optional default."""
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value with validation."""
        # Basic type checking for known keys
        all_keys = {**self.REQUIRED_KEYS, **self.OPTIONAL_KEYS}
        if key in all_keys:
            expected_type = all_keys[key]
            if isinstance(expected_type, tuple):
                if not isinstance(value, expected_type):
                    raise ValueError(f"Invalid type for {key}: expected {expected_type}, got {type(value).__name__}")
            else:
                if not isinstance(value, expected_type) and value is not None:
                    raise ValueError(f"Invalid type for {key}: expected {expected_type.__name__}, got {type(value).__name__}")

        self.data[key] = value
        logging.info(f"Configuration key '{key}' updated - config.py:270")

    def get_sanitized_data(self) -> Dict[str, Any]:
        """Get configuration data with sensitive values masked."""
        sanitized = self.data.copy()
        for key in self._sensitive_keys:
            if key in sanitized and sanitized[key]:
                sanitized[key] = "*" * 8 + sanitized[key][-4:] if len(str(sanitized[key])) > 4 else "*" * 8
        return sanitized

    def has_valid_api_keys(self) -> Dict[str, bool]:
        """Check which API services have valid keys configured."""
        return {
            "openai": bool(self.data.get("openai_api_key")),
            "ollama": True,  # Ollama doesn't require API key for local use
            "elevenlabs": bool(self.data.get("elevenlabs_api_key")),
            "gemini": bool(self.data.get("gemini_api_key")),
            "supabase": bool(self.data.get("supabase_url") and self.data.get("supabase_anon_key")),
            "anthropic": bool(self.data.get("anthropic_api_key"))
        }

    def __str__(self) -> str:
        """String representation of configuration (sanitized)."""
        return json.dumps(self.get_sanitized_data(), indent=2)

    def __repr__(self) -> str:
        """Developer representation of configuration."""
        return f"Config(path='{self.config_path}', keys={len(self.data)})"
