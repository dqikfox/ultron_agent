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


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    pass


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