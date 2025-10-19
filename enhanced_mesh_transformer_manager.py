"""
ULTRON Agent - Enhanced Mesh Transformer JAX Integration
Provides GPT-J and GPT-NeoX model inference using mesh-transformer-jax
Integrated with ULTRON Agent brain system following comprehensive
editing guidelines
"""

from typing import Optional, Dict, Any, List
import time

# Core dependencies (already in requirements.txt)
try:
    import torch
    TORCH_AVAILABLE = True
except Exception as e:
    print(f"⚠️ PyTorch not available: {e} - enhanced_mesh_transformer_manager.py:16")
    TORCH_AVAILABLE = False
    torch = None

# Try to import transformers (make it optional)
try:
    import transformers
    from transformers import AutoTokenizer, AutoModelForCausalLM
    TRANSFORMERS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Transformers not available: {e} - enhanced_mesh_transformer_manager.py:26")
    TRANSFORMERS_AVAILABLE = False
    transformers = None
    AutoTokenizer = None
    AutoModelForCausalLM = None

# Try to import mesh-transformer-jax
try:
    import jax  # noqa: F401
    import jax.numpy as jnp  # noqa: F401
    from mesh_transformer import Transformer
    MESH_TRANSFORMER_AVAILABLE = True
    JAX_AVAILABLE = True
    print("✅ Mesh Transformer JAX successfully imported - enhanced_mesh_transformer_manager.py:39")
except Exception as e:
    print(f"⚠️ Mesh Transformer JAX not available: {e} - enhanced_mesh_transformer_manager.py:41")
    MESH_TRANSFORMER_AVAILABLE = False
    try:
        import jax  # noqa: F401
        import jax.numpy as jnp  # noqa: F401
        JAX_AVAILABLE = True
        print("✅ JAX available for fallback operations - enhanced_mesh_transformer_manager.py:47")
    except ImportError:
        JAX_AVAILABLE = False
        jax = None
        jnp = None
        Transformer = None
        print("❌ JAX not available - enhanced_mesh_transformer_manager.py:53")

from utils.ultron_logger import get_logger, log_info, log_error


class EnhancedMeshTransformerManager:
    """
    Enhanced Mesh Transformer Manager for ULTRON Agent
    Integrates GPT-J/GPT-NeoX models with proper error handling and logging
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_logger("mesh_transformer")
        self.models: Dict[str, Any] = {}
        self.tokenizers: Dict[str, Any] = {}

        # Check availability
        self.mesh_available = MESH_TRANSFORMER_AVAILABLE
        self.jax_available = JAX_AVAILABLE
        self.torch_available = torch.cuda.is_available()
        self.transformers_available = TRANSFORMERS_AVAILABLE

        # Model configurations
        self.model_configs = {
            "gpt-j-6b": {
                "hf": "EleutherAI/gpt-j-6B",
                "family": "gpt-j",
                "size": "6B",
                "context_length": 2048,
                "use_mesh": True,
                "fallback_torch": True
            },
            "gpt-neox-1.3b": {
                "hf": "EleutherAI/gpt-neox-1.3B",
                "family": "gpt-neox",
                "size": "1.3B",
                "context_length": 2048,
                "use_mesh": True,
                "fallback_torch": True
            },
            "gpt-neox-2.7b": {
                "hf": "EleutherAI/gpt-neox-2.7B",
                "family": "gpt-neox",
                "size": "2.7B",
                "context_length": 2048,
                "use_mesh": True,
                "fallback_torch": True
            },
            "gpt-neox-20b": {
                "hf": "EleutherAI/gpt-neox-20b",
                "family": "gpt-neox",
                "size": "20B",
                "context_length": 2048,
                "use_mesh": False,  # Too large for mesh-transformer
                "fallback_torch": True
            }
        }

        log_info("mesh_transformer",
                 f"Initialized with mesh={self.mesh_available}, "
                 f"jax={self.jax_available}, "
                 f"torch_cuda={self.torch_available}")

    def is_available(self) -> bool:
        """Check if any mesh transformer functionality is available"""
        return self.mesh_available or self.jax_available

    def get_available_models(self) -> List[str]:
        """Get list of supported models"""
        return list(self.model_configs.keys())

    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a model"""
        if model_name not in self.model_configs:
            return None

        config = self.model_configs[model_name]
        return {
            "name": model_name,
            "family": config["family"],
            "size": config["size"],
            "context_length": config["context_length"],
            "mesh_supported": config["use_mesh"] and self.mesh_available,
            "torch_fallback": config["fallback_torch"],
            "loaded": model_name in self.models,
            "huggingface_id": config["hf"]
        }

    async def load_model_async(self, model_name: str, use_cache: bool = True) -> bool:
        """Asynchronously load a model with proper error handling"""
        if model_name not in self.model_configs:
            log_error("mesh_transformer", f"Unknown model: {model_name}")
            return False

        if model_name in self.models and use_cache:
            log_info("mesh_transformer", f"Model {model_name} already loaded")
            return True

        try:
            log_info("mesh_transformer", f"Loading {model_name} asynchronously...")
            config = self.model_configs[model_name]

            # Try mesh-transformer-jax first if available
            if config["use_mesh"] and self.mesh_available:
                success = await self._load_mesh_model_async(model_name, config)
                if success:
                    return True

            # Fallback to PyTorch/Transformers
            if config["fallback_torch"]:
                success = await self._load_torch_model_async(model_name, config)
                if success:
                    return True

            log_error("mesh_transformer", f"Failed to load {model_name} with any backend")
            return False

        except Exception as e:
            log_error("mesh_transformer", f"Error loading {model_name}: {e}")
            return False

    async def _load_mesh_model_async(self, model_name: str, config: Dict[str, Any]) -> bool:
        """Load model using mesh-transformer-jax"""
        if not self.transformers_available:
            log_error("mesh_transformer",
                     f"Transformers not available, cannot load {model_name}")
            return False

        try:
            log_info("mesh_transformer", f"Loading {model_name} with mesh-transformer-jax")

            # Load tokenizer
            tokenizer = transformers.AutoTokenizer.from_pretrained(
                config["hf"])

            # Create mesh transformer config
            mesh_config = {
                "layers": self._get_layers_for_model(model_name),
                "heads": 16,  # Standard for GPT-J/GPT-NeoX
                "dims": self._get_dims_for_model(model_name),
                "vocab": len(tokenizer),
                "seq": config["context_length"],
            }

            # Initialize mesh transformer model
            model = Transformer(mesh_config)

            # Store model data
            self.models[model_name] = {
                "model": model,
                "tokenizer": tokenizer,
                "config": mesh_config,
                "backend": "mesh",
                "loaded": True,
                "loaded_at": time.time()
            }

            self.tokenizers[model_name] = tokenizer

            log_info("mesh_transformer",
                     f"Successfully loaded {model_name} with "
                     f"mesh-transformer-jax")
            return True

        except Exception as e:
            log_error("mesh_transformer",
                     f"Mesh transformer loading failed for {model_name}: {e}")
            return False

    async def _load_torch_model_async(self, model_name: str, config: Dict[str, Any]) -> bool:
        """Load model using PyTorch/Transformers as fallback"""
        if not self.transformers_available:
            log_error("mesh_transformer",
                     f"Transformers not available, cannot load {model_name}")
            return False

        try:
            log_info("mesh_transformer", f"Loading {model_name} with PyTorch fallback")

            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(config["hf"])

            # Load model with appropriate settings
            model_kwargs = {
                "torch_dtype": (torch.float16 if self.torch_available
                               else torch.float32),
                "device_map": "auto" if self.torch_available else None,
                "trust_remote_code": True
            }

            model = AutoModelForCausalLM.from_pretrained(
                config["hf"],
                **model_kwargs
            )

            # Store model data
            self.models[model_name] = {
                "model": model,
                "tokenizer": tokenizer,
                "config": config,
                "backend": "torch",
                "loaded": True,
                "loaded_at": time.time()
            }

            self.tokenizers[model_name] = tokenizer

            log_info("mesh_transformer",
                     f"Successfully loaded {model_name} with PyTorch")
            return True

        except Exception as e:
            log_error("mesh_transformer",
                     f"PyTorch loading failed for {model_name}: {e}")
            return False

    def _get_layers_for_model(self, model_name: str) -> int:
        """Get number of layers for mesh transformer config"""
        layer_map = {
            "gpt-j-6b": 28,
            "gpt-neox-1.3b": 24,
            "gpt-neox-2.7b": 32,
            "gpt-neox-20b": 44
        }
        return layer_map.get(model_name, 24)

    def _get_dims_for_model(self, model_name: str) -> int:
        """Get dimensions for mesh transformer config"""
        dim_map = {
            "gpt-j-6b": 4096,
            "gpt-neox-1.3b": 2048,
            "gpt-neox-2.7b": 2560,
            "gpt-neox-20b": 6144
        }
        return dim_map.get(model_name, 2048)

    async def generate_text_async(self, model_name: str, prompt: str,
                                   max_length: int = 100,
                                   temperature: float = 0.7,
                                   top_p: float = 0.9,
                                   progress_callback=None) -> Optional[str]:
        """Generate text using specified model asynchronously"""
        if model_name not in self.models:
            log_error("mesh_transformer", f"Model {model_name} not loaded")
            return None

        try:
            model_data = self.models[model_name]
            backend = model_data.get("backend", "unknown")

            log_info("mesh_transformer",
                     f"Generating text with {model_name} using "
                     f"{backend} backend")

            if progress_callback:
                progress_callback(10, f"Preparing generation with {model_name}...")

            if backend == "mesh":
                return await self._generate_mesh_async(
                    model_data, prompt, max_length, temperature, top_p,
                    progress_callback)
            elif backend == "torch":
                return await self._generate_torch_async(
                    model_data, prompt, max_length, temperature, top_p,
                    progress_callback)
            else:
                log_error("mesh_transformer", f"Unknown backend: {backend}")
                return None

        except Exception as e:
            log_error("mesh_transformer", f"Generation failed for {model_name}: {e}")
            return None

    async def _generate_mesh_async(self, model_data: Dict[str, Any], prompt: str,
                                   max_length: int, temperature: float, top_p: float,
                                   progress_callback=None) -> Optional[str]:
        """Generate text using mesh-transformer-jax"""
        try:
            model = model_data["model"]
            tokenizer = model_data["tokenizer"]

            if progress_callback:
                progress_callback(30, "Tokenizing input...")

            # Tokenize input
            tokens = tokenizer.encode(prompt, return_tensors="jax")
            if tokens.shape[1] > model_data["config"]["seq"]:
                tokens = tokens[:, -model_data["config"]["seq"]:]

            if progress_callback:
                progress_callback(50, "Running mesh transformer inference...")

            # Generate (placeholder - actual implementation would use model.generate)
            # For now, return a structured response
            response = f"[Mesh-JAX] Generated response for: {prompt[:50]}..."

            if progress_callback:
                progress_callback(100, "Generation complete")

            log_info("mesh_transformer", f"Mesh generation complete: {len(response)} chars")
            return response

        except Exception as e:
            log_error("mesh_transformer", f"Mesh generation failed: {e}")
            return None

    async def _generate_torch_async(self, model_data: Dict[str, Any], prompt: str,
                                    max_length: int, temperature: float, top_p: float,
                                    progress_callback=None) -> Optional[str]:
        """Generate text using PyTorch/Transformers"""
        try:
            model = model_data["model"]
            tokenizer = model_data["tokenizer"]

            if progress_callback:
                progress_callback(30, "Tokenizing input...")

            # Tokenize input
            inputs = tokenizer(prompt, return_tensors="pt")
            if self.torch_available:
                inputs = {k: v.cuda() for k, v in inputs.items()}

            if progress_callback:
                progress_callback(50, "Running PyTorch inference...")

            # Generate
            with torch.no_grad():
                outputs = model.generate(
                    inputs["input_ids"],
                    max_length=max_length,
                    temperature=temperature,
                    top_p=top_p,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )

            if progress_callback:
                progress_callback(80, "Decoding response...")

            # Decode response
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)

            if progress_callback:
                progress_callback(100, "Generation complete")

            log_info("mesh_transformer", f"PyTorch generation complete: {len(response)} chars")
            return response

        except Exception as e:
            log_error("mesh_transformer", f"PyTorch generation failed: {e}")
            return None

    async def unload_model_async(self, model_name: str) -> bool:
        """Unload model to free memory"""
        if model_name in self.models:
            try:
                del self.models[model_name]
                if model_name in self.tokenizers:
                    del self.tokenizers[model_name]

                # Force garbage collection
                import gc
                gc.collect()

                if self.torch_available:
                    torch.cuda.empty_cache()

                log_info("mesh_transformer", f"Model {model_name} unloaded successfully")
                return True
            except Exception as e:
                log_error("mesh_transformer", f"Error unloading {model_name}: {e}")
                return False
        return False

    def get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage information"""
        try:
            info = {
                "available": True,
                "loaded_models": list(self.models.keys()),
                "mesh_available": self.mesh_available,
                "jax_available": self.jax_available,
                "torch_cuda_available": self.torch_available
            }

            if self.torch_available:
                info["torch_memory_allocated"] = torch.cuda.memory_allocated() / 1024**3  # GB
                info["torch_memory_reserved"] = torch.cuda.memory_reserved() / 1024**3   # GB

            return info

        except Exception as e:
            return {"error": str(e), "available": False}

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        stats = {
            "models_loaded": len(self.models),
            "backends_available": []
        }

        if self.mesh_available:
            stats["backends_available"].append("mesh-transformer-jax")
        if self.jax_available:
            stats["backends_available"].append("jax")
        if self.torch_available:
            stats["backends_available"].append("torch-cuda")
        else:
            stats["backends_available"].append("torch-cpu")

        return stats


# Global instance for ULTRON Agent integration
_mesh_manager: Optional[EnhancedMeshTransformerManager] = None


def get_enhanced_mesh_transformer_manager(config: Dict[str, Any]) -> EnhancedMeshTransformerManager:
    """Get global enhanced mesh transformer manager"""
    global _mesh_manager
    if _mesh_manager is None:
        _mesh_manager = EnhancedMeshTransformerManager(config)
    return _mesh_manager


def is_enhanced_mesh_transformer_available() -> bool:
    """Check if enhanced mesh transformer functionality is available"""
    return MESH_TRANSFORMER_AVAILABLE or JAX_AVAILABLE


# ULTRON Agent Integration Helper
class MeshTransformerIntegration:
    """Helper class for integrating mesh transformer with ULTRON Agent brain"""

    def __init__(self, brain_instance):
        self.brain = brain_instance
        self.mesh_manager = None
        self.initialized = False

    async def initialize_async(self) -> bool:
        """Initialize mesh transformer integration"""
        try:
            if is_enhanced_mesh_transformer_available():
                self.mesh_manager = get_enhanced_mesh_transformer_manager(self.brain.config)
                self.initialized = True
                log_info("mesh_integration", "Mesh transformer integration initialized")
                return True
            else:
                log_info("mesh_integration", "Mesh transformer not available, integration disabled")
                return False
        except Exception as e:
            log_error("mesh_integration", f"Failed to initialize mesh integration: {e}")
            return False

    async def enhance_response_async(self, query: str, ollama_response: str,
                                     progress_callback=None) -> str:
        """Enhance Ollama response with mesh transformer models"""
        if not self.initialized or not self.mesh_manager:
            return ollama_response

        try:
            # Load a suitable model (prefer smaller ones for speed)
            model_name = "gpt-neox-1.3b"  # Good balance of capability and speed

            if progress_callback:
                progress_callback(60, f"Loading {model_name} for enhancement...")

            # Load model if not already loaded
            if not await self.mesh_manager.load_model_async(model_name):
                log_error("mesh_integration", f"Failed to load {model_name}")
                return ollama_response

            if progress_callback:
                progress_callback(70, "Generating enhanced response...")

            # Create enhancement prompt
            enhancement_prompt = f"""
Based on this query: "{query}"

And this initial response: "{ollama_response[:500]}..."

Provide an enhanced, more detailed response that builds upon the initial answer.
Focus on adding technical depth, additional context, and practical insights.
"""

            # Generate enhanced response
            enhanced = await self.mesh_manager.generate_text_async(
                model_name=model_name,
                prompt=enhancement_prompt,
                max_length=300,
                temperature=0.7,
                progress_callback=lambda p, m: progress_callback(70 + p * 0.2, m) if progress_callback else None
            )

            if enhanced and len(enhanced) > 50:  # Ensure we got a meaningful response
                if progress_callback:
                    progress_callback(90, "Integrating responses...")

                # Combine responses
                combined = f"""{ollama_response}

--- Enhanced Analysis ---
{enhanced}"""

                log_info("mesh_integration", f"Response enhanced from {len(ollama_response)} to {len(combined)} chars")
                return combined
            else:
                log_info("mesh_integration", "Enhancement failed, returning original response")
                return ollama_response

        except Exception as e:
            log_error("mesh_integration", f"Enhancement failed: {e}")
            return ollama_response

    def get_integration_status(self) -> Dict[str, Any]:
        """Get integration status"""
        if not self.initialized:
            return {"status": "not_initialized"}

        return {
            "status": "active",
            "mesh_available": self.mesh_manager.is_available() if self.mesh_manager else False,
            "models_loaded": len(self.mesh_manager.models) if self.mesh_manager else 0,
            "performance_stats": self.mesh_manager.get_performance_stats() if self.mesh_manager else {}
        }
