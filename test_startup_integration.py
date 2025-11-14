"""
Startup Integration Test - Verify all systems work together
"""
import asyncio
import sys
from pathlib import Path

async def test_agent_initialization():
    """Test agent can initialize with all components"""
    print("\n[TEST] Agent Initialization")
    try:
        from agent_core import UltronAgent
        agent = UltronAgent()
        print("  [OK] Agent created")
        
        # Initialize async
        await agent.initialize()
        print("  [OK] Agent initialized")
        
        # Check components
        assert agent.config is not None, "Config missing"
        print("  [OK] Config loaded")
        
        assert agent.tools is not None, "Tools missing"
        print(f"  [OK] Tools loaded: {len(agent.tools)} tools")
        
        # Check for autonomous tool
        tool_names = [name.lower() for name in agent.tools.keys()]
        if 'autonomouspyautogui' in tool_names:
            print("  [OK] Autonomous PyAutoGUI tool loaded")
        else:
            print("  [WARN] Autonomous PyAutoGUI tool not loaded")
        
        return True
        
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False

async def test_tool_execution():
    """Test tool can execute commands"""
    print("\n[TEST] Tool Execution")
    try:
        from agent_core import UltronAgent
        agent = UltronAgent()
        await agent.initialize()
        
        # Test command processing
        result = await agent.process_command("get screen size")
        print(f"  [OK] Command processed: {result.get('success', False)}")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False

async def test_autonomous_executor():
    """Test autonomous executor module"""
    print("\n[TEST] Autonomous Executor")
    try:
        from ultron_exec import UltronExecutor
        
        executor = UltronExecutor()
        print("  [OK] Executor created")
        
        # Test simple code execution
        code = "result = 2 + 2"
        result = executor.execute_code(code)
        print(f"  [OK] Code executed: {result.get('success', False)}")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False

async def test_cloud_integration():
    """Test cloud integration modules"""
    print("\n[TEST] Cloud Integration")
    try:
        # Test cloud router
        from tools.cloud_router import CloudRouter
        router = CloudRouter()
        print("  [OK] Cloud router loaded")
        
        # Test cheap cloud
        from tools.cheap_cloud import CheapCloud
        cloud = CheapCloud()
        print("  [OK] Cheap cloud loaded")
        
        return True
        
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False

async def test_proactive_assistant():
    """Test proactive assistant module"""
    print("\n[TEST] Proactive Assistant")
    try:
        from utils.proactive_assistant import ProactiveAssistant
        
        assistant = ProactiveAssistant()
        print("  [OK] Proactive assistant loaded")
        
        return True
        
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False

async def main():
    """Run all integration tests"""
    print("=" * 60)
    print("ULTRON AGENT STARTUP INTEGRATION TEST")
    print("=" * 60)
    
    tests = [
        ("Agent Initialization", test_agent_initialization),
        ("Tool Execution", test_tool_execution),
        ("Autonomous Executor", test_autonomous_executor),
        ("Cloud Integration", test_cloud_integration),
        ("Proactive Assistant", test_proactive_assistant),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n[ERROR] {name} crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  [{status}] {name}")
    
    print(f"\nRESULT: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\nALL TESTS PASSED - System ready!")
        return 0
    else:
        print(f"\n{total - passed} tests failed - Check errors above")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
