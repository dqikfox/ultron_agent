"""
ULTRON Agent Dependency Analyzer Tool
Analyze project dependencies, detect security vulnerabilities, and suggest updates
"""

import ast
import re
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict

from utils.ultron_logger import get_logger

logger = get_logger("dependency_analyzer")


class DependencyAnalyzerTool:
    """
    Analyzes project dependencies and provides insights.
    - Finds unused dependencies
    - Detects import patterns
    - Suggests dependency updates
    - Identifies circular dependencies
    """
    
    name = "Dependency Analyzer"
    description = "Analyze project dependencies and detect issues"
    
    # Configuration constants
    HIGH_IMPORT_THRESHOLD = 20  # Number of imports considered high
    MAX_CYCLES_TO_DISPLAY = 5  # Maximum circular dependencies to show
    TOP_IMPORTS_LIMIT = 10  # Number of top imports to display
    
    def __init__(self):
        self.workspace_root = Path(".")
        self.python_files: List[Path] = []
        self.imports: Dict[str, Set[str]] = defaultdict(set)
        self.requirements: Set[str] = set()
        logger.info("Dependency Analyzer Tool initialized")
    
    def match(self, command: str) -> bool:
        """Check if command matches this tool"""
        keywords = [
            'dependency', 'dependencies', 'import', 'imports',
            'require', 'package', 'module', 'unused', 'circular'
        ]
        command_lower = command.lower()
        return any(keyword in command_lower for keyword in keywords)
    
    def execute(self, command: str) -> str:
        """Execute dependency analysis command"""
        command_lower = command.lower()
        
        try:
            if 'analyze' in command_lower or 'analysis' in command_lower:
                return self._analyze_dependencies()
            
            elif 'unused' in command_lower:
                return self._find_unused_dependencies()
            
            elif 'circular' in command_lower:
                return self._find_circular_dependencies()
            
            elif 'import' in command_lower:
                return self._analyze_imports()
            
            elif 'update' in command_lower or 'outdated' in command_lower:
                return self._check_outdated_packages()
            
            else:
                return self._analyze_dependencies()
        
        except Exception as e:
            logger.error(f"Dependency analyzer error: {e}")
            return f"Error analyzing dependencies: {str(e)}"
    
    def _scan_python_files(self) -> None:
        """Scan workspace for Python files and extract imports"""
        self.python_files = []
        self.imports.clear()
        
        # Find all Python files
        for py_file in self.workspace_root.rglob("*.py"):
            # Skip virtual environments and test directories
            if any(part in str(py_file) for part in ['.venv', 'venv', '__pycache__', '.git']):
                continue
            
            self.python_files.append(py_file)
            
            # Extract imports
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse AST to find imports
                try:
                    tree = ast.parse(content)
                    file_imports = self._extract_imports_from_ast(tree)
                    self.imports[str(py_file)] = file_imports
                except SyntaxError:
                    pass  # Skip files with syntax errors
                    
            except Exception as e:
                logger.debug(f"Error reading {py_file}: {e}")
    
    def _extract_imports_from_ast(self, tree: ast.AST) -> Set[str]:
        """Extract import statements from AST"""
        imports = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split('.')[0])
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])
        
        return imports
    
    def _load_requirements(self) -> None:
        """Load requirements from requirements.txt"""
        self.requirements.clear()
        
        req_file = self.workspace_root / "requirements.txt"
        if req_file.exists():
            try:
                with open(req_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Extract package name (before ==, >=, etc.)
                            match = re.match(r'^([a-zA-Z0-9_-]+)', line)
                            if match:
                                self.requirements.add(match.group(1).lower())
            except Exception as e:
                logger.error(f"Error loading requirements: {e}")
    
    def _analyze_dependencies(self) -> str:
        """Comprehensive dependency analysis"""
        self._scan_python_files()
        self._load_requirements()
        
        # Collect all imported packages
        all_imports = set()
        for file_imports in self.imports.values():
            all_imports.update(file_imports)
        
        # Find common Python standard library modules to exclude
        stdlib_modules = {
            'os', 'sys', 'json', 'time', 'datetime', 'pathlib', 'typing',
            'collections', 're', 'ast', 'subprocess', 'threading', 'asyncio',
            'logging', 'hashlib', 'uuid', 'inspect', 'dataclasses'
        }
        
        # Third-party imports
        third_party_imports = all_imports - stdlib_modules
        
        report = f"""
╔══════════════════════════════════════════════════════════════════╗
║          DEPENDENCY ANALYSIS REPORT                              ║
╚══════════════════════════════════════════════════════════════════╝

📊 PROJECT OVERVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Python Files Scanned:      {len(self.python_files)}
Total Imports Found:       {len(all_imports)}
Standard Library:          {len(all_imports & stdlib_modules)}
Third-Party Packages:      {len(third_party_imports)}
Declared Requirements:     {len(self.requirements)}

📦 THIRD-PARTY DEPENDENCIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        # List third-party imports
        for pkg in sorted(third_party_imports):
            in_req = '✅' if pkg.lower() in self.requirements else '❌'
            report += f"{in_req} {pkg}\n"
        
        # Find unused requirements
        unused_reqs = set()
        for req in self.requirements:
            # Check if requirement is imported
            req_base = req.split('[')[0].lower()  # Handle extras like package[extra]
            if req_base not in {imp.lower() for imp in third_party_imports}:
                unused_reqs.add(req)
        
        if unused_reqs:
            report += f"""
⚠️  POTENTIALLY UNUSED REQUIREMENTS ({len(unused_reqs)})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            for req in sorted(unused_reqs):
                report += f"• {req}\n"
        
        # Find missing requirements
        missing_reqs = set()
        for imp in third_party_imports:
            if imp.lower() not in self.requirements:
                missing_reqs.add(imp)
        
        if missing_reqs:
            report += f"""
❌ MISSING FROM REQUIREMENTS ({len(missing_reqs)})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            for req in sorted(missing_reqs):
                report += f"• {req}\n"
        
        # Import frequency analysis
        import_counts = defaultdict(int)
        for file_imports in self.imports.values():
            for imp in file_imports:
                import_counts[imp] += 1
        
        top_imports = sorted(import_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        report += f"""
🔝 TOP 10 MOST IMPORTED PACKAGES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        for pkg, count in top_imports:
            report += f"{pkg:20s} : {count:3d} files\n"
        
        return report.strip()
    
    def _find_unused_dependencies(self) -> str:
        """Find dependencies listed in requirements but not imported"""
        self._scan_python_files()
        self._load_requirements()
        
        # Collect all imports
        all_imports = set()
        for file_imports in self.imports.values():
            all_imports.update(imp.lower() for imp in file_imports)
        
        # Find unused
        unused = []
        for req in self.requirements:
            req_base = req.split('[')[0].lower()
            if req_base not in all_imports:
                unused.append(req)
        
        report = f"""
╔══════════════════════════════════════════════════════════════════╗
║          UNUSED DEPENDENCIES REPORT                              ║
╚══════════════════════════════════════════════════════════════════╝

"""
        
        if unused:
            report += f"Found {len(unused)} potentially unused dependencies:\n\n"
            for dep in sorted(unused):
                report += f"❌ {dep}\n"
            
            report += f"""
💡 RECOMMENDATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Review if these packages are truly unused
• Some packages may be transitive dependencies
• Check if imports use different names (e.g., Pillow → PIL)
• Consider removing genuinely unused packages
"""
        else:
            report += "✅ All declared dependencies appear to be in use!\n"
        
        return report.strip()
    
    def _find_circular_dependencies(self) -> str:
        """Detect circular import dependencies"""
        self._scan_python_files()
        
        # Build dependency graph
        graph: Dict[str, Set[str]] = defaultdict(set)
        
        for file_path, file_imports in self.imports.items():
            file_module = str(file_path).replace('/', '.').replace('\\', '.').replace('.py', '')
            
            for imp in file_imports:
                # Try to match imports to local files
                for other_file in self.python_files:
                    other_module = str(other_file).replace('/', '.').replace('\\', '.').replace('.py', '')
                    if imp in other_module:
                        graph[file_module].add(other_module)
        
        # Find cycles using DFS
        cycles = []
        visited = set()
        
        def dfs(node: str, path: List[str], path_set: Set[str]):
            visited.add(node)
            path.append(node)
            path_set.add(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, path, path_set)
                elif neighbor in path_set:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)
            
            path.pop()
            path_set.remove(node)
        
        for node in graph:
            if node not in visited:
                dfs(node, [], set())
        
        report = f"""
╔══════════════════════════════════════════════════════════════════╗
║          CIRCULAR DEPENDENCY ANALYSIS                            ║
╚══════════════════════════════════════════════════════════════════╝

"""
        
        if cycles:
            report += f"⚠️  Found {len(cycles)} circular dependencies:\n\n"
            
            for i, cycle in enumerate(cycles[:self.MAX_CYCLES_TO_DISPLAY], 1):
                report += f"{i}. Cycle detected:\n"
                for j, module in enumerate(cycle):
                    if j < len(cycle) - 1:
                        report += f"   {module}\n   ↓\n"
                    else:
                        report += f"   {module}\n\n"
            
            report += """
💡 RECOMMENDATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Refactor code to break circular dependencies
• Use dependency injection
• Move shared code to a common module
• Consider using late imports (import inside functions)
"""
        else:
            report += "✅ No circular dependencies detected!\n"
        
        return report.strip()
    
    def _analyze_imports(self) -> str:
        """Analyze import patterns and provide insights"""
        self._scan_python_files()
        
        # Count imports per file
        imports_per_file = {str(f): len(imps) for f, imps in self.imports.items()}
        
        # Find files with most imports
        top_files = sorted(imports_per_file.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Calculate statistics
        import_counts = list(imports_per_file.values())
        avg_imports = sum(import_counts) / len(import_counts) if import_counts else 0
        max_imports = max(import_counts) if import_counts else 0
        
        report = f"""
╔══════════════════════════════════════════════════════════════════╗
║          IMPORT PATTERN ANALYSIS                                 ║
╚══════════════════════════════════════════════════════════════════╝

📊 STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Average Imports per File:  {avg_imports:.1f}
Maximum Imports in File:   {max_imports}
Files Analyzed:            {len(imports_per_file)}

🔝 FILES WITH MOST IMPORTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        for file_path, count in top_files:
            file_name = Path(file_path).name
            report += f"{count:3d} imports : {file_name}\n"
        
        # Detect potential issues
        high_import_files = [f for f, c in imports_per_file.items() if c > self.HIGH_IMPORT_THRESHOLD]
        
        if high_import_files:
            report += f"""
⚠️  FILES WITH HIGH IMPORT COUNT (>{self.HIGH_IMPORT_THRESHOLD})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Found {len(high_import_files)} files with high import counts.
Consider refactoring these files to reduce complexity.
"""
        
        return report.strip()
    
    def _check_outdated_packages(self) -> str:
        """Check for outdated packages (requires pip)"""
        try:
            result = subprocess.run(
                ['pip', 'list', '--outdated', '--format=json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                outdated = json.loads(result.stdout)
                
                report = f"""
╔══════════════════════════════════════════════════════════════════╗
║          OUTDATED PACKAGES REPORT                                ║
╚══════════════════════════════════════════════════════════════════╝

"""
                
                if outdated:
                    report += f"Found {len(outdated)} outdated packages:\n\n"
                    
                    for pkg in outdated:
                        report += f"📦 {pkg['name']}\n"
                        report += f"   Current:  {pkg['version']}\n"
                        report += f"   Latest:   {pkg['latest_version']}\n\n"
                    
                    report += "💡 Run 'pip install --upgrade <package>' to update\n"
                else:
                    report += "✅ All packages are up to date!\n"
                
                return report.strip()
            else:
                return "❌ Error checking for outdated packages"
        
        except Exception as e:
            logger.error(f"Error checking outdated packages: {e}")
            return f"Error: {str(e)}"
    
    @classmethod
    def schema(cls):
        """Return tool schema for AI integration"""
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "command": {
                    "type": "string",
                    "description": "Analysis command (analyze, unused, circular, imports, outdated)"
                }
            }
        }


# Export for tool discovery
__all__ = ['DependencyAnalyzerTool']
