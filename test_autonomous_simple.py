"""
Simple Autonomous Execution Test (No Unicode)
"""
import asyncio
from agent_core import UltronAgent

async def test():
    print("="*60)
    print("ULTRON Autonomous Execution Test")
    print("="*60)
    
    agent = UltronAgent()
    
    try:
        print("\n[1/4] Initializing agent...")
        await agent.initialize()
        print(f"[OK] Agent initialized with {len(agent.tools)} tools")
        
        # Check for autonomous tool
        if 'autonomouspyautogui' in agent.tools:
            print("[OK] Autonomous PyAutoGUI tool loaded")
        else:
            print("[WARN] Autonomous PyAutoGUI tool NOT found")
            print(f"Available tools: {list(agent.tools.keys())[:5]}")
        
        print("\n[2/4] Testing screen size command...")
        result = await agent.process_command("what is the screen size")
        print(f"Response: {result.get('response', 'No response')[:100]}")
        
        print("\n[3/4] Testing mouse position...")
        result = await agent.process_command("where is the mouse")
        print(f"Response: {result.get('response', 'No response')[:100]}")
        
        print("\n[4/4] Testing screenshot...")
        result = await agent.process_command("take a screenshot")
        print(f"Response: {result.get('response', 'No response')[:100]}")
        
        print("\n" + "="*60)
        print("Test Complete!")
        print("="*60)
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)[:200]}")
    finally:
        agent.is_running = False

if __name__ == "__main__":
    asyncio.run(test())
