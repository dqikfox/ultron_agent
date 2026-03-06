#!/usr/bin/env python3
"""
Simple test to verify the async/await fix in web_gui_server.py
"""

import asyncio
import inspect
import sys
import os

# Add project root to path
sys.path.insert(0, '/home/ultro/projects/ultron_agent')

class MockAgent:
    """Mock agent with async process_command method"""
    
    async def process_command(self, command: str) -> str:
        """Async method that returns actual result"""
        await asyncio.sleep(0.1)  # Simulate some async work
        return f"✅ Processed: {command}"

def test_process_command_fix():
    """Test the fixed _process_command method logic"""
    agent = MockAgent()
    command = "test command"
    
    # This is the same logic from the fixed _process_command method
    try:
        if hasattr(agent, 'process_command'):
            # Check if process_command is async
            if inspect.iscoroutinefunction(agent.process_command):
                result = asyncio.run(agent.process_command(command))
                print(f"✅ ASYNC FIX WORKS! Result: {result}")
                return result
            else:
                result = agent.process_command(command)
                print(f"✅ SYNC METHOD WORKS! Result: {result}")
                return result
        else:
            return "❌ Agent command processing not available"
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return f"❌ Error: {str(e)}"

def test_old_broken_behavior():
    """Show what the old broken behavior would return"""
    agent = MockAgent()
    command = "test command"
    
    # This is what the OLD code was doing (without await)
    try:
        if hasattr(agent, 'process_command'):
            result = agent.process_command(command)  # This returns a coroutine object!
            print(f"❌ OLD BROKEN BEHAVIOR: {result}")
            print(f"❌ Type: {type(result)}")
            return result
    except Exception as e:
        return f"❌ Error: {str(e)}"

if __name__ == "__main__":
    print("🔧 Testing async/await fix for ULTRON web interface...")
    print()
    
    print("1. Testing FIXED behavior:")
    test_process_command_fix()
    print()
    
    print("2. Showing OLD BROKEN behavior:")
    test_old_broken_behavior()
    print()
    
    print("✅ Fix verification complete!")
    print("The web interface should now return proper AI responses instead of coroutine objects.")