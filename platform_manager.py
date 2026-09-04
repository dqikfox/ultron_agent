"""
ULTRON Agent 3.0 - Multi-Platform Support Manager
Provides platform-specific features and compatibility
across Windows, macOS, and Linux
"""

import platform
import sys
from typing import Dict, Any, List
from pathlib import Path


class PlatformManager:
    """
    Manages platform-specific operations and provides unified interface
    across Windows, macOS, Linux, and mobile platforms
    """

    def __init__(self):
        self.system = platform.system().lower()
        self.release = platform.release()
        self.version = platform.version()
        self.machine = platform.machine()
        self.processor = platform.processor()

        # Platform-specific configurations
        self.platform_config = self._load_platform_config()

    def _load_platform_config(self) -> Dict[str, Any]:
        """Load platform-specific configuration"""
        base_config = {
            "supported_platforms": ["windows", "darwin", "linux"],
            "mobile_platforms": ["ios", "android"],
            "features": {
                "voice_synthesis": True,
                "speech_recognition": True,
                "file_operations": True,
                "network_operations": True,
                "system_monitoring": True
            }
        }

        # Windows-specific config
        if self.system == "windows":
            base_config.update({
                "path_separator": "\\",
                "line_ending": "\r\n",
                "default_shell": "cmd.exe",
                "powershell_available": self._check_powershell(),
                "wsl_available": self._check_wsl(),
                "features": {
                    **base_config["features"],
                    "windows_specific": True,
                    "registry_access": True,
                    "task_scheduler": True
                }
            })

        # macOS-specific config
        elif self.system == "darwin":
            base_config.update({
                "path_separator": "/",
                "line_ending": "\n",
                "default_shell": "/bin/bash",
                "homebrew_available": self._check_homebrew(),
                "features": {
                    **base_config["features"],
                    "macos_specific": True,
                    "spotlight_search": True,
                    "notification_center": True
                }
            })

        # Linux-specific config
        elif self.system == "linux":
            base_config.update({
                "path_separator": "/",
                "line_ending": "\n",
                "default_shell": "/bin/bash",
                "package_manager": self._detect_package_manager(),
                "features": {
                    **base_config["features"],
                    "linux_specific": True,
                    "systemd_services": True,
                    "cron_jobs": True
                }
            })

        return base_config

    def _check_powershell(self) -> bool:
        """Check if PowerShell is available on Windows"""
        try:
            import subprocess
            result = subprocess.run(
                ["powershell", "-Command", "Write-Host 'test'"],
                capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError,
                subprocess.SubprocessError):
            return False

    def _check_wsl(self) -> bool:
        """Check if WSL is available on Windows"""
        try:
            import subprocess
            result = subprocess.run(
                ["wsl", "--list"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError,
                subprocess.SubprocessError):
            return False

    def _check_homebrew(self) -> bool:
        """Check if Homebrew is available on macOS"""
        try:
            import subprocess
            result = subprocess.run(
                ["brew", "--version"],
                capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError,
                subprocess.SubprocessError):
            return False

    def _detect_package_manager(self) -> str:
        """Detect the package manager on Linux"""
        package_managers = ["apt", "yum", "dnf", "pacman", "zypper"]

        for pm in package_managers:
            try:
                import subprocess
                result = subprocess.run(
                    [pm, "--version"],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    return pm
            except (subprocess.TimeoutExpired, FileNotFoundError,
                    subprocess.SubprocessError):
                continue

        return "unknown"

    def get_platform_info(self) -> Dict[str, Any]:
        """Get comprehensive platform information"""
        return {
            "system": self.system,
            "release": self.release,
            "version": self.version,
            "machine": self.machine,
            "processor": self.processor,
            "python_version": sys.version,
            "platform_config": self.platform_config
        }

    def is_supported_platform(self) -> bool:
        """Check if the current platform is supported"""
        return self.system in self.platform_config["supported_platforms"]

    def get_platform_specific_features(self) -> List[str]:
        """Get list of platform-specific features available"""
        features = []
        for feature, available in self.platform_config.get(
            "features", {}
        ).items():
            if available:
                features.append(feature)
        return features

    def get_path_separator(self) -> str:
        """Get the platform-specific path separator"""
        return self.platform_config.get("path_separator", "/")

    def get_line_ending(self) -> str:
        """Get the platform-specific line ending"""
        return self.platform_config.get("line_ending", "\n")

    def get_default_shell(self) -> str:
        """Get the default shell for the platform"""
        return self.platform_config.get("default_shell", "/bin/bash")

    def execute_platform_command(
        self, command: str, **kwargs
    ) -> Dict[str, Any]:
        """
        Execute a command with platform-specific handling

        Args:
            command: Command to execute
            **kwargs: Additional arguments for subprocess.run

        Returns:
            Dictionary with execution results
        """
        try:
            import subprocess

            # Platform-specific command adjustments
            if (self.system == "windows" and
                    not command.startswith("powershell")):
                # Use cmd.exe for Windows commands
                cmd_args = ["cmd.exe", "/c", command]
            else:
                # Use shell for other platforms
                cmd_args = [self.get_default_shell(), "-c", command]

            result = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
                timeout=kwargs.get("timeout", 30),
                **{k: v for k, v in kwargs.items() if k != "timeout"}
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": command,
                "platform": self.system
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out",
                "command": command,
                "platform": self.system
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": command,
                "platform": self.system
            }

    def get_platform_recommendations(self) -> List[str]:
        """Get platform-specific setup recommendations"""
        recommendations = []

        if self.system == "windows":
            if not self.platform_config.get("powershell_available"):
                recommendations.append(
                    "Install PowerShell for enhanced Windows integration"
                )
            if not self.platform_config.get("wsl_available"):
                recommendations.append(
                    "Consider installing WSL for Linux compatibility"
                )

        elif self.system == "darwin":
            if not self.platform_config.get("homebrew_available"):
                recommendations.append(
                    "Install Homebrew for package management"
                )

        elif self.system == "linux":
            pm = self.platform_config.get("package_manager", "unknown")
            if pm == "unknown":
                recommendations.append(
                    "Install a package manager (apt, yum, dnf, etc.)"
                )

        return recommendations

    def normalize_path(self, path_str: str) -> str:
        """Normalize a path for the current platform"""
        return str(Path(path_str))

    def get_user_home_directory(self) -> str:
        """Get the user's home directory in a platform-independent way"""
        return str(Path.home())

    def get_platform_startup_methods(self) -> List[str]:
        """Get available methods to start applications on startup"""
        methods = []

        if self.system == "windows":
            methods.extend([
                "Windows Registry (Run key)",
                "Task Scheduler",
                "Startup folder"
            ])

        elif self.system == "darwin":
            methods.extend([
                "Launch Agents",
                "Login Items",
                "cron jobs"
            ])

        elif self.system == "linux":
            methods.extend([
                "systemd user services",
                "cron jobs",
                ".bashrc or .profile",
                "desktop environment autostart"
            ])

        return methods

    def is_mobile_platform(self) -> bool:
        """Check if running on a mobile platform"""
        return self.system in self.platform_config.get("mobile_platforms", [])

    def get_memory_info(self) -> Dict[str, Any]:
        """Get platform-specific memory information"""
        try:
            import psutil
            memory = psutil.virtual_memory()

            return {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "percentage": memory.percent,
                "platform": self.system
            }
        except ImportError:
            return {"error": "psutil not available for memory monitoring"}

    def get_disk_info(self) -> Dict[str, Any]:
        """Get platform-specific disk information"""
        try:
            import psutil
            disks = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disks.append({
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percentage": usage.percent
                    })
                except PermissionError:
                    continue

            return {
                "disks": disks,
                "platform": self.system
            }
        except ImportError:
            return {"error": "psutil not available for disk monitoring"}

    def get_network_info(self) -> Dict[str, Any]:
        """Get platform-specific network information"""
        try:
            import psutil
            network = psutil.net_if_addrs()
            connections = psutil.net_connections()

            interfaces = {}
            for interface, addresses in network.items():
                interfaces[interface] = [
                    {
                        "family": (
                            addr.family.name if hasattr(addr.family, 'name')
                            else str(addr.family)
                        ),
                        "address": addr.address,
                        "netmask": addr.netmask,
                        "broadcast": addr.broadcast
                    }
                    for addr in addresses
                ]

            return {
                "interfaces": interfaces,
                "connections_count": len(connections),
                "platform": self.system
            }
        except ImportError:
            return {"error": "psutil not available for network monitoring"}
