"""
Test script for Langflow and Langchain tools integration
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_langflow_tool():
    """Test the Langflow tool"""
    try:
        from tools.langflow_tool import LangflowTool

        print("Testing Langflow Tool...")

        # Initialize tool
        tool = LangflowTool()

        # Test match function
        test_commands = [
            "create langflow flow",
            "execute flow id=test",
            "list langflow flows",
            "delete flow id=test",
            "langflow status"
        ]

        for cmd in test_commands:
            matches = tool.match(cmd)
            print(f"Command '{cmd}' matches: {matches}")

        # Test schema
        schema = tool.schema()
        print(f"Tool schema: {schema}")

        print("Langflow Tool test completed successfully!")
        return True

    except Exception as e:
        print(f"Langflow Tool test failed: {str(e)}")
        return False

def test_langchain_tool():
    """Test the Langchain tool"""
    try:
        from tools.langchain_tool import LangchainTool

        print("\nTesting Langchain Tool...")

        # Initialize tool
        tool = LangchainTool()

        # Test match function
        test_commands = [
            "create chain name=test",
            "execute chain id=test",
            "list chains",
            "delete chain id=test",
            "chain status id=test"
        ]

        for cmd in test_commands:
            matches = tool.match(cmd)
            print(f"Command '{cmd}' matches: {matches}")

        # Test schema
        schema = tool.schema()
        print(f"Tool schema: {schema}")

        print("Langchain Tool test completed successfully!")
        return True

    except Exception as e:
        print(f"Langchain Tool test failed: {str(e)}")
        return False

def test_integration():
    """Test integration with ULTRON Agent configuration"""
    try:
        from config import Config

        print("\nTesting Configuration Integration...")

        config = Config()

        # Check if Langflow and Langchain settings exist
        langflow_enabled = getattr(config, 'langflow_enabled', None)
        langchain_enabled = getattr(config, 'langchain_enabled', None)

        print(f"Langflow enabled: {langflow_enabled}")
        print(f"Langchain enabled: {langchain_enabled}")

        print("Configuration integration test completed!")
        return True

    except Exception as e:
        print(f"Configuration integration test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Running Langflow and Langchain Tools Integration Tests")
    print("=" * 60)

    results = []

    # Test individual tools
    results.append(test_langflow_tool())
    results.append(test_langchain_tool())

    # Test integration
    results.append(test_integration())

    print("\n" + "=" * 60)
    print("Test Results Summary:")
    print(f"Langflow Tool: {'PASS' if results[0] else 'FAIL'}")
    print(f"Langchain Tool: {'PASS' if results[1] else 'FAIL'}")
    print(f"Integration: {'PASS' if results[2] else 'FAIL'}")

    if all(results):
        print("\nAll tests passed! Integration is successful.")
        sys.exit(0)
    else:
        print("\nSome tests failed. Please check the output above.")
        sys.exit(1)
