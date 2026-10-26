#!/usr/bin/env python3
"""
Quick Test Execution Script for ULTRON Agent 2
Demonstrates the comprehensive testing setup
"""

import subprocess
import sys
import os
from pathlib import Path

def run_quick_test():
    """Run a quick test to demonstrate the testing setup"""
    print("🤖 ULTRON Agent 2 - Quick Test Demonstration")
    print("=" * 50)
    
    project_root = Path(__file__).parent
    
    # Check if pytest is available
    try:
        import pytest
        print("✅ pytest is available")
    except ImportError:
        print("📦 Installing pytest...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest", "pytest-asyncio"], check=True)
    
    # Run a simple test to verify setup
    print("\n🧪 Running basic configuration test...")
    
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_config.py::TestConfig::test_init_config",
        "-v"
    ]
    
    try:
        result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Test execution successful!")
            print("📊 Test output:")
            print(result.stdout)
        else:
            print("⚠️  Test execution completed with issues:")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
    
    except Exception as e:
        print(f"❌ Error running test: {e}")
    
    print("\n📁 Available test files:")
    tests_dir = project_root / "tests"
    if tests_dir.exists():
        for test_file in tests_dir.glob("test_*.py"):
            print(f"   📄 {test_file.name}")
    
    print("\n🚀 To run comprehensive tests:")
    print("   python test_runner_comprehensive.py")
    print("   python test_runner_comprehensive.py --category unit")
    print("   python test_runner_comprehensive.py --file test_config.py")
    print("   python test_runner_comprehensive.py --health")
    
    print("\n🏁 Testing setup demonstration complete!")

if __name__ == "__main__":
    run_quick_test()
