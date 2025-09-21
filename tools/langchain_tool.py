"""
Langchain Tool for ULTRON Agent 3.0

This tool provides integration with Langchain for AI chain management,
allowing users to create, execute, and manage AI workflows and chains.

Author: ULTRON Agent Development Team
Version: 1.0.0
"""

import json
import re
from typing import Dict, Any, List, Optional
from pathlib import Path

from utils.ultron_logger import log_info, log_error, log_ai_decision
from config import Config


class LangchainTool:
    """
    Langchain integration tool for ULTRON Agent.

    Provides capabilities for:
    - Creating and managing AI chains
    - Executing chain workflows
    - Managing chain configurations
    - Integrating with various AI models
    """

    name = "langchain_tool"
    description = (
        "Langchain integration for AI chain management and workflow "
        "execution. Supports creating, executing, and managing AI chains "
        "with various models."
    )

    def __init__(self):
        """Initialize the Langchain tool"""
        self.config = Config()
        self.logger = None
        self.chains_dir = Path("chains")
        self.chains_dir.mkdir(exist_ok=True)

        # Initialize Langchain components
        self._initialize_langchain()

        log_info(
            "langchain_tool",
            "Langchain tool initialized successfully"
        )

    def _initialize_langchain(self):
        """Initialize Langchain components and configurations"""
        try:
            # Import Langchain components
            from langchain.chains import LLMChain
            from langchain.prompts import PromptTemplate
            from langchain.memory import ConversationBufferMemory

            # Store references for later use
            self.LLMChain = LLMChain
            self.PromptTemplate = PromptTemplate
            self.ConversationBufferMemory = ConversationBufferMemory

            log_info("langchain_tool", "Langchain components loaded")

        except ImportError as e:
            log_error(
                "langchain_tool",
                f"Failed to import Langchain components: {str(e)}"
            )
            raise

    def match(self, command: str) -> bool:
        """
        Check if command matches Langchain tool patterns

        Args:
            command: User command string

        Returns:
            bool: True if command matches Langchain patterns
        """
        langchain_patterns = [
            r'\blangchain\b',
            r'\bchain\b.*\b(create|execute|run|manage)\b',
            r'\bai.*\b(chain|workflow)\b',
            r'\b(create|execute|run)\b.*\bchain\b',
            r'\bllm.*\bchain\b',
            r'\bprompt.*\bchain\b'
        ]

        command_lower = command.lower()
        return any(
            re.search(pattern, command_lower)
            for pattern in langchain_patterns
        )

    def execute(self, command: str) -> str:
        """
        Execute Langchain-related commands

        Args:
            command: User command string

        Returns:
            str: Execution result
        """
        try:
            log_info("langchain_tool", f"Executing command: {command}")

            # Parse command type
            if self._is_create_chain_command(command):
                return self._handle_create_chain(command)
            elif self._is_execute_chain_command(command):
                return self._handle_execute_chain(command)
            elif self._is_list_chains_command(command):
                return self._handle_list_chains(command)
            elif self._is_delete_chain_command(command):
                return self._handle_delete_chain(command)
            elif self._is_chain_status_command(command):
                return self._handle_chain_status(command)
            else:
                return self._handle_general_chain_command(command)

        except Exception as e:
            error_msg = f"Langchain tool execution failed: {str(e)}"
            log_error("langchain_tool", error_msg)
            return f"Error: {error_msg}"

    def _is_create_chain_command(self, command: str) -> bool:
        """Check if command is for creating a chain"""
        return any(keyword in command.lower() for keyword in [
            'create chain', 'new chain', 'build chain'
        ])

    def _is_execute_chain_command(self, command: str) -> bool:
        """Check if command is for executing a chain"""
        return any(keyword in command.lower() for keyword in [
            'execute chain', 'run chain', 'start chain'
        ])

    def _is_list_chains_command(self, command: str) -> bool:
        """Check if command is for listing chains"""
        return any(keyword in command.lower() for keyword in [
            'list chains', 'show chains', 'get chains'
        ])

    def _is_delete_chain_command(self, command: str) -> bool:
        """Check if command is for deleting a chain"""
        return any(keyword in command.lower() for keyword in [
            'delete chain', 'remove chain'
        ])

    def _is_chain_status_command(self, command: str) -> bool:
        """Check if command is for checking chain status"""
        return any(keyword in command.lower() for keyword in [
            'chain status', 'status chain'
        ])

    def _handle_create_chain(self, command: str) -> str:
        """Handle chain creation commands"""
        try:
            # Parse chain configuration from command
            chain_config = self._parse_chain_config(command)

            if not chain_config:
                return (
                    "Error: Could not parse chain configuration from command"
                )

            # Create the chain
            result = self._create_langchain_chain(chain_config)

            log_info(
                "langchain_tool",
                log_info(
                    "langchain_tool",
                    "Chain created successfully: "
                    f"{chain_config.get('name', 'unnamed')}"
                )
            )

            return f"Chain created successfully: {result}"

        except Exception as e:
            log_error("langchain_tool", f"Failed to create chain: {str(e)}")
            return f"Error creating chain: {str(e)}"

    def _handle_execute_chain(self, command: str) -> str:
        """Handle chain execution commands"""
        try:
            # Parse chain ID and input data
            chain_id, input_data = self._parse_chain_execution(command)

            if not chain_id:
                return "Error: Could not parse chain ID from command"

            # Execute the chain
            result = self._execute_langchain_chain(chain_id, input_data)

            log_info(
                "langchain_tool",
                f"Chain executed successfully: {chain_id}"
            )

            return f"Chain execution result: {result}"

        except Exception as e:
            log_error("langchain_tool", f"Failed to execute chain: {str(e)}")
            return f"Error executing chain: {str(e)}"

    def _handle_list_chains(self, command: str) -> str:
        """Handle list chains commands"""
        try:
            chains = self._list_langchain_chains()

            if not chains:
                return "No chains found"

            result = "Available Chains:\n"
            for chain in chains:
                result += f"- {chain['name']} (ID: {chain['id']})\n"
                if 'description' in chain:
                    result += f"  Description: {chain['description']}\n"

            return result

        except Exception as e:
            log_error("langchain_tool", f"Failed to list chains: {str(e)}")
            return f"Error listing chains: {str(e)}"

    def _handle_delete_chain(self, command: str) -> str:
        """Handle chain deletion commands"""
        try:
            chain_id = self._parse_chain_id(command)

            if not chain_id:
                return "Error: Could not parse chain ID from command"

            result = self._delete_langchain_chain(chain_id)

            log_info(
                "langchain_tool",
                f"Chain deleted successfully: {chain_id}"
            )

            return f"Chain deleted: {result}"

        except Exception as e:
            log_error("langchain_tool", f"Failed to delete chain: {str(e)}")
            return f"Error deleting chain: {str(e)}"

    def _handle_chain_status(self, command: str) -> str:
        """Handle chain status commands"""
        try:
            chain_id = self._parse_chain_id(command)

            if not chain_id:
                return "Error: Could not parse chain ID from command"

            status = self._get_chain_status(chain_id)

            return f"Chain Status: {status}"

        except Exception as e:
            log_error(
                "langchain_tool",
                f"Failed to get chain status: {str(e)}"
            )
            return f"Error getting chain status: {str(e)}"

    def _handle_general_chain_command(self, command: str) -> str:
        """Handle general chain-related commands"""
        return (
            "Langchain Tool Help:\n"
            "- Create chain: 'create chain name=my_chain model=gpt-4'\n"
            "- Execute chain: 'execute chain id=my_chain_id input=hello'\n"
            "- List chains: 'list chains'\n"
            "- Delete chain: 'delete chain id=my_chain_id'\n"
            "- Chain status: 'chain status id=my_chain_id'"
        )

    def _create_langchain_chain(
        self, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new Langchain chain"""
        try:
            chain_name = config.get('name', 'unnamed_chain')
            model_name = config.get('model', 'gpt-3.5-turbo')
            template = config.get('template', 'Tell me about {topic}')

            # Create prompt template (placeholder for future use)
            # prompt = self.PromptTemplate(
            #     input_variables=['topic'],
            #     template=template
            # )

            # Create chain configuration
            chain_data = {
                'id': f"chain_{chain_name}_{hash(str(config))}",
                'name': chain_name,
                'model': model_name,
                'template': template,
                'config': config,
                'created_at': str(self._get_current_time())
            }

            # Save chain configuration
            self._save_chain_config(chain_data)

            return chain_data

        except Exception as e:
            raise Exception(f"Failed to create chain: {str(e)}")

    def _execute_langchain_chain(
        self, chain_id: str, input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a Langchain chain"""
        try:
            # Load chain configuration
            chain_config = self._load_chain_config(chain_id)

            if not chain_config:
                raise Exception(f"Chain not found: {chain_id}")

            # Initialize LLM (placeholder - would integrate with actual LLM)
            # This is a simplified version for demonstration
            result = {
                'chain_id': chain_id,
                'input': input_data,
                'output': (
                    f"Chain {chain_id} executed with input: {input_data}"
                ),
                'timestamp': str(self._get_current_time())
            }

            log_ai_decision(
                "langchain_tool",
                f"Executed chain {chain_id}",
                ai_model=chain_config.get('model', 'unknown')
            )

            return result

        except Exception as e:
            raise Exception(f"Failed to execute chain: {str(e)}")

    def _list_langchain_chains(self) -> List[Dict[str, Any]]:
        """List all available chains"""
        try:
            chains = []
            for config_file in self.chains_dir.glob("*.json"):
                try:
                    with open(config_file, 'r') as f:
                        chain_data = json.load(f)
                        chains.append({
                            'id': chain_data['id'],
                            'name': chain_data['name'],
                            'description': chain_data.get('description', ''),
                            'model': chain_data.get('model', 'unknown')
                        })
                except Exception as e:
                    log_error(
                        "langchain_tool",
                        f"Failed to load chain config {config_file}: {str(e)}"
                    )

            return chains

        except Exception as e:
            raise Exception(f"Failed to list chains: {str(e)}")

    def _delete_langchain_chain(self, chain_id: str) -> Dict[str, Any]:
        """Delete a Langchain chain"""
        try:
            config_file = self.chains_dir / f"{chain_id}.json"

            if not config_file.exists():
                raise Exception(f"Chain not found: {chain_id}")

            config_file.unlink()

            return {
                'success': True,
                'message': f"Chain {chain_id} deleted successfully"
            }

        except Exception as e:
            raise Exception(f"Failed to delete chain: {str(e)}")

    def _get_chain_status(self, chain_id: str) -> Dict[str, Any]:
        """Get status of a chain"""
        try:
            chain_config = self._load_chain_config(chain_id)

            if not chain_config:
                return {'status': 'not_found'}

            return {
                'status': 'available',
                'name': chain_config.get('name', 'unknown'),
                'model': chain_config.get('model', 'unknown'),
                'last_modified': chain_config.get('created_at', 'unknown')
            }

        except Exception as e:
            return {'status': 'error', 'error': str(e)}

    def _parse_chain_config(self, command: str) -> Optional[Dict[str, Any]]:
        """Parse chain configuration from command"""
        config = {}

        # Extract name
        if "name=" in command:
            name_match = re.search(r'name=([^\s]+)', command)
            if name_match:
                config['name'] = name_match.group(1)

        # Extract model
        if "model=" in command:
            model_match = re.search(r'model=([^\s]+)', command)
            if model_match:
                config['model'] = model_match.group(1)

        # Extract template
        if "template=" in command:
            template_part = command.split("template=")[1]
            if template_part.startswith('"'):
                config['template'] = template_part.split('"')[1]
            else:
                config['template'] = template_part.split()[0]

        return config if config else None

    def _parse_chain_execution(self, command: str) -> tuple:
        """Parse chain ID and input data from command"""
        chain_id = None
        input_data = {}

        # Extract chain ID
        if "id=" in command:
            id_match = re.search(r'id=([^\s]+)', command)
            if id_match:
                chain_id = id_match.group(1)

        # Extract input data
        if "input=" in command:
            input_part = command.split("input=")[1]
            if input_part.startswith('"'):
                input_data['topic'] = input_part.split('"')[1]
            else:
                input_data['topic'] = input_part.split()[0]

        return chain_id, input_data

    def _parse_chain_id(self, command: str) -> Optional[str]:
        """Parse chain ID from command"""
        if "id=" in command:
            id_match = re.search(r'id=([^\s]+)', command)
            if id_match:
                return id_match.group(1)
        return None

    def _save_chain_config(self, chain_data: Dict[str, Any]):
        """Save chain configuration to file"""
        config_file = self.chains_dir / f"{chain_data['id']}.json"
        with open(config_file, 'w') as f:
            json.dump(chain_data, f, indent=2)

    def _load_chain_config(self, chain_id: str) -> Optional[Dict[str, Any]]:
        """Load chain configuration from file"""
        config_file = self.chains_dir / f"{chain_id}.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        return None

    def _get_current_time(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now()

    @classmethod
    def schema(cls):
        """Return tool schema for ULTRON Agent tool system"""
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "command": {
                    "type": "string",
                    "description": "Langchain command to execute"
                }
            }
        }


# Export the tool class
__all__ = ['LangchainTool']
