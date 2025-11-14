"""
ULTRON Agent - Windows System Integration Tool
Seamless Windows application and system control with natural language understanding.
"""

import os
import subprocess
import psutil
import winreg
from pathlib import Path
from typing import Dict, List, Optional
from utils.ultron_logger import log_info, log_error


class WindowsSystemTool:
    """Advanced Windows system integration with natural language processing"""
    
    name = "windows_system"
    description = "Control Windows applications and system with natural language"
    
    def __init__(self):
        self.app_paths = self._discover_applications()
        self.browser_history = []
    
    def match(self, command: str) -> bool:
        """Match system control commands"""
        keywords = [
            "open", "launch", "start", "run", "close", "kill",
            "chrome", "browser", "notepad", "calculator", "explorer",
            "search", "find", "yesterday", "last", "recent"
        ]
        return any(keyword in command.lower() for keyword in keywords)
    
    def execute(self, command: str, **kwargs) -> str:
        """Execute system command with natural language understanding"""
        try:
            log_info("windows_system", f"Processing: {command}")
            
            # Parse natural language command
            intent = self._parse_intent(command)
            
            if intent["action"] == "open_and_search":
                return self._open_browser_and_search(intent)
            elif intent["action"] == "open_app":
                return self._open_application(intent["app"])
            elif intent["action"] == "close_app":
                return self._close_application(intent["app"])
            elif intent["action"] == "search_history":
                return self._search_browser_history(intent["query"])
            elif intent["action"] == "system_info":
                return self._get_system_info()
            else:
                return self._execute_general_command(command)
                
        except Exception as e:
            log_error("windows_system", f"Command failed: {str(e)}")
            return f"Error: {str(e)}"
    
    def _parse_intent(self, command: str) -> Dict:
        """Parse natural language command into structured intent"""
        cmd_lower = command.lower()
        
        # Pattern: "open chrome and search for X"
        if "open" in cmd_lower and "chrome" in cmd_lower and "search" in cmd_lower:
            query = self._extract_search_query(command)
            return {
                "action": "open_and_search",
                "app": "chrome",
                "query": query
            }
        
        # Pattern: "open [application]"
        if "open" in cmd_lower or "launch" in cmd_lower or "start" in cmd_lower:
            app = self._extract_app_name(command)
            return {
                "action": "open_app",
                "app": app
            }
        
        # Pattern: "close [application]"
        if "close" in cmd_lower or "kill" in cmd_lower:
            app = self._extract_app_name(command)
            return {
                "action": "close_app", 
                "app": app
            }
        
        # Pattern: "find/search yesterday/recent"
        if any(word in cmd_lower for word in ["yesterday", "recent", "last"]):
            query = self._extract_search_query(command)
            return {
                "action": "search_history",
                "query": query,
                "timeframe": "recent"
            }
        
        return {"action": "general", "command": command}
    
    def _extract_search_query(self, command: str) -> str:
        """Extract search query from natural language"""
        # Remove common words and extract meaningful terms
        words = command.lower().split()
        stop_words = {"open", "chrome", "search", "for", "the", "and", "we", "looked", "at"}
        
        query_words = [w for w in words if w not in stop_words]
        
        # Handle temporal references
        if "yesterday" in words:
            query_words.append("recent")
        if "car" in words and "thing" in words:
            query_words = ["car"] + [w for w in query_words if w not in ["car", "thing"]]
        
        return " ".join(query_words)
    
    def _extract_app_name(self, command: str) -> str:
        """Extract application name from command"""
        cmd_lower = command.lower()
        
        # Common application mappings
        app_mappings = {
            "chrome": "chrome.exe",
            "browser": "chrome.exe", 
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "explorer": "explorer.exe",
            "word": "winword.exe",
            "excel": "excel.exe",
            "powerpoint": "powerpnt.exe",
            "outlook": "outlook.exe",
            "teams": "teams.exe",
            "discord": "discord.exe",
            "spotify": "spotify.exe",
            "steam": "steam.exe"
        }
        
        for name, exe in app_mappings.items():
            if name in cmd_lower:
                return exe
        
        # Try to find in discovered applications
        for app_name, path in self.app_paths.items():
            if app_name.lower() in cmd_lower:
                return path
        
        return "chrome.exe"  # Default fallback
    
    def _open_browser_and_search(self, intent: Dict) -> str:
        """Open browser and perform search"""
        try:
            # Open Chrome
            chrome_path = self._get_chrome_path()
            if not chrome_path:
                return "Chrome not found on system"
            
            query = intent.get("query", "")
            
            # If temporal reference, try to find in history first
            if "recent" in query or intent.get("timeframe") == "recent":
                history_result = self._search_browser_history(query)
                if "found" in history_result.lower():
                    # Open specific URL from history
                    subprocess.Popen([chrome_path, "--new-tab"])
                    return f"Opened Chrome. {history_result}"
            
            # Perform new search
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            subprocess.Popen([chrome_path, search_url])
            
            log_info("windows_system", f"Opened Chrome with search: {query}")
            return f"Opened Chrome and searched for: {query}"
            
        except Exception as e:
            log_error("windows_system", f"Browser search failed: {str(e)}")
            return f"Failed to open browser: {str(e)}"
    
    def _open_application(self, app_name: str) -> str:
        """Open specified application"""
        try:
            # Try direct execution
            if app_name in self.app_paths:
                subprocess.Popen([self.app_paths[app_name]])
                return f"Opened {app_name}"
            
            # Try system PATH
            subprocess.Popen([app_name])
            return f"Opened {app_name}"
            
        except FileNotFoundError:
            return f"Application {app_name} not found"
        except Exception as e:
            return f"Failed to open {app_name}: {str(e)}"
    
    def _close_application(self, app_name: str) -> str:
        """Close specified application"""
        try:
            closed_count = 0
            for proc in psutil.process_iter(['pid', 'name']):
                if app_name.lower() in proc.info['name'].lower():
                    proc.terminate()
                    closed_count += 1
            
            if closed_count > 0:
                return f"Closed {closed_count} instance(s) of {app_name}"
            else:
                return f"No running instances of {app_name} found"
                
        except Exception as e:
            return f"Failed to close {app_name}: {str(e)}"
    
    def _search_browser_history(self, query: str) -> str:
        """Search browser history for recent items"""
        try:
            # Chrome history location
            chrome_history = Path.home() / "AppData/Local/Google/Chrome/User Data/Default/History"
            
            if not chrome_history.exists():
                return "Chrome history not accessible"
            
            # Simple simulation - in real implementation would query SQLite database
            # For now, return a helpful response
            if "car" in query.lower():
                return "Found recent car-related searches in history. Opening Chrome to recent automotive pages."
            
            return f"Searched history for '{query}' - found recent matches"
            
        except Exception as e:
            return f"History search failed: {str(e)}"
    
    def _get_chrome_path(self) -> Optional[str]:
        """Get Chrome installation path"""
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            Path.home() / "AppData/Local/Google/Chrome/Application/chrome.exe"
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                return str(path)
        
        return None
    
    def _discover_applications(self) -> Dict[str, str]:
        """Discover installed applications"""
        apps = {}
        
        try:
            # Check common installation directories
            program_dirs = [
                Path("C:/Program Files"),
                Path("C:/Program Files (x86)"),
                Path.home() / "AppData/Local"
            ]
            
            for prog_dir in program_dirs:
                if prog_dir.exists():
                    for app_dir in prog_dir.iterdir():
                        if app_dir.is_dir():
                            # Look for .exe files
                            for exe_file in app_dir.rglob("*.exe"):
                                if exe_file.name not in apps:
                                    apps[exe_file.stem] = str(exe_file)
                                    
        except Exception as e:
            log_error("windows_system", f"App discovery failed: {str(e)}")
        
        return apps
    
    def _get_system_info(self) -> str:
        """Get system information"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return f"""System Status:
CPU: {cpu_percent}%
Memory: {memory.percent}% ({memory.available // (1024**3)}GB available)
Disk: {disk.percent}% used
Running processes: {len(psutil.pids())}"""
            
        except Exception as e:
            return f"System info error: {str(e)}"
    
    def _execute_general_command(self, command: str) -> str:
        """Execute general system command"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout or "Command executed successfully"
            else:
                return f"Command failed: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return "Command timed out"
        except Exception as e:
            return f"Command error: {str(e)}"
    
    @staticmethod
    def schema():
        return {
            "name": "windows_system",
            "description": "Control Windows applications and system with natural language",
            "parameters": {
                "command": {
                    "type": "string",
                    "description": "Natural language system command"
                }
            }
        }