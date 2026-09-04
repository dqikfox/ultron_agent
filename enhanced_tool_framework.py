#!/usr/bin/env python3
"""Enhanced Tool Integration Framework"""

import os
import json
import requests
import subprocess
from typing import Dict, List, Any, Optional
from utils.ultron_logger import log_info, log_error

class ToolRegistry:
    def __init__(self):
        self.tools = {}
        self.load_tools()
    
    def load_tools(self):
        """Load all available tools"""
        self.tools = {
            "file_system": FileSystemTool(),
            "web_browser": WebBrowserTool(),
            "api_connector": APIConnectorTool(),
            "database": DatabaseTool(),
            "email": EmailTool(),
            "system_control": SystemControlTool()
        }
        log_info("tool_registry", f"Loaded {len(self.tools)} tools")
    
    def get_tool(self, name: str):
        """Get tool by name"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all available tools"""
        return list(self.tools.keys())

class BaseTool:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute tool action"""
        raise NotImplementedError

class FileSystemTool(BaseTool):
    def __init__(self):
        super().__init__("file_system", "File system operations")
    
    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        try:
            if action == "read":
                path = kwargs.get("path")
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {"success": True, "content": content}
            
            elif action == "write":
                path = kwargs.get("path")
                content = kwargs.get("content", "")
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return {"success": True, "message": f"File written: {path}"}
            
            elif action == "list":
                path = kwargs.get("path", ".")
                files = os.listdir(path)
                return {"success": True, "files": files}
            
            elif action == "create_dir":
                path = kwargs.get("path")
                os.makedirs(path, exist_ok=True)
                return {"success": True, "message": f"Directory created: {path}"}
            
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
        
        except Exception as e:
            log_error("file_system_tool", f"Action {action} failed: {e}")
            return {"success": False, "error": str(e)}

class WebBrowserTool(BaseTool):
    def __init__(self):
        super().__init__("web_browser", "Web browsing and scraping")
    
    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        try:
            if action == "get":
                url = kwargs.get("url")
                response = requests.get(url, timeout=10)
                return {"success": True, "content": response.text, "status_code": response.status_code}
            
            elif action == "search":
                query = kwargs.get("query")
                # Simple search using DuckDuckGo
                search_url = f"https://duckduckgo.com/html/?q={query}"
                response = requests.get(search_url, timeout=10)
                return {"success": True, "results": response.text[:1000]}
            
            elif action == "download":
                url = kwargs.get("url")
                filename = kwargs.get("filename", "download.tmp")
                response = requests.get(url, timeout=30)
                with open(filename, 'wb') as f:
                    f.write(response.content)
                return {"success": True, "message": f"Downloaded: {filename}"}
            
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
        
        except Exception as e:
            log_error("web_browser_tool", f"Action {action} failed: {e}")
            return {"success": False, "error": str(e)}

class APIConnectorTool(BaseTool):
    def __init__(self):
        super().__init__("api_connector", "API integrations")
        self.api_keys = self._load_api_keys()
    
    def _load_api_keys(self) -> Dict[str, str]:
        """Load API keys from config"""
        try:
            with open("ultron_config.json", 'r') as f:
                config = json.load(f)
                return config.get("api_keys", {})
        except:
            return {}
    
    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        try:
            if action == "github":
                return self._github_api(kwargs)
            elif action == "slack":
                return self._slack_api(kwargs)
            else:
                return {"success": False, "error": f"Unknown API: {action}"}
        
        except Exception as e:
            log_error("api_connector_tool", f"API {action} failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _github_api(self, params: Dict) -> Dict[str, Any]:
        """GitHub API integration"""
        token = self.api_keys.get("github_token")
        if not token:
            return {"success": False, "error": "GitHub token not configured"}
        
        operation = params.get("operation", "list_repos")
        headers = {"Authorization": f"token {token}"}
        
        if operation == "list_repos":
            response = requests.get("https://api.github.com/user/repos", headers=headers)
            return {"success": True, "repos": response.json()}
        
        return {"success": False, "error": f"Unknown GitHub operation: {operation}"}
    
    def _slack_api(self, params: Dict) -> Dict[str, Any]:
        """Slack API integration"""
        token = self.api_keys.get("slack_token")
        if not token:
            return {"success": False, "error": "Slack token not configured"}
        
        # Placeholder for Slack integration
        return {"success": True, "message": "Slack integration placeholder"}

class DatabaseTool(BaseTool):
    def __init__(self):
        super().__init__("database", "Database operations")
    
    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        try:
            if action == "sqlite_query":
                db_path = kwargs.get("db_path")
                query = kwargs.get("query")
                
                import sqlite3
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute(query)
                
                if query.strip().upper().startswith("SELECT"):
                    results = cursor.fetchall()
                    conn.close()
                    return {"success": True, "results": results}
                else:
                    conn.commit()
                    conn.close()
                    return {"success": True, "message": "Query executed"}
            
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
        
        except Exception as e:
            log_error("database_tool", f"Action {action} failed: {e}")
            return {"success": False, "error": str(e)}

class EmailTool(BaseTool):
    def __init__(self):
        super().__init__("email", "Email automation")
    
    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        # Placeholder for email functionality
        return {"success": True, "message": f"Email {action} - placeholder implementation"}

class SystemControlTool(BaseTool):
    def __init__(self):
        super().__init__("system_control", "System control operations")
    
    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        try:
            if action == "run_command":
                command = kwargs.get("command")
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
                return {
                    "success": True,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "return_code": result.returncode
                }
            
            elif action == "get_processes":
                result = subprocess.run("tasklist", shell=True, capture_output=True, text=True)
                return {"success": True, "processes": result.stdout}
            
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
        
        except Exception as e:
            log_error("system_control_tool", f"Action {action} failed: {e}")
            return {"success": False, "error": str(e)}

# Global tool registry instance
tool_registry = ToolRegistry()