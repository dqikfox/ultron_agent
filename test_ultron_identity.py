#!/usr/bin/env python3
"""
Test ULTRON Identity and Tool Awareness
Run this to verify the model knows it's ULTRON and has tool access
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agent_core import UltronAgent


async def test_identity():
    """Test ULTRON identity awareness"""
    print("=" * 60)
    print("ULTRON IDENTITY & TOOL AWARENESS TEST")
    print("=" * 60)
    
    # Initialize agent
    print("\n[1/4] Initializing ULTRON Agent...")
    agent = UltronAgent()
    await agent.initialize()
    
    # Test 1: Identity Check
    print("\n[2/4] Testing Identity Awareness...")
    print("Question: 'Who are you?'")
    response1 = await agent.brain.direct_chat("Who are you? What is your name and purpose?")
    print(f"\nResponse:\n{response1}\n")
    
    # Check for ULTRON identity
    if "ULTRON" in response1.upper():
        print("✅ PASS: Model identifies as ULTRON")
    else:
        print("❌ FAIL: Model does NOT identify as ULTRON")
    
    # Test 2: Tool Awareness
    print("\n[3/4] Testing Tool Awareness...")
    print("Question: 'What tools do you have access to?'")
    response2 = await agent.brain.direct_chat("What tools and capabilities do you have access to? List some examples.")
    print(f"\nResponse:\n{response2}\n")
    
    # Check for tool mentions
    tool_count = len(agent.tools)
    if any(word in response2.lower() for word in ['tool', 'capability', 'access', 'system']):
        print(f"✅ PASS: Model mentions tools/capabilities ({tool_count} tools loaded)")
    else:
        print(f"❌ FAIL: Model doesn't mention tools ({tool_count} tools loaded)")
    
    # Test 3: Service Awareness
    print("\n[4/4] Testing Service Awareness...")
    print("Question: 'What systems are you connected to?'")
    response3 = await agent.brain.direct_chat("What systems and services are you connected to? What can you do?")
    print(f"\nResponse:\n{response3}\n")
    
    # Check for service mentions
    services = ['memory', 'brain', 'voice', 'vision', 'ollama']
    mentioned_services = [s for s in services if s in response3.lower()]
    if mentioned_services:
        print(f"✅ PASS: Model mentions services: {', '.join(mentioned_services)}")
    else:
        print("❌ FAIL: Model doesn't mention connected services")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Memory System: {'✅ UltronMemory' if hasattr(agent.memory, 'get_ultron_identity') else '❌ Basic Memory'}")
    print(f"Tools Loaded: {tool_count}")
    print(f"Brain Connected: {'✅' if agent.brain else '❌'}")
    print(f"Ollama Model: {agent.config.get('llm_model', 'unknown')}")
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(test_identity())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
