"""
Ollama Manager for ULTRON Agent 2.0
Handles Ollama connection, model loading, and model switching
"""

import subprocess
import requests
import json
import logging
import time
import threading
from pathlib import Path

logger = logging.getLogger(__name__)

class OllamaManager:
    """Manages Ollama connection and model operations"""
    
    def __init__(self, config=None):
        self.config = config
        self.base_url = "http://127.0.0.1:11434"
        self.current_model = None
        self.available_models = []
        self.is_connected = False
        
        # Initialize connection
        self.check_connection()
        
    def check_connection(self):
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                self.is_connected = True
                self.available_models = self._parse_models(response.json())
                logger.info(f"Ollama connected successfully. Available models: {len(self.available_models)}")
                
                # Check current model
                self.current_model = self._get_current_model()
                return True
            else:
                self.is_connected = False
                logger.error(f"Ollama connection failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.is_connected = False
            logger.error(f"Ollama connection error: {e}")
            return False
    
    def _parse_models(self, response_data):
        """Parse available models from Ollama response"""
        models = []
        if 'models' in response_data:
            for model in response_data['models']:
                models.append(model.get('name', 'unknown'))
        return models
    
    def _get_current_model(self):
        """Get currently loaded model"""
        try:
            if self.config and hasattr(self.config, 'data'):
                configured_model = self.config.data.get('llm_model', 'qwen2.5:latest')
                
                # Check if configured model is available
                if configured_model in self.available_models:
                    return configured_model
                
                # Try to find qwen2.5 variants
                for model in self.available_models:
                    if 'qwen2.5' in model.lower():
                        return model
                
                # Fallback to first available model
                if self.available_models:
                    return self.available_models[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting current model: {e}")
            return None
    
    def switch_model(self, model_name):
        """Switch to a different model using proper Ollama commands"""
        try:
            logger.info(f"Switching to model: {model_name}")
            
            # First, check if the model is available locally
            if model_name not in self.available_models:
                logger.info(f"Model {model_name} not found locally, attempting to pull...")
                success = self.pull_model(model_name)
                if not success:
                    logger.error(f"Failed to pull model: {model_name}")
                    return False
            
            # Stop any currently running models
            self._stop_running_models()
            
            # Run the model to load it (using subprocess for better control)
            cmd = ["ollama", "run", model_name, "--help"]  # Use --help to load without interactive mode
            logger.info(f"Executing: {' '.join(cmd)}")
            
            try:
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=False
                )
                
                # Check if model loaded successfully
                if process.returncode == 0 or "Available Commands" in process.stdout:
                    self.current_model = model_name
                    logger.info(f"Model switched successfully to: {model_name}")
                    
                    # Update config if available
                    if self.config and hasattr(self.config, 'data'):
                        self.config.data['llm_model'] = model_name
                    
                    # Verify the model is working
                    if self.test_model(model_name):
                        return True
                    else:
                        logger.warning(f"Model {model_name} loaded but not responding properly")
                        return True  # Still consider it successful if loaded
                else:
                    logger.error(f"Model switch failed. Error: {process.stderr}")
                    return False
                    
            except subprocess.TimeoutExpired:
                logger.error(f"Timeout switching to model: {model_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error switching model: {e}")
            return False
    
    def _stop_running_models(self):
        """Stop all currently running models"""
        try:
            # Get running models
            result = subprocess.run(
                ["ollama", "ps"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:  # Skip header
                    for line in lines[1:]:
                        if line.strip():
                            model_name = line.split()[0]
                            logger.info(f"Stopping running model: {model_name}")
                            subprocess.run(
                                ["ollama", "stop", model_name],
                                capture_output=True,
                                timeout=10
                            )
        except Exception as e:
            logger.warning(f"Error stopping running models: {e}")
    
    def list_running_models(self):
        """List currently running models"""
        try:
            result = subprocess.run(
                ["ollama", "ps"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                running_models = []
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:  # Skip header
                    for line in lines[1:]:
                        if line.strip():
                            parts = line.split()
                            if len(parts) >= 4:
                                running_models.append({
                                    'name': parts[0],
                                    'id': parts[1],
                                    'size': parts[2],
                                    'until': parts[3] if len(parts) > 3 else 'N/A'
                                })
                return running_models
            else:
                logger.error(f"Failed to list running models: {result.stderr}")
                return []
                
        except Exception as e:
            logger.error(f"Error listing running models: {e}")
            return []
    
    def pull_model(self, model_name):
        """Pull a model from Ollama registry using proper command"""
        try:
            logger.info(f"Pulling model: {model_name}")
            
            cmd = ["ollama", "pull", model_name]
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout for large models
            )
            
            if process.returncode == 0:
                logger.info(f"Model pulled successfully: {model_name}")
                # Refresh available models
                self.check_connection()
                return True
            else:
                logger.error(f"Failed to pull model {model_name}: {process.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout pulling model: {model_name}")
            return False
        except Exception as e:
            logger.error(f"Error pulling model: {e}")
            return False
    
    def remove_model(self, model_name):
        """Remove a model from local storage"""
        try:
            logger.info(f"Removing model: {model_name}")
            
            cmd = ["ollama", "rm", model_name]
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if process.returncode == 0:
                logger.info(f"Model removed successfully: {model_name}")
                # Refresh available models
                self.check_connection()
                return True
            else:
                logger.error(f"Failed to remove model {model_name}: {process.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error removing model: {e}")
            return False
    
    def show_model_info(self, model_name):
        """Show detailed information about a model"""
        try:
            cmd = ["ollama", "show", model_name]
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if process.returncode == 0:
                return process.stdout
            else:
                logger.error(f"Failed to get model info for {model_name}: {process.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return None
    
    def test_model(self, model_name=None):
        """Test if a model is working"""
        try:
            test_model = model_name or self.current_model
            if not test_model:
                return False
            
            # Simple test prompt
            data = {
                "model": test_model,
                "prompt": "Hello, respond with just 'OK'",
                "stream": False
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Model test successful for {test_model}")
                return True
            else:
                logger.error(f"Model test failed for {test_model}: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Model test error: {e}")
            return False
    
    def get_status(self):
        """Get comprehensive Ollama status"""
        status = {
            'connected': self.is_connected,
            'current_model': self.current_model,
            'available_models': self.available_models,
            'model_count': len(self.available_models),
            'running_models': []
        }
        
        if self.is_connected:
            # Get running models
            status['running_models'] = self.list_running_models()
            
            # Test current model if available
            if self.current_model:
                status['model_working'] = self.test_model()
            else:
                status['model_working'] = False
        else:
            status['model_working'] = False
        
        return status
    
    def get_model_sizes(self):
        """Get size information for all models"""
        try:
            cmd = ["ollama", "list"]
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if process.returncode == 0:
                model_info = {}
                lines = process.stdout.strip().split('\n')
                if len(lines) > 1:  # Skip header
                    for line in lines[1:]:
                        if line.strip():
                            parts = line.split()
                            if len(parts) >= 3:
                                model_name = parts[0]
                                size = parts[2]
                                modified = ' '.join(parts[3:]) if len(parts) > 3 else 'Unknown'
                                model_info[model_name] = {
                                    'size': size,
                                    'modified': modified,
                                    'id': parts[1] if len(parts) > 1 else 'Unknown'
                                }
                return model_info
            else:
                logger.error(f"Failed to get model sizes: {process.stderr}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting model sizes: {e}")
            return {}
    
    def ensure_default_model(self):
        """Ensure default model (qwen2.5) is loaded"""
        try:
            default_models = ['qwen2.5:latest', 'qwen2.5', 'qwen2.5:7b']
            
            # Check if any qwen2.5 variant is available
            for model in default_models:
                if model in self.available_models:
                    if self.current_model != model:
                        return self.switch_model(model)
                    return True
            
            # Try to pull qwen2.5:latest if not available
            logger.info("Default model qwen2.5 not found, attempting to pull...")
            if self.pull_model('qwen2.5:latest'):
                return self.switch_model('qwen2.5:latest')
            
            return False
            
        except Exception as e:
            logger.error(f"Error ensuring default model: {e}")
            return False

# Global Ollama manager instance
_ollama_manager = None

def get_ollama_manager(config=None):
    """Get global Ollama manager instance"""
    global _ollama_manager
    if _ollama_manager is None:
        _ollama_manager = OllamaManager(config)
    return _ollama_manager

def test_ollama_connection():
    """Test Ollama connection"""
    manager = get_ollama_manager()
    return manager.check_connection()

if __name__ == "__main__":
    # Test the Ollama manager
    print("Testing Ollama Manager... - ollama_manager.py:407")
    manager = OllamaManager()
    status = manager.get_status()
    print(f"Ollama Status: {status} - ollama_manager.py:410")
    
    if status['connected']:
        print("Ensuring default model... - ollama_manager.py:413")
        manager.ensure_default_model()
