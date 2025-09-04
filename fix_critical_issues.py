#!/usr/bin/env python3
"""
Critical Issue Fix Script for Ultron Agent

This script addresses the most critical orphans and broken links identified
by the analysis tool, focusing on high-impact, low-risk fixes.
"""

import os
import json
import shutil
from pathlib import Path
from typing import List, Dict, Set
import ast


class CriticalIssueFixer:
    """Fixes critical orphan and broken link issues"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.results_file = self.project_root / 'orphan_analysis_results.json'
        self.backup_dir = self.project_root / '.orphan_fixes_backup'
        
        # Load analysis results
        if self.results_file.exists():
            with open(self.results_file, 'r') as f:
                self.results = json.load(f)
        else:
            raise FileNotFoundError("Analysis results not found. Run detect_orphans.py first.")
        
        self.fixes_applied = []
        
    def create_backup(self):
        """Create backup directory for files we might modify"""
        self.backup_dir.mkdir(exist_ok=True)
        print(f"📁 Backup directory created: {self.backup_dir}")
    
    def fix_syntax_errors(self):
        """Fix critical syntax errors in Python files"""
        print("\n🔧 Fixing syntax errors...")
        
        syntax_errors = [item for item in self.results['broken_imports'] 
                        if item.get('type') == 'syntax_error']
        
        critical_files = [
            'nvidia_enhanced_ultron.py',
            'main_gui_server.py',
            'ollama_keepalive.py',
            'ultron_advanced_ai_nvidia.py',
            'frontend_server.py'
        ]
        
        for error in syntax_errors:
            file_path = self.project_root / error['file']
            
            if not file_path.exists():
                continue
                
            # Focus on critical files first
            if error['file'] in critical_files:
                print(f"   🔍 Examining {error['file']}...")
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Common syntax error fixes
                    fixed_content = self._fix_common_syntax_errors(content)
                    
                    if fixed_content != content:
                        # Backup original
                        backup_path = self.backup_dir / error['file']
                        backup_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(file_path, backup_path)
                        
                        # Write fixed content
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(fixed_content)
                        
                        # Test if fix worked
                        try:
                            ast.parse(fixed_content)
                            print(f"   ✅ Fixed syntax errors in {error['file']}")
                            self.fixes_applied.append(f"Fixed syntax errors in {error['file']}")
                        except SyntaxError:
                            # Restore backup if fix didn't work
                            shutil.copy2(backup_path, file_path)
                            print(f"   ❌ Could not fix {error['file']}, restored backup")
                            
                except Exception as e:
                    print(f"   ❌ Error processing {error['file']}: {e}")
    
    def _fix_common_syntax_errors(self, content: str) -> str:
        """Fix common syntax errors in Python files"""
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            fixed_line = line
            
            # Fix markdown code blocks in Python files (common issue)
            if line.strip().startswith('```'):
                fixed_line = '# ' + line
            
            # Fix incomplete string literals
            if line.count('"') % 2 == 1 and not line.strip().endswith('\\'):
                if line.rstrip().endswith('"'):
                    pass  # Line ends with quote, likely OK
                else:
                    # Try to close the string
                    fixed_line = line + '"'
            
            # Fix incomplete function definitions
            if line.strip().startswith('def ') and not line.rstrip().endswith(':'):
                if '(' in line and ')' not in line:
                    fixed_line = line + '):'
                elif not line.rstrip().endswith(':'):
                    fixed_line = line + ':'
            
            fixed_lines.append(fixed_line)
        
        return '\n'.join(fixed_lines)
    
    def create_missing_assets(self):
        """Create critical missing asset files"""
        print("\n🎨 Creating critical missing assets...")
        
        # Focus on most commonly referenced missing assets
        asset_counts = {}
        for asset in self.results['missing_assets']:
            asset_path = asset['asset_path']
            if asset_path in asset_counts:
                asset_counts[asset_path] += 1
            else:
                asset_counts[asset_path] = 1
        
        # Sort by frequency
        common_assets = sorted(asset_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Create the most commonly referenced missing assets
        critical_assets = [
            'favicon.ico',
            'favicon.png', 
            'ultron_icon.png',
            'wake.wav',
            'confirm.wav',
            'error.wav',
            'button_press.wav',
            'pokedex_open.wav'
        ]
        
        for asset_name, count in common_assets[:10]:
            if any(critical in asset_name for critical in critical_assets):
                self._create_placeholder_asset(asset_name, count)
    
    def _create_placeholder_asset(self, asset_name: str, reference_count: int):
        """Create a placeholder asset file"""
        # Determine where to create the asset
        possible_locations = [
            self.project_root / 'resources' / 'images',
            self.project_root / 'web_gui' / 'assets',
            self.project_root / 'gui' / 'ultron_enhanced' / 'web' / 'assets',
            self.project_root / 'assets',
            self.project_root / 'static'
        ]
        
        # Create in the first existing directory, or create a new one
        target_dir = None
        for location in possible_locations:
            if location.exists():
                target_dir = location
                break
        
        if not target_dir:
            target_dir = self.project_root / 'assets'
            target_dir.mkdir(exist_ok=True)
        
        target_file = target_dir / asset_name
        
        if not target_file.exists():
            # Create appropriate placeholder
            if asset_name.endswith(('.png', '.ico', '.jpg', '.jpeg', '.gif')):
                self._create_placeholder_image(target_file)
            elif asset_name.endswith(('.wav', '.mp3')):
                self._create_placeholder_audio(target_file)
            else:
                self._create_placeholder_text(target_file)
            
            print(f"   ✅ Created placeholder: {target_file.relative_to(self.project_root)} (referenced {reference_count} times)")
            self.fixes_applied.append(f"Created placeholder asset: {asset_name}")
    
    def _create_placeholder_image(self, file_path: Path):
        """Create a minimal placeholder image"""
        # Create a simple 1x1 pixel PNG
        # PNG header for 1x1 pixel transparent image
        png_data = bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
            0x00, 0x00, 0x00, 0x0D,  # IHDR chunk length
            0x49, 0x48, 0x44, 0x52,  # IHDR
            0x00, 0x00, 0x00, 0x01,  # Width: 1
            0x00, 0x00, 0x00, 0x01,  # Height: 1
            0x08, 0x06, 0x00, 0x00, 0x00,  # Bit depth: 8, Color type: 6 (RGBA), Compression: 0, Filter: 0, Interlace: 0
            0x1F, 0x15, 0xC4, 0x89,  # IHDR CRC
            0x00, 0x00, 0x00, 0x0D,  # IDAT chunk length
            0x49, 0x44, 0x41, 0x54,  # IDAT
            0x78, 0x9C, 0x62, 0x00, 0x02, 0x00, 0x00, 0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4,  # Compressed image data
            0x00, 0x00, 0x00, 0x00,  # IEND chunk length
            0x49, 0x45, 0x4E, 0x44,  # IEND
            0xAE, 0x42, 0x60, 0x82   # IEND CRC
        ])
        
        with open(file_path, 'wb') as f:
            f.write(png_data)
    
    def _create_placeholder_audio(self, file_path: Path):
        """Create a minimal placeholder audio file"""
        # Create a minimal WAV file with silence
        # This is a 1-second silence WAV file
        wav_header = bytes([
            # RIFF header
            0x52, 0x49, 0x46, 0x46,  # "RIFF"
            0x24, 0x08, 0x00, 0x00,  # File size - 8
            0x57, 0x41, 0x56, 0x45,  # "WAVE"
            # fmt chunk
            0x66, 0x6d, 0x74, 0x20,  # "fmt "
            0x10, 0x00, 0x00, 0x00,  # Chunk size
            0x01, 0x00,              # Audio format (PCM)
            0x01, 0x00,              # Number of channels
            0x44, 0xAC, 0x00, 0x00,  # Sample rate (44100)
            0x88, 0x58, 0x01, 0x00,  # Byte rate
            0x02, 0x00,              # Block align
            0x10, 0x00,              # Bits per sample
            # data chunk
            0x64, 0x61, 0x74, 0x61,  # "data"
            0x00, 0x08, 0x00, 0x00,  # Data size
        ])
        
        # Add 2048 bytes of silence (zeros)
        silence_data = bytes([0x00] * 2048)
        
        with open(file_path, 'wb') as f:
            f.write(wav_header + silence_data)
    
    def _create_placeholder_text(self, file_path: Path):
        """Create a placeholder text file"""
        content = f"""# Placeholder file for {file_path.name}
# This file was automatically created to resolve broken references
# Replace with actual content as needed

# Created by Ultron Agent orphan detection and fix tool
"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def remove_confirmed_orphans(self):
        """Remove files that are confirmed orphans"""
        print("\n🗑️  Removing confirmed orphan files...")
        
        # Be very conservative - only remove files that are clearly safe to remove
        safe_to_remove_patterns = [
            '*.pyc',
            '*.pyo', 
            '*__pycache__*',
            '*.log',
            '*.tmp',
            '*backup*',
            '*test*screenshot*',
            '*.bak'
        ]
        
        orphaned_files = self.results['orphaned_files']
        removed_count = 0
        
        for orphan in orphaned_files:
            file_path = self.project_root / orphan['file']
            
            if not file_path.exists():
                continue
            
            # Only remove if it matches safe patterns
            should_remove = any(
                file_path.match(pattern) for pattern in safe_to_remove_patterns
            )
            
            # Additional safety checks
            file_size = orphan.get('size', 0)
            if file_size > 1024 * 1024:  # Don't remove files > 1MB without manual review
                should_remove = False
            
            if should_remove:
                try:
                    # Backup before removal
                    backup_path = self.backup_dir / orphan['file']
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, backup_path)
                    
                    # Remove the file
                    file_path.unlink()
                    removed_count += 1
                    print(f"   🗑️  Removed: {orphan['file']}")
                    self.fixes_applied.append(f"Removed orphan file: {orphan['file']}")
                    
                except Exception as e:
                    print(f"   ❌ Could not remove {orphan['file']}: {e}")
        
        print(f"   📊 Removed {removed_count} orphan files")
    
    def create_gitignore_entries(self):
        """Add appropriate .gitignore entries for common orphan patterns"""
        print("\n📝 Updating .gitignore...")
        
        gitignore_path = self.project_root / '.gitignore'
        
        # Entries to add based on orphan analysis
        new_entries = [
            "# Orphan detection and fix tool outputs",
            "ORPHAN_ANALYSIS_REPORT.md",
            "orphan_analysis_results.json",
            ".orphan_fixes_backup/",
            "",
            "# Common orphan file patterns",
            "*.tmp",
            "*screenshot_*.png",
            "*backup*",
            ".snapshots/",
            "*.log",
            "__pycache__/",
            "*.pyc",
            "*.pyo",
            "",
            "# Development artifacts",
            ".pytest_cache/",
            "cache/",
            "*.swp",
            "*.swo",
            "*~"
        ]
        
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                existing_content = f.read()
        else:
            existing_content = ""
        
        # Check which entries are new
        lines_to_add = []
        for entry in new_entries:
            if entry and entry not in existing_content:
                lines_to_add.append(entry)
        
        if lines_to_add:
            with open(gitignore_path, 'a') as f:
                f.write('\n\n')
                f.write('\n'.join(lines_to_add))
                f.write('\n')
            
            print(f"   ✅ Added {len([e for e in lines_to_add if e and not e.startswith('#')])} new .gitignore entries")
            self.fixes_applied.append("Updated .gitignore with orphan patterns")
    
    def generate_fix_report(self):
        """Generate a report of fixes applied"""
        print("\n📋 Generating fix report...")
        
        report_lines = [
            "# 🔧 Ultron Agent Critical Issues Fix Report",
            f"",
            f"**Fix Date**: {os.popen('date').read().strip()}",
            f"**Backup Location**: {self.backup_dir.relative_to(self.project_root)}",
            "",
            "## 📊 Summary",
            f"- **Total Fixes Applied**: {len(self.fixes_applied)}",
            "",
            "## 🔧 Fixes Applied",
            ""
        ]
        
        for i, fix in enumerate(self.fixes_applied, 1):
            report_lines.append(f"{i}. {fix}")
        
        report_lines.extend([
            "",
            "## 🚨 Manual Review Required",
            "",
            "The following issues require manual attention:",
            "",
            "### Syntax Errors",
            "- Files with syntax errors that couldn't be automatically fixed",
            "- Review files in backup directory if fixes were attempted",
            "",
            "### Large Orphaned Files", 
            "- Files > 1MB that weren't automatically removed",
            "- Review orphan analysis report for full list",
            "",
            "### Missing Dependencies",
            "- Broken imports that may indicate missing packages",
            "- Update requirements.txt as needed",
            "",
            "## 🔄 Rollback Instructions",
            "",
            "To rollback changes:",
            "1. Copy files from backup directory back to original locations",
            "2. Revert .gitignore changes if needed", 
            "3. Re-run orphan detection to verify",
            "",
            "## 📚 Next Steps",
            "",
            "1. Review and test all fixed files",
            "2. Address remaining syntax errors manually",
            "3. Install any missing dependencies",
            "4. Consider removing large orphaned files after review",
            "5. Update documentation references if needed"
        ])
        
        report_path = self.project_root / 'CRITICAL_FIXES_REPORT.md'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        print(f"   ✅ Fix report saved to: {report_path}")
        
        return len(self.fixes_applied)
    
    def apply_all_fixes(self):
        """Apply all critical fixes"""
        print("🚀 Starting critical issue fixes for Ultron Agent...")
        
        self.create_backup()
        self.fix_syntax_errors()
        self.create_missing_assets()
        self.remove_confirmed_orphans()
        self.create_gitignore_entries()
        
        fixes_count = self.generate_fix_report()
        
        print(f"\n✅ Critical fixes complete! Applied {fixes_count} fixes.")
        print(f"📁 Backups saved to: {self.backup_dir}")
        print("📋 Review CRITICAL_FIXES_REPORT.md for details")
        
        return fixes_count


def main():
    """Main function"""
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    fixer = CriticalIssueFixer(project_root)
    fixer.apply_all_fixes()


if __name__ == "__main__":
    main()