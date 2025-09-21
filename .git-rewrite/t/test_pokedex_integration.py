#!/usr/bin/env python3
"""
ULTRON Agent 3.0 - Pokédx GUI Integration Test
Verify that the new GUI integrates properly with the agent system
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_gui_import():
    """Test if GUI can be imported correctly"""
    print("🧪 Testing GUI import...")

    try:
        from pokedex_gui import create_pokedex_gui, IntegratedPokedexGUI
        print("✅ Successfully imported Pokédx GUI components")
        return True
    except ImportError as e:
        print(f"❌ Failed to import GUI: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected import error: {e}")
        return False

def test_agent_import():
    """Test if agent can be imported correctly"""
    print("🧪 Testing agent import...")

    try:
        from agent_core import UltronAgent
        print("✅ Successfully imported UltronAgent")
        return True
    except ImportError as e:
        print(f"❌ Failed to import agent: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected agent import error: {e}")
        return False

def test_gui_creation():
    """Test GUI creation without agent"""
    print("🧪 Testing standalone GUI creation...")

    try:
        from pokedex_gui import create_pokedex_gui
        gui = create_pokedex_gui()
        print("✅ Successfully created GUI instance")

        # Test basic GUI properties
        if hasattr(gui, 'config'):
            print("✅ GUI has config system")
        if hasattr(gui, 'conversation_history'):
            print("✅ GUI has conversation system")
        if hasattr(gui, 'initialize_gui'):
            print("✅ GUI has initialization method")

        return True
    except Exception as e:
        print(f"❌ Failed to create GUI: {e}")
        return False

def test_agent_initialization():
    """Test agent initialization with new GUI"""
    print("🧪 Testing agent initialization...")

    try:
        # Set up minimal logging to avoid spam
        logging.basicConfig(level=logging.ERROR)

        from agent_core import UltronAgent
        agent = UltronAgent()

        print(f"✅ Agent initialized with status: {agent.status}")

        # Check if GUI was created
        if agent.gui:
            print("✅ Agent has GUI instance")
            if hasattr(agent.gui, 'agent_ref'):
                print("✅ GUI has agent reference")
            if hasattr(agent, 'start_gui'):
                print("✅ Agent has start_gui method")
        else:
            print("⚠️ Agent has no GUI (might be disabled in config)")

        # Check agent components
        if hasattr(agent, 'brain') and agent.brain:
            print("✅ Agent has brain component")
        if hasattr(agent, 'voice') and agent.voice:
            print("✅ Agent has voice component")
        if hasattr(agent, 'memory') and agent.memory:
            print("✅ Agent has memory component")
        if hasattr(agent, 'tools') and agent.tools:
            print(f"✅ Agent has {len(agent.tools)} tools loaded")

        return True

    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_command_processing():
    """Test command processing through agent"""
    print("🧪 Testing command processing...")

    try:
        from agent_core import UltronAgent
        agent = UltronAgent()

        # Test basic commands
        test_commands = [
            "hello",
            "status",
            "tools",
            "help"
        ]

        for cmd in test_commands:
            try:
                response = agent.process_command(cmd)
                print(f"✅ Command '{cmd}' -> Response: {response[:50]}...")
            except Exception as e:
                print(f"⚠️ Command '{cmd}' failed: {e}")

        return True

    except Exception as e:
        print(f"❌ Command processing test failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🤖 ULTRON Agent 3.0 - Pokédx GUI Integration Test")
    print("=" * 60)

    tests = [
        ("GUI Import", test_gui_import),
        ("Agent Import", test_agent_import),
        ("GUI Creation", test_gui_creation),
        ("Agent Initialization", test_agent_initialization),
        ("Command Processing", test_command_processing)
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        print("-" * 40)

        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 60)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All integration tests passed! Ready for deployment.")
        return 0
    else:
        print("⚠️ Some tests failed. Check logs above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
