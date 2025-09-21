#!/usr/bin/env python3
"""
Test script for configuration schema validation.
This demonstrates the new validation system in action.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config, ValidationSeverity


def test_config_validation():
    """Test the configuration validation system."""
    print("🔍 Testing ULTRON Configuration Schema Validation")
    print("=" * 60)

    try:
        # Load configuration
        config = Config()
        print("✅ Configuration loaded successfully")

        # Validate configuration
        issues = config.validate()
        print(f"📊 Found {len(issues)} validation issues")

        # Get validation summary
        summary = config.get_validation_summary()
        print("📈 Validation Summary:")
        print(f"   Errors: {summary['errors']}")
        print(f"   Warnings: {summary['warnings']}")
        print(f"   Info: {summary['info']}")
        print(f"   Total: {summary['total']}")

        # Check if configuration is valid
        is_valid = config.is_valid()
        print(f"✅ Configuration is {'valid' if is_valid else 'invalid'}")

        # Display issues by severity
        if issues:
            print("\n📋 Detailed Issues:")
            for issue in issues:
                severity_icon = {
                    ValidationSeverity.ERROR: "❌",
                    ValidationSeverity.WARNING: "⚠️",
                    ValidationSeverity.INFO: "ℹ️"
                }.get(issue.severity, "?")
                severity_str = issue.severity.value
                print(f"   {severity_icon} [{severity_str}] {issue.field}: "
                      f"{issue.message}")
                if issue.suggestion:
                    print(f"      💡 Suggestion: {issue.suggestion}")

        # Test specific configuration values
        print("\n🔧 Configuration Values Check:")
        print(f"   Voice Engine: {config.get('voice_engine', 'N/A')}")
        print(f"   LLM Model: {config.get('llm_model', 'N/A')}")
        print(f"   GUI Theme: {config.get('gui_theme', 'N/A')}")
        print(f"   Debug Mode: {config.get('debug', 'N/A')}")

        return True

    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_config_validation()
    sys.exit(0 if success else 1)
