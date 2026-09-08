class Tool:
    name = "BaseTool"
    description = "Base class for all tools."
    parameters = {}

    def __init__(self):
        pass

    def match(self, command: str) -> bool:
        raise NotImplementedError("Subclasses should implement this method.")

    def execute(self, command: str) -> str:
        raise NotImplementedError("Subclasses should implement this method.")

    @classmethod
    def schema(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": cls.parameters
        }