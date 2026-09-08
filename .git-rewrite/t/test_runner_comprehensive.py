#!/usr/bin/env python3
"""
Comprehensive Test Runner for ULTRON Agent 2
Executes all test suites with detailed reporting and analysis
"""

import sys
import os
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Any
import argparse


class UltronTestRunner:
    """Comprehensive test runner for ULTRON Agent 2"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent
        self.tests_dir = self.project_root / "tests"
        self.reports_dir = self.project_root / "test_reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        # Test categories
        self.test_categories = {
            "unit": [
                "test_config.py",
                "test_memory_fixed.py", 
                "test_voice_manager.py",
                "test_ollama_manager.py",
                "test_action_logger_fixed.py",
                "test_tools.py",
                "test_event_system_fixed.py"
            ],
            "integration": [
                "test_integration.py"
            ],
            "performance": [
                "test_performance.py"
            ],
            "security": [
                "test_security.py"
            ]
        }
        
        self.results = {}
    
    def setup_environment(self):
        """Setup test environment"""
        print("🔧 Setting up test environment...")
        
        # Create necessary directories
        directories = [
            "temp_logs",
            "temp_config",
            "temp_cache",
            "temp_screenshots",
            "test_reports"
        ]
        
        for dir_name in directories:
            dir_path = self.project_root / dir_name
            dir_path.mkdir(exist_ok=True)
        
        # Install test dependencies if needed
        try:
            import pytest
            import pytest_cov
            import pytest_html
            import pytest_benchmark
        except ImportError:
            print("📦 Installing test dependencies...")
            subprocess.run([
                sys.executable, "-m", "pip", "install",
                "pytest", "pytest-cov", "pytest-html", "pytest-benchmark",
                "pytest-asyncio", "pytest-mock"
            ], check=True)
    
    def run_test_category(self, category: str, files: List[str]) -> Dict[str, Any]:
        """Run tests for a specific category"""
        print(f"\n🧪 Running {category.upper()} tests...")
        
        category_results = {
            "category": category,
            "start_time": time.time(),
            "files": [],
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": [],
            "coverage": {}
        }
        
        for test_file in files:
            test_path = self.tests_dir / test_file
            if not test_path.exists():
                print(f"⚠️  Test file not found: {test_file}")
                continue
            
            print(f"  📄 Running {test_file}...")
            
            # Prepare pytest command
            cmd = [
                sys.executable, "-m", "pytest",
                str(test_path),
                "-v",
                "--tb=short",
                f"--html={self.reports_dir}/report_{category}_{test_file.replace('.py', '')}.html",
                "--self-contained-html",
                f"--cov={self.project_root}",
                f"--cov-report=html:{self.reports_dir}/coverage_{category}_{test_file.replace('.py', '')}",
                f"--cov-report=json:{self.reports_dir}/coverage_{category}_{test_file.replace('.py', '')}.json",
                "--cov-report=term-missing",
                f"--junit-xml={self.reports_dir}/junit_{category}_{test_file.replace('.py', '')}.xml"
            ]
            
            # Add benchmark for performance tests
            if category == "performance":
                cmd.extend(["--benchmark-only", "--benchmark-json", 
                           f"{self.reports_dir}/benchmark_{test_file.replace('.py', '')}.json"])
            
            try:
                # Run pytest
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
                
                # Parse results
                file_result = self.parse_pytest_output(result.stdout, result.stderr, result.returncode)
                file_result["file"] = test_file
                
                category_results["files"].append(file_result)
                category_results["total_tests"] += file_result["total_tests"]
                category_results["passed"] += file_result["passed"]
                category_results["failed"] += file_result["failed"]
                category_results["skipped"] += file_result["skipped"]
                
                if file_result["errors"]:
                    category_results["errors"].extend(file_result["errors"])
                
                # Load coverage data if available
                coverage_file = self.reports_dir / f"coverage_{category}_{test_file.replace('.py', '')}.json"
                if coverage_file.exists():
                    try:
                        with open(coverage_file) as f:
                            coverage_data = json.load(f)
                            category_results["coverage"][test_file] = coverage_data.get("totals", {})
                    except Exception as e:
                        print(f"⚠️  Could not load coverage data: {e}")
                
                print(f"    ✅ Passed: {file_result['passed']}, ❌ Failed: {file_result['failed']}, ⏭️  Skipped: {file_result['skipped']}")
                
            except Exception as e:
                print(f"    ❌ Error running {test_file}: {e}")
                category_results["errors"].append({
                    "file": test_file,
                    "error": str(e),
                    "type": "execution_error"
                })
        
        category_results["end_time"] = time.time()
        category_results["duration"] = category_results["end_time"] - category_results["start_time"]
        
        return category_results
    
    def parse_pytest_output(self, stdout: str, stderr: str, returncode: int) -> Dict[str, Any]:
        """Parse pytest output to extract test results"""
        result = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": [],
            "returncode": returncode,
            "stdout": stdout,
            "stderr": stderr
        }
        
        # Parse test results from output
        lines = stdout.split('\n')
        for line in lines:
            if "failed" in line.lower() and "passed" in line.lower():
                # Parse summary line like "5 failed, 10 passed in 2.34s"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "failed," and i > 0:
                        result["failed"] = int(parts[i-1])
                    elif part == "passed" and i > 0:
                        result["passed"] = int(parts[i-1])
                    elif part == "skipped" and i > 0:
                        result["skipped"] = int(parts[i-1])
            elif " PASSED " in line:
                result["passed"] += 1
            elif " FAILED " in line:
                result["failed"] += 1
                # Extract error details
                result["errors"].append({
                    "test": line.split(" FAILED ")[0].strip(),
                    "type": "test_failure"
                })
            elif " SKIPPED " in line:
                result["skipped"] += 1
        
        result["total_tests"] = result["passed"] + result["failed"] + result["skipped"]
        
        return result
    
    def run_all_tests(self, categories: List[str] = None) -> Dict[str, Any]:
        """Run all test categories"""
        print("🚀 Starting ULTRON Agent 2 Test Suite")
        print("=" * 50)
        
        self.setup_environment()
        
        if categories is None:
            categories = list(self.test_categories.keys())
        
        overall_results = {
            "start_time": time.time(),
            "categories": {},
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "total_files": 0,
                "categories_run": len(categories)
            }
        }
        
        for category in categories:
            if category in self.test_categories:
                category_results = self.run_test_category(category, self.test_categories[category])
                overall_results["categories"][category] = category_results
                
                # Update summary
                overall_results["summary"]["total_tests"] += category_results["total_tests"]
                overall_results["summary"]["passed"] += category_results["passed"]
                overall_results["summary"]["failed"] += category_results["failed"]
                overall_results["summary"]["skipped"] += category_results["skipped"]
                overall_results["summary"]["total_files"] += len(category_results["files"])
        
        overall_results["end_time"] = time.time()
        overall_results["duration"] = overall_results["end_time"] - overall_results["start_time"]
        
        # Save comprehensive results
        self.save_results(overall_results)
        
        # Print summary
        self.print_summary(overall_results)
        
        return overall_results
    
    def save_results(self, results: Dict[str, Any]):
        """Save test results to files"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        # Save JSON results
        json_file = self.reports_dir / f"test_results_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Generate HTML report
        self.generate_html_report(results, timestamp)
        
        print(f"\n📊 Detailed results saved to: {json_file}")
    
    def generate_html_report(self, results: Dict[str, Any], timestamp: str):
        """Generate comprehensive HTML report"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>ULTRON Agent 2 - Test Results</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .summary {{ background: #ecf0f1; padding: 15px; margin: 20px 0; border-radius: 5px; }}
        .category {{ margin: 20px 0; border: 1px solid #bdc3c7; border-radius: 5px; }}
        .category-header {{ background: #34495e; color: white; padding: 10px; }}
        .category-content {{ padding: 15px; }}
        .passed {{ color: #27ae60; }}
        .failed {{ color: #e74c3c; }}
        .skipped {{ color: #f39c12; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #f8f9fa; border-radius: 3px; }}
        .coverage {{ background: #d5f4e6; padding: 10px; margin: 10px 0; border-radius: 3px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 ULTRON Agent 2 - Test Results</h1>
        <p>Generated: {timestamp}</p>
    </div>
    
    <div class="summary">
        <h2>📊 Overall Summary</h2>
        <div class="metric">
            <strong>Total Tests:</strong> {results['summary']['total_tests']}
        </div>
        <div class="metric passed">
            <strong>Passed:</strong> {results['summary']['passed']}
        </div>
        <div class="metric failed">
            <strong>Failed:</strong> {results['summary']['failed']}
        </div>
        <div class="metric skipped">
            <strong>Skipped:</strong> {results['summary']['skipped']}
        </div>
        <div class="metric">
            <strong>Duration:</strong> {results['duration']:.2f}s
        </div>
        <div class="metric">
            <strong>Success Rate:</strong> {(results['summary']['passed'] / max(results['summary']['total_tests'], 1) * 100):.1f}%
        </div>
    </div>
"""
        
        # Add category details
        for category_name, category_data in results["categories"].items():
            html_content += f"""
    <div class="category">
        <div class="category-header">
            <h3>🧪 {category_name.upper()} Tests</h3>
        </div>
        <div class="category-content">
            <p><strong>Duration:</strong> {category_data['duration']:.2f}s</p>
            <p><strong>Files Tested:</strong> {len(category_data['files'])}</p>
            
            <table>
                <tr>
                    <th>Test File</th>
                    <th>Total</th>
                    <th class="passed">Passed</th>
                    <th class="failed">Failed</th>
                    <th class="skipped">Skipped</th>
                    <th>Status</th>
                </tr>
"""
            
            for file_data in category_data["files"]:
                status = "✅ PASS" if file_data["failed"] == 0 else "❌ FAIL"
                html_content += f"""
                <tr>
                    <td>{file_data['file']}</td>
                    <td>{file_data['total_tests']}</td>
                    <td class="passed">{file_data['passed']}</td>
                    <td class="failed">{file_data['failed']}</td>
                    <td class="skipped">{file_data['skipped']}</td>
                    <td>{status}</td>
                </tr>
"""
            
            html_content += """
            </table>
        </div>
    </div>
"""
        
        html_content += """
</body>
</html>
"""
        
        html_file = self.reports_dir / f"test_report_{timestamp}.html"
        with open(html_file, 'w') as f:
            f.write(html_content)
        
        print(f"📄 HTML report saved to: {html_file}")
    
    def print_summary(self, results: Dict[str, Any]):
        """Print test summary to console"""
        print("\n" + "=" * 50)
        print("🏁 ULTRON Agent 2 Test Suite Complete")
        print("=" * 50)
        
        summary = results["summary"]
        
        print(f"📊 Overall Results:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   ✅ Passed: {summary['passed']}")
        print(f"   ❌ Failed: {summary['failed']}")
        print(f"   ⏭️  Skipped: {summary['skipped']}")
        print(f"   ⏱️  Duration: {results['duration']:.2f}s")
        
        success_rate = (summary['passed'] / max(summary['total_tests'], 1)) * 100
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        print(f"\n📁 Test Categories:")
        for category_name, category_data in results["categories"].items():
            status = "✅" if category_data["failed"] == 0 else "❌"
            print(f"   {status} {category_name.upper()}: {category_data['passed']}/{category_data['total_tests']} passed")
        
        if summary['failed'] > 0:
            print(f"\n⚠️  {summary['failed']} tests failed. Check reports for details.")
            print(f"📁 Reports saved in: {self.reports_dir}")
        else:
            print(f"\n🎉 All tests passed successfully!")
        
        print("=" * 50)
    
    def run_specific_tests(self, test_files: List[str]):
        """Run specific test files"""
        print(f"🧪 Running specific tests: {', '.join(test_files)}")
        
        for test_file in test_files:
            test_path = self.tests_dir / test_file
            if test_path.exists():
                cmd = [
                    sys.executable, "-m", "pytest",
                    str(test_path),
                    "-v", "--tb=short"
                ]
                subprocess.run(cmd, cwd=self.project_root)
            else:
                print(f"❌ Test file not found: {test_file}")
    
    def check_test_health(self):
        """Check if all test files are properly structured"""
        print("🔍 Checking test health...")
        
        issues = []
        
        for category, files in self.test_categories.items():
            for test_file in files:
                test_path = self.tests_dir / test_file
                
                if not test_path.exists():
                    issues.append(f"Missing test file: {test_file}")
                    continue
                
                # Check if file has basic test structure
                try:
                    with open(test_path, 'r') as f:
                        content = f.read()
                        
                    if "import pytest" not in content:
                        issues.append(f"{test_file}: Missing pytest import")
                    
                    if "def test_" not in content:
                        issues.append(f"{test_file}: No test functions found")
                    
                    if "class Test" not in content:
                        issues.append(f"{test_file}: No test classes found")
                
                except Exception as e:
                    issues.append(f"{test_file}: Error reading file - {e}")
        
        if issues:
            print("⚠️  Issues found:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("✅ All test files are healthy!")
        
        return len(issues) == 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="ULTRON Agent 2 Test Runner")
    parser.add_argument("--category", "-c", choices=["unit", "integration", "performance", "security"],
                       help="Run specific test category")
    parser.add_argument("--file", "-f", nargs="+", help="Run specific test files")
    parser.add_argument("--health", action="store_true", help="Check test health")
    parser.add_argument("--project-root", help="Project root directory")
    
    args = parser.parse_args()
    
    runner = UltronTestRunner(args.project_root)
    
    if args.health:
        runner.check_test_health()
    elif args.file:
        runner.run_specific_tests(args.file)
    elif args.category:
        runner.run_all_tests([args.category])
    else:
        runner.run_all_tests()


if __name__ == "__main__":
    main()
