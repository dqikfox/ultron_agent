import os
import sys
import json
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from .base import Tool

try:
    import github3
except ImportError:
    github3 = None

logger = logging.getLogger(__name__)

class ProjectAutomationError(Exception):
    """Custom exception for project automation errors."""
    pass

class GitHubManager:
    """Manages GitHub repository operations."""
    def __init__(self, credentials: Dict[str, str]):
        self.credentials = credentials
        self.github_client = None
        self.repository = None

    def authenticate(self) -> bool:
        if not github3:
            logger.error("github3.py library is not installed. GitHub integration is disabled.")
            return False
        try:
            self.github_client = github3.login(token=self.credentials['access_token'])
            user = self.github_client.me()
            logger.info(f"Successfully authenticated with GitHub as: {user.login}")
            return True
        except Exception as e:
            logger.error(f"GitHub authentication failed: {str(e)}")
            return False

    def create_repository(self, project_name: str, description: str) -> bool:
        try:
            repo_name = project_name.replace(" ", "-").lower()
            owner = self.credentials['repo_owner']
            logger.info(f"Checking for GitHub repository: {owner}/{repo_name}")
            
            self.repository = self.github_client.repository(owner, repo_name)
            if self.repository:
                logger.info(f"Repository {repo_name} already exists.")
                return True

        except github3.exceptions.NotFoundError:
            logger.info(f"Repository {repo_name} not found. Creating new repository...")
            try:
                self.repository = self.github_client.create_repository(
                    name=repo_name,
                    description=description,
                    private=False,
                    auto_init=True,
                    gitignore_template='Python'
                )
                logger.info(f"Successfully created repository: {repo_name}")
                return True
            except Exception as e:
                logger.error(f"Failed to create repository: {str(e)}")
                return False
        except Exception as e:
            logger.error(f"An error occurred while checking repository: {str(e)}")
            return False

    def create_file(self, path: str, content: str, commit_message: str) -> bool:
        if not self.repository:
            return False
        try:
            existing_file = self.repository.file_contents(path)
            existing_file.update(commit_message, content.encode('utf-8'))
            logger.info(f"Updated existing file in repo: {path}")
        except github3.exceptions.NotFoundError:
            self.repository.create_file(path=path, message=commit_message, content=content.encode('utf-8'))
            logger.info(f"Created new file in repo: {path}")
        except Exception as e:
            logger.error(f"Failed to create/update file {path} in repo: {str(e)}")
            return False
        return True

class ProjectGenerator:
    """Orchestrates the project generation process."""
    def __init__(self, github_manager: Optional[GitHubManager]):
        self.github_manager = github_manager

    def run_automation(self, project_requirements: Dict[str, Any]) -> str:
        try:
            project_name = project_requirements['project_name']
            project_path = Path(project_name.replace(" ", "_"))
            project_path.mkdir(exist_ok=True)
            logger.info(f"Created local project directory at: {project_path.resolve()}")

            structure = project_requirements.get('project_structure', {})
            for directory, files in structure.items():
                dir_path = project_path / (directory if directory else "")
                dir_path.mkdir(parents=True, exist_ok=True)
                for file_name in files:
                    content = self._generate_file_content(file_name, project_name, project_requirements)
                    (dir_path / file_name).write_text(content, encoding='utf-8')

            if self.github_manager:
                if self.github_manager.create_repository(project_name, project_requirements.get('description', '')):
                    for dirpath, _, filenames in os.walk(project_path):
                        for filename in filenames:
                            local_path = Path(dirpath) / filename
                            repo_path = local_path.relative_to(project_path).as_posix()
                            content = local_path.read_text(encoding='utf-8')
                            self.github_manager.create_file(repo_path, content, f"feat: Add {filename}")
                    return f"Success! Project '{project_name}' created locally and on GitHub."
                return f"Warning: Project '{project_name}' created locally, but failed to create GitHub repo."
            
            return f"Success! Project '{project_name}' created locally. GitHub integration was skipped."

        except Exception as e:
            logger.error(f"Project automation failed: {e}", exc_info=True)
            return f"Error during project automation: {e}"

    def _generate_file_content(self, file_name: str, project_name: str, requirements: Dict[str, Any]) -> str:
        if file_name == "README.md":
            return f"# {project_name}\n\n{requirements.get('description', '')}\n"
        if file_name == "requirements.txt":
            return "# Add your project dependencies here\nrequests\nfastapi\nuvicorn\n"
        if file_name == "models.yaml":
            return yaml.dump({'models': requirements.get('models', [])}, default_flow_style=False, sort_keys=False)
        if file_name == ".gitignore":
            return "__pycache__/\n*.pyc\n.env\nvenv/\n*.log\n"
        if file_name.endswith(".py"):
            return f'"""Module for {file_name}"""\n\nprint("Hello from {file_name}!")\n - project_generator_tool.py:133'
        return f"# Content for {file_name}\n"

class ProjectGeneratorTool(Tool):
    def __init__(self, agent):
        self.name = "create_project"
        self.description = "Automates the setup of a new software project, including local directories and optional GitHub repository."
        self.parameters = {
            "type": "object",
            "properties": {
                "project_name": {"type": "string", "description": "The name of the new project."},
                "description": {"type": "string", "description": "A short description for the project."},
                "github_token": {"type": "string", "description": "Optional. A GitHub PAT to create and push to a repository."},
                "github_owner": {"type": "string", "description": "Optional. The GitHub username or organization to own the repository."}
            },
            "required": ["project_name", "description"]
        }
        self.agent = agent

    def match(self, user_input: str) -> bool:
        return any(keyword in user_input.lower() for keyword in ["create project", "new project", "scaffold"])

    def execute(self, project_name: str, description: str, github_token: Optional[str] = None, github_owner: Optional[str] = None) -> str:
        logger.info(f"Executing project generator for '{project_name}'")
        
        github_manager = None
        if github_token and github_owner:
            github_manager = GitHubManager({"access_token": github_token, "repo_owner": github_owner})
            if not github_manager.authenticate():
                return "GitHub authentication failed. Please check your token and owner name."
        else:
            logger.warning("GitHub details not provided. Skipping GitHub integration.")

        # This list of models is based on the user's system
        user_models = [
            {'name': 'qwen2.5vl:latest', 'size': '6.0 GB', 'type': 'vision', 'family': 'qwen'},
            {'name': 'qwen3:0.6b', 'size': '522 MB', 'type': 'text-generation', 'family': 'qwen'},
            {'name': 'qikfox/Eleven:latest', 'size': '2.0 GB', 'type': 'text-to-speech', 'family': 'eleven'},
            {'name': 'llama3.2:latest', 'size': '2.0 GB', 'type': 'text-generation', 'family': 'llama'},
            {'name': 'qwen2.5:latest', 'size': '4.7 GB', 'type': 'text-generation', 'family': 'qwen'},
            {'name': 'mxbai-embed-large:latest', 'size': '669 MB', 'type': 'embedding', 'family': 'mxbai'},
            {'name': 'Qwen2.5-7B-Mini.Q5_K_S:latest', 'size': '1.9 GB', 'type': 'text-generation', 'family': 'qwen'},
            {'name': 'L3.2-8X3B-MOE-Dark-Champion-Inst-18.4B-uncen-ablit_D_AU-Q3_k_s:latest', 'size': '8.3 GB', 'type': 'text-generation', 'family': 'llama'},
            {'name': 'phi-3-mini-128k-instruct.Q5_K_M:latest', 'size': '2.8 GB', 'type': 'text-generation', 'family': 'phi'},
            {'name': 'hermes3:latest', 'size': '4.7 GB', 'type': 'text-generation', 'family': 'hermes'},
            {'name': 'hermes3:8b', 'size': '4.7 GB', 'type': 'text-generation', 'family': 'hermes'}
        ]

        requirements = {
            "project_name": project_name,
            "description": description,
            "models": user_models,
            "project_structure": {
                "src": ["main.py", "utils.py"],
                "config": ["config.yaml", "models.yaml"],
                "tests": ["test_main.py"],
                "docs": ["README.md"],
                "": ["requirements.txt", ".gitignore"]
            }
        }

        project_generator = ProjectGenerator(github_manager)
        return project_generator.run_automation(requirements)

