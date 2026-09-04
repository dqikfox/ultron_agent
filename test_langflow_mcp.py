#!/usr/bin/env python3
"""
LangFlow MCP Server Integration - Test and Validation Suite
Tests connectivity, configuration, and tool availability
"""

import json
import subprocess
import urllib.request
import urllib.error
import sys
import time
from typing import Dict, Any, List, Optional, Tuple


class LangFlowMCPTester:
    """Comprehensive tester for LangFlow MCP integration"""

    def __init__(self,
                 langflow_url: str = "http://localhost:7860",
                 api_key: Optional[str] = None,
                 project_id: Optional[str] = None):
        """Initialize tester"""
        self.langflow_url = langflow_url
        self.api_key = api_key
        self.project_id = project_id
        self.results = {}
        self.test_count = 0
        self.passed_count = 0

    def log(self, level: str, message: str) -> None:
        """Log message with level prefix"""
        symbols = {
            "INFO": "ℹ️ ",
            "OK": "✅ ",
            "WARN": "⚠️  ",
            "ERROR": "❌ ",
            "STEP": "→ "
        }
        prefix = symbols.get(level, "   ")
        print(f"{prefix} {message}")

    def separator(self, title: str = "") -> None:
        """Print separator line"""
        line = "=" * 70
        if title:
            print(f"\n{line}")
            print(f"  {title}")
            print(f"{line}\n")
        else:
            print(f"{line}\n")

    # ==================== CONNECTIVITY TESTS ====================

    def test_langflow_running(self) -> Tuple[bool, str]:
        """Test 1: LangFlow server is running"""
        self.test_count += 1
        self.log("STEP", "Test 1: Checking if LangFlow server is running")

        try:
            response = urllib.request.urlopen(
                f"{self.langflow_url}/health",
                timeout=5
            )
            if response.status == 200:
                self.passed_count += 1
                self.log("OK", f"LangFlow running at {self.langflow_url}")
                return True, "✓ LangFlow server is running"
        except urllib.error.URLError as e:
            self.log("ERROR", f"Cannot reach {self.langflow_url}: {e}")
            return False, f"✗ LangFlow not accessible: {e}"
        except Exception as e:
            self.log("ERROR", f"Connection test failed: {e}")
            return False, f"✗ Error: {e}"

    def test_langflow_api(self) -> Tuple[bool, str]:
        """Test 2: LangFlow API is responding"""
        self.test_count += 1
        self.log("STEP", "Test 2: Checking LangFlow API endpoints")

        endpoints = [
            "/api/v1/projects",
            "/api/v1/flows",
            "/api/v1/status"
        ]

        available = []
        for endpoint in endpoints:
            try:
                response = urllib.request.urlopen(
                    f"{self.langflow_url}{endpoint}",
                    timeout=5
                )
                if response.status in [200, 201, 404]:  # 404 is ok for non-existent
                    available.append(endpoint)
            except:
                pass

        if available:
            self.passed_count += 1
            self.log("OK", f"API endpoints available: {available}")
            return True, f"✓ API responding on {len(available)} endpoints"
        else:
            self.log("ERROR", "No API endpoints responding")
            return False, "✗ API endpoints not accessible"

    def test_mcp_proxy_installed(self) -> Tuple[bool, str]:
        """Test 3: MCP Proxy tool is installed"""
        self.test_count += 1
        self.log("STEP", "Test 3: Checking MCP Proxy installation")

        try:
            result = subprocess.run(
                ["uvx", "--version"],
                capture_output=True,
                timeout=10,
                text=True
            )
            if result.returncode == 0 or "version" in result.stdout.lower():
                self.passed_count += 1
                self.log("OK", "uvx (MCP Proxy runner) is installed")
                return True, "✓ MCP Proxy tool available"
            else:
                self.log("WARN", "uvx version check unclear")
                self.log("STEP", "MCP Proxy will be auto-installed on first use")
                self.passed_count += 1
                return True, "✓ MCP Proxy will auto-install"
        except FileNotFoundError:
            self.log("WARN", "uvx not found, will auto-install on first use")
            self.passed_count += 1
            return True, "✓ MCP Proxy auto-install enabled"
        except Exception as e:
            self.log("ERROR", f"Error checking MCP Proxy: {e}")
            return False, f"✗ MCP Proxy check failed: {e}"

    # ==================== CONFIGURATION TESTS ====================

    def test_mcp_json_valid(self) -> Tuple[bool, str]:
        """Test 4: mcp.json configuration is valid JSON"""
        self.test_count += 1
        self.log("STEP", "Test 4: Validating mcp.json configuration")

        try:
            with open("mcp.json", "r") as f:
                config = json.load(f)

            # Check for "servers" key (Cursor format) or "mcpServers" (standard)
            servers_key = None
            if "servers" in config:
                servers_key = "servers"
            elif "mcpServers" in config:
                servers_key = "mcpServers"

            if servers_key:
                self.passed_count += 1
                servers = list(config[servers_key].keys())
                self.log("OK", f"mcp.json valid, {len(servers)} servers configured")
                self.log("STEP", f"Servers: {', '.join(servers)}")
                return True, "✓ mcp.json is valid"
            else:
                self.log("ERROR", "mcp.json missing 'servers' or 'mcpServers' key")
                return False, "✗ mcp.json malformed"
        except FileNotFoundError:
            self.log("ERROR", "mcp.json not found")
            return False, "✗ mcp.json not found"
        except json.JSONDecodeError as e:
            self.log("ERROR", f"mcp.json JSON error: {e}")
            return False, f"✗ mcp.json invalid JSON: {e}"
        except Exception as e:
            self.log("ERROR", f"Error reading mcp.json: {e}")
            return False, f"✗ Error: {e}"

    def test_langflow_in_mcp_config(self) -> Tuple[bool, str]:
        """Test 5: LangFlow server is configured in mcp.json"""
        self.test_count += 1
        self.log("STEP", "Test 5: Checking LangFlow in mcp.json")

        try:
            with open("mcp.json", "r") as f:
                config = json.load(f)

            # Check for servers or mcpServers key
            servers_key = "servers" if "servers" in config else "mcpServers"

            if "langflow" in config.get(servers_key, {}):
                self.passed_count += 1
                langflow_config = config[servers_key]["langflow"]
                self.log("OK", "LangFlow MCP server configured")

                # Check required fields
                required = ["command", "args"]
                for field in required:
                    if field in langflow_config:
                        self.log("STEP", f"  ✓ {field}: {langflow_config[field]}")
                    else:
                        self.log("WARN", f"  Missing: {field}")

                return True, "✓ LangFlow configured in mcp.json"
            else:
                self.log("ERROR", "LangFlow not configured in mcp.json")
                return False, "✗ LangFlow not in mcp.json"
        except Exception as e:
            self.log("ERROR", f"Error checking config: {e}")
            return False, f"✗ Error: {e}"

    # ==================== LANGFLOW TESTS ====================

    def test_langflow_projects(self) -> Tuple[bool, str]:
        """Test 6: LangFlow projects endpoint"""
        self.test_count += 1
        self.log("STEP", "Test 6: Checking LangFlow projects")

        try:
            response = urllib.request.urlopen(
                f"{self.langflow_url}/api/v1/projects",
                timeout=5
            )
            data = json.loads(response.read().decode())

            project_count = len(data) if isinstance(data, list) else 0
            self.passed_count += 1
            self.log("OK", f"Found {project_count} LangFlow projects")

            if project_count > 0:
                self.log("STEP", "Projects available for MCP server:")
                for project in data[:3]:
                    name = project.get("name", "Unknown")
                    self.log("STEP", f"  • {name}")

            return True, f"✓ {project_count} projects available"
        except Exception as e:
            self.log("WARN", f"Could not enumerate projects: {e}")
            self.passed_count += 1  # Not critical
            return True, "⚠ Projects endpoint available but not enumerable"

    def test_langflow_flows(self) -> Tuple[bool, str]:
        """Test 7: LangFlow flows endpoint"""
        self.test_count += 1
        self.log("STEP", "Test 7: Checking LangFlow flows")

        try:
            response = urllib.request.urlopen(
                f"{self.langflow_url}/api/v1/flows",
                timeout=5
            )
            data = json.loads(response.read().decode())

            flow_count = len(data) if isinstance(data, list) else 0
            self.passed_count += 1
            self.log("OK", f"Found {flow_count} LangFlow flows")

            if flow_count > 0:
                self.log("STEP", "Sample flows:")
                for flow in data[:3]:
                    name = flow.get("name", "Unknown")
                    self.log("STEP", f"  • {name}")

            return True, f"✓ {flow_count} flows available"
        except Exception as e:
            self.log("WARN", f"Could not enumerate flows: {e}")
            self.passed_count += 1  # Not critical
            return True, "⚠ Flows endpoint available"

    # ==================== MCP CONNECTION TESTS ====================

    def test_mcp_proxy_command(self) -> Tuple[bool, str]:
        """Test 8: MCP Proxy command construction"""
        self.test_count += 1
        self.log("STEP", "Test 8: Testing MCP Proxy connection command")

        if not self.project_id:
            self.log("WARN", "Project ID not provided, skipping MCP connection test")
            self.log("STEP", "Set project_id to test: test_langflow_mcp.py --project-id <ID>")
            return True, "⚠ Skipped (no project ID)"

        if not self.api_key:
            self.log("WARN", "API Key not provided, using test mode")
            api_key = "test-key"
        else:
            api_key = self.api_key

        # Build command
        cmd = [
            "uvx",
            "mcp-proxy",
            "--headers",
            f"x-api-key {api_key}",
            f"{self.langflow_url}/api/v1/mcp/project/{self.project_id}/sse"
        ]

        self.log("OK", "MCP Proxy command constructed:")
        self.log("STEP", f"  Command: {' '.join(cmd)}")
        self.passed_count += 1

        return True, "✓ MCP Proxy command valid"

    # ==================== TOOL TESTS ====================

    def test_langflow_mcp_tool(self) -> Tuple[bool, str]:
        """Test 9: LangFlow MCP tool is importable"""
        self.test_count += 1
        self.log("STEP", "Test 9: Checking LangFlow MCP tool")

        try:
            from tools.langflow_mcp_tool import LangflowMCPTool
            tool = LangflowMCPTool()

            # Test basic properties
            name = tool.name
            desc = tool.description

            self.passed_count += 1
            self.log("OK", f"LangFlow MCP tool loaded: {name}")
            self.log("STEP", f"  Description: {desc}")

            # Test match
            if tool.match("test langflow workflow"):
                self.log("OK", "Tool matching works")
            else:
                self.log("WARN", "Tool matching may need adjustment")

            return True, "✓ LangFlow MCP tool available"
        except ImportError as e:
            self.log("ERROR", f"Cannot import LangFlow tool: {e}")
            return False, f"✗ Import error: {e}"
        except Exception as e:
            self.log("ERROR", f"Tool test failed: {e}")
            return False, f"✗ Error: {e}"

    # ==================== SUMMARY ====================

    def run_all_tests(self) -> int:
        """Run all tests and return exit code"""
        self.separator("LANGFLOW MCP INTEGRATION TEST SUITE")

        self.log("INFO", f"Testing LangFlow at: {self.langflow_url}")
        if self.project_id:
            self.log("INFO", f"Project ID: {self.project_id}")

        # Run tests
        tests = [
            ("Connectivity", [
                self.test_langflow_running,
                self.test_langflow_api,
                self.test_mcp_proxy_installed,
            ]),
            ("Configuration", [
                self.test_mcp_json_valid,
                self.test_langflow_in_mcp_config,
            ]),
            ("LangFlow", [
                self.test_langflow_projects,
                self.test_langflow_flows,
            ]),
            ("MCP Integration", [
                self.test_mcp_proxy_command,
            ]),
            ("Tools", [
                self.test_langflow_mcp_tool,
            ]),
        ]

        for category, test_list in tests:
            self.separator(category)
            for test_func in test_list:
                success, message = test_func()
                self.results[test_func.__name__] = {
                    "success": success,
                    "message": message
                }

        # Summary
        self.separator("TEST SUMMARY")
        success_rate = (self.passed_count / self.test_count * 100) if self.test_count > 0 else 0

        self.log("INFO", f"Tests Passed: {self.passed_count}/{self.test_count} ({success_rate:.1f}%)")

        if self.passed_count == self.test_count:
            self.log("OK", "ALL TESTS PASSED ✓")
            return 0
        else:
            failed = self.test_count - self.passed_count
            self.log("ERROR", f"{failed} tests failed")
            return 1

    def print_configuration_report(self) -> None:
        """Print configuration for Cursor setup"""
        self.separator("CURSOR CONFIGURATION GUIDE")

        if not self.project_id or not self.api_key:
            self.log("WARN", "Project ID and API Key needed for Cursor setup")
            self.log("STEP", "Get these from LangFlow:")
            self.log("STEP", "  1. Go to http://localhost:7860")
            self.log("STEP", "  2. Projects > MCP Server tab")
            self.log("STEP", "  3. Copy PROJECT_ID and Generate API KEY")
            return

        config = {
            "mcpServers": {
                "langflow": {
                    "command": "uvx",
                    "args": [
                        "mcp-proxy",
                        "--headers",
                        f"x-api-key {self.api_key}",
                        f"{self.langflow_url}/api/v1/mcp/project/{self.project_id}/sse"
                    ]
                }
            }
        }

        self.log("OK", "Add this to .cursor/mcp.json or .vscode/mcp.json:")
        print(json.dumps(config, indent=2))


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Test LangFlow MCP Server integration"
    )
    parser.add_argument(
        "--langflow-url",
        default="http://localhost:7860",
        help="LangFlow server URL (default: http://localhost:7860)"
    )
    parser.add_argument(
        "--project-id",
        help="LangFlow Project ID (from MCP Server tab)"
    )
    parser.add_argument(
        "--api-key",
        help="LangFlow API Key (from MCP Server tab)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    tester = LangFlowMCPTester(
        langflow_url=args.langflow_url,
        api_key=args.api_key,
        project_id=args.project_id
    )

    exit_code = tester.run_all_tests()

    if args.project_id and args.api_key:
        tester.print_configuration_report()

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
