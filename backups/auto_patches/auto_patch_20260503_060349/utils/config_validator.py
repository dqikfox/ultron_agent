"""Configuration validation for ULTRON Agent"""
import json
import os
from pathlib import Path

def validate_config(config_path='ultron_config.json'):
    """Validate configuration file"""
    if not Path(config_path).exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path) as f:
        config = json.load(f)
    
    # Required fields (API key optional)
    required = ['alert_mode', 'control_mode']
    for key in required:
        if key not in config:
            config[key] = 'log_and_speak' if key == 'alert_mode' else 'voice_and_terminal'
    
    # Validate API key format if present
    api_key = config.get('openai_api_key', '')
    if api_key and not api_key.startswith('sk-') and not api_key.startswith('USE_ENV_'):
        raise ValueError("Invalid API key format")
    
    return config

def check_environment():
    """Check required environment setup"""
    checks = {
        'logs_dir': Path('logs').exists(),
        'tesseract': Path(r'C:\Program Files\Tesseract-OCR\tesseract.exe').exists(),
    }
    return checks
