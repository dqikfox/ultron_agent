#!/usr/bin/env python3
"""
ULTRON Agent Auto-Monitor
Monitors repository for issues and suggests improvements
"""

import time
import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timedelta

class RepoAutoMonitor:
    def __init__(self, repo_path: str = "c:/Projects/ultron_agent_2"):
        self.repo_path = Path(repo_path)
        self.setup_logging()
        self.last_check = datetime.now()
        self.issues_found = []

    def setup_logging(self):
        """Setup logging for the monitor"""
        logging.basicConfig(
            filename='auto_monitor.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def safe_file_scan(self, max_depth: int = 3) -> List[Path]:
        """Safely scan files without getting stuck in circular references"""
        files = []

        def scan_dir(path: Path, current_depth: int = 0):
            if current_depth > max_depth:
                return

            try:
                for item in path.iterdir():
                    if item.is_file():
                        # Skip problematic files
                        if not any(skip in str(item) for skip in [
                            '__pycache__', '.git', 'node_modules', '.cache',
                            'logs', 'cache', 'temp', '.pytest_cache'
                        ]):
                            files.append(item)
                    elif item.is_dir() and current_depth < max_depth:
                        # Avoid circular references
                        if not any(circular in str(item) for circular in [
                            'node_modules', '.git', '__pycache__'
                        ]):
                            scan_dir(item, current_depth + 1)
            except (OSError, PermissionError) as e:
                self.logger.warning(f"Cannot scan {path}: {e}")

        scan_dir(self.repo_path)
        return files

    def analyze_python_files(self) -> List[Dict[str, Any]]:
        """Analyze Python files for common issues"""
        issues = []

        python_files = [f for f in self.safe_file_scan() if f.suffix == '.py']

        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')

                # Check for common issues
                file_issues = self.analyze_file_content(file_path, content, lines)
                issues.extend(file_issues)

            except Exception as e:
                self.logger.error(f"Error analyzing {file_path}: {e}")

        return issues

    def analyze_file_content(self, file_path: Path, content: str, lines: List[str]) -> List[Dict[str, Any]]:
        """Analyze individual file content for issues"""
        issues = []

        # Check for TODO/FIXME comments
        for i, line in enumerate(lines, 1):
            if 'TODO' in line.upper():
                issues.append({
                    'type': 'todo',
                    'file': str(file_path),
                    'line': i,
                    'message': f'TODO comment found: {line.strip()[:100]}'
                })
            if 'FIXME' in line.upper():
                issues.append({
                    'type': 'fixme',
                    'file': str(file_path),
                    'line': i,
                    'message': f'FIXME comment found: {line.strip()[:100]}'
                })

        # Check for debug prints in production code
        if 'print(' in content and 'test' not in str(file_path).lower():
            issues.append({
                'type': 'debug_print',
                'file': str(file_path),
                'line': 0,
                'message': 'Debug print statement found in non-test file'
            })

        # Check for missing error handling
        if 'try:' in content and 'except:' not in content:
            issues.append({
                'type': 'missing_error_handling',
                'file': str(file_path),
                'line': 0,
                'message': 'Try block without except block'
            })

        return issues

    def generate_report(self, issues: List[Dict[str, Any]]) -> str:
        """Generate a human-readable report"""
        if not issues:
            return "✅ No issues found in the last scan!"

        report = f"🔍 Repository Scan Report ({len(issues)} issues found)\n"
        report += "=" * 60 + "\n\n"

        # Group issues by type
        by_type = {}
        for issue in issues:
            issue_type = issue['type']
            if issue_type not in by_type:
                by_type[issue_type] = []
            by_type[issue_type].append(issue)

        for issue_type, type_issues in by_type.items():
            report += f"⚠️  {issue_type.upper()} ({len(type_issues)}):\n"
            for issue in type_issues[:3]:  # Show first 3 of each type
                report += f"  • {issue['file']}:{issue['line']} - {issue['message']}\n"
            if len(type_issues) > 3:
                report += f"  ... and {len(type_issues) - 3} more\n"
            report += "\n"

        return report

    def run_monitoring_cycle(self) -> str:
        """Run one complete monitoring cycle"""
        self.logger.info("Starting monitoring cycle")

        try:
            # Analyze Python files
            issues = self.analyze_python_files()

            # Generate report
            report = self.generate_report(issues)

            # Update tracking
            self.last_check = datetime.now()
            self.issues_found = issues

            self.logger.info(f"Monitoring cycle complete. Found {len(issues)} issues.")
            return report

        except Exception as e:
            error_msg = f"Error during monitoring: {e}"
            self.logger.error(error_msg)
            return f"❌ {error_msg}"

def main():
    """Main monitoring function"""
    monitor = RepoAutoMonitor()

    print("🔍 ULTRON Agent Auto-Monitor Started")
    print("Monitoring for code quality issues...")
    print("=" * 50)

    while True:
        try:
            report = monitor.run_monitoring_cycle()
            print(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(report)

            # Wait 5 minutes before next check
            print("\n⏰ Waiting 5 minutes for next scan...")
            time.sleep(300)  # 5 minutes

        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
            break
        except Exception as e:
            print(f"❌ Monitoring error: {e}")
            time.sleep(60)  # Wait 1 minute on error

if __name__ == "__main__":
    main()
