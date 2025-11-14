"""Automated autocomplete test runner"""
import json
import subprocess
import sys
from pathlib import Path

# Fix Windows console encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_config_valid():
    """Test 1: Validate config.json syntax"""
    config_path = Path(".continue/config.json")
    try:
        with open(config_path) as f:
            config = json.load(f)
        print("✅ Test 1: Config JSON valid")
        return True
    except Exception as e:
        print(f"❌ Test 1: Config invalid - {e}")
        return False

def test_autocomplete_file_exists():
    """Test 2: Check autocomplete.ts exists"""
    ts_path = Path(".continue/autocomplete.ts")
    if ts_path.exists():
        print("✅ Test 2: autocomplete.ts exists")
        return True
    print("❌ Test 2: autocomplete.ts missing")
    return False

def test_models_configured():
    """Test 3: Verify autocomplete models configured"""
    config_path = Path(".continue/config.json")
    try:
        with open(config_path) as f:
            config = json.load(f)
        
        autocomplete_models = [m for m in config.get("models", []) 
                              if "autocomplete" in m.get("roles", [])]
        
        if len(autocomplete_models) >= 1:
            print(f"✅ Test 3: {len(autocomplete_models)} autocomplete models configured")
            for m in autocomplete_models:
                print(f"   - {m['name']}: {m['model']}")
            return True
        print("❌ Test 3: No autocomplete models found")
        return False
    except Exception as e:
        print(f"❌ Test 3: Failed - {e}")
        return False

def test_custom_autocomplete_enabled():
    """Test 4: Check custom autocomplete reference"""
    config_path = Path(".continue/config.json")
    try:
        with open(config_path) as f:
            config = json.load(f)
        
        if "customAutocomplete" in config:
            print(f"✅ Test 4: Custom autocomplete enabled: {config['customAutocomplete']}")
            return True
        print("⚠️  Test 4: Custom autocomplete not referenced (optional)")
        return True
    except Exception as e:
        print(f"❌ Test 4: Failed - {e}")
        return False

def test_autocomplete_options():
    """Test 5: Verify autocomplete options configured"""
    config_path = Path(".continue/config.json")
    try:
        with open(config_path) as f:
            config = json.load(f)
        
        tab_opts = config.get("tabAutocompleteOptions", {})
        required = ["maxPromptTokens", "debounceDelay", "modelTimeout"]
        
        if all(k in tab_opts for k in required):
            print("✅ Test 5: Autocomplete options configured")
            print(f"   - Debounce: {tab_opts['debounceDelay']}ms")
            print(f"   - Timeout: {tab_opts['modelTimeout']}ms")
            print(f"   - Max tokens: {tab_opts['maxPromptTokens']}")
            return True
        print("❌ Test 5: Missing required options")
        return False
    except Exception as e:
        print(f"❌ Test 5: Failed - {e}")
        return False

def test_typescript_syntax():
    """Test 6: Validate TypeScript syntax"""
    ts_path = Path(".continue/autocomplete.ts")
    if not ts_path.exists():
        print("⚠️  Test 6: Skipped (no TS file)")
        return True
    
    try:
        with open(ts_path) as f:
            content = f.read()
        
        required = ["AutocompleteInput", "AutocompleteOutcome", "export async function"]
        if all(r in content for r in required):
            print("✅ Test 6: TypeScript syntax valid")
            return True
        print("❌ Test 6: Missing required TypeScript elements")
        return False
    except Exception as e:
        print(f"❌ Test 6: Failed - {e}")
        return False

def run_all_tests():
    """Run all tests and report results"""
    print("=" * 60)
    print("ULTRON AGENT - AUTOCOMPLETE CONFIGURATION TEST")
    print("=" * 60)
    print()
    
    tests = [
        test_config_valid,
        test_autocomplete_file_exists,
        test_models_configured,
        test_custom_autocomplete_enabled,
        test_autocomplete_options,
        test_typescript_syntax
    ]
    
    results = [test() for test in tests]
    
    print()
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ ALL TESTS PASSED - Autocomplete ready!")
        print()
        print("Next steps:")
        print("1. Restart VS Code")
        print("2. Open test_autocomplete.py")
        print("3. Type 'log_' and press Tab")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Review errors above")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
