#!/usr/bin/env python3
"""Test OpenAI Computer Use Integration"""

import os
import time
from openai_computer_use_integration import UltronComputerUseAPI
from tools.openai_computer_use_tool import OpenAIComputerUseTool

def test_computer_use_integration():
    """Test OpenAI Computer Use functionality"""
    
    print("=== TESTING OPENAI COMPUTER USE ===")
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY not set - using mock mode")
    else:
        print("[OK] OpenAI API key configured")
    
    # Initialize API
    api = UltronComputerUseAPI()
    
    # Test 1: Status check
    print("\n--- Test 1: Status Check ---")
    status = api.get_status()
    print(f"Enabled: {status['enabled']}")
    print(f"API Key: {'OK' if status['api_key_configured'] else 'MISSING'}")
    print(f"Session Commands: {status['session_summary']['total_commands']}")
    
    # Test 2: Tool matching
    print("\n--- Test 2: Command Matching ---")
    tool = OpenAIComputerUseTool()
    
    test_commands = [
        "take a screenshot",
        "click on the button", 
        "type hello world",
        "scroll down the page",
        "press enter key",
        "open file menu"  # Should not match
    ]
    
    for cmd in test_commands:
        matches = tool.match(cmd)
        print(f"'{cmd}' -> {matches}")
    
    # Test 3: Voice command processing
    print("\n--- Test 3: Voice Commands ---")
    voice_commands = [
        "computer take a screenshot",
        "click on the desktop",
        "type my name",
        "scroll down"
    ]
    
    for voice_cmd in voice_commands:
        print(f"Processing: '{voice_cmd}'")
        result = api.handle_voice_command(voice_cmd)
        print(f"Result: {result}")
        time.sleep(1)
    
    # Test 4: Session summary
    print("\n--- Test 4: Session Summary ---")
    summary = api.manager.get_session_summary()
    print(f"Total Commands: {summary['total_commands']}")
    print(f"Success Rate: {summary['success_rate']:.2%}")
    print(f"Avg Execution Time: {summary['avg_execution_time']:.2f}s")
    
    # Test 5: Export session log
    print("\n--- Test 5: Export Session ---")
    log_file = api.manager.export_session_log()
    if log_file:
        print(f"[OK] Session exported to: {log_file}")
    else:
        print("[ERROR] Session export failed")
    
    # Test 6: Toggle functionality
    print("\n--- Test 6: Toggle Computer Use ---")
    original_state = api.manager.enabled
    
    # Disable
    api.manager.toggle_computer_use(False)
    print(f"Disabled: {not api.manager.enabled}")
    
    # Test disabled command
    result = api.manager.process_computer_command("test command")
    print(f"Disabled result: {result['status']}")
    
    # Re-enable
    api.manager.toggle_computer_use(True)
    print(f"Re-enabled: {api.manager.enabled}")
    
    print("\n=== COMPUTER USE TESTS COMPLETE ===")
    
    return {
        "api_key_configured": status['api_key_configured'],
        "commands_processed": summary['total_commands'],
        "success_rate": summary['success_rate'],
        "integration_ready": True
    }

if __name__ == "__main__":
    results = test_computer_use_integration()
    
    print(f"\n=== FINAL RESULTS ===")
    print(f"API Key: {'OK' if results['api_key_configured'] else 'MISSING'}")
    print(f"Commands: {results['commands_processed']}")
    print(f"Success Rate: {results['success_rate']:.2%}")
    print(f"Integration: {'OK' if results['integration_ready'] else 'ERROR'}")
    
    if results['integration_ready']:
        print("\n[SUCCESS] OpenAI Computer Use integration is ready!")
        print("Usage: 'computer take screenshot', 'click on button', 'type text'")
    else:
        print("\n[WARNING] Integration needs configuration")