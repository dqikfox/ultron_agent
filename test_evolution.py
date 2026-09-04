#!/usr/bin/env python3
"""
Evolution Test Suite - Phase 1 API Enhancements.

Tests the new system metrics, comprehensive health, and console
execution endpoints
"""

import json
import urllib.request
import urllib.error
import sys
from datetime import datetime

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'


def log_header(text):
    """Print formatted header"""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{text:^70}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")


def log_pass(text):
    """Print pass message"""
    print(f"{GREEN}✓ PASS{RESET}: {text}")


def log_fail(text):
    """Print fail message"""
    print(f"{RED}✗ FAIL{RESET}: {text}")


def log_info(text):
    """Print info message"""
    print(f"{YELLOW}ℹ INFO{RESET}: {text}")


def log_section(text):
    """Print section header"""
    print(f"\n{CYAN}━━━ {text} ━━━{RESET}")


def test_api_endpoint(method, path, expected_status=200, body=None,
                      test_name=""):
    """Test an API endpoint and verify it returns JSON"""
    url = f"http://localhost:8080{path}"
    try:
        if method == "GET":
            req = urllib.request.Request(url)
            resp = urllib.request.urlopen(req)
        elif method == "POST":
            data = json.dumps(body or {}).encode('utf-8')
            req = urllib.request.Request(
                url,
                data=data,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            resp = urllib.request.urlopen(req)

        status = resp.status
        response_data = json.load(resp)

        if status == expected_status:
            log_pass(f"{test_name} ({method} {path}) - Status {status} OK")
            return True, response_data
        else:
            msg = f"{test_name} - Expected {expected_status}, got {status}"
            log_fail(msg)
            return False, response_data

    except urllib.error.HTTPError as e:
        response = e.read().decode('utf-8')
        log_fail(f"{test_name} - HTTP {e.code}: {response[:100]}")
        return False, None
    except Exception as e:
        log_fail(f"{test_name} - {str(e)[:100]}")
        return False, None


def main():
    """Main test function"""
    log_header("🚀 ULTRON EVOLUTION TEST SUITE - PHASE 1")
    log_info(f"Timestamp: {datetime.now().isoformat()}")
    log_info("Testing new system metrics and health monitoring APIs")

    # Ensure web server is running
    log_section("Step 1: Web Server Health Check")
    try:
        urllib.request.urlopen("http://localhost:8080/api/status")
        log_pass("Web server is running on port 8080")
    except Exception:
        log_fail("Web server not responding on port 8080")
        log_info("Start web server with: python web_gui_server.py")
        return 1

    results = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'tests': []
    }

    # Test 1: System Metrics Endpoint
    log_section("Test 1: System Metrics Endpoint")
    log_info("Endpoint: GET /api/system/metrics")
    success, data = test_api_endpoint('GET', '/api/system/metrics', 200,
                                      test_name="System Metrics")
    results['total'] += 1
    if success and data:
        if 'metrics' in data:
            metrics = data['metrics']
            log_pass(f"  CPU: {metrics['cpu']['percent']}%")
            mem_msg = (f"  Memory: {metrics['memory']['used_gb']:.1f}GB / "
                       f"{metrics['memory']['total_gb']:.1f}GB")
            log_pass(mem_msg)
            disk_msg = (f"  Disk: {metrics['disk']['used_gb']:.1f}GB / "
                        f"{metrics['disk']['total_gb']:.1f}GB")
            log_pass(disk_msg)
            log_pass(f"  Processes: {metrics['process_count']}")
            results['passed'] += 1
            results['tests'].append(
                {'name': 'System Metrics', 'status': 'PASS', 'data': metrics}
            )
        else:
            log_fail("  Missing 'metrics' field in response")
            results['failed'] += 1
    else:
        results['failed'] += 1

    # Test 2: Comprehensive Health Endpoint
    log_section("Test 2: Comprehensive Health Endpoint")
    log_info("Endpoint: GET /api/health/full")
    success, data = test_api_endpoint('GET', '/api/health/full', 200,
                                      test_name="Comprehensive Health")
    results['total'] += 1
    if success and data:
        overall = data.get('overall_status', 'unknown')
        log_pass(f"  Overall Status: {overall.upper()}")

        components = data.get('components', {})
        for component, status in components.items():
            comp_status = status.get('status', 'unknown').upper()
            log_pass(f"  {component.upper()}: {comp_status}")

        results['passed'] += 1
        results['tests'].append(
            {'name': 'Comprehensive Health', 'status': 'PASS', 'health': data}
        )
    else:
        results['failed'] += 1

    # Test 3: Console Command Execution (Safe Commands)
    log_section("Test 3: Console Command Execution (Safe)")
    log_info("Endpoint: POST /api/console/execute")

    # Test safe command: echo
    success, data = test_api_endpoint(
        'POST', '/api/console/execute', 200,
        body={'command': 'echo ULTRON_TEST', 'timeout': 5},
        test_name="Console Echo Command"
    )
    results['total'] += 1
    if success and data:
        if data.get('success'):
            output = data.get('stdout', '').strip()
            log_pass(f"  Command executed successfully")
            log_pass(f"  Output: {output}")
            results['passed'] += 1
            results['tests'].append(
                {'name': 'Console Execute (Echo)', 'status': 'PASS'}
            )
        else:
            log_fail(f"  Command failed: {data.get('error')}")
            results['failed'] += 1
    else:
        results['failed'] += 1

    # Test 4: Console Command Security (Blocked Commands)
    log_section("Test 4: Console Command Security (Unsafe Detection)")
    log_info("Endpoint: POST /api/console/execute (with unsafe command)")

    success, data = test_api_endpoint(
        'POST', '/api/console/execute', 200,
        body={'command': 'rm -rf /', 'timeout': 5},
        test_name="Console Unsafe Command"
    )
    results['total'] += 1
    if success and data:
        error = data.get('error', '')
        if not data.get('success') and 'not whitelisted' in error:
            log_pass(f"  Unsafe command correctly blocked")
            log_pass(f"  Security message: {data['error']}")
            results['passed'] += 1
            results['tests'].append(
                {'name': 'Console Security', 'status': 'PASS'}
            )
        else:
            log_fail(f"  Security check failed - command not blocked!")
            results['failed'] += 1
    else:
        results['failed'] += 1

    # Test 5: Autonomous Status with New Health Data
    log_section("Test 5: Autonomous Status Endpoint")
    log_info("Endpoint: GET /api/autonomous/status")
    success, data = test_api_endpoint('GET', '/api/autonomous/status', 200,
                                      test_name="Autonomous Status")
    results['total'] += 1
    if success and data:
        log_pass(f"  Active: {data.get('is_active', False)}")
        learning_records = data.get('learning_records', [])
        record_count = len(learning_records) if isinstance(
            learning_records, list) else learning_records
        log_pass(f"  Learning Records: {record_count}")
        results['passed'] += 1
        results['tests'].append(
            {'name': 'Autonomous Status', 'status': 'PASS'}
        )
    else:
        results['failed'] += 1

    # Test 6: System Status vs System Metrics Comparison
    log_section("Test 6: System Status vs System Metrics")
    log_info("Comparing /api/status vs /api/system/metrics")

    # Get both responses
    _, status_data = test_api_endpoint('GET', '/api/status', 200,
                                       test_name="Status Endpoint")
    _, metrics_data = test_api_endpoint('GET', '/api/system/metrics', 200,
                                        test_name="Metrics Endpoint")

    results['total'] += 1
    if status_data and metrics_data:
        status_cpu = status_data.get('system', {}).get('cpu_percent', 0)
        metrics_cpu = metrics_data.get('metrics', {}).get('cpu', {}).get('percent', 0)

        log_pass(f"  Status API CPU: {status_cpu}%")
        log_pass(f"  Metrics API CPU: {metrics_cpu}%")
        log_pass(f"  Both endpoints returning valid data")
        results['passed'] += 1
        results['tests'].append(
            {'name': 'API Comparison', 'status': 'PASS'}
        )
    else:
        results['failed'] += 1

    # Summary
    log_header("📊 TEST RESULTS SUMMARY")

    total = results['total']
    passed = results['passed']
    failed = results['failed']
    percentage = (passed / total * 100) if total > 0 else 0

    print(f"\n{CYAN}Tests Run:    {total}{RESET}")
    print(f"{GREEN}Passed:       {passed}{RESET}")
    print(f"{RED}Failed:       {failed}{RESET}")
    print(f"\n{CYAN}Success Rate: {percentage:.1f}%{RESET}")

    if failed == 0:
        print(f"\n{GREEN}{'='*70}{RESET}")
        print(f"{GREEN}🎉 ALL EVOLUTION TESTS PASSED!"
              f" Phase 1 Complete!{RESET}")
        print(f"{GREEN}{'='*70}{RESET}")
        return 0
    else:
        print(f"\n{RED}{'='*70}{RESET}")
        print(f"{RED}⚠️  Some tests failed. Review logs above.{RESET}")
        print(f"{RED}{'='*70}{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
if __name__ == "__main__":
    sys.exit(main())
