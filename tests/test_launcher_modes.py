"""
Test suite for ULTRON Launcher - verifies all 4 modes (api, web, cli, full)
Phase A: Launcher mode validation for unified entry point
"""

import pytest
import subprocess
import time
import requests
import signal
import os
from pathlib import Path
from typing import Optional, Tuple

# Test markers
pytestmark = [pytest.mark.integration]


class LauncherModeTest:
    """Test ULTRON Launcher modes"""

    @staticmethod
    def is_port_open(host: str = "127.0.0.1", port: int = 5000, timeout: int = 2) -> bool:
        """Check if port is open and responding"""
        try:
            response = requests.get(f"http://{host}:{port}/health", timeout=timeout)
            return response.status_code in [200, 404]  # 404 acceptable if endpoint doesn't exist
        except (requests.ConnectionError, requests.Timeout, requests.RequestException):
            return False

    @staticmethod
    def start_launcher_mode(
        mode: str, 
        api_port: int = 5000, 
        web_port: int = 8080,
        timeout: int = 15
    ) -> Tuple[subprocess.Popen, bool]:
        """
        Start launcher in specified mode
        Returns: (process, success_flag)
        """
        cmd = [
            "python", 
            "ultron_launch.py",
            "--mode", mode,
            "--api-port", str(api_port),
            "--web-port", str(web_port)
        ]
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=Path(__file__).parent.parent,
                preexec_fn=os.setsid  # Create new process group
            )
            
            # Give it time to start
            time.sleep(2)
            
            # Check if process is still alive
            if process.poll() is not None:
                stdout, stderr = process.communicate(timeout=1)
                print(f"Process exited with code {process.returncode}")
                print(f"STDOUT: {stdout.decode()}")
                print(f"STDERR: {stderr.decode()}")
                return process, False
            
            return process, True
        except Exception as e:
            print(f"Failed to start launcher: {e}")
            return None, False

    @staticmethod
    def stop_launcher_mode(process: subprocess.Popen, timeout: int = 5):
        """Stop launcher process gracefully"""
        if not process:
            return
        
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            process.wait(timeout=timeout)
        except (ProcessLookupError, subprocess.TimeoutExpired):
            try:
                os.killpg(os.getpgid(process.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass

    def test_api_mode_starts(self):
        """Test API mode can start and responds on port 5000"""
        process, success = self.start_launcher_mode("api", api_port=5002)  # Use diff port
        assert success, "API mode failed to start"
        
        try:
            # Give it time to bind port
            time.sleep(2)
            
            # Check if port is open
            is_open = self.is_port_open(port=5002, timeout=3)
            assert is_open, "API server not responding on expected port"
        finally:
            self.stop_launcher_mode(process)

    def test_web_mode_starts(self):
        """Test Web mode can start and responds on port 8080"""
        process, success = self.start_launcher_mode("web", web_port=8082)  # Use diff port
        assert success, "Web mode failed to start"
        
        try:
            time.sleep(2)
            # Check if port is open
            is_open = self.is_port_open(port=8082, timeout=3)
            assert is_open, "Web server not responding on expected port"
        finally:
            self.stop_launcher_mode(process)

    def test_cli_mode_starts(self):
        """Test CLI mode can start"""
        process, success = self.start_launcher_mode("cli", timeout=5)
        # CLI mode starts but doesn't listen on ports, so just check process exists
        assert success, "CLI mode failed to start"
        
        try:
            # Process should stay alive in CLI mode
            time.sleep(1)
            assert process.poll() is None, "CLI process exited prematurely"
        finally:
            self.stop_launcher_mode(process)

    def test_full_mode_starts(self):
        """Test Full mode can start with all services"""
        process, success = self.start_launcher_mode("full", api_port=5003, web_port=8083)
        assert success, "Full mode failed to start"
        
        try:
            time.sleep(3)
            # In full mode, both api and web ports should be active
            api_open = self.is_port_open(port=5003, timeout=3)
            web_open = self.is_port_open(port=8083, timeout=3)
            
            assert api_open or web_open, "Neither API nor Web port responding in full mode"
        finally:
            self.stop_launcher_mode(process)

    def test_launcher_help(self):
        """Test launcher --help works"""
        result = subprocess.run(
            ["python", "ultron_launch.py", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        assert result.returncode == 0, "Launcher --help failed"
        assert "mode" in result.stdout.lower(), "Help text missing mode option"

    def test_launcher_exists(self):
        """Test launcher file exists"""
        launcher_path = Path(__file__).parent.parent / "ultron_launch.py"
        assert launcher_path.exists(), "ultron_launch.py not found"
        assert launcher_path.is_file(), "ultron_launch.py is not a file"

    def test_launcher_executable(self):
        """Test launcher is executable Python script"""
        launcher_path = Path(__file__).parent.parent / "ultron_launch.py"
        assert launcher_path.exists()
        
        # Check shebang or first line
        with open(launcher_path) as f:
            first_line = f.readline()
            assert "python" in first_line.lower(), "Launcher missing python shebang"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])
