from .base import Tool

class FileTool(Tool):
    name = "file_search"
    description = "Perform file operations such as listing, reading, and writing files."
    parameters = {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["list", "read", "write"], "description": "The file operation to perform."},
            "path": {"type": "string", "description": "The file or directory path."},
            "content": {"type": "string", "description": "Content to write (for write action).", "default": ""}
        },
        "required": ["action", "path"]
    }

    def __init__(self):
        super().__init__()

    def match(self, command: str) -> bool:
        cmd = command.lower()
        return any(x in cmd for x in ["list files", "read file", "write file"])

    def execute(self, command: str = "", path: str = "", content: str = "", action: str = "") -> str:
        if action == "list":
            return str(self.list_files(path or "."))
        elif action == "read":
            if not path:
                return "No file specified."
            return self.read_file(path)
        elif action == "write":
            if not path or content == "":
                return "Usage: write file <path> <content>"
            return self.write_file(path, content)
        else:
            return "Unknown file command."

    def list_files(self, directory: str) -> list:
        """List all files in the given directory."""
        import os
        try:
            return os.listdir(directory)
        except Exception as e:
            return [f"Error listing files: {e}"]

    def read_file(self, file_path: str) -> str:
        """Read the contents of a file."""
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except Exception as e:
            return f"Error reading file: {e}"

    def write_file(self, file_path: str, content: str) -> str:
        """Write content to a file."""
        try:
            with open(file_path, 'w') as file:
                file.write(content)
            return "File written successfully."
        except Exception as e:
            return f"Error writing file: {e}"