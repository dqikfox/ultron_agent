#!/usr/bin/env python3
"""
ULTRON Debug Test Suite - Comprehensive Testing & Validation
Tests all components and provides detailed diagnostics
"""

import os
import sys
import subprocess
import requests
import time
import json
from pathlib import Path
from datetime import datetime

class UltronDebugTester:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.services = {
            'main_gui': {'port': 5000, 'script': 'main_gui_server.py', 'name': 'Main GUI Server'},
            'chat_engine': {'port': 5173, 'script': 'frontend_server.py', 'name': 'Chat Engine'},
            'gui_api': {'port': 3000, 'script': 'gui_api_server.py', 'name': 'GUI API Server'},
            'agent_core': {'port': 8000, 'script': 'agent_core.py', 'name': 'Agent Core'}
        }
        self.test_results = {}

    def run_command(self, command, timeout=10):
        """Run a command and return the result"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f'Command timed out after {timeout} seconds'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def test_python_environment(self):
        """Test Python environment and dependencies"""
        print("🐍 Testing Python Environment...")

        # Test Python version
        python_result = self.run_command('python --version')
        if python_result['success']:
            print(f"✅ Python: {python_result['stdout'].strip()}")
        else:
            print(f"❌ Python: {python_result.get('error', 'Failed')}")

        # Test required packages
        packages = ['flask', 'requests', 'pathlib']
        for package in packages:
            try:
                __import__(package)
                print(f"✅ Package {package}: Available")
            except ImportError:
                print(f"❌ Package {package}: Missing")

    def test_file_structure(self):
        """Test required files and directories"""
        print("\n📁 Testing File Structure...")

        required_files = [
            'main_gui_server.py',
            'frontend_server.py',
            'gui_api_server.py',
            'agent_core.py',
            'web_bridge.py',
            'gui/ultron_enhanced/web/index.html'
        ]

        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                size = full_path.stat().st_size if full_path.is_file() else "DIR"
                print(f"✅ {file_path}: Exists ({size} bytes)")
            else:
                print(f"❌ {file_path}: Missing")

    def test_port_availability(self):
        """Test if required ports are available"""
        print("\n🔌 Testing Port Availability...")

        for service_id, info in self.services.items():
            port = info['port']
            result = self.run_command(f'netstat -an | findstr ":{port}"')

            if result['success'] and result['stdout'].strip():
                print(f"❌ Port {port} ({info['name']}): Already in use")
            else:
                print(f"✅ Port {port} ({info['name']}): Available")

    def test_individual_service(self, service_id, timeout=30):
        """Test starting an individual service"""
        service_info = self.services[service_id]
        print(f"\n🧪 Testing {service_info['name']}...")

        # Start the service
        script_path = self.project_root / service_info['script']
        if not script_path.exists():
            print(f"❌ Script not found: {script_path}")
            return False

        print(f"🚀 Starting {service_info['name']}...")

        # Set debug environment
        env = os.environ.copy()
        env['ULTRON_DEBUG'] = '1'
        env['PYTHONUNBUFFERED'] = '1'

        try:
            # Start the process
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env
            )

            # Wait a bit for startup
            time.sleep(5)

            # Check if it's running
            if process.poll() is None:
                print(f"✅ {service_info['name']}: Process started")

                # Test HTTP endpoint
                try:
                    response = requests.get(f"http://localhost:{service_info['port']}", timeout=5)
                    print(f"✅ {service_info['name']}: HTTP responding ({response.status_code})")
                    success = True
                except requests.exceptions.RequestException as e:
                    print(f"❌ {service_info['name']}: HTTP not responding - {e}")
                    success = False

                # Stop the process
                process.terminate()
                process.wait(timeout=5)
                print(f"🛑 {service_info['name']}: Process stopped")

            else:
                # Process died, get error output
                stdout, stderr = process.communicate()
                print(f"❌ {service_info['name']}: Process died")
                if stderr:
                    print(f"   Error: {stderr.decode()}")
                success = False

            return success

        except Exception as e:
            print(f"❌ {service_info['name']}: Test failed - {e}")
            return False

    def test_gui_content(self):
        """Test GUI content accessibility"""
        print("\n🎨 Testing GUI Content...")

        gui_index = self.project_root / "gui" / "ultron_enhanced" / "web" / "index.html"
        if gui_index.exists():
            with open(gui_index, 'r', encoding='utf-8') as f:
                content = f.read()

            # Basic content checks
            checks = [
                ('title', '<title>' in content),
                ('CSS links', 'stylesheet' in content),
                ('JavaScript', 'script' in content or '.js' in content),
                ('ULTRON branding', 'ULTRON' in content or 'ultron' in content.lower())
            ]

            for check_name, check_result in checks:
                status = "✅" if check_result else "❌"
                print(f"{status} GUI {check_name}: {'Found' if check_result else 'Missing'}")
        else:
            print("❌ GUI index.html not found")

    def run_full_diagnostic(self):
        """Run complete diagnostic suite"""
        print("🔧 ULTRON DEBUG TEST SUITE")
        print("=" * 60)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Project: {self.project_root}")
        print("=" * 60)

        # Run all tests
        self.test_python_environment()
        self.test_file_structure()
        self.test_port_availability()
        self.test_gui_content()

        # Test individual services (optional, takes time)
        test_services = input("\n🤔 Test individual services? (takes ~2 minutes) [y/N]: ")
        if test_services.lower() == 'y':
            for service_id in self.services:
                success = self.test_individual_service(service_id)
                self.test_results[service_id] = success

        # Generate report
        self.generate_report()

    def generate_report(self):
        """Generate diagnostic report"""
        print("\n📋 DIAGNOSTIC REPORT")
        print("=" * 60)

        if self.test_results:
            print("Service Tests:")
            for service_id, success in self.test_results.items():
                service_name = self.services[service_id]['name']
                status = "✅ PASSED" if success else "❌ FAILED"
                print(f"  {service_name}: {status}")

        # Save report to file
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'project_root': str(self.project_root),
            'service_results': self.test_results,
            'python_version': sys.version
        }

        report_file = self.project_root / 'debug_logs' / f'diagnostic_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)

        print(f"\n📄 Report saved: {report_file}")
        print("\n🎯 Next Steps:")
        print("  1. Run 'python run_debug.bat' for full system launch")
        print("  2. Use 'python debug_monitor.py' for real-time monitoring")
        print("  3. Check debug_logs/ for detailed information")

def main():
    tester = UltronDebugTester()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == 'quick':
            tester.test_python_environment()
            tester.test_file_structure()
        elif command in tester.services:
            tester.test_individual_service(command)
        else:
            print(f"Unknown command: {command}")
            print("Available commands: quick, full, or service names:", list(tester.services.keys()))
    else:
        tester.run_full_diagnostic()

if __name__ == "__main__":
    main()
