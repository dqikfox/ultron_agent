"""
ULTRON Agent Project Automation Tool

This tool provides ULTRON Agent users with the ability to generate
comprehensive Python scripts for automating local AI model setup,
GitHub repository creation, and project management.

Uses Anthropic Claude API to generate production-ready automation scripts.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
import anthropic
from datetime import datetime
from pathlib import Path

# ULTRON Agent imports
from utils.ultron_logger import log_info, log_error, log_ai_decision
from ultron_agent.config import UltronConfig


class ProjectAutomationTool:
    """
    Tool for generating automated project setup scripts using Anthropic Claude

    This tool creates comprehensive Python scripts that automate:
    - Local AI model setup and configuration
    - GitHub repository creation and management
    - Project structure generation
    - Model integration and testing
    """

    name = "Project Automation Tool"
    description = (
        "Generate comprehensive Python scripts for automating AI project setup, "
        "local model management, and GitHub repository creation using Anthropic Claude."
    )

    def __init__(self, config: Optional[UltronConfig] = None):
        """Initialize the Project Automation tool"""
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.anthropic_client = None

        # Initialize Anthropic client
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key and self.config:
            api_key = getattr(self.config, 'anthropic_api_key', None)

        if api_key:
            try:
                self.anthropic_client = anthropic.Anthropic(api_key=api_key)
                log_info("project_automation_tool", "Anthropic client initialized successfully")
            except Exception as e:
                log_error("project_automation_tool", f"Failed to initialize Anthropic client: {str(e)}")
                self.anthropic_client = None
        else:
            log_error("project_automation_tool", "No Anthropic API key found")
            self.anthropic_client = None

    def match(self, command: str) -> bool:
        """
        Check if command matches Project Automation tool patterns

        Args:
            command: User command string

        Returns:
            bool: True if command matches this tool
        """
        command_lower = command.lower()

        # Match various project automation related commands
        patterns = [
            "generate project script", "create automation script",
            "project automation", "automate project setup",
            "generate python script", "create project tool",
            "ai project generator", "automation script",
            "local model setup", "github automation",
            "github repository", "repository creation",
            "project generator", "script generator"
        ]

        return any(pattern in command_lower for pattern in patterns)

    def execute(self, command: str) -> str:
        """
        Execute project automation script generation

        Args:
            command: User command string

        Returns:
            str: Generated script or error message
        """
        try:
            log_info("project_automation_tool", f"Executing command: {command}")

            # Parse command to extract parameters
            params = self._parse_command_parameters(command)

            # Generate the automation script
            script = self._generate_automation_script(params)

            if script:
                # Save the script to file
                saved_path = self._save_script_to_file(script, params)

                log_ai_decision(
                    "project_automation_tool",
                    f"Generated automation script for: {params.get('project_type', 'general project')}",
                    ai_model="claude-sonnet-4-20250514"
                )
                return f"✅ Project automation script generated successfully!\n\n📁 Saved to: {saved_path}\n\n{script[:1000]}...\n\n💡 Full script saved to the file above."
            else:
                return "❌ Failed to generate automation script. Check logs for details."

        except Exception as e:
            error_msg = f"Error executing project automation: {str(e)}"
            log_error("project_automation_tool", error_msg)
            return error_msg

    def _parse_command_parameters(self, command: str) -> Dict[str, Any]:
        """
        Parse command parameters from user input

        Args:
            command: User command string

        Returns:
            dict: Parsed parameters
        """
        params = {
            "project_type": "ai_content_generator",
            "include_models": True,
            "include_github": True,
            "complexity": "comprehensive"
        }

        command_lower = command.lower()

        # Detect project type
        if "ml" in command_lower or "machine learning" in command_lower:
            params["project_type"] = "ml_project"
        elif "web" in command_lower or "flask" in command_lower or "django" in command_lower:
            params["project_type"] = "web_app"
        elif "data" in command_lower or "analysis" in command_lower:
            params["project_type"] = "data_science"
        elif "api" in command_lower or "rest" in command_lower:
            params["project_type"] = "api_service"

        # Check for specific requirements
        if "simple" in command_lower:
            params["complexity"] = "basic"
        elif "advanced" in command_lower or "complex" in command_lower:
            params["complexity"] = "advanced"

        if "no github" in command_lower or "skip github" in command_lower:
            params["include_github"] = False
        if "no models" in command_lower or "skip models" in command_lower:
            params["include_models"] = False

        return params

    def _generate_automation_script(self, params: Dict[str, Any]) -> Optional[str]:
        """
        Generate automation script using Anthropic Claude

        Args:
            params: Script generation parameters

        Returns:
            str: Generated script or None if failed
        """
        if not self.anthropic_client:
            log_error("project_automation_tool", "Anthropic client not available")
            return None

        try:
            # Create the detailed prompt for Claude
            prompt = self._build_claude_prompt(params)

            # Make API call to Claude
            message = self.anthropic_client.beta.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=20000,
                temperature=1,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )

            # Extract the generated script
            if message.content and len(message.content) > 0:
                script_content = message.content[0].text

                # Clean up the response (remove <script> tags if present)
                if "<script>" in script_content and "</script>" in script_content:
                    start = script_content.find("<script>") + len("<script>")
                    end = script_content.find("</script>")
                    script_content = script_content[start:end].strip()

                log_info("project_automation_tool", f"Generated script of length: {len(script_content)}")
                return script_content
            else:
                log_error("project_automation_tool", "No content received from Claude API")
                return None

        except Exception as e:
            log_error("project_automation_tool", f"Claude API call failed: {str(e)}")
            return None

    def _save_script_to_file(self, script_content: str, params: Dict[str, Any]) -> str:
        """
        Save the generated script to a file in the generated_scripts directory

        Args:
            script_content: The generated script content
            params: Script generation parameters

        Returns:
            str: Path to the saved file
        """
        try:
            # Create generated_scripts directory if it doesn't exist
            scripts_dir = Path("generated_scripts")
            scripts_dir.mkdir(exist_ok=True)

            # Generate filename based on project type and timestamp
            project_type = params.get("project_type", "general")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{project_type}_automation_{timestamp}.py"
            file_path = scripts_dir / filename

            # Save the script
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(script_content)

            log_info("project_automation_tool", f"Script saved to: {file_path}")
            return str(file_path)

        except Exception as e:
            log_error("project_automation_tool", f"Failed to save script to file: {str(e)}")
            return "Failed to save script to file"

    def _build_claude_prompt(self, params: Dict[str, Any]) -> str:
        """
        Build the detailed prompt for Claude

        Args:
            params: Script generation parameters

        Returns:
            str: Complete prompt for Claude
        """
        project_type = params.get("project_type", "ai_content_generator")
        complexity = params.get("complexity", "comprehensive")
        include_models = params.get("include_models", True)
        include_github = params.get("include_github", True)

        # Base prompt structure
        prompt = f"""You are tasked with creating a Python script that automates the process of running local models and creating GitHub projects on a Windows PC without user intervention. The script should be {complexity}, well-structured, and include error handling. Follow these instructions to create the script:

1. Start by importing necessary libraries and modules for file handling, GitHub integration, and local model management.

2. Use the following input variables in your script:

<project_requirements>
{{{{PROJECT_REQUIREMENTS}}}}
</project_requirements>

<local_models>
{{{{LOCAL_MODELS}}}}
</local_models>

<github_credentials>
{{{{GITHUB_CREDENTIALS}}}}
</github_credentials>

3. Create functions for the following tasks:
   a. Setting up and configuring local models
   b. Creating and managing GitHub repositories
   c. Generating project structure and files
   d. Running local models and processing outputs
   e. Committing and pushing changes to GitHub

4. Implement error handling and logging throughout the script to capture and report any issues that may occur during execution.

5. Create a main function that orchestrates the entire process, calling the individual functions in the correct order.

6. Include comments and docstrings to explain the purpose and functionality of each section of the script.

7. At the end of the script, include a section that demonstrates how to execute the script and any required command-line arguments.

"""

        # Customize prompt based on project type
        if project_type == "ai_content_generator":
            prompt += """
Your script should focus on AI content generation, including:
- Multiple local AI model integration (GPT, BERT, T5, etc.)
- Content generation for blog posts, social media, product descriptions
- Automated content categorization and formatting
- GitHub repository setup with proper documentation
"""
        elif project_type == "ml_project":
            prompt += """
Your script should focus on machine learning projects, including:
- ML model training and evaluation pipelines
- Data preprocessing and feature engineering
- Model serialization and deployment
- Experiment tracking and versioning
"""
        elif project_type == "web_app":
            prompt += """
Your script should focus on web applications, including:
- Web framework setup (Flask/Django/FastAPI)
- Database integration and migrations
- API endpoint creation
- Frontend template generation
"""
        elif project_type == "data_science":
            prompt += """
Your script should focus on data science projects, including:
- Data ingestion and cleaning pipelines
- Exploratory data analysis automation
- Visualization generation
- Statistical analysis and reporting
"""
        elif project_type == "api_service":
            prompt += """
Your script should focus on API services, including:
- RESTful API design and implementation
- Authentication and authorization
- Request/response handling
- API documentation generation
"""

        # Add model and GitHub requirements
        if include_models:
            prompt += """
The script must include comprehensive local model management:
- Model downloading and caching
- Multi-framework support (PyTorch, TensorFlow, etc.)
- Model validation and testing
- Performance monitoring and optimization
"""
        else:
            prompt += """
Skip local model integration - focus on project structure and GitHub automation only.
"""

        if include_github:
            prompt += """
The script must include full GitHub integration:
- Repository creation and configuration
- Automated file generation and commits
- Branch management and pull requests
- Issue and project board setup
"""
        else:
            prompt += """
Skip GitHub integration - focus on local project setup only.
"""

        prompt += """
Your final output should be a complete, executable Python script that accomplishes the task of running local models and creating GitHub projects automatically. The script should be well-commented, include error handling, and be ready for execution on a Windows PC.

Provide your script within <script> tags. Do not include any explanation or commentary outside of the script itself; all necessary information should be contained within comments in the script."""

        return prompt

    @classmethod
    def schema(cls):
        """Return tool schema for ULTRON Agent tool system"""
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "command": {
                    "type": "string",
                    "description": "Project automation command (e.g., 'generate project script for AI content generator')"
                }
            }
        }


# Export the tool class
__all__ = ['ProjectAutomationTool']
