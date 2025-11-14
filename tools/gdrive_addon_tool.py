"""GDrive ULTRON Addon Integration Tool"""
import requests

class GDriveAddonTool:
    name = "gdrive_addon"
    description = "Access GDrive ULTRON Node.js addon (OpenAI chat, file uploads)"
    
    def __init__(self):
        self.base_url = "http://localhost:3001"
    
    def match(self, command: str) -> bool:
        return "gdrive" in command.lower() or "node chat" in command.lower()
    
    def execute(self, command: str, **kwargs) -> str:
        if "upload" in command.lower():
            return "Use POST /upload with multipart/form-data"
        
        try:
            response = requests.post(f"{self.base_url}/chat", 
                json={"message": command}, timeout=30)
            return response.json().get("response", "No response")
        except Exception as e:
            return f"GDrive addon offline: {e}"
    
    @classmethod
    def schema(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {"command": {"type": "string"}}
        }
