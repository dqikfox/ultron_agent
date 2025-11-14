"""VS Code Integration Tool - Open files and projects in VS Code"""
import subprocess
import os
from pathlib import Path

class VSCodeIntegrationTool:
    name = "VS Code Integration"
    description = "Open VS Code with files, folders, and projects"
    
    def __init__(self, config=None, memory=None):
        self.config = config
        self.memory = memory
    
    def match(self, command: str) -> bool:
        keywords = ['vscode', 'vs code', 'code editor', 'open in code']
        return any(k in command.lower() for k in keywords)
    
    def execute(self, command: str, **kwargs) -> str:
        cmd_lower = command.lower()
        
        try:
            # Open current directory
            if 'open project' in cmd_lower or 'open folder' in cmd_lower:
                subprocess.Popen(['code', '.'])
                return f"✅ VS Code opening: {os.getcwd()}"
            
            # Open specific file
            words = command.split()
            for word in words:
                if '.' in word:  # Likely a filename
                    file_path = Path(word)
                    if file_path.exists():
                        subprocess.Popen(['code', str(file_path)])
                        return f"✅ VS Code opening: {file_path}"
            
            # Default: open current directory
            subprocess.Popen(['code', '.'])
            return "✅ VS Code launched"
            
        except Exception as e:
            return f"❌ VS Code error: {str(e)}"
    
    @classmethod
    def schema(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "command": {"type": "string", "description": "VS Code command"}
            }
        }
