"""Ultron Agent package initialization."""
from __future__ import annotations

# Import version from centralized version module
from ultron_agent.__version__ import __version__, get_version, get_version_info

__title__ = "Ultron Agent"
__description__ = "Local voice-first AI assistant with multi-model support"
__author__ = "dqikfox"

# Lazy imports to avoid dependency issues during packaging
def _import_config():
    """Lazy import of config module."""
    try:
        from ultron_agent.config import UltronConfig, get_config, load_config
        return UltronConfig, get_config, load_config
    except ImportError as e:
        raise ImportError(f"Config module not available: {e}")

def _import_logging():
    """Lazy import of logging module."""
    try:
        from ultron_agent.logging_config import setup_logging, get_logger
        return setup_logging, get_logger
    except ImportError as e:
        raise ImportError(f"Logging module not available: {e}")

def _import_health():
    """Lazy import of health module."""
    try:
        from ultron_agent.health import get_health_checker
        return get_health_checker
    except ImportError as e:
        raise ImportError(f"Health module not available: {e}")

# Make lazy imports available at module level
def __getattr__(name: str):
    """Lazy attribute access for optional imports."""
    if name in ['UltronConfig', 'get_config', 'load_config']:
        UltronConfig, get_config, load_config = _import_config()
        if name == 'UltronConfig':
            return UltronConfig
        elif name == 'get_config':
            return get_config
        elif name == 'load_config':
            return load_config
    elif name in ['setup_logging', 'get_logger']:
        setup_logging, get_logger = _import_logging()
        if name == 'setup_logging':
            return setup_logging
        elif name == 'get_logger':
            return get_logger
    elif name == 'get_health_checker':
        get_health_checker = _import_health()
        return get_health_checker
    
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    "__version__",
    "__title__",
    "__description__", 
    "__author__",
    "get_version",
    "get_version_info",
    "UltronConfig",
    "get_config",
    "load_config",
    "setup_logging",
    "get_logger",
    "get_health_checker"
]
