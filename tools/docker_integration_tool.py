"""Docker Integration Tool - Manage containers and images"""
import subprocess

class DockerIntegrationTool:
    name = "Docker Integration"
    description = "Manage Docker containers, images, and services"
    
    def __init__(self, config=None, memory=None):
        self.config = config
        self.memory = memory
    
    def match(self, command: str) -> bool:
        keywords = ['docker', 'container', 'image', 'compose']
        return any(k in command.lower() for k in keywords)
    
    def execute(self, command: str, **kwargs) -> str:
        cmd_lower = command.lower()
        
        try:
            # List containers
            if 'list' in cmd_lower or 'ps' in cmd_lower:
                result = subprocess.run(['docker', 'ps', '-a'], capture_output=True, text=True)
                return f"✅ Docker containers:\n{result.stdout}"
            
            # List images
            if 'images' in cmd_lower:
                result = subprocess.run(['docker', 'images'], capture_output=True, text=True)
                return f"✅ Docker images:\n{result.stdout}"
            
            # Start container
            if 'start' in cmd_lower:
                words = command.split()
                if len(words) > 1:
                    container = words[-1]
                    result = subprocess.run(['docker', 'start', container], capture_output=True, text=True)
                    return f"✅ Started container: {container}"
                return "❌ Specify container name"
            
            # Stop container
            if 'stop' in cmd_lower:
                words = command.split()
                if len(words) > 1:
                    container = words[-1]
                    result = subprocess.run(['docker', 'stop', container], capture_output=True, text=True)
                    return f"✅ Stopped container: {container}"
                return "❌ Specify container name"
            
            # Docker compose
            if 'compose' in cmd_lower:
                if 'up' in cmd_lower:
                    subprocess.Popen(['docker-compose', 'up', '-d'])
                    return "✅ Docker Compose starting services"
                if 'down' in cmd_lower:
                    subprocess.run(['docker-compose', 'down'])
                    return "✅ Docker Compose stopped services"
            
            return "❌ Unknown Docker command. Try: list, images, start, stop, compose"
            
        except Exception as e:
            return f"❌ Docker error: {str(e)}"
    
    @classmethod
    def schema(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "command": {"type": "string", "description": "Docker command"}
            }
        }
