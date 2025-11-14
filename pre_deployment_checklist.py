#!/usr/bin/env python3
"""
ULTRON Agent 3.0 - Pre-Deployment Checklist

Performs comprehensive pre-deployment validation before starting services.
Checks configuration, dependencies, connectivity, and resource availability.
"""

import sys
from deployment_validator import DeploymentValidator


class PreDeploymentChecklist:
    """Pre-deployment validation checklist"""

    def __init__(self):
        self.validator = DeploymentValidator()
        self.checks_passed = True

    def run_checklist(self) -> bool:
        """Run complete pre-deployment checklist"""
        print("\n" + "="*80)
        print("PRE-DEPLOYMENT CHECKLIST - ULTRON AGENT 3.0")
        print("="*80 + "\n")

        print("Starting comprehensive pre-deployment validation...")
        print("This process validates all system requirements.\n")

        # Run validator
        success = self.validator.validate_all()

        # Generate checklist report
        self._generate_checklist_report()

        return success

    def _generate_checklist_report(self):
        """Generate detailed checklist report"""
        print("\n" + "="*80)
        print("DEPLOYMENT READINESS REPORT")
        print("="*80 + "\n")

        # Category checks
        categories = {
            'Python & Environment': [
                'Python Version',
                'Python Executable',
                'Virtual Environment'
            ],
            'System Resources': [
                'RAM Available',
                'Disk Space',
                'CPU Cores'
            ],
            'Dependencies': [
                'Critical Dependencies',
                'Core Module Imports'
            ],
            'Configuration': [
                'Configuration File',
                'Configuration Keys',
                'Configuration Values'
            ],
            'Network': [
                'Port Availability',
                'Network Connectivity'
            ],
            'Services': [
                'Ollama Service',
                'API Health Check',
                'Model Availability'
            ],
        }

        for category, checks in categories.items():
            results = [
                r for r in self.validator.results
                if r.check_name in checks
            ]
            passed = sum(1 for r in results if r.status)
            total = len(results)

            status = "[PASS]" if passed == total else "[FAIL]"
            print(f"{status} {category}: {passed}/{total} checks")

            for result in results:
                symbol = "OK" if result.status else "FAIL"
                print(f"    [{symbol}] {result.check_name}")        # Recommendations
        print("\n" + "-"*80)
        print("RECOMMENDATIONS")
        print("-"*80 + "\n")

        if not self.validator.all_passed():
            self._print_recommendations()
        else:
            print("No issues found - system is ready for deployment!\n")

    def _print_recommendations(self):
        """Print recommendations based on validation results"""
        failed = [r for r in self.validator.results if not r.status]

        for result in failed:
            if result.severity == 'critical':
                print(f"CRITICAL: {result.check_name}")
                print(f"  Action required: {result.message}\n")
            elif result.severity == 'warning':
                print(f"WARNING: {result.check_name}")
                print(f"  Recommended action: {result.message}\n")

    def print_next_steps(self):
        """Print next steps for deployment"""
        if self.validator.all_passed():
            print("\n" + "="*80)
            print("NEXT STEPS")
            print("="*80 + "\n")

            print("System validation passed! Ready to proceed with deployment:")
            print("  1. Review deployment guide: DEPLOYMENT_GUIDE.md")
            print("  2. Start services: python main.py")
            print("  3. Access web GUI: http://localhost:8080")
            print("  4. Monitor logs: logs/")
            print("  5. Run health checks: curl http://localhost:5000/health\n")


def main():
    """Main entry point"""
    checklist = PreDeploymentChecklist()
    success = checklist.run_checklist()
    checklist.print_next_steps()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
