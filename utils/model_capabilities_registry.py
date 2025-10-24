"""
Model Capabilities Registry - Track and query model-specific features

This module provides a registry for tracking capabilities of different Ollama models,
enabling the agent to dynamically adapt to model strengths and limitations.
"""

import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
import json
from pathlib import Path

from utils.ultron_logger import log_info, log_error


class ModelCapabilities:
    """Represents the capabilities of a specific model"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.supports_vision = False
        self.supports_function_calling = False
        self.supports_streaming = True
        self.max_context_length = 4096
        self.specializations = []
        self.parameters = {}
        self.tested = False
        self.last_updated = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'model_name': self.model_name,
            'supports_vision': self.supports_vision,
            'supports_function_calling': self.supports_function_calling,
            'supports_streaming': self.supports_streaming,
            'max_context_length': self.max_context_length,
            'specializations': self.specializations,
            'parameters': self.parameters,
            'tested': self.tested,
            'last_updated': self.last_updated
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelCapabilities':
        """Create from dictionary"""
        caps = cls(data.get('model_name', 'unknown'))
        caps.supports_vision = data.get('supports_vision', False)
        caps.supports_function_calling = data.get('supports_function_calling', False)
        caps.supports_streaming = data.get('supports_streaming', True)
        caps.max_context_length = data.get('max_context_length', 4096)
        caps.specializations = data.get('specializations', [])
        caps.parameters = data.get('parameters', {})
        caps.tested = data.get('tested', False)
        caps.last_updated = data.get('last_updated', datetime.now().isoformat())
        return caps


class ModelCapabilitiesRegistry:
    """
    Registry for tracking Ollama model capabilities.
    Enables dynamic adaptation to model strengths.
    """
    
    # Known model capabilities (from documentation and testing)
    KNOWN_MODELS = {
        'llama3.1': {
            'supports_vision': False,
            'supports_function_calling': True,
            'max_context_length': 8192,
            'specializations': ['general', 'reasoning', 'coding']
        },
        'llava:7b': {
            'supports_vision': True,
            'supports_function_calling': False,
            'max_context_length': 4096,
            'specializations': ['vision', 'image_analysis', 'general']
        },
        'qwen3-coder:480b-cloud': {
            'supports_vision': False,
            'supports_function_calling': True,
            'max_context_length': 32768,
            'specializations': ['coding', 'analysis', 'debugging']
        },
        'deepseek-r1:14b': {
            'supports_vision': False,
            'supports_function_calling': True,
            'max_context_length': 16384,
            'specializations': ['reasoning', 'mathematics', 'coding']
        },
        'llama3.2': {
            'supports_vision': False,
            'supports_function_calling': True,
            'max_context_length': 8192,
            'specializations': ['general', 'reasoning']
        }
    }
    
    def __init__(self, cache_file: str = 'data/model_capabilities.json'):
        """
        Initialize the registry.
        
        Args:
            cache_file: Path to cache file for storing capabilities
        """
        self.cache_file = Path(cache_file)
        self.capabilities: Dict[str, ModelCapabilities] = {}
        self.logger = logging.getLogger(__name__)
        
        # Create data directory if needed
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load from cache
        self._load_from_cache()
        
        # Initialize known models
        self._initialize_known_models()
        
        log_info("model_capabilities_registry", 
                f"Initialized with {len(self.capabilities)} model profiles")
    
    def _initialize_known_models(self):
        """Initialize capabilities for known models"""
        for model_name, caps_data in self.KNOWN_MODELS.items():
            if model_name not in self.capabilities:
                caps = ModelCapabilities(model_name)
                caps.supports_vision = caps_data.get('supports_vision', False)
                caps.supports_function_calling = caps_data.get('supports_function_calling', False)
                caps.max_context_length = caps_data.get('max_context_length', 4096)
                caps.specializations = caps_data.get('specializations', [])
                self.capabilities[model_name] = caps
    
    def _load_from_cache(self):
        """Load capabilities from cache file"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    for model_name, caps_data in data.items():
                        self.capabilities[model_name] = ModelCapabilities.from_dict(caps_data)
                log_info("model_capabilities_registry", 
                        f"Loaded {len(self.capabilities)} model profiles from cache")
        except Exception as e:
            log_error("model_capabilities_registry", f"Error loading cache: {e}")
    
    def _save_to_cache(self):
        """Save capabilities to cache file"""
        try:
            data = {name: caps.to_dict() for name, caps in self.capabilities.items()}
            with open(self.cache_file, 'w') as f:
                json.dump(data, f, indent=2)
            log_info("model_capabilities_registry", "Saved model capabilities to cache")
        except Exception as e:
            log_error("model_capabilities_registry", f"Error saving cache: {e}")
    
    def get_capabilities(self, model_name: str) -> Optional[ModelCapabilities]:
        """
        Get capabilities for a model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            ModelCapabilities or None if not found
        """
        # Normalize model name (remove version tags if needed)
        base_model = model_name.split(':')[0] if ':' in model_name else model_name
        
        # Try exact match first
        if model_name in self.capabilities:
            return self.capabilities[model_name]
        
        # Try base model name
        if base_model in self.capabilities:
            return self.capabilities[base_model]
        
        # Return None if not found
        return None
    
    def register_model(self, model_name: str, capabilities: Dict[str, Any]):
        """
        Register or update a model's capabilities.
        
        Args:
            model_name: Name of the model
            capabilities: Dictionary of capabilities
        """
        try:
            caps = ModelCapabilities(model_name)
            caps.supports_vision = capabilities.get('supports_vision', False)
            caps.supports_function_calling = capabilities.get('supports_function_calling', False)
            caps.supports_streaming = capabilities.get('supports_streaming', True)
            caps.max_context_length = capabilities.get('max_context_length', 4096)
            caps.specializations = capabilities.get('specializations', [])
            caps.parameters = capabilities.get('parameters', {})
            caps.tested = capabilities.get('tested', False)
            
            self.capabilities[model_name] = caps
            self._save_to_cache()
            
            log_info("model_capabilities_registry", 
                    f"Registered capabilities for model: {model_name}")
            
        except Exception as e:
            log_error("model_capabilities_registry", 
                     f"Error registering model {model_name}: {e}")
    
    def supports_vision(self, model_name: str) -> bool:
        """Check if model supports vision"""
        caps = self.get_capabilities(model_name)
        return caps.supports_vision if caps else False
    
    def supports_function_calling(self, model_name: str) -> bool:
        """Check if model supports function calling"""
        caps = self.get_capabilities(model_name)
        return caps.supports_function_calling if caps else False
    
    def get_max_context_length(self, model_name: str) -> int:
        """Get maximum context length for model"""
        caps = self.get_capabilities(model_name)
        return caps.max_context_length if caps else 4096
    
    def get_specializations(self, model_name: str) -> List[str]:
        """Get model specializations"""
        caps = self.get_capabilities(model_name)
        return caps.specializations if caps else []
    
    def find_best_model_for_task(self, task_type: str, available_models: List[str]) -> Optional[str]:
        """
        Find the best model for a specific task type.
        
        Args:
            task_type: Type of task (vision, coding, reasoning, etc.)
            available_models: List of available model names
            
        Returns:
            Best model name or None
        """
        try:
            best_model = None
            best_score = -1
            
            for model_name in available_models:
                caps = self.get_capabilities(model_name)
                if not caps:
                    continue
                
                # Calculate score based on specializations
                score = 0
                if task_type in caps.specializations:
                    score += 10
                elif any(task_type in spec for spec in caps.specializations):
                    score += 5
                
                # Bonus for tested models
                if caps.tested:
                    score += 2
                
                # Bonus for larger context (for complex tasks)
                if caps.max_context_length > 8192:
                    score += 1
                
                if score > best_score:
                    best_score = score
                    best_model = model_name
            
            if best_model:
                log_info("model_capabilities_registry", 
                        f"Selected {best_model} for task '{task_type}' (score: {best_score})")
            
            return best_model
            
        except Exception as e:
            log_error("model_capabilities_registry", 
                     f"Error finding best model: {e}")
            return None
    
    def list_models_by_capability(self, capability: str) -> List[str]:
        """
        List all models that have a specific capability.
        
        Args:
            capability: Capability name (vision, function_calling, etc.)
            
        Returns:
            List of model names
        """
        matching_models = []
        
        for model_name, caps in self.capabilities.items():
            if capability == 'vision' and caps.supports_vision:
                matching_models.append(model_name)
            elif capability == 'function_calling' and caps.supports_function_calling:
                matching_models.append(model_name)
            elif capability in caps.specializations:
                matching_models.append(model_name)
        
        return matching_models
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get statistics about the registry"""
        return {
            'total_models': len(self.capabilities),
            'vision_models': len(self.list_models_by_capability('vision')),
            'function_calling_models': len(self.list_models_by_capability('function_calling')),
            'tested_models': sum(1 for caps in self.capabilities.values() if caps.tested),
            'cache_file': str(self.cache_file),
            'models': list(self.capabilities.keys())
        }


# Global registry instance
_registry_instance = None


def get_model_capabilities_registry() -> ModelCapabilitiesRegistry:
    """Get or create the global model capabilities registry"""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = ModelCapabilitiesRegistry()
    return _registry_instance
