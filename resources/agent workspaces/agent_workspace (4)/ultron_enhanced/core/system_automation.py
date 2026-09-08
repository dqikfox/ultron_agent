"""
ULTRON Enhanced - System Automation Module
Advanced system control and automation capabilities
"""

import os
import sys
import json
import time
import psutil
import subprocess
import threading
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging
import ctypes
from datetime import datetime, timedelta

class SystemAutomation:
    """Advanced system automation and control"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.is_admin = self._check_admin_privileges()
        self.automation_tasks = []
        self.scheduled_tasks = {}
        self.system_monitor = SystemMonitor()
        self.process_manager = ProcessManager()
        self.file_manager = FileManager()
        
        logging.info(f"System automation initialized (Admin: {self.is_admin})")
    
    def _check_admin_privileges(self) -> bool:
        """Check if running with administrator privileges"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def execute_command(self, command_type: str, command_data: Dict) -> Dict:
        """Execute system automation command"""
        try:
            if command_type == "power_control":
                return self._handle_power_control(command_data)
            elif command_type == "process_control":
                return self._handle_process_control(command_data)
            elif command_type == "file_operation":
                return self._handle_file_operation(command_data)
            elif command_type == "system_info":
                return self._handle_system_info(command_data)
            elif command_type == "automation_task":
                return self._handle_automation_task(command_data)
            elif command_type == "scheduled_task":
                return self._handle_scheduled_task(command_data)
            else:
                return {
                    "success": False,
                    "message": f"Unknown command type: {command_type}"
                }
        except Exception as e:
            logging.error(f"Command execution error: {e}")
            return {
                "success": False,
                "message": f"Command execution failed: {str(e)}"
            }
    
    def _handle_power_control(self, data: Dict) -> Dict:
        """Handle power control commands"""
        action = data.get("action", "").lower()
        
        if not self.is_admin:
            return {
                "success": False,
                "message": "Administrator privileges required for power control"
            }
        
        try:
            if action == "shutdown":
                subprocess.run(["shutdown", "/s", "/t", "10"], check=True)
                return {
                    "success": True,
                    "message": "System shutdown initiated (10 seconds delay)"
                }
            elif action == "restart":
                subprocess.run(["shutdown", "/r", "/t", "10"], check=True)
                return {
                    "success": True,
                    "message": "System restart initiated (10 seconds delay)"
                }
            elif action == "hibernate":
                subprocess.run(["shutdown", "/h"], check=True)
                return {
                    "success": True,
                    "message": "System hibernation initiated"
                }
            elif action == "sleep":
                subprocess.run(["powercfg", "/hibernate", "off"], check=True)
                subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], check=True)
                return {
                    "success": True,
                    "message": "System sleep mode activated"
                }
            elif action == "cancel":
                subprocess.run(["shutdown", "/a"], check=True)
                return {
                    "success": True,
                    "message": "Pending shutdown/restart cancelled"
                }
            else:
                return {
                    "success": False,
                    "message": f"Unknown power action: {action}"
                }
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "message": f"Power control failed: {e}"
            }
    
    def _handle_process_control(self, data: Dict) -> Dict:
        """Handle process control commands"""
        return self.process_manager.execute_command(data)
    
    def _handle_file_operation(self, data: Dict) -> Dict:
        """Handle file operation commands"""
        return self.file_manager.execute_command(data)
    
    def _handle_system_info(self, data: Dict) -> Dict:
        """Handle system information requests"""
        return self.system_monitor.get_system_info(data.get("info_type", "all"))
    
    def _handle_automation_task(self, data: Dict) -> Dict:
        """Handle automation task commands"""
        action = data.get("action", "")
        
        if action == "create":
            return self._create_automation_task(data)
        elif action == "execute":
            return self._execute_automation_task(data)
        elif action == "list":
            return self._list_automation_tasks()
        elif action == "delete":
            return self._delete_automation_task(data)
        else:
            return {
                "success": False,
                "message": f"Unknown automation action: {action}"
            }
    
    def _handle_scheduled_task(self, data: Dict) -> Dict:
        """Handle scheduled task commands"""
        action = data.get("action", "")
        
        if action == "create":
            return self._create_scheduled_task(data)
        elif action == "list":
            return self._list_scheduled_tasks()
        elif action == "cancel":
            return self._cancel_scheduled_task(data)
        else:
            return {
                "success": False,
                "message": f"Unknown scheduled action: {action}"
            }
    
    def _create_automation_task(self, data: Dict) -> Dict:
        """Create a new automation task"""
        task = {
            "id": len(self.automation_tasks) + 1,
            "name": data.get("name", f"Task_{int(time.time())}"),
            "description": data.get("description", ""),
            "commands": data.get("commands", []),
            "created": datetime.now().isoformat(),
            "status": "ready"
        }
        
        self.automation_tasks.append(task)
        
        return {
            "success": True,
            "message": f"Automation task '{task['name']}' created",
            "task_id": task["id"]
        }
    
    def _execute_automation_task(self, data: Dict) -> Dict:
        """Execute an automation task"""
        task_id = data.get("task_id")
        task_name = data.get("task_name")
        
        task = None
        if task_id:
            task = next((t for t in self.automation_tasks if t["id"] == task_id), None)
        elif task_name:
            task = next((t for t in self.automation_tasks if t["name"] == task_name), None)
        
        if not task:
            return {
                "success": False,
                "message": "Task not found"
            }
        
        # Execute task commands
        results = []
        for command in task["commands"]:
            try:
                result = self.execute_command(command["type"], command["data"])
                results.append(result)
            except Exception as e:
                results.append({
                    "success": False,
                    "message": f"Command failed: {str(e)}"
                })
        
        task["status"] = "completed"
        task["last_run"] = datetime.now().isoformat()
        task["results"] = results
        
        return {
            "success": True,
            "message": f"Task '{task['name']}' executed",
            "results": results
        }
    
    def _list_automation_tasks(self) -> Dict:
        """List all automation tasks"""
        return {
            "success": True,
            "tasks": self.automation_tasks.copy()
        }
    
    def _delete_automation_task(self, data: Dict) -> Dict:
        """Delete an automation task"""
        task_id = data.get("task_id")
        
        for i, task in enumerate(self.automation_tasks):
            if task["id"] == task_id:
                removed_task = self.automation_tasks.pop(i)
                return {
                    "success": True,
                    "message": f"Task '{removed_task['name']}' deleted"
                }
        
        return {
            "success": False,
            "message": "Task not found"
        }
    
    def _create_scheduled_task(self, data: Dict) -> Dict:
        """Create a scheduled task"""
        task_id = f"scheduled_{int(time.time())}"
        
        schedule_time = data.get("schedule_time")  # Unix timestamp
        task_data = data.get("task_data", {})
        
        self.scheduled_tasks[task_id] = {
            "id": task_id,
            "schedule_time": schedule_time,
            "task_data": task_data,
            "created": time.time(),
            "status": "scheduled"
        }
        
        # Start scheduler thread if not running
        self._start_task_scheduler()
        
        return {
            "success": True,
            "message": f"Task scheduled for {datetime.fromtimestamp(schedule_time)}",
            "task_id": task_id
        }
    
    def _list_scheduled_tasks(self) -> Dict:
        """List all scheduled tasks"""
        return {
            "success": True,
            "scheduled_tasks": list(self.scheduled_tasks.values())
        }
    
    def _cancel_scheduled_task(self, data: Dict) -> Dict:
        """Cancel a scheduled task"""
        task_id = data.get("task_id")
        
        if task_id in self.scheduled_tasks:
            removed_task = self.scheduled_tasks.pop(task_id)
            return {
                "success": True,
                "message": f"Scheduled task {task_id} cancelled"
            }
        
        return {
            "success": False,
            "message": "Scheduled task not found"
        }
    
    def _start_task_scheduler(self):
        """Start the task scheduler thread"""
        if not hasattr(self, '_scheduler_running') or not self._scheduler_running:
            self._scheduler_running = True
            scheduler_thread = threading.Thread(target=self._task_scheduler_loop, daemon=True)
            scheduler_thread.start()
    
    def _task_scheduler_loop(self):
        """Task scheduler main loop"""
        while self._scheduler_running:
            current_time = time.time()
            
            # Check for tasks to execute
            tasks_to_execute = []
            for task_id, task in self.scheduled_tasks.items():
                if task["schedule_time"] <= current_time and task["status"] == "scheduled":
                    tasks_to_execute.append(task_id)
            
            # Execute scheduled tasks
            for task_id in tasks_to_execute:
                task = self.scheduled_tasks[task_id]
                try:
                    result = self.execute_command(
                        task["task_data"]["type"],
                        task["task_data"]["data"]
                    )
                    task["status"] = "completed"
                    task["result"] = result
                    task["executed_time"] = current_time
                    
                    logging.info(f"Scheduled task {task_id} executed successfully")
                except Exception as e:
                    task["status"] = "failed"
                    task["error"] = str(e)
                    logging.error(f"Scheduled task {task_id} failed: {e}")
            
            time.sleep(1)  # Check every second

class SystemMonitor:
    """System monitoring and information gathering"""
    
    def __init__(self):
        self.last_stats = {}
    
    def get_system_info(self, info_type: str = "all") -> Dict:
        """Get system information"""
        try:
            if info_type == "all" or info_type == "basic":
                return self._get_basic_info()
            elif info_type == "processes":
                return self._get_process_info()
            elif info_type == "network":
                return self._get_network_info()
            elif info_type == "disk":
                return self._get_disk_info()
            elif info_type == "memory":
                return self._get_memory_info()
            else:
                return {
                    "success": False,
                    "message": f"Unknown info type: {info_type}"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to get system info: {str(e)}"
            }
    
    def _get_basic_info(self) -> Dict:
        """Get basic system information"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "success": True,
            "system_info": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available": memory.available,
                "memory_total": memory.total,
                "disk_percent": (disk.used / disk.total) * 100,
                "disk_free": disk.free,
                "disk_total": disk.total,
                "boot_time": psutil.boot_time(),
                "current_time": time.time()
            }
        }
    
    def _get_process_info(self) -> Dict:
        """Get process information"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by CPU usage
        processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
        
        return {
            "success": True,
            "processes": processes[:20]  # Top 20 processes
        }
    
    def _get_network_info(self) -> Dict:
        """Get network information"""
        network_stats = psutil.net_io_counters()
        network_connections = len(psutil.net_connections())
        
        return {
            "success": True,
            "network_info": {
                "bytes_sent": network_stats.bytes_sent,
                "bytes_recv": network_stats.bytes_recv,
                "packets_sent": network_stats.packets_sent,
                "packets_recv": network_stats.packets_recv,
                "active_connections": network_connections
            }
        }
    
    def _get_disk_info(self) -> Dict:
        """Get detailed disk information"""
        disk_partitions = psutil.disk_partitions()
        disk_info = []
        
        for partition in disk_partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": (usage.used / usage.total) * 100
                })
            except PermissionError:
                continue
        
        return {
            "success": True,
            "disk_info": disk_info
        }
    
    def _get_memory_info(self) -> Dict:
        """Get detailed memory information"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            "success": True,
            "memory_info": {
                "virtual": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used,
                    "free": memory.free
                },
                "swap": {
                    "total": swap.total,
                    "used": swap.used,
                    "free": swap.free,
                    "percent": swap.percent
                }
            }
        }

class ProcessManager:
    """Process management functionality"""
    
    def execute_command(self, data: Dict) -> Dict:
        """Execute process management command"""
        action = data.get("action", "").lower()
        
        if action == "list":
            return self._list_processes()
        elif action == "kill":
            return self._kill_process(data)
        elif action == "start":
            return self._start_process(data)
        elif action == "info":
            return self._get_process_info(data)
        else:
            return {
                "success": False,
                "message": f"Unknown process action: {action}"
            }
    
    def _list_processes(self) -> Dict:
        """List running processes"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return {
            "success": True,
            "processes": processes
        }
    
    def _kill_process(self, data: Dict) -> Dict:
        """Kill a process by PID or name"""
        pid = data.get("pid")
        name = data.get("name")
        
        try:
            if pid:
                process = psutil.Process(pid)
                process.terminate()
                return {
                    "success": True,
                    "message": f"Process {pid} terminated"
                }
            elif name:
                killed_count = 0
                for proc in psutil.process_iter(['pid', 'name']):
                    if proc.info['name'].lower() == name.lower():
                        try:
                            psutil.Process(proc.info['pid']).terminate()
                            killed_count += 1
                        except:
                            pass
                
                return {
                    "success": True,
                    "message": f"Terminated {killed_count} processes named '{name}'"
                }
            else:
                return {
                    "success": False,
                    "message": "Process PID or name required"
                }
        except psutil.NoSuchProcess:
            return {
                "success": False,
                "message": "Process not found"
            }
        except psutil.AccessDenied:
            return {
                "success": False,
                "message": "Access denied - insufficient privileges"
            }
    
    def _start_process(self, data: Dict) -> Dict:
        """Start a new process"""
        command = data.get("command")
        working_dir = data.get("working_dir", None)
        
        if not command:
            return {
                "success": False,
                "message": "Command required"
            }
        
        try:
            process = subprocess.Popen(
                command,
                cwd=working_dir,
                shell=True
            )
            
            return {
                "success": True,
                "message": f"Process started with PID {process.pid}",
                "pid": process.pid
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to start process: {str(e)}"
            }
    
    def _get_process_info(self, data: Dict) -> Dict:
        """Get detailed information about a process"""
        pid = data.get("pid")
        
        if not pid:
            return {
                "success": False,
                "message": "Process PID required"
            }
        
        try:
            process = psutil.Process(pid)
            info = {
                "pid": process.pid,
                "name": process.name(),
                "status": process.status(),
                "cpu_percent": process.cpu_percent(),
                "memory_percent": process.memory_percent(),
                "create_time": process.create_time(),
                "num_threads": process.num_threads(),
                "cmdline": process.cmdline()
            }
            
            return {
                "success": True,
                "process_info": info
            }
        except psutil.NoSuchProcess:
            return {
                "success": False,
                "message": "Process not found"
            }

class FileManager:
    """File management functionality"""
    
    def execute_command(self, data: Dict) -> Dict:
        """Execute file management command"""
        action = data.get("action", "").lower()
        
        if action == "list":
            return self._list_files(data)
        elif action == "copy":
            return self._copy_file(data)
        elif action == "move":
            return self._move_file(data)
        elif action == "delete":
            return self._delete_file(data)
        elif action == "create":
            return self._create_file(data)
        elif action == "info":
            return self._get_file_info(data)
        else:
            return {
                "success": False,
                "message": f"Unknown file action: {action}"
            }
    
    def _list_files(self, data: Dict) -> Dict:
        """List files in directory"""
        path = data.get("path", ".")
        
        try:
            path_obj = Path(path)
            if not path_obj.exists():
                return {
                    "success": False,
                    "message": "Path does not exist"
                }
            
            files = []
            for item in path_obj.iterdir():
                try:
                    stat = item.stat()
                    files.append({
                        "name": item.name,
                        "path": str(item),
                        "is_dir": item.is_dir(),
                        "size": stat.st_size,
                        "modified": stat.st_mtime
                    })
                except:
                    pass
            
            return {
                "success": True,
                "files": files,
                "current_path": str(path_obj.absolute())
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to list files: {str(e)}"
            }
    
    def _copy_file(self, data: Dict) -> Dict:
        """Copy file or directory"""
        source = data.get("source")
        destination = data.get("destination")
        
        if not source or not destination:
            return {
                "success": False,
                "message": "Source and destination required"
            }
        
        try:
            import shutil
            
            source_path = Path(source)
            dest_path = Path(destination)
            
            if source_path.is_dir():
                shutil.copytree(source_path, dest_path)
            else:
                shutil.copy2(source_path, dest_path)
            
            return {
                "success": True,
                "message": f"Copied {source} to {destination}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Copy failed: {str(e)}"
            }
    
    def _move_file(self, data: Dict) -> Dict:
        """Move file or directory"""
        source = data.get("source")
        destination = data.get("destination")
        
        if not source or not destination:
            return {
                "success": False,
                "message": "Source and destination required"
            }
        
        try:
            import shutil
            shutil.move(source, destination)
            
            return {
                "success": True,
                "message": f"Moved {source} to {destination}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Move failed: {str(e)}"
            }
    
    def _delete_file(self, data: Dict) -> Dict:
        """Delete file or directory"""
        path = data.get("path")
        
        if not path:
            return {
                "success": False,
                "message": "File path required"
            }
        
        try:
            path_obj = Path(path)
            
            if path_obj.is_dir():
                import shutil
                shutil.rmtree(path_obj)
            else:
                path_obj.unlink()
            
            return {
                "success": True,
                "message": f"Deleted {path}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Delete failed: {str(e)}"
            }
    
    def _create_file(self, data: Dict) -> Dict:
        """Create new file or directory"""
        path = data.get("path")
        content = data.get("content", "")
        is_dir = data.get("is_dir", False)
        
        if not path:
            return {
                "success": False,
                "message": "File path required"
            }
        
        try:
            path_obj = Path(path)
            
            if is_dir:
                path_obj.mkdir(parents=True, exist_ok=True)
                return {
                    "success": True,
                    "message": f"Directory created: {path}"
                }
            else:
                path_obj.parent.mkdir(parents=True, exist_ok=True)
                path_obj.write_text(content)
                return {
                    "success": True,
                    "message": f"File created: {path}"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Create failed: {str(e)}"
            }
    
    def _get_file_info(self, data: Dict) -> Dict:
        """Get file information"""
        path = data.get("path")
        
        if not path:
            return {
                "success": False,
                "message": "File path required"
            }
        
        try:
            path_obj = Path(path)
            
            if not path_obj.exists():
                return {
                    "success": False,
                    "message": "File does not exist"
                }
            
            stat = path_obj.stat()
            
            info = {
                "name": path_obj.name,
                "path": str(path_obj.absolute()),
                "is_dir": path_obj.is_dir(),
                "is_file": path_obj.is_file(),
                "size": stat.st_size,
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "accessed": stat.st_atime
            }
            
            if path_obj.is_file():
                info["extension"] = path_obj.suffix
            
            return {
                "success": True,
                "file_info": info
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to get file info: {str(e)}"
            }
