"""NAT integration for Ultron Agent"""
import subprocess
import json
from pathlib import Path

class NATIntegration:
    def __init__(self, nat_path="/home/ultro/projects/NeMo-Agent-Toolkit"):
        self.nat_path = Path(nat_path)
        
    def run_nat_workflow(self, config_file, input_text):
        """Execute NAT workflow and return result"""
        cmd = [
            "bash", "-c", 
            f"cd {self.nat_path} && "
            f"source venv/bin/activate && "
            f"export NVIDIA_API_KEY=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 && "
            f"nat run --config_file {config_file} --input '{input_text}'"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout
        
    def create_ultron_workflow(self):
        """Create NAT workflow for Ultron tools"""
        config = {
            "functions": {
                "ultron_voice": {"_type": "current_datetime"},
                "ultron_vision": {"_type": "current_datetime"}
            },
            "llms": {
                "ultron_nim": {
                    "_type": "nim",
                    "model_name": "meta/llama-3.1-8b-instruct",
                    "temperature": 0.0
                }
            },
            "workflow": {
                "_type": "react_agent",
                "tool_names": ["ultron_voice", "ultron_vision"],
                "llm_name": "ultron_nim",
                "verbose": True
            }
        }
        
        with open(self.nat_path / "ultron_workflow.yml", "w") as f:
            import yaml
            yaml.dump(config, f)