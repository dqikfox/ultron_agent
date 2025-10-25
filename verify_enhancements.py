#!/usr/bin/env python3
"""
ULTRON Agent Enhancement Verification Script
Verifies all enhancements from 2025-10-25 are working correctly.
"""

import sys
import json
from pathlib import Path

def check_gui_fix():
    """Verify GUI auto-download fix is in place"""
    print("1. Checking GUI auto-download fix...")
    gui_file = Path("gui/ultron_enhanced/web/app.js")

    if not gui_file.exists():
        print("   ❌ GUI file not found")
        return False

    content = gui_file.read_text(encoding='utf-8')
    if "this.userRequestedExport = false;" in content:
        print("   ✅ GUI fix applied (userRequestedExport initialization found)")
        return True
    else:
        print("   ❌ GUI fix not found")
        return False

def check_diagnostics_imports():
    """Verify diagnostics system can be imported"""
    print("\n2. Checking diagnostics system imports...")
    try:
        from diagnostics import diagnostic_wrapper, track_metric, get_diagnostics
        print("   ✅ Diagnostics module imports successfully")
        return True
    except Exception as e:
        print(f"   ❌ Diagnostics import failed: {e}")
        return False

def check_brain_diagnostics():
    """Verify brain.py has diagnostics integration"""
    print("\n3. Checking brain.py diagnostics integration...")
    brain_file = Path("brain.py")

    if not brain_file.exists():
        print("   ❌ brain.py not found")
        return False

    content = brain_file.read_text(encoding='utf-8')
    checks = [
        ("diagnostics import", "from diagnostics import"),
        ("think decorator", "@diagnostic_wrapper"),
    ]

    passed = 0
    for check_name, search_str in checks:
        if search_str in content:
            print(f"   ✅ {check_name} found")
            passed += 1
        else:
            print(f"   ❌ {check_name} not found")

    return passed == len(checks)

def check_agent_core_diagnostics():
    """Verify agent_core.py has diagnostics integration"""
    print("\n4. Checking agent_core.py diagnostics integration...")
    agent_file = Path("agent_core.py")

    if not agent_file.exists():
        print("   ❌ agent_core.py not found")
        return False

    content = agent_file.read_text(encoding='utf-8')
    checks = [
        ("diagnostics import", "from diagnostics import"),
        ("diagnostics initialization", "self.diagnostics = get_diagnostics"),
        ("voice command decorator", "@diagnostic_wrapper"),
    ]

    passed = 0
    for check_name, search_str in checks:
        if search_str in content:
            print(f"   ✅ {check_name} found")
            passed += 1
        else:
            print(f"   ❌ {check_name} not found")

    return passed == len(checks)

def check_run_bat_services():
    """Verify run.bat includes new services"""
    print("\n5. Checking run.bat service integration...")
    run_file = Path("run.bat")

    if not run_file.exists():
        print("   ❌ run.bat not found")
        return False

    content = run_file.read_text(encoding='utf-8')
    checks = [
        ("API Server step", "ULTRON API Server"),
        ("Diagnostics Dashboard step", "ULTRON Diagnostics"),
        ("6 services summary", "Diagnostics      : http://localhost:5001"),
    ]

    passed = 0
    for check_name, search_str in checks:
        if search_str in content:
            print(f"   ✅ {check_name} found")
            passed += 1
        else:
            print(f"   ❌ {check_name} not found")

    return passed == len(checks)

def check_documentation():
    """Verify enhancement documentation exists"""
    print("\n6. Checking enhancement documentation...")
    docs = [
        "ENHANCEMENTS_2025-10-25.md",
        "DEVELOPER_QUICK_REFERENCE.md",
        "DEVELOPER_SUMMARY_VISUAL.md",
    ]

    found = 0
    for doc in docs:
        if Path(doc).exists():
            print(f"   ✅ {doc} exists")
            found += 1
        else:
            print(f"   ❌ {doc} not found")

    return found == len(docs)

def main():
    """Run all verification checks"""
    print("=" * 60)
    print("ULTRON Agent Enhancement Verification")
    print("Date: 2025-10-25")
    print("=" * 60)

    checks = [
        check_gui_fix,
        check_diagnostics_imports,
        check_brain_diagnostics,
        check_agent_core_diagnostics,
        check_run_bat_services,
        check_documentation,
    ]

    results = []
    for check in checks:
        try:
            results.append(check())
        except Exception as e:
            print(f"   ❌ Check failed with error: {e}")
            results.append(False)

    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)

    print(f"\nPassed: {passed}/{total} checks")

    if passed == total:
        print("\n✅ ALL ENHANCEMENTS VERIFIED SUCCESSFULLY!")
        print("\nNext steps:")
        print("1. Run 'run.bat' to start all services")
        print("2. Open http://localhost:8080 to verify GUI fix")
        print("3. Open http://localhost:5001 for diagnostics dashboard")
        return 0
    else:
        print("\n⚠️ Some checks failed. Review output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
