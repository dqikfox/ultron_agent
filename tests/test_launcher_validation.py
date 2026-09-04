"""
Unit test validation for ULTRON Launcher structure and configuration
Phase A: Launcher validation (no server startup needed)
"""

import pytest
from pathlib import Path
import subprocess
import sys


class TestLauncherValidation:
    """Validate launcher structure, arguments, and basic functionality"""

    def test_launcher_file_exists(self):
        """Test ultron_launch.py exists"""
        launcher = Path(__file__).parent.parent / "ultron_launch.py"
        assert launcher.exists()
        assert launcher.is_file()

    def test_launcher_is_valid_python(self):
        """Test launcher is valid Python syntax"""
        launcher = Path(__file__).parent.parent / "ultron_launch.py"
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(launcher)],
            capture_output=True
        )
        assert result.returncode == 0, f"Launcher syntax error: {result.stderr.decode()}"

    def test_launcher_help_works(self):
        """Test launcher --help returns proper usage info"""
        launcher = Path(__file__).parent.parent / "ultron_launch.py"
        result = subprocess.run(
            [sys.executable, str(launcher), "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "mode" in result.stdout.lower()
        assert "api" in result.stdout
        assert "web" in result.stdout
        assert "cli" in result.stdout
        assert "full" in result.stdout

    def test_launcher_api_mode_supported(self):
        """Test launcher supports --mode api"""
        launcher = Path(__file__).parent.parent / "ultron_launch.py"
        result = subprocess.run(
            [sys.executable, str(launcher), "--help"],
            capture_output=True,
            text=True
        )
        assert "api" in result.stdout

    def test_launcher_web_mode_supported(self):
        """Test launcher supports --mode web"""
        launcher = Path(__file__).parent.parent / "ultron_launch.py"
        result = subprocess.run(
            [sys.executable, str(launcher), "--help"],
            capture_output=True,
            text=True
        )
        assert "web" in result.stdout

    def test_launcher_cli_mode_supported(self):
        """Test launcher supports --mode cli"""
        launcher = Path(__file__).parent.parent / "ultron_launch.py"
        result = subprocess.run(
            [sys.executable, str(launcher), "--help"],
            capture_output=True,
            text=True
        )
        assert "cli" in result.stdout

    def test_launcher_full_mode_supported(self):
        """Test launcher supports --mode full"""
        launcher = Path(__file__).parent.parent / "ultron_launch.py"
        result = subprocess.run(
            [sys.executable, str(launcher), "--help"],
            capture_output=True,
            text=True
        )
        assert "full" in result.stdout

    def test_launcher_port_arguments(self):
        """Test launcher supports port configuration"""
        launcher = Path(__file__).parent.parent / "ultron_launch.py"
        result = subprocess.run(
            [sys.executable, str(launcher), "--help"],
            capture_output=True,
            text=True
        )
        assert "api-port" in result.stdout
        assert "web-port" in result.stdout

    def test_launcher_host_argument(self):
        """Test launcher supports host configuration"""
        launcher = Path(__file__).parent.parent / "ultron_launch.py"
        result = subprocess.run(
            [sys.executable, str(launcher), "--help"],
            capture_output=True,
            text=True
        )
        assert "host" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
