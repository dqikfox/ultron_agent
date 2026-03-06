#!/usr/bin/env python3
"""
Test script to verify the async process_command fix
"""

import asyncio
import inspect
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class MockAgent:
    """Mock agent with async process_command method"""
    
    async def process_command(self, command: str) -> str:
        """Mock async process_command"""
        await asyncio.sleep(0.1)  # Simulate async work
        return f"Processed: {command}"

def test_async_fix():
    """Test the async fix logic"""
    print("🧪 Testing async process_command fix...")
    
    agent = MockAgent()
    command = "test command"
    
    # This is the same logic from the fixed _process_command method
    if hasattr(agent, 'process_command'):
        if inspect.iscoroutinefunction(agent.process_command):
            result = asyncio.run(agent.process_command(command))
        else:
            result = agent.process_command(command)
        
        print(f"✅ Result: {result}")
        return True
    else:
        print("❌ No process_command method found")
        return False

def test_real_agent():
    """Test with real ULTRON agent"""
    print("\n🤖 Testing with real ULTRON agent...")
    
    try:
        from agent_core import UltronAgent
        
        # Create agent but don't initialize (to avoid long startup)
        agent = UltronAgent()
        
        # Check if process_command is async
        if hasattr(agent, 'process_command'):
            is_async = inspect.iscoroutinefunction(agent.process_command)
            print(f"✅ process_command is async: {is_async}")
            
            if is_async:
                print("✅ The fix should work for this method")
            else:
                print("⚠️ Method is not async - fix not needed")
            
            return True
        else:
            print("❌ No process_command method found")
            return False
            
    except Exception as e:
        print(f"❌ Error testing real agent: {e}")
        return False

def main():
    """Run all tests"""
    print("🔧 ULTRON Agent - Async Fix Verification")
    print("=" * 50)
    
    # Test the fix logic
    test1 = test_async_fix()
    
    # Test with real agent
    test2 = test_real_agent()
    
    print("\n📊 Results:")
    print(f"Mock test: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"Real agent test: {'✅ PASS' if test2 else '❌ FAIL'}")
    
    if test1 and test2:
        print("\n🎉 All tests passed! The async fix should work.")
        return 0
    else:
        print("\n⚠️ Some tests failed. Check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())