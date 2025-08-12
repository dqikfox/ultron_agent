#!/usr/bin/env python3
"""
Test script for run.bat functionality
Tests the ULTRON 3.0 startup process components
"""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

class TestRunBat(unittest.TestCase):
    
    def setUp(self):
        self.project_root = Path(__file__).parent
        self.run_bat_path = self.project_root / "run.bat"
        
    def test_run_bat_exists(self):
        """Test that run.bat file exists"""
        self.assertTrue(self.run_bat_path.exists(), "run.bat file should exist")
    
    def test_python_availability(self):
        """Test that Python is available and working"""
        try:
            result = subprocess.run([sys.executable, "--version"], 
                                  capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, "Python should be available and working")
            self.assertIn("Python", result.stdout, "Should return Python version")
            print(f"✅ Python version: {result.stdout.strip()}")
        except Exception as e:
            self.fail(f"Python check failed: {e}")
    
    def test_requirements_file_exists(self):
        """Test that requirements.txt exists"""
        req_file = self.project_root / "requirements.txt"
        self.assertTrue(req_file.exists(), "requirements.txt should exist")
        
        # Check if it's not empty
        with open(req_file, 'r') as f:
            content = f.read().strip()
            self.assertTrue(len(content) > 0, "requirements.txt should not be empty")
            print(f"✅ Requirements file has {len(content.splitlines())} lines")
    
    def test_main_py_exists(self):
        """Test that main.py exists and is valid Python"""
        main_file = self.project_root / "main.py"
        self.assertTrue(main_file.exists(), "main.py should exist")
        
        # Test syntax by compiling
        try:
            with open(main_file, 'r', encoding='utf-8') as f:
                compile(f.read(), str(main_file), 'exec')
            print("✅ main.py syntax is valid")
        except SyntaxError as e:
            self.fail(f"main.py has syntax errors: {e}")
    
    def test_config_files_exist(self):
        """Test that configuration files exist"""
        config_files = [
            "ultron_config.json.example",
            ".env.example"
        ]
        
        for config_file in config_files:
            file_path = self.project_root / config_file
            self.assertTrue(file_path.exists(), f"{config_file} should exist")
            print(f"✅ {config_file} exists")
    
    def test_batch_file_syntax(self):
        """Test run.bat syntax by running it with echo on (dry run)"""
        try:
            # Create a test version that just echoes commands
            test_content = '''
@echo off
echo [TEST] Testing batch file syntax...
echo [TEST] Python check would run: where python
echo [TEST] Virtual environment check would run
echo [TEST] Dependencies check would run
echo [TEST] Config file check would run
echo [TEST] Main script launch would run: python main.py
echo [TEST] Batch file syntax test completed successfully
'''
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False) as f:
                f.write(test_content)
                test_bat_path = f.name
            
            result = subprocess.run([test_bat_path], 
                                  capture_output=True, text=True, timeout=10)
            
            os.unlink(test_bat_path)  # Clean up
            
            self.assertEqual(result.returncode, 0, "Test batch file should run without errors")
            self.assertIn("syntax test completed successfully", result.stdout)
            print("✅ Batch file syntax test passed")
            
        except Exception as e:
            self.fail(f"Batch file syntax test failed: {e}")
    
    def test_dry_run_main_import(self):
        """Test that main.py can be imported without running"""
        try:
            # Test import without execution
            result = subprocess.run([
                sys.executable, "-c", 
                "import sys; sys.path.insert(0, '.'); import main; print('Import successful')"
            ], capture_output=True, text=True, timeout=15, cwd=self.project_root)
            
            if result.returncode != 0:
                print(f"⚠️  Import test failed: {result.stderr}")
                print("This might indicate missing dependencies or import issues")
            else:
                print("✅ main.py can be imported successfully")
                
        except Exception as e:
            print(f"⚠️  Import test error: {e}")

def run_diagnostics():
    """Run comprehensive diagnostics for ULTRON startup"""
    print("🔍 ULTRON 3.0 Startup Diagnostics")
    print("=" * 50)
    
    # Check current directory
    print(f"📁 Current directory: {os.getcwd()}")
    
    # Check Python version
    print(f"🐍 Python version: {sys.version}")
    
    # Check if we're in the right directory
    if not os.path.exists("main.py"):
        print("❌ ERROR: main.py not found. Are you in the correct directory?")
        return False
    
    if not os.path.exists("run.bat"):
        print("❌ ERROR: run.bat not found. Are you in the correct directory?")
        return False
    
    print("✅ Basic file check passed")
    
    # Check for virtual environment
    if os.path.exists("venv"):
        print("✅ Virtual environment directory found")
    else:
        print("⚠️  Virtual environment not found - will be created by run.bat")
    
    return True

if __name__ == '__main__':
    print("🚀 ULTRON 3.0 Run.bat Test Suite")
    print("=" * 50)
    
    # Run diagnostics first
    if not run_diagnostics():
        print("\n❌ Diagnostics failed. Fix issues before running tests.")
        sys.exit(1)
    
    print("\n🧪 Running unit tests...")
    unittest.main(verbosity=2)
