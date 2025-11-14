"""
PyCharm IDE Integration Tool for ULTRON Agent
Enables bi-directional sync between PyCharm and ULTRON, debugging support, and real-time tool registration.

Author: ULTRON Agent + Copilot + Amazon Q Collaboration
Date: November 1, 2025
Status: PHASE 2A - Enhanced Implementation
"""

import asyncio
import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from tools.tool_interface import ToolInterface
from utils.ultron_logger import log_info, log_error, log_ai_decision
from utils.event_system import get_event_system


class PyCharmAPI:
    """Interface to communicate with PyCharm IDE"""

    def __init__(self, port: int = 63342):
        self.port = port
        self.base_url = f"http://localhost:{port}"
        self.project_root = Path.home() / ".pycharm"
        self.plugin_config = self.project_root / "pycharm_integration.xml"
        self.pycharm_exe = self._find_pycharm_executable()

    def _find_pycharm_executable(self) -> str:
        """Find PyCharm executable path"""
        common_paths = [
            r"C:\Program Files\JetBrains\PyCharm 2025.2.1.1\bin\pycharm64.exe",
            r"C:\Program Files\JetBrains\PyCharm 2025.1\bin\pycharm64.exe",
            r"C:\Program Files\JetBrains\PyCharm Professional\bin\pycharm64.exe",
        ]

        for path in common_paths:
            if os.path.exists(path):
                return path

        # Try finding in PATH
        try:
            result = subprocess.run(["where", "pycharm"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except:
            pass

        return "pycharm64.exe"

    async def get_file_content(self, file_path: str) -> str:
        """Get file content from PyCharm"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            log_info("pycharm_api", f"Retrieved file content: {file_path}")
            return content
        except FileNotFoundError:
            log_error("pycharm_api", f"File not found: {file_path}")
            return ""
        except Exception as e:
            log_error("pycharm_api", f"Error reading file {file_path}: {e}")
            return ""

    async def set_file_content(self, file_path: str, content: str) -> bool:
        """Set file content in PyCharm"""
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            log_info("pycharm_api", f"Updated file: {file_path}")
            return True
        except Exception as e:
            log_error("pycharm_api", f"Error writing file {file_path}: {e}")
            return False

    async def launch_debugger(self, file_path: str, breakpoint_line: int = 0) -> bool:
        """Launch PyCharm debugger for file"""
        try:
            if breakpoint_line > 0:
                cmd = f'"{self.pycharm_exe}" --line {breakpoint_line} "{file_path}"'
            else:
                cmd = f'"{self.pycharm_exe}" "{file_path}"'

            subprocess.Popen(cmd, shell=True)
            log_info("pycharm_api", f"Launched debugger for {file_path}:{breakpoint_line}")
            return True
        except Exception as e:
            log_error("pycharm_api", f"Error launching debugger: {e}")
            return False

    async def get_project_structure(self) -> Dict[str, Any]:
        """Get PyCharm project structure"""
        try:
            project_root = Path.cwd()
            structure = {
                "root": str(project_root),
                "python_files": len(list(project_root.rglob("*.py"))),
                "tools_directory": str(project_root / "tools"),
                "modules": []
            }

            tools_dir = project_root / "tools"
            if tools_dir.exists():
                for py_file in tools_dir.glob("*.py"):
                    if not py_file.name.startswith("_"):
                        structure["modules"].append({
                            "name": py_file.stem,
                            "path": str(py_file),
                            "size": py_file.stat().st_size
                        })

            log_info("pycharm_api", f"Retrieved project structure with {len(structure['modules'])} modules")
            return structure
        except Exception as e:
            log_error("pycharm_api", f"Error getting project structure: {e}")
            return {}


class FileWatcher:
    """Watches tool files for changes from PyCharm"""

    def __init__(self):
        self.watched_files: Dict[str, float] = {}
        self.callbacks: List[callable] = []
        self.monitoring = False

    def add_watch(self, file_path: str):
        """Add file to watch list"""
        try:
            self.watched_files[file_path] = os.path.getmtime(file_path)
            log_info("file_watcher", f"Added watch: {file_path}")
        except FileNotFoundError:
            log_error("file_watcher", f"Cannot watch non-existent file: {file_path}")

    def add_callback(self, callback: callable):
        """Add callback for file changes"""
        self.callbacks.append(callback)

    async def start_monitoring(self):
        """Start monitoring watched files"""
        self.monitoring = True
        while self.monitoring:
            try:
                for file_path, last_mtime in list(self.watched_files.items()):
                    if os.path.exists(file_path):
                        current_mtime = os.path.getmtime(file_path)
                        if current_mtime > last_mtime:
                            self.watched_files[file_path] = current_mtime
                            for callback in self.callbacks:
                                await callback(file_path)
                            log_info("file_watcher", f"Detected change: {file_path}")
                await asyncio.sleep(1)
            except Exception as e:
                log_error("file_watcher", f"Monitoring error: {e}")
                await asyncio.sleep(1)

    def stop_monitoring(self):
        """Stop monitoring files"""
        self.monitoring = False
        log_info("file_watcher", "Stopped monitoring")


class ToolParser:
    """Parse Python tool files for ULTRON integration"""

    @staticmethod
    def parse_tool_definition(file_content: str) -> Optional[Dict[str, Any]]:
        """Extract tool definition from Python file"""
        try:
            class_match = re.search(r'class\s+(\w+)\s*\(', file_content)
            if not class_match:
                return None

            class_name = class_match.group(1)
            docstring_match = re.search(r'"""(.*?)"""', file_content, re.DOTALL)
            description = docstring_match.group(1).strip() if docstring_match else "No description"

            name_match = re.search(r'def name\(self\).*?return\s+["\']([^"\']+)["\']', file_content, re.DOTALL)
            name = name_match.group(1) if name_match else class_name

            match_match = re.search(r'keywords\s*=\s*\[(.*?)\]', file_content, re.DOTALL)
            keywords = []
            if match_match:
                kw_text = match_match.group(1)
                keywords = re.findall(r'["\']([^"\']+)["\']', kw_text)

            tool_def = {
                "class_name": class_name,
                "name": name,
                "description": description,
                "keywords": keywords,
                "parsed_at": datetime.now().isoformat()
            }

            log_info("tool_parser", f"Parsed tool: {name}")
            return tool_def
        except Exception as e:
            log_error("tool_parser", f"Error parsing tool definition: {e}")
            return None


class PyCharmIntegrationTool(ToolInterface):
    """Bridge between ULTRON and PyCharm IDE

    Enables:
    - Real-time tool file sync from PyCharm to ULTRON
    - Debugging support with PyCharm debugger
    - Project structure awareness
    - Automatic tool registration on save
    """

    def __init__(self):
        self.pycharm_api = PyCharmAPI()
        self.file_watcher = FileWatcher()
        self.sync_queue: List[str] = []
        self.tool_registry: Dict[str, Dict] = {}
        self.event_system = get_event_system()
        self.is_monitoring = False

        log_info("pycharm_integration", "PyCharm Integration Tool initialized")

    @property
    def name(self) -> str:
        return "PyCharm IDE Integration"

    @property
    def description(self) -> str:
        return "Bridge between ULTRON Agent and PyCharm IDE - enables real-time tool sync and debugging"

    def match(self, command: str) -> bool:
        """Check if command matches PyCharm integration"""
        keywords = [
            "pycharm", "ide integration", "sync tool", "debug tool",
            "project structure", "file watch", "start monitoring", "open file", "edit"
        ]
        return any(kw in command.lower() for kw in keywords)

    def execute(self, command: str, **kwargs) -> str:
        """Execute PyCharm integration command"""
        try:
            command_lower = command.lower()

            if "sync" in command_lower and "tool" in command_lower:
                return self._handle_sync_tool(command, **kwargs)
            elif "debug" in command_lower:
                return self._handle_debug_tool(command, **kwargs)
            elif "project" in command_lower or "structure" in command_lower:
                return self._handle_project_structure(command, **kwargs)
            elif "start" in command_lower and "monitoring" in command_lower:
                return self._handle_start_monitoring(command, **kwargs)
            elif "stop" in command_lower and "monitoring" in command_lower:
                return self._handle_stop_monitoring(command, **kwargs)
            elif "registry" in command_lower or ("list" in command_lower and "tool" in command_lower):
                return self._handle_list_tools(command, **kwargs)
            elif "open" in command_lower or "edit" in command_lower:
                return self._handle_open_file(command, **kwargs)
            else:
                return f"Unknown PyCharm command: {command}"

        except Exception as e:
            error_msg = f"PyCharm integration error: {e}"
            log_error("pycharm_integration", error_msg)
            return error_msg

    def _handle_sync_tool(self, command: str, **kwargs) -> str:
        """Sync tool from PyCharm to ULTRON"""
        try:
            file_path = self._extract_filepath(command)
            if not file_path:
                return "No file path specified. Usage: sync tool /path/to/tool.py"

            content = asyncio.run(self.pycharm_api.get_file_content(file_path))
            if not content:
                return f"Failed to read file: {file_path}"

            tool_def = ToolParser.parse_tool_definition(content)
            if not tool_def:
                return f"No tool definition found in: {file_path}"

            self.tool_registry[tool_def["name"]] = {
                **tool_def,
                "file_path": file_path,
                "content": content,
                "synced_at": datetime.now().isoformat()
            }

            self.file_watcher.add_watch(file_path)

            result = f"✓ Tool synced: {tool_def['name']}\n"
            result += f"  File: {file_path}\n"
            result += f"  Keywords: {', '.join(tool_def['keywords'])}"

            log_ai_decision(
                "pycharm_integration",
                f"Tool synced from PyCharm: {tool_def['name']}",
                ai_model="pycharm_integration",
                confidence_score=0.95
            )

            return result

        except Exception as e:
            return f"Error syncing tool: {e}"

    def _handle_debug_tool(self, command: str, **kwargs) -> str:
        """Launch debugging session for tool"""
        try:
            tool_name = self._extract_tool_name(command)
            if not tool_name or tool_name not in self.tool_registry:
                available = ", ".join(self.tool_registry.keys())
                return f"Tool not found: {tool_name}\nAvailable: {available or 'None'}"

            tool_def = self.tool_registry[tool_name]
            file_path = tool_def["file_path"]

            success = asyncio.run(self.pycharm_api.launch_debugger(file_path))
            if success:
                result = f"✓ Debugger launched for: {tool_name}\n"
                result += f"  File: {file_path}\n"
                result += "  Set breakpoints and run to hit them"
                log_info("pycharm_integration", f"Debugger launched for {tool_name}")
                return result
            else:
                return f"Failed to launch debugger for {tool_name}"

        except Exception as e:
            return f"Error launching debugger: {e}"

    def _handle_project_structure(self, command: str, **kwargs) -> str:
        """Get PyCharm project structure"""
        try:
            structure = asyncio.run(self.pycharm_api.get_project_structure())
            if not structure:
                return "Failed to retrieve project structure"

            result = "PyCharm Project Structure:\n"
            result += f"  Root: {structure['root']}\n"
            result += f"  Python Files: {structure['python_files']}\n"
            result += f"  Tools Directory: {structure['tools_directory']}\n"
            result += f"  Modules: {len(structure['modules'])}\n"

            if structure['modules']:
                result += "\n  Modules:\n"
                for mod in structure['modules']:
                    result += f"    - {mod['name']} ({mod['size']} bytes)\n"

            return result

        except Exception as e:
            return f"Error getting project structure: {e}"

    def _handle_start_monitoring(self, command: str, **kwargs) -> str:
        """Start monitoring tool files for changes"""
        try:
            if self.is_monitoring:
                return "✓ File monitoring already active"

            self.is_monitoring = True

            async def on_file_change(file_path):
                log_info("pycharm_integration", f"Detected change in {file_path}")
                await self._async_sync_tool(file_path)

            self.file_watcher.add_callback(on_file_change)
            asyncio.create_task(self.file_watcher.start_monitoring())

            result = "✓ File monitoring started\n"
            result += f"  Watching {len(self.file_watcher.watched_files)} files\n"
            result += "  Changes will be synced automatically"

            log_info("pycharm_integration", "Started file monitoring")
            return result

        except Exception as e:
            return f"Error starting monitoring: {e}"

    def _handle_stop_monitoring(self, command: str, **kwargs) -> str:
        """Stop monitoring tool files"""
        try:
            if not self.is_monitoring:
                return "✓ File monitoring not active"

            self.file_watcher.stop_monitoring()
            self.is_monitoring = False

            result = "✓ File monitoring stopped"
            log_info("pycharm_integration", "Stopped file monitoring")
            return result

        except Exception as e:
            return f"Error stopping monitoring: {e}"

    def _handle_list_tools(self, command: str, **kwargs) -> str:
        """List all synced tools"""
        if not self.tool_registry:
            return "No tools synced yet. Use 'sync tool' to add tools."

        result = "Synced Tools Registry:\n"
        for name, tool_def in self.tool_registry.items():
            result += f"\n  • {name}\n"
            result += f"    File: {tool_def['file_path']}\n"
            result += f"    Keywords: {', '.join(tool_def['keywords'])}\n"
            result += f"    Synced: {tool_def['synced_at']}\n"

        return result

    def _handle_open_file(self, command: str, **kwargs) -> str:
        """Open file in PyCharm"""
        try:
            file_path = self._extract_filepath(command)
            if not file_path:
                # Try to open current project
                project_path = os.getcwd()
                subprocess.Popen(f'"{self.pycharm_api.pycharm_exe}" "{project_path}"', shell=True)
                return f"✓ Opening PyCharm with project: {project_path}"

            if os.path.exists(file_path):
                subprocess.Popen(f'"{self.pycharm_api.pycharm_exe}" "{file_path}"', shell=True)
                return f"✓ Opening file in PyCharm: {file_path}"
            else:
                return f"File not found: {file_path}"
        except Exception as e:
            return f"Error opening file: {e}"

    async def _async_sync_tool(self, file_path: str):
        """Async helper to sync tool"""
        content = await self.pycharm_api.get_file_content(file_path)
        if content:
            tool_def = ToolParser.parse_tool_definition(content)
            if tool_def:
                self.tool_registry[tool_def["name"]] = {
                    **tool_def,
                    "file_path": file_path,
                    "content": content,
                    "synced_at": datetime.now().isoformat()
                }
                await self.event_system.emit("tool_synced_from_pycharm", {
                    "tool_name": tool_def["name"],
                    "file_path": file_path
                })

    @staticmethod
    def _extract_filepath(command: str) -> Optional[str]:
        """Extract file path from command"""
        quoted_match = re.search(r'["\']([^"\']+\.py)["\']', command)
        if quoted_match:
            return quoted_match.group(1)

        path_match = re.search(r'(\S+\.py)', command)
        if path_match:
            return path_match.group(1)

        return None

    @staticmethod
    def _extract_tool_name(command: str) -> Optional[str]:
        """Extract tool name from command"""
        quoted_match = re.search(r'["\']([^"\']+)["\']', command)
        if quoted_match:
            return quoted_match.group(1)

        word_match = re.search(r'(?:debug|tool|sync)\s+(?:tool\s+)?(\w+)', command, re.IGNORECASE)
        if word_match:
            return word_match.group(1)

        return None

    @classmethod
    def schema(cls) -> Dict[str, Any]:
        """Return tool schema for OpenAI-compatible function calling"""
        return {
            "name": "pycharm_integration",
            "description": "PyCharm IDE integration for ULTRON Agent",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": (
                            "Integration command: sync tool, debug tool, "
                            "project structure, start monitoring, stop "
                            "monitoring, list tools, open file"
                        )
                    }
                },
                "required": ["command"]
            }
        }
