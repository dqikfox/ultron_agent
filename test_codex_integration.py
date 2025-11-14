"""Test Codex integration with ULTRON Agent"""
import os
import sys

def test_environment():
    """Test environment setup"""
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"✅ OPENAI_API_KEY set (length: {len(api_key)})")
        return True
    else:
        print("❌ OPENAI_API_KEY not set")
        return False

def test_codex_config():
    """Test Codex config file"""
    config_path = os.path.expanduser("~/.codex/config.toml")
    if os.path.exists(config_path):
        print(f"✅ Codex config exists: {config_path}")
        with open(config_path, 'r') as f:
            content = f.read()
            if "gpt-4o-mini" in content:
                print("✅ Model configured: gpt-4o-mini")
            if "OPENAI_API_KEY" in content:
                print("✅ API key reference found")
        return True
    else:
        print(f"❌ Codex config not found: {config_path}")
        return False

def main():
    print("🧪 Testing Codex Integration\n")
    
    env_ok = test_environment()
    config_ok = test_codex_config()
    
    print("\n📊 Test Results:")
    print(f"Environment: {'✅ PASS' if env_ok else '❌ FAIL'}")
    print(f"Config: {'✅ PASS' if config_ok else '❌ FAIL'}")
    
    if env_ok and config_ok:
        print("\n✅ Codex integration ready!")
        print("Next: Restart VS Code and test Codex chat")
    else:
        print("\n❌ Setup incomplete")
        if not env_ok:
            print("Run: $env:OPENAI_API_KEY = 'your-key'")
        if not config_ok:
            print("Check ~/.codex/config.toml exists")

if __name__ == "__main__":
    main()
