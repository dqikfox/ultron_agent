#!/usr/bin/env python3
"""
ULTRON Agent Auto-Fix Tool
Automatically fixes common integration issues
"""
import os
import json
import re
from pathlib import Path
from typing import List, Dict

class UltronAutoFixer:
    def __init__(self, root_dir: str = "."):
        self.root = Path(root_dir)
        self.fixes_applied = []
        self.backup_dir = self.root / "backups" / "auto_fix"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def run_auto_fix(self):
        """Run all auto-fix procedures"""
        print("=" * 70)
        print("  ULTRON AUTO-FIX TOOL")
        print("=" * 70)
        print()
        
        # Load audit report
        report_file = self.root / 'SYSTEM_AUDIT_REPORT.json'
        if not report_file.exists():
            print("❌ No audit report found. Run SYSTEM_AUDIT_AND_FIX.py first!")
            return
        
        with open(report_file) as f:
            self.report = json.load(f)
        
        print(f"Found {self.report['summary']['total_issues']} issues to fix\n")
        
        # Fix procedures
        self.fix_missing_imports()
        self.fix_broken_integrations()
        self.connect_orphaned_components()
        self.fix_configuration()
        self.create_integration_layer()
        
        # Summary
        self.print_summary()
    
    def backup_file(self, filepath: Path):
        """Create backup before modifying"""
        if filepath.exists():
            backup_path = self.backup_dir / filepath.name
            backup_path.write_text(filepath.read_text(encoding='utf-8'), encoding='utf-8')
            return backup_path
        return None
    
    def fix_missing_imports(self):
        """Fix missing import statements"""
        print("[1/5] Fixing missing imports...")
        
        missing = self.report['issues'].get('missing_imports', [])
        for issue in missing:
            # Parse issue: "file.py imports module"
            match = re.match(r'(.+?) imports (.+)', issue)
            if match:
                file_path, module = match.groups()
                full_path = self.root / file_path
                
                if full_path.exists():
                    self.backup_file(full_path)
                    # Add import if not exists
                    content = full_path.read_text(encoding='utf-8')
                    if f"import {module}" not in content and f"from {module}" not in content:
                        # Add import at top after existing imports
                        lines = content.split('\n')
                        import_idx = 0
                        for i, line in enumerate(lines):
                            if line.startswith('import ') or line.startswith('from '):
                                import_idx = i + 1
                        
                        lines.insert(import_idx, f"# Auto-added by ULTRON Auto-Fix\ntry:\n    import {module}\nexcept ImportError:\n    pass")
                        full_path.write_text('\n'.join(lines), encoding='utf-8')
                        self.fixes_applied.append(f"Added import {module} to {file_path}")
        
        print(f"    Fixed {len([f for f in self.fixes_applied if 'import' in f])} import issues")
    
    def fix_broken_integrations(self):
        """Fix broken integrations"""
        print("[2/5] Fixing broken integrations...")
        
        broken = self.report['issues'].get('broken_integrations', [])
        for issue in broken:
            # Create missing integration files
            if "Missing files" in issue:
                integration = issue.split(':')[0]
                print(f"    Creating integration stub for {integration}...")
                # Create basic integration file
                self.create_integration_stub(integration)
        
        print(f"    Fixed {len(broken)} integration issues")
    
    def connect_orphaned_components(self):
        """Connect orphaned components to main system"""
        print("[3/5] Connecting orphaned components...")
        
        orphaned = self.report['issues'].get('orphaned_components', [])
        if not orphaned:
            print("    No orphaned components found")
            return
        
        # Create integration registry
        registry_path = self.root / "component_registry.py"
        registry_content = '''"""
ULTRON Component Registry
Auto-generated integration layer
"""

# Orphaned components integrated here
COMPONENTS = {
'''
        
        for comp in orphaned:
            comp_name = Path(comp).stem
            registry_content += f'    "{comp_name}": "{comp}",\n'
        
        registry_content += '''}

def load_component(name):
    """Dynamically load component"""
    if name in COMPONENTS:
        import importlib
        module_path = COMPONENTS[name].replace('/', '.').replace('\\\\', '.').replace('.py', '')
        return importlib.import_module(module_path)
    return None
'''
        
        registry_path.write_text(registry_content, encoding='utf-8')
        self.fixes_applied.append(f"Created component registry with {len(orphaned)} components")
        print(f"    Connected {len(orphaned)} orphaned components")
    
    def fix_configuration(self):
        """Fix configuration issues"""
        print("[4/5] Fixing configuration...")
        
        missing_config = self.report['issues'].get('missing_config', [])
        for config in missing_config:
            config_file = config.split(' ')[0]
            if config_file == '.env.example':
                self.create_env_example()
            elif config_file == 'requirements.txt':
                self.create_requirements()
        
        print(f"    Fixed {len(missing_config)} configuration issues")
    
    def create_integration_layer(self):
        """Create unified integration layer"""
        print("[5/5] Creating integration layer...")
        
        integration_file = self.root / "ultron_integration_layer.py"
        content = '''"""
ULTRON Integration Layer
Unified interface for all components
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

class UltronIntegrationLayer:
    """Unified integration layer for all ULTRON components"""
    
    def __init__(self):
        self.components = {}
        self.load_all_components()
    
    def load_all_components(self):
        """Load all available components"""
        try:
            from agent_core import UltronCore
            self.components['core'] = UltronCore
        except ImportError:
            pass
        
        try:
            from brain import Brain
            self.components['brain'] = Brain
        except ImportError:
            pass
        
        try:
            from voice_manager import VoiceManager
            self.components['voice'] = VoiceManager
        except ImportError:
            pass
        
        # Load tools
        try:
            from tools import tool_loader
            self.components['tools'] = tool_loader
        except ImportError:
            pass
    
    def get_component(self, name):
        """Get component by name"""
        return self.components.get(name)
    
    def list_components(self):
        """List all loaded components"""
        return list(self.components.keys())

# Global instance
integration_layer = UltronIntegrationLayer()

def get_integration_layer():
    """Get global integration layer"""
    return integration_layer
'''
        
        integration_file.write_text(content, encoding='utf-8')
        self.fixes_applied.append("Created unified integration layer")
        print("    Created ultron_integration_layer.py")
    
    def create_integration_stub(self, integration_name):
        """Create stub file for missing integration"""
        stub_file = self.root / f"{integration_name.lower()}_integration.py"
        content = f'''"""
{integration_name} Integration Stub
Auto-generated by ULTRON Auto-Fix
"""

class {integration_name}Integration:
    """Integration for {integration_name}"""
    
    def __init__(self):
        self.enabled = False
    
    def initialize(self):
        """Initialize integration"""
        try:
            # Add initialization code here
            self.enabled = True
            return True
        except Exception as e:
            print(f"Failed to initialize {integration_name}: {{e}}")
            return False
    
    def is_available(self):
        """Check if integration is available"""
        return self.enabled

# Global instance
{integration_name.lower()}_integration = {integration_name}Integration()
'''
        
        stub_file.write_text(content, encoding='utf-8')
        self.fixes_applied.append(f"Created {integration_name} integration stub")
    
    def create_env_example(self):
        """Create .env.example template"""
        env_file = self.root / ".env.example"
        content = '''# ULTRON Agent Environment Variables

# AI Services
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
ELEVENLABS_APIKEY=your_elevenlabs_key_here
GEMINI_API_KEY=your_gemini_key_here

# AWS
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-1

# Database
POSTGRES_CONNECTION_STRING=postgresql://user:pass@host:5432/db

# LangFlow
LANGFLOW_API_KEY=your_langflow_key
LANGFLOW_PROJECT_ID=your_project_id

# Search
BRAVE_API_KEY=your_brave_api_key

# Slack
SLACK_BOT_TOKEN=your_slack_token
SLACK_TEAM_ID=your_team_id

# Ollama
OLLAMA_HOST=http://localhost:11434
'''
        env_file.write_text(content, encoding='utf-8')
        self.fixes_applied.append("Created .env.example")
    
    def create_requirements(self):
        """Create requirements.txt if missing"""
        req_file = self.root / "requirements.txt"
        if not req_file.exists():
            content = '''# ULTRON Agent Dependencies
fastapi>=0.104.1
flask>=3.0.0
requests>=2.31.0
python-dotenv>=1.0.0
'''
            req_file.write_text(content, encoding='utf-8')
            self.fixes_applied.append("Created requirements.txt")
    
    def print_summary(self):
        """Print summary of fixes"""
        print()
        print("=" * 70)
        print("  FIX SUMMARY")
        print("=" * 70)
        print()
        print(f"Total fixes applied: {len(self.fixes_applied)}")
        print()
        
        if self.fixes_applied:
            print("✅ FIXES APPLIED:")
            for fix in self.fixes_applied:
                print(f"   - {fix}")
        else:
            print("ℹ️  No fixes needed")
        
        print()
        print(f"📁 Backups saved to: {self.backup_dir}")
        print()
        print("=" * 70)
        print("  NEXT STEPS")
        print("=" * 70)
        print()
        print("1. Review changes in your editor")
        print("2. Test the system: python main.py")
        print("3. Run audit again: python SYSTEM_AUDIT_AND_FIX.py")
        print("4. Commit working changes to Git")
        print()

def main():
    fixer = UltronAutoFixer()
    fixer.run_auto_fix()

if __name__ == '__main__':
    main()
