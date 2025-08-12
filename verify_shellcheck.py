#!/usr/bin/env python3
"""
Shellcheck Installation Verification Script
Tests that shellcheck is properly installed and accessible
"""

import subprocess
import sys
import os

def test_shellcheck():
    """Test if shellcheck is properly installed and working"""
    print("🔍 Testing Shellcheck Installation...")
    
    try:
        # Test direct command
        result = subprocess.run(['shellcheck', '--version'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Shellcheck is working!")
            print(f"📄 Version info:\n{result.stdout}")
            return True
        else:
            print(f"❌ Shellcheck command failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ Shellcheck command not found in PATH")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Shellcheck command timed out")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_path():
    """Check if shellcheck is in PATH"""
    print("\n🔍 Checking PATH...")
    path_dirs = os.environ.get('PATH', '').split(os.pathsep)
    
    scoop_dirs = [d for d in path_dirs if 'scoop' in d.lower()]
    if scoop_dirs:
        print(f"✅ Found scoop directories in PATH: {scoop_dirs}")
    else:
        print("⚠️  No scoop directories found in PATH")
    
    return bool(scoop_dirs)

def suggest_fixes():
    """Suggest fixes for shellcheck installation issues"""
    print("\n🔧 Suggested fixes:")
    print("1. Restart your terminal/IDE to refresh PATH")
    print("2. Run: scoop install shellcheck")
    print("3. Add scoop shims to PATH manually:")
    print("   $env:PATH += ';$env:USERPROFILE\\scoop\\shims'")
    print("4. Use full path to shellcheck:")
    print("   $env:USERPROFILE\\scoop\\shims\\shellcheck.exe")

if __name__ == '__main__':
    print("🚀 ULTRON 3.0 - Shellcheck Verification")
    print("=" * 50)
    
    shellcheck_ok = test_shellcheck()
    path_ok = check_path()
    
    if shellcheck_ok and path_ok:
        print("\n🎉 Shellcheck is properly installed and configured!")
        sys.exit(0)
    else:
        print("\n❌ Shellcheck installation issues detected")
        suggest_fixes()
        sys.exit(1)
