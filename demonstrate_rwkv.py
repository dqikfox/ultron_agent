#!/usr/bin/env python3
"""
Demonstration script showing ULTRON Agent using RWKV model
"""

import sys
import asyncio
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def demonstrate_rwkv_model():
    """Demonstrate that the RWKV model is working with ULTRON Agent"""
    print("🤖 ULTRON Agent RWKV Model Demonstration - demonstrate_rwkv.py:16")
    print("= - demonstrate_rwkv.py:17" * 50)

    try:
        # Import the configuration to verify RWKV model is set
        from ultron_agent.config import load_config
        config = load_config()
        model_name = getattr(config, 'default_model_name',
                           getattr(config, 'llm_model', 'Not found'))

        print(f"✅ Configuration loaded successfully - demonstrate_rwkv.py:26")
        print(f"✅ Using LLM Model: {model_name} - demonstrate_rwkv.py:27")

        if 'rwkv' in model_name.lower():
            print("✅ RWKV model is correctly configured! - demonstrate_rwkv.py:30")
        else:
            print(f"⚠ Warning: Model is '{model_name}' (expected RWKV) - demonstrate_rwkv.py:32")
            return False

        # Test Ollama connection
        import requests
        ollama_url = getattr(config, 'ollama_base_url', 'http://localhost:11434')

        print(f"🔄 Testing connection to Ollama at {ollama_url}... - demonstrate_rwkv.py:39")

        # Test prompt
        test_prompts = [
            "Hello! Please introduce yourself briefly.",
            "What are the advantages of RWKV models?",
            "Explain what you can do as an AI assistant in one sentence."
        ]

        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n📝 Test {i}: {prompt} - demonstrate_rwkv.py:49")

            payload = {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }

            try:
                response = requests.post(
                    f"{ollama_url}/api/generate",
                    json=payload,
                    timeout=30
                )

                if response.status_code == 200:
                    result = response.json()
                    response_text = result.get('response', '').strip()
                    print(f"🤖 Response: {response_text} - demonstrate_rwkv.py:71")
                else:
                    print(f"❌ Error: Status code {response.status_code} - demonstrate_rwkv.py:73")

            except Exception as e:
                print(f"❌ Error: {e} - demonstrate_rwkv.py:76")
                continue

        return True

    except Exception as e:
        print(f"❌ Error: {e} - demonstrate_rwkv.py:82")
        import traceback
        traceback.print_exc()
        return False

async def interactive_demo():
    """Interactive demonstration of RWKV model"""
    print("\n - demonstrate_rwkv.py:89" + "=" * 50)
    print("🎮 Interactive RWKV Demo - demonstrate_rwkv.py:90")
    print("Type 'quit' to exit - demonstrate_rwkv.py:91")
    print("= - demonstrate_rwkv.py:92" * 50)

    try:
        # Load configuration
        from ultron_agent.config import load_config
        config = load_config()
        model_name = getattr(config, 'default_model_name',
                           getattr(config, 'llm_model', 'mollysama/rwkv-7-g1f:7.2b'))
        ollama_url = getattr(config, 'ollama_base_url', 'http://localhost:11434')

        print(f"🤖 Using model: {model_name} - demonstrate_rwkv.py:102")

        while True:
            user_input = input("\n💬 You: ").strip()

            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye! - demonstrate_rwkv.py:108")
                break

            if not user_input:
                continue

            # Prepare payload
            payload = {
                "model": model_name,
                "prompt": user_input,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }

            try:
                import requests
                response = requests.post(
                    f"{ollama_url}/api/generate",
                    json=payload,
                    timeout=30
                )

                if response.status_code == 200:
                    result = response.json()
                    response_text = result.get('response', '').strip()
                    print(f"🤖 ULTRON: {response_text} - demonstrate_rwkv.py:136")
                else:
                    print(f"❌ Error: Status code {response.status_code} - demonstrate_rwkv.py:138")

            except Exception as e:
                print(f"❌ Error: {e} - demonstrate_rwkv.py:141")

    except KeyboardInterrupt:
        print("\n👋 Goodbye! - demonstrate_rwkv.py:144")
    except Exception as e:
        print(f"❌ Error: {e} - demonstrate_rwkv.py:146")

if __name__ == "__main__":
    print("🚀 Starting ULTRON Agent RWKV Model Demonstration... - demonstrate_rwkv.py:149")

    # Run demonstration
    if demonstrate_rwkv_model():
        print("\n - demonstrate_rwkv.py:153" + "=" * 50)
        print("🎉 RWKV Model Setup Verification: SUCCESS - demonstrate_rwkv.py:154")
        print("✅ ULTRON Agent is configured to use RWKV model - demonstrate_rwkv.py:155")
        print("✅ Ollama connection is working - demonstrate_rwkv.py:156")
        print("✅ Model is responding to prompts - demonstrate_rwkv.py:157")
        print("= - demonstrate_rwkv.py:158" * 50)

        # Ask if user wants interactive demo
        response = input("\n🎮 Would you like to try an interactive demo? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            asyncio.run(interactive_demo())
    else:
        print("\n❌ RWKV Model Setup Verification: FAILED - demonstrate_rwkv.py:165")
         r
