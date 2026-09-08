"""System control and automation"""
import psutil
import subprocess
import os
import logging
from datetime import datetime

class SystemControl:
    def __init__(self, config):
        self.config = config['system']
        self.admin_mode = self.check_admin()
        self.available = True
    
    def check_admin(self):
        try:
            if os.name == 'nt':  # Windows
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin()
            else:
                return os.geteuid() == 0
        except:
            return False
    
    async def get_status(self):
        try:
            return {
                "cpu": psutil.cpu_percent(interval=1),
                "memory": psutil.virtual_memory().percent,
                "disk": psutil.disk_usage('/').percent,
                "admin": self.admin_mode,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logging.error(f"System status error: {e}")
            return {"error": str(e)}
    
    async def launch_application(self, app_name):
        safe_apps = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "paint": "mspaint.exe",
            "cmd": "cmd.exe",
            "browser": "start chrome"
        }
        
        app_lower = app_name.lower()
        if app_lower in safe_apps:
            try:
                if os.name == 'nt':
                    subprocess.Popen(safe_apps[app_lower], shell=True)
                else:
                    subprocess.Popen(app_lower, shell=True)
                return {"success": True, "message": f"Launched {app_name}"}
            except Exception as e:
                return {"success": False, "message": f"Failed to launch {app_name}: {e}"}
        else:
            return {"success": False, "message": f"Application '{app_name}' not in safe list"}
    
    async def shutdown(self):
        if self.admin_mode:
            try:
                if os.name == 'nt':
                    subprocess.run(["shutdown", "/s", "/t", "10"], check=True)
                else:
                    subprocess.run(["sudo", "shutdown", "-h", "now"], check=True)
                return True
            except Exception as e:
                logging.error(f"Shutdown error: {e}")
        return False
    
    async def restart(self):
        if self.admin_mode:
            try:
                if os.name == 'nt':
                    subprocess.run(["shutdown", "/r", "/t", "10"], check=True)
                else:
                    subprocess.run(["sudo", "reboot"], check=True)
                return True
            except Exception as e:
                logging.error(f"Restart error: {e}")
        return False
    
    async def sleep(self):
        try:
            if os.name == 'nt':
                subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], check=True)
            else:
                subprocess.run(["systemctl", "suspend"], check=True)
            return True
        except Exception as e:
            logging.error(f"Sleep error: {e}")
            return False
    
    def is_available(self):
        return self.available
