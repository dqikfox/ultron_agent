"""Unity AI Integration Tool - Connects Unity AI Assistant, Generators, and Inference to ULTRON"""

import requests
import json
from utils.ultron_logger import log_info, log_error, log_ai_decision


class UnityAITool:
    name = "Unity AI Integration"
    description = "Interface with Unity AI Assistant, Generators, and Inference engine"
    
    def __init__(self, config=None):
        self.config = config or {}
        self.unity_host = self.config.get("unity_host", "http://localhost:8765")
        self.inference_port = self.config.get("unity_inference_port", 8080)
    
    def match(self, command: str) -> bool:
        keywords = ["unity", "generate asset", "run model", "unity ai", "inference"]
        return any(k in command.lower() for k in keywords)
    
    def execute(self, command: str, **kwargs) -> str:
        log_info("unity_ai_tool", f"Processing: {command}")
        
        cmd_lower = command.lower()
        
        if "generate" in cmd_lower or "asset" in cmd_lower:
            return self._generate_asset(command)
        elif "inference" in cmd_lower or "run model" in cmd_lower:
            return self._run_inference(command)
        elif "assistant" in cmd_lower or "help" in cmd_lower:
            return self._query_assistant(command)
        else:
            return self._query_assistant(command)
    
    def _generate_asset(self, prompt: str) -> str:
        """Generate Unity assets using AI Generators"""
        try:
            payload = {"prompt": prompt, "type": "auto"}
            response = requests.post(
                f"{self.unity_host}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                log_ai_decision("unity_ai_tool", "Asset generated", ai_model="unity_generator")
                return f"Generated: {result.get('asset_path', 'asset')}"
            else:
                return f"Generation failed: {response.status_code}"
        except Exception as e:
            log_error("unity_ai_tool", f"Generation error: {str(e)}")
            return f"Error: {str(e)}"
    
    def _run_inference(self, command: str) -> str:
        """Run ML model inference via Unity AI Inference"""
        try:
            payload = {"input": command}
            response = requests.post(
                f"http://localhost:{self.inference_port}/inference",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                log_ai_decision("unity_ai_tool", "Inference complete", ai_model="unity_inference")
                return f"Result: {result.get('output', 'No output')}"
            else:
                return f"Inference failed: {response.status_code}"
        except Exception as e:
            log_error("unity_ai_tool", f"Inference error: {str(e)}")
            return f"Error: {str(e)}"
    
    def _query_assistant(self, query: str) -> str:
        """Query Unity AI Assistant"""
        try:
            payload = {"query": query}
            response = requests.post(
                f"{self.unity_host}/api/assistant",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                log_ai_decision("unity_ai_tool", "Assistant query", ai_model="unity_assistant")
                return result.get("response", "No response")
            else:
                return f"Query failed: {response.status_code}"
        except Exception as e:
            log_error("unity_ai_tool", f"Assistant error: {str(e)}")
            return f"Error: {str(e)}"
    
    @classmethod
    def schema(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "command": {"type": "string", "description": "Unity AI command"}
            }
        }
