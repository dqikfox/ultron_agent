#!/usr/bin/env python3
"""
ULTRON Agent 3.0 - Full System Diagnostic
Comprehensive health check of all system components
"""

import requests
import json
import subprocess
import socket
import os
import sys
from datetime import datetime

class UltronDiagnostic:
    def __init__(self):
        self.results = {}
        self.issues = []
        self.successes = []

    def print_header(self, title):
        print(f"\n{'='*60}")
        print(f"🔍 {title}")
        print(f"{'='*60}")

    def print_status(self, item, status, details=""):
        icon = "✅" if status else "❌"
        print(f"{icon} {item}")
        if details:
            print(f"   {details}")

        if status:
            self.successes.append(item)
        else:
            self.issues.append(f"{item}: {details}")

    def check_port(self, port, service_name):
        """Check if a port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result == 0
        except:
            return False

    def test_http_endpoint(self, url, timeout=5):
        """Test HTTP endpoint"""
        try:
            response = requests.get(url, timeout=timeout)
            return response.ok, response.status_code, response.text[:200]
        except Exception as e:
            return False, 0, str(e)

    def test_post_endpoint(self, url, data, timeout=10):
        """Test HTTP POST endpoint"""
        try:
            response = requests.post(url, json=data, timeout=timeout)
            return response.ok, response.status_code, response.text[:500]
        except Exception as e:
            return False, 0, str(e)

    def check_file_exists(self, filepath):
        """Check if file exists"""
        return os.path.exists(filepath)

    def run_diagnostic(self):
        """Run full system diagnostic"""

        self.print_header("ULTRON Agent 3.0 - System Diagnostic")
        print(f"🕐 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🐍 Python Version: {sys.version}")
        print(f"📁 Current Directory: {os.getcwd()}")

        # 1. Core Files Check
        self.print_header("1. Core Files Verification")
        core_files = [
            "main.py",
            "web_gui_server.py",
            "ultron_bridge.py",
            "brain.py",
            "voice.py",
            "vision.py",
            "ultron_config.json",
            "requirements.txt",
            "gui/ultron_enhanced/web/index.html",
            "gui/ultron_enhanced/web/app.js",
            "gui/ultron_enhanced/web/style.css"
        ]

        for file in core_files:
            exists = self.check_file_exists(file)
            self.print_status(f"File: {file}", exists)

        # 2. Port and Service Check
        self.print_header("2. Network Services Status")
        services = [
            (11434, "Ollama LLM Service"),
            (8080, "Web GUI Server"),
            (5001, "Bridge Server"),
            (5000, "API Server")
        ]

        for port, name in services:
            is_open = self.check_port(port, name)
            self.print_status(f"{name} (Port {port})", is_open)

        # 3. Ollama Service Check
        self.print_header("3. Ollama LLM Service")
        ollama_base = "http://localhost:11434"

        # Test Ollama API
        success, status, response = self.test_http_endpoint(f"{ollama_base}/api/tags")
        self.print_status("Ollama API Connection", success, f"Status: {status}")

        if success:
            try:
                models = json.loads(response).get('models', [])
                self.print_status(f"Available Models", len(models) > 0, f"Count: {len(models)}")
                if models:
                    print(f"   📋 Models: {', '.join([m['name'][:20] for m in models[:5]])}")
                    if len(models) > 5:
                        print(f"   ... and {len(models)-5} more")
            except:
                self.print_status("Model List Parsing", False, "Could not parse model list")

        # 4. Web GUI Server Check
        self.print_header("4. Web GUI Server")
        gui_base = "http://localhost:8080"

        # Test main page
        success, status, response = self.test_http_endpoint(gui_base)
        self.print_status("Main GUI Page", success, f"Status: {status}")

        # Test API endpoints
        api_endpoints = [
            "/api/status",
            "/api/llm/status",
            "/api/voice/status",
            "/api/brain/status",
            "/api/llm/models"
        ]

        for endpoint in api_endpoints:
            success, status, response = self.test_http_endpoint(f"{gui_base}{endpoint}")
            self.print_status(f"API: {endpoint}", success, f"Status: {status}")

            if success and endpoint == "/api/llm/status":
                try:
                    data = json.loads(response)
                    model = data.get('model', 'Unknown')
                    print(f"   🤖 Current Model: {model}")
                except:
                    pass

        # 5. Chat Functionality Test
        self.print_header("5. AI Chat Functionality")

        chat_data = {"message": "Hello! Please respond with exactly: 'ULTRON DIAGNOSTIC TEST SUCCESSFUL'"}
        success, status, response = self.test_post_endpoint(f"{gui_base}/api/llm/chat", chat_data, timeout=30)

        self.print_status("Chat Endpoint", success, f"Status: {status}")

        if success:
            try:
                chat_response = json.loads(response)
                ai_message = chat_response.get('response', '')
                self.print_status("AI Response Generated", len(ai_message) > 0, f"Length: {len(ai_message)} chars")
                print(f"   🤖 AI Says: {ai_message[:100]}...")

                # Check if AI understood the test
                test_successful = "DIAGNOSTIC TEST SUCCESSFUL" in ai_message.upper()
                self.print_status("AI Understanding Test", test_successful)

            except Exception as e:
                self.print_status("Chat Response Parsing", False, str(e))

        # 6. Configuration Check
        self.print_header("6. Configuration Files")

        config_files = [
            "ultron_config.json",
            "requirements.txt",
            "requirements_bridge.txt"
        ]

        for config_file in config_files:
            exists = self.check_file_exists(config_file)
            self.print_status(f"Config: {config_file}", exists)

            if exists and config_file.endswith('.json'):
                try:
                    with open(config_file, 'r') as f:
                        config_data = json.load(f)
                    self.print_status(f"  Valid JSON format", True, f"Keys: {len(config_data)}")
                except Exception as e:
                    self.print_status(f"  JSON parsing", False, str(e))

        # 7. Python Dependencies
        self.print_header("7. Python Dependencies")

        required_modules = [
            'requests',
            'flask',
            'threading',
            'json',
            'logging',
            'socket',
            'http.server'
        ]

        for module in required_modules:
            try:
                __import__(module)
                self.print_status(f"Module: {module}", True)
            except ImportError as e:
                self.print_status(f"Module: {module}", False, str(e))

        # 8. System Summary
        self.print_header("8. Diagnostic Summary")

        total_checks = len(self.successes) + len(self.issues)
        success_rate = (len(self.successes) / total_checks * 100) if total_checks > 0 else 0

        print(f"📊 Total Checks: {total_checks}")
        print(f"✅ Successful: {len(self.successes)}")
        print(f"❌ Issues Found: {len(self.issues)}")
        print(f"📈 Success Rate: {success_rate:.1f}%")

        if self.issues:
            print(f"\n🔧 Issues to Address:")
            for i, issue in enumerate(self.issues, 1):
                print(f"   {i}. {issue}")

        print(f"\n🎯 System Status: {'HEALTHY' if success_rate > 80 else 'NEEDS ATTENTION' if success_rate > 60 else 'CRITICAL'}")

        # 9. Recommendations
        self.print_header("9. Recommendations")

        if success_rate > 90:
            print("🎉 Excellent! Your ULTRON Agent system is running perfectly!")
            print("🚀 Ready for full AI interaction and voice control.")
        elif success_rate > 70:
            print("⚠️  System is mostly functional but has some issues.")
            print("🔧 Address the issues above for optimal performance.")
        else:
            print("🚨 Critical issues detected. System needs attention.")
            print("🛠️  Please resolve the major issues before using the system.")

        return success_rate > 70

if __name__ == "__main__":
    diagnostic = UltronDiagnostic()
    diagnostic.run_diagnostic()
