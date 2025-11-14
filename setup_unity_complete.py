#!/usr/bin/env python3
"""Complete Unity setup with credentials"""

import json
import shutil
from pathlib import Path

def setup_unity():
    # Create .ultron directory
    config_dir = Path.home() / ".ultron"
    config_dir.mkdir(exist_ok=True)
    
    # Copy credentials to proper location
    source = Path("unity_credentials.json")
    dest = config_dir / "unity_config.json"
    
    if source.exists():
        shutil.copy(source, dest)
        print(f"[OK] Credentials copied to: {dest}")
    else:
        print("[ERROR] unity_credentials.json not found")
        return
    
    # Test authentication
    print("\n[TEST] Testing Unity authentication...")
    try:
        from tools.unity_hub_tool import UnityHubTool
        tool = UnityHubTool()
        result = tool.execute("unity auth test")
        print(result)
    except Exception as e:
        print(f"[WARNING] Test failed: {e}")
    
    print("\n" + "="*60)
    print("[SUCCESS] Unity Integration Setup Complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Start integration server: .\\start_unity_integration.bat")
    print("2. Create Unity project: python -c \"from tools.unity_hub_tool import UnityHubTool; print(UnityHubTool().execute('create unity project MyGame'))\"")
    print("3. Test connection: curl http://localhost:9000/unity/connect")

if __name__ == "__main__":
    setup_unity()
