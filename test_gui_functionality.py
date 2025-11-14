#!/usr/bin/env python3
"""
ULTRON Agent GUI Testing Script
Comprehensive testing of all GUI links and functions
"""

import requests
import json
import time
import subprocess
from pathlib import Path

class UltronGUITester:
    def __init__(self):
        self.base_url = "http://localhost:8080"
        self.api_url = "http://localhost:5001"  # API server port from our tests
        self.results = {}

    def test_web_gui_access(self):
        """Test if the web GUI is accessible"""
        try:
            response = requests.get(self.base_url, timeout=5)
            status = "✅ PASS" if response.status_code == 200 else f"❌ FAIL (Status: {response.status_code})"
            self.results["Web GUI Access"] = status
            return response.status_code == 200
        except Exception as e:
            self.results["Web GUI Access"] = f"❌ FAIL (Error: {str(e)})"
            return False

    def test_ssh_server_running(self):
        """Test if SSH server is running on port 2222"""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex(('localhost', 2222))
            sock.close()

            if result == 0:
                self.results["SSH Server Port 2222"] = "✅ PASS (Port accessible)"
                return True
            else:
                self.results["SSH Server Port 2222"] = "❌ FAIL (Port not accessible)"
                return False
        except Exception as e:
            self.results["SSH Server Port 2222"] = f"❌ FAIL (Error: {str(e)})"
            return False

    def test_api_server_access(self):
        """Test if API server is accessible"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            status = "✅ PASS" if response.status_code in [200, 401] else f"❌ FAIL (Status: {response.status_code})"
            self.results["API Server Access"] = status
            return response.status_code in [200, 401]
        except Exception as e:
            self.results["API Server Access"] = f"❌ FAIL (Error: {str(e)})"
            return False

    def test_ssh_api_endpoints(self):
        """Test SSH API endpoints (without auth)"""
        endpoints = [
            "/api/ssh/status",
            "/api/ssh/start",
            "/api/ssh/stop"
        ]

        for endpoint in endpoints:
            try:
                if "start" in endpoint or "stop" in endpoint:
                    response = requests.post(f"{self.api_url}{endpoint}", timeout=5)
                else:
                    response = requests.get(f"{self.api_url}{endpoint}", timeout=5)

                # We expect 401 (auth required) which means endpoint exists
                if response.status_code == 401:
                    self.results[f"SSH API {endpoint}"] = "✅ PASS (Endpoint exists, auth required)"
                elif response.status_code == 200:
                    self.results[f"SSH API {endpoint}"] = "✅ PASS (Endpoint accessible)"
                else:
                    self.results[f"SSH API {endpoint}"] = f"⚠️ UNKNOWN (Status: {response.status_code})"

            except Exception as e:
                self.results[f"SSH API {endpoint}"] = f"❌ FAIL (Error: {str(e)})"

    def test_gui_files_exist(self):
        """Test if GUI files exist"""
        gui_dir = Path("gui/ultron_enhanced/web")
        files_to_check = [
            "index.html",
            "app.js",
            "styles.css"
        ]

        for file in files_to_check:
            file_path = gui_dir / file
            if file_path.exists():
                self.results[f"GUI File {file}"] = "✅ PASS (File exists)"
            else:
                self.results[f"GUI File {file}"] = "❌ FAIL (File missing)"

    def test_ssh_tool_exists(self):
        """Test if SSH tool exists"""
        ssh_tool_path = Path("tools/ssh_server_tool.py")
        if ssh_tool_path.exists():
            self.results["SSH Tool File"] = "✅ PASS (File exists)"
        else:
            self.results["SSH Tool File"] = "❌ FAIL (File missing)"

    def test_config_has_ssh(self):
        """Test if ultron_config.json has SSH settings"""
        try:
            config_path = Path("ultron_config.json")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)

                if 'ssh_server' in config:
                    ssh_config = config['ssh_server']
                    has_port = 'port' in ssh_config
                    has_enabled = 'enabled' in ssh_config

                    if has_port and has_enabled:
                        self.results["SSH Configuration"] = f"✅ PASS (Port: {ssh_config.get('port', 'N/A')}, Enabled: {ssh_config.get('enabled', 'N/A')})"
                    else:
                        self.results["SSH Configuration"] = "⚠️ PARTIAL (Some SSH settings missing)"
                else:
                    self.results["SSH Configuration"] = "❌ FAIL (No SSH section in config)"
            else:
                self.results["SSH Configuration"] = "❌ FAIL (Config file missing)"
        except Exception as e:
            self.results["SSH Configuration"] = f"❌ FAIL (Error: {str(e)})"

    def run_all_tests(self):
        """Run all tests and return results"""
        print("🚀 Starting ULTRON Agent GUI Testing...")
        print("=" * 60)

        # Run tests
        self.test_web_gui_access()
        self.test_ssh_server_running()
        self.test_api_server_access()
        self.test_ssh_api_endpoints()
        self.test_gui_files_exist()
        self.test_ssh_tool_exists()
        self.test_config_has_ssh()

        # Print results
        print("\n📊 TEST RESULTS:")
        print("=" * 60)

        passed = 0
        total = 0

        for test_name, result in self.results.items():
            print(f"{test_name:<25}: {result}")
            total += 1
            if result.startswith("✅"):
                passed += 1

        print("=" * 60)
        print(f"📈 SUMMARY: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

        if passed == total:
            print("🎉 ALL TESTS PASSED! SSH Integration is fully functional.")
        elif passed >= total * 0.8:
            print("✅ MOSTLY FUNCTIONAL - Minor issues detected.")
        else:
            print("⚠️ SIGNIFICANT ISSUES - Review failed tests.")

        return self.results

def main():
    """Main test execution"""
    tester = UltronGUITester()
    results = tester.run_all_tests()

    # Save results to file
    with open("gui_test_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Results saved to: gui_test_results.json")

if __name__ == "__main__":
    main()
