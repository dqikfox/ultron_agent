#!/usr/bin/env python3
"""
Auto-discover and document all ULTRON Agent tools.
Generates a comprehensive tool inventory for AI developer guidance.
"""

import os
import re
import ast
from pathlib import Path
from typing import Dict, List, Tuple

def extract_tool_info(filepath: str) -> Dict:
    """Extract tool metadata from Python file."""
    info = {
        "file": Path(filepath).name,
        "path": filepath,
        "class": None,
        "docstring": None,
        "methods": [],
        "inherits_from": None
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    info["class"] = node.name
                    info["docstring"] = ast.get_docstring(node)
                    
                    # Check inheritance
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            info["inherits_from"] = base.id
                    
                    # Extract methods
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            info["methods"].append(item.name)
    except Exception as e:
        info["error"] = str(e)
    
    return info

def discover_tools(tools_dir: str = "tools") -> List[Dict]:
    """Discover all tools in the tools directory."""
    tools = []
    
    if not os.path.isdir(tools_dir):
        return tools
    
    for filename in sorted(os.listdir(tools_dir)):
        if filename.endswith(".py") and not filename.startswith("_"):
            filepath = os.path.join(tools_dir, filename)
            tool_info = extract_tool_info(filepath)
            tools.append(tool_info)
    
    return tools

def categorize_tools(tools: List[Dict]) -> Dict[str, List[Dict]]:
    """Categorize tools by function."""
    categories = {
        "Cloud & Infrastructure": [],
        "Development Tools": [],
        "Memory & Data": [],
        "Mobile & Web": [],
        "Automation & Integration": [],
        "AI & Model Inference": [],
        "System & Platform": [],
        "GUI & Interface": [],
        "Other": []
    }
    
    for tool in tools:
        filename_lower = tool["file"].lower()
        
        if any(x in filename_lower for x in ["aws", "cloud", "docker", "redis", "cheap"]):
            categories["Cloud & Infrastructure"].append(tool)
        elif any(x in filename_lower for x in ["project", "dependency", "analyzer", "autogen"]):
            categories["Development Tools"].append(tool)
        elif any(x in filename_lower for x in ["memory", "context"]):
            categories["Memory & Data"].append(tool)
        elif any(x in filename_lower for x in ["mobile", "web", "browser", "adb"]):
            categories["Mobile & Web"].append(tool)
        elif any(x in filename_lower for x in ["autopilot", "automation", "sync", "integration"]):
            categories["Automation & Integration"].append(tool)
        elif any(x in filename_lower for x in ["bedrock", "unity", "inference", "avatar", "barracuda"]):
            categories["AI & Model Inference"].append(tool)
        elif any(x in filename_lower for x in ["windows", "system"]):
            categories["System & Platform"].append(tool)
        elif any(x in filename_lower for x in ["gui", "interface", "validation"]):
            categories["GUI & Interface"].append(tool)
        else:
            categories["Other"].append(tool)
    
    return categories

def generate_markdown(tools: List[Dict], categories: Dict[str, List[Dict]]) -> str:
    """Generate comprehensive markdown documentation."""
    md = []
    md.append("# ULTRON Agent Tools Inventory\n")
    md.append("Auto-generated tool discovery and documentation.\n")
    md.append(f"**Total Tools Found:** {len(tools)}\n")
    
    # Table of Contents
    md.append("## Tool Categories\n")
    for category, cat_tools in categories.items():
        if cat_tools:
            md.append(f"- **{category}** ({len(cat_tools)} tools)")
    
    md.append("\n---\n")
    
    # Detailed listing by category
    for category, cat_tools in categories.items():
        if not cat_tools:
            continue
        
        md.append(f"\n## {category} ({len(cat_tools)})\n")
        
        for tool in cat_tools:
            md.append(f"\n### {tool['class'] or tool['file']}\n")
            md.append(f"- **File:** `{tool['file']}`")
            md.append(f"- **Inherits From:** `{tool['inherits_from']}`" if tool['inherits_from'] else "- **Inherits From:** ToolInterface (standard)")
            
            if tool.get('docstring'):
                md.append(f"- **Description:** {tool['docstring'][:200]}")
            
            if tool['methods']:
                public_methods = [m for m in tool['methods'] if not m.startswith('_')]
                if public_methods:
                    md.append(f"- **Public Methods:** {', '.join(public_methods[:5])}")
                    if len(public_methods) > 5:
                        md.append(f"  ... and {len(public_methods) - 5} more")
            
            if tool.get('error'):
                md.append(f"- ⚠️ **Parse Error:** {tool['error']}")
    
    # How to discover tools at runtime
    md.append("\n---\n")
    md.append("\n## Runtime Tool Discovery\n")
    md.append("""
To discover all available tools at runtime:

```python
from tools.tool_loader import ToolLoader

# Initialize tool loader
loader = ToolLoader()
tools = loader.load_all_tools()

# List available tools
for tool_name, tool_instance in tools.items():
    print(f"{tool_name}: {tool_instance.__class__.__name__}")
```

**Key Points:**
- Tools are auto-discovered from the `tools/` directory
- All tool classes must inherit from `ToolInterface`
- New tools are automatically loaded—no manual registration needed
- Tool loading happens in `tools/tool_loader.py`
""")
    
    # How to add new tools
    md.append("\n## Adding New Tools\n")
    md.append("""
1. Create a new Python file in the `tools/` directory (e.g., `my_tool.py`)
2. Inherit from `ToolInterface`:

```python
from tools.tool_interface import ToolInterface

class MyTool(ToolInterface):
    def __init__(self):
        super().__init__("my_tool", "Tool description")
    
    def execute(self, **kwargs):
        # Your implementation
        return result
```

3. The tool will be automatically discovered on next startup
4. No manual registration or import needed
""")
    
    return "\n".join(md)

if __name__ == "__main__":
    print("Discovering ULTRON Agent tools...")
    tools = discover_tools()
    categories = categorize_tools(tools)
    
    print(f"Found {len(tools)} tools across {len([c for c in categories.values() if c])} categories\n")
    
    # Print summary
    for category, cat_tools in categories.items():
        if cat_tools:
            print(f"  {category}: {len(cat_tools)} tools")
    
    # Generate documentation
    markdown = generate_markdown(tools, categories)
    
    # Save to file
    output_file = "TOOLS_INVENTORY.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    print(f"\n✅ Documentation generated: {output_file}")
