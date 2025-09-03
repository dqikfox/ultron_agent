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
from ultron_agent.errors import UltronError, ErrorCategory, ErrorSeverity

# Import core agent
from ultron_agent.agent_core import ModernUltronAgent, UltronAgent

# Import AI components
from ultron_agent.ai import UltronBrain, OllamaManager

# Import interface components  
from ultron_agent.interfaces import VoiceManager, VisionManager

# Import storage components
from ultron_agent.storage import Memory

__all__ = [
    # Package metadata
    "__version__",
    "__title__", 
    "__description__",
    "__author__",
    
    # Core infrastructure
    "UltronConfig",
    "get_config", 
    "load_config",
    "setup_logging",
    "get_logger",
    "get_health_checker",
    "UltronError",
    "ErrorCategory", 
    "ErrorSeverity",
    
    # Core agent
    "ModernUltronAgent",
    "UltronAgent",  # Backward compatibility
    
    # AI components
    "UltronBrain",
    "OllamaManager",
    
    # Interface components
    "VoiceManager",
    "VisionManager", 
    
    # Storage components
    "Memory",
]
