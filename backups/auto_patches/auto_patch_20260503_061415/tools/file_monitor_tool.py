"""
File Monitor Tool - Real-time directory monitoring with change detection
Implements advantages from ultron_prelink.py
"""
import os
import time
from datetime import datetime
from utils.ultron_logger import log_info, log_error

class FileMonitorTool:
    name = "file_monitor"
    description = "Monitor directories for file changes in real-time"
    
    def __init__(self, config=None):
        self.config = config or {}
        self.monitored_paths = {}
    
    def match(self, command: str) -> bool:
        return any(k in command.lower() for k in ["monitor", "watch folder", "track changes"])
    
    def execute(self, command: str, **kwargs) -> str:
        try:
            if "start" in command.lower():
                path = kwargs.get("path", os.path.expanduser("~/Documents"))
                return self.start_monitoring(path)
            elif "stop" in command.lower():
                return self.stop_monitoring()
            elif "status" in command.lower():
                return self.get_status()
            else:
                return "Usage: monitor start <path> | monitor stop | monitor status"
        except Exception as e:
            log_error("file_monitor", f"Error: {str(e)}")
            return f"Error: {str(e)}"
    
    def start_monitoring(self, path: str) -> str:
        if not os.path.exists(path):
            return f"Path does not exist: {path}"
        
        self.monitored_paths[path] = set(os.listdir(path))
        log_info("file_monitor", f"Started monitoring: {path}")
        return f"Monitoring started for: {path}"
    
    def check_changes(self, path: str) -> dict:
        if path not in self.monitored_paths:
            return {"error": "Path not monitored"}
        
        current = set(os.listdir(path))
        previous = self.monitored_paths[path]
        
        created = current - previous
        deleted = previous - current
        
        self.monitored_paths[path] = current
        
        return {
            "created": list(created),
            "deleted": list(deleted),
            "timestamp": datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        }
    
    def stop_monitoring(self) -> str:
        count = len(self.monitored_paths)
        self.monitored_paths.clear()
        return f"Stopped monitoring {count} path(s)"
    
    def get_status(self) -> str:
        if not self.monitored_paths:
            return "No paths currently monitored"
        return f"Monitoring {len(self.monitored_paths)} path(s): {', '.join(self.monitored_paths.keys())}"
    
    @classmethod
    def schema(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "path": {"type": "string", "description": "Directory path to monitor"}
            }
        }
