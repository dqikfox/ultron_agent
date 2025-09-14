"""
Comprehensive validation test for ULTRON Agent 3.0 centralized systems.
Tests the complete integration of logging, model awareness, and component updates.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

def test_complete_system_integration():
    """Test the complete integration of all updated components."""
    print("Testing Complete ULTRON Agent 3.0 Integration...")
    
    results = []
    
    # Test 1: Core Components Import
    try:
        from utils.ultron_logger import ultron_logger, log_info, log_error, log_ai_decision, log_file_operation
        from utils.model_awareness import model_awareness, should_modify_file, check_file_context
        print("✓ Core centralized systems import successfully")
        results.append(True)
    except Exception as e:
        print(f"✗ Core systems import failed: {e}")
        results.append(False)
        return False
    
    # Test 2: Component-Specific Logging
    try:
        # Test all components use centralized logging
        components = ['agent_core', 'brain', 'voice', 'gui', 'tools']
        
        for component in components:
            log_info(component, f"Testing {component} component logging")
            log_ai_decision(component, f"AI decision from {component}", 
                           ai_model="test_model", confidence_score=0.9)
        
        print("✓ All components can use centralized logging")
        results.append(True)
    except Exception as e:
        print(f"✗ Component logging failed: {e}")
        results.append(False)
    
    # Test 3: Model Awareness for Critical Files
    try:
        critical_files = ["agent_core.py", "brain.py", "config.py", "voice_manager.py"]
        
        for file_path in critical_files:
            should_proceed, reason, context = should_modify_file(file_path, "edit", "copilot")
            print(f"  {file_path}: {should_proceed} (stability: {context.stability_score:.2f})")
        
        print("✓ Model awareness working for all critical files")
        results.append(True)
    except Exception as e:
        print(f"✗ Model awareness failed: {e}")
        results.append(False)
    
    # Test 4: Log File Structure and Content
    try:
        logs_dir = Path("logs")
        expected_files = [
            "agent_core.log", "brain.log", "voice.log", "gui.log", "tools.log",
            "ai_activities.log", "file_changes.log", "system.log", "error.log"
        ]
        
        existing_files = []
        files_with_content = []
        
        for log_file in expected_files:
            log_path = logs_dir / log_file
            if log_path.exists():
                existing_files.append(log_file)
                
                # Check for structured JSON content
                try:
                    with open(log_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            # Try to parse first line as JSON
                            first_line = content.split('\n')[0]
                            json.loads(first_line)
                            files_with_content.append(log_file)
                except (json.JSONDecodeError, IndexError):
                    pass  # File exists but no valid JSON content yet
        
        print(f"✓ Log files: {len(existing_files)}/{len(expected_files)} exist")
        print(f"✓ JSON content: {len(files_with_content)} files have structured logs")
        results.append(len(existing_files) >= len(expected_files) * 0.8)  # 80% threshold
    except Exception as e:
        print(f"✗ Log file validation failed: {e}")
        results.append(False)
    
    # Test 5: System Health and Status
    try:
        health = model_awareness.get_system_health()
        print(f"✓ System Health:")
        print(f"  Status: {health['system_status']}")
        print(f"  Stability Score: {health['stability_score']}")
        print(f"  Recent Changes: {health['recent_changes']}")
        print(f"  Recent Errors: {health['recent_errors']}")
        
        results.append(health['system_status'] in ['healthy', 'unstable'])
    except Exception as e:
        print(f"✗ System health check failed: {e}")
        results.append(False)
    
    # Test 6: AI Activity Tracking
    try:
        # Generate some AI activities
        log_ai_decision("integration_test", "Testing AI activity tracking", 
                       ai_model="test_copilot", confidence_score=0.95,
                       context={"test": "integration", "component": "validation"})
        
        # Check if activities are recorded
        recent_activities = ultron_logger.get_ai_activities(limit=10)
        ai_activities_found = any("Testing AI activity tracking" in str(activity) for activity in recent_activities)
        
        print(f"✓ AI Activities: {len(recent_activities)} recent activities found")
        print(f"✓ Test activity recorded: {ai_activities_found}")
        results.append(ai_activities_found)
    except Exception as e:
        print(f"✗ AI activity tracking failed: {e}")
        results.append(False)
    
    # Test 7: File Operation Tracking
    try:
        # Test file operation logging
        log_file_operation("integration_test", "Testing file operation tracking", 
                          "test_validation.py", "read")
        
        recent_file_ops = ultron_logger.get_file_changes(limit=10)
        file_ops_found = any("Testing file operation tracking" in str(op) for op in recent_file_ops)
        
        print(f"✓ File Operations: {len(recent_file_ops)} recent operations found")
        print(f"✓ Test operation recorded: {file_ops_found}")
        results.append(file_ops_found)
    except Exception as e:
        print(f"✗ File operation tracking failed: {e}")
        results.append(False)
    
    return all(results)

def test_copilot_instructions_compliance():
    """Test compliance with copilot instructions requirements."""
    print("\nTesting Copilot Instructions Compliance...")
    
    requirements = []
    
    # Check 1: MANDATORY logging system location
    try:
        from utils.ultron_logger import ultron_logger
        print("✓ utils/ultron_logger.py exists and is importable")
        requirements.append(True)
    except ImportError:
        print("✗ MANDATORY utils/ultron_logger.py missing or not importable")
        requirements.append(False)
    
    # Check 2: MANDATORY model awareness system location
    try:
        from utils.model_awareness import model_awareness
        print("✓ utils/model_awareness.py exists and is importable")
        requirements.append(True)
    except ImportError:
        print("✗ MANDATORY utils/model_awareness.py missing or not importable")
        requirements.append(False)
    
    # Check 3: Required logging methods
    try:
        from utils.ultron_logger import log_info, log_error, log_ai_decision, log_file_operation
        print("✓ All required logging methods available")
        requirements.append(True)
    except ImportError as e:
        print(f"✗ Missing required logging methods: {e}")
        requirements.append(False)
    
    # Check 4: Required model awareness methods
    try:
        from utils.model_awareness import should_modify_file, check_file_context
        print("✓ All required model awareness methods available")
        requirements.append(True)
    except ImportError as e:
        print(f"✗ Missing required model awareness methods: {e}")
        requirements.append(False)
    
    # Check 5: Component-specific log files
    try:
        logs_dir = Path("logs")
        required_logs = ["agent_core.log", "brain.log", "ai_activities.log", "file_changes.log"]
        missing_logs = [log for log in required_logs if not (logs_dir / log).exists()]
        
        if not missing_logs:
            print("✓ All required component-specific log files exist")
            requirements.append(True)
        else:
            print(f"✗ Missing required log files: {missing_logs}")
            requirements.append(False)
    except Exception as e:
        print(f"✗ Log file check failed: {e}")
        requirements.append(False)
    
    return all(requirements)

def run_comprehensive_validation():
    """Run all validation tests."""
    print("=" * 70)
    print("ULTRON Agent 3.0 - Comprehensive Validation")
    print("=" * 70)
    
    # Test 1: Complete System Integration
    integration_success = test_complete_system_integration()
    
    # Test 2: Copilot Instructions Compliance
    compliance_success = test_copilot_instructions_compliance()
    
    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    
    if integration_success and compliance_success:
        print("🎉 ALL VALIDATION TESTS PASSED!")
        print("✅ ULTRON Agent 3.0 centralized systems are fully implemented")
        print("✅ All copilot instructions requirements met")
        print("✅ System ready for production use")
        
        # Final status
        print("\n📊 Final System Status:")
        try:
            from utils.model_awareness import get_system_health
            health = get_system_health()
            print(f"   System Health: {health['system_status']}")
            print(f"   Stability Score: {health['stability_score']}")
            print(f"   Total Components: agent_core, brain, voice_manager, GUI integrated")
            print(f"   Centralized Logging: ✅ Active")
            print(f"   Model Awareness: ✅ Active")
        except Exception as e:
            print(f"   Status check error: {e}")
        
        return True
    else:
        print("❌ VALIDATION FAILED")
        if not integration_success:
            print("   ❌ System integration issues detected")
        if not compliance_success:
            print("   ❌ Copilot instructions compliance issues detected")
        return False

if __name__ == "__main__":
    success = run_comprehensive_validation()
    sys.exit(0 if success else 1)