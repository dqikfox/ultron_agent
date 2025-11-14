#!/usr/bin/env python3
"""
ULTRON Agent System Audit & Auto-Fix Tool
Finds disconnected components, missing imports, broken integrations
"""
import os
import re
import json
import ast
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

class UltronSystemAuditor:
    def __init__(self, root_dir: str = "."):
        self.root = Path(root_dir)
        self.issues = defaultdict(list)
        self.components = {}
        self.imports = defaultdict(set)
        self.exports = defaultdict(set)
        self.connections = defaultdict(set)
        
    def audit_full_system(self):
        """Run complete system audit"""
        print("=" * 70)
        print("  ULTRON AGENT SYSTEM AUDIT")
        print("=" * 70)
        print()
        
        # Phase 1: Discover all components
        print("[1/7] Discovering components...")
        self.discover_components()
        print(f"    Found {len(self.components)} components")
        
        # Phase 2: Analyze imports/exports
        print("[2/7] Analyzing imports and exports...")
        self.analyze_imports_exports()
        print(f"    Found {sum(len(v) for v in self.imports.values())} imports")
        
        # Phase 3: Check connections
        print("[3/7] Checking component connections...")
        self.check_connections()
        
        # Phase 4: Find missing dependencies
        print("[4/7] Finding missing dependencies...")
        self.find_missing_dependencies()
        
        # Phase 5: Check configuration
        print("[5/7] Checking configuration files...")
        self.check_configuration()
        
        # Phase 6: Validate integrations
        print("[6/7] Validating integrations...")
        self.validate_integrations()
        
        # Phase 7: Generate report
        print("[7/7] Generating report...")
        self.generate_report()
        
    def discover_components(self):
        """Find all Python files and categorize them"""
        categories = {
            'core': ['agent_core.py', 'brain.py', 'main.py'],
            'servers': ['*_server.py'],
            'tools': ['tools/*.py'],
            'utils': ['utils/*.py'],
            'gui': ['gui/**/*.py'],
            'tests': ['tests/**/*.py']
        }
        
        for category, patterns in categories.items():
            for pattern in patterns:
                for file in self.root.glob(pattern):
                    if file.is_file() and not file.name.startswith('__'):
                        rel_path = file.relative_to(self.root)
                        self.components[str(rel_path)] = {
                            'category': category,
                            'path': file,
                            'size': file.stat().st_size,
                            'exists': True
                        }
    
    def analyze_imports_exports(self):
        """Analyze import statements and exported functions"""
        for comp_path, comp_info in self.components.items():
            try:
                with open(comp_info['path'], 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Find imports
                import_pattern = r'^(?:from|import)\s+([a-zA-Z0-9_.]+)'
                for match in re.finditer(import_pattern, content, re.MULTILINE):
                    module = match.group(1)
                    self.imports[comp_path].add(module)
                
                # Find class/function definitions (exports)
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            self.exports[comp_path].add(f"class:{node.name}")
                        elif isinstance(node, ast.FunctionDef):
                            if not node.name.startswith('_'):
                                self.exports[comp_path].add(f"func:{node.name}")
                except:
                    pass
                    
            except Exception as e:
                self.issues['read_errors'].append(f"{comp_path}: {str(e)}")
    
    def check_connections(self):
        """Check which components are connected"""
        for comp_path, imports in self.imports.items():
            for imp in imports:
                # Check if import refers to another component
                for other_path in self.components.keys():
                    module_name = other_path.replace('/', '.').replace('\\', '.').replace('.py', '')
                    if imp.startswith(module_name) or module_name.endswith(imp):
                        self.connections[comp_path].add(other_path)
        
        # Find orphaned components
        all_components = set(self.components.keys())
        connected = set()
        for conns in self.connections.values():
            connected.update(conns)
        connected.update(self.connections.keys())
        
        orphaned = all_components - connected
        if orphaned:
            self.issues['orphaned_components'] = list(orphaned)
    
    def find_missing_dependencies(self):
        """Find imports that don't exist"""
        project_modules = set()
        for comp_path in self.components.keys():
            module = comp_path.replace('/', '.').replace('\\', '.').replace('.py', '')
            project_modules.add(module)
        
        for comp_path, imports in self.imports.items():
            for imp in imports:
                # Skip standard library
                if imp.split('.')[0] in ['os', 'sys', 'json', 'time', 'datetime', 're', 'pathlib']:
                    continue
                
                # Check if it's a project module
                is_project = any(imp.startswith(pm) or pm.endswith(imp) for pm in project_modules)
                if is_project:
                    # Check if file exists
                    possible_paths = [
                        self.root / f"{imp.replace('.', '/')}.py",
                        self.root / imp.replace('.', '/') / "__init__.py"
                    ]
                    if not any(p.exists() for p in possible_paths):
                        self.issues['missing_imports'].append(f"{comp_path} imports {imp}")
    
    def check_configuration(self):
        """Check configuration files"""
        config_files = {
            'ultron_config.json': 'Main configuration',
            'mcp.json': 'MCP servers',
            'requirements.txt': 'Python dependencies',
            '.env.example': 'Environment template'
        }
        
        for config_file, description in config_files.items():
            path = self.root / config_file
            if not path.exists():
                self.issues['missing_config'].append(f"{config_file} ({description})")
            else:
                # Validate JSON files
                if config_file.endswith('.json'):
                    try:
                        with open(path) as f:
                            json.load(f)
                    except json.JSONDecodeError as e:
                        self.issues['invalid_config'].append(f"{config_file}: {str(e)}")
    
    def validate_integrations(self):
        """Check if major integrations are properly connected"""
        integrations = {
            'Ollama': {
                'files': ['brain.py', 'ollama_manager.py'],
                'imports': ['ollama', 'requests'],
                'config': 'llm_model'
            },
            'Voice': {
                'files': ['voice.py', 'voice_manager.py'],
                'imports': ['elevenlabs', 'pyttsx3'],
                'config': 'voice_enabled'
            },
            'GUI': {
                'files': ['web_gui_server.py', 'gui/ultron_enhanced/web/index.html'],
                'imports': ['flask', 'fastapi'],
                'config': 'gui_port'
            },
            'Tools': {
                'files': ['tools/__init__.py', 'tools/base.py'],
                'imports': [],
                'config': 'tools_enabled'
            }
        }
        
        for integration, requirements in integrations.items():
            missing = []
            for file in requirements['files']:
                if not (self.root / file).exists():
                    missing.append(file)
            
            if missing:
                self.issues['broken_integrations'].append(
                    f"{integration}: Missing files {missing}"
                )
    
    def generate_report(self):
        """Generate comprehensive report"""
        print()
        print("=" * 70)
        print("  AUDIT REPORT")
        print("=" * 70)
        print()
        
        # Summary
        total_issues = sum(len(v) for v in self.issues.values())
        print(f"Total Components: {len(self.components)}")
        print(f"Total Issues: {total_issues}")
        print()
        
        # Detailed issues
        if self.issues:
            for issue_type, items in self.issues.items():
                if items:
                    print(f"🚨 {issue_type.upper().replace('_', ' ')}:")
                    for item in items[:10]:  # Show first 10
                        print(f"   - {item}")
                    if len(items) > 10:
                        print(f"   ... and {len(items) - 10} more")
                    print()
        else:
            print("✅ No issues found!")
        
        # Component statistics
        print("📊 COMPONENT STATISTICS:")
        categories = defaultdict(int)
        for comp in self.components.values():
            categories[comp['category']] += 1
        for category, count in sorted(categories.items()):
            print(f"   {category}: {count} files")
        print()
        
        # Connection statistics
        print("🔗 CONNECTION STATISTICS:")
        print(f"   Connected components: {len(self.connections)}")
        print(f"   Total connections: {sum(len(v) for v in self.connections.values())}")
        if self.issues.get('orphaned_components'):
            print(f"   ⚠ Orphaned components: {len(self.issues['orphaned_components'])}")
        print()
        
        # Save detailed report
        self.save_report()
    
    def save_report(self):
        """Save detailed report to file"""
        report = {
            'timestamp': str(Path.ctime(Path('.'))),
            'summary': {
                'total_components': len(self.components),
                'total_issues': sum(len(v) for v in self.issues.values()),
                'categories': dict(defaultdict(int))
            },
            'components': {k: {**v, 'path': str(v['path'])} for k, v in self.components.items()},
            'issues': dict(self.issues),
            'connections': {k: list(v) for k, v in self.connections.items()}
        }
        
        report_file = self.root / 'SYSTEM_AUDIT_REPORT.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Detailed report saved: {report_file}")
        print()

def main():
    auditor = UltronSystemAuditor()
    auditor.audit_full_system()
    
    print("=" * 70)
    print("  NEXT STEPS")
    print("=" * 70)
    print()
    print("1. Review SYSTEM_AUDIT_REPORT.json for details")
    print("2. Run: python SYSTEM_INTEGRATION_FIX.py (auto-fix tool)")
    print("3. Run: python COMPONENT_MAPPER.py (visualize connections)")
    print()

if __name__ == '__main__':
    main()
