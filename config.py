"""
Configuration management for Ultron Agent 2.

This module provides configuration loading, validation, and access
for all components of the Ultron Agent system.
"""

import json
import os
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    pass


class ValidationSeverity(Enum):
    """Severity levels for configuration validation issues."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """Represents a configuration validation issue."""
    field: str
    message: str
    severity: ValidationSeverity
    suggested_value: Optional[Any] = None


class ConfigSchema:
    """JSON Schema-based configuration validation."""

    # Define the complete configuration schema
    SCHEMA = {
        "type": "object",
        "properties": {
            # Core system settings
            "use_voice": {"type": "boolean"},
            "use_vision": {"type": "boolean"},
            "use_api": {"type": "boolean"},
            "use_gui": {"type": "boolean"},
            "debug": {"type": "boolean"},
            "log_level": {
                "type": "string",
                "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            },
            "offline_mode": {"type": "boolean"},

            # Voice settings
            "voice_enabled": {"type": "boolean"},
            "voice_engine": {
                "type": "string",
                "enum": ["elevenlabs", "pyttsx3", "openai"]
            },
            "stt_engine": {
                "type": "string",
                "enum": ["whisper", "google", "sphinx", "elevenlabs"]
            },
            "tts_engine": {
                "type": "string",
                "enum": ["elevenlabs", "pyttsx3", "openai"]
            },
            "voice_rate": {
                "type": "number",
                "minimum": 50,
                "maximum": 400
            },
            "voice_volume": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 1.0
            },
            "voice_stability": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 1.0
            },
            "voice_similarity": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 1.0
            },
            "voice_cache_dir": {"type": "string"},
            "mic_energy_threshold": {
                "type": "number",
                "minimum": 0,
                "maximum": 4000
            },
            "disable_tts_cache": {"type": "boolean"},
            "microphone_device_index": {
                "type": ["number", "null"],
                "minimum": 0
            },

            # AI/ML settings
            "llm_model": {"type": "string"},
            "ollama_base_url": {"type": "string"},
            "max_concurrent_requests": {
                "type": "integer",
                "minimum": 1,
                "maximum": 100
            },

            # GUI settings
            "gui_enabled": {"type": "boolean"},
            "gui_theme": {"type": "string"},
            "gui_width": {
                "type": "integer",
                "minimum": 400,
                "maximum": 3840
            },
            "gui_height": {
                "type": "integer",
                "minimum": 300,
                "maximum": 2160
            },

            # Server settings
            "api_host": {"type": "string"},
            "api_port": {
                "type": "integer",
                "minimum": 1024,
                "maximum": 65535
            },

            # Feature flags
            "vision_enabled": {"type": "boolean"},
            "memory_enabled": {"type": "boolean"},
            "tools_enabled": {"type": "boolean"},
            "enable_audit_logging": {"type": "boolean"},
            "enable_maverick": {"type": "boolean"},
            "maverick_analysis_interval": {
                "type": "number",
                "minimum": 1,
                "maximum": 3600
            },
            "maverick_auto_apply": {"type": "boolean"},

            # Integration settings
            "use_pochi": {"type": "boolean"},
            "autogen_studio_enabled": {"type": "boolean"},
            "autogen_studio_port": {
                "type": "integer",
                "minimum": 1024,
                "maximum": 65535
            },
            "autogen_studio_host": {"type": "string"},
            "autogen_studio_database_url": {"type": "string"},
            "autogen_studio_default_llm": {"type": "string"},
            "autogen_studio_max_agents": {
                "type": "integer",
                "minimum": 1,
                "maximum": 100
            },
            "autogen_studio_session_timeout": {
                "type": "number",
                "minimum": 60,
                "maximum": 86400
            },

            "langflow_enabled": {"type": "boolean"},
            "langflow_host": {"type": "string"},
            "langflow_port": {
                "type": "integer",
                "minimum": 1024,
                "maximum": 65535
            },
            "langflow_api_url": {"type": "string"},

            "langchain_enabled": {"type": "boolean"},
            "langchain_default_model": {"type": "string"},
            "langchain_temperature": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 2.0
            },
            "langchain_max_tokens": {
                "type": "integer",
                "minimum": 1,
                "maximum": 32768
            },
            "langchain_verbose": {"type": "boolean"}
        },
        "additionalProperties": True  # Allow custom properties
    }

    @classmethod
    def validate_config(cls, config: Dict[str, Any]) -> List[ValidationIssue]:
        """
        Validate configuration against schema.

        Args:
            config: Configuration dictionary to validate

        Returns:
            List of validation issues found
        """
        issues = []

        # Validate each field in the schema
        for field, field_schema in cls.SCHEMA.get("properties", {}).items():
            if field in config:
                issue = cls._validate_field(field, config[field], field_schema)
                if issue:
                    issues.append(issue)

        # Check for logical consistency
        issues.extend(cls._validate_logical_consistency(config))

        return issues

    @classmethod
    def _validate_field(cls, field: str, value: Any,
                       schema: Dict[str, Any]) -> Optional[ValidationIssue]:
        """Validate a single field against its schema."""
        field_type = schema.get("type")

        # Handle union types (e.g., ["number", "null"])
        if isinstance(field_type, list):
            if value is None and "null" in field_type:
                return None
            # Try each type
            for t in field_type:
                if t != "null":
                    temp_schema = schema.copy()
                    temp_schema["type"] = t
                    if not cls._validate_field_type(value, temp_schema):
                        continue
                    return None
            return ValidationIssue(
                field=field,
                message=f"Value must be one of types: {field_type}",
                severity=ValidationSeverity.ERROR
            )

        # Validate single type
        if not cls._validate_field_type(value, schema):
            expected_type = field_type
            if isinstance(field_type, list):
                expected_type = " or ".join(field_type)
            return ValidationIssue(
                field=field,
                message=f"Expected {expected_type}, got "
                        f"{type(value).__name__}",
                severity=ValidationSeverity.ERROR
            )

        # Validate constraints
        if field_type == "number" or field_type == "integer":
            min_val = schema.get("minimum")
            max_val = schema.get("maximum")
            if min_val is not None and value < min_val:
                return ValidationIssue(
                    field=field,
                    message=f"Value {value} is below minimum {min_val}",
                    severity=ValidationSeverity.ERROR,
                    suggested_value=min_val
                )
            if max_val is not None and value > max_val:
                return ValidationIssue(
                    field=field,
                    message=f"Value {value} exceeds maximum {max_val}",
                    severity=ValidationSeverity.ERROR,
                    suggested_value=max_val
                )

        # Validate enum values
        enum_values = schema.get("enum")
        if enum_values and value not in enum_values:
            return ValidationIssue(
                field=field,
                message=f"Value '{value}' not in allowed values: "
                        f"{enum_values}",
                severity=ValidationSeverity.ERROR,
                suggested_value=enum_values[0]
            )

        return None

    @classmethod
    def _validate_field_type(cls, value: Any, schema: Dict[str, Any]) -> bool:
        """Validate field type matches schema."""
        field_type = schema.get("type")

        if field_type == "string":
            return isinstance(value, str)
        elif field_type == "number":
            return isinstance(value, (int, float))
        elif field_type == "integer":
            return isinstance(value, int)
        elif field_type == "boolean":
            return isinstance(value, bool)
        elif field_type == "object":
            return isinstance(value, dict)
        elif field_type == "array":
            return isinstance(value, list)

        return True  # Unknown type, allow

    @classmethod
    def _validate_logical_consistency(cls, config: Dict[str, Any]
                                     ) -> List[ValidationIssue]:
        """Validate logical consistency between configuration values."""
        issues = []

        # Voice engine consistency
        if config.get("voice_enabled"):
            voice_engine = config.get("voice_engine")
            if voice_engine == "elevenlabs":
                # Check if ElevenLabs settings are reasonable
                stability = config.get("voice_stability", 0.5)
                if not (0.0 <= stability <= 1.0):
                    issues.append(ValidationIssue(
                        field="voice_stability",
                        message="Voice stability must be between 0.0 and 1.0",
                        severity=ValidationSeverity.ERROR,
                        suggested_value=0.5
                    ))

        # Port conflicts
        ports = []
        port_fields = [
            ("api_port", "API server"),
            ("autogen_studio_port", "AutoGen Studio"),
            ("langflow_port", "Langflow")
        ]

        for field, service in port_fields:
            port = config.get(field)
            if port:
                if port in [p["port"] for p in ports]:
                    issues.append(ValidationIssue(
                        field=field,
                        message=f"Port {port} conflicts with another service",
                        severity=ValidationSeverity.ERROR
                    ))
                else:
                    ports.append({"port": port, "service": service, "field": field})

        # Model URL validation
        ollama_url = config.get("ollama_base_url", "")
        if ollama_url and not ollama_url.startswith(("http://", "https://")):
            issues.append(ValidationIssue(
                field="ollama_base_url",
                message="Ollama URL must start with http:// or https://",
                severity=ValidationSeverity.ERROR,
                suggested_value="http://localhost:11434"
            ))

        return issues


class Config:
    """Configuration manager for Ultron Agent."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration from the specified path or default locations.

        Args:
            config_path: Optional path to configuration file. If not provided,
                         will search in default locations.
        """
        self.logger = logging.getLogger(__name__)
        self._config_data = {}

        # Default configuration
        self._config_data = {
            "version": "3.0.0",
            "app_name": "Ultron Agent",
            "debug_mode": False,
            "log_level": "INFO",
            "servers": {
                "nvidia_ai": {
                    "enabled": True,
                    "host": "localhost",
                    "port": 8000
                },
                "web_gui": {
                    "enabled": True,
                    "host": "localhost",
                    "port": 8080
                },
                "api": {
                    "enabled": True,
                    "host": "localhost",
                    "port": 5000
                }
            },
            "gui": {
                "enabled": True,
                "type": "pokedex",  # Options: pokedex, web, electron, cli
                "theme": "dark"
            },
            "memory": {
                "short_term_limit": 10,
                "long_term_file": "long_term_memory.json",
                "use_google_drive": False
            },
            "voice": {
                "enabled": False,
                "engine": "pyttsx3",  # Options: pyttsx3, elevenlabs
                "recognition": "google"  # Options: google, whisper
            },
            # API Keys - loaded from environment variables
            "api_keys": {
                "openai": os.getenv("OPENAI_API_KEY", ""),
                "anthropic": os.getenv("ANTHROPIC_APIKEY", ""),
                "elevenlabs": os.getenv("ELEVENLABS_API_KEY", ""),
                "elevenlabs_agent_id": os.getenv("ELEVENLABS_AGENT_ID", ""),
                "gemini": os.getenv("GEMINI_API_KEY", ""),
                "google": os.getenv("GOOGLE_API_KEY_ULTRON", ""),
                "mistral": os.getenv("MISTRAL_API_KEY", ""),
                "nvidia": os.getenv("NVIDIA_API_KEY", ""),
                "ollama": os.getenv("OLLAMA_API_KEY", ""),
                "groq": os.getenv("GROQ_API_KEY", ""),
                "deepseek": os.getenv("DEEPSEEK_API_KEY", ""),
                "together": os.getenv("TOGETHER_API_KEY", ""),
                "paperspace": os.getenv("PAPERSPACES_API_KEY", ""),
                "supabase_url": os.getenv("SUPABASE_URL", ""),
                "supabase_anon_key": os.getenv("SUPABASE_ANON_KEY", ""),
                "supabase_service_role": os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
                "jwt_secret": os.getenv("JWT_SECRET", ""),
                "logflare_api": os.getenv("LOGFLARE_API_KEY", ""),
                "logflare_backend": os.getenv("LOGFLARE_LOGGER_BACKEND_API_KEY", ""),
                "postman": os.getenv("POSTMAN_API", ""),
                "petshop": os.getenv("PETSHOP_APIKEY", ""),
                "codegpt": os.getenv("CODEGTP_API_KEY", "")
            }
        }

        # Load configuration from file if provided
        if config_path:
            self._load_config(config_path)
        else:
            # Try default locations
            default_locations = [
                "ultron_config.json",
                os.path.expanduser("~/.ultron/config.json"),
                "/etc/ultron/config.json"
            ]

            for location in default_locations:
                if os.path.exists(location):
                    self._load_config(location)
                    break

        # Validate configuration after loading
        self._validate_configuration()

        # Validate API keys after loading
        self._validate_api_keys()

    def _validate_configuration(self):
        """Validate configuration against schema and logical consistency."""
        try:
            issues = ConfigSchema.validate_config(self._config_data)

            if issues:
                # Group issues by severity
                errors = [i for i in issues if i.severity == ValidationSeverity.ERROR]
                warnings = [i for i in issues if i.severity == ValidationSeverity.WARNING]
                infos = [i for i in issues if i.severity == ValidationSeverity.INFO]

                # Log errors
                if errors:
                    self.logger.error("Configuration validation errors found:")
                    for issue in errors:
                        self.logger.error(f"  {issue.field}: {issue.message}")
                        if issue.suggested_value is not None:
                            self.logger.error(f"    Suggested: {issue.suggested_value}")

                # Log warnings
                if warnings:
                    self.logger.warning("Configuration validation warnings:")
                    for issue in warnings:
                        self.logger.warning(f"  {issue.field}: {issue.message}")

                # Log info
                if infos:
                    for issue in infos:
                        self.logger.info(f"Config info - {issue.field}: {issue.message}")

                # If there are errors, raise exception
                if errors:
                    error_messages = [f"{e.field}: {e.message}" for e in errors]
                    raise ConfigValidationError(
                        "Configuration validation failed:\n" +
                        "\n".join(f"  - {msg}" for msg in error_messages)
                    )

        except Exception as e:
            if isinstance(e, ConfigValidationError):
                raise
            self.logger.error(f"Configuration validation error: {e}")
            # Don't fail on validation errors in production, just log
            if os.getenv("STRICT_CONFIG_VALIDATION", "false").lower() == "true":
                raise ConfigValidationError(f"Configuration validation failed: {e}")

    def _validate_api_keys(self):
        """Validate that required API keys are available."""
        required_keys = ["openai", "elevenlabs", "ollama"]
        missing_keys = []

        for key in required_keys:
            if not self._config_data["api_keys"].get(key):
                missing_keys.append(key.upper())

        if missing_keys:
            self.logger.warning(f"Missing required API keys: {', '.join(missing_keys)}")
            self.logger.info("Please set these as environment variables or in ultron_config.json")

        # Log available keys (without values for security)
        available_keys = [k for k, v in self._config_data["api_keys"].items() if v]
        if available_keys:
            self.logger.info(f"Available API keys: {', '.join(available_keys)}")

    def get_api_key(self, service: str) -> Optional[str]:
        """Get API key for a specific service.

        Args:
            service: Service name (e.g., 'openai', 'elevenlabs')

        Returns:
            API key if available, None otherwise
        """
        return self._config_data["api_keys"].get(service)

    def set_api_key(self, service: str, key: str):
        """Set API key for a specific service.

        Args:
            service: Service name
            key: API key value
        """
        self._config_data["api_keys"][service] = key
        self.logger.info(f"Updated API key for {service}")

    def get_available_services(self) -> List[str]:
        """Get list of services with available API keys.

        Returns:
            List of service names with valid API keys
        """
        return [service for service, key in self._config_data["api_keys"].items() if key]

    def _load_config(self, config_path: str) -> None:
        """Load configuration from the specified file.

        Args:
            config_path: Path to configuration file.
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                # Update default config with file config
                self._update_dict(self._config_data, file_config)
                self.logger.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            self.logger.error(f"Failed to load configuration from {config_path}: {e}")

    def _update_dict(self, target: Dict, source: Dict) -> None:
        """Recursively update a dictionary with another dictionary.

        Args:
            target: Target dictionary to update.
            source: Source dictionary with new values.
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._update_dict(target[key], value)
            else:
                target[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key.

        Args:
            key: Configuration key, can use dot notation for nested keys.
            default: Default value to return if key not found.

        Returns:
            Configuration value or default if not found.
        """
        keys = key.split('.')
        value = self._config_data

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.

        Args:
            key: Configuration key, can use dot notation for nested keys.
            value: Value to set.
        """
        keys = key.split('.')
        config = self._config_data

        for i, k in enumerate(keys[:-1]):
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def save(self, config_path: str) -> None:
        """Save configuration to file.

        Args:
            config_path: Path to save configuration file.
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)

            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config_data, f, indent=2)

            self.logger.info(f"Saved configuration to {config_path}")
        except Exception as e:
            self.logger.error(f"Failed to save configuration to {config_path}: {e}")

    @property
    def data(self) -> Dict:
        """Get a copy of the entire configuration.

        Returns:
            Copy of configuration dictionary.
        """
        return self._config_data.copy()

    def validate(self) -> List[ValidationIssue]:
        """Validate current configuration and return any issues found.

        Returns:
            List of validation issues (errors, warnings, info)
        """
        return ConfigSchema.validate_config(self._config_data)

    def get_validation_summary(self) -> Dict[str, int]:
        """Get a summary of validation issues by severity.

        Returns:
            Dictionary with counts of errors, warnings, and info issues
        """
        issues = self.validate()
        return {
            "errors": len([i for i in issues
                          if i.severity == ValidationSeverity.ERROR]),
            "warnings": len([i for i in issues
                            if i.severity == ValidationSeverity.WARNING]),
            "info": len([i for i in issues
                        if i.severity == ValidationSeverity.INFO]),
            "total": len(issues)
        }

    def is_valid(self) -> bool:
        """Check if configuration is valid (no errors).

        Returns:
            True if no validation errors, False otherwise
        """
        issues = self.validate()
        return not any(i.severity == ValidationSeverity.ERROR for i in issues)
