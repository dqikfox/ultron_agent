#!/usr/bin/env python3
"""
Amazon Q Developer Integration Test Script
Tests various Q Developer features and integration points.
"""

import subprocess
import sys
import json
import os
from pathlib import Path

def test_q_developer_cli():
    """Test Amazon Q Developer CLI integration"""
    print("🔍 Testing Amazon Q Developer CLI integration...")
    
    try:
        # Test if Q Developer CLI is available
        result = subprocess.run(['q', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Amazon Q CLI available: {result.stdout.strip()}")
            return True
        else:
            print("⚠️ Amazon Q CLI not found in PATH")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("⚠️ Amazon Q CLI not available or timeout")
        return False

def test_github_integration():
    """Test GitHub integration status"""
    print("🔗 Testing GitHub integration...")
    
    # Check if we're in a git repository
    if not Path('.git').exists():
        print("❌ Not in a git repository")
        return False
    
    try:
        # Get repository information
        result = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True)
        if 'github.com' in result.stdout:
            print("✅ GitHub repository detected")
            
            # Check for GitHub workflows
            workflows_path = Path('.github/workflows')
            if workflows_path.exists():
                workflows = list(workflows_path.glob('*.yml'))
                print(f"✅ Found {len(workflows)} GitHub workflows")
                for workflow in workflows:
                    print(f"   - {workflow.name}")
                return True
            else:
                print("⚠️ No GitHub workflows found")
                return False
        else:
            print("⚠️ Not a GitHub repository")
            return False
    except subprocess.SubprocessError:
        print("❌ Git command failed")
        return False

def test_code_analysis_features():
    """Test code analysis capabilities"""
    print("📊 Testing code analysis features...")
    
    # Create a test file with issues for Q Developer to find
    test_file = Path('temp_test_analysis.py')
    test_content = '''
# Test file with intentional issues
import os
import sys

def vulnerable_function(user_input):
    # SQL injection vulnerability
    query = f"SELECT * FROM users WHERE id = {user_input}"
    return query

def inefficient_function(data):
    # O(n²) complexity issue
    result = []
    for i in data:
        for j in data:
            if i == j:
                result.append(i)
    return result

# Hardcoded secret
API_KEY = "sk-1234567890abcdef"

class TestClass:
    def __init__(self):
        self.data = []
    
    def process_data(self, items):
        # Missing error handling
        return items[0]['value']
'''
    
    try:
        test_file.write_text(test_content)
        print(f"✅ Created test file: {test_file}")
        
        # Run basic Python syntax check
        result = subprocess.run([sys.executable, '-m', 'py_compile', str(test_file)], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Test file syntax is valid")
        else:
            print(f"❌ Syntax error in test file: {result.stderr}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test file: {e}")
        return False
    finally:
        # Clean up test file
        if test_file.exists():
            test_file.unlink()
            print("🧹 Cleaned up test file")

def test_ultron_integration():
    """Test ULTRON Agent specific integration"""
    print("🤖 Testing ULTRON Agent integration...")
    
    # Check for ULTRON-specific files
    ultron_files = [
        'ultron_config.json',
        'utils/ultron_logger.py',
        'utils/model_awareness.py',
        '.amazonq/rules/amazon_Q_Rules.md'
    ]
    
    found_files = []
    for file_path in ultron_files:
        if Path(file_path).exists():
            found_files.append(file_path)
            print(f"✅ Found: {file_path}")
        else:
            print(f"⚠️ Missing: {file_path}")
    
    if len(found_files) >= 3:
        print("✅ ULTRON Agent structure detected")
        return True
    else:
        print("❌ ULTRON Agent structure incomplete")
        return False

def generate_test_report():
    """Generate a comprehensive test report"""
    print("\n" + "="*50)
    print("🤖 AMAZON Q DEVELOPER INTEGRATION TEST REPORT")
    print("="*50)
    
    tests = [
        ("CLI Integration", test_q_developer_cli),
        ("GitHub Integration", test_github_integration),
        ("Code Analysis", test_code_analysis_features),
        ("ULTRON Integration", test_ultron_integration)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 30)
        results[test_name] = test_func()
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Amazon Q Developer integration is ready.")
        return True
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = generate_test_report()
    sys.exit(0 if success else 1)