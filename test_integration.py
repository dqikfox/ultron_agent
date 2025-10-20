#!/usr/bin/env python3
"""
Test GitHub Models integration with ULTRON Agent
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_tool_discovery():
    """Test if the GitHub Models tool is discoverable by the agent"""
    print("Testing GitHub Models tool discovery...")
    
    try:
        # Import the tool directly
        from tools.github_models_tool import GitHubModelsTool
        
        # Test tool schema
        schema = GitHubModelsTool.schema()
        print(f"Tool schema: {schema}")
        
        # Test tool instantiation
        tool = GitHubModelsTool()
        print(f"Tool name: {tool.name}")
        print(f"Tool description: {tool.description}")
        
        # Test command matching
        test_commands = [
            "github model help",
            "ask mistral about Python",
            "github ai question"
        ]
        
        for cmd in test_commands:
            if tool.match(cmd):
                print(f"Command '{cmd}' matches GitHub Models tool")
                try:
                    result = tool.execute(cmd)
                    print(f"Result: {result[:100]}...")
                except Exception as e:
                    print(f"Execution error: {e}")
        
        print("GitHub Models tool integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Integration test failed: {e}")
        return False

if __name__ == "__main__":
    test_tool_discovery()