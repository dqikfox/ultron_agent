#!/usr/bin/env python3
"""
Test script to verify configuration loading
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_config_loading():
    """Test that the configuration loads correctly"""
    try:
        # Try to import the config module directly
        from ultron_agent.config import load_config, UltronConfig

        print("✓ Successfully imported ultron_agent.config")

        # Load configuration
        config = load_config()
        print("✓ Configuration loaded successfully")

        # Check the model name
        model_name = getattr(config, 'default_model_name', getattr(config, 'llm_model', 'Not found'))
        print(f"✓ LLM Model: {model_name}")

        # Check Ollama URL
        ollama_url = getattr(config, 'ollama_base_url', 'Not found')
        print(f"✓ Ollama URL: {ollama_url}")

        if 'rwkv' in str(model_name).lower():
            print("✓ RWKV model is correctly configured!")
            return True
        else:
            print(f"⚠ Warning: Model is '{model_name}' (not RWKV)")
            return False

    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing configuration loading...")
    print("=" * 40)

    success = test_config_loading()

    if success:
        print("\n🎉 Configuration test passed!")
        sys.exit(0)
    else:
        print("\n❌ Configuration test failed!")
        sys.exit(1)
