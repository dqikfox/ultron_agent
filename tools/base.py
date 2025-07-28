class Tool:
    def __init__(self):
        self.name = "BaseTool"
        self.description = "Base class for all tools."
    
    def match(self, command: str) -> bool:
        raise NotImplementedError("Subclasses should implement this method.")
    
    def execute(self, command: str) -> str:
        raise NotImplementedError("Subclasses should implement this method.")