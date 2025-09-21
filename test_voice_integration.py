#!/usr/bin/env python3
"""
Voice Integration Test Script for ULTRON Agent

This script tests the voice system integration in the agent core.
Run this to verify that voice commands are properly processed.
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_core import UltronAgent

async def test_voice_integration():
    """Test the voice system integration"""
    print("🧪 Testing ULTRON Agent Voice Integration...")
    print("=" * 50)

    # Initialize agent
    agent = UltronAgent()

    try:
        print("1. Initializing agent...")
        await agent.initialize()
        print("✅ Agent initialized successfully")

        # Check voice system
        print("\n2. Checking voice system...")
        if agent.voice:
            print("✅ Voice system initialized")
            print(f"   Voice type: {type(agent.voice).__name__}")

            # Test speaking
            print("\n3. Testing voice speaking...")
            test_text = "Voice integration test successful!"
            result = await agent.speak(test_text)
            if result:
                print("✅ Voice speaking test passed")
            else:
                print("❌ Voice speaking test failed")

            # Test voice command handling
            print("\n4. Testing voice command processing...")
            test_command = "hello world"
            response = await agent.handle_voice_command(test_command)
            print(f"✅ Voice command processed: {response}")

        else:
            print("❌ Voice system not initialized")
            print("   Check ultron_config.json for voice settings")

        # Check configuration
        print("\n5. Checking configuration...")
        use_voice = agent.config.get("use_voice", False)
        voice_engine = agent.config.get("voice_engine", "unknown")
        print(f"   use_voice: {use_voice}")
        print(f"   voice_engine: {voice_engine}")

        if use_voice:
            print("✅ Voice is enabled in configuration")
        else:
            print("⚠️  Voice is disabled in configuration")

        print("\n" + "=" * 50)
        print("🎉 Voice integration test completed!")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Cleanup
        if hasattr(agent, 'shutdown'):
            await agent.shutdown()

if __name__ == "__main__":
    asyncio.run(test_voice_integration())