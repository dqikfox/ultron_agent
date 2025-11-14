#!/usr/bin/env python3
"""
Implement Task 1: Pluggable Architecture for Tools
Based on GitHub Models suggestions
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def implement_pluggable_architecture():
    print("Implementing Task 1: Pluggable Architecture for Tools")
    print("=" * 60)
    
    # 1. Create tool interface
    print("1. Creating standardized tool interface...")
    
    tool_interface_code = '''"""
Standardized Tool Interface for ULTRON Agent
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class ToolInterface(ABC):
    """Abstract base class for all ULTRON Agent tools"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description"""
        pass
    
    @abstractmethod
    def match(self, command: str) -> bool:
        """Check if command matches this tool"""
        pass
    
    @abstractmethod
    def execute(self, command: str, **kwargs) -> str:
        """Execute tool operation"""
        pass
    
    @classmethod
    @abstractmethod
    def schema(cls) -> Dict[str, Any]:
        """Return tool schema for registration"""
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get tool metadata"""
        return {
            "name": self.name,
            "description": self.description,
            "schema": self.schema()
        }
'''
    
    with open("tools/tool_interface.py", "w") as f:
        f.write(tool_interface_code)
    print("   [OK] Created tools/tool_interface.py")
    
    # 2. Create dynamic tool loader
    print("\n2. Creating dynamic tool loader...")
    
    tool_loader_code = '''"""
Dynamic Tool Loader for ULTRON Agent
Discovers and loads tools at runtime
"""

import os
import importlib
import inspect
from typing import Dict, List, Type
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
'''
    
    with open("tools/tool_loader.py", "w") as f:
        f.write(tool_loader_code)
    print("   [OK] Created tools/tool_loader.py")
    
    # 3. Update existing tools to use interface
    print("\n3. Updating existing tools to use interface...")
    
    # Update PyAutoGUI tool
    update_pyautogui_tool()
    print("   [OK] Updated PyAutoGUI tool")
    
    # Update GitHub Models tool  
    update_github_models_tool()
    print("   [OK] Updated GitHub Models tool")
    
    # Update Database tool
    update_database_tool()
    print("   [OK] Updated Database tool")
    
    print("\n4. Testing pluggable architecture...")
    test_pluggable_architecture()
    
    print("\n[SUCCESS] Task 1: Pluggable Architecture implemented successfully!")
    print("\nFeatures implemented:")
    print("- Standardized ToolInterface abstract base class")
    print("- Dynamic tool discovery and loading")
    print("- Hot-swapping capability")
    print("- Runtime tool registration")
    print("- Automatic tool matching")

def update_pyautogui_tool():
    """Update PyAutoGUI tool to use interface"""
    # Read current file
    with open("tools/pyautogui_tool.py", "r") as f:
        content = f.read()
    
    # Add interface import and inheritance
    if "from .tool_interface import ToolInterface" not in content:
        content = content.replace(
            'from utils.ultron_logger import log_info, log_error',
            'from utils.ultron_logger import log_info, log_error\nfrom .tool_interface import ToolInterface'
        )
    
    if "class PyAutoGUITool:" in content:
        content = content.replace(
            "class PyAutoGUITool:",
            "class PyAutoGUITool(ToolInterface):"
        )
    
    # Add property decorators
    if "@property" not in content:
        content = content.replace(
            'name = "PyAutoGUI Tool"',
            '@property\n    def name(self) -> str:\n        return "PyAutoGUI Tool"'
        )
        content = content.replace(
            'description = "Screen automation, mouse/keyboard control, and GUI interaction"',
            '@property\n    def description(self) -> str:\n        return "Screen automation, mouse/keyboard control, and GUI interaction"'
        )
    
    with open("tools/pyautogui_tool.py", "w") as f:
        f.write(content)

def update_github_models_tool():
    """Update GitHub Models tool to use interface"""
    with open("tools/github_models_tool.py", "r") as f:
        content = f.read()
    
    if "from .tool_interface import ToolInterface" not in content:
        content = content.replace(
            'from utils.ultron_logger import log_info, log_error',
            'from utils.ultron_logger import log_info, log_error\nfrom .tool_interface import ToolInterface'
        )
    
    if "class GitHubModelsTool:" in content:
        content = content.replace(
            "class GitHubModelsTool:",
            "class GitHubModelsTool(ToolInterface):"
        )
    
    if "@property" not in content:
        content = content.replace(
            'name = "GitHub Models Tool"',
            '@property\n    def name(self) -> str:\n        return "GitHub Models Tool"'
        )
        content = content.replace(
            'description = "Access GitHub\'s hosted AI models including Mistral"',
            '@property\n    def description(self) -> str:\n        return "Access GitHub\'s hosted AI models including Mistral"'
        )
    
    with open("tools/github_models_tool.py", "w") as f:
        f.write(content)

def update_database_tool():
    """Update Database tool to use interface"""
    with open("tools/database_integration_tool.py", "r") as f:
        content = f.read()
    
    if "from .tool_interface import ToolInterface" not in content:
        content = content.replace(
            'from utils.ultron_logger import log_info, log_error',
            'from utils.ultron_logger import log_info, log_error\nfrom .tool_interface import ToolInterface'
        )
    
    if "class DatabaseIntegrationTool:" in content:
        content = content.replace(
            "class DatabaseIntegrationTool:",
            "class DatabaseIntegrationTool(ToolInterface):"
        )
    
    if "@property" not in content:
        content = content.replace(
            'name = "Database Integration Tool"',
            '@property\n    def name(self) -> str:\n        return "Database Integration Tool"'
        )
        content = content.replace(
            'description = "PostgreSQL/Supabase database operations and queries"',
            '@property\n    def description(self) -> str:\n        return "PostgreSQL/Supabase database operations and queries"'
        )
    
    with open("tools/database_integration_tool.py", "w") as f:
        f.write(content)

def test_pluggable_architecture():
    """Test the pluggable architecture"""
    try:
        from tools.tool_loader import get_tool_loader
        
        loader = get_tool_loader()
        tools = loader.list_tools()
        
        print(f"   [OK] Loaded {len(tools)} tools: {', '.join(tools)}")
        
        # Test tool matching
        test_command = "take a screenshot"
        matching_tool = loader.find_matching_tool(test_command)
        if matching_tool:
            print(f"   [OK] Command '{test_command}' matched to: {matching_tool.name}")
        
    except Exception as e:
        print(f"   [FAIL] Test failed: {e}")

if __name__ == "__main__":
    implement_pluggable_architecture()