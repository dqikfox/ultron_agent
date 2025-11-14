"""
Test script to verify Ollama integration with ULTRON Agent brain
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from brain import UltronBrain
from utils.ultron_logger import log_info, log_error

async def test_ollama_communication():
    """Test direct communication with Ollama through the brain module"""

    print("=" * 60)
    print("ULTRON Agent - Ollama Integration Test")
    print("=" * 60)
    print()

    # Initialize brain
    print("[1/4] Initializing UltronBrain...")
    try:
        brain = UltronBrain()
        await brain.initialize()
        log_info("test_ollama", "Brain initialized successfully")
        print("✅ Brain initialization successful")
    except Exception as e:
        log_error("test_ollama", f"Brain initialization failed: {e}")
        print(f"❌ Brain initialization failed: {e}")
        return False

    print()

    # Test simple query
    print("[2/4] Testing simple query...")
    try:
        response = await brain.think("What is 2+2? Answer in one sentence.")
        print(f"✅ Response: {response}")
        log_info("test_ollama", f"Simple query successful: {response}")
    except Exception as e:
        log_error("test_ollama", f"Simple query failed: {e}")
        print(f"❌ Simple query failed: {e}")
        return False

    print()

    # Test complex query
    print("[3/4] Testing complex query...")
    try:
        response = await brain.think("Explain what an AI agent is in 2 sentences.")
        print(f"✅ Response: {response}")
        log_info("test_ollama", f"Complex query successful")
    except Exception as e:
        log_error("test_ollama", f"Complex query failed: {e}")
        print(f"❌ Complex query failed: {e}")
        return False

    print()

    # Test planning capability
    print("[4/4] Testing planning capability...")
    try:
        plan = await brain.plan("Create a simple Python script", context={})
        print(f"✅ Plan generated: {len(plan)} steps")
        log_info("test_ollama", f"Planning successful: {len(plan)} steps")
        for i, step in enumerate(plan[:3], 1):  # Show first 3 steps
            print(f"   Step {i}: {step[:80]}...")
    except Exception as e:
        log_error("test_ollama", f"Planning failed: {e}")
        print(f"❌ Planning failed: {e}")
        return False

    print()
    print("=" * 60)
    print("✅ ALL TESTS PASSED - Ollama integration working correctly!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    print()
    result = asyncio.run(test_ollama_communication())
    sys.exit(0 if result else 1)
