"""
ULTRON System Automation - Advanced System Control and Management
Implements system automation with security and performance monitoring.
"""

import os
import sys
import time
import logging
import asyncio
import subprocess
import psutil
import threading
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import json
import hashlib
import ctypes
from datetime import datetime, timedelta

# Platform specific imports
if sys.platform.startswith('win'):
    try:
        import win32api
        import win32con
        import win32gui
        import win32process
        import win32service
        import win32security
        WIN32_AVAILABLE = True
    except ImportError:
        WIN32_AVAILABLE = False
        logging.warning("Win32 modules not available")
else:
    WIN32_AVAILABLE = False

import pyautogui
import requests

class SystemAutomation:
    """Advanced system automation and control"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger("SystemAutomation")
        
        # Security settings
        self.admin_privileges = self._check_admin_privileges()
        self.trusted_processes = set()
        self.activity_log = []
        
        # Performance monitoring
        self.performance_data = []
        self.monitoring_active = False
        self.monitor_thread = None
        
        # Process management
        self.managed_processes = {}
        self.automation_scripts = {}
        
        # Network monitoring
        self.network_interfaces = []
        self.trusted_mac_addresses = set(config.trusted_mac_addresses)
        
        # Initialize components
        self._initialize_security()
        self._load_automation_scripts()
        
        if config.performance_monitoring:
            self.start_performance_monitoring()
        
        self.logger.info(f"System automation initialized (Admin: {self.admin_privileges})")
    
    def _check_admin_privileges(self) -> bool:
        """Check if running with admin privileges"""
        try:
            if sys.platform.startswith('win'):
                return ctypes.windll.shell32.IsUserAnAdmin()
            else:
                return os.geteuid() == 0
        except Exception as e:
            self.logger.error(f"Admin check error: {e}")
            return False
    
    def _initialize_security(self):
        """Initialize security components"""
        try:
            # Load trusted MAC addresses
            if self.config.security_enabled:
                self._scan_network_interfaces()
                self.logger.info(f"Security enabled - {len(self.trusted_mac_addresses)} trusted MACs")
            
            # Initialize activity logging
            self.activity_log_file = Path("D:/ULTRON/logs/activity.log")
            self.activity_log_file.parent.mkdir(exist_ok=True)
            
        except Exception as e:
            self.logger.error(f"Security initialization error: {e}")
    
    def _scan_network_interfaces(self):
        """Scan and catalog network interfaces"""
        try:
            interfaces = psutil.net_if_addrs()
            self.network_interfaces = []
            
            for interface_name, addresses in interfaces.items():
                for addr in addresses:
                    if addr.family.name == 'AF_PACKET' or 'MAC' in str(addr.family):
                        mac_address = addr.address
                        self.network_interfaces.append({
                            'interface': interface_name,
                            'mac': mac_address,
                            'trusted': mac_address in self.trusted_mac_addresses
                        })
            
            self.logger.info(f"Found {len(self.network_interfaces)} network interfaces")
            
        except Exception as e:
            self.logger.error(f"Network interface scan error: {e}")
    
    def _load_automation_scripts(self):
        """Load automation scripts from config"""
        try:
            scripts_file = Path("D:/ULTRON/automation_scripts.json")
            if scripts_file.exists():
                with open(scripts_file, 'r') as f:
                    self.automation_scripts = json.load(f)
                self.logger.info(f"Loaded {len(self.automation_scripts)} automation scripts")
        except Exception as e:
            self.logger.error(f"Script loading error: {e}")
    
    def start_performance_monitoring(self):
        """Start system performance monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._performance_monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("Performance monitoring started")
    
    def stop_performance_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2)
        self.logger.info("Performance monitoring stopped")
    
    def _performance_monitor_loop(self):
        """Performance monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect system metrics
                metrics = {
                    'timestamp': time.time(),
                    'cpu_percent': psutil.cpu_percent(interval=None),
                    'memory': dict(psutil.virtual_memory()._asdict()),
                    'disk': dict(psutil.disk_usage('/')._asdict()),
                    'network': dict(psutil.net_io_counters()._asdict()),
                    'processes': len(psutil.pids()),
                    'boot_time': psutil.boot_time()
                }
                
                # Add to performance data (keep last 1000 entries)
                self.performance_data.append(metrics)
                if len(self.performance_data) > 1000:
                    self.performance_data.pop(0)
                
                time.sleep(5)  # Monitor every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Performance monitoring error: {e}")
                time.sleep(10)
    
    async def handle_power_command(self, command: str):
        """Handle power management commands"""
        try:
            command = command.lower().strip()
            
            if not self.admin_privileges:
                self.logger.warning("Power commands require admin privileges")
                return {"success": False, "error": "Admin privileges required"}
            
            self.log_activity("power_command", command, "pending")
            
            if "shutdown" in command:
                return await self._shutdown_system()
            elif "restart" in command or "reboot" in command:
                return await self._restart_system()
            elif "sleep" in command:
                return await self._sleep_system()
            elif "hibernate" in command:
                return await self._hibernate_system()
            else:
                return {"success": False, "error": "Unknown power command"}
                
        except Exception as e:
            self.logger.error(f"Power command error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _shutdown_system(self):
        """Shutdown the system"""
        try:
            self.logger.info("Initiating system shutdown...")
            self.log_activity("shutdown", "system", "initiated")
            
            if sys.platform.startswith('win'):
                subprocess.run(["shutdown", "/s", "/t", "30"], check=True)
                return {"success": True, "message": "System shutdown initiated (30 seconds)"}
            else:
                subprocess.run(["sudo", "shutdown", "-h", "+1"], check=True)
                return {"success": True, "message": "System shutdown initiated (1 minute)"}
                
        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _restart_system(self):
        """Restart the system"""
        try:
            self.logger.info("Initiating system restart...")
            self.log_activity("restart", "system", "initiated")
            
            if sys.platform.startswith('win'):
                subprocess.run(["shutdown", "/r", "/t", "30"], check=True)
                return {"success": True, "message": "System restart initiated (30 seconds)"}
            else:
                subprocess.run(["sudo", "reboot"], check=True)
                return {"success": True, "message": "System restart initiated"}
                
        except Exception as e:
            self.logger.error(f"Restart error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _sleep_system(self):
        """Put system to sleep"""
        try:
            self.logger.info("Putting system to sleep...")
            self.log_activity("sleep", "system", "initiated")
            
            if sys.platform.startswith('win'):
                subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], check=True)
                return {"success": True, "message": "System entering sleep mode"}
            else:
                subprocess.run(["sudo", "systemctl", "suspend"], check=True)
                return {"success": True, "message": "System entering sleep mode"}
                
        except Exception as e:
            self.logger.error(f"Sleep error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _hibernate_system(self):
        """Hibernate the system"""
        try:
            self.logger.info("Hibernating system...")
            self.log_activity("hibernate", "system", "initiated")
            
            if sys.platform.startswith('win'):
                subprocess.run(["shutdown", "/h"], check=True)
                return {"success": True, "message": "System hibernating"}
            else:
                subprocess.run(["sudo", "systemctl", "hibernate"], check=True)
                return {"success": True, "message": "System hibernating"}
                
        except Exception as e:
            self.logger.error(f"Hibernate error: {e}")
            return {"success": False, "error": str(e)}
    
    async def manage_process(self, action: str, target: str):
        """Manage system processes"""
        try:
            action = action.lower()
            
            if action == "list":
                return await self._list_processes(target)
            elif action == "kill":
                return await self._kill_process(target)
            elif action == "start":
                return await self._start_process(target)
            elif action == "restart":
                return await self._restart_process(target)
            else:
                return {"success": False, "error": "Unknown process action"}
                
        except Exception as e:
            self.logger.error(f"Process management error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _list_processes(self, filter_name: str = "") -> Dict[str, Any]:
        """List running processes"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                try:
                    info = proc.info
                    if not filter_name or filter_name.lower() in info['name'].lower():
                        processes.append({
                            'pid': info['pid'],
                            'name': info['name'],
                            'cpu_percent': info['cpu_percent'],
                            'memory_mb': info['memory_info'].rss / 1024 / 1024 if info['memory_info'] else 0
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            
            return {
                "success": True,
                "processes": processes[:20],  # Top 20 processes
                "total_count": len(processes)
            }
            
        except Exception as e:
            self.logger.error(f"Process listing error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _kill_process(self, target: str) -> Dict[str, Any]:
        """Kill a process by name or PID"""
        try:
            killed_count = 0
            
            # Try to parse as PID first
            try:
                pid = int(target)
                proc = psutil.Process(pid)
                proc.terminate()
                proc.wait(timeout=5)
                killed_count = 1
                self.log_activity("kill_process", f"PID:{pid}", "success")
            except ValueError:
                # Kill by name
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        if target.lower() in proc.info['name'].lower():
                            proc.terminate()
                            killed_count += 1
                            self.log_activity("kill_process", proc.info['name'], "success")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            
            if killed_count > 0:
                return {"success": True, "message": f"Killed {killed_count} process(es)"}
            else:
                return {"success": False, "error": "No matching processes found"}
                
        except Exception as e:
            self.logger.error(f"Process kill error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _start_process(self, command: str) -> Dict[str, Any]:
        """Start a new process"""
        try:
            # Security check for dangerous commands
            dangerous_commands = ['rm -rf', 'del /f', 'format', 'fdisk']
            if any(cmd in command.lower() for cmd in dangerous_commands):
                self.logger.warning(f"Blocked dangerous command: {command}")
                return {"success": False, "error": "Command blocked for security"}
            
            # Start the process
            if sys.platform.startswith('win'):
                process = subprocess.Popen(command, shell=True)
            else:
                process = subprocess.Popen(command.split())
            
            self.managed_processes[process.pid] = {
                'command': command,
                'start_time': time.time(),
                'process': process
            }
            
            self.log_activity("start_process", command, "success")
            
            return {
                "success": True,
                "pid": process.pid,
                "message": f"Process started with PID {process.pid}"
            }
            
        except Exception as e:
            self.logger.error(f"Process start error: {e}")
            return {"success": False, "error": str(e)}
    
    async def automate_desktop_task(self, task_name: str, parameters: Dict[str, Any] = None):
        """Automate desktop tasks"""
        try:
            if task_name not in self.automation_scripts:
                return {"success": False, "error": f"Task '{task_name}' not found"}
            
            script = self.automation_scripts[task_name]
            result = await self._execute_automation_script(script, parameters or {})
            
            self.log_activity("automation", task_name, "completed")
            return result
            
        except Exception as e:
            self.logger.error(f"Desktop automation error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_automation_script(self, script: Dict[str, Any], parameters: Dict[str, Any]):
        """Execute automation script"""
        try:
            actions = script.get('actions', [])
            
            for action in actions:
                action_type = action.get('type')
                
                if action_type == 'click':
                    x, y = action.get('x', 0), action.get('y', 0)
                    pyautogui.click(x, y)
                    
                elif action_type == 'type':
                    text = action.get('text', '')
                    # Replace parameters
                    for key, value in parameters.items():
                        text = text.replace(f'{{{key}}}', str(value))
                    pyautogui.type(text)
                    
                elif action_type == 'key':
                    key = action.get('key', '')
                    pyautogui.press(key)
                    
                elif action_type == 'wait':
                    duration = action.get('duration', 1)
                    await asyncio.sleep(duration)
                    
                elif action_type == 'screenshot':
                    pyautogui.screenshot()
                
                # Small delay between actions
                await asyncio.sleep(0.1)
            
            return {"success": True, "message": "Automation script completed"}
            
        except Exception as e:
            self.logger.error(f"Automation script error: {e}")
            return {"success": False, "error": str(e)}
    
    def log_activity(self, action_type: str, content: str, result: str):
        """Log system activity"""
        try:
            entry = {
                "timestamp": datetime.now().isoformat(),
                "type": action_type,
                "content": content[:200] + "..." if len(content) > 200 else content,
                "result": result,
                "user": os.getlogin() if hasattr(os, 'getlogin') else "unknown"
            }
            
            self.activity_log.append(entry)
            
            # Write to file
            with open(self.activity_log_file, "a") as f:
                f.write(json.dumps(entry) + "\n")
            
            # Keep only last 1000 entries in memory
            if len(self.activity_log) > 1000:
                self.activity_log.pop(0)
                
        except Exception as e:
            self.logger.error(f"Activity logging error: {e}")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        try:
            # Basic system info
            info = {
                "platform": sys.platform,
                "python_version": sys.version,
                "admin_privileges": self.admin_privileges,
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                "uptime_hours": (time.time() - psutil.boot_time()) / 3600
            }
            
            # CPU info
            info["cpu"] = {
                "count": psutil.cpu_count(),
                "percent": psutil.cpu_percent(interval=1),
                "freq": dict(psutil.cpu_freq()._asdict()) if psutil.cpu_freq() else {}
            }
            
            # Memory info
            memory = psutil.virtual_memory()
            info["memory"] = {
                "total_gb": memory.total / (1024**3),
                "available_gb": memory.available / (1024**3),
                "percent": memory.percent,
                "used_gb": memory.used / (1024**3)
            }
            
            # Disk info
            disk = psutil.disk_usage('/')
            info["disk"] = {
                "total_gb": disk.total / (1024**3),
                "free_gb": disk.free / (1024**3),
                "used_gb": disk.used / (1024**3),
                "percent": (disk.used / disk.total) * 100
            }
            
            # Network info
            info["network"] = {
                "interfaces": len(self.network_interfaces),
                "trusted_macs": len(self.trusted_mac_addresses)
            }
            
            return info
            
        except Exception as e:
            self.logger.error(f"System info error: {e}")
            return {"error": str(e)}
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        try:
            if not self.performance_data:
                return {"error": "No performance data available"}
            
            recent_data = self.performance_data[-60:]  # Last 60 measurements
            
            # Calculate averages
            avg_cpu = sum(d['cpu_percent'] for d in recent_data) / len(recent_data)
            avg_memory = sum(d['memory']['percent'] for d in recent_data) / len(recent_data)
            
            return {
                "monitoring_active": self.monitoring_active,
                "data_points": len(self.performance_data),
                "recent_avg_cpu": round(avg_cpu, 2),
                "recent_avg_memory": round(avg_memory, 2),
                "current_processes": recent_data[-1]['processes'] if recent_data else 0,
                "uptime_hours": round((time.time() - psutil.boot_time()) / 3600, 2)
            }
            
        except Exception as e:
            self.logger.error(f"Performance metrics error: {e}")
            return {"error": str(e)}
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get security status"""
        try:
            return {
                "security_enabled": self.config.security_enabled,
                "admin_privileges": self.admin_privileges,
                "trusted_mac_count": len(self.trusted_mac_addresses),
                "network_interfaces": len(self.network_interfaces),
                "activity_log_entries": len(self.activity_log),
                "managed_processes": len(self.managed_processes),
                "automation_scripts": len(self.automation_scripts)
            }
            
        except Exception as e:
            self.logger.error(f"Security status error: {e}")
            return {"error": str(e)}
    
    async def cleanup_managed_processes(self):
        """Clean up managed processes"""
        try:
            for pid, proc_info in list(self.managed_processes.items()):
                try:
                    process = proc_info['process']
                    if process.poll() is not None:  # Process has finished
                        del self.managed_processes[pid]
                        self.logger.info(f"Cleaned up finished process PID {pid}")
                except Exception as e:
                    self.logger.error(f"Process cleanup error for PID {pid}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Process cleanup error: {e}")
