"""Redis Integration - Manage Redis cache and data"""
import subprocess

class RedisIntegrationTool:
    name = "Redis Integration"
    description = "Manage Redis cache server and data operations"
    
    def __init__(self, config=None, memory=None):
        self.config = config
        self.memory = memory
    
    def match(self, command: str) -> bool:
        return 'redis' in command.lower()
    
    def execute(self, command: str, **kwargs) -> str:
        try:
            import redis
            cmd_lower = command.lower()
            
            if 'start' in cmd_lower or 'launch' in cmd_lower:
                subprocess.Popen(['redis-server'])
                return "✅ Redis server starting on port 6379"
            
            if 'status' in cmd_lower or 'check' in cmd_lower:
                r = redis.Redis(host='localhost', port=6379, decode_responses=True)
                r.ping()
                return "✅ Redis is running and responsive"
            
            return "❌ Unknown Redis command. Try: start, status"
        except Exception as e:
            return f"❌ Redis error: {str(e)}"
    
    @classmethod
    def schema(cls):
        return {"name": cls.name, "description": cls.description}
