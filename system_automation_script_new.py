import ollama
import psutil
import os
import logging
import keyboard
import time
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

# Configure logging with more detailed format
logging.basicConfig(
    filename='system_automation.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)

# Directory for file operations using pathlib
WORKING_DIR = Path("automated_files")
WORKING_DIR.mkdir(exist_ok=True)
logging.info(f"Ensuring working directory exists: {WORKING_DIR}")

class SystemTools:
    """Class to encapsulate system operation tools"""
    
    @staticmethod
    async def run_diagnostics() -> Dict[str, Any]:
        """Run comprehensive system diagnostics and return structured results."""
        try:
            cpu_usage = psutil.cpu_percent(interval=1, percpu=True)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            battery = psutil.sensors_battery()
            processes = list(psutil.process_iter(['name', 'pid', 'cpu_percent', 'memory_percent']))
            
            # Sort processes by CPU usage
            top_processes = sorted(processes, key=lambda p: p.info['cpu_percent'], reverse=True)[:5]
            
            diagnostic_data = {
                "cpu": {
                    "total_usage": sum(cpu_usage) / len(cpu_usage),
                    "per_core_usage": cpu_usage
                },
                "memory": {
                    "total": memory.total / (1024**3),
                    "available": memory.available / (1024**3),
                    "used": memory.used / (1024**3),
                    "percent": memory.percent
                },
                "disk": {
                    "total": disk.total / (1024**3),
                    "used": disk.used / (1024**3),
                    "free": disk.free / (1024**3),
                    "percent": disk.percent
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv
                },
                "battery": {
                    "percent": battery.percent if battery else None,
                    "power_plugged": battery.power_plugged if battery else None
                },
                "top_processes": [
                    {
                        "name": p.info['name'],
                        "pid": p.info['pid'],
                        "cpu_percent": p.info['cpu_percent'],
                        "memory_percent": p.info['memory_percent']
                    } for p in top_processes
                ]
            }
            
            # Format a human-readable report
            report = (
                f"System Diagnostics Report:\n"
                f"CPU Usage: {diagnostic_data['cpu']['total_usage']:.1f}% (Average)\n"
                f"Memory: {diagnostic_data['memory']['used']:.1f}GB used of {diagnostic_data['memory']['total']:.1f}GB ({diagnostic_data['memory']['percent']}%)\n"
                f"Disk: {diagnostic_data['disk']['used']:.1f}GB used of {diagnostic_data['disk']['total']:.1f}GB ({diagnostic_data['disk']['percent']}%)\n"
                f"Network: ↑{diagnostic_data['network']['bytes_sent']/1024**2:.1f}MB ↓{diagnostic_data['network']['bytes_recv']/1024**2:.1f}MB\n"
                f"\nTop CPU-Intensive Processes:\n"
            )
            
            for proc in diagnostic_data['top_processes']:
                report += f"- {proc['name']}: {proc['cpu_percent']:.1f}% CPU, {proc['memory_percent']:.1f}% MEM\n"
            
            if battery:
                report += f"\nBattery: {diagnostic_data['battery']['percent']}% {'(Charging)' if diagnostic_data['battery']['power_plugged'] else '(On Battery)'}"
            
            logging.info("Diagnostics completed successfully")
            return {"data": diagnostic_data, "report": report}
            
        except Exception as e:
            logging.error(f"Diagnostics error: {str(e)}", exc_info=True)
            raise

    @staticmethod
    async def file_operation(operation: str, filename: str, content: str = "", extension: str = ".txt") -> Dict[str, str]:
        """Perform file operations with proper locking and error handling."""
        try:
            filepath = WORKING_DIR / f"{filename}{extension}"
            
            async with asyncio.Lock():  # Prevent concurrent file access
                if operation == "create":
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    logging.info(f"Created file: {filepath}")
                    return {"status": "success", "filepath": str(filepath), "message": f"File created: {filepath}"}
                
                elif operation == "edit":
                    if not filepath.exists():
                        raise FileNotFoundError(f"File not found: {filepath}")
                    with open(filepath, 'a', encoding='utf-8') as f:
                        f.write(f"\n{content}")
                    logging.info(f"Edited file: {filepath}")
                    return {"status": "success", "filepath": str(filepath), "message": f"File edited: {filepath}"}
                
                elif operation == "delete":
                    if not filepath.exists():
                        raise FileNotFoundError(f"File not found: {filepath}")
                    filepath.unlink()
                    logging.info(f"Deleted file: {filepath}")
                    return {"status": "success", "filepath": str(filepath), "message": f"File deleted: {filepath}"}
                
        except Exception as e:
            logging.error(f"File operation error: {str(e)}", exc_info=True)
            raise

    @classmethod
    async def create_file(cls, filename: str, content: str, extension: str = ".txt") -> Dict[str, str]:
        """Create a file with the specified content and extension."""
        return await cls.file_operation("create", filename, content, extension)

    @classmethod
    async def edit_file(cls, filename: str, content: str, extension: str = ".txt") -> Dict[str, str]:
        """Edit an existing file with new content."""
        return await cls.file_operation("edit", filename, content, extension)

    @classmethod
    async def delete_file(cls, filename: str, extension: str = ".txt") -> Dict[str, str]:
        """Delete a file."""
        return await cls.file_operation("delete", filename, extension=extension)

    @staticmethod
    async def list_files() -> Dict[str, Any]:
        """List all files in the working directory with details."""
        try:
            files = []
            for file_path in WORKING_DIR.glob('*'):
                stat = file_path.stat()
                files.append({
                    "name": file_path.name,
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "type": file_path.suffix[1:] if file_path.suffix else "unknown"
                })
            
            if not files:
                return {"status": "success", "files": [], "message": "No files found in working directory."}
            
            # Generate readable report
            report = "Files in working directory:\n"
            for file in files:
                report += f"- {file['name']} ({file['size']/1024:.1f}KB, modified: {file['modified']})\n"
            
            logging.info("Listed files in working directory")
            return {"status": "success", "files": files, "report": report}
            
        except Exception as e:
            logging.error(f"File listing error: {str(e)}", exc_info=True)
            raise

    @staticmethod
    async def write_to_active_window(text: str) -> Dict[str, str]:
        """Write text to the active window by simulating keystrokes."""
        try:
            await asyncio.sleep(1)  # Give user time to focus the target window
            keyboard.write(text)
            keyboard.press_and_release('enter')
            logging.info(f"Wrote to active window: {text[:50]}...")
            return {"status": "success", "text": text, "message": "Text written to active window"}
        except Exception as e:
            logging.error(f"Error writing to active window: {str(e)}", exc_info=True)
            raise

class CommandProcessor:
    """Class to handle command processing and tool management"""
    
    def __init__(self):
        self.system_tools = SystemTools()
        self.registered_tools = self._register_default_tools()
        self.command_history = []
        
    def _register_default_tools(self) -> List[Dict[str, Any]]:
        """Register the default system tools."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "run_diagnostics",
                    "description": "Run comprehensive system diagnostics including CPU, memory, disk usage, network, battery, and top processes.",
                    "parameters": {}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_file",
                    "description": "Create a new file with specified content.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {"type": "string", "description": "Name of the file without extension"},
                            "content": {"type": "string", "description": "Content to write to the file"},
                            "extension": {"type": "string", "description": "File extension (default: .txt)"}
                        },
                        "required": ["filename", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "edit_file",
                    "description": "Edit an existing file by appending content.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {"type": "string", "description": "Name of the file without extension"},
                            "content": {"type": "string", "description": "Content to append to the file"},
                            "extension": {"type": "string", "description": "File extension (default: .txt)"}
                        },
                        "required": ["filename", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_file",
                    "description": "Delete a file from the working directory.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {"type": "string", "description": "Name of the file without extension"},
                            "extension": {"type": "string", "description": "File extension (default: .txt)"}
                        },
                        "required": ["filename"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_files",
                    "description": "List all files in the working directory with details.",
                    "parameters": {}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_to_active_window",
                    "description": "Write text to the currently active window.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string", "description": "Text to write to the active window"}
                        },
                        "required": ["text"]
                    }
                }
            }
        ]

    async def process_command(self, command: str, use_openai: bool = True) -> str:
        """Process a natural language command using OpenAI's agent network or Ollama."""
        try:
            # Add command to history
            self.command_history.append(command)
            
            if use_openai and os.getenv("OPENAI_API_KEY"):
                from tools.openai_tools import OpenAITools
                from tools.agent_network import AgentNetwork
                
                config = {"openai_api_key": os.getenv("OPENAI_API_KEY")}
                agent_network = AgentNetwork(config)
                agent_network.register_tools(self.registered_tools)
                
                result = await agent_network.process_request(command)
                return result["response"]
            
            # Fallback to Ollama
            response = await self._process_with_ollama(command)
            return await self._execute_command(command.lower(), response)
            
        except Exception as e:
            logging.error(f"Command processing error: {str(e)}", exc_info=True)
            return f"Error processing command: {str(e)}"

    async def _process_with_ollama(self, command: str) -> str:
        """Process command with Ollama."""
        try:
            english_command = "Please reply in English. " + command
            response = ollama.chat(
                model='qwen2.5',
                messages=[{'role': 'user', 'content': english_command}]
            )
            return response['message']['content']
        except Exception as e:
            logging.error(f"Ollama processing error: {str(e)}", exc_info=True)
            raise

    async def _execute_command(self, command_lower: str, ollama_response: str) -> str:
        """Execute command based on the command type and Ollama's response."""
        try:
            # Command routing
            if "diagnostics" in command_lower or "system info" in command_lower:
                result = await self.system_tools.run_diagnostics()
                return result["report"]
            
            elif "create file" in command_lower:
                filename = f"file_{int(datetime.now().timestamp())}"
                extension = ".txt" if "text" in command_lower else ".py"
                result = await self.system_tools.create_file(filename, ollama_response, extension)
                return result["message"]
            
            elif "edit file" in command_lower:
                filename = command_lower.split("edit file")[-1].strip().split()[0]
                extension = ".txt" if filename.endswith(".txt") else ".py"
                result = await self.system_tools.edit_file(
                    filename.replace(extension, ""), 
                    ollama_response, 
                    extension
                )
                return result["message"]
            
            elif "delete file" in command_lower:
                filename = command_lower.split("delete file")[-1].strip().split()[0]
                extension = ".txt" if filename.endswith(".txt") else ".py"
                result = await self.system_tools.delete_file(
                    filename.replace(extension, ""),
                    extension
                )
                return result["message"]
            
            elif "list files" in command_lower:
                result = await self.system_tools.list_files()
                return result["report"]
            
            elif "write to console" in command_lower or "write to powershell" in command_lower:
                result = await self.system_tools.write_to_active_window(ollama_response)
                return result["message"]
            
            # Handle Python script generation
            elif "python" in command_lower and "script" in command_lower:
                filename = f"script_{int(datetime.now().timestamp())}"
                result = await self.system_tools.create_file(filename, ollama_response, ".py")
                return result["message"]
            
            elif "help" in command_lower:
                return self._show_help()
            
            return ollama_response
            
        except Exception as e:
            logging.error(f"Command execution error: {str(e)}", exc_info=True)
            return f"Error executing command: {str(e)}"
            
    def _show_help(self) -> str:
        """Show help information."""
        return """
Available Commands:
- run diagnostics: Show comprehensive system status
- create file: Create a new file (text or Python)
- edit file <filename>: Edit an existing file
- delete file <filename>: Delete a file
- list files: Show all files with details
- write to console: Send text to active window
- create python script: Generate Python code
- help: Show this help message
- exit: Quit the program

Additional Features:
- Automatic error handling and logging
- File operation safety with locks
- Command history tracking
- Detailed diagnostics with top processes
- Network and battery monitoring
"""

async def main():
    """Main function to handle user input and process commands."""
    print("""Advanced System Automation Script
=================================
Features:
- OpenAI/Ollama Integration
- Comprehensive System Diagnostics
- File Operations & Management
- Active Window Text Control
- Python Script Generation

Type 'exit' to quit, 'help' for command list.""")
    
    processor = CommandProcessor()
    use_openai = bool(os.getenv("OPENAI_API_KEY"))
    
    if use_openai:
        print("\nUsing OpenAI's agent network for enhanced capabilities.")
    else:
        print("\nUsing Ollama (qwen2.5) for command processing.")
    
    while True:
        try:
            command = input("\n> ")
            if command.lower() == 'exit':
                print("\nExiting...")
                logging.info("Script terminated by user")
                break
            
            result = await processor.process_command(command, use_openai=use_openai)
            print(f"\n{result}")
            
        except KeyboardInterrupt:
            print("\nInterrupted by user. Type 'exit' to quit properly.")
        except Exception as e:
            logging.error(f"Main loop error: {str(e)}", exc_info=True)
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.critical(f"Fatal error: {str(e)}", exc_info=True)
        print(f"\nFatal error: {str(e)}")
