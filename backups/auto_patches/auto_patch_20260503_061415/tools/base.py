"""Base Tool Class"""

class Tool:
    name = ""
    description = ""
    
    def match(self, command: str) -> bool:
        return False
    
    def execute(self, **kwargs):
        return "Not implemented"
    
    @staticmethod
    def schema():
        return {}