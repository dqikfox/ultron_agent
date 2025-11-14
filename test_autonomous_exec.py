"""
Test Autonomous Execution Integration
Tests PyAutoGUI control through agent_core
"""
import asyncio
import sys
from agent_core import UltronAgent

async def test_autonomous_execution():
    """Test autonomous PyAutoGUI execution"""
    
    print("=" * 60)
    print("ULTRON Autonomous Execution Test")
    print("=" * 60)
    print()
    
    # Initialize agent
    print("Initializing ULTRON Agent...")
    agent = UltronAgent()
    
    try:
        await agent.initialize()
        print("✅ Agent initialized successfully")
        print(f"✅ Loaded {len(agent.tools)} tools")
        print()
        
        # Check if autonomous_pyautogui tool loaded
        if 'autonomouspyautogui' in agent.tools:
            print("✅ Autonomous PyAutoGUI tool loaded")
        else:
            print("❌ Autonomous PyAutoGUI tool NOT loaded")
            print("Available tools:", list(agent.tools.keys())[:10])
            return
        
        print()
        print("=" * 60)
        print("Running Test Commands")
        print("=" * 60)
        print()
        
        # Test 1: Get screen info
        print("Test 1: Get screen size")
        result = await agent.process_command("what is the screen size")
        print(f"Result: {result.get('response', 'No response')}")
        print()
        
        # Test 2: Get mouse position
        print("Test 2: Get mouse position")
        result = await agent.process_command("where is the mouse")
        print(f"Result: {result.get('response', 'No response')}")
        print()
        
        # Test 3: Move mouse (safe test)
        print("Test 3: Move mouse to center")
        result = await agent.process_command("move mouse to center of screen")
        print(f"Result: {result.get('response', 'No response')}")
        print()
        
        # Test 4: Screenshot
        print("Test 4: Take screenshot")
        result = await agent.process_command("take a screenshot")
        print(f"Result: {result.get('response', 'No response')}")
        print()
        
        print("=" * 60)
        print("All Tests Complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        agent.is_running = False

if __name__ == "__main__":
    asyncio.run(test_autonomous_execution())
