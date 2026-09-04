from .base import Tool
import logging
import os
import subprocess

class SystemTool(Tool):
    def __init__(self):
        self.name = "SystemTool"
        self.description = "Control system operations such as opening applications and shutting down."
        super().__init__()

    def match(self, command: str) -> bool:
        cmd = command.lower()
        return "open" in cmd or "shutdown" in cmd or "restart" in cmd

    def execute(self, command: str) -> str:
        command = command.lower()
        if "open" in command:
            app_name = command.replace("open", "").strip()
            return self.open_application(app_name)
        elif "shutdown" in command:
            return self.shutdown_system()
        elif "restart" in command:
            return self.restart_system()
        return "Unknown system command."

    def open_application(self, app_name: str) -> str:
        try:
            if os.name == 'nt':  # Windows
                os.startfile(app_name)
            elif os.name == 'posix':  # macOS or Linux
                subprocess.Popen(["open", app_name]) if os.uname().sysname == 'Darwin' else subprocess.Popen([app_name])
            return f"Opened {app_name}."
        except Exception as e:
            logging.error(f"Failed to open application: {e}")
            return f"Error opening {app_name}: {e}"

    def shutdown_system(self) -> str:
        try:
            if os.name == 'nt':  # Windows
                subprocess.call(["shutdown", "/s", "/t", "1"])
            else:  # macOS or Linux
                subprocess.call(["shutdown", "now"])
            return "Shutting down the system."
        except Exception as e:
            logging.error(f"Shutdown failed: {e}")
            return f"Error shutting down the system: {e}"

    def restart_system(self) -> str:
        try:
            if os.name == 'nt':  # Windows
                subprocess.call(["shutdown", "/r", "/t", "1"])
            else:  # macOS or Linux
                subprocess.call(["reboot"])
            return "Restarting the system."
        except Exception as e:
            logging.error(f"Restart failed: {e}")
            return f"Error restarting the system: {e}"