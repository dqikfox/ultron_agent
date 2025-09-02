"""
ULTRON Agent Core Module
========================

Core system modules for ULTRON Agent Enhanced.
This package contains the essential components for voice processing,
system automation, computer vision, and web server functionality.
"""

__version__ = "3.0.0"
__author__ = "ULTRON Agent Development Team"

# Import core components for easy access
from .voice_processor import VoiceProcessor
from .system_automation import SystemAutomation
from .vision_system import VisionSystem
from .web_server import UltronWebServer
from .file_sorter import FileSorter

__all__ = [
    'VoiceProcessor',
    'SystemAutomation', 
    'VisionSystem',
    'UltronWebServer',
    'FileSorter'
]