"""
ULTRON Enhanced - Core Modules Package
Advanced AI system components for automation, voice control, vision, and web interface
"""

__version__ = "2.0.0"
__author__ = "MiniMax Agent"
__description__ = "ULTRON Enhanced AI System with Pokedex-style Controls"

# Module imports for easy access
try:
    from .voice_processor import VoiceProcessor, UltronVoiceCommands
    from .system_automation import SystemAutomation, SystemMonitor, ProcessManager, FileManager
    from .vision_system import VisionSystem, VisionUtils
    from .web_server import UltronWebServer, WebServerUtils
    
    # Module availability flags
    VOICE_AVAILABLE = True
    AUTOMATION_AVAILABLE = True
    VISION_AVAILABLE = True
    WEB_AVAILABLE = True
    
except ImportError as e:
    import logging
    logging.warning(f"Some ULTRON core modules failed to import: {e}")
    
    # Set availability flags based on what imported successfully
    try:
        from .voice_processor import VoiceProcessor, UltronVoiceCommands
        VOICE_AVAILABLE = True
    except ImportError:
        VOICE_AVAILABLE = False
    
    try:
        from .system_automation import SystemAutomation, SystemMonitor, ProcessManager, FileManager
        AUTOMATION_AVAILABLE = True
    except ImportError:
        AUTOMATION_AVAILABLE = False
    
    try:
        from .vision_system import VisionSystem, VisionUtils
        VISION_AVAILABLE = True
    except ImportError:
        VISION_AVAILABLE = False
    
    try:
        from .web_server import UltronWebServer, WebServerUtils
        WEB_AVAILABLE = True
    except ImportError:
        WEB_AVAILABLE = False

# Core system information
CORE_INFO = {
    "version": __version__,
    "modules": {
        "voice_processor": VOICE_AVAILABLE,
        "system_automation": AUTOMATION_AVAILABLE,
        "vision_system": VISION_AVAILABLE,
        "web_server": WEB_AVAILABLE
    },
    "features": {
        "pokedex_interface": True,
        "voice_recognition": VOICE_AVAILABLE,
        "system_control": AUTOMATION_AVAILABLE,
        "computer_vision": VISION_AVAILABLE,
        "web_interface": WEB_AVAILABLE,
        "real_time_monitoring": True,
        "task_automation": AUTOMATION_AVAILABLE,
        "file_management": AUTOMATION_AVAILABLE
    }
}

def get_system_capabilities():
    """Get comprehensive system capabilities information"""
    return CORE_INFO.copy()

def check_dependencies():
    """Check if all required dependencies are available"""
    missing_deps = []
    optional_deps = []
    
    # Check core dependencies
    try:
        import psutil
    except ImportError:
        missing_deps.append("psutil")
    
    try:
        import tkinter
    except ImportError:
        missing_deps.append("tkinter")
    
    # Check optional dependencies
    try:
        import speech_recognition
    except ImportError:
        optional_deps.append("speech_recognition")
    
    try:
        import pyttsx3
    except ImportError:
        optional_deps.append("pyttsx3")
    
    try:
        import PIL
    except ImportError:
        optional_deps.append("Pillow")
    
    try:
        import cv2
    except ImportError:
        optional_deps.append("opencv-python")
    
    try:
        import pygame
    except ImportError:
        optional_deps.append("pygame")
    
    try:
        import openai
    except ImportError:
        optional_deps.append("openai")
    
    return {
        "missing_required": missing_deps,
        "missing_optional": optional_deps,
        "all_required_available": len(missing_deps) == 0,
        "full_features_available": len(missing_deps) == 0 and len(optional_deps) == 0
    }

def initialize_logging(log_level="INFO", log_file=None):
    """Initialize logging for ULTRON system"""
    import logging
    import os
    from pathlib import Path
    
    # Create logs directory if it doesn't exist
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    if log_file:
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format=log_format,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    else:
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format=log_format
        )
    
    logging.info("ULTRON Enhanced logging initialized")

# Version and compatibility information
PYTHON_MIN_VERSION = (3, 8)
SUPPORTED_PLATFORMS = ["Windows", "Linux", "macOS"]
RECOMMENDED_PLATFORM = "Windows"

def check_compatibility():
    """Check system compatibility"""
    import sys
    import platform
    
    issues = []
    warnings = []
    
    # Check Python version
    if sys.version_info < PYTHON_MIN_VERSION:
        issues.append(f"Python {PYTHON_MIN_VERSION[0]}.{PYTHON_MIN_VERSION[1]}+ required, found {sys.version}")
    
    # Check platform
    current_platform = platform.system()
    if current_platform not in SUPPORTED_PLATFORMS:
        warnings.append(f"Platform {current_platform} not officially supported")
    elif current_platform != RECOMMENDED_PLATFORM:
        warnings.append(f"{RECOMMENDED_PLATFORM} is recommended for full functionality")
    
    return {
        "compatible": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "python_version": sys.version,
        "platform": current_platform
    }

# Export main classes for easy importing
__all__ = [
    "VoiceProcessor",
    "UltronVoiceCommands", 
    "SystemAutomation",
    "SystemMonitor",
    "ProcessManager", 
    "FileManager",
    "VisionSystem",
    "VisionUtils",
    "UltronWebServer",
    "WebServerUtils",
    "get_system_capabilities",
    "check_dependencies",
    "check_compatibility",
    "initialize_logging",
    "CORE_INFO"
]
