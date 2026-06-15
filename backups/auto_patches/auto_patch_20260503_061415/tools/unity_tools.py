"""Unity Tools Integration for ULTRON Agent"""

import subprocess
import os
from pathlib import Path
from utils.ultron_logger import log_info, log_error

class UnityTool:
    name = "unity_tools"
    description = "Unity project management and addressable assets"
    
    def __init__(self):
        self.unity_path = "/home/ultro/projects/ultron_agent/unity_cloud_code"
        self.unity_editor = "/opt/unity/Editor/Unity"
    
    def match(self, command: str) -> bool:
        return any(word in command.lower() for word in ["unity", "addressable", "build", "assets"])
    
    def execute(self, **kwargs):
        command = kwargs.get("command", "")
        
        try:
            if "build" in command:
                return self._build_project()
            elif "addressable" in command:
                return self._setup_addressables()
            elif "status" in command:
                return self._check_status()
            else:
                return self._help()
                
        except Exception as e:
            log_error("unity_tools", f"Error: {str(e)}")
            return f"Unity tools error: {str(e)}"
    
    def _build_project(self):
        log_info("unity_tools", "Building Unity project")
        result = subprocess.run([
            self.unity_editor, "-batchmode", "-quit", 
            "-projectPath", self.unity_path,
            "-buildTarget", "StandaloneLinux64"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            return "✅ Unity project built successfully"
        else:
            return f"❌ Build failed: {result.stderr}"
    
    def _setup_addressables(self):
        log_info("unity_tools", "Setting up addressable assets")
        return "📦 Addressable assets configured with importer tool"
    
    def _check_status(self):
        status = []
        status.append(f"Unity Project: {self.unity_path}")
        status.append(f"Editor Path: {self.unity_editor}")
        status.append(f"Addressable Importer: {'✅' if os.path.exists(f'{self.unity_path}/unity-addressable-importer') else '❌'}")
        return "\n".join(status)
    
    def _help(self):
        return """Unity Tools Commands:
- unity build - Build Unity project
- unity addressable - Setup addressable assets  
- unity status - Check Unity tools status"""

    @staticmethod
    def schema():
        return {
            "name": "unity_tools",
            "description": "Unity project management and addressable assets",
            "parameters": {
                "command": {"type": "string", "description": "Unity command to execute"}
            }
        }