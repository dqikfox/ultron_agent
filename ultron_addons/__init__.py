"""
ultron_addons
================

This package contains extensions and add-ons for the Ultron Agent project. The goal
is to provide modular components that can be dropped into the existing Ultron
architecture without modifying the core repository. These add-ons include
connectors for new services, enhanced memory backends, advanced brain
implementations, additional tool definitions, and utilities to manage
evolution of the agent over time.

All modules are designed to be self-contained and have minimal dependencies
outside of the Python standard library. When necessary, optional third-party
libraries can be used; however, the classes will degrade gracefully if those
libraries are unavailable. See the documentation in each module for details.
"""

from .connectors import Connector, GoogleDriveConnector
from .memory_enhanced import VectorMemory
from .brain_extension import AdvancedUltronBrain
from .tools import SearchTool, CalculatorTool
from .evolution import EvolutionManager

__all__ = [
    "Connector",
    "GoogleDriveConnector",
    "VectorMemory",
    "AdvancedUltronBrain",
    "SearchTool",
    "CalculatorTool",
    "EvolutionManager",
]
