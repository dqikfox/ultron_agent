#!/usr/bin/env python3
"""
ULTRON Agent 3.0 - Secure Configuration Management
Handles encrypted configuration and sensitive data management
"""

import os
import json
import base64
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)


class SecureConfigManager:
    """Secure configuration manager with encryption support."""
    
    def __init__(self, config_path: str = "ultron_config_secure.json"):
        self.config_path = Path(config_path)
        self.encrypted_path = Path(config_path + ".enc")
        self._cipher_suite: Optional[Fernet] = None
        self._config_cache: Optional[Dict[str, Any]] = None
        
    def _get_encryption_key(self) -> bytes:
        """Generate or retrieve encryption key from environment."""
        # Try to get key from environment
        env_key = os.getenv('ULTRON_SECRET_KEY')
        if env_key:
            # Derive key from environment variable
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'ultron_salt_2024',  # Use a fixed salt for consistency
                iterations=100000,
            )
            return base64.urlsafe_b64encode(kdf.derive(env_key.encode()))
        
        # Generate new key if none exists
        key = Fernet.generate_key()
        logger.warning("Generated new encryption key. Set ULTRON_SECRET_KEY environment variable.")
        return key
        
    def _get_cipher_suite(self) -> Fernet:
        """Get or create cipher suite for encryption/decryption."""
        if self._cipher_suite is None:
            key = self._get_encryption_key()
            self._cipher_suite = Fernet(key)
        return self._cipher_suite
        
    def encrypt_config(self, config_data: Dict[str, Any]) -> bool:
        """Encrypt configuration data to file."""
        try:
            cipher_suite = self._get_cipher_suite()
            
            # Convert config to JSON and encrypt
            json_data = json.dumps(config_data, indent=2).encode()
            encrypted_data = cipher_suite.encrypt(json_data)
            
            # Write encrypted data to file
            with open(self.encrypted_path, 'wb') as f:
                f.write(encrypted_data)
                
            # Create hash for integrity verification
            hash_obj = hashlib.sha256(encrypted_data)
            hash_file = Path(str(self.encrypted_path) + ".hash")
            with open(hash_file, 'w') as f:
                f.write(hash_obj.hexdigest())
                
            logger.info(f"Configuration encrypted and saved to {self.encrypted_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to encrypt configuration: {e}")
            return False
            
    def decrypt_config(self) -> Optional[Dict[str, Any]]:
        """Decrypt configuration data from file."""
        if not self.encrypted_path.exists():
            logger.warning(f"Encrypted config file not found: {self.encrypted_path}")
            return None
            
        try:
            cipher_suite = self._get_cipher_suite()
            
            # Read and verify hash
            hash_file = Path(str(self.encrypted_path) + ".hash")
            if hash_file.exists():
                with open(hash_file, 'r') as f:
                    expected_hash = f.read().strip()
                    
                with open(self.encrypted_path, 'rb') as f:
                    encrypted_data = f.read()
                    
                actual_hash = hashlib.sha256(encrypted_data).hexdigest()
                if expected_hash != actual_hash:
                    logger.error("Configuration file integrity check failed")
                    return None
            else:
                with open(self.encrypted_path, 'rb') as f:
                    encrypted_data = f.read()
            
            # Decrypt and parse JSON
            decrypted_data = cipher_suite.decrypt(encrypted_data)
            config_data = json.loads(decrypted_data.decode())
            
            logger.info("Configuration decrypted successfully")
            return config_data
            
        except Exception as e:
            logger.error(f"Failed to decrypt configuration: {e}")
            return None
            
    def load_config(self, use_cache: bool = True) -> Dict[str, Any]:
        """Load configuration from encrypted file or fallback to plain text."""
        if use_cache and self._config_cache is not None:
            return self._config_cache
            
        # Try encrypted config first
        config = self.decrypt_config()
        
        # Fallback to plain text config
        if config is None and self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                logger.info(f"Loaded plain text configuration from {self.config_path}")
            except Exception as e:
                logger.error(f"Failed to load plain text configuration: {e}")
                config = {}
        
        # Default configuration if nothing found
        if config is None:
            config = self._get_default_config()
            logger.info("Using default configuration")
            
        # Merge with environment variables
        config = self._merge_env_vars(config)
        
        # Cache the configuration
        self._config_cache = config
        return config
        
    def save_config(self, config_data: Dict[str, Any], encrypt: bool = True) -> bool:
        """Save configuration data."""
        try:
            if encrypt:
                # Save as encrypted
                success = self.encrypt_config(config_data)
                if success:
                    # Remove plain text file if encryption succeeded
                    if self.config_path.exists():
                        self.config_path.unlink()
                        logger.info("Removed plain text configuration file")
                return success
            else:
                # Save as plain text
                with open(self.config_path, 'w') as f:
                    json.dump(config_data, f, indent=2)
                logger.info(f"Configuration saved to {self.config_path}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
            
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "environment": "development",
            "logging": {
                "level": "INFO",
                "file": "logs/ultron.log",
                "max_size": "10MB",
                "backup_count": 5
            },
            "security": {
                "secret_key_env": "ULTRON_SECRET_KEY",
                "api_key_timeout": 3600,
                "max_failed_attempts": 5
            },
            "ai": {
                "openai": {
                    "api_key_env": "OPENAI_API_KEY",
                    "model": "gpt-3.5-turbo",
                    "max_tokens": 4096
                },
                "ollama": {
                    "host": "localhost:11434",
                    "model": "llama2"
                }
            },
            "voice": {
                "engine": "pyttsx3",
                "rate": 200,
                "volume": 0.9
            },
            "monitoring": {
                "health_check_enabled": True,
                "metrics_enabled": True,
                "prometheus_port": 9090
            },
            "server": {
                "host": "localhost",
                "port": 8080,
                "debug": False
            }
        }
        
    def _merge_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge environment variables into configuration."""
        env_mappings = {
            "ULTRON_ENV": ["environment"],
            "ULTRON_HOST": ["server", "host"],
            "ULTRON_PORT": ["server", "port"],
            "ULTRON_DEBUG": ["server", "debug"],
            "OPENAI_API_KEY": ["ai", "openai", "api_key"],
            "OLLAMA_HOST": ["ai", "ollama", "host"],
            "LOG_LEVEL": ["logging", "level"],
            "PROMETHEUS_PORT": ["monitoring", "prometheus_port"]
        }
        
        for env_var, config_path in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # Navigate to the correct nested position
                current = config
                for key in config_path[:-1]:
                    if key not in current:
                        current[key] = {}
                    current = current[key]
                
                # Convert value to appropriate type
                final_key = config_path[-1]
                if env_var in ["ULTRON_PORT", "PROMETHEUS_PORT"]:
                    current[final_key] = int(env_value)
                elif env_var in ["ULTRON_DEBUG"]:
                    current[final_key] = env_value.lower() in ['true', '1', 'yes']
                else:
                    current[final_key] = env_value
                    
        return config
        
    def get_sensitive_value(self, key_path: str, default: Any = None) -> Any:
        """Get sensitive value from configuration with proper error handling."""
        try:
            config = self.load_config()
            keys = key_path.split('.')
            
            current = config
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return default
                    
            # If it's an environment variable reference, get from env
            if isinstance(current, str) and current.endswith('_env'):
                env_var = current.replace('_env', '').upper()
                return os.getenv(env_var, default)
                
            return current
            
        except Exception as e:
            logger.error(f"Failed to get sensitive value for {key_path}: {e}")
            return default
            
    def validate_config(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Validate configuration and return validation results."""
        if config is None:
            config = self.load_config()
            
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Required sections
        required_sections = ["logging", "security", "ai", "monitoring", "server"]
        for section in required_sections:
            if section not in config:
                validation_results["errors"].append(f"Missing required section: {section}")
                validation_results["valid"] = False
                
        # Environment-specific validations
        if config.get("environment") == "production":
            # Production-specific requirements
            if not os.getenv("ULTRON_SECRET_KEY"):
                validation_results["errors"].append("ULTRON_SECRET_KEY environment variable required for production")
                validation_results["valid"] = False
                
            if config.get("server", {}).get("debug", False):
                validation_results["warnings"].append("Debug mode should be disabled in production")
                
        # Security validations
        security_config = config.get("security", {})
        if security_config.get("max_failed_attempts", 0) > 10:
            validation_results["warnings"].append("High max_failed_attempts value may pose security risk")
            
        return validation_results
        
    def rotate_encryption_key(self) -> bool:
        """Rotate encryption key and re-encrypt configuration."""
        try:
            # Load current config
            config = self.decrypt_config()
            if config is None:
                logger.error("Cannot rotate key: unable to decrypt current configuration")
                return False
                
            # Backup current encrypted file
            backup_path = Path(str(self.encrypted_path) + f".backup.{int(time.time())}")
            if self.encrypted_path.exists():
                self.encrypted_path.rename(backup_path)
                logger.info(f"Backed up current config to {backup_path}")
                
            # Clear cipher suite to force new key generation
            self._cipher_suite = None
            
            # Re-encrypt with new key
            success = self.encrypt_config(config)
            if success:
                logger.info("Encryption key rotated successfully")
                return True
            else:
                # Restore backup if re-encryption failed
                if backup_path.exists():
                    backup_path.rename(self.encrypted_path)
                    logger.error("Key rotation failed, restored backup")
                return False
                
        except Exception as e:
            logger.error(f"Failed to rotate encryption key: {e}")
            return False


# Global config manager instance
config_manager = SecureConfigManager()


def get_config() -> Dict[str, Any]:
    """Get current configuration."""
    return config_manager.load_config()


def get_sensitive_config(key_path: str, default: Any = None) -> Any:
    """Get sensitive configuration value."""
    return config_manager.get_sensitive_value(key_path, default)


def validate_configuration() -> Dict[str, Any]:
    """Validate current configuration."""
    return config_manager.validate_config()


if __name__ == "__main__":
    import time
    
    # Example usage
    manager = SecureConfigManager()
    
    # Load and display configuration
    config = manager.load_config()
    print("Configuration loaded:")
    print(json.dumps({k: v for k, v in config.items() if k != "security"}, indent=2))
    
    # Validate configuration
    validation = manager.validate_config(config)
    print(f"\nValidation results: {validation}")
    
    # Test encryption
    if manager.encrypt_config(config):
        print("✅ Configuration encrypted successfully")
        
        # Test decryption
        decrypted = manager.decrypt_config()
        if decrypted:
            print("✅ Configuration decrypted successfully")
        else:
            print("❌ Configuration decryption failed")
    else:
        print("❌ Configuration encryption failed")