"""
Dynamic Tool Loader for ULTRON Agent
Discovers and loads tools at runtime
"""

import os
import importlib
import inspect
from typing import Dict, List, Type, Optional
from .tool_interface import ToolInterface
from utils.ultron_logger import log_info, log_error

class ToolLoader:
    """Dynamic tool discovery and loading"""
    
    def __init__(self, tools_dir: str = "tools"):
        self.tools_dir = tools_dir
        self.loaded_tools: Dict[str, ToolInterface] = {}
        self.tool_classes: Dict[str, Type[ToolInterface]] = {}
    
    def discover_tools(self) -> List[str]:
        """Discover available tool files"""
        tool_files = []
        
        if not os.path.exists(self.tools_dir):
            log_error("tool_loader", f"Tools directory not found: {self.tools_dir}")
            return tool_files
        
        for filename in os.listdir(self.tools_dir):
            if (filename.endswith("_tool.py") and 
                not filename.startswith("__") and
                filename != "tool_interface.py"):
                tool_files.append(filename[:-3])  # Remove .py extension
        
        log_info("tool_loader", f"Discovered {len(tool_files)} tool files")
        return tool_files
    
    def load_tool_module(self, module_name: str) -> bool:
        """Load a single tool module"""
        try:
            module = importlib.import_module(f"{self.tools_dir}.{module_name}")
            
            # Find tool classes in module
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (issubclass(obj, ToolInterface) and 
                    obj != ToolInterface and
                    not inspect.isabstract(obj)):
                    
                    # Instantiate tool
                    tool_instance = obj()
                    tool_name = tool_instance.name
                    
                    self.loaded_tools[tool_name] = tool_instance
                    self.tool_classes[tool_name] = obj
                    
                    log_info("tool_loader", f"Loaded tool: {tool_name}")
                    return True
            
            return False
        except Exception as e:
            log_error("tool_loader", f"Failed to load {module_name}: {e}")
            return False
    
    def load_all_tools(self) -> Dict[str, ToolInterface]:
        """Load all discovered tools"""
        tool_files = self.discover_tools()
        
        for tool_file in tool_files:
            self.load_tool_module(tool_file)
        
        log_info("tool_loader", f"Loaded {len(self.loaded_tools)} tools total")
        return self.loaded_tools
    
    def reload_tool(self, tool_name: str) -> bool:
        """Reload a specific tool (hot-swap)"""
        try:
            if tool_name in self.tool_classes:
                # Find module name
                tool_class = self.tool_classes[tool_name]
                module_name = tool_class.__module__.split(".")[-1]
                
                # Reload module
                module = importlib.reload(importlib.import_module(f"{self.tools_dir}.{module_name}"))
                
                # Re-instantiate tool
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (issubclass(obj, ToolInterface) and 
                        obj != ToolInterface and
                        not inspect.isabstract(obj)):
                        
                        tool_instance = obj()
                        if tool_instance.name == tool_name:
                            self.loaded_tools[tool_name] = tool_instance
                            self.tool_classes[tool_name] = obj
                            log_info("tool_loader", f"Reloaded tool: {tool_name}")
                            return True
            
            return False
        except Exception as e:
            log_error("tool_loader", f"Failed to reload {tool_name}: {e}")
            return False
    
    def get_tool(self, tool_name: str) -> Optional[ToolInterface]:
        """Get a loaded tool by name"""
        return self.loaded_tools.get(tool_name)
    
    def list_tools(self) -> List[str]:
        """List all loaded tool names"""
        return list(self.loaded_tools.keys())
    
    def find_matching_tool(self, command: str) -> Optional[ToolInterface]:
        """Find tool that matches the command"""
        for tool in self.loaded_tools.values():
            if tool.match(command):
                return tool
        return None

# Global tool loader instance
_tool_loader = None

def get_tool_loader() -> ToolLoader:
    """Get global tool loader instance"""
    global _tool_loader
    if _tool_loader is None:
        _tool_loader = ToolLoader()
        _tool_loader.load_all_tools()
    return _tool_loader
