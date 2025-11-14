#!/usr/bin/env python3
"""AWS Integration Setup Script for ULTRON Agent - One-Command Installation"""

import os
import sys
import subprocess
import json
from pathlib import Path


class AWSSetupWizard:
    """Interactive AWS setup wizard for ULTRON Agent"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.config_file = self.project_root / "ultron_config.json"
        self.aws_region = "us-east-1"
        self.setup_complete = False

    def run(self):
        """Run the complete AWS setup wizard"""
        print("\n" + "=" * 80)
        print("🚀 ULTRON Agent - AWS Integration Setup Wizard")
        print("=" * 80 + "\n")

        try:
            self._check_prerequisites()
            self._collect_aws_credentials()
            self._verify_aws_connection()
            self._update_config()
            self._display_next_steps()
            self.setup_complete = True
            print("\n✅ AWS Setup Complete!")
            print("=" * 80 + "\n")
        except KeyboardInterrupt:
            print("\n\n❌ Setup cancelled by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Setup failed: {e}")
            sys.exit(1)

    def _check_prerequisites(self):
        """Check if prerequisites are installed"""
        print("📋 Checking prerequisites...\n")

        # Check AWS CLI
        try:
            result = subprocess.run(
                ["aws", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            print(f"  ✅ AWS CLI: {result.stdout.strip()}")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("  ❌ AWS CLI not found")
            print("\n     Install from: https://aws.amazon.com/cli/")
            print("     Or: choco install awscli (Windows)")
            sys.exit(1)

        # Check Python version
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        if sys.version_info < (3, 10):
            print(f"  ❌ Python {python_version} (requires 3.10+)")
            sys.exit(1)
        print(f"  ✅ Python: {python_version}")

        # Check boto3
        try:
            import boto3  # noqa: F401
            print("  ✅ boto3: installed")
        except ImportError:
            print("  ❌ boto3 not installed")
            print("     Run: pip install boto3")
            sys.exit(1)

        print()

    def _collect_aws_credentials(self):
        """Collect AWS credentials from user"""
        print("🔐 AWS Credentials Setup\n")

        # Ask for credential setup method
        print("Choose credential setup method:")
        print("  1. AWS CLI (aws configure)")
        print("  2. Manual environment variables")
        print("  3. Skip (use existing credentials)")
        choice = input("\nChoice (1-3): ").strip()

        if choice == "1":
            print("\nRunning: aws configure")
            subprocess.run(["aws", "configure"], check=False)
        elif choice == "2":
            self._setup_env_vars()
        elif choice == "3":
            print("Skipping credential setup...")
        else:
            print("Invalid choice")
            self._collect_aws_credentials()

        print()

    def _setup_env_vars(self):
        """Setup environment variables"""
        print("\nEnter AWS credentials:")
        access_key = input("AWS Access Key ID (AKIA...): ").strip()
        secret_key = input("AWS Secret Access Key: ").strip()

        if not access_key or not secret_key:
            print("❌ Credentials cannot be empty")
            self._setup_env_vars()
            return

        os.environ["AWS_ACCESS_KEY_ID"] = access_key
        os.environ["AWS_SECRET_ACCESS_KEY"] = secret_key
        os.environ["AWS_DEFAULT_REGION"] = self.aws_region

        print(f"\n✅ Environment variables set")
        print(f"   AWS_DEFAULT_REGION: {self.aws_region}")

    def _verify_aws_connection(self):
        """Verify AWS connection works"""
        print("🔍 Verifying AWS Connection\n")

        try:
            result = subprocess.run(
                ["aws", "sts", "get-caller-identity"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                identity = json.loads(result.stdout)
                print(f"  ✅ Connected to AWS")
                print(f"     Account: {identity.get('Account')}")
                print(f"     User: {identity.get('Arn')}")
            else:
                print(f"  ❌ AWS connection failed:")
                print(f"     {result.stderr}")
                sys.exit(1)

        except Exception as e:
            print(f"  ❌ Error verifying AWS: {e}")
            sys.exit(1)

        # Check Bedrock access
        try:
            result = subprocess.run(
                ["aws", "bedrock-runtime", "list-foundation-models"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                print(f"  ✅ AWS Bedrock accessible")
            else:
                print(f"  ⚠️  AWS Bedrock not accessible")
                print(f"     (This is OK if Bedrock not in your region)")

        except Exception as e:
            print(f"  ⚠️  Could not verify Bedrock: {e}")

        print()

    def _update_config(self):
        """Update ultron_config.json with AWS section"""
        print("⚙️  Updating Configuration\n")

        try:
            # Read existing config
            if self.config_file.exists():
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                print(f"  ✅ Read {self.config_file}")
            else:
                config = {}
                print(f"  📝 Creating new {self.config_file}")

            # Add AWS section
            config["aws_config"] = {
                "enabled": True,
                "region": self.aws_region,
                "bedrock_enabled": True,
                "use_secrets_manager": False,
                "credentials_source": "environment"
            }

            config["services"] = config.get("services", {})
            config["services"]["bedrock_fallback"] = True

            # Write updated config
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)
            print(f"  ✅ Updated {self.config_file}")

        except Exception as e:
            print(f"  ❌ Error updating config: {e}")
            sys.exit(1)

        print()

    def _display_next_steps(self):
        """Display next steps for user"""
        print("📋 Next Steps\n")

        print("1️⃣  Deploy AWS Config (Optional but Recommended):")
        print("     aws cloudformation create-stack \\")
        print("       --stack-name ultron-config \\")
        print("       --template-body file://EnableAWSConfig.yml \\")
        print("       --parameters ParameterKey=AllSupported,ParameterValue=True")
        print()

        print("2️⃣  Verify Setup:")
        print("     aws sts get-caller-identity")
        print("     aws bedrock-runtime list-foundation-models")
        print()

        print("3️⃣  Start ULTRON:")
        print("     python main.py")
        print()

        print("4️⃣  Use AWS Services:")
        print("     /delegate \"Analyze code using AWS Bedrock\"")
        print("     /delegate \"Check AWS Config compliance\"")
        print()

        print("📚 Learn More:")
        print("     Read: AWS_QUICKSTART.md (10 minutes)")
        print("     Read: AWS_CONFIG_SETUP_GUIDE.md (30 minutes)")
        print("     Read: AWS_INTEGRATION_INDEX.md (Reference)")
        print()


def main():
    """Main entry point"""
    wizard = AWSSetupWizard()
    wizard.run()


if __name__ == "__main__":
    main()
