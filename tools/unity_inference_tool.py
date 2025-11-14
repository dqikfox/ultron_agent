"""Unity AI Inference Integration - Create and run models per Unity docs"""

import requests
import json
from pathlib import Path
from utils.ultron_logger import log_info, log_error


class UnityInferenceTool:
    name = "Unity AI Inference"
    description = "Create and run ML models in Unity using Sentis runtime"
    
    def __init__(self, config=None):
        self.config = config or {}
        self.bridge_url = self.config.get("unity_bridge_url", "http://localhost:8765")
        self.models_dir = Path("UnityGame/Assets/Models")
        self.models_dir.mkdir(parents=True, exist_ok=True)
    
    def match(self, command: str) -> bool:
        keywords = ["inference", "run model", "create model", "sentis", "onnx"]
        return any(k in command.lower() for k in keywords)
    
    def execute(self, command: str, **kwargs) -> str:
        log_info("unity_inference", f"Command: {command}")
        
        if "create model" in command.lower():
            return self._create_model(command)
        elif "run model" in command.lower() or "inference" in command.lower():
            return self._run_model(command)
        else:
            return "Usage: 'create model [type]' or 'run model [name] with [input]'"
    
    def _create_model(self, prompt: str) -> str:
        """Generate Unity C# script for model inference"""
        script = f"""using Unity.Sentis;
using UnityEngine;

public class ModelRunner : MonoBehaviour
{{
    public ModelAsset modelAsset;
    private IWorker worker;
    private Model runtimeModel;

    void Start()
    {{
        // Load model
        runtimeModel = ModelLoader.Load(modelAsset);
        worker = WorkerFactory.CreateWorker(BackendType.GPUCompute, runtimeModel);
    }}

    public Tensor RunInference(Tensor input)
    {{
        // Execute model
        worker.Execute(input);
        
        // Get output
        TensorFloat output = worker.PeekOutput() as TensorFloat;
        return output;
    }}

    void OnDestroy()
    {{
        worker?.Dispose();
    }}
}}"""
        
        output_path = self.models_dir.parent / "Scripts" / "ModelRunner.cs"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(script)
        
        log_info("unity_inference", f"Created: {output_path}")
        return f"Model runner created: {output_path}"
    
    def _run_model(self, command: str) -> str:
        """Run inference via bridge"""
        try:
            r = requests.post(
                f"{self.bridge_url}/inference",
                json={"input": command},
                timeout=30
            )
            if r.status_code == 200:
                result = r.json().get("output", "")
                log_info("unity_inference", "Inference complete")
                return f"Output: {result}"
            return f"Error: {r.status_code}"
        except Exception as e:
            log_error("unity_inference", str(e))
            return f"Error: {str(e)}"
    
    @classmethod
    def schema(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "command": {"type": "string", "description": "Model command"}
            }
        }
