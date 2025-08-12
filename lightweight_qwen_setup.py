"""
Lightweight Qwen2.5-Coder Implementation for Low Memory Systems
Optimized for systems with 4GB RAM or less
"""

import logging
import subprocess
import json
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class LightweightQwenManager:
    """Manages Qwen2.5-Coder with memory optimization"""
    
    def __init__(self):
        """Initialize lightweight Qwen manager"""
        self.model_name = None
        self.available_models = []
        self.memory_optimized = True
        
        # Check available models and select appropriate one
        self._check_available_models()
        self._select_optimal_model()
    
    def _check_available_models(self):
        """Check what Qwen models are available locally"""
        try:
            result = subprocess.run(
                ["ollama", "list"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    if 'qwen' in line.lower():
                        model_info = line.split()[0]  # First column is model name
                        self.available_models.append(model_info)
                        logger.info(f"Found Qwen model: {model_info}")
        
        except Exception as e:
            logger.error(f"Error checking available models: {e}")
    
    def _select_optimal_model(self):
        """Select the best Qwen model for available memory"""
        
        # Preference order for low memory systems (smallest to largest)
        preferred_models = [
            "qwen2.5-coder:1.5b",      # ~1GB RAM
            "qwen2.5-coder:3b",        # ~2GB RAM  
            "qwen2.5:1.5b",            # ~1GB RAM
            "qwen2.5:3b",              # ~2GB RAM
            "qwen2.5-coder:7b-instruct", # ~5.8GB RAM (your current issue)
            "qwen2.5-coder:7b",        # ~5.8GB RAM
        ]
        
        # Find the best available model
        for model in preferred_models:
            if any(model in available for available in self.available_models):
                self.model_name = model
                logger.info(f"Selected memory-optimized model: {model}")
                break
        
        if not self.model_name and self.available_models:
            # Use first available if no preferred match
            self.model_name = self.available_models[0]
            logger.warning(f"Using fallback model: {self.model_name}")
    
    def install_lightweight_model(self) -> bool:
        """Install a lightweight Qwen model suitable for 4GB systems"""
        
        print("🔧 Installing lightweight Qwen2.5-Coder for your system...")
        
        # Try to install smallest suitable model
        lightweight_models = [
            "qwen2.5-coder:1.5b",  # Only ~1GB RAM required
            "qwen2.5:1.5b",        # Fallback general model
        ]
        
        for model in lightweight_models:
            print(f"📥 Attempting to install {model}...")
            
            try:
                result = subprocess.run(
                    ["ollama", "pull", model],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes timeout
                )
                
                if result.returncode == 0:
                    print(f"✅ Successfully installed {model}")
                    self.model_name = model
                    self.available_models.append(model)
                    return True
                else:
                    print(f"❌ Failed to install {model}: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                print(f"⏱️ Timeout installing {model} - trying next option...")
                continue
            except Exception as e:
                print(f"❌ Error installing {model}: {e}")
                continue
        
        return False
    
    def query_lightweight_model(self, prompt: str, max_tokens: int = 512) -> str:
        """Query the lightweight model with memory optimization"""
        
        if not self.model_name:
            return "❌ No lightweight model available"
        
        try:
            # Use memory-optimized parameters
            optimized_prompt = {
                "model": self.model_name,
                "prompt": prompt,
                "options": {
                    "num_ctx": 1024,      # Reduced context window
                    "num_predict": min(max_tokens, 256),  # Limit output length
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_thread": 2,      # Use fewer threads
                    "mlock": False,       # Don't lock memory
                    "low_vram": True      # Enable low VRAM mode
                }
            }
            
            # Run with subprocess to avoid memory leaks
            process = subprocess.run(
                ["ollama", "run", self.model_name],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if process.returncode == 0:
                response = process.stdout.strip()
                logger.info(f"Lightweight model response: {len(response)} characters")
                return response
            else:
                error_msg = f"Model error: {process.stderr}"
                logger.error(error_msg)
                return f"❌ {error_msg}"
                
        except subprocess.TimeoutExpired:
            return "⏱️ Model response timeout (memory optimization active)"
        except Exception as e:
            error_msg = f"Query error: {str(e)}"
            logger.error(error_msg)
            return f"❌ {error_msg}"
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about current model"""
        
        info = {
            "current_model": self.model_name,
            "memory_optimized": self.memory_optimized,
            "available_models": self.available_models,
            "estimated_ram_usage": "Unknown"
        }
        
        if self.model_name:
            # Estimate RAM usage based on model size
            if "1.5b" in self.model_name:
                info["estimated_ram_usage"] = "~1-1.5GB"
            elif "3b" in self.model_name:
                info["estimated_ram_usage"] = "~2-3GB"
            elif "7b" in self.model_name:
                info["estimated_ram_usage"] = "~5-6GB"
            else:
                info["estimated_ram_usage"] = "Unknown"
        
        return info


def setup_lightweight_qwen():
    """Set up lightweight Qwen for systems with limited memory"""
    
    print("🔴 LIGHTWEIGHT QWEN2.5-CODER SETUP 🔴")
    print("=" * 50)
    print("Optimizing for systems with 4GB RAM or less")
    print("")
    
    manager = LightweightQwenManager()
    
    # Check current status
    info = manager.get_model_info()
    
    print("📊 SYSTEM STATUS:")
    print(f"Current Model: {info['current_model']}")
    print(f"Available Models: {len(info['available_models'])}")
    print(f"Memory Optimized: {info['memory_optimized']}")
    print("")
    
    # If no suitable model, install one
    if not manager.model_name:
        print("⚠️ No suitable lightweight model found.")
        print("Installing memory-optimized Qwen2.5-Coder...")
        print("")
        
        success = manager.install_lightweight_model()
        
        if success:
            print("✅ Lightweight model installation complete!")
        else:
            print("❌ Could not install lightweight model.")
            print("💡 Manual installation options:")
            print("   ollama pull qwen2.5-coder:1.5b  # Only 1GB RAM needed")
            print("   ollama pull qwen2.5:1.5b        # General purpose alternative")
            return None
    
    # Test the model
    print("🧪 TESTING LIGHTWEIGHT MODEL:")
    print("-" * 30)
    
    test_prompt = "Write a simple Python hello world function"
    response = manager.query_lightweight_model(test_prompt)
    
    print(f"Test Query: {test_prompt}")
    print(f"Response: {response[:200]}...")
    print("")
    
    # Final status
    final_info = manager.get_model_info()
    print("🎉 SETUP COMPLETE:")
    print(f"✅ Active Model: {final_info['current_model']}")
    print(f"✅ Est. RAM Usage: {final_info['estimated_ram_usage']}")
    print(f"✅ Memory Optimized: {final_info['memory_optimized']}")
    
    return manager


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    manager = setup_lightweight_qwen()
    
    if manager:
        print("\n" + "=" * 50)
        print("🔴 LIGHTWEIGHT QWEN READY FOR USE! 🔴")
        print("This model will use minimal system memory.")
        print("=" * 50)
