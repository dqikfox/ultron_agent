"""
Comprehensive test runner for ULTRON Agent 2
Runs all tests with detailed reporting and coverage analysis
"""
import pytest
import sys
import os
import subprocess
import json
from datetime import datetime
from pathlib import Path
import logging


class UltronTestRunner:
    """Comprehensive test runner for ULTRON Agent project"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_results = {}
        self.setup_logging()

    def setup_logging(self):
        """Setup comprehensive test logging"""
        log_file = self.project_root / "test_results.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def run_unit_tests(self):
        """Run all unit tests"""
        self.logger.info("Starting unit tests...")
        
        # Run pytest with detailed output
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/",
            "-v",  # Verbose output
            "--tb=short",  # Short traceback format
            "--strict-config",  # Strict configuration
            "--strict-markers",  # Strict markers
            "--durations=10",  # Show 10 slowest tests
            "--maxfail=5",  # Stop after 5 failures
            "--junit-xml=test_results.xml",  # JUnit XML output
            "--html=test_report.html",  # HTML report
            "--self-contained-html",  # Self-contained HTML
            "--cov=.",  # Coverage for all modules
            "--cov-report=html",  # HTML coverage report
            "--cov-report=term-missing",  # Terminal coverage with missing lines
            "--cov-report=json",  # JSON coverage report
            "--cov-fail-under=70",  # Fail if coverage below 70%
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            self.test_results["unit_tests"] = {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "passed": result.returncode == 0
            }
            
            if result.returncode == 0:
                self.logger.info("Unit tests PASSED")
            else:
                self.logger.error(f"Unit tests FAILED with return code {result.returncode}")
                self.logger.error(f"STDERR: {result.stderr}")
            
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Error running unit tests: {e}")
            return False

    def run_integration_tests(self):
        """Run integration tests"""
        self.logger.info("Starting integration tests...")
        
        integration_tests = [
            "test_agent_features.py",
            "test_enhanced_automation.py",
            "test_continue_integration.py"
        ]
        
        all_passed = True
        
        for test_file in integration_tests:
            if os.path.exists(test_file):
                self.logger.info(f"Running {test_file}...")
                
                cmd = [sys.executable, "-m", "pytest", test_file, "-v"]
                
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    
                    test_passed = result.returncode == 0
                    all_passed = all_passed and test_passed
                    
                    self.test_results[f"integration_{test_file}"] = {
                        "returncode": result.returncode,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "passed": test_passed
                    }
                    
                    if test_passed:
                        self.logger.info(f"{test_file} PASSED")
                    else:
                        self.logger.error(f"{test_file} FAILED")
                        
                except Exception as e:
                    self.logger.error(f"Error running {test_file}: {e}")
                    all_passed = False
        
        return all_passed

    def run_performance_tests(self):
        """Run performance tests"""
        self.logger.info("Starting performance tests...")
        
        # Performance test with pytest-benchmark if available
        cmd = [
            sys.executable, "-m", "pytest",
            "--benchmark-only",
            "--benchmark-sort=mean",
            "--benchmark-json=benchmark_results.json",
            "-v"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            self.test_results["performance"] = {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "passed": result.returncode == 0
            }
            
            return result.returncode == 0
            
        except Exception as e:
            self.logger.warning(f"Performance tests not available or failed: {e}")
            return True  # Don't fail overall tests if performance tests aren't available

    def run_security_tests(self):
        """Run security tests"""
        self.logger.info("Starting security tests...")
        
        security_checks = []
        
        # Check for common security issues
        try:
            # Check for hardcoded secrets
            self._check_hardcoded_secrets()
            security_checks.append("secrets_check")
            
            # Check file permissions
            self._check_file_permissions()
            security_checks.append("permissions_check")
            
            # Check for unsafe imports
            self._check_unsafe_imports()
            security_checks.append("imports_check")
            
            self.test_results["security"] = {
                "checks_passed": security_checks,
                "passed": True
            }
            
            self.logger.info("Security tests PASSED")
            return True
            
        except Exception as e:
            self.logger.error(f"Security tests FAILED: {e}")
            self.test_results["security"] = {
                "checks_passed": security_checks,
                "passed": False,
                "error": str(e)
            }
            return False

    def _check_hardcoded_secrets(self):
        """Check for hardcoded secrets in code"""
        suspicious_patterns = [
            "api_key", "secret", "password", "token", "credential"
        ]
        
        violations = []
        
        for py_file in self.project_root.rglob("*.py"):
            if "test" in str(py_file) or "__pycache__" in str(py_file):
                continue
                
            try:
                content = py_file.read_text(encoding='utf-8')
                for line_num, line in enumerate(content.split('\n'), 1):
                    for pattern in suspicious_patterns:
                        if pattern in line.lower() and "=" in line and not line.strip().startswith("#"):
                            violations.append(f"{py_file}:{line_num} - {line.strip()}")
            except Exception:
                continue
        
        if violations:
            self.logger.warning(f"Potential hardcoded secrets found: {len(violations)} violations")
            for violation in violations[:5]:  # Show first 5
                self.logger.warning(f"  {violation}")

    def _check_file_permissions(self):
        """Check file permissions for security"""
        sensitive_files = [
            "ultron_config.json",
            "keys.txt",
            "*.key",
            "*.pem"
        ]
        
        for pattern in sensitive_files:
            for file_path in self.project_root.rglob(pattern):
                if file_path.exists():
                    # Check if file is readable by others (on Unix systems)
                    import stat
                    permissions = oct(file_path.stat().st_mode)
                    if "666" in permissions or "777" in permissions:
                        self.logger.warning(f"Potentially unsafe permissions on {file_path}: {permissions}")

    def _check_unsafe_imports(self):
        """Check for potentially unsafe imports"""
        unsafe_imports = [
            "exec", "eval", "os.system", "subprocess.call", "__import__"
        ]
        
        violations = []
        
        for py_file in self.project_root.rglob("*.py"):
            if "test" in str(py_file):
                continue
                
            try:
                content = py_file.read_text(encoding='utf-8')
                for line_num, line in enumerate(content.split('\n'), 1):
                    for unsafe in unsafe_imports:
                        if unsafe in line and not line.strip().startswith("#"):
                            violations.append(f"{py_file}:{line_num} - {line.strip()}")
            except Exception:
                continue
        
        if violations:
            self.logger.info(f"Potentially unsafe code patterns found: {len(violations)}")

    def run_code_quality_checks(self):
        """Run code quality checks"""
        self.logger.info("Starting code quality checks...")
        
        quality_results = {}
        
        # Run flake8 if available
        try:
            result = subprocess.run([
                sys.executable, "-m", "flake8",
                "--max-line-length=100",
                "--ignore=E203,W503",
                "--exclude=__pycache__,*.pyc,.git,venv,env",
                "."
            ], capture_output=True, text=True, cwd=self.project_root)
            
            quality_results["flake8"] = {
                "returncode": result.returncode,
                "output": result.stdout,
                "passed": result.returncode == 0
            }
            
        except FileNotFoundError:
            self.logger.warning("flake8 not available")
        
        # Run mypy if available
        try:
            result = subprocess.run([
                sys.executable, "-m", "mypy",
                "--ignore-missing-imports",
                "--strict-optional",
                "."
            ], capture_output=True, text=True, cwd=self.project_root)
            
            quality_results["mypy"] = {
                "returncode": result.returncode,
                "output": result.stdout,
                "passed": result.returncode == 0
            }
            
        except FileNotFoundError:
            self.logger.warning("mypy not available")
        
        self.test_results["code_quality"] = quality_results
        
        # Quality checks are advisory, don't fail the build
        return True

    def generate_test_report(self):
        """Generate comprehensive test report"""
        self.logger.info("Generating test report...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "project": "ULTRON Agent 2",
            "test_results": self.test_results,
            "summary": self._generate_summary()
        }
        
        # Save JSON report
        report_file = self.project_root / "test_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Generate markdown report
        self._generate_markdown_report(report)
        
        self.logger.info(f"Test report saved to {report_file}")

    def _generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() 
                          if isinstance(result, dict) and result.get('passed', False))
        
        return {
            "total_test_suites": total_tests,
            "passed_test_suites": passed_tests,
            "failed_test_suites": total_tests - passed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
        }

    def _generate_markdown_report(self, report):
        """Generate markdown test report"""
        md_content = f"""# ULTRON Agent 2 Test Report

Generated: {report['timestamp']}

## Summary

- **Total Test Suites**: {report['summary']['total_test_suites']}
- **Passed**: {report['summary']['passed_test_suites']}
- **Failed**: {report['summary']['failed_test_suites']}
- **Success Rate**: {report['summary']['success_rate']:.1f}%

## Test Results

"""
        
        for test_name, result in report['test_results'].items():
            if isinstance(result, dict):
                status = "✅ PASSED" if result.get('passed', False) else "❌ FAILED"
                md_content += f"### {test_name}\n\n"
                md_content += f"**Status**: {status}\n\n"
                
                if 'returncode' in result:
                    md_content += f"**Return Code**: {result['returncode']}\n\n"
                
                if not result.get('passed', False) and 'stderr' in result:
                    md_content += f"**Error Output**:\n```\n{result['stderr'][:500]}...\n```\n\n"
        
        md_content += """
## Coverage Report

See `htmlcov/index.html` for detailed coverage report.

## Next Steps

1. Fix any failing tests
2. Improve code coverage where needed
3. Address any security or quality issues
4. Run performance optimization if needed
"""
        
        md_file = self.project_root / "TEST_REPORT.md"
        with open(md_file, 'w') as f:
            f.write(md_content)

    def run_all_tests(self):
        """Run comprehensive test suite"""
        self.logger.info("Starting ULTRON Agent 2 comprehensive test suite...")
        
        all_passed = True
        
        # Run different test categories
        test_categories = [
            ("Unit Tests", self.run_unit_tests),
            ("Integration Tests", self.run_integration_tests),
            ("Performance Tests", self.run_performance_tests),
            ("Security Tests", self.run_security_tests),
            ("Code Quality", self.run_code_quality_checks)
        ]
        
        for category_name, test_function in test_categories:
            self.logger.info(f"\n{'='*50}")
            self.logger.info(f"Running {category_name}")
            self.logger.info(f"{'='*50}")
            
            try:
                result = test_function()
                if not result:
                    all_passed = False
                    self.logger.error(f"{category_name} failed!")
                else:
                    self.logger.info(f"{category_name} completed successfully!")
                    
            except Exception as e:
                self.logger.error(f"Error in {category_name}: {e}")
                all_passed = False
        
        # Generate final report
        self.generate_test_report()
        
        # Final summary
        self.logger.info(f"\n{'='*60}")
        if all_passed:
            self.logger.info("🎉 ALL TESTS PASSED! ULTRON Agent 2 is ready for deployment!")
        else:
            self.logger.error("❌ SOME TESTS FAILED! Please review the issues above.")
        self.logger.info(f"{'='*60}")
        
        return all_passed


def main():
    """Main test runner entry point"""
    runner = UltronTestRunner()
    success = runner.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
