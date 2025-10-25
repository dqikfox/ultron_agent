#!/usr/bin/env python3
"""Simple integration test for ULTRON Agent enhancements"""

import os
import json
from pathlib import Path

def test_files_created():
    """Test that all new files were created"""
    required_files = [
        'aws_integration/lambda_functions/oasis_bedrock_handler.py',
        'aws_integration/cloudformation/ultron-aws-infrastructure.yaml',
        'aws_integration/monitoring/cost_monitor.py',
        'tools/aws_bedrock_tool.py',
        'tools/voice_aws_tool.py',
        'tools/mcp_enhanced_tool.py',
        '.github/workflows/amazon-q-review.yml',
        '.github/workflows/aws-deployment.yml',
        'development_dashboard.py'
    ]
    
    results = []
    for file_path in required_files:
        if Path(file_path).exists():
            results.append(f"PASS: {file_path}")
        else:
            results.append(f"FAIL: {file_path}")
    
    return results

def test_config_updated():
    """Test that configuration was updated"""
    config_path = Path("ultron_config.json")
    
    if not config_path.exists():
        return "FAIL: ultron_config.json not found"
    
    with open(config_path) as f:
        config = json.load(f)
    
    required_sections = ['aws_bedrock', 'voice_aws', 'mcp_enhanced']
    results = []
    
    for section in required_sections:
        if section in config:
            results.append(f"PASS: {section} configuration added")
        else:
            results.append(f"FAIL: {section} configuration missing")
    
    return results

def test_tools_available():
    """Test that new tools are available"""
    tools_dir = Path("tools")
    new_tools = [
        'aws_bedrock_tool.py',
        'voice_aws_tool.py', 
        'mcp_enhanced_tool.py'
    ]
    
    results = []
    for tool in new_tools:
        tool_path = tools_dir / tool
        if tool_path.exists():
            results.append(f"PASS: {tool} available")
        else:
            results.append(f"FAIL: {tool} missing")
    
    return results

def main():
    print("ULTRON Agent Integration Test")
    print("=" * 40)
    
    # Test file creation
    print("\n1. Testing file creation:")
    file_results = test_files_created()
    for result in file_results:
        print(f"   {result}")
    
    # Test configuration
    print("\n2. Testing configuration:")
    config_results = test_config_updated()
    for result in config_results:
        print(f"   {result}")
    
    # Test tools
    print("\n3. Testing tools:")
    tool_results = test_tools_available()
    for result in tool_results:
        print(f"   {result}")
    
    # Summary
    all_results = file_results + config_results + tool_results
    passed = len([r for r in all_results if r.startswith("PASS")])
    total = len(all_results)
    
    print(f"\nSummary: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! Integration ready.")
    else:
        print("Some tests failed. Check output above.")

if __name__ == "__main__":
    main()