"""
ULTRON Agent - MCP Connection Diagnostic Tool

This script helps diagnose MCP (Model Context Protocol) connection issues
and provides recommendations for resolving server connectivity problems.

Usage: python mcp_diagnostic.py
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any


class MCPDiagnosticTool:
    """Diagnostic tool for MCP connection issues"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.issues_found = []
        self.recommendations = []

    def run_diagnostics(self) -> Dict[str, Any]:
        """Run comprehensive diagnostics"""
        print("🔍 ULTRON Agent - MCP Connection Diagnostics")
        print("=" * 60)

        results = {
            "server_status": self.check_server_status(),
            "npm_status": self.check_npm_status(),
            "vscode_config": self.check_vscode_config(),
            "network_connectivity": self.check_network_connectivity(),
            "extension_conflicts": self.check_extension_conflicts(),
            "issues_found": self.issues_found,
            "recommendations": self.recommendations
        }

        return results

    def check_server_status(self) -> Dict[str, Any]:
        """Check status of running servers"""
        print("\n📡 Checking server status...")

        servers_to_check = {
            "Langflow": 7861,
            "Web GUI": 8080,
            "Ollama": 11434,
            "API Server": 5000
        }

        server_status = {}

        for name, port in servers_to_check.items():
            try:
                # Use netstat to check if port is listening
                result = subprocess.run(
                    ["netstat", "-ano"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if (f":{port} " in result.stdout and
                        "LISTENING" in result.stdout):
                    server_status[name] = "RUNNING"
                    print(f"  ✅ {name} server is running on port {port}")
                else:
                    server_status[name] = "NOT_RUNNING"
                    print(f"  ❌ {name} server is NOT running on port {port}")
                    self.issues_found.append(
                        f"{name} server not running on port {port}")
                    self.recommendations.append(
                        f"Start {name} server on port {port}")

            except Exception as e:
                server_status[name] = "ERROR"
                print(f"  ⚠️  Error checking {name} server: {str(e)}")
                self.issues_found.append(
                    f"Error checking {name} server: {str(e)}")

        return server_status

    def check_npm_status(self) -> Dict[str, Any]:
        """Check npm configuration and package status"""
        print("\n📦 Checking npm status...")

        npm_status = {}

        try:
            # Check npm version
            result = subprocess.run(
                ["npm", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                npm_status["version"] = result.stdout.strip()
                print(f"  ✅ npm version: {npm_status['version']}")
            else:
                npm_status["version"] = "ERROR"
                print(f"  ❌ npm version check failed: {result.stderr}")
                self.issues_found.append("npm version check failed")
                self.recommendations.append("Install or repair npm")

        except FileNotFoundError:
            npm_status["version"] = "NOT_INSTALLED"
            print("  ❌ npm is not installed")
            self.issues_found.append("npm is not installed")
            self.recommendations.append("Install Node.js and npm")

        except Exception as e:
            npm_status["version"] = "ERROR"
            print(f"  ⚠️  Error checking npm: {str(e)}")
            self.issues_found.append(f"npm error: {str(e)}")

        # Check for package-lock.json issues
        package_lock = self.project_root / "package-lock.json"
        if package_lock.exists():
            try:
                with open(package_lock, 'r', encoding='utf-8') as f:
                    json.load(f)  # Validate JSON structure

                npm_status["package_lock"] = "VALID"
                print("  ✅ package-lock.json is valid")

            except json.JSONDecodeError as e:
                npm_status["package_lock"] = "INVALID"
                print(f"  ❌ package-lock.json is corrupted: {str(e)}")
                self.issues_found.append("package-lock.json is corrupted")
                self.recommendations.append(
                    "Delete package-lock.json and node_modules, "
                    "then run npm install")

        return npm_status

    def check_vscode_config(self) -> Dict[str, Any]:
        """Check VS Code configuration for MCP-related settings"""
        print("\n⚙️  Checking VS Code configuration...")

        vscode_config = {}

        # Check workspace settings
        workspace_file = self.project_root / "ultron-agent.code-workspace"
        if workspace_file.exists():
            try:
                with open(workspace_file, 'r', encoding='utf-8') as f:
                    workspace_data = json.load(f)

                vscode_config["workspace"] = "VALID"
                print("  ✅ VS Code workspace configuration is valid")

                # Check for any MCP-related settings
                settings = workspace_data.get("settings", {})
                mcp_settings = {
                    key: value for key, value in settings.items()
                    if "mcp" in key.lower()
                }

                if mcp_settings:
                    vscode_config["mcp_settings"] = mcp_settings
                    print(f"  ℹ️  Found MCP-related settings: "
                          f"{list(mcp_settings.keys())}")
                else:
                    print("  ℹ️  No MCP-related settings found in workspace")

            except json.JSONDecodeError as e:
                vscode_config["workspace"] = "INVALID"
                print(f"  ❌ VS Code workspace configuration is "
                      f"invalid: {str(e)}")
                self.issues_found.append(
                    "VS Code workspace configuration is invalid")
                self.recommendations.append(
                    "Fix or recreate ultron-agent.code-workspace file")

        # Check .vscode/settings.json
        vscode_dir = self.project_root / ".vscode"
        settings_file = vscode_dir / "settings.json"

        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    json.load(f)  # Validate JSON structure

                vscode_config["settings"] = "VALID"
                print("  ✅ VS Code settings.json is valid")

            except json.JSONDecodeError as e:
                vscode_config["settings"] = "INVALID"
                print(f"  ❌ VS Code settings.json is invalid: {str(e)}")
                self.issues_found.append("VS Code settings.json is invalid")
                self.recommendations.append(
                    "Fix or recreate .vscode/settings.json file")

        return vscode_config

    def check_network_connectivity(self) -> Dict[str, Any]:
        """Check network connectivity to required services"""
        print("\n🌐 Checking network connectivity...")

        network_status = {}

        # Test localhost connectivity
        test_ports = [7861, 8080, 11434, 5000]

        for port in test_ports:
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', port))
                sock.close()

                if result == 0:
                    network_status[f"localhost:{port}"] = "CONNECTED"
                    print(f"  ✅ localhost:{port} is accessible")
                else:
                    network_status[f"localhost:{port}"] = "NOT_CONNECTED"
                    print(f"  ❌ localhost:{port} is not accessible")
                    self.issues_found.append(
                        f"Cannot connect to localhost:{port}")
                    self.recommendations.append(
                        f"Ensure service is running on port {port}")

            except Exception as e:
                network_status[f"localhost:{port}"] = "ERROR"
                print(f"  ⚠️  Error testing localhost:{port}: {str(e)}")

        return network_status

    def check_extension_conflicts(self) -> Dict[str, Any]:
        """Check for potential extension conflicts"""
        print("\n🔌 Checking for extension conflicts...")

        extension_status = {}

        # Check for conflicting AI extensions
        workspace_file = self.project_root / "ultron-agent.code-workspace"

        if workspace_file.exists():
            try:
                with open(workspace_file, 'r', encoding='utf-8') as f:
                    workspace_data = json.load(f)

                extensions = workspace_data.get("extensions", {})
                recommendations = extensions.get("recommendations", [])

                # Check for multiple AI assistants
                ai_extensions = [
                    ext for ext in recommendations
                    if any(keyword in ext.lower() for keyword in [
                        "copilot", "amazon", "q", "continue", "tabnine", "kite"
                    ])
                ]

                if len(ai_extensions) > 1:
                    extension_status["multiple_ai"] = ai_extensions
                    print(f"  ⚠️  Multiple AI extensions detected: "
                          f"{ai_extensions}")
                    print("    This may cause conflicts. Consider disabling "
                          "all but one.")
                    self.issues_found.append(
                        f"Multiple AI extensions: {ai_extensions}")
                    self.recommendations.append(
                        "Disable conflicting AI extensions, "
                        "keep only GitHub Copilot")

                else:
                    extension_status["ai_extensions"] = ai_extensions
                    print(f"  ✅ AI extensions: {ai_extensions}")

            except Exception as e:
                print(f"  ⚠️  Error checking extensions: {str(e)}")

        return extension_status

    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate diagnostic report"""
        report = []
        report.append("🔍 ULTRON Agent - MCP Connection Diagnostic Report")
        report.append("=" * 60)
        report.append("")

        # Issues found
        if self.issues_found:
            report.append("🚨 ISSUES FOUND:")
            for i, issue in enumerate(self.issues_found, 1):
                report.append(f"  {i}. {issue}")
            report.append("")
        else:
            report.append("✅ NO ISSUES FOUND")
            report.append("")

        # Recommendations
        if self.recommendations:
            report.append("💡 RECOMMENDATIONS:")
            for i, rec in enumerate(self.recommendations, 1):
                report.append(f"  {i}. {rec}")
            report.append("")

        # Server status
        report.append("📡 SERVER STATUS:")
        for server, status in results["server_status"].items():
            status_icon = "✅" if status == "RUNNING" else "❌"
            report.append(f"  {status_icon} {server}: {status}")
        report.append("")

        # Quick fixes
        report.append("🔧 QUICK FIXES:")
        report.append("  1. Restart VS Code")
        report.append("  2. Check if required servers are running:")
        report.append("     - python main.py (for ULTRON Agent)")
        report.append("     - ollama serve (for Ollama)")
        report.append("     - Start Langflow server if needed")
        report.append("  3. Clear npm cache: npm cache clean --force")
        report.append("  4. Reinstall node modules: rm -rf node_modules && "
                      "npm install")
        report.append("  5. Check VS Code extensions for conflicts")

        return "\n".join(report)


def main():
    """Main diagnostic function"""
    diagnostic_tool = MCPDiagnosticTool()

    try:
        results = diagnostic_tool.run_diagnostics()
        report = diagnostic_tool.generate_report(results)

        print("\n" + report)

        # Save report to file
        report_file = (diagnostic_tool.project_root /
                       "mcp_diagnostic_report.txt")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n📄 Report saved to: {report_file}")

        # Exit with appropriate code
        if diagnostic_tool.issues_found:
            print("\n⚠️  Issues found. Please review the "
                  "recommendations above.")
            sys.exit(1)
        else:
            print("\n✅ All diagnostics passed!")
            sys.exit(0)

    except Exception as e:
        print(f"\n❌ Diagnostic failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
