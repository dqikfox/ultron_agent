#!/usr/bin/env python3
"""Unity Hub Integration Tool for ULTRON Agent"""

import os
import json
import subprocess
import requests
from pathlib import Path
from tools.tool_interface import ToolInterface
from utils.ultron_logger import log_info, log_error

class UnityHubTool(ToolInterface):
    """Unity Hub integration for project management"""

    @property
    def name(self) -> str:
        return "Unity Hub Tool"

    @property
    def description(self) -> str:
        return "Manage Unity projects and integrate ULTRON Agent"

    def match(self, command: str) -> bool:
        keywords = ["unity", "hub", "project", "create unity", "unity project"]
        return any(kw in command.lower() for kw in keywords)

    def execute(self, command: str, **kwargs) -> str:
        try:
            cmd_lower = command.lower()
            
            if "create" in cmd_lower and "project" in cmd_lower:
                return self._create_unity_project(command)
            elif "list" in cmd_lower:
                return self._list_unity_projects()
            elif "integrate" in cmd_lower:
                return self._integrate_ultron(command)
            elif "status" in cmd_lower:
                return self._check_unity_status()
            elif "config" in cmd_lower or "settings" in cmd_lower:
                return self._check_unity_config()
            elif "auth" in cmd_lower:
                return self._setup_unity_auth(command)
            elif "remote" in cmd_lower or "config" in cmd_lower:
                return self._handle_remote_config(command)
            else:
                return self._show_help()
                
        except Exception as e:
            log_error("unity_hub_tool", f"Error: {e}")
            return f"Unity Hub tool error: {e}"

    def _create_unity_project(self, command: str) -> str:
        """Create new Unity project with ULTRON integration"""
        
        # Extract project name from command
        words = command.split()
        project_name = "UltronGame"
        for i, word in enumerate(words):
            if word.lower() in ["project", "called", "named"] and i + 1 < len(words):
                project_name = words[i + 1]
                break
        
        projects_dir = Path.home() / "Unity Projects"
        project_path = projects_dir / project_name
        
        try:
            # Create project directory
            project_path.mkdir(parents=True, exist_ok=True)
            
            # Create Unity project structure
            assets_dir = project_path / "Assets"
            scripts_dir = assets_dir / "Scripts"
            ultron_dir = scripts_dir / "ULTRON"
            
            assets_dir.mkdir(exist_ok=True)
            scripts_dir.mkdir(exist_ok=True)
            ultron_dir.mkdir(exist_ok=True)
            
            # Copy ULTRON integration files
            self._copy_ultron_files(ultron_dir)
            
            # Create project settings
            self._create_project_settings(project_path, project_name)
            
            log_info("unity_hub_tool", f"Created Unity project: {project_name}")
            
            return f"✅ Created Unity project '{project_name}' with ULTRON integration at: {project_path}"
            
        except Exception as e:
            return f"❌ Failed to create project: {e}"

    def _copy_ultron_files(self, ultron_dir: Path):
        """Copy ULTRON integration files to Unity project"""
        
        ultron_files = [
            "UnityUltronClient.cs",
            "UnityExampleUsage.cs"
        ]
        
        for file_name in ultron_files:
            source_file = Path(__file__).parent.parent / file_name
            if source_file.exists():
                dest_file = ultron_dir / file_name
                dest_file.write_text(source_file.read_text())

    def _create_project_settings(self, project_path: Path, project_name: str):
        """Create Unity project settings"""
        
        project_settings = {
            "m_EditorVersion": "2022.3.0f1",
            "m_EditorVersionWithRevision": "2022.3.0f1 (fb119bb0b476)",
            "projectName": project_name,
            "ultronIntegration": {
                "enabled": True,
                "serverUrl": "http://localhost:9000",
                "version": "1.0"
            }
        }
        
        project_version_file = project_path / "ProjectSettings" / "ProjectVersion.txt"
        project_version_file.parent.mkdir(exist_ok=True)
        
        with open(project_version_file, 'w') as f:
            f.write(f"m_EditorVersion: {project_settings['m_EditorVersion']}\n")
            f.write(f"m_EditorVersionWithRevision: {project_settings['m_EditorVersionWithRevision']}\n")

    def _list_unity_projects(self) -> str:
        """List Unity projects"""
        
        projects_dir = Path.home() / "Unity Projects"
        if not projects_dir.exists():
            return "No Unity Projects directory found"
        
        projects = []
        for item in projects_dir.iterdir():
            if item.is_dir():
                # Check if it's a Unity project
                if (item / "Assets").exists() or (item / "ProjectSettings").exists():
                    has_ultron = (item / "Assets" / "Scripts" / "ULTRON").exists()
                    status = "🤖 ULTRON" if has_ultron else "📁 Unity"
                    projects.append(f"{status} {item.name}")
        
        if not projects:
            return "No Unity projects found"
        
        return "Unity Projects:\n" + "\n".join(projects)

    def _integrate_ultron(self, command: str) -> str:
        """Integrate ULTRON into existing Unity project"""
        
        # Extract project name
        words = command.split()
        project_name = None
        for i, word in enumerate(words):
            if word.lower() in ["into", "with"] and i + 1 < len(words):
                project_name = words[i + 1]
                break
        
        if not project_name:
            return "❌ Please specify project name: 'integrate ultron into MyProject'"
        
        projects_dir = Path.home() / "Unity Projects"
        project_path = projects_dir / project_name
        
        if not project_path.exists():
            return f"❌ Project '{project_name}' not found"
        
        try:
            # Create ULTRON directory
            ultron_dir = project_path / "Assets" / "Scripts" / "ULTRON"
            ultron_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy integration files
            self._copy_ultron_files(ultron_dir)
            
            # Create example scene setup
            self._create_example_scene(project_path)
            
            return f"✅ ULTRON integration added to '{project_name}'"
            
        except Exception as e:
            return f"❌ Integration failed: {e}"

    def _create_example_scene(self, project_path: Path):
        """Create example scene with ULTRON setup"""
        
        scenes_dir = project_path / "Assets" / "Scenes"
        scenes_dir.mkdir(exist_ok=True)
        
        example_scene = scenes_dir / "UltronExample.unity"
        if not example_scene.exists():
            # Create basic Unity scene file
            scene_content = """%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!29 &1
OcclusionCullingSettings:
  m_ObjectHideFlags: 0
  serializedVersion: 2
  m_OcclusionBakeSettings:
    smallestOccluder: 5
    smallestHole: 0.25
    backfaceThreshold: 100
  m_SceneGUID: 00000000000000000000000000000000
  m_OcclusionCullingData: {fileID: 0}
--- !u!104 &2
RenderSettings:
  m_ObjectHideFlags: 0
  serializedVersion: 9
  m_Fog: 0
  m_FogColor: {r: 0.5, g: 0.5, b: 0.5, a: 1}
"""
            example_scene.write_text(scene_content)

    def _check_unity_status(self) -> str:
        """Check Unity Hub and Unity Editor status"""
        
        status_info = []
        
        # Check Unity Hub
        try:
            result = subprocess.run(["Unity Hub.exe", "--version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                status_info.append("✅ Unity Hub: Available")
            else:
                status_info.append("❌ Unity Hub: Not found")
        except:
            status_info.append("❌ Unity Hub: Not installed")
        
        # Check Unity Editor installations
        unity_installs = self._find_unity_installations()
        if unity_installs:
            status_info.append(f"✅ Unity Editors: {len(unity_installs)} found")
            for install in unity_installs[:3]:  # Show first 3
                status_info.append(f"   📦 {install}")
            # Check your specific installation
            if "6000.2.9f1" in unity_installs:
                status_info.append("   🎯 Your version (6000.2.9f1): Ready")
        else:
            status_info.append("❌ Unity Editor: Not found")
        
        # Check ULTRON integration server
        try:
            import requests
            response = requests.get("http://localhost:9000/unity/connect", timeout=2)
            status_info.append("✅ ULTRON Integration Server: Running")
        except:
            status_info.append("❌ ULTRON Integration Server: Not running")
        
        return "\n".join(status_info)

    def _find_unity_installations(self) -> list:
        """Find Unity Editor installations"""
        
        installations = []
        
        # Common Unity installation paths
        unity_paths = [
            Path("C:/Program Files/Unity/Hub/Editor"),
            Path.home() / "AppData/Roaming/UnityHub/installs"
        ]
        
        for base_path in unity_paths:
            if base_path.exists():
                for item in base_path.iterdir():
                    if item.is_dir():
                        unity_exe = item / "Editor" / "Unity.exe"
                        if unity_exe.exists():
                            installations.append(item.name)
        
        return installations

    def _check_unity_config(self) -> str:
        """Check Unity configuration API"""
        
        try:
            # Test Unity configuration API
            response = requests.get("https://config.unity3d.com/api/v1/settings", timeout=5)
            
            if response.status_code == 401:
                return "🔐 Unity Config API: Requires authentication\n" + \
                       "Use 'unity auth setup' to configure credentials"
            elif response.status_code == 200:
                return "✅ Unity Config API: Authenticated and accessible"
            else:
                return f"⚠️ Unity Config API: HTTP {response.status_code}"
                
        except Exception as e:
            return f"❌ Unity Config API: Connection failed - {e}"

    def _setup_unity_auth(self, command: str) -> str:
        """Setup Unity authentication"""
        
        config_file = Path.home() / ".ultron" / "unity_config.json"
        config_file.parent.mkdir(exist_ok=True)
        
        if "setup" in command.lower():
            # Create auth config template
            auth_config = {
                "unity_project_id": "your-project-id",
                "unity_api_key": "your-api-key",
                "unity_organization_id": "your-org-id",
                "config_api_url": "https://config.unity3d.com/api/v1/settings"
            }
            
            with open(config_file, 'w') as f:
                json.dump(auth_config, f, indent=2)
            
            return f"🔧 Unity auth config created at: {config_file}\n" + \
                   "Please edit the file with your Unity credentials:\n" + \
                   "• Project ID from Unity Dashboard\n" + \
                   "• API Key from Unity Services\n" + \
                   "• Organization ID from Unity Cloud"
        
        elif "test" in command.lower():
            # Test authentication
            if not config_file.exists():
                return "❌ No auth config found. Run 'unity auth setup' first"
            
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                headers = {
                    "Authorization": f"Bearer {config.get('unity_api_key', '')}",
                    "Content-Type": "application/json"
                }
                
                response = requests.get(
                    config.get('config_api_url', 'https://config.unity3d.com/api/v1/settings'),
                    headers=headers,
                    timeout=5
                )
                
                if response.status_code == 200:
                    return "✅ Unity authentication successful"
                elif response.status_code == 401:
                    return "❌ Unity authentication failed - check API key"
                else:
                    return f"⚠️ Unity API returned: HTTP {response.status_code}"
                    
            except Exception as e:
                return f"❌ Auth test failed: {e}"
        
        else:
            return "Unity Auth Commands:\n" + \
                   "• 'unity auth setup' - Create auth config\n" + \
                   "• 'unity auth test' - Test authentication"

    def _handle_remote_config(self, command: str) -> str:
        """Handle Unity Remote Config operations"""
        cmd_lower = command.lower()
        if "list" in cmd_lower and "env" in cmd_lower:
            return self._list_environments()
        elif "get" in cmd_lower:
            return self._get_config()
        elif "create" in cmd_lower:
            return self._create_config(command)
        else:
            return "🌐 Remote Config: list environments | get config | create config [name]"

    def _list_environments(self) -> str:
        """List Unity Remote Config environments"""
        config = self._load_unity_config()
        if not config:
            return "❌ Unity auth not configured. Run 'unity auth setup' first"
        
        try:
            import base64
            key_id = config.get('unity_key_id', '')
            secret_key = config.get('unity_secret_key', '')
            credentials = f"{key_id}:{secret_key}"
            auth_token = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                "Authorization": f"Basic {auth_token}",
                "Content-Type": "application/json"
            }
            
            project_id = config.get('unity_project_id')
            url = f"https://services.api.unity.com/remote-config/v1/projects/{project_id}/environments"
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                environments = data.get('environments', [])
                result = "🌍 Unity Remote Config Environments:\n"
                for env in environments:
                    name = env.get('name', 'Unknown')
                    env_id = env.get('id', 'N/A')
                    is_default = env.get('isDefault', False)
                    status = "🏠 Default" if is_default else "📁 Environment"
                    result += f"   {status} {name} (ID: {env_id})\n"
                return result
            else:
                return f"❌ Failed to list environments: HTTP {response.status_code}"
        except Exception as e:
            return f"❌ Environment list error: {e}"

    def _get_config(self) -> str:
        """Get Unity Remote Config"""
        config = self._load_unity_config()
        if not config:
            return "❌ Unity auth not configured. Run 'unity auth setup' first"
        
        try:
            import base64
            key_id = config.get('unity_key_id', '')
            secret_key = config.get('unity_secret_key', '')
            credentials = f"{key_id}:{secret_key}"
            auth_token = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                "Authorization": f"Basic {auth_token}",
                "Content-Type": "application/json"
            }
            
            project_id = config.get('unity_project_id')
            url = f"https://services.api.unity.com/remote-config/v1/projects/{project_id}/configs"
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                configs = data.get('configs', [])
                result = "⚙️ Unity Remote Configs:\n"
                for cfg in configs:
                    cfg_type = cfg.get('type', 'unknown')
                    cfg_id = cfg.get('id', 'N/A')
                    value_count = len(cfg.get('value', []))
                    result += f"   📋 {cfg_type} (ID: {cfg_id}) - {value_count} settings\n"
                return result
            else:
                return f"❌ Failed to get configs: HTTP {response.status_code}"
        except Exception as e:
            return f"❌ Config get error: {e}"

    def _create_config(self, command: str) -> str:
        """Create Unity Remote Config with ULTRON settings"""
        config = self._load_unity_config()
        if not config:
            return "❌ Unity auth not configured. Run 'unity auth setup' first"
        
        try:
            import base64
            key_id = config.get('unity_key_id', '')
            secret_key = config.get('unity_secret_key', '')
            credentials = f"{key_id}:{secret_key}"
            auth_token = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                "Authorization": f"Basic {auth_token}",
                "Content-Type": "application/json"
            }
            
            project_id = config.get('unity_project_id')
            
            # Get default environment
            env_url = f"https://services.api.unity.com/remote-config/v1/projects/{project_id}/environments/default"
            env_response = requests.get(env_url, headers=headers, timeout=10)
            
            if env_response.status_code != 200:
                return f"❌ Failed to get default environment: HTTP {env_response.status_code}"
            
            env_data = env_response.json()
            environment_id = env_data.get('id')
            
            # Create ULTRON config
            config_data = {
                "environmentId": environment_id,
                "type": "settings",
                "value": [
                    {"key": "ultron_enabled", "type": "bool", "value": True},
                    {"key": "ultron_server_url", "type": "string", "value": "http://localhost:9000"},
                    {"key": "ultron_ai_model", "type": "string", "value": "llava:7b"},
                    {"key": "ultron_voice_enabled", "type": "bool", "value": True}
                ]
            }
            
            url = f"https://services.api.unity.com/remote-config/v1/projects/{project_id}/configs"
            response = requests.post(url, headers=headers, json=config_data, timeout=10)
            
            if response.status_code == 200:
                result_data = response.json()
                config_id = result_data.get('id', 'N/A')
                return f"✅ Created ULTRON config (ID: {config_id})\nSettings: ultron_enabled, ultron_server_url, ultron_ai_model, ultron_voice_enabled"
            else:
                return f"❌ Failed to create config: HTTP {response.status_code}"
        except Exception as e:
            return f"❌ Config creation error: {e}"

    def _load_unity_config(self) -> dict:
        """Load Unity configuration"""
        config_file = Path.home() / ".ultron" / "unity_config.json"
        if not config_file.exists():
            return None
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except:
            return None

    def _show_help(self) -> str:
        """Show Unity Hub tool help"""
        
        return """Unity Hub Tool Commands:
        
🎮 Project Management:
• "create unity project [name]" - Create new Unity project with ULTRON
• "list unity projects" - List existing Unity projects
• "integrate ultron into [project]" - Add ULTRON to existing project

🔧 Status & Info:
• "unity status" - Check Unity Hub and Editor status
• "unity config" - Check Unity configuration API
• "unity auth setup" - Setup Unity API authentication
• "unity auth test" - Test Unity API authentication
• "list remote config environments" - List Unity environments
• "get remote config" - Get current configurations
• "create remote config" - Create ULTRON config
• "unity help" - Show this help

📁 Example Usage:
• "create unity project MyGame"
• "integrate ultron into ExistingGame"
• "list unity projects"

🚀 Quick Start:
1. Create project: "create unity project MyAIGame"
2. Start ULTRON server: run start_unity_integration.bat
3. Open Unity project and add UnityUltronClient component
"""

    @classmethod
    def schema(cls) -> dict:
        return {
            "name": "unity_hub_tool",
            "description": "Manage Unity projects and integrate ULTRON Agent",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Unity Hub command to execute"
                    }
                },
                "required": ["command"]
            }
        }