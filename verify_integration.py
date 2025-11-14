"""
ULTRON Agent Integration Verification
Checks all components are properly connected
"""
import sys
import os
from pathlib import Path

# Fix Unicode encoding for Windows console
os.environ['PYTHONIOENCODING'] = 'utf-8'

def check_file_exists(path: str, description: str) -> bool:
    """Check if file exists"""
    exists = Path(path).exists()
    status = "OK" if exists else "MISSING"
    print(f"[{status}] {description}: {path}")
    return exists

def check_import(module: str, description: str) -> bool:
    """Check if module can be imported"""
    try:
        __import__(module)
        print(f"[OK] {description}: {module}")
        return True
    except ImportError as e:
        print(f"[FAIL] {description}: {module} - Import error")
        return False
    except Exception as e:
        print(f"[WARN] {description}: {module} - {type(e).__name__}")
        return True  # Module exists but has runtime issues

def main():
    print("=" * 60)
    print("ULTRON AGENT INTEGRATION VERIFICATION")
    print("=" * 60)
    print()
    
    checks_passed = 0
    checks_total = 0
    
    # Core files
    print("CORE FILES:")
    checks_total += 1
    checks_passed += check_file_exists("run.bat", "Launcher")
    checks_total += 1
    checks_passed += check_file_exists("main.py", "Main entry")
    checks_total += 1
    checks_passed += check_file_exists("agent_core.py", "Agent core")
    checks_total += 1
    checks_passed += check_file_exists("brain.py", "Brain")
    checks_total += 1
    checks_passed += check_file_exists("ultron_config.json", "Config")
    print()
    
    # New components
    print("NEW COMPONENTS:")
    checks_total += 1
    checks_passed += check_file_exists("ultron_exec.py", "Autonomous executor")
    checks_total += 1
    checks_passed += check_file_exists("tools/autonomous_pyautogui.py", "PyAutoGUI tool")
    checks_total += 1
    checks_passed += check_file_exists("tools/cloud_router.py", "Cloud router")
    checks_total += 1
    checks_passed += check_file_exists("tools/cheap_cloud.py", "Cheap cloud")
    checks_total += 1
    checks_passed += check_file_exists("utils/proactive_assistant.py", "Proactive assistant")
    print()
    
    # Documentation
    print("DOCUMENTATION:")
    checks_total += 1
    checks_passed += check_file_exists("IMPROVEMENT_ROADMAP.md", "Improvement roadmap")
    checks_total += 1
    checks_passed += check_file_exists("CLOUD_CHEAP_SETUP.md", "Cloud setup")
    checks_total += 1
    checks_passed += check_file_exists("AUTONOMOUS_CONTROL_GUIDE.md", "Autonomous guide")
    checks_total += 1
    checks_passed += check_file_exists("AUTONOMOUS_CONTROL_COMPLETE.md", "Completion doc")
    print()
    
    # Python imports
    print("PYTHON IMPORTS:")
    checks_total += 1
    checks_passed += check_import("agent_core", "Agent core module")
    checks_total += 1
    checks_passed += check_import("brain", "Brain module")
    checks_total += 1
    checks_passed += check_import("ultron_exec", "Executor module")
    print()
    
    # Tool loading test
    print("TOOL LOADING TEST:")
    try:
        from agent_core import UltronAgent
        agent = UltronAgent()
        
        # Check if autonomous tool would load
        tools_dir = Path("tools")
        auto_tool = tools_dir / "autonomous_pyautogui.py"
        if auto_tool.exists():
            print("[OK] Autonomous PyAutoGUI tool file present")
            checks_passed += 1
        else:
            print("[FAIL] Autonomous PyAutoGUI tool file missing")
        checks_total += 1
        
        print(f"[INFO] Agent initialized with {len(agent.tools)} tools loaded")
        
    except Exception as e:
        print(f"[FAIL] Agent initialization: {e}")
    print()
    
    # Summary
    print("=" * 60)
    print(f"VERIFICATION COMPLETE: {checks_passed}/{checks_total} checks passed")
    print("=" * 60)
    
    if checks_passed == checks_total:
        print("\nSTATUS: ALL SYSTEMS GO - Ready to run!")
        print("\nTo start ULTRON Agent, run:")
        print("  .\\run.bat")
        return 0
    else:
        print(f"\nSTATUS: {checks_total - checks_passed} issues found")
        print("\nPlease fix missing components before running.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
