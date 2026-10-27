"""Unity Barracuda Integration - Neural network inference in Unity"""

from pathlib import Path
from utils.ultron_logger import log_info, log_error


class UnityBarracudaTool:
    name = "Unity Barracuda"
    description = "Create neural network inference scripts for Unity using Barracuda"
    
    def __init__(self, config=None):
        self.config = config or {}
        self.output_dir = Path("UnityGame/Assets/Scripts/ML")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def match(self, command: str) -> bool:
        keywords = ["barracuda", "neural network", "ml model", "onnx unity"]
        return any(k in command.lower() for k in keywords)
    
    def execute(self, command: str, **kwargs) -> str:
        log_info("unity_barracuda", f"Command: {command}")
        
        if "create" in command.lower() or "generate" in command.lower():
            return self._create_inference_script()
        else:
            return "Usage: 'create barracuda inference script'"
    
    def _create_inference_script(self) -> str:
        """Generate Unity Barracuda inference script"""
        script = """using Unity.Barracuda;
using UnityEngine;

public class BarracudaInference : MonoBehaviour
{
    public NNModel modelAsset;
    private Model runtimeModel;
    private IWorker worker;

    void Start()
    {
        // Load model
        runtimeModel = ModelLoader.Load(modelAsset);
        
        // Create worker (GPU compute backend)
        worker = WorkerFactory.CreateWorker(WorkerFactory.Type.ComputePrecompiled, runtimeModel);
    }

    public float[] RunInference(float[] inputData, int[] inputShape)
    {
        // Create input tensor
        Tensor input = new Tensor(inputShape[0], inputShape[1], inputShape[2], inputShape[3], inputData);
        
        // Execute model
        worker.Execute(input);
        
        // Get output
        Tensor output = worker.PeekOutput();
        float[] results = output.ToReadOnlyArray();
        
        // Cleanup
        input.Dispose();
        
        return results;
    }

    void OnDestroy()
    {
        worker?.Dispose();
    }
}"""
        
        output_path = self.output_dir / "BarracudaInference.cs"
        output_path.write_text(script, encoding='utf-8')
        
        # Create example usage script
        example = """using UnityEngine;

public class MLExample : MonoBehaviour
{
    public BarracudaInference inference;

    void Start()
    {
        // Example: Run inference on 28x28 grayscale image
        float[] imageData = new float[28 * 28];
        // ... fill imageData ...
        
        int[] shape = new int[] { 1, 28, 28, 1 }; // batch, height, width, channels
        float[] results = inference.RunInference(imageData, shape);
        
        Debug.Log($"Inference result: {results[0]}");
    }
}"""
        
        example_path = self.output_dir / "MLExample.cs"
        example_path.write_text(example, encoding='utf-8')
        
        log_info("unity_barracuda", f"Created: {output_path}")
        return f"Barracuda scripts created:\n{output_path}\n{example_path}"
    
    @classmethod
    def schema(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "command": {"type": "string", "description": "Barracuda command"}
            }
        }
