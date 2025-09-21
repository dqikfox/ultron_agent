#!/usr/bin/env python3
"""
Voice Command Simulator for ULTRON Agent

This script simulates voice commands for testing the voice integration
without requiring actual microphone input.
"""

import asyncio
import sys
import os
import time

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_core import UltronAgent

class VoiceSimulator:
    """Simulates voice commands for testing"""

    def __init__(self, agent):
        self.agent = agent
        self.commands = [
            "hello ultron",
            "what time is it",
            "tell me a joke",
            "open browser",
            "show system status",
            "list available tools",
            "goodbye"
        ]

    async def simulate_voice_session(self):
        """Simulate a voice interaction session"""
        print("\n🎤 Starting Voice Command Simulation...")
        print("=" * 50)

        for i, command in enumerate(self.commands, 1):
            print(f"\n[{i}/{len(self.commands)}] Simulating voice command: '{command}'")

            # Simulate processing delay
            await asyncio.sleep(0.5)

            try:
                # Process the command
                response = await self.agent.handle_voice_command(command)
                print(f"🤖 Agent response: {response}")

                # Wait between commands
                await asyncio.sleep(1)

            except Exception as e:
                print(f"❌ Error processing command '{command}': {e}")

        print("\n" + "=" * 50)
        print("🎉 Voice simulation completed!")

async def main():
    """Main test function"""
    print("🧪 ULTRON Agent Voice Command Simulator")
    print("=" * 50)

    # Initialize agent
    agent = UltronAgent()

    try:
        print("1. Initializing agent...")
        await agent.initialize()
        print("✅ Agent initialized successfully")

        # Check voice system
        if not agent.voice:
            print("❌ Voice system not available - cannot run simulation")
            return

        print("✅ Voice system ready")

        # Start simulation
        simulator = VoiceSimulator(agent)
        await simulator.simulate_voice_session()

    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Cleanup
        if hasattr(agent, 'shutdown'):
            try:
                await agent.shutdown()
            except:
                pass

if __name__ == "__main__":
    asyncio.run(main())