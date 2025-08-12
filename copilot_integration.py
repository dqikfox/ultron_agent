"""
GitHub Copilot Integration for ULTRON Agent 3.0
Provides enhanced AI assistance with project context and Python script access
"""

import os
import ast
import json
import subprocess
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from security_utils import sanitize_log_input, validate_file_path
from integration_manager import integration_manager

class CopilotIntegration:
    """Enhanced Copilot integration with project context."""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.logger = logging.getLogger(__name__)
        self.context_cache = {}
        self.script_registry = {}
        self._scan_project_scripts()
        
    def _scan_project_scripts(self):
        """Scan and register all Python scripts in the project."""
        try:
            for py_file in self.project_root.rglob("*.py"):
                if validate_file_path(str(py_file.relative_to(self.project_root))):
                    self.script_registry[py_file.stem] = {
                        'path': py_file,
                        'functions': self._extract_functions(py_file),
                        'classes': self._extract_classes(py_file),
                        'imports': self._extract_imports(py_file)
                    }
        except Exception as e:
            self.logger.error(f"Script scanning failed: {sanitize_log_input(str(e))}")
    
    def _extract_functions(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract function definitions from Python file."""
        functions = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
                
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        'name': node.name,
                        'args': [arg.arg for arg in node.args.args],
                        'docstring': ast.get_docstring(node),
                        'line': node.lineno,
                        'is_async': isinstance(node, ast.AsyncFunctionDef)
                    })
        except Exception as e:
            self.logger.warning(f"Function extraction failed for {file_path}: {str(e)}")
        return functions
    
    def _extract_classes(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract class definitions from Python file."""
        classes = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
                
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = []
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            methods.append({
                                'name': item.name,
                                'args': [arg.arg for arg in item.args.args],
                                'line': item.lineno
                            })
                    
                    classes.append({
                        'name': node.name,
                        'methods': methods,
                        'docstring': ast.get_docstring(node),
                        'line': node.lineno
                    })
        except Exception as e:
            self.logger.warning(f"Class extraction failed for {file_path}: {str(e)}")
        return classes
    
    def _extract_imports(self, file_path: Path) -> List[str]:
        """Extract import statements from Python file."""
        imports = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
                
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")
        except Exception as e:
            self.logger.warning(f"Import extraction failed for {file_path}: {str(e)}")
        return imports
    
    def get_project_context(self) -> Dict[str, Any]:
        """Generate comprehensive project context for Copilot."""
        return {
            'project_name': 'ULTRON Agent 3.0',
            'project_root': str(self.project_root),
            'scripts': {name: {
                'path': str(info['path']),
                'functions': [f['name'] for f in info['functions']],
                'classes': [c['name'] for c in info['classes']],
                'key_imports': info['imports'][:10]  # Top 10 imports
            } for name, info in self.script_registry.items()},
            'architecture': {
                'core_modules': ['agent_core', 'brain', 'config', 'gui_ultimate'],
                'security_modules': ['security_utils'],
                'integration_modules': ['integration_manager', 'performance_optimizer'],
                'ai_integrations': ['Amazon Q', 'GitHub Copilot', 'Sixth AI']
            }
        }
    
    def generate_copilot_context_file(self):
        """Generate .copilot-context.json for enhanced suggestions."""
        context = {
            "version": "1.0",
            "project": {
                "name": "ULTRON Agent 3.0",
                "description": "Advanced AI agent with multi-modal capabilities",
                "type": "python-ai-agent"
            },
            "codebase": {
                "patterns": {
                    "security": "Always use security_utils for input sanitization",
                    "logging": "Use sanitize_log_input for all log messages",
                    "async": "Prefer async/await for I/O operations",
                    "error_handling": "Use specific exceptions, not broad except clauses"
                },
                "modules": self.get_project_context()['scripts'],
                "conventions": {
                    "naming": "snake_case for functions and variables",
                    "docstrings": "Use Google-style docstrings",
                    "type_hints": "Always include type hints",
                    "imports": "Group imports: stdlib, third-party, local"
                }
            },
            "ai_context": {
                "focus_areas": [
                    "Security-first development",
                    "Performance optimization",
                    "Multi-AI integration",
                    "Async programming patterns"
                ],
                "avoid": [
                    "Hardcoded credentials",
                    "Broad exception handling",
                    "Blocking I/O operations",
                    "Unsanitized user input"
                ]
            }
        }
        
        context_file = self.project_root / ".copilot-context.json"
        with open(context_file, 'w', encoding='utf-8') as f:
            json.dump(context, f, indent=2)
        
        self.logger.info("Generated .copilot-context.json for enhanced AI assistance")
        return context_file
    
    def create_copilot_snippets(self):
        """Create VS Code snippets for common ULTRON patterns."""
        snippets = {
            "ULTRON Security Function": {
                "prefix": "ultron-secure-func",
                "body": [
                    "def ${1:function_name}(${2:params}) -> ${3:return_type}:",
                    "    \"\"\"${4:Description}",
                    "    ",
                    "    Args:",
                    "        ${2:params}: ${5:Parameter description}",
                    "    ",
                    "    Returns:",
                    "        ${3:return_type}: ${6:Return description}",
                    "    \"\"\"",
                    "    try:",
                    "        # Sanitize inputs",
                    "        sanitized_input = sanitize_log_input(str(${7:input_var}))",
                    "        ",
                    "        # Your implementation here",
                    "        ${8:implementation}",
                    "        ",
                    "        return ${9:result}",
                    "    except Exception as e:",
                    "        logger.error(f\"${1:function_name} failed: {sanitize_log_input(str(e))}\")",
                    "        raise"
                ],
                "description": "ULTRON secure function template"
            },
            "ULTRON Async Handler": {
                "prefix": "ultron-async",
                "body": [
                    "async def ${1:handler_name}(${2:params}) -> ${3:return_type}:",
                    "    \"\"\"${4:Async handler description}\"\"\"",
                    "    try:",
                    "        async with ${5:context_manager}:",
                    "            ${6:implementation}",
                    "            return ${7:result}",
                    "    except Exception as e:",
                    "        logger.error(f\"Async operation failed: {sanitize_log_input(str(e))}\")",
                    "        raise"
                ],
                "description": "ULTRON async handler template"
            },
            "ULTRON Security Check": {
                "prefix": "ultron-security",
                "body": [
                    "# Security validation",
                    "if not validate_file_path(${1:file_path}):",
                    "    raise ValueError(\"Invalid file path\")",
                    "",
                    "sanitized_input = sanitize_log_input(${2:user_input})",
                    "sanitized_output = sanitize_html_output(${3:html_content})"
                ],
                "description": "ULTRON security validation"
            },
            "ULTRON Component Registration": {
                "prefix": "ultron-component",
                "body": [
                    "# Register component with integration manager",
                    "${1:component_instance} = ${2:ComponentClass}()",
                    "integration_manager.register_component('${3:component_name}', ${1:component_instance})",
                    "",
                    "# Initialize if needed",
                    "if hasattr(${1:component_instance}, 'initialize'):",
                    "    await ${1:component_instance}.initialize()"
                ],
                "description": "Register component with ULTRON integration manager"
            }
        }
        
        snippets_dir = self.project_root / ".vscode"
        snippets_dir.mkdir(exist_ok=True)
        
        snippets_file = snippets_dir / "ultron.code-snippets"
        with open(snippets_file, 'w', encoding='utf-8') as f:
            json.dump(snippets, f, indent=2)
        
        self.logger.info("Created ULTRON code snippets for VS Code")
        return snippets_file
    
    def setup_copilot_workspace(self):
        """Setup complete Copilot workspace configuration."""
        workspace_config = {
            "folders": [{"path": "."}],
            "settings": {
                "github.copilot.enable": {
                    "*": True,
                    "python": True,
                    "json": True,
                    "markdown": True
                },
                "github.copilot.advanced": {
                    "length": 500,
                    "temperature": "",
                    "top_p": "",
                    "stops": {
                        "python": ["\\ndef ", "\\nclass ", "\\nif ", "\\n#"]
                    }
                },
                "python.analysis.extraPaths": [
                    "./",
                    "./tests/",
                    "./security_utils.py"
                ],
                "python.analysis.autoImportCompletions": True,
                "editor.suggest.showWords": False,
                "editor.inlineSuggest.enabled": True
            },
            "extensions": {
                "recommendations": [
                    "github.copilot",
                    "github.copilot-chat",
                    "ms-python.python",
                    "amazonwebservices.amazon-q-vscode"
                ]
            }
        }
        
        workspace_file = self.project_root / "ultron-agent.code-workspace"
        with open(workspace_file, 'w', encoding='utf-8') as f:
            json.dump(workspace_config, f, indent=2)
        
        return workspace_file
    
    def get_function_signature(self, script_name: str, function_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed function signature from registered scripts."""
        if script_name in self.script_registry:
            for func in self.script_registry[script_name]['functions']:
                if func['name'] == function_name:
                    return func
        return None
    
    def suggest_imports(self, current_file: str) -> List[str]:
        """Suggest relevant imports based on project context."""
        suggestions = []
        
        # Core ULTRON imports
        core_imports = [
            "from security_utils import sanitize_log_input, sanitize_html_output, validate_file_path",
            "from integration_manager import integration_manager",
            "from performance_optimizer import PerformanceMonitor",
            "import logging",
            "import asyncio",
            "from typing import Dict, List, Any, Optional"
        ]
        
        # Analyze current file to suggest relevant imports
        try:
            current_path = self.project_root / current_file
            if current_path.exists():
                with open(current_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Suggest based on content patterns
                if 'async def' in content or 'await ' in content:
                    suggestions.append("import asyncio")
                if 'logging' in content or 'logger' in content:
                    suggestions.append("import logging")
                if 'sanitize' in content:
                    suggestions.append("from security_utils import sanitize_log_input, sanitize_html_output")
                if 'validate' in content:
                    suggestions.append("from security_utils import validate_file_path, validate_api_key")
        
        except Exception as e:
            self.logger.warning(f"Import suggestion failed: {str(e)}")
        
        return core_imports + suggestions
    
    def initialize_full_integration(self):
        """Initialize complete Copilot integration."""
        try:
            # Generate context file
            self.generate_copilot_context_file()
            
            # Create code snippets
            self.create_copilot_snippets()
            
            # Setup workspace
            workspace_file = self.setup_copilot_workspace()
            
            # Register with integration manager
            integration_manager.register_component('copilot_integration', self)
            
            self.logger.info("Copilot integration fully initialized")
            
            return {
                'status': 'success',
                'context_file': '.copilot-context.json',
                'snippets_file': '.vscode/ultron.code-snippets',
                'workspace_file': str(workspace_file.name),
                'registered_scripts': len(self.script_registry)
            }
            
        except Exception as e:
            self.logger.error(f"Copilot integration failed: {sanitize_log_input(str(e))}")
            return {'status': 'error', 'message': str(e)}

# Global instance
copilot_integration = CopilotIntegration()

if __name__ == "__main__":
    # Initialize integration when run directly
    result = copilot_integration.initialize_full_integration()
    print(f"Copilot Integration Result: {result}")