"""
Standardized Tool Interface for ULTRON Agent
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class ToolInterface(ABC):
    """Abstract base class for all ULTRON Agent tools"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description"""
        pass
    
    @abstractmethod
    def match(self, command: str) -> bool:
        """Check if command matches this tool"""
        pass
    
    @abstractmethod
    def execute(self, command: str, **kwargs) -> str:
        """Execute tool operation"""
        pass
    
    @classmethod
    @abstractmethod
    def schema(cls) -> Dict[str, Any]:
        """Return tool schema for registration"""
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get tool metadata"""
        return {
            "name": self.name,
            "description": self.description,
            "schema": self.schema()
        }
