#!/usr/bin/env python3
"""Quick Unity configuration script with your project IDs"""

import json
from pathlib import Path

def configure_unity():
    """Configure Unity integration with project IDs"""
    config_dir = Path.home() / ".ultron"
    config_dir.mkdir(exist_ok=True)
    
    config = {
        "unity_project_id": "09462e87-758e-430c-a9d9-90b334206984",
        "unity_environment_id": "036d7a54-d699-4eb5-b932-c78726974310",
        "unity_bucket_id": "62a96ca6-4710-4328-8b9d-d2bb3d935b9f",
        "unity_release_id": "cdc6a861-8e2f-48c1-8cf7-13a1968b3a68",
        "unity_key_id": "YOUR_KEY_ID_HERE",
        "unity_secret_key": "YOUR_SECRET_KEY_HERE",
        "unity_organization_id": "YOUR_ORG_ID_HERE",
        "config_api_url": "https://services.api.unity.com/remote-config/v1"
    }
    
    config_file = config_dir / "unity_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print("=" * 60)
    print("✅ Unity Configuration Created")
    print("=" * 60)
    print(f"\nConfig file: {config_file}")
    print("\n📋 Your Project IDs (Already Configured):")
    print(f"   Project ID:     {config['unity_project_id']}")
    print(f"   Environment ID: {config['unity_environment_id']}")
    print(f"   Bucket ID:      {config['unity_bucket_id']}")
    print(f"   Release ID:     {config['unity_release_id']}")
    
    print("\n⚠️ REQUIRED: Get Service Account Credentials")
    print("=" * 60)
    print("\n1. Go to Unity Dashboard:")
    print("   https://dashboard.unity3d.com/")
    
    print("\n2. Select your project:")
    print("   09462e87-758e-430c-a9d9-90b334206984")
    
    print("\n3. Navigate to:")
    print("   Project Settings → Service Accounts")
    
    print("\n4. Create new Service Account:")
    print("   • Name: ULTRON Agent")
    print("   • Permissions: Remote Config (Read/Write)")
    
    print("\n5. Copy credentials and edit config file:")
    print(f"   {config_file}")
    
    print("\n   Replace:")
    print("   • YOUR_KEY_ID_HERE → Service Account Key ID")
    print("   • YOUR_SECRET_KEY_HERE → Service Account Secret Key")
    print("   • YOUR_ORG_ID_HERE → Organization ID")
    
    print("\n6. Test authentication:")
    print("   python -c \"from tools.unity_hub_tool import UnityHubTool; print(UnityHubTool().execute('unity auth test'))\"")
    
    print("\n" + "=" * 60)
    print("Next Steps:")
    print("=" * 60)
    print("1. Get credentials from Unity Dashboard")
    print("2. Edit config file with real credentials")
    print("3. Test authentication")
    print("4. Start Unity integration server")
    print("5. Create/setup Unity project")
    print("\nEstimated time: 30-45 minutes")
    print("=" * 60)

if __name__ == "__main__":
    configure_unity()
