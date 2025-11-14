"""
ULTRON GUI Navigation Test Suite
Tests all navigation links and logs interactions
"""
import requests
import json
from datetime import datetime

class GUINavigationTester:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.test_results = []

    def log(self, message, status="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "status": status,
            "message": message
        }
        self.test_results.append(log_entry)
        print(f"[{timestamp}] [{status}] {message}")

    def test_endpoint(self, endpoint, method="GET", data=None):
        """Test a specific API endpoint"""
        url = f"{self.base_url}{endpoint}"
        self.log(f"Testing {method} {endpoint}")

        try:
            if method == "GET":
                response = requests.get(url, timeout=5)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=5)

            self.log(f"  Response: {response.status_code}",
                    "SUCCESS" if response.status_code == 200 else "WARNING")

            if response.status_code == 200:
                try:
                    json_data = response.json()
                    self.log(f"  Data: {json.dumps(json_data, indent=2)[:200]}...", "DATA")
                except:
                    self.log(f"  Text: {response.text[:200]}...", "DATA")

            return response.status_code == 200

        except Exception as e:
            self.log(f"  Error: {str(e)}", "ERROR")
            return False

    def test_all_navigation_endpoints(self):
        """Test all navigation-related API endpoints"""
        self.log("=" * 60)
        self.log("STARTING ULTRON GUI NAVIGATION TESTS")
        self.log("=" * 60)

        # Test main endpoints for each navigation section
        endpoints = {
            "Dashboard": "/api/system/stats",
            "System Info": "/api/system/info",
            "Vision System": "/api/vision/status",
            "NVIDIA NIM": "/api/nvidia/status",
            "Game Status": "/api/game/status",
            "Tools List": "/api/tools/list",
            "Assistant Status": "/api/assistant/status",
            "SSH Status": "/api/ssh/status",
            "File System": "/api/files/list",
            "Tasks": "/api/tasks/list",
            "LLM Models": "/api/models/list",
            "Voice Status": "/api/voice/status",
            "AutoGen Status": "/api/autogen/status",
        }

        results = {}
        for name, endpoint in endpoints.items():
            self.log(f"\n--- Testing {name} ---")
            results[name] = self.test_endpoint(endpoint)

        # Test command endpoint
        self.log(f"\n--- Testing Command Endpoint ---")
        results["Command API"] = self.test_endpoint(
            "/api/command",
            method="POST",
            data={"command": "status"}
        )

        # Generate summary
        self.log("\n" + "=" * 60)
        self.log("TEST SUMMARY")
        self.log("=" * 60)

        passed = sum(1 for v in results.values() if v)
        total = len(results)

        self.log(f"✅ Passed: {passed}/{total}")
        self.log(f"❌ Failed: {total - passed}/{total}")

        self.log("\nDetailed Results:")
        for name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            self.log(f"  {status} - {name}")

        # Save results to file
        self.save_results()

        return passed == total

    def save_results(self):
        """Save test results to JSON file"""
        filename = f"gui_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        self.log(f"\n📝 Test results saved to: {filename}")

def main():
    print("\n🚀 ULTRON GUI Navigation Tester\n")
    tester = GUINavigationTester()
    success = tester.test_all_navigation_endpoints()

    if success:
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n⚠️ Some tests failed. Check logs for details.")
        return 1

if __name__ == "__main__":
    exit(main())
