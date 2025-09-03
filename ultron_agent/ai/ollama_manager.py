"""
Ollama Manager for ULTRON Agent 3.0
Handles Ollama connection, model loading, and model switching
"""
from __future__ import annotations

import json
import logging
import subprocess
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests

from ..config import UltronConfig
from ..errors import UltronError, ErrorCategory, ErrorSeverity

logger = logging.getLogger(__name__)


class OllamaManager:
    """Manages Ollama connection and model operations."""

    def __init__(self, config: Optional[UltronConfig] = None) -> None:
        """Initialize the Ollama manager."""
        self.config = config or UltronConfig()
        self.base_url = self.config.ollama_base_url
        self.current_model = self.config.llm_model
        self.available_models: List[Dict[str, Any]] = []
        self.is_connected = False
        self._lock = threading.Lock()
        
        # Initialize connection
        self.check_connection()

    def check_connection(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                self.is_connected = True
                self.available_models = self._parse_models(response.json())
                logger.info(f"Ollama connected successfully. Available models: {len(self.available_models)}")
                
                # Verify current model exists
                if not self._model_exists(self.current_model):
                    logger.warning(f"Current model '{self.current_model}' not found, using first available")
                    if self.available_models:
                        self.current_model = self.available_models[0]["name"]
                
                return True
            else:
                self.is_connected = False
                raise UltronError(
                    f"Ollama connection failed: HTTP {response.status_code}",
                    category=ErrorCategory.API,
                    severity=ErrorSeverity.HIGH,
                    recovery_suggestion="Check if Ollama service is running on the correct port"
                )
                
        except requests.RequestException as e:
            self.is_connected = False
            raise UltronError(
                f"Ollama connection error: {e}",
                category=ErrorCategory.API,
                severity=ErrorSeverity.HIGH,
                recovery_suggestion="Start Ollama service using 'ollama serve'",
                original_error=e
            )

    def _parse_models(self, response_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse model data from Ollama API response."""
        try:
            models = response_data.get("models", [])
            parsed_models = []
            
            for model in models:
                parsed_models.append({
                    "name": model.get("name", "unknown"),
                    "size": model.get("size", 0),
                    "modified_at": model.get("modified_at"),
                    "digest": model.get("digest"),
                    "details": model.get("details", {})
                })
            
            return parsed_models
        except Exception as e:
            logger.error(f"Error parsing models: {e}")
            return []

    def _model_exists(self, model_name: str) -> bool:
        """Check if a model exists in the available models list."""
        return any(model["name"] == model_name for model in self.available_models)

    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models."""
        if not self.is_connected:
            self.check_connection()
        return self.available_models.copy()

    def get_current_model(self) -> str:
        """Get the currently selected model."""
        return self.current_model

    def switch_model(self, model_name: str) -> bool:
        """Switch to a different model."""
        with self._lock:
            if not self.is_connected:
                raise UltronError(
                    "Ollama not connected",
                    category=ErrorCategory.API,
                    severity=ErrorSeverity.HIGH,
                    recovery_suggestion="Check Ollama connection first"
                )
            
            if not self._model_exists(model_name):
                available_names = [m["name"] for m in self.available_models]
                raise UltronError(
                    f"Model '{model_name}' not found. Available models: {available_names}",
                    category=ErrorCategory.MODEL,
                    severity=ErrorSeverity.MEDIUM,
                    recovery_suggestion=f"Use one of these models: {', '.join(available_names)}"
                )
            
            old_model = self.current_model
            self.current_model = model_name
            logger.info(f"Switched model from '{old_model}' to '{model_name}'")
            return True

    def pull_model(self, model_name: str) -> bool:
        """Pull a new model from Ollama registry."""
        try:
            logger.info(f"Pulling model: {model_name}")
            
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name, "stream": False},
                timeout=300  # 5 minute timeout for model pulls
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully pulled model: {model_name}")
                # Refresh available models
                self.check_connection()
                return True
            else:
                raise UltronError(
                    f"Failed to pull model '{model_name}': HTTP {response.status_code}",
                    category=ErrorCategory.MODEL,
                    severity=ErrorSeverity.HIGH,
                    recovery_suggestion="Check model name and network connectivity"
                )
                
        except requests.RequestException as e:
            raise UltronError(
                f"Error pulling model '{model_name}': {e}",
                category=ErrorCategory.MODEL,
                severity=ErrorSeverity.HIGH,
                recovery_suggestion="Check network connection and Ollama service status",
                original_error=e
            )

    def delete_model(self, model_name: str) -> bool:
        """Delete a model from Ollama."""
        try:
            if model_name == self.current_model:
                raise UltronError(
                    "Cannot delete currently active model",
                    category=ErrorCategory.MODEL,
                    severity=ErrorSeverity.MEDIUM,
                    recovery_suggestion="Switch to another model first"
                )
            
            response = requests.delete(
                f"{self.base_url}/api/delete",
                json={"name": model_name}
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully deleted model: {model_name}")
                # Refresh available models
                self.check_connection()
                return True
            else:
                raise UltronError(
                    f"Failed to delete model '{model_name}': HTTP {response.status_code}",
                    category=ErrorCategory.MODEL,
                    severity=ErrorSeverity.HIGH
                )
                
        except requests.RequestException as e:
            raise UltronError(
                f"Error deleting model '{model_name}': {e}",
                category=ErrorCategory.MODEL,
                severity=ErrorSeverity.HIGH,
                original_error=e
            )

    def get_model_info(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """Get detailed information about a model."""
        target_model = model_name or self.current_model
        
        try:
            response = requests.post(
                f"{self.base_url}/api/show",
                json={"name": target_model}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise UltronError(
                    f"Failed to get info for model '{target_model}': HTTP {response.status_code}",
                    category=ErrorCategory.MODEL,
                    severity=ErrorSeverity.MEDIUM
                )
                
        except requests.RequestException as e:
            raise UltronError(
                f"Error getting model info for '{target_model}': {e}",
                category=ErrorCategory.MODEL,
                severity=ErrorSeverity.MEDIUM,
                original_error=e
            )

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status information."""
        return {
            "connected": self.is_connected,
            "base_url": self.base_url,
            "current_model": self.current_model,
            "available_models": len(self.available_models),
            "models": [{"name": m["name"], "size": m["size"]} for m in self.available_models]
        }

    def health_check(self) -> Tuple[bool, str]:
        """Perform a health check on the Ollama service."""
        try:
            # Check basic connectivity
            if not self.check_connection():
                return False, "Connection failed"
            
            # Try a simple generation test
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.current_model,
                    "prompt": "Hello",
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return True, "Healthy"
            else:
                return False, f"Generation test failed: HTTP {response.status_code}"
                
        except Exception as e:
            return False, f"Health check failed: {e}"