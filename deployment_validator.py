#!/usr/bin/env python3
"""
ULTRON Agent 3.0 - Comprehensive Deployment Validator

Validates all system requirements for production deployment:
- Python version and environment
- Dependencies and packages
- System resources (RAM, disk, CPU)
- Network connectivity
- Port availability
- Configuration integrity
- Database connectivity
- API endpoint health
- Model availability
"""

import os
import sys
import json
import socket
import psutil
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ValidationResult:
    """Container for validation check result"""
    check_name: str
    status: bool  # True = pass, False = fail
    message: str
    severity: str  # 'critical', 'warning', 'info'

    def __str__(self):
        symbol = "[PASS]" if self.status else "[FAIL]"
        return f"{symbol} {self.check_name}: {self.message}"
class DeploymentValidator:
    """Comprehensive deployment validator"""

    def __init__(self, config_path: str = "ultron_config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.results: List[ValidationResult] = []
        self.start_time = datetime.now()

    def _load_config(self) -> Dict:
        """Load configuration file"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {}

    def add_result(self, result: ValidationResult):
        """Add validation result"""
        self.results.append(result)
        print(f"  {result}")

    def validate_all(self) -> bool:
        """Run all validation checks"""
        print("\n" + "="*80)
        print("ULTRON AGENT 3.0 - DEPLOYMENT VALIDATOR")
        print("="*80 + "\n")

        # Part 1: Python & Environment
        print("[1/7] PYTHON & ENVIRONMENT")
        print("-" * 80)
        self.validate_python_version()
        self.validate_python_executable()
        self.validate_virtual_environment()

        # Part 2: System Resources
        print("\n[2/7] SYSTEM RESOURCES")
        print("-" * 80)
        self.validate_ram()
        self.validate_disk_space()
        self.validate_cpu_cores()

        # Part 3: Dependencies
        print("\n[3/7] DEPENDENCIES")
        print("-" * 80)
        self.validate_dependencies()
        self.validate_imports()

        # Part 4: Configuration
        print("\n[4/7] CONFIGURATION")
        print("-" * 80)
        self.validate_config_file()
        self.validate_config_keys()
        self.validate_config_values()

        # Part 5: Network & Ports
        print("\n[5/7] NETWORK & PORTS")
        print("-" * 80)
        self.validate_port_availability()
        self.validate_network_connectivity()

        # Part 6: Services & APIs
        print("\n[6/7] SERVICES & APIs")
        print("-" * 80)
        self.validate_ollama_connection()
        self.validate_api_endpoints()

        # Part 7: Model Availability
        print("\n[7/7] MODEL AVAILABILITY")
        print("-" * 80)
        self.validate_models()

        # Summary
        self.print_summary()

        return self.all_passed()

    # ==================== VALIDATION CHECKS ====================

    def validate_python_version(self):
        """Check Python version (3.10+)"""
        major, minor = sys.version_info[:2]
        version_str = f"{major}.{minor}.{sys.version_info[2]}"

        if major == 3 and minor >= 10:
            self.add_result(ValidationResult(
                "Python Version",
                True,
                f"Python {version_str} (OK 3.10+ required)",
                "info"
            ))
        else:
            self.add_result(ValidationResult(
                "Python Version",
                False,
                f"Python {version_str} (ERR 3.10+ required)",
                "critical"
            ))

    def validate_python_executable(self):
        """Check Python executable path"""
        exe = sys.executable
        exists = Path(exe).exists()

        self.add_result(ValidationResult(
            "Python Executable",
            exists,
            f"{exe}",
            "critical" if not exists else "info"
        ))

    def validate_virtual_environment(self):
        """Check if running in virtual environment"""
        in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )

        self.add_result(ValidationResult(
            "Virtual Environment",
            in_venv,
            f"Prefix: {sys.prefix}" if in_venv else "Not in venv (warning)",
            "warning" if not in_venv else "info"
        ))

    def validate_ram(self):
        """Check available RAM (minimum 2GB)"""
        total_gb = psutil.virtual_memory().total / (1024**3)
        available_gb = psutil.virtual_memory().available / (1024**3)
        min_gb = 2

        status = available_gb >= min_gb
        self.add_result(ValidationResult(
            "RAM Available",
            status,
            f"{available_gb:.1f}GB available, {total_gb:.1f}GB total (min {min_gb}GB)",
            "critical" if not status else "info"
        ))

    def validate_disk_space(self):
        """Check available disk space (minimum 1GB)"""
        cwd = Path.cwd()
        min_gb = 1

        try:
            if hasattr(os, 'statvfs'):
                # Unix-like systems
                stat = os.statvfs(str(cwd))
                available_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
            else:
                # Windows systems
                import shutil
                stat = shutil.disk_usage(str(cwd))
                available_gb = stat.free / (1024**3)

            status = available_gb >= min_gb
            self.add_result(ValidationResult(
                "Disk Space",
                status,
                f"{available_gb:.1f}GB available (min {min_gb}GB)",
                "critical" if not status else "info"
            ))
        except Exception as e:
            self.add_result(ValidationResult(
                "Disk Space",
                False,
                f"Error checking disk space: {e}",
                "warning"
            ))

    def validate_cpu_cores(self):
        """Check CPU cores (minimum 2)"""
        cores = psutil.cpu_count(logical=False)
        logical_cores = psutil.cpu_count(logical=True)
        min_cores = 2

        status = cores >= min_cores
        self.add_result(ValidationResult(
            "CPU Cores",
            status,
            f"{cores} physical, {logical_cores} logical (min {min_cores} required)",
            "warning" if not status else "info"
        ))

    def validate_dependencies(self) -> bool:
        """Check critical dependencies"""
        critical_packages = [
            'pytest', 'aiohttp', 'flask', 'psutil', 'requests'
        ]

        missing = []
        for package in critical_packages:
            try:
                __import__(package)
            except ImportError:
                missing.append(package)

        status = len(missing) == 0
        message = "All dependencies installed" if status else f"Missing: {', '.join(missing)}"

        self.add_result(ValidationResult(
            "Critical Dependencies",
            status,
            message,
            "critical" if not status else "info"
        ))

        return status

    def validate_imports(self) -> bool:
        """Test importing core modules"""
        modules = [
            'utils.task_scheduler',
            'utils.security_utils',
            'utils.dynamic_loader',
            'utils.ultron_logger',
        ]

        failed = []
        for module in modules:
            try:
                __import__(module)
            except ImportError as e:
                failed.append(f"{module}: {e}")

        status = len(failed) == 0
        message = "All core modules importable" if status else f"Failed: {len(failed)}"

        self.add_result(ValidationResult(
            "Core Module Imports",
            status,
            message,
            "critical" if not status else "info"
        ))

        return status

    def validate_config_file(self) -> bool:
        """Check configuration file exists and is valid"""
        exists = self.config_path.exists()
        valid_json = False

        if exists:
            try:
                json.loads(self.config_path.read_text())
                valid_json = True
            except json.JSONDecodeError:
                pass

        status = exists and valid_json
        message = f"Config file valid" if status else f"Config file {self.config_path} invalid or missing"

        self.add_result(ValidationResult(
            "Configuration File",
            status,
            message,
            "critical" if not status else "info"
        ))

        return status

    def validate_config_keys(self) -> bool:
        """Check required configuration keys"""
        required_keys = [
            'llm_model',
            'ollama_base_url',
            'api_port',
            'web_gui_port',
        ]

        missing = [k for k in required_keys if k not in self.config]
        status = len(missing) == 0
        message = "All required keys present" if status else f"Missing: {', '.join(missing)}"

        self.add_result(ValidationResult(
            "Configuration Keys",
            status,
            message,
            "critical" if not status else "info"
        ))

        return status

    def validate_config_values(self) -> bool:
        """Validate configuration values"""
        warnings = []

        # Check LLM model
        model = self.config.get('llm_model', 'unknown')
        if model not in ['dolphin3:latest', 'llava:7b', 'llama3.1', 'deepseek-r1:14b', 'qwen3-coder:480b-cloud']:
            warnings.append(f"Unusual model: {model}")

        # Check ports
        api_port = self.config.get('api_port', 5000)
        if not (1024 <= api_port <= 65535):
            warnings.append(f"Invalid API port: {api_port}")

        status = len(warnings) == 0
        message = "All values valid" if status else f"Warnings: {'; '.join(warnings)}"

        self.add_result(ValidationResult(
            "Configuration Values",
            status,
            message,
            "warning" if not status else "info"
        ))

        return status

    def validate_port_availability(self) -> bool:
        """Check if required ports are available"""
        ports = {
            'API': self.config.get('api_port', 5000),
            'Web GUI': self.config.get('web_gui_port', 8080),
            'Ollama': 11434,
            'Chat': self.config.get('chat_port', 8000),
        }

        unavailable = []
        for name, port in ports.items():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                if result == 0:
                    unavailable.append(f"{name}:{port}")
            except Exception:
                pass

        status = len(unavailable) == 0
        message = "All ports available" if status else f"In use: {', '.join(unavailable)}"

        self.add_result(ValidationResult(
            "Port Availability",
            status,
            message,
            "warning" if not status else "info"
        ))

        return status

    def validate_network_connectivity(self) -> bool:
        """Check network connectivity"""
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            self.add_result(ValidationResult(
                "Network Connectivity",
                True,
                "Internet connectivity verified",
                "info"
            ))
            return True
        except Exception as e:
            self.add_result(ValidationResult(
                "Network Connectivity",
                False,
                f"Network error: {e}",
                "warning"
            ))
            return False

    def validate_ollama_connection(self) -> bool:
        """Check Ollama service connection"""
        ollama_url = self.config.get('ollama_base_url', 'http://localhost:11434')

        try:
            import aiohttp
            import asyncio

            async def check():
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{ollama_url}/api/tags", timeout=5) as resp:
                        return resp.status == 200

            # Try sync approach first
            try:
                import requests
                resp = requests.get(f"{ollama_url}/api/tags", timeout=5)
                status = resp.status_code == 200
            except Exception:
                status = False

            message = f"Ollama responding at {ollama_url}" if status else f"Ollama not responding at {ollama_url}"
            self.add_result(ValidationResult(
                "Ollama Service",
                status,
                message,
                "critical" if not status else "info"
            ))

            return status
        except Exception as e:
            self.add_result(ValidationResult(
                "Ollama Service",
                False,
                f"Error connecting to Ollama: {e}",
                "critical"
            ))
            return False

    def validate_api_endpoints(self) -> bool:
        """Check API endpoint health"""
        api_port = self.config.get('api_port', 5000)
        base_url = f"http://localhost:{api_port}"

        try:
            import requests
            resp = requests.get(f"{base_url}/health", timeout=5)
            status = resp.status_code == 200

            message = f"API responding at {base_url}" if status else f"API not responding at {base_url}"
            self.add_result(ValidationResult(
                "API Health Check",
                status,
                message,
                "warning" if not status else "info"
            ))

            return status
        except Exception as e:
            self.add_result(ValidationResult(
                "API Health Check",
                False,
                f"API not accessible: {e}",
                "warning"  # Warning, not critical (API may not be running yet)
            ))
            return False

    def validate_models(self) -> bool:
        """Check model availability"""
        ollama_url = self.config.get('ollama_base_url', 'http://localhost:11434')
        default_model = self.config.get('llm_model', 'dolphin3:latest')

        try:
            import requests
            resp = requests.get(f"{ollama_url}/api/tags", timeout=5)

            if resp.status_code == 200:
                models = resp.json().get('models', [])
                model_names = [m.get('name', '') for m in models]

                has_model = any(default_model in name for name in model_names)
                message = f"Found {len(models)} models" if models else "No models found"

                self.add_result(ValidationResult(
                    "Model Availability",
                    has_model or len(models) > 0,
                    message,
                    "warning" if not has_model else "info"
                ))

                return has_model
            else:
                self.add_result(ValidationResult(
                    "Model Availability",
                    False,
                    f"Failed to query models (status {resp.status_code})",
                    "warning"
                ))
                return False
        except Exception as e:
            self.add_result(ValidationResult(
                "Model Availability",
                False,
                f"Cannot check models: {e}",
                "warning"
            ))
            return False

    # ==================== REPORTING ====================

    def all_passed(self) -> bool:
        """Check if all critical checks passed"""
        critical_failed = [r for r in self.results if r.severity == 'critical' and not r.status]
        return len(critical_failed) == 0

    def print_summary(self):
        """Print validation summary"""
        print("\n" + "="*80)
        print("VALIDATION SUMMARY")
        print("="*80)

        total = len(self.results)
        passed = sum(1 for r in self.results if r.status)
        failed = total - passed

        critical_failed = [r for r in self.results if r.severity == 'critical' and not r.status]
        warnings = [r for r in self.results if r.severity == 'warning' and not r.status]

        print(f"\nTotal Checks:      {total}")
        print(f"Passed:            {passed}")
        print(f"Failed:            {failed}")
        print(f"Critical Issues:   {len(critical_failed)}")
        print(f"Warnings:          {len(warnings)}")

        if critical_failed:
            print("\n[CRITICAL ISSUES]:")
            for result in critical_failed:
                print(f"  - {result.check_name}: {result.message}")

        if warnings:
            print("\n[WARNINGS]:")
            for result in warnings:
                print(f"  - {result.check_name}: {result.message}")

        elapsed = (datetime.now() - self.start_time).total_seconds()
        status = "OK: READY FOR DEPLOYMENT" if self.all_passed() else "FAIL: DEPLOYMENT BLOCKED"

        print(f"\n{status}")
        print(f"Validation time: {elapsed:.2f}s")
        print("="*80 + "\n")


def main():
    """Main entry point"""
    validator = DeploymentValidator()
    success = validator.validate_all()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
