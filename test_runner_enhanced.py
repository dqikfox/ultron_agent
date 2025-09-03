#!/usr/bin/env python3
"""
Comprehensive test runner for ULTRON Agent 3.0
Runs all tests with proper categorization and reporting
"""

import subprocess
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any
import json
import time

class TestRunner:
    """Enhanced test runner with categorized test execution"""
    
    def __init__(self):
        self.results = {
            'security': {'passed': 0, 'failed': 0, 'errors': []},
            'unit': {'passed': 0, 'failed': 0, 'errors': []},
            'integration': {'passed': 0, 'failed': 0, 'errors': []},
            'performance': {'passed': 0, 'failed': 0, 'errors': []},
        }
        self.total_time = 0
    
    def run_security_tests(self) -> bool:
        """Run security-focused tests"""
        print("🔒 Running Security Tests...")
        security_tests = [
            'test_security.py',
            'test_accessible_gui_validation.py',
        ]
        
        success = True
        for test_file in security_tests:
            if Path(test_file).exists():
                result = self._run_test_file(test_file, 'security')
                success = success and result
        
        return success
    
    def run_unit_tests(self) -> bool:
        """Run unit tests"""
        print("🧪 Running Unit Tests...")
        unit_tests = [
            'test_agent_features.py',
            'test_brain.py',
            'test_ai_integration.py',
        ]
        
        success = True
        for test_file in unit_tests:
            if Path(test_file).exists():
                result = self._run_test_file(test_file, 'unit')
                success = success and result
        
        return success
    
    def run_integration_tests(self) -> bool:
        """Run integration tests"""
        print("🔗 Running Integration Tests...")
        integration_tests = [
            'test_integration.py',
            'test_gui_ultimate.py',
            'test_pokedex_integration.py',
        ]
        
        success = True
        for test_file in integration_tests:
            if Path(test_file).exists():
                result = self._run_test_file(test_file, 'integration')
                success = success and result
        
        return success
    
    def run_performance_tests(self) -> bool:
        """Run performance tests"""
        print("⚡ Running Performance Tests...")
        perf_tests = [
            'test_enhanced_automation.py',
        ]
        
        success = True
        for test_file in perf_tests:
            if Path(test_file).exists():
                result = self._run_test_file(test_file, 'performance')
                success = success and result
        
        return success
    
    def _run_test_file(self, test_file: str, category: str) -> bool:
        """Run a specific test file and categorize results"""
        try:
            print(f"  Running {test_file}...")
            start_time = time.time()
            
            result = subprocess.run(
                [sys.executable, '-m', 'pytest', test_file, '-v', '--tb=short'],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per test file
            )
            
            duration = time.time() - start_time
            self.total_time += duration
            
            if result.returncode == 0:
                self.results[category]['passed'] += 1
                print(f"    ✅ PASSED ({duration:.1f}s)")
                return True
            else:
                self.results[category]['failed'] += 1
                error_msg = f"{test_file}: {result.stderr[:200]}"
                self.results[category]['errors'].append(error_msg)
                print(f"    ❌ FAILED ({duration:.1f}s)")
                return False
                
        except subprocess.TimeoutExpired:
            self.results[category]['failed'] += 1
            error_msg = f"{test_file}: Test timed out after 300 seconds"
            self.results[category]['errors'].append(error_msg)
            print(f"    ⏱️ TIMEOUT")
            return False
        except Exception as e:
            self.results[category]['failed'] += 1
            error_msg = f"{test_file}: {str(e)}"
            self.results[category]['errors'].append(error_msg)
            print(f"    💥 ERROR: {e}")
            return False
    
    def generate_report(self) -> None:
        """Generate comprehensive test report"""
        print("\n" + "="*60)
        print("📊 TEST EXECUTION SUMMARY")
        print("="*60)
        
        total_passed = sum(cat['passed'] for cat in self.results.values())
        total_failed = sum(cat['failed'] for cat in self.results.values())
        total_tests = total_passed + total_failed
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {total_passed} ✅")
        print(f"Failed: {total_failed} ❌")
        print(f"Success Rate: {(total_passed/max(total_tests,1)*100):.1f}%")
        print(f"Total Time: {self.total_time:.1f}s")
        
        print("\n📋 BY CATEGORY:")
        for category, results in self.results.items():
            total_cat = results['passed'] + results['failed']
            if total_cat > 0:
                success_rate = (results['passed'] / total_cat * 100)
                print(f"  {category.upper()}: {results['passed']}/{total_cat} ({success_rate:.1f}%)")
        
        # Show errors if any
        for category, results in self.results.items():
            if results['errors']:
                print(f"\n❌ {category.upper()} ERRORS:")
                for error in results['errors']:
                    print(f"  • {error}")
        
        # Save detailed report
        report_file = f"test_report_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump({
                'summary': {
                    'total_tests': total_tests,
                    'passed': total_passed,
                    'failed': total_failed,
                    'success_rate': total_passed/max(total_tests,1)*100,
                    'total_time': self.total_time
                },
                'results': self.results,
                'timestamp': time.time()
            }, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")

def main():
    """Main test runner entry point"""
    parser = argparse.ArgumentParser(description='ULTRON Agent Test Runner')
    parser.add_argument('--security', action='store_true', help='Run security tests only')
    parser.add_argument('--unit', action='store_true', help='Run unit tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    parser.add_argument('--performance', action='store_true', help='Run performance tests only')
    parser.add_argument('--all', action='store_true', help='Run all tests (default)')
    
    args = parser.parse_args()
    
    # If no specific test type selected, run all
    if not (args.security or args.unit or args.integration or args.performance):
        args.all = True
    
    runner = TestRunner()
    success = True
    
    print("🧪 ULTRON Agent 3.0 - Comprehensive Test Suite")
    print("=" * 50)
    
    if args.all or args.security:
        success = runner.run_security_tests() and success
    
    if args.all or args.unit:
        success = runner.run_unit_tests() and success
    
    if args.all or args.integration:
        success = runner.run_integration_tests() and success
    
    if args.all or args.performance:
        success = runner.run_performance_tests() and success
    
    runner.generate_report()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        return 0
    else:
        print("\n⚠️ Some tests failed. Check the report above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())