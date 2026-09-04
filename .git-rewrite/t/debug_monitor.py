#!/usr/bin/env python3
"""
ULTRON Debug Monitor - Real-time System Monitoring & Debugging
Provides comprehensive monitoring of all ULTRON services
"""

import time
import requests
import json
import subprocess
import os
import sys
from datetime import datetime
from pathlib import Path
import threading
import queue

class UltronDebugMonitor:
    def __init__(self):
        self.services = {
            'main_gui': {'port': 5000, 'name': 'Main GUI Server', 'url': 'http://localhost:5000'},
            'chat_engine': {'port': 5173, 'name': 'Chat Engine', 'url': 'http://localhost:5173'},
            'gui_api': {'port': 3000, 'name': 'GUI API Server', 'url': 'http://localhost:3000'},
            'agent_core': {'port': 8000, 'name': 'Agent Core', 'url': 'http://localhost:8000'}
        }
        self.log_dir = Path("debug_logs")
        self.log_dir.mkdir(exist_ok=True)
        self.monitor_active = True

    def check_port(self, port):
        """Check if a port is listening"""
        try:
            result = subprocess.run(
                ['netstat', '-an'],
                capture_output=True,
                text=True,
                shell=True
            )
            return f":{port}" in result.stdout
        except:
            return False

    def check_http_health(self, url):
        """Check HTTP health of a service"""
        try:
            response = requests.get(url, timeout=3)
            return {
                'status': 'OK',
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds()
            }
        except requests.exceptions.RequestException as e:
            return {
                'status': 'ERROR',
                'error': str(e)
            }

    def get_service_status(self):
        """Get comprehensive status of all services"""
        status = {}
        for service_id, service_info in self.services.items():
            port_listening = self.check_port(service_info['port'])
            http_health = self.check_http_health(service_info['url']) if port_listening else None

            status[service_id] = {
                'name': service_info['name'],
                'port': service_info['port'],
                'url': service_info['url'],
                'port_listening': port_listening,
                'http_health': http_health,
                'timestamp': datetime.now().isoformat()
            }
        return status

    def monitor_logs(self, log_file, service_name):
        """Monitor log file for changes"""
        if not os.path.exists(log_file):
            print(f"⚠️  Log file not found: {log_file}")
            return

        print(f"📝 Monitoring {service_name} logs: {log_file}")
        with open(log_file, 'r') as f:
            # Go to end of file
            f.seek(0, 2)
            while self.monitor_active:
                line = f.readline()
                if line:
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    print(f"[{timestamp}] {service_name}: {line.strip()}")
                else:
                    time.sleep(1)

    def print_status_table(self, status):
        """Print formatted status table"""
        print("\n" + "="*80)
        print(f"🔍 ULTRON SYSTEM STATUS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

        for service_id, info in status.items():
            port_status = "✅ LISTENING" if info['port_listening'] else "❌ NOT LISTENING"

            if info['http_health']:
                if info['http_health']['status'] == 'OK':
                    http_status = f"✅ HTTP OK ({info['http_health']['status_code']}) - {info['http_health']['response_time']:.3f}s"
                else:
                    http_status = f"❌ HTTP ERROR - {info['http_health']['error']}"
            else:
                http_status = "⭕ HTTP NOT TESTED" if not info['port_listening'] else "❌ HTTP FAILED"

            print(f"🔧 {info['name']:20} | Port {info['port']:4} | {port_status:15} | {http_status}")

        print("="*80)

    def save_debug_report(self, status):
        """Save debug report to file"""
        report_file = self.log_dir / f"debug_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        # Add system information
        debug_report = {
            'timestamp': datetime.now().isoformat(),
            'services': status,
            'system_info': {
                'python_version': sys.version,
                'working_directory': os.getcwd(),
                'debug_logs_dir': str(self.log_dir.absolute())
            }
        }

        with open(report_file, 'w') as f:
            json.dump(debug_report, f, indent=2)

        print(f"📄 Debug report saved: {report_file}")

    def run_continuous_monitor(self, interval=10):
        """Run continuous monitoring"""
        print("🚀 Starting ULTRON Debug Monitor...")
        print(f"⏱️  Monitoring interval: {interval} seconds")
        print("Press Ctrl+C to stop monitoring\n")

        try:
            while True:
                status = self.get_service_status()
                self.print_status_table(status)

                # Check for any issues
                issues = []
                for service_id, info in status.items():
                    if not info['port_listening']:
                        issues.append(f"{info['name']} not listening on port {info['port']}")
                    elif info['http_health'] and info['http_health']['status'] != 'OK':
                        issues.append(f"{info['name']} HTTP health check failed")

                if issues:
                    print(f"\n⚠️  ISSUES DETECTED:")
                    for issue in issues:
                        print(f"   • {issue}")

                print(f"\n⏱️  Next check in {interval} seconds...\n")
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
            self.monitor_active = False

    def run_single_check(self):
        """Run a single status check"""
        print("🔍 Running single system status check...\n")
        status = self.get_service_status()
        self.print_status_table(status)
        self.save_debug_report(status)

    def check_log_files(self):
        """Check debug log files"""
        print("📂 DEBUG LOG FILES STATUS:")
        print("="*50)

        log_files = [
            'main_gui_debug.log',
            'frontend_debug.log',
            'gui_api_debug.log',
            'agent_core_debug.log',
            'web_bridge_debug.log'
        ]

        for log_file in log_files:
            file_path = self.log_dir / log_file
            if file_path.exists():
                size = file_path.stat().st_size
                modified = datetime.fromtimestamp(file_path.stat().st_mtime)
                print(f"✅ {log_file:25} | {size:8} bytes | Modified: {modified.strftime('%H:%M:%S')}")

                # Check for errors in the log
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        error_count = content.lower().count('error') + content.lower().count('exception') + content.lower().count('traceback')
                        if error_count > 0:
                            print(f"⚠️  {log_file} contains {error_count} potential error indicators")
                except Exception as e:
                    print(f"❌ Could not read {log_file}: {e}")
            else:
                print(f"❌ {log_file:25} | NOT FOUND")

        print("="*50)

def main():
    monitor = UltronDebugMonitor()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == 'continuous':
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            monitor.run_continuous_monitor(interval)
        elif command == 'logs':
            monitor.check_log_files()
        elif command == 'single':
            monitor.run_single_check()
        else:
            print("Usage: python debug_monitor.py [continuous|single|logs] [interval]")
    else:
        # Interactive menu
        print("🔧 ULTRON DEBUG MONITOR")
        print("1. Single status check")
        print("2. Continuous monitoring (10s intervals)")
        print("3. Check debug log files")
        print("4. Custom continuous monitoring")

        choice = input("\nSelect option (1-4): ").strip()

        if choice == '1':
            monitor.run_single_check()
        elif choice == '2':
            monitor.run_continuous_monitor(10)
        elif choice == '3':
            monitor.check_log_files()
        elif choice == '4':
            try:
                interval = int(input("Enter monitoring interval (seconds): "))
                monitor.run_continuous_monitor(interval)
            except ValueError:
                print("Invalid interval, using default 10 seconds")
                monitor.run_continuous_monitor(10)
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()
