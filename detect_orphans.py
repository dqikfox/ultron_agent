#!/usr/bin/env python3
"""
Ultron Agent Orphan & Broken Link Detection Tool

This tool detects:
1. Orphaned files and directories (not referenced in code)
2. Broken imports and missing dependencies
3. Missing asset files referenced in code
4. Duplicate/redundant files
5. Outdated references and broken file paths
"""

import os
import sys
import ast
import json
import re
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
import importlib.util


class OrphanDetector:
    """Comprehensive orphan and broken link detector for Ultron Agent"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.results = {
            'broken_imports': [],
            'missing_assets': [],
            'orphaned_files': [],
            'duplicate_files': [],
            'unreferenced_directories': [],
            'broken_references': [],
            'recommendations': []
        }
        
        # Directories to ignore for orphan detection
        self.ignore_dirs = {
            '.git', '__pycache__', '.pytest_cache', 'node_modules', 
            '.vscode', '.snapshots', 'Oracle_JDK-24', 'cache'
        }
        
        # File patterns to ignore
        self.ignore_patterns = {
            '*.pyc', '*.pyo', '*.log', '*.tmp', '.DS_Store',
            '*.png', '*.jpg', '*.jpeg', '*.gif', '*.ico'  # Will handle separately
        }
        
        # Known asset extensions
        self.asset_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.ico', '.wav', '.mp3', '.css', '.js'}
        
    def analyze_project(self) -> Dict:
        """Run comprehensive analysis of the project"""
        print("🔍 Starting Ultron Agent Orphan & Broken Link Analysis...")
        
        # Step 1: Scan for broken imports
        print("\n📦 Analyzing imports and dependencies...")
        self._detect_broken_imports()
        
        # Step 2: Find missing assets
        print("\n🎨 Checking for missing assets...")
        self._detect_missing_assets()
        
        # Step 3: Find orphaned files
        print("\n🔍 Detecting orphaned files...")
        self._detect_orphaned_files()
        
        # Step 4: Find duplicates
        print("\n📁 Finding duplicate files...")
        self._detect_duplicate_files()
        
        # Step 5: Check for broken file references
        print("\n🔗 Checking file references...")
        self._detect_broken_references()
        
        # Step 6: Generate recommendations
        print("\n💡 Generating recommendations...")
        self._generate_recommendations()
        
        return self.results
    
    def _detect_broken_imports(self):
        """Detect broken Python imports"""
        python_files = list(self.project_root.rglob("*.py"))
        
        for py_file in python_files:
            if any(ignore_dir in py_file.parts for ignore_dir in self.ignore_dirs):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Parse AST to find imports
                try:
                    tree = ast.parse(content, filename=str(py_file))
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                self._check_import(py_file, alias.name)
                        
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                self._check_import(py_file, node.module, node.names)
                                
                except SyntaxError:
                    self.results['broken_imports'].append({
                        'file': str(py_file.relative_to(self.project_root)),
                        'error': 'Syntax error in file',
                        'type': 'syntax_error'
                    })
                    
            except Exception as e:
                self.results['broken_imports'].append({
                    'file': str(py_file.relative_to(self.project_root)),
                    'error': f'Error reading file: {str(e)}',
                    'type': 'read_error'
                })
    
    def _check_import(self, file_path: Path, module_name: str, names: List = None):
        """Check if an import is valid"""
        try:
            # Check for relative imports within project
            if module_name.startswith('.'):
                # Handle relative imports
                current_package = file_path.parent
                relative_path = self._resolve_relative_import(current_package, module_name)
                if relative_path and not relative_path.exists():
                    self.results['broken_imports'].append({
                        'file': str(file_path.relative_to(self.project_root)),
                        'import': module_name,
                        'error': 'Relative import target not found',
                        'type': 'missing_relative'
                    })
            else:
                # Check if it's a local module
                parts = module_name.split('.')
                potential_file = self.project_root / '/'.join(parts) + '.py'
                potential_dir = self.project_root / '/'.join(parts) / '__init__.py'
                
                if (potential_file.exists() or potential_dir.exists()):
                    return  # Local module exists
                
                # Try to import standard/installed modules
                try:
                    importlib.util.find_spec(module_name)
                except (ImportError, ModuleNotFoundError, ValueError):
                    # Could be a missing dependency
                    if not self._is_likely_standard_library(module_name):
                        self.results['broken_imports'].append({
                            'file': str(file_path.relative_to(self.project_root)),
                            'import': module_name,
                            'error': 'Module not found',
                            'type': 'missing_module'
                        })
        except Exception as e:
            pass  # Skip problematic imports for now
    
    def _resolve_relative_import(self, current_dir: Path, import_name: str) -> Optional[Path]:
        """Resolve relative import to actual file path"""
        levels = len(import_name) - len(import_name.lstrip('.'))
        module_name = import_name.lstrip('.')
        
        target_dir = current_dir
        for _ in range(levels - 1):
            target_dir = target_dir.parent
        
        if module_name:
            target_path = target_dir / (module_name.replace('.', '/') + '.py')
            if not target_path.exists():
                target_path = target_dir / module_name.replace('.', '/') / '__init__.py'
            return target_path
        return target_dir / '__init__.py'
    
    def _is_likely_standard_library(self, module_name: str) -> bool:
        """Check if module is likely from standard library"""
        stdlib_modules = {
            'os', 'sys', 'json', 'ast', 're', 'pathlib', 'collections', 
            'importlib', 'hashlib', 'threading', 'asyncio', 'logging',
            'datetime', 'time', 'math', 'random', 'typing', 'functools'
        }
        return module_name.split('.')[0] in stdlib_modules
    
    def _detect_missing_assets(self):
        """Detect missing asset files referenced in code"""
        # Patterns to look for asset references
        asset_patterns = [
            r'["\']([^"\']+\.(?:png|jpg|jpeg|gif|ico|wav|mp3|css|js))["\']',
            r'src=["\']([^"\']+)["\']',
            r'href=["\']([^"\']+)["\']',
            r'url\(["\']?([^"\']+)["\']?\)',
            r'asset[s]?[/\\]([^"\']+)',
            r'favicon\.ico',
            r'resources/images/([^"\']+)'
        ]
        
        # Scan all text files
        text_extensions = {'.py', '.html', '.js', '.css', '.md', '.json', '.yaml', '.yml', '.txt'}
        
        for file_path in self.project_root.rglob("*"):
            if file_path.suffix in text_extensions and file_path.is_file():
                if any(ignore_dir in file_path.parts for ignore_dir in self.ignore_dirs):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    for pattern in asset_patterns:
                        matches = re.findall(pattern, content)
                        for match in matches:
                            self._check_asset_exists(file_path, match)
                            
                except Exception:
                    continue
    
    def _check_asset_exists(self, source_file: Path, asset_path: str):
        """Check if referenced asset file exists"""
        # Try different resolution strategies
        potential_paths = [
            self.project_root / asset_path,
            source_file.parent / asset_path,
            self.project_root / 'resources' / asset_path,
            self.project_root / 'assets' / asset_path,
            self.project_root / 'web_gui' / 'assets' / asset_path,
            self.project_root / 'gui' / 'ultron_enhanced' / 'web' / 'assets' / asset_path,
            self.project_root / 'static' / asset_path
        ]
        
        # Check if any path exists
        exists = any(path.exists() for path in potential_paths)
        
        if not exists and asset_path != 'assets/placeholder.txt':
            self.results['missing_assets'].append({
                'source_file': str(source_file.relative_to(self.project_root)),
                'asset_path': asset_path,
                'searched_paths': [str(p.relative_to(self.project_root)) for p in potential_paths]
            })
    
    def _detect_orphaned_files(self):
        """Detect files that are not referenced anywhere"""
        all_files = set()
        referenced_files = set()
        
        # Get all files
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and not any(ignore_dir in file_path.parts for ignore_dir in self.ignore_dirs):
                if not any(file_path.name.endswith(pattern.replace('*', '')) for pattern in self.ignore_patterns):
                    all_files.add(file_path)
        
        # Find references to files in code and documentation
        for file_path in all_files:
            if file_path.suffix in {'.py', '.md', '.html', '.js', '.css', '.json', '.yaml', '.yml', '.txt', '.bat'}:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Look for file references
                    for other_file in all_files:
                        if other_file != file_path:
                            relative_path = other_file.relative_to(self.project_root)
                            file_name = other_file.name
                            
                            # Check various reference patterns
                            if (str(relative_path) in content or 
                                file_name in content or
                                str(relative_path).replace('\\', '/') in content or
                                str(relative_path).replace('/', '\\') in content):
                                referenced_files.add(other_file)
                                
                except Exception:
                    continue
        
        # Files that are not referenced (potential orphans)
        orphaned = all_files - referenced_files
        
        # Filter out some common files that may not be directly referenced
        essential_files = {
            'main.py', '__init__.py', 'setup.py', 'requirements.txt',
            'README.md', 'LICENSE', '.gitignore', 'pyproject.toml',
            'pytest.ini', 'conftest.py'
        }
        
        for orphan in orphaned:
            if orphan.name not in essential_files:
                self.results['orphaned_files'].append({
                    'file': str(orphan.relative_to(self.project_root)),
                    'size': orphan.stat().st_size if orphan.exists() else 0,
                    'type': 'potential_orphan'
                })
    
    def _detect_duplicate_files(self):
        """Detect duplicate files based on content hash"""
        file_hashes = defaultdict(list)
        
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and not any(ignore_dir in file_path.parts for ignore_dir in self.ignore_dirs):
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                        file_hash = hashlib.md5(content).hexdigest()
                        file_hashes[file_hash].append(file_path)
                except Exception:
                    continue
        
        # Find duplicates
        for file_hash, files in file_hashes.items():
            if len(files) > 1:
                self.results['duplicate_files'].append({
                    'hash': file_hash,
                    'files': [str(f.relative_to(self.project_root)) for f in files],
                    'size': files[0].stat().st_size if files[0].exists() else 0
                })
    
    def _detect_broken_references(self):
        """Detect broken file path references in documentation and config"""
        reference_patterns = [
            r'`([^`]+\.[a-zA-Z0-9]+)`',  # Backtick file references
            r'"([^"]+\.[a-zA-Z0-9]+)"',  # Quoted file paths
            r"'([^']+\.[a-zA-Z0-9]+)'",  # Single quoted file paths
            r'file:///([^\\s]+)',        # File URLs
            r'\.\/([^\\s]+\.[a-zA-Z0-9]+)',  # Relative paths
        ]
        
        doc_files = list(self.project_root.rglob("*.md")) + list(self.project_root.rglob("*.txt"))
        
        for doc_file in doc_files:
            if any(ignore_dir in doc_file.parts for ignore_dir in self.ignore_dirs):
                continue
                
            try:
                with open(doc_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                for pattern in reference_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        # Try to resolve the path
                        potential_path = self.project_root / match
                        if not potential_path.exists():
                            # Try relative to the document
                            potential_path = doc_file.parent / match
                            if not potential_path.exists():
                                self.results['broken_references'].append({
                                    'source_file': str(doc_file.relative_to(self.project_root)),
                                    'broken_reference': match,
                                    'type': 'file_reference'
                                })
                                
            except Exception:
                continue
    
    def _generate_recommendations(self):
        """Generate recommendations based on analysis results"""
        recommendations = []
        
        # Broken imports recommendations
        if self.results['broken_imports']:
            recommendations.append({
                'category': 'Broken Imports',
                'priority': 'HIGH',
                'count': len(self.results['broken_imports']),
                'action': 'Fix import statements or install missing dependencies',
                'details': 'Review requirements.txt and ensure all dependencies are listed'
            })
        
        # Missing assets recommendations
        if self.results['missing_assets']:
            recommendations.append({
                'category': 'Missing Assets',
                'priority': 'MEDIUM',
                'count': len(self.results['missing_assets']),
                'action': 'Create missing asset files or update references',
                'details': 'Focus on web interface assets like images and audio files'
            })
        
        # Orphaned files recommendations
        orphan_count = len(self.results['orphaned_files'])
        if orphan_count > 50:  # Many orphans
            recommendations.append({
                'category': 'Orphaned Files',
                'priority': 'MEDIUM',
                'count': orphan_count,
                'action': 'Review and clean up unused files',
                'details': 'Consider removing files that are not part of the main architecture'
            })
        
        # Duplicates recommendations
        if self.results['duplicate_files']:
            total_duplicate_size = sum(dup['size'] * (len(dup['files']) - 1) 
                                     for dup in self.results['duplicate_files'])
            recommendations.append({
                'category': 'Duplicate Files',
                'priority': 'LOW',
                'count': len(self.results['duplicate_files']),
                'action': 'Remove duplicate files to save space',
                'details': f'Could save approximately {total_duplicate_size // 1024} KB'
            })
        
        # Broken references recommendations
        if self.results['broken_references']:
            recommendations.append({
                'category': 'Broken References',
                'priority': 'LOW',
                'count': len(self.results['broken_references']),
                'action': 'Update documentation with correct file paths',
                'details': 'Fix broken links in documentation files'
            })
        
        self.results['recommendations'] = recommendations
    
    def generate_report(self) -> str:
        """Generate a comprehensive report"""
        report = [
            "# 🔍 Ultron Agent Orphan & Broken Link Analysis Report",
            f"\n**Analysis Date**: {os.popen('date').read().strip()}",
            f"**Project Root**: {self.project_root}",
            "\n## 📊 Summary\n"
        ]
        
        # Summary statistics
        total_issues = (len(self.results['broken_imports']) + 
                       len(self.results['missing_assets']) + 
                       len(self.results['orphaned_files']) + 
                       len(self.results['duplicate_files']) + 
                       len(self.results['broken_references']))
        
        report.append(f"- **Total Issues Found**: {total_issues}")
        report.append(f"- **Broken Imports**: {len(self.results['broken_imports'])}")
        report.append(f"- **Missing Assets**: {len(self.results['missing_assets'])}")
        report.append(f"- **Orphaned Files**: {len(self.results['orphaned_files'])}")
        report.append(f"- **Duplicate Files**: {len(self.results['duplicate_files'])}")
        report.append(f"- **Broken References**: {len(self.results['broken_references'])}")
        
        # Detailed sections
        self._add_section_to_report(report, "🚨 Broken Imports", self.results['broken_imports'])
        self._add_section_to_report(report, "🎨 Missing Assets", self.results['missing_assets'])
        self._add_section_to_report(report, "👻 Orphaned Files", self.results['orphaned_files'][:20])  # Limit output
        self._add_section_to_report(report, "📄 Duplicate Files", self.results['duplicate_files'])
        self._add_section_to_report(report, "🔗 Broken References", self.results['broken_references'])
        
        # Recommendations
        if self.results['recommendations']:
            report.append("\n## 💡 Recommendations\n")
            for rec in self.results['recommendations']:
                report.append(f"### {rec['category']} - Priority: {rec['priority']}")
                report.append(f"- **Count**: {rec['count']} issues")
                report.append(f"- **Action**: {rec['action']}")
                report.append(f"- **Details**: {rec['details']}\n")
        
        return '\n'.join(report)
    
    def _add_section_to_report(self, report: List[str], title: str, items: List):
        """Add a section to the report"""
        if not items:
            return
            
        report.append(f"\n## {title}\n")
        
        for i, item in enumerate(items[:10]):  # Limit to first 10 items
            if isinstance(item, dict):
                if 'file' in item:
                    report.append(f"{i+1}. **File**: `{item['file']}`")
                    if 'import' in item:
                        report.append(f"   - **Import**: `{item['import']}`")
                    if 'error' in item:
                        report.append(f"   - **Error**: {item['error']}")
                    if 'asset_path' in item:
                        report.append(f"   - **Missing Asset**: `{item['asset_path']}`")
                elif 'files' in item:  # Duplicate files
                    report.append(f"{i+1}. **Duplicate Files**:")
                    for f in item['files']:
                        report.append(f"   - `{f}`")
                report.append("")
        
        if len(items) > 10:
            report.append(f"*... and {len(items) - 10} more items*\n")


def main():
    """Main function to run the orphan detection tool"""
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    print(f"🔍 Analyzing Ultron Agent project at: {project_root}")
    
    detector = OrphanDetector(project_root)
    results = detector.analyze_project()
    
    # Generate and save report
    report = detector.generate_report()
    
    report_file = os.path.join(project_root, 'ORPHAN_ANALYSIS_REPORT.md')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ Analysis complete! Report saved to: {report_file}")
    
    # Also save raw JSON results
    json_file = os.path.join(project_root, 'orphan_analysis_results.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"📊 Raw results saved to: {json_file}")
    
    # Print summary
    total_issues = (len(results['broken_imports']) + 
                   len(results['missing_assets']) + 
                   len(results['orphaned_files']) + 
                   len(results['duplicate_files']) + 
                   len(results['broken_references']))
    
    print(f"\n📈 Summary: {total_issues} total issues found")
    print(f"   - Broken Imports: {len(results['broken_imports'])}")
    print(f"   - Missing Assets: {len(results['missing_assets'])}")
    print(f"   - Orphaned Files: {len(results['orphaned_files'])}")
    print(f"   - Duplicate Files: {len(results['duplicate_files'])}")
    print(f"   - Broken References: {len(results['broken_references'])}")


if __name__ == "__main__":
    main()