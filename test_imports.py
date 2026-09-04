#!/usr/bin/env python3
"""
Quick test script to check for import issues in ULTRON Agent
"""

import sys
import traceback

def test_import(module_name, description=""):
    """Test importing a module and report results"""
    try:
        __import__(module_name)
        print(f"✅ {module_name} - {description}")
        return True
    except ImportError as e:
        print(f"❌ {module_name} - {description}: {e}")
        return False
    except Exception as e:
        print(f"⚠️  {module_name} - {description}: {e}")
        return False

def main():
    print("🔍 Testing ULTRON Agent imports...")
    print("=" * 50)
    
    # Test core modules
    success_count = 0
    total_count = 0
    
    tests = [
        ("agent_core", "Main agent system"),
        ("brain", "AI reasoning system"),
        ("memory", "Memory management"),
        ("voice", "Voice system"),
        ("vision", "Vision system"),
        ("config", "Configuration management"),
        ("security_utils", "Security utilities"),
        ("utils.ultron_logger", "Logging system"),
        ("utils.event_system", "Event system"),
        ("tools.mobile_web_interface_tool", "Web interface tool"),
        ("tools.multimodal_vision_tool", "Vision tool"),
    ]
    
    for module, desc in tests:
        total_count += 1
        if test_import(module, desc):
            success_count += 1
    
    print("=" * 50)
    print(f"Results: {success_count}/{total_count} modules imported successfully")
    
    if success_count == total_count:
        print("🎉 All core modules imported successfully!")
        return 0
    else:
        print("⚠️  Some modules have import issues. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())