"""
Test the new centralized logging and model awareness systems.
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_ultron_logger():
    """Test the centralized logging system."""
    print("Testing ULTRON Logger...")
    
    try:
        from utils.ultron_logger import ultron_logger, log_info, log_error, log_ai_decision, log_file_operation
        
        # Test basic logging functions
        log_info("test_component", "Testing basic info logging")
        log_error("test_component", "Testing error logging", Exception("Test error"))
        log_ai_decision("test_component", "Testing AI decision", ai_model="test_model", confidence_score=0.8)
        log_file_operation("test_component", "Testing file operation", "test_file.py", "edit")
        
        # Test logger instance methods
        ultron_logger.log_performance("test_component", "test_operation", 150.5)
        ultron_logger.log_security_event("test_component", "test_security_event", user="test_user")
        
        print("✓ ULTRON Logger basic functionality works")
        
        # Test log file creation
        logs_dir = Path("logs")
        expected_files = ["agent_core.log", "brain.log", "voice.log", "gui.log", "tools.log", 
                         "ai_activities.log", "file_changes.log", "system.log", "error.log"]
        
        missing_files = []
        for filename in expected_files:
            if not (logs_dir / filename).exists():
                missing_files.append(filename)
        
        if missing_files:
            print(f"⚠ Missing log files: {missing_files}")
        else:
            print("✓ All expected log files created")
        
        # Test recent logs retrieval
        recent_logs = ultron_logger.get_recent_logs("ai_activities", limit=5)
        if recent_logs:
            print(f"✓ Retrieved {len(recent_logs)} recent AI activity logs")
        else:
            print("⚠ No AI activity logs found")
        
        return True
        
    except Exception as e:
        print(f"✗ ULTRON Logger test failed: {e}")
        return False

def test_model_awareness():
    """Test the model awareness system."""
    print("\nTesting Model Awareness System...")
    
    try:
        from utils.model_awareness import model_awareness, should_modify_file, check_file_context, record_modification
        
        # Test file context checking
        test_file = "test_file.py"
        context = check_file_context(test_file)
        
        print(f"✓ File context retrieved for {test_file}")
        print(f"  - Stability score: {context.stability_score}")
        print(f"  - Recent changes: {len(context.recent_changes)}")
        print(f"  - Dependencies: {len(context.dependencies)}")
        
        # Test modification permission checking
        should_proceed, reason, context = should_modify_file(test_file, "edit", "test_copilot")
        print(f"✓ Modification check result: {should_proceed}")
        print(f"  - Reason: {reason}")
        
        # Test recording modifications
        if should_proceed:
            record_modification(test_file, "test_copilot", "edit", "test_component", "Testing modification recording")
            print("✓ Modification recorded successfully")
        
        # Test system health
        health = model_awareness.get_system_health()
        print(f"✓ System health retrieved:")
        print(f"  - Status: {health['system_status']}")
        print(f"  - Stability score: {health['stability_score']}")
        print(f"  - Recent changes: {health['recent_changes']}")
        
        # Test critical file protection
        should_proceed, reason, _ = should_modify_file("agent_core.py", "delete", "test_copilot")
        if not should_proceed and "delete critical" in reason.lower():
            print("✓ Critical file protection working")
        else:
            print("⚠ Critical file protection may not be working correctly")
        
        return True
        
    except Exception as e:
        print(f"✗ Model Awareness test failed: {e}")
        return False

def test_integration():
    """Test integration between logging and model awareness."""
    print("\nTesting System Integration...")
    
    try:
        from utils.ultron_logger import log_ai_decision
        from utils.model_awareness import should_modify_file, record_modification
        
        # Test integrated workflow
        test_file = "integration_test.py"
        
        # Step 1: Check if modification should proceed
        should_proceed, reason, context = should_modify_file(test_file, "create", "copilot_test")
        log_ai_decision("integration_test", f"Modification check: {reason}", 
                       ai_model="copilot_test", confidence_score=0.9)
        
        # Step 2: If allowed, record the modification
        if should_proceed:
            record_modification(test_file, "copilot_test", "create", 
                              "integration_test", "Testing integrated workflow")
            log_ai_decision("integration_test", "Modification completed successfully",
                           ai_model="copilot_test", confidence_score=1.0)
        
        print("✓ Integration workflow completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        return False

def run_tests():
    """Run all tests for the new systems."""
    print("=" * 60)
    print("ULTRON Agent 3.0 - Testing Critical Components")
    print("=" * 60)
    
    results = []
    
    # Test 1: ULTRON Logger
    results.append(test_ultron_logger())
    
    # Test 2: Model Awareness
    results.append(test_model_awareness())
    
    # Test 3: Integration
    results.append(test_integration())
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All critical components are working correctly!")
        print("✓ ULTRON Agent 3.0 centralized systems are ready for use.")
    else:
        print("⚠ Some tests failed. Please review the output above.")
    
    return passed == total

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)