from __future__ import annotations

from typing import List, Optional, Dict, Any


class ModelManager:
    """
    Simple multi-model coordination facade around a provided config-like object.
    Expects config to have get/set/save_config methods (gracefully degrades otherwise).
    """
    def __init__(self, config: Optional[Any] = None):
        self.config = config

    def available_models(self) -> List[str]:
        if self.config and hasattr(self.config, "get"):
            return list(self.config.get("ollama_models", [])) or ["qwen2.5:latest", "llama3.2:latest"]
        return ["qwen2.5:latest", "llama3.2:latest"]

    def active_model(self) -> str:
        models = self.available_models()
        if self.config and hasattr(self.config, "get"):
            return self.config.get("llm_model", models[0])
        return models[0]

    def set_active_model(self, model: str) -> None:
        if self.config and hasattr(self.config, "set"):
            self.config.set("llm_model", model)
            if hasattr(self.config, "save_config"):
                self.config.save_config()