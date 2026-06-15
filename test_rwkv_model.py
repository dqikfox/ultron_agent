#!/usr/bin/env python3
"""
Test script to verify RWKV model configuration with ULTRON Agent
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_rwkv_model():
    """Test that the RWKV model is properly configured"""
    try:
        # Import configuration
        from agent_core import UltronAgent

        # Create agent instance to test config loading
        agent = UltronAgent()
        config = agent.config

        # Check if the model is set correctly
        # Try different ways to access the model name
        model_name = getattr(config, 'default_model_name',
                           getattr(config, 'llm_model',
                                 config.__dict__.get('llm_model', 'Not set')))
        ollama_url = getattr(config, 'ollama_base_url',
                           config.__dict__.get('ollama_base_url', 'Not set'))

        print(f"✓ Configuration loaded successfully")
        print(f"✓ LLM Model: {model_name}")
        print(f"✓ Ollama URL: {ollama_url}")

        if 'rwkv' in model_name.lower():
            print("✓ RWKV model is correctly configured!")
            return True
        else:
            print(f"⚠ Warning: Model is not RWKV but '{model_name}'")
            return False

    except Exception as e:
        print(f"❌ Error testing RWKV model: {e}")
        return False

def test_ollama_connection():
    """Test connection to Ollama with RWKV model"""
    try:
        import requests

        # Load config to get model name and URL
        from agent_core import UltronAgent
        agent = UltronAgent()
        config = agent.config
        model_name = config.get('llm_model', 'mollysama/rwkv-7-g1f:7.2b')
        ollama_url = config.get('ollama_base_url', 'http://localhost:11434')

        # Test the model
        test_prompt = "Hello, this is a test. Please respond with a short greeting."
        payload = {
            "model": model_name,
            "prompt": test_prompt,
            "stream": False
        }

        print(f"✓ Testing connection to Ollama at {ollama_url}")
        response = requests.post(f"{ollama_url}/api/generate", json=payload, timeout=30)

        if response.status_code == 200:
            result = response.json()
            response_text = result.get('response', '')
            print(f"✓ Ollama connection successful!")
            print(f"✓ Model response: {response_text[:100]}...")
            return True
        else:
            print(f"❌ Ollama returned status code: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error testing Ollama connection: {e}")
        return False

if __name__ == "__main__":
    print("Testing RWKV model configuration with ULTRON Agent...")
    print("=" * 50)

    # Test configuration
    config_ok = test_rwkv_model()
    print()

    # Test Ollama connection
    connection_ok = test_ollama_connection()
    print()

    if config_ok and connection_ok:
        print("🎉 All tests passed! RWKV model is ready to use with ULTRON Agent.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please check the configuration.")
        sys.exit(1)
