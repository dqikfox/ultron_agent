#!/usr/bin/env python3
"""
ULTRON Agent Documentation Generator

This script analyzes the codebase and generates API documentation
by extracting class definitions, methods, and docstrings.
"""

import os
import re
import ast
from pathlib import Path
from typing import Dict, List, Any


class DocumentationGenerator:
    """Generate documentation from Python source code."""
    
    def __init__(self, source_dir: str = "."):
        self.source_dir = Path(source_dir)
        self.api_docs = {}
        
    def extract_docstring(self, node: ast.AST) -> str:
        """Extract docstring from AST node."""
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
            if (node.body and 
                isinstance(node.body[0], ast.Expr) and 
                isinstance(node.body[0].value, ast.Constant) and
                isinstance(node.body[0].value.value, str)):
                return node.body[0].value.value
        return ""
    
    def analyze_class(self, node: ast.ClassDef) -> Dict[str, Any]:
        """Analyze a class definition."""
        class_info = {
            "name": node.name,
            "docstring": self.extract_docstring(node),
            "methods": [],
            "properties": []
        }
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = {
                    "name": item.name,
                    "docstring": self.extract_docstring(item),
                    "is_async": False,
                    "args": [arg.arg for arg in item.args.args],
                    "decorators": [dec.id if isinstance(dec, ast.Name) else str(dec) for dec in item.decorator_list]
                }
                class_info["methods"].append(method_info)
            elif isinstance(item, ast.AsyncFunctionDef):
                method_info = {
                    "name": item.name,
                    "docstring": self.extract_docstring(item),
                    "is_async": True,
                    "args": [arg.arg for arg in item.args.args],
                    "decorators": [dec.id if isinstance(dec, ast.Name) else str(dec) for dec in item.decorator_list]
                }
                class_info["methods"].append(method_info)
                
        return class_info
    
    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            file_info = {
                "file": str(file_path),
                "module_docstring": self.extract_docstring(tree),
                "classes": [],
                "functions": []
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Only include top-level classes
                    if any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree) if hasattr(parent, 'body') and node in getattr(parent, 'body', [])):
                        continue
                    class_info = self.analyze_class(node)
                    file_info["classes"].append(class_info)
                    
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Only include top-level functions
                    if any(isinstance(parent, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) 
                           for parent in ast.walk(tree) if hasattr(parent, 'body') and node in getattr(parent, 'body', [])):
                        continue
                        
                    func_info = {
                        "name": node.name,
                        "docstring": self.extract_docstring(node),
                        "is_async": isinstance(node, ast.AsyncFunctionDef),
                        "args": [arg.arg for arg in node.args.args]
                    }
                    file_info["functions"].append(func_info)
            
            return file_info
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return {"file": str(file_path), "error": str(e)}
    
    def generate_markdown(self, file_info: Dict[str, Any]) -> str:
        """Generate markdown documentation for a file."""
        md = []
        
        # File header
        filename = Path(file_info["file"]).name
        md.append(f"## {filename}\n")
        
        if file_info.get("module_docstring"):
            md.append(f"{file_info['module_docstring']}\n")
        
        # Classes
        for class_info in file_info.get("classes", []):
            md.append(f"### Class: `{class_info['name']}`\n")
            
            if class_info["docstring"]:
                md.append(f"{class_info['docstring']}\n")
            
            # Methods
            for method in class_info["methods"]:
                async_prefix = "async " if method["is_async"] else ""
                args_str = ", ".join(method["args"])
                md.append(f"#### `{async_prefix}{method['name']}({args_str})`\n")
                
                if method["docstring"]:
                    md.append(f"{method['docstring']}\n")
                
                if method["decorators"]:
                    decorators = ", ".join(method["decorators"])
                    md.append(f"**Decorators:** {decorators}\n")
                
                md.append("")
        
        # Top-level functions
        for func in file_info.get("functions", []):
            async_prefix = "async " if func["is_async"] else ""
            args_str = ", ".join(func["args"])
            md.append(f"### Function: `{async_prefix}{func['name']}({args_str})`\n")
            
            if func["docstring"]:
                md.append(f"{func['docstring']}\n")
        
        return "\n".join(md)
    
    def generate_api_docs(self, output_file: str = "docs/API_REFERENCE.md"):
        """Generate complete API documentation."""
        core_files = [
            "agent_core.py",
            "brain.py", 
            "voice_manager.py",
            "config.py",
            "memory.py",
            "main.py"
        ]
        
        all_docs = [
            "# ULTRON Agent API Reference",
            "",
            "Auto-generated API documentation from source code analysis.",
            "",
            "## Table of Contents",
            ""
        ]
        
        file_docs = []
        
        for filename in core_files:
            file_path = self.source_dir / filename
            if file_path.exists():
                print(f"Analyzing {filename}...")
                file_info = self.analyze_file(file_path)
                
                if "error" not in file_info:
                    # Add to table of contents
                    all_docs.append(f"- [{filename}](#{filename.replace('.py', '').replace('_', '-')})")
                    
                    # Generate documentation
                    doc = self.generate_markdown(file_info)
                    file_docs.append(doc)
        
        all_docs.extend(["", "---", ""])
        all_docs.extend(file_docs)
        
        # Write documentation
        output_path = Path(output_file)
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(all_docs))
        
        print(f"API documentation generated: {output_path}")


def main():
    """Generate API documentation."""
    generator = DocumentationGenerator()
    generator.generate_api_docs()
    print("Documentation generation complete!")


if __name__ == "__main__":
    main()