class FileTool:
    def __init__(self):
        self.name = "FileTool"
        self.description = "Perform file operations such as listing, reading, and writing files."

    def list_files(self, directory: str) -> list:
        """List all files in the given directory."""
        import os
        try:
            return os.listdir(directory)
        except Exception as e:
            return f"Error listing files: {e}"

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