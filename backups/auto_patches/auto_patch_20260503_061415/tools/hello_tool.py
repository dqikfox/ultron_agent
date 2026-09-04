"""Hello Tool - Friendly greeting tool created via automated orchestration"""
from utils.ultron_logger import log_info

class HelloTool:
    name = "hello_tool"
    description = "Friendly greeting tool"
    
    def match(self, command: str) -> bool:
        """Match commands containing 'hello' or 'hi'"""
        return "hello" in command.lower() or "hi" in command.lower()
    
    def execute(self, command: str) -> str:
        """Execute greeting with optional name extraction"""
        log_info("hello_tool", f"Executing: {command}")
        
        # Extract name if provided
        words = command.split()
        name = "there"
        if len(words) > 1:
            last_word = words[-1]
            if last_word.lower() not in ["hello", "hi"]:
                name = last_word
        
        return f"Hello {name}! How can I help you today?"
    
    @classmethod
    def schema(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {}
        }
