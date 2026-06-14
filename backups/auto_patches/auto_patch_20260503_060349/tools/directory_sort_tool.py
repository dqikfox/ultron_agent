"""
Directory Sort Tool - Automatic file organization by extension
Implements advantages from ultron.py
"""
import os
import shutil
from pathlib import Path
from utils.ultron_logger import log_info, log_error, log_file_operation

class DirectorySortTool:
    name = "directory_sort"
    description = "Automatically organize files by extension"
    
    def __init__(self, config=None):
        self.config = config or {}
    
    def match(self, command: str) -> bool:
        return any(k in command.lower() for k in ["sort", "organize", "clean folder"])
    
    def execute(self, command: str, **kwargs) -> str:
        try:
            path = kwargs.get("path", os.getcwd())
            return self.sort_directory(path)
        except Exception as e:
            log_error("directory_sort", f"Error: {str(e)}")
            return f"Error: {str(e)}"
    
    def sort_directory(self, path: str) -> str:
        if not os.path.exists(path):
            return f"Path does not exist: {path}"
        
        log_info("directory_sort", f"Sorting files in {path}")
        
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        types = {}
        
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext not in types:
                types[ext] = []
            types[ext].append(f)
        
        moved = 0
        for ext, items in types.items():
            folder_name = ext[1:] if ext else "no_ext"
            folder = os.path.join(path, folder_name)
            os.makedirs(folder, exist_ok=True)
            
            for f in items:
                src = os.path.join(path, f)
                dst = os.path.join(folder, f)
                if not os.path.exists(dst):
                    shutil.move(src, dst)
                    log_file_operation("directory_sort", f"Moved: {f}", dst, "move")
                    moved += 1
        
        log_info("directory_sort", "Auto-sort complete")
        return f"Sorted {moved} file(s) into {len(types)} folder(s)"
    
    def generate_report(self, path: str) -> dict:
        if not os.path.exists(path):
            return {"error": "Path does not exist"}
        
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        total = len(files)
        size = sum(os.path.getsize(os.path.join(path, f)) for f in files)
        
        return {
            "total_files": total,
            "total_size_kb": round(size / 1024, 2),
            "path": path
        }
    
    @classmethod
    def schema(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "path": {"type": "string", "description": "Directory path to sort"}
            }
        }
