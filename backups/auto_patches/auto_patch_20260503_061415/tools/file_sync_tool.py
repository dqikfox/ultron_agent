"""
File Sync Tool - Automated file synchronization with versioning
Implements advantages from ultronwatchdog.py
"""
import os
import shutil
import hashlib
from datetime import datetime
from pathlib import Path
from utils.ultron_logger import log_info, log_error, log_file_operation

class FileSyncTool:
    name = "file_sync"
    description = "Synchronize files between directories with versioning"
    
    def __init__(self, config=None):
        self.config = config or {}
        self.file_hashes = {}
    
    def match(self, command: str) -> bool:
        return any(k in command.lower() for k in ["sync", "backup", "mirror"])
    
    def execute(self, command: str, **kwargs) -> str:
        try:
            source = kwargs.get("source")
            dest = kwargs.get("dest")
            
            if not source or not dest:
                return "Usage: sync <source> <dest>"
            
            return self.sync_directories(source, dest)
        except Exception as e:
            log_error("file_sync", f"Error: {str(e)}")
            return f"Error: {str(e)}"
    
    def hash_file(self, path: str) -> str:
        with open(path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def archive_file(self, src_path: str, rel_path: str, version_dir: str):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_path = os.path.join(version_dir, f"{timestamp}_{rel_path.replace(os.sep, '_')}")
        os.makedirs(os.path.dirname(version_path), exist_ok=True)
        shutil.copy2(src_path, version_path)
        log_file_operation("file_sync", f"Archived: {rel_path}", version_path, "archive")
    
    def sync_directories(self, source: str, dest: str) -> str:
        if not os.path.exists(source):
            return f"Source does not exist: {source}"
        
        os.makedirs(dest, exist_ok=True)
        version_dir = os.path.join(source, ".versions")
        os.makedirs(version_dir, exist_ok=True)
        
        synced = 0
        for root, _, files in os.walk(source):
            if ".versions" in root:
                continue
            
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, source)
                dest_path = os.path.join(dest, rel_path)
                
                try:
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    current_hash = self.hash_file(full_path)
                    
                    if rel_path not in self.file_hashes or self.file_hashes[rel_path] != current_hash:
                        if os.path.exists(dest_path):
                            self.archive_file(dest_path, rel_path, version_dir)
                        shutil.copy2(full_path, dest_path)
                        self.file_hashes[rel_path] = current_hash
                        synced += 1
                        log_info("file_sync", f"Synced: {rel_path}")
                except Exception as e:
                    log_error("file_sync", f"Failed to sync {rel_path}: {str(e)}")
        
        return f"Sync complete: {synced} file(s) synchronized"
    
    @classmethod
    def schema(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "source": {"type": "string", "description": "Source directory"},
                "dest": {"type": "string", "description": "Destination directory"}
            }
        }
