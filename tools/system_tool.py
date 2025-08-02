from .base import Tool
import logging
import os
import subprocess
import json

class SystemTool(Tool):
    def __init__(self):
        self.name = "SystemTool"
        self.description = "Control system operations such as opening applications and shutting down."
        super().__init__()

    def match(self, command: str) -> bool:
        cmd = command.lower()
        return "open" in cmd or "shutdown" in cmd or "restart" in cmd or "system info" in cmd

    def execute(self, command: str) -> str:
        command = command.lower()
        if "open" in command:
            app_name = command.replace("open", "").strip()
            return self.open_application(app_name)
        elif "shutdown" in command:
            return self.shutdown_system()
        elif "restart" in command:
            return self.restart_system()
        elif "system info" in command:
            return self.get_system_info()
        return "Unknown system command."

    def get_system_info(self) -> str:
        """Gathers and returns detailed system information."""
        import psutil
        import platform
        import socket
        import uuid

        try:
            info = {}
            # System Information
            info['platform'] = platform.system()
            info['platform_release'] = platform.release()
            info['platform_version'] = platform.version()
            info['architecture'] = platform.machine()
            info['hostname'] = socket.gethostname()
            info['ip_address'] = socket.gethostbyname(socket.gethostname())
            info['mac_address'] = ':'.join(hex(uuid.getnode())[2:].zfill(12)[i:i+2] for i in range(0, 12, 2))
            info['processor'] = platform.processor()
            info['ram'] = f"{psutil.virtual_memory().total / (1024**3):.2f} GB"

            # CPU Information
            info['cpu_cores'] = psutil.cpu_count(logical=False)
            info['cpu_logical_processors'] = psutil.cpu_count(logical=True)
            cpufreq = psutil.cpu_freq()
            info['cpu_max_frequency'] = f"{cpufreq.max:.2f} Mhz"
            info['cpu_min_frequency'] = f"{cpufreq.min:.2f} Mhz"
            info['cpu_current_frequency'] = f"{cpufreq.current:.2f} Mhz"
            info['cpu_usage_per_core'] = [
                f"Core {i}: {percentage}%" for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1))
            ]
            info['total_cpu_usage'] = f"{psutil.cpu_percent()}%"

            # Memory Information
            svmem = psutil.virtual_memory()
            info['total_memory'] = f"{svmem.total / (1024**3):.2f} GB"
            info['available_memory'] = f"{svmem.available / (1024**3):.2f} GB"
            info['used_memory'] = f"{svmem.used / (1024**3):.2f} GB"
            info['memory_percentage'] = f"{svmem.percent}%"

            # Disk Information
            partitions = psutil.disk_partitions()
            disk_info = []
            for partition in partitions:
                try:
                    partition_usage = psutil.disk_usage(partition.mountpoint)
                    disk_info.append(
                        f"Device: {partition.device}, Mountpoint: {partition.mountpoint}, "
                        f"File system type: {partition.fstype}, Total Size: {partition_usage.total / (1024**3):.2f} GB, "
                        f"Used: {partition_usage.used / (1024**3):.2f} GB, Free: {partition_usage.free / (1024**3):.2f} GB, "
                        f"Percentage: {partition_usage.percent}%"
                    )
                except PermissionError:
                    continue
            info['disk_information'] = "\n".join(disk_info)

            # Network Information
            net_io = psutil.net_io_counters()
            info['bytes_sent'] = f"{net_io.bytes_sent / (1024**2):.2f} MB"
            info['bytes_received'] = f"{net_io.bytes_recv / (1024**2):.2f} MB"

            return json.dumps(info, indent=4)

        except Exception as e:
            logging.error(f"Failed to get system info: {e} - system_tool.py:93")
            return f"Error getting system info: {e}"

    def open_application(self, app_name: str) -> str:
        try:
            if os.name == 'nt':  # Windows
                # If opening a Python script, use the specified interpreter
                if app_name.lower().endswith('.py'):
                    subprocess.Popen([r"C:/Python310/python.exe", app_name])
                else:
                    os.startfile(app_name)
            elif os.name == 'posix':  # macOS or Linux
                subprocess.Popen(["open", app_name]) if os.uname().sysname == 'Darwin' else subprocess.Popen([app_name])
            return f"Opened {app_name}."
        except Exception as e:
            logging.error(f"Failed to open application: {e} - system_tool.py:108")
            return f"Error opening {app_name}: {e}"

    def shutdown_system(self) -> str:
        try:
            if os.name == 'nt':  # Windows
                subprocess.call(["shutdown", "/s", "/t", "1"])
            else:  # macOS or Linux
                subprocess.call(["shutdown", "now"])
            return "Shutting down the system."
        except Exception as e:
            logging.error(f"Shutdown failed: {e} - system_tool.py:119")
            return f"Error shutting down the system: {e}"

    def restart_system(self) -> str:
        try:
            if os.name == 'nt':  # Windows
                subprocess.call(["shutdown", "/r", "/t", "1"])
            else:  # macOS or Linux
                subprocess.call(["reboot"])
            return "Restarting the system."
        except Exception as e:
            logging.error(f"Restart failed: {e} - system_tool.py:130")
            return f"Error restarting the system: {e}"
