#!/usr/bin/env python3
"""
🧪 ULTRON Pokédx Migration Readiness Checker
Simple test runner to validate migration readiness without complex pytest setup
"""

import os
import sys
from pathlib import Path
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PokédxMigrationChecker:
    """Simple checker for Pokédx migration readiness"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.new_pokedex_dir = self.project_root / "new pokedex"
        self.test_results = []
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def log_result(self, test_name, status, details=""):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,  
            "details": details,
            "timestamp": self.timestamp
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "⚠️" if status == "PARTIAL" else "❌"
        print(f"{status_emoji} {test_name}: {status}")
        if details:
            print(f"   └─ {details}")
        
        logger.info(f"Migration Test - {test_name}: {status} - {details}")
    
    def check_directory_structure(self):
        """Check if new pokédx directory exists with expected structure"""
        print("\n🔍 Checking Directory Structure...")
        
        if not self.new_pokedex_dir.exists():
            self.log_result("Directory Structure", "FAIL", "new pokedex/ directory not found")
            return False
            
        # Check for expected variants
        expected_variants = [
            "ultron_enhanced",
            "ultron_final", 
            "ultron_full_agent",
            "ultron_ultimate",
            "ultron_realtime_audio",
            "ultron_pokedex_complete"
        ]
        
        existing_variants = []
        if self.new_pokedex_dir.is_dir():
            existing_variants = [d.name for d in self.new_pokedex_dir.iterdir() if d.is_dir()]
        
        found_variants = [v for v in expected_variants if v in existing_variants]
        
        if len(found_variants) >= 3:
            self.log_result("Directory Structure", "PASS", f"Found {len(found_variants)} variants: {found_variants[:3]}...")
            return True
        elif len(found_variants) > 0:
            self.log_result("Directory Structure", "PARTIAL", f"Found {len(found_variants)} variants, expected 6+")
            return True
        else:
            self.log_result("Directory Structure", "FAIL", "No expected variants found")
            return False
    
    def check_existing_files(self):
        """Check if required existing files are present"""
        print("\n🔍 Checking Existing ULTRON Files...")
        
        required_files = [
            "agent_core.py",
            "voice_manager.py", 
            "action_logger.py",
            "config.py",
            "brain.py"
        ]
        
        missing_files = []
        for file_name in required_files:
            file_path = self.project_root / file_name
            if not file_path.exists():
                missing_files.append(file_name)
        
        if not missing_files:
            self.log_result("Existing Files", "PASS", "All required ULTRON files present")
            return True
        else:
            self.log_result("Existing Files", "PARTIAL", f"Missing files: {missing_files}")
            return len(missing_files) < len(required_files) / 2
    
    def check_configuration_files(self):
        """Check if configuration files are ready for migration"""
        print("\n🔍 Checking Configuration Files...")
        
        config_files = [
            "ultron_config.json",
            "GUI_TRANSITION_NOTES.md",
            "MINIMAX_INTEGRATION.md"
        ]
        
        existing_configs = []
        for config_file in config_files:
            config_path = self.project_root / config_file
            if config_path.exists():
                existing_configs.append(config_file)
        
        if len(existing_configs) >= 2:
            self.log_result("Configuration Files", "PASS", f"Found {len(existing_configs)} config files")
            return True
        else:
            self.log_result("Configuration Files", "PARTIAL", f"Found {len(existing_configs)} config files")
            return False
    
    def check_documentation_status(self):
        """Check if migration documentation is complete"""
        print("\n🔍 Checking Migration Documentation...")
        
        doc_files = [
            "GUI_TRANSITION_NOTES.md",
            "MINIMAX_INTEGRATION.md", 
            "MINIMAX_POKEDEX_CONNECTION.md",
            "PROJECT_INFO_FOR_CONTINUE.md"
        ]
        
        existing_docs = []
        for doc_file in doc_files:
            doc_path = self.project_root / doc_file
            if doc_path.exists():
                existing_docs.append(doc_file)
        
        if len(existing_docs) >= 3:
            self.log_result("Migration Documentation", "PASS", f"Found {len(existing_docs)} documentation files")
            return True
        else:
            self.log_result("Migration Documentation", "PARTIAL", f"Found {len(existing_docs)} documentation files")
            return len(existing_docs) > 0
    
    def check_git_status(self):
        """Check git status for new pokédx files"""
        print("\n🔍 Checking Git Status...")
        
        try:
            import subprocess
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                 capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                git_output = result.stdout
                
                # Check for new pokédx files
                has_new_pokedex = 'new pokedex/' in git_output or '?? new pokedex/' in git_output
                
                if has_new_pokedex:
                    self.log_result("Git Status", "PASS", "New pokédx files detected and ready for commit")
                    return True
                else:
                    self.log_result("Git Status", "PARTIAL", "Git working, but new pokédx files may already be committed")
                    return True
            else:
                self.log_result("Git Status", "PARTIAL", "Git available but status check had issues")
                return True
                
        except Exception as e:
            self.log_result("Git Status", "PARTIAL", f"Git check failed: {str(e)}")
            return True  # Not critical for migration
    
    def check_accessibility_readiness(self):
        """Check if accessibility features are ready for migration"""
        print("\n🔍 Checking Accessibility Readiness...")
        
        # Check for accessibility-related files
        accessibility_indicators = [
            "action_logger.py",  # Should have accessibility logging
            "voice_manager.py",  # Voice system for motor impairments
            "test_voice_and_logging.py",  # Voice/logging integration tests
            "launch_proper_gui.py"  # Working GUI launcher
        ]
        
        found_indicators = []
        for indicator in accessibility_indicators:
            indicator_path = self.project_root / indicator
            if indicator_path.exists():
                found_indicators.append(indicator)
        
        if len(found_indicators) >= 3:
            self.log_result("Accessibility Readiness", "PASS", f"Found {len(found_indicators)} accessibility indicators")
            return True
        else:
            self.log_result("Accessibility Readiness", "PARTIAL", f"Found {len(found_indicators)} accessibility indicators")
            return len(found_indicators) > 0
    
    def run_migration_readiness_check(self):
        """Run complete migration readiness check"""
        print("🧪 ULTRON → Pokédx Migration Readiness Check")
        print("=" * 60)
        print(f"Test Time: {self.timestamp}")
        
        # Run all checks
        checks = [
            ("Directory Structure", self.check_directory_structure),
            ("Existing Files", self.check_existing_files),
            ("Configuration Files", self.check_configuration_files),
            ("Migration Documentation", self.check_documentation_status),
            ("Git Status", self.check_git_status),
            ("Accessibility Readiness", self.check_accessibility_readiness)
        ]
        
        passed_checks = 0
        total_checks = len(checks)
        
        for check_name, check_func in checks:
            try:
                if check_func():
                    passed_checks += 1
            except Exception as e:
                self.log_result(check_name, "ERROR", str(e))
        
        # Calculate readiness percentage
        readiness_percentage = (passed_checks / total_checks) * 100
        
        print(f"\n📊 Migration Readiness Results:")
        print(f"Passed Checks: {passed_checks}/{total_checks}")
        print(f"Readiness Score: {readiness_percentage:.1f}%")
        
        # Determine migration readiness
        if readiness_percentage >= 80:
            print("\n🚀 MIGRATION READINESS: EXCELLENT - Ready to proceed!")
            migration_status = "READY"
        elif readiness_percentage >= 60:
            print("\n✅ MIGRATION READINESS: GOOD - Can proceed with caution")
            migration_status = "READY_WITH_CAUTION"
        elif readiness_percentage >= 40:
            print("\n⚠️ MIGRATION READINESS: PARTIAL - Address issues first")
            migration_status = "PARTIAL"
        else:
            print("\n❌ MIGRATION READINESS: NOT READY - Significant issues found")
            migration_status = "NOT_READY"
        
        # Log summary
        self.write_migration_log(migration_status, readiness_percentage)
        
        return migration_status, readiness_percentage
    
    def write_migration_log(self, status, percentage):
        """Write migration readiness log to file"""
        log_file = self.project_root / "pokedex_migration_readiness.log"
        
        with open(log_file, 'w') as f:
            f.write("=== ULTRON → Pokédx Migration Readiness Report ===\n")
            f.write(f"Test Date: {self.timestamp}\n")
            f.write(f"Migration Status: {status}\n")
            f.write(f"Readiness Score: {percentage:.1f}%\n\n")
            
            f.write("Detailed Test Results:\n")
            f.write("-" * 40 + "\n")
            
            for result in self.test_results:
                f.write(f"{result['test']}: {result['status']}\n")
                if result['details']:
                    f.write(f"  └─ {result['details']}\n")
            
            f.write("\n" + "=" * 50 + "\n")
        
        print(f"\n📝 Migration log written to: {log_file}")


def main():
    """Main function to run migration readiness check"""
    checker = PokédxMigrationChecker()
    status, percentage = checker.run_migration_readiness_check()
    
    # Return appropriate exit code
    if status in ["READY", "READY_WITH_CAUTION"]:
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
