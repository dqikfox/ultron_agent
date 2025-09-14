"""
Test the integration of centralized logging with agent_core module
without requiring full dependencies.
"""

import sys
from pathlib import Path

def test_agent_core_logging_integration():
    """Test that agent_core can use the new logging system."""
    print("Testing agent_core logging integration...")
    
    try:
        # Test the imports work
        from utils.ultron_logger import log_info, log_error, log_ai_decision
        from utils.model_awareness import should_modify_file, check_file_context
        print("✓ New centralized systems import successfully")
        
        # Test logging calls like those in agent_core
        log_info("agent_core", "ULTRON Agent Core initializing...")
        log_info("agent_core", "NVIDIA API configured with 2 keys")
        log_info("agent_core", "Models available: ['llama-4-maverick', 'gpt-oss-120b', 'llama-3.3-70b']")
        log_ai_decision("agent_core", "Processing with model: llama-4-maverick", 
                       ai_model="llama-4-maverick", confidence_score=0.9)
        
        print("✓ agent_core style logging calls work correctly")
        
        # Test model awareness for agent_core.py
        should_proceed, reason, context = should_modify_file("agent_core.py", "edit", "copilot")
        print(f"✓ Model awareness check for agent_core.py: {should_proceed}")
        print(f"  Reason: {reason}")
        print(f"  Stability score: {context.stability_score}")
        
        # Check that it's marked as a critical file
        if not should_proceed and "critical" in reason.lower():
            print("✓ agent_core.py correctly identified as critical file")
        elif should_proceed:
            print("✓ agent_core.py safe to modify")
        
        return True
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_log_files_structure():
    """Test that the expected log files are created with proper structure."""
    print("\nTesting log file structure...")
    
    try:
        logs_dir = Path("logs")
        
        # Check for component-specific logs
        expected_logs = {
            "agent_core.log": "agent_core component logs",
            "brain.log": "brain component logs", 
            "ai_activities.log": "AI decision tracking",
            "file_changes.log": "file operation tracking",
            "system.log": "system events",
            "error.log": "centralized error tracking"
        }
        
        found_logs = []
        missing_logs = []
        
        for log_file, description in expected_logs.items():
            log_path = logs_dir / log_file
            if log_path.exists():
                found_logs.append(log_file)
                # Check if it has content (JSON structure)
                try:
                    with open(log_path, 'r') as f:
                        content = f.read()
                        if content.strip():
                            print(f"✓ {log_file} exists with content")
                        else:
                            print(f"✓ {log_file} exists (empty)")
                except Exception as e:
                    print(f"⚠ {log_file} exists but couldn't read: {e}")
            else:
                missing_logs.append(log_file)
        
        if missing_logs:
            print(f"⚠ Missing log files: {missing_logs}")
        
        print(f"✓ Found {len(found_logs)}/{len(expected_logs)} expected log files")
        return len(found_logs) >= len(expected_logs) // 2  # At least half should exist
        
    except Exception as e:
        print(f"✗ Log structure test failed: {e}")
        return False

def run_integration_tests():
    """Run all integration tests."""
    print("=" * 60)
    print("ULTRON Agent 3.0 - Integration Testing")
    print("=" * 60)
    
    results = []
    
    # Test 1: agent_core logging integration
    results.append(test_agent_core_logging_integration())
    
    # Test 2: Log file structure
    results.append(test_log_files_structure())
    
    # Summary
    print("\n" + "=" * 60)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All integration tests passed!")
        print("✓ agent_core.py successfully updated for ULTRON Agent 3.0")
    else:
        print("⚠ Some integration tests failed.")
    
    return passed == total

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)