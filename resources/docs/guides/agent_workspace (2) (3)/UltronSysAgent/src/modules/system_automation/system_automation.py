"""
System Automation module for UltronSysAgent
Handles system commands, file operations, and administrative tasks
"""

import asyncio
import logging
import subprocess
import os
import shutil
import winreg
import psutil
from typing import Dict, List, Any, Optional
from pathlib import Path
import json

from ...core.event_bus import EventBus, EventTypes
from ...core.logger import command_logger

class SystemAutomation:
    """System automation and control module"""
    
    def __init__(self, config, event_bus: EventBus):
        self.config = config
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)
        
        # Command history for auditing
        self.command_history = []
        
        # Dangerous commands that require confirmation
        self.dangerous_commands = {
            'format', 'del', 'rd', 'rmdir', 'delete', 'remove',
            'shutdown', 'restart', 'reboot', 'kill', 'taskkill',
            'reg delete', 'netsh', 'diskpart', 'cipher'
        }
        
        # Whitelisted safe commands
        self.safe_commands = {
            'dir', 'ls', 'cd', 'pwd', 'echo', 'type', 'cat',
            'ping', 'ipconfig', 'systeminfo', 'tasklist',
            'date', 'time', 'whoami', 'hostname'
        }
        
        # Setup event handlers
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """Setup event bus handlers"""
        self.event_bus.subscribe(EventTypes.SYSTEM_COMMAND, self._handle_system_command)
        self.event_bus.subscribe(EventTypes.ADMIN_REQUEST, self._handle_admin_request)
    
    async def start(self):
        """Start the system automation module"""
        self.logger.info("⚙️ Starting System Automation...")
        
        # Check admin privileges
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            self.logger.info(f"Admin privileges: {'Available' if is_admin else 'Not available'}")
        except:
            self.logger.warning("Could not check admin privileges")
        
        await self.event_bus.publish(EventTypes.MODULE_STARTED, 
                                    {"module": "system_automation"}, 
                                    source="system_automation")
    
    async def stop(self):
        """Stop the system automation module"""
        self.logger.info("⚙️ Stopping System Automation...")
        
        await self.event_bus.publish(EventTypes.MODULE_STOPPED, 
                                    {"module": "system_automation"}, 
                                    source="system_automation")
    
    async def _handle_system_command(self, event):
        """Handle system command execution requests"""
        try:
            user_input = event.data.get('user_input', '')
            ai_response = event.data.get('ai_response', '')
            requires_admin = event.data.get('requires_admin', False)
            
            # Parse potential commands from AI response
            commands = self._extract_commands_from_response(ai_response)
            
            for command in commands:
                await self._execute_command(command, requires_admin)
                
        except Exception as e:
            self.logger.error(f"Error handling system command: {e}")
    
    async def _handle_admin_request(self, event):
        """Handle administrative action requests"""
        try:
            action = event.data.get('action', '')
            params = event.data.get('params', {})
            
            if not self.config.is_admin_mode():
                await self.event_bus.publish(EventTypes.SYSTEM_RESPONSE, 
                                           {
                                               "success": False,
                                               "message": "Admin mode required for this action",
                                               "action": action
                                           }, 
                                           source="system_automation")
                return
            
            result = await self._execute_admin_action(action, params)
            
            await self.event_bus.publish(EventTypes.SYSTEM_RESPONSE, 
                                       {
                                           "success": result.get('success', False),
                                           "message": result.get('message', ''),
                                           "data": result.get('data', {}),
                                           "action": action
                                       }, 
                                       source="system_automation")
            
        except Exception as e:
            self.logger.error(f"Error handling admin request: {e}")
    
    def _extract_commands_from_response(self, ai_response: str) -> List[str]:
        """Extract executable commands from AI response"""
        commands = []
        
        # Look for command blocks or indicators
        lines = ai_response.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Check for command indicators
            if any(indicator in line.lower() for indicator in ['execute:', 'command:', 'run:']):
                # Extract the actual command
                for indicator in ['execute:', 'command:', 'run:']:
                    if indicator in line.lower():
                        cmd = line.lower().split(indicator, 1)[1].strip()
                        if cmd:
                            commands.append(cmd)
                        break
            
            # Check for code blocks
            elif line.startswith('```') and 'cmd' in line.lower():
                # This indicates a command block might follow
                continue
            elif line.startswith('```'):
                # End of code block
                continue
        
        return commands
    
    async def _execute_command(self, command: str, requires_admin: bool = False):
        """Execute a system command with safety checks"""
        try:
            # Security checks
            if not self._is_command_safe(command):
                if not self.config.is_admin_mode():
                    self.logger.warning(f"Unsafe command blocked (not in admin mode): {command}")
                    return
                
                if self.config.get('security.require_admin_confirmation', True):
                    # Request confirmation for dangerous commands
                    await self.event_bus.publish(EventTypes.ADMIN_REQUEST, 
                                               {
                                                   "action": "confirm_dangerous_command",
                                                   "params": {"command": command}
                                               }, 
                                               source="system_automation")
                    return
            
            # Log the command
            command_logger.log_command(command, admin_mode=self.config.is_admin_mode())
            
            # Execute the command
            result = await self._run_command(command)
            
            # Store in history
            self.command_history.append({
                "command": command,
                "timestamp": asyncio.get_event_loop().time(),
                "result": result,
                "admin_mode": self.config.is_admin_mode()
            })
            
            # Publish result
            await self.event_bus.publish(EventTypes.SYSTEM_RESPONSE, 
                                       {
                                           "success": result.get('success', False),
                                           "output": result.get('output', ''),
                                           "error": result.get('error', ''),
                                           "command": command
                                       }, 
                                       source="system_automation")
            
        except Exception as e:
            self.logger.error(f"Error executing command '{command}': {e}")
    
    def _is_command_safe(self, command: str) -> bool:
        """Check if a command is safe to execute"""
        command_lower = command.lower().strip()
        
        # Check against dangerous commands
        for dangerous in self.dangerous_commands:
            if dangerous in command_lower:
                return False
        
        # Check whitelist mode
        if self.config.get('security.whitelist_mode', False):
            return any(safe in command_lower for safe in self.safe_commands)
        
        return True
    
    async def _run_command(self, command: str) -> Dict[str, Any]:
        """Run a system command and return results"""
        try:
            # Execute command
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                shell=True
            )
            
            stdout, stderr = await process.communicate()
            
            success = process.returncode == 0
            output = stdout.decode('utf-8', errors='ignore').strip()
            error = stderr.decode('utf-8', errors='ignore').strip()
            
            return {
                "success": success,
                "output": output,
                "error": error,
                "return_code": process.returncode
            }
            
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "return_code": -1
            }
    
    async def _execute_admin_action(self, action: str, params: Dict) -> Dict[str, Any]:
        """Execute administrative actions"""
        try:
            if action == "file_operation":
                return await self._handle_file_operation(params)
            elif action == "registry_operation":
                return await self._handle_registry_operation(params)
            elif action == "service_operation":
                return await self._handle_service_operation(params)
            elif action == "process_operation":
                return await self._handle_process_operation(params)
            elif action == "network_operation":
                return await self._handle_network_operation(params)
            elif action == "confirm_dangerous_command":
                return await self._handle_dangerous_command_confirmation(params)
            else:
                return {
                    "success": False,
                    "message": f"Unknown admin action: {action}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Error executing admin action: {e}"
            }
    
    async def _handle_file_operation(self, params: Dict) -> Dict[str, Any]:
        """Handle file operations"""
        operation = params.get('operation')
        path = params.get('path')
        
        if not path:
            return {"success": False, "message": "Path required"}
        
        try:
            if operation == "create_directory":
                os.makedirs(path, exist_ok=True)
                command_logger.log_file_access(path, "create_directory")
                return {"success": True, "message": f"Directory created: {path}"}
            
            elif operation == "delete_file":
                if os.path.exists(path):
                    os.remove(path)
                    command_logger.log_file_access(path, "delete_file")
                    return {"success": True, "message": f"File deleted: {path}"}
                else:
                    return {"success": False, "message": "File not found"}
            
            elif operation == "copy_file":
                destination = params.get('destination')
                if destination:
                    shutil.copy2(path, destination)
                    command_logger.log_file_access(f"{path} -> {destination}", "copy_file")
                    return {"success": True, "message": f"File copied to: {destination}"}
                else:
                    return {"success": False, "message": "Destination required"}
            
            else:
                return {"success": False, "message": f"Unknown file operation: {operation}"}
                
        except Exception as e:
            return {"success": False, "message": f"File operation failed: {e}"}
    
    async def _handle_registry_operation(self, params: Dict) -> Dict[str, Any]:
        """Handle Windows registry operations"""
        operation = params.get('operation')
        key_path = params.get('key_path')
        
        if not key_path:
            return {"success": False, "message": "Registry key path required"}
        
        try:
            if operation == "read_value":
                value_name = params.get('value_name', '')
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                    value, reg_type = winreg.QueryValueEx(key, value_name)
                    command_logger.log_command(f"Registry read: {key_path}\\{value_name}")
                    return {
                        "success": True, 
                        "data": {"value": value, "type": reg_type},
                        "message": "Registry value read successfully"
                    }
            
            elif operation == "write_value":
                value_name = params.get('value_name')
                value_data = params.get('value_data')
                value_type = params.get('value_type', winreg.REG_SZ)
                
                if not all([value_name, value_data]):
                    return {"success": False, "message": "Value name and data required"}
                
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                    winreg.SetValueEx(key, value_name, 0, value_type, value_data)
                    command_logger.log_command(f"Registry write: {key_path}\\{value_name}")
                    return {"success": True, "message": "Registry value written successfully"}
            
            else:
                return {"success": False, "message": f"Unknown registry operation: {operation}"}
                
        except Exception as e:
            return {"success": False, "message": f"Registry operation failed: {e}"}
    
    async def _handle_service_operation(self, params: Dict) -> Dict[str, Any]:
        """Handle Windows service operations"""
        operation = params.get('operation')
        service_name = params.get('service_name')
        
        if not service_name:
            return {"success": False, "message": "Service name required"}
        
        try:
            if operation == "status":
                # Get service status using sc command
                result = await self._run_command(f'sc query "{service_name}"')
                return {
                    "success": result['success'],
                    "data": {"output": result['output']},
                    "message": "Service status retrieved"
                }
            
            elif operation in ["start", "stop", "restart"]:
                cmd = f'sc {operation} "{service_name}"'
                result = await self._run_command(cmd)
                command_logger.log_command(f"Service {operation}: {service_name}")
                return {
                    "success": result['success'],
                    "message": f"Service {operation} command executed"
                }
            
            else:
                return {"success": False, "message": f"Unknown service operation: {operation}"}
                
        except Exception as e:
            return {"success": False, "message": f"Service operation failed: {e}"}
    
    async def _handle_process_operation(self, params: Dict) -> Dict[str, Any]:
        """Handle process operations"""
        operation = params.get('operation')
        
        try:
            if operation == "list":
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                    try:
                        processes.append(proc.info)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                return {
                    "success": True,
                    "data": {"processes": processes[:50]},  # Limit to 50 processes
                    "message": "Process list retrieved"
                }
            
            elif operation == "kill":
                pid = params.get('pid')
                if pid:
                    try:
                        proc = psutil.Process(pid)
                        proc.terminate()
                        command_logger.log_command(f"Process terminated: PID {pid}")
                        return {"success": True, "message": f"Process {pid} terminated"}
                    except psutil.NoSuchProcess:
                        return {"success": False, "message": "Process not found"}
                else:
                    return {"success": False, "message": "PID required"}
            
            else:
                return {"success": False, "message": f"Unknown process operation: {operation}"}
                
        except Exception as e:
            return {"success": False, "message": f"Process operation failed: {e}"}
    
    async def _handle_network_operation(self, params: Dict) -> Dict[str, Any]:
        """Handle network operations"""
        operation = params.get('operation')
        
        try:
            if operation == "ping":
                host = params.get('host', 'google.com')
                result = await self._run_command(f'ping -n 4 {host}')
                return {
                    "success": result['success'],
                    "data": {"output": result['output']},
                    "message": f"Ping to {host} completed"
                }
            
            elif operation == "netstat":
                result = await self._run_command('netstat -an')
                return {
                    "success": result['success'],
                    "data": {"output": result['output'][:2000]},  # Limit output
                    "message": "Network connections retrieved"
                }
            
            elif operation == "ipconfig":
                result = await self._run_command('ipconfig /all')
                return {
                    "success": result['success'],
                    "data": {"output": result['output']},
                    "message": "IP configuration retrieved"
                }
            
            else:
                return {"success": False, "message": f"Unknown network operation: {operation}"}
                
        except Exception as e:
            return {"success": False, "message": f"Network operation failed: {e}"}
    
    async def _handle_dangerous_command_confirmation(self, params: Dict) -> Dict[str, Any]:
        """Handle confirmation for dangerous commands"""
        command = params.get('command')
        
        # This would typically show a confirmation dialog in the GUI
        # For now, we'll auto-confirm if dangerous commands are enabled
        if self.config.get('security.dangerous_commands_enabled', False):
            await self._execute_command(command, requires_admin=True)
            return {"success": True, "message": "Dangerous command executed"}
        else:
            return {"success": False, "message": "Dangerous command blocked by security policy"}
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system automation status"""
        try:
            # Get system info
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('C:')
            
            return {
                "admin_mode": self.config.is_admin_mode(),
                "command_history_count": len(self.command_history),
                "system_info": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": (disk.used / disk.total) * 100,
                    "uptime": psutil.boot_time()
                },
                "security": {
                    "whitelist_mode": self.config.get('security.whitelist_mode', False),
                    "dangerous_commands_enabled": self.config.get('security.dangerous_commands_enabled', False),
                    "require_confirmation": self.config.get('security.require_admin_confirmation', True)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system status: {e}")
            return {"error": str(e)}
