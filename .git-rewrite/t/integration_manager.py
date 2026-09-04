"""
Integration Manager for ULTRON Agent 3.0
Connects and orchestrates all system components
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from security_utils import sanitize_log_input, SecurityConfig
from performance_optimizer import PerformanceMonitor

class IntegrationManager:
    """Manages integration between all ULTRON components."""
    
    def __init__(self):
        self.components = {}
        self.performance_monitor = PerformanceMonitor()
        self.logger = logging.getLogger(__name__)
        
    def register_component(self, name: str, component: Any) -> None:
        """Register a component with the integration manager."""
        self.components[name] = component
        self.logger.info(f"Component registered: {sanitize_log_input(name)}")
        
    def get_component(self, name: str) -> Optional[Any]:
        """Get a registered component."""
        return self.components.get(name)
        
    async def initialize_all(self) -> bool:
        """Initialize all registered components."""
        try:
            for name, component in self.components.items():
                if hasattr(component, 'initialize'):
                    await component.initialize()
                self.logger.info(f"Initialized: {sanitize_log_input(name)}")
            return True
        except Exception as e:
            self.logger.error(f"Initialization failed: {sanitize_log_input(str(e))}")
            return False
            
    async def health_check(self) -> Dict[str, bool]:
        """Check health of all components."""
        health_status = {}
        for name, component in self.components.items():
            try:
                if hasattr(component, 'health_check'):
                    health_status[name] = await component.health_check()
                else:
                    health_status[name] = True
            except Exception:
                health_status[name] = False
        return health_status
        
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            'components': list(self.components.keys()),
            'performance': self.performance_monitor.get_metrics(),
            'security': SecurityConfig.__dict__
        }

# Global integration manager instance
integration_manager = IntegrationManager()