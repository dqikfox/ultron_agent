#!/usr/bin/env python3
"""
UltronSysAgent Demo Script
Demonstrates core functionality without full GUI
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def demo_event_system():
    """Demonstrate the event bus system"""
    print("🔄 Demonstrating Event System...")
    
    from src.core.event_bus import EventBus, EventTypes
    
    event_bus = EventBus()
    
    # Create a simple event handler
    async def demo_handler(event):
        print(f"  📨 Received event: {event.type} from {event.source}")
        print(f"  📄 Data: {event.data}")
    
    # Subscribe to events
    event_bus.subscribe("demo_event", demo_handler)
    
    # Publish an event
    await event_bus.publish("demo_event", {"message": "Hello from event bus!"}, source="demo")
    
    # Process events
    await event_bus.process_events()
    
    print("  ✅ Event system working\n")

async def demo_config_system():
    """Demonstrate configuration management"""
    print("⚙️ Demonstrating Configuration System...")
    
    from src.core.config import ConfigManager
    
    config = ConfigManager()
    config.load()
    
    # Show some config values
    print(f"  🔧 Admin mode: {config.get('system.admin_mode')}")
    print(f"  🔧 Voice enabled: {config.get('voice.always_listening')}")
    print(f"  🔧 Primary AI model: {config.get('ai.primary_model')}")
    print(f"  🔧 Offline mode: {config.is_offline_mode()}")
    
    print("  ✅ Configuration system working\n")

async def demo_memory_system():
    """Demonstrate memory management"""
    print("🧠 Demonstrating Memory System...")
    
    try:
        from src.core.event_bus import EventBus
        from src.core.config import ConfigManager
        from src.modules.memory_manager.memory_manager import MemoryManager
        
        config = ConfigManager()
        config.load()
        event_bus = EventBus()
        
        memory = MemoryManager(config, event_bus)
        await memory.start()
        
        # Store some test interactions
        await memory.store_interaction(
            "What is the weather like?", 
            "I don't have access to weather data right now, but I can help you with other tasks.",
            model_used="demo"
        )
        
        await memory.store_interaction(
            "Tell me about Python",
            "Python is a high-level programming language known for its simplicity and readability.",
            model_used="demo"
        )
        
        # Test context retrieval
        context = await memory.get_relevant_context("programming", limit=1)
        
        print(f"  🔍 Retrieved context: {context[:100]}..." if context else "  🔍 No context found")
        
        await memory.stop()
        print("  ✅ Memory system working\n")
        
    except Exception as e:
        print(f"  ⚠️ Memory system demo failed: {e}\n")

async def demo_file_manager():
    """Demonstrate file management"""
    print("📁 Demonstrating File Manager...")
    
    try:
        from src.core.event_bus import EventBus
        from src.core.config import ConfigManager
        from src.modules.file_manager.file_manager import FileManager
        
        config = ConfigManager()
        config.load()
        event_bus = EventBus()
        
        file_manager = FileManager(config, event_bus)
        await file_manager.start()
        
        # Create a test file
        test_content = "# UltronSysAgent Demo\n\nThis is a test file created by the demo script.\n\n- Feature 1\n- Feature 2\n- Feature 3"
        
        result = await file_manager.create_file("data/demo_test.md", test_content)
        
        if result['success']:
            print(f"  📝 Created test file: {result['path']}")
            
            # Process the file
            process_result = await file_manager.process_file("data/demo_test.md")
            
            if process_result['success']:
                content_preview = process_result['content'][:100]
                print(f"  📖 File content preview: {content_preview}...")
            else:
                print(f"  ⚠️ File processing failed: {process_result.get('error')}")
        else:
            print(f"  ⚠️ File creation failed: {result.get('error')}")
        
        await file_manager.stop()
        print("  ✅ File manager working\n")
        
    except Exception as e:
        print(f"  ⚠️ File manager demo failed: {e}\n")

async def demo_scheduler():
    """Demonstrate task scheduler"""
    print("⏰ Demonstrating Scheduler...")
    
    try:
        from src.core.event_bus import EventBus
        from src.core.config import ConfigManager
        from src.modules.scheduler.scheduler import Scheduler
        
        config = ConfigManager()
        config.load()
        event_bus = EventBus()
        
        scheduler = Scheduler(config, event_bus)
        await scheduler.start()
        
        # Create a test task
        task_id = await scheduler.create_task(
            name="Demo Task",
            description="A demonstration scheduled task",
            command="echo Demo task executed!",
            schedule_type="interval",
            schedule_data={"interval_seconds": 3600},  # Every hour
            max_runs=1
        )
        
        print(f"  📅 Created task: {task_id}")
        
        # Get task status
        tasks = scheduler.get_tasks()
        print(f"  📊 Total tasks: {len(tasks)}")
        
        status = scheduler.get_status()
        print(f"  🔄 Scheduler status: {status['running']}")
        
        await scheduler.stop()
        print("  ✅ Scheduler working\n")
        
    except Exception as e:
        print(f"  ⚠️ Scheduler demo failed: {e}\n")

async def demo_plugin_system():
    """Demonstrate plugin system"""
    print("🔌 Demonstrating Plugin System...")
    
    try:
        # Import the example plugin
        sys.path.insert(0, str(project_root / "plugins"))
        import example_plugin
        
        from src.core.event_bus import EventBus
        from src.core.config import ConfigManager
        
        config = ConfigManager()
        config.load()
        event_bus = EventBus()
        
        # Create plugin instance
        plugin = example_plugin.ExamplePlugin(config, event_bus)
        
        # Get plugin info
        info = plugin.get_info()
        print(f"  🔌 Plugin: {info['name']} v{info['version']}")
        print(f"  📝 Description: {info['description']}")
        print(f"  ⚡ Capabilities: {', '.join(info['capabilities'])}")
        
        # Start plugin
        await plugin.start()
        
        # Test plugin command
        await plugin._process_plugin_command("test", "demo")
        
        await plugin.stop()
        print("  ✅ Plugin system working\n")
        
    except Exception as e:
        print(f"  ⚠️ Plugin system demo failed: {e}\n")

async def demo_ai_brain():
    """Demonstrate AI brain (without API calls)"""
    print("🧠 Demonstrating AI Brain...")
    
    try:
        from src.core.event_bus import EventBus
        from src.core.config import ConfigManager
        from src.modules.memory_manager.memory_manager import MemoryManager
        from src.modules.ai_brain.ai_brain import AIBrain
        
        config = ConfigManager()
        config.load()
        
        # Force offline mode for demo
        config.set('api.offline_mode', True)
        
        event_bus = EventBus()
        
        memory = MemoryManager(config, event_bus)
        await memory.start()
        
        ai_brain = AIBrain(config, event_bus, memory)
        await ai_brain.start()
        
        # Show AI brain status
        status = ai_brain.get_status()
        print(f"  🤖 Current model: {status['current_model']}")
        print(f"  💭 Memory enabled: {status['memory_enabled']}")
        print(f"  📡 Offline mode: {status['offline_mode']}")
        print(f"  📚 Conversation length: {status['conversation_length']}")
        
        await ai_brain.stop()
        await memory.stop()
        print("  ✅ AI brain initialized\n")
        
    except Exception as e:
        print(f"  ⚠️ AI brain demo failed: {e}\n")

async def main():
    """Main demo function"""
    print("🤖 UltronSysAgent Core Functionality Demo")
    print("=" * 50)
    print("This demo shows core components working without GUI or external APIs.\n")
    
    # Run all demos
    await demo_event_system()
    await demo_config_system()
    await demo_memory_system()
    await demo_file_manager()
    await demo_scheduler()
    await demo_plugin_system()
    await demo_ai_brain()
    
    print("🎉 Demo completed!")
    print("\nTo start the full UltronSysAgent with GUI:")
    print("  python main.py")
    print("\nTo run installation tests:")
    print("  python scripts/test_installation.py")
    print("\nFor setup and configuration:")
    print("  python scripts/setup_windows.py")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
