"""Streamlit Integration Tool - Launch and manage Streamlit apps"""
import subprocess
import os
from pathlib import Path

class StreamlitIntegrationTool:
    name = "Streamlit Integration"
    description = "Launch Streamlit web apps for data visualization and ML demos"
    
    def __init__(self, config=None, memory=None):
        self.config = config
        self.memory = memory
    
    def match(self, command: str) -> bool:
        keywords = ['streamlit', 'dashboard', 'web app', 'data viz']
        return any(k in command.lower() for k in keywords)
    
    def execute(self, command: str, **kwargs) -> str:
        cmd_lower = command.lower()
        
        try:
            # Run specific Streamlit app
            words = command.split()
            for word in words:
                if word.endswith('.py') and 'streamlit' in cmd_lower:
                    file_path = Path(word)
                    if file_path.exists():
                        subprocess.Popen(['streamlit', 'run', str(file_path)])
                        return f"✅ Streamlit app running: {file_path} at http://localhost:8501"
            
            # Look for app.py or main.py
            for filename in ['app.py', 'main.py', 'streamlit_app.py']:
                file_path = Path(filename)
                if file_path.exists():
                    subprocess.Popen(['streamlit', 'run', str(file_path)])
                    return f"✅ Streamlit app running: {filename} at http://localhost:8501"
            
            return "❌ No Streamlit app file found (app.py, main.py, or specify file)"
            
        except Exception as e:
            return f"❌ Streamlit error: {str(e)}"
    
    @classmethod
    def schema(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "command": {"type": "string", "description": "Streamlit command"}
            }
        }
