"""Ultron Agent package initialization."""
from __future__ import annotations

__version__ = "3.0.0"
__title__ = "Ultron Agent"
__description__ = "Local voice-first AI assistant with multi-model support"
__author__ = "dqikfox"

# Import main components for easy access
from ultron_agent.config import UltronConfig, get_config, load_config
from ultron_agent.logging_config import setup_logging, get_logger
from ultron_agent.health import get_health_checker

__all__ = [
    "__version__",
    "__title__",
    "__description__",
    "__author__",
    "UltronConfig",
    "get_config",
    "load_config",
    "setup_logging",
    "get_logger",
    "get_health_checker"
]
