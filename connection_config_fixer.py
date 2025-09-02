"""
Connection Configuration Fixer for ULTRON Agent 3.0
Fixes URL configuration issues, especially for Ollama and Tamagotchi project connections
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import re

logger = logging.getLogger(__name__)

class ConnectionConfigurationFixer:
    """
    Fixes common connection configuration issues in ULTRON Agent
    Addresses URL misconfigurations, port conflicts, and service connection problems
    """
    
    def __init__(self):
        self.fixes_applied: List[str] = []
        self.issues_found: List[str] = []
        
        # Common incorrect URLs and their correct versions
        self.url_fixes = {
            # Ollama common misconfigurations
            "http://localhost:11435": "http://localhost:11434",
            "https://localhost:11434": "http://localhost:11434", 
            "http://127.0.0.1:11435": "http://localhost:11434",
            "localhost:11435": "http://localhost:11434",
            
            # Common web server misconfigurations
            "http://localhost:8081": "http://localhost:8080",
            "https://localhost:8080": "http://localhost:8080",
            
            # MiniMax/Tamagotchi connection fixes
            "minimax.localhost": "localhost",
            "tamagotchi.minimax": "localhost"
        }
        
        # Files that commonly contain connection URLs
        self.config_files = [
            "ultron_config.json",
            "index.html",
            "web_gui/index.html", 
            "ultron.js",
            "tamagotchi_server.py",
            "web_gui_server.py",
            "ollama_manager.py",
            "utils/startup.py"
        ]

    def diagnose_connection_issues(self) -> Dict[str, Any]:
        """Diagnose connection configuration issues"""
        logger.info("🔍 Diagnosing connection configuration issues...")
        
        diagnosis = {
            "timestamp": "now",
            "ollama_issues": [],
            "web_gui_issues": [],
            "tamagotchi_issues": [],
            "general_issues": [],
            "files_with_issues": [],
            "recommended_fixes": []
        }
        
        # Check each configuration file
        for file_path in self.config_files:
            path = Path(file_path)
            if path.exists():
                issues = self._check_file_for_issues(path)
                if issues:
                    diagnosis["files_with_issues"].append({
                        "file": str(path),
                        "issues": issues
                    })
        
        # Check specific configuration patterns
        diagnosis["ollama_issues"] = self._check_ollama_configuration()
        diagnosis["web_gui_issues"] = self._check_web_gui_configuration()
        diagnosis["tamagotchi_issues"] = self._check_tamagotchi_configuration()
        
        # Generate recommendations
        diagnosis["recommended_fixes"] = self._generate_fix_recommendations(diagnosis)
        
        return diagnosis

    def _check_file_for_issues(self, file_path: Path) -> List[Dict[str, Any]]:
        """Check a specific file for connection issues"""
        issues = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Check for incorrect URLs
            for incorrect_url, correct_url in self.url_fixes.items():
                if incorrect_url in content:
                    issues.append({
                        "type": "incorrect_url",
                        "incorrect": incorrect_url,
                        "correct": correct_url,
                        "line_numbers": self._find_line_numbers(content, incorrect_url)
                    })
            
            # Check for null/undefined URL configurations  
            null_patterns = [
                r'".*_url":\s*null',
                r"'.*_url':\s*null",
                r'ollamaUrl.*=.*null',
                r'baseUrl.*=.*null'
            ]
            
            for pattern in null_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    issues.append({
                        "type": "null_url_config",
                        "pattern": match.group(),
                        "line_number": content[:match.start()].count('\n') + 1
                    })
            
        except Exception as e:
            logger.error(f"Error checking file {file_path}: {e}")
            
        return issues

    def _find_line_numbers(self, content: str, search_text: str) -> List[int]:
        """Find line numbers where text appears"""
        lines = content.split('\n')
        line_numbers = []
        
        for i, line in enumerate(lines, 1):
            if search_text in line:
                line_numbers.append(i)
                
        return line_numbers

    def _check_ollama_configuration(self) -> List[Dict[str, Any]]:
        """Check Ollama-specific configuration issues"""
        issues = []
        
        # Check ultron_config.json for Ollama settings
        config_file = Path("ultron_config.json")
        if config_file.exists():
            try:
                with open(config_file) as f:
                    config = json.load(f)
                
                # Check for missing Ollama base URL
                if "ollama_base_url" not in config:
                    issues.append({
                        "type": "missing_config",
                        "message": "ollama_base_url not configured",
                        "file": "ultron_config.json"
                    })
                elif config.get("ollama_base_url") is None:
                    issues.append({
                        "type": "null_config", 
                        "message": "ollama_base_url is null",
                        "file": "ultron_config.json"
                    })
                    
            except Exception as e:
                issues.append({
                    "type": "config_read_error",
                    "message": f"Error reading ultron_config.json: {e}",
                    "file": "ultron_config.json"
                })
        
        return issues

    def _check_web_gui_configuration(self) -> List[Dict[str, Any]]:
        """Check web GUI configuration issues"""
        issues = []
        
        # Check for web GUI files
        gui_files = ["index.html", "web_gui/index.html", "ultron.js"]
        
        for gui_file in gui_files:
            path = Path(gui_file)
            if path.exists():
                try:
                    content = path.read_text(encoding='utf-8', errors='ignore')
                    
                    # Check for common GUI connection issues
                    if "localhost:11435" in content:
                        issues.append({
                            "type": "incorrect_port",
                            "message": "Web GUI pointing to wrong Ollama port (11435 instead of 11434)",
                            "file": gui_file
                        })
                    
                    if "baseUrl" in content and "null" in content:
                        issues.append({
                            "type": "null_base_url",
                            "message": "Base URL not configured in web GUI",
                            "file": gui_file
                        })
                        
                except Exception as e:
                    if "codec can't decode" not in str(e):
                        logger.error(f"Error checking GUI file {gui_file}: {e}")
        
        return issues

    def _check_tamagotchi_configuration(self) -> List[Dict[str, Any]]:
        """Check Tamagotchi project specific configuration issues"""
        issues = []
        
        # Look for Tamagotchi-related files
        possible_files = [
            "tamagotchi_server.py",
            "minimax_config.json", 
            "resources/*/tamagotchi*",
            "web_gui/tamagotchi*"
        ]
        
        for pattern in possible_files:
            if "*" in pattern:
                # Handle glob patterns
                for path in Path(".").rglob(pattern.split("*")[-1] + "*"):
                    if path.is_file():
                        self._check_tamagotchi_file(path, issues)
            else:
                path = Path(pattern)
                if path.exists():
                    self._check_tamagotchi_file(path, issues)
        
        return issues

    def _check_tamagotchi_file(self, file_path: Path, issues: List[Dict[str, Any]]):
        """Check a specific Tamagotchi-related file"""
        # Skip binary files
        text_extensions = {'.py', '.js', '.json', '.html', '.css', '.txt', '.md', '.yml', '.yaml', '.xml', '.cfg', '.ini'}
        if file_path.suffix.lower() not in text_extensions:
            return
            
        # Skip if file is too large (likely binary)
        if file_path.stat().st_size > 1024 * 1024:  # 1MB limit
            return
            
        # Skip our own fixer files to avoid detecting example patterns
        if file_path.name in ['connection_config_fixer.py', 'enhancement_manager.py', 'test_ultron_enhancements.py']:
            return
            
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Check for MiniMax connection issues
            if "minimax" in content.lower():
                if "localhost:11435" in content or "11435" in content:
                    issues.append({
                        "type": "tamagotchi_port_error",
                        "message": "Tamagotchi project using wrong Ollama port",
                        "file": str(file_path)
                    })
                
                if "minimax.localhost" in content:
                    issues.append({
                        "type": "tamagotchi_domain_error", 
                        "message": "Incorrect domain configuration for MiniMax",
                        "file": str(file_path)
                    })
                    
        except Exception as e:
            # Only log if it's not a common binary file error
            if "codec can't decode" not in str(e):
                logger.error(f"Error checking Tamagotchi file {file_path}: {e}")

    def _generate_fix_recommendations(self, diagnosis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate specific fix recommendations based on diagnosis"""
        recommendations = []
        
        # Ollama fixes
        if diagnosis["ollama_issues"]:
            recommendations.append({
                "priority": "high",
                "category": "ollama",
                "title": "Fix Ollama Connection Configuration", 
                "actions": [
                    "Ensure Ollama is running: 'ollama serve'",
                    "Verify correct port (11434) in all configuration files",
                    "Update ultron_config.json with correct ollama_base_url",
                    "Test connection: curl http://localhost:11434/api/tags"
                ]
            })
        
        # Web GUI fixes
        if diagnosis["web_gui_issues"]:
            recommendations.append({
                "priority": "medium",
                "category": "web_gui",
                "title": "Fix Web GUI Connection Issues",
                "actions": [
                    "Update baseUrl in JavaScript files to http://localhost:11434",
                    "Check CORS settings for cross-origin requests",
                    "Ensure web server is running on correct port (8080)"
                ]
            })
        
        # Tamagotchi fixes
        if diagnosis["tamagotchi_issues"]:
            recommendations.append({
                "priority": "high", 
                "category": "tamagotchi",
                "title": "Fix Tamagotchi/MiniMax Connection",
                "actions": [
                    "Update MiniMax configuration to use localhost:11434",
                    "Check MiniMax deployment settings",
                    "Verify network connectivity between MiniMax and Ollama",
                    "Test connection from MiniMax environment"
                ]
            })
        
        # General connection fixes
        if any(diagnosis[key] for key in ["ollama_issues", "web_gui_issues", "tamagotchi_issues"]):
            recommendations.append({
                "priority": "low",
                "category": "general",
                "title": "General Connection Health",
                "actions": [
                    "Run service health check",
                    "Check for port conflicts",
                    "Verify firewall settings",
                    "Check DNS resolution for localhost"
                ]
            })
        
        return recommendations

    def apply_automatic_fixes(self) -> Dict[str, Any]:
        """Apply automatic fixes that are safe to apply"""
        logger.info("🔧 Applying automatic connection configuration fixes...")
        
        results = {
            "fixes_applied": 0,
            "fixes_failed": 0, 
            "files_modified": [],
            "backup_files_created": [],
            "errors": []
        }
        
        # Apply URL fixes to configuration files
        for file_path in self.config_files:
            path = Path(file_path)
            if path.exists():
                try:
                    modified = self._fix_file_urls(path)
                    if modified:
                        results["fixes_applied"] += 1
                        results["files_modified"].append(str(path))
                        
                        # Create backup
                        backup_path = path.with_suffix(f"{path.suffix}.backup_connection_fix")
                        path.rename(backup_path)
                        results["backup_files_created"].append(str(backup_path))
                        
                except Exception as e:
                    results["fixes_failed"] += 1
                    results["errors"].append(f"Error fixing {path}: {e}")
                    logger.error(f"Error fixing {path}: {e}")
        
        # Apply specific configuration fixes
        try:
            config_fixes = self._fix_ultron_config()
            results["fixes_applied"] += len(config_fixes)
            results["files_modified"].extend(config_fixes)
        except Exception as e:
            results["fixes_failed"] += 1
            results["errors"].append(f"Error fixing ultron_config.json: {e}")
        
        logger.info(f"✅ Applied {results['fixes_applied']} connection fixes")
        if results["fixes_failed"] > 0:
            logger.warning(f"⚠️ {results['fixes_failed']} fixes failed")
            
        return results

    def _fix_file_urls(self, file_path: Path) -> bool:
        """Fix URLs in a specific file"""
        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            # Apply URL fixes
            for incorrect_url, correct_url in self.url_fixes.items():
                if incorrect_url in content:
                    content = content.replace(incorrect_url, correct_url)
                    logger.info(f"Fixed URL in {file_path}: {incorrect_url} -> {correct_url}")
            
            # Write back if modified
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                return True
                
        except Exception as e:
            logger.error(f"Error fixing URLs in {file_path}: {e}")
            raise
            
        return False

    def _fix_ultron_config(self) -> List[str]:
        """Fix ULTRON configuration file"""
        config_file = Path("ultron_config.json")
        if not config_file.exists():
            return []
        
        try:
            with open(config_file) as f:
                config = json.load(f)
            
            modified = False
            fixes = []
            
            # Add missing Ollama configuration
            if "ollama_base_url" not in config or config.get("ollama_base_url") is None:
                config["ollama_base_url"] = "http://localhost:11434"
                modified = True
                fixes.append("Added ollama_base_url configuration")
            
            # Fix incorrect Ollama URL
            if config.get("ollama_base_url") in self.url_fixes:
                config["ollama_base_url"] = self.url_fixes[config["ollama_base_url"]]
                modified = True
                fixes.append("Fixed incorrect ollama_base_url")
            
            # Ensure web GUI port is correct
            if "web_gui_port" not in config:
                config["web_gui_port"] = 8080
                modified = True
                fixes.append("Added web_gui_port configuration")
            
            # Save if modified
            if modified:
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)
                logger.info(f"Updated {config_file} with connection fixes")
                return [str(config_file)]
                
        except Exception as e:
            logger.error(f"Error fixing ultron_config.json: {e}")
            raise
            
        return []

    def create_service_startup_script(self) -> Path:
        """Create an enhanced service startup script"""
        script_content = '''#!/bin/bash
# Enhanced ULTRON Service Startup Script
# Fixes connection issues and starts all services in correct order

echo "🚀 ULTRON Enhanced Service Startup"
echo "=================================="

# Fix connection configurations first
echo "🔧 Fixing connection configurations..."
python -c "
from connection_config_fixer import ConnectionConfigurationFixer
fixer = ConnectionConfigurationFixer()
results = fixer.apply_automatic_fixes()
print(f'Applied {results[\"fixes_applied\"]} fixes')
"

# Start Ollama first (critical dependency)
echo "🤖 Starting Ollama service..."
if ! pgrep -f "ollama serve" > /dev/null; then
    ollama serve &
    echo "  Ollama server starting..."
    sleep 5
else
    echo "  Ollama already running"
fi

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:11434/api/tags > /dev/null; then
        echo "  ✅ Ollama is ready!"
        break
    fi
    sleep 1
done

# Start web GUI server
echo "🌐 Starting Web GUI server..."
if ! pgrep -f "web_gui_server.py" > /dev/null; then
    python web_gui_server.py &
    echo "  Web GUI server starting..."
    sleep 2
else
    echo "  Web GUI server already running"
fi

# Start agent core
echo "🧠 Starting ULTRON Agent Core..."
if ! pgrep -f "main.py" > /dev/null; then
    python main.py &
    echo "  Agent core starting..."
    sleep 3
else
    echo "  Agent core already running"
fi

# Start monitoring
echo "📊 Starting monitoring dashboard..."
if ! pgrep -f "monitoring_dashboard.py" > /dev/null; then
    python monitoring_dashboard.py &
    echo "  Monitoring dashboard starting..."
    sleep 2
else
    echo "  Monitoring dashboard already running"
fi

echo ""
echo "✅ ULTRON Services Startup Complete!"
echo ""
echo "🌐 Access Points:"
echo "  📊 Dashboard:     http://localhost:9000"  
echo "  🤖 Web GUI:       http://localhost:8080"
echo "  📡 Ollama API:    http://localhost:11434"
echo ""
echo "🔍 Check service status:"
echo "  python -c \\"from service_manager import get_service_manager; print(get_service_manager().get_service_status_report())\\"
'''
        
        script_path = Path("start_ultron_enhanced.sh")
        script_path.write_text(script_content)
        script_path.chmod(0o755)  # Make executable
        
        logger.info(f"Created enhanced startup script: {script_path}")
        return script_path

def main():
    """Test the connection configuration fixer"""
    logging.basicConfig(level=logging.INFO)
    
    fixer = ConnectionConfigurationFixer()
    
    print("🔍 ULTRON Connection Configuration Fixer")
    print("=" * 50)
    
    # Diagnose issues
    diagnosis = fixer.diagnose_connection_issues()
    
    print("Issues Found:")
    total_issues = len(diagnosis["ollama_issues"]) + len(diagnosis["web_gui_issues"]) + len(diagnosis["tamagotchi_issues"])
    print(f"  Total: {total_issues}")
    print(f"  Ollama: {len(diagnosis['ollama_issues'])}")
    print(f"  Web GUI: {len(diagnosis['web_gui_issues'])}")
    print(f"  Tamagotchi: {len(diagnosis['tamagotchi_issues'])}")
    
    if diagnosis["files_with_issues"]:
        print("\nFiles with issues:")
        for file_info in diagnosis["files_with_issues"]:
            print(f"  📄 {file_info['file']}: {len(file_info['issues'])} issues")
    
    # Show recommendations
    if diagnosis["recommended_fixes"]:
        print("\nRecommendations:")
        for fix in diagnosis["recommended_fixes"]:
            print(f"  🔧 {fix['title']} ({fix['priority']} priority)")
    
    # Apply automatic fixes
    print("\n🔧 Applying automatic fixes...")
    results = fixer.apply_automatic_fixes()
    
    print(f"  ✅ Applied: {results['fixes_applied']}")
    print(f"  ❌ Failed: {results['fixes_failed']}")
    
    if results["files_modified"]:
        print("  📝 Modified files:")
        for file in results["files_modified"]:
            print(f"    - {file}")
    
    # Create startup script
    script_path = fixer.create_service_startup_script()
    print(f"\n📜 Created startup script: {script_path}")

if __name__ == "__main__":
    main()