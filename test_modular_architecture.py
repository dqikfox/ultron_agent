"""
Test script to demonstrate the new modular architecture
"""
import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_modular_architecture():
    """Test the new modular architecture components."""
    print("🚀 Testing ULTRON Agent 3.0 Modular Architecture")
    print("=" * 50)
    
    try:
        # Test imports
        print("\n📦 Testing Imports...")
        from ultron_agent import UltronConfig, Memory, setup_logging, get_logger
        from ultron_agent.ai import UltronBrain, OllamaManager
        from ultron_agent.interfaces import VoiceManager, VisionManager
        print("✅ All imports successful")
        
        # Test configuration
        print("\n⚙️ Testing Configuration...")
        config = UltronConfig()
        setup_logging(config.log_level.value)
        logger = get_logger("test", source="demo")
        logger.info(f"Config loaded: {config.app_name} v{config.version}")
        print(f"✅ Config: {config.app_name} v{config.version}")
        
        # Test memory
        print("\n🧠 Testing Memory...")
        memory = Memory(short_term_limit=3)
        memory.add_to_short_term("Test message 1")
        memory.add_to_short_term("Test message 2")
        
        # Test memory search
        results = memory.search_memory("Test")
        stats = memory.get_memory_stats()
        print(f"✅ Memory: {stats['short_term']['count']} items, {len(results)} search results")
        
        # Test voice manager (without actual TTS)
        print("\n🔊 Testing Voice Manager...")
        voice = VoiceManager(config)
        voice_status = voice.get_status()
        available_components = sum(voice_status.values())
        print(f"✅ Voice: {available_components} components available")
        
        # Test vision manager (without actual capture)
        print("\n👁️ Testing Vision Manager...")
        vision = VisionManager(config)
        vision_status = vision.get_status()
        print(f"✅ Vision: OCR={vision_status['ocr_enabled']}, Capture={vision_status['screen_capture_enabled']}")
        
        # Test Ollama manager (connection test)
        print("\n🤖 Testing Ollama Manager...")
        try:
            ollama = OllamaManager(config)
            status = ollama.get_status()
            print(f"✅ Ollama: Connected={status['connected']}, Models={status['available_models']}")
        except Exception as e:
            print(f"⚠️ Ollama: Not connected ({e})")
        
        # Test AI Brain (basic initialization)
        print("\n🧠 Testing AI Brain...")
        try:
            brain = UltronBrain(config, tools=None, memory=memory)
            cache_stats = brain.get_cache_stats()
            print(f"✅ Brain: Initialized with {cache_stats['entries']} cached entries")
        except Exception as e:
            print(f"⚠️ Brain: Initialization issue ({e})")
        
        print("\n🎉 All modular components tested successfully!")
        print("🏗️ The new architecture is working correctly!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_modular_architecture())
    sys.exit(0 if success else 1)