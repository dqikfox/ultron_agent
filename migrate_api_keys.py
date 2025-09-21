#!/usr/bin/env python3
"""
ULTRON Agent API Key Migration Script

This script helps migrate existing API keys from environment variables
or configuration files to the secure secrets manager.

Usage:
    python migrate_api_keys.py

Requirements:
    - Python 3.10+
    - utils/secrets_manager.py
    - ultron_agent/config.py
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main migration function."""
    print("🔐 ULTRON Agent API Key Migration Tool")
    print("=" * 50)

    try:
        # Import required modules
        from ultron_agent.config import migrate_api_keys_to_secrets_manager
        from utils.secrets_manager import SecretsManager

        print("✅ Imported required modules")

        # Check if secrets manager is available
        secrets_manager = SecretsManager()
        print("✅ Secrets manager initialized")

        # Run migration
        print("\n🔄 Starting API key migration...")
        results = migrate_api_keys_to_secrets_manager()

        if not results:
            print("❌ Migration failed - secrets manager not available")
            return 1

        # Report results
        print("\n📊 Migration Results:")
        print("-" * 30)

        success_count = 0
        for key_name, success in results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"{key_name}: {status}")
            if success:
                success_count += 1

        print(f"\n🎉 Migration completed: {success_count}/{len(results)} keys migrated successfully")

        if success_count > 0:
            print("\n🔒 Your API keys are now stored securely in the secrets manager.")
            print("💡 You can now safely remove API keys from environment variables if desired.")
            print("🔧 Use the secrets manager to manage your API keys going forward.")

        return 0 if success_count == len(results) else 1

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're running this from the project root directory")
        return 1
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        logger.exception("Migration error")
        return 1

if __name__ == "__main__":
    sys.exit(main())