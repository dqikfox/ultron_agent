#!/usr/bin/env python3
"""
Quick test to verify ULTRON core components
"""
import sys
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("ULTRON Agent - Component Test")
print("=" * 60)

# Test 1: Configuration
print("\n[1/5] Testing configuration loading...")
try:
    from config import Config
    config = Config.from_file("ultron_config.json")
    print(f"✓ Config loaded: {config.llm_model}")
except Exception as e:
    print(f"✗ Config failed: {e}")

# Test 2: Security Utils
print("\n[2/5] Testing security utilities...")
try:
    from security_utils import sanitize_log_input, sanitize_html_output
    test = sanitize_log_input("test\ninput")
    print(f"✓ Security utils working")
except Exception as e:
    print(f"✗ Security utils failed: {e}")

# Test 3: Event System
print("\n[3/5] Testing event system...")
try:
    from utils.event_system import EventSystem
    events = EventSystem()
    print(f"✓ Event system initialized")
except Exception as e:
    print(f"✗ Event system failed: {e}")

# Test 4: Logging
print("\n[4/5] Testing logging system...")
try:
    from utils.ultron_logger import log_info, log_error
    log_info("test", "Component test running")
    print(f"✓ Logging system working")
except Exception as e:
    print(f"✗ Logging failed: {e}")

# Test 5: Ollama Connection
print("\n[5/5] Testing Ollama connection...")
try:
    import requests
    response = requests.get("http://localhost:11434/api/tags", timeout=2)
    if response.status_code == 200:
        print(f"✓ Ollama responding on port 11434")
    else:
        print(f"⚠ Ollama returned status {response.status_code}")
except Exception as e:
    print(f"✗ Ollama connection failed: {e}")

print("\n" + "=" * 60)
print("Component test complete!")
print("=" * 60)

# Provide diagnostic info
print("\nDiagnostic Information:")
print(f"Python: {sys.version}")
print(f"Platform: {sys.platform}")
print(f"Working directory: {Path.cwd()}")
print("\nNote: agent_core.py has syntax errors that need to be fixed")
print("Check logs/agent_core.log for details when running main.py")
