"""
Copilot CLI Self-Prompting Automation Tool

Integrates GitHub Copilot CLI for autonomous task execution,
self-improvement, and delegated code modifications.
"""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum

from tools.tool_interface import ToolInterface
from utils.ultron_logger import log_info, log_error, log_ai_decision
from utils.event_system import get_event_system
from diagnostics import diagnostic_wrapper


class TaskPriority(Enum):
    """Task priority levels for Copilot CLI automation"""
    CRITICAL = 1      # Blocking issues, security, core functionality
    HIGH = 2           # Performance, stability improvements
    MEDIUM = 3         # Code quality, documentation, technical debt
    LOW = 4             # Nice-to-have improvements, refactoring


class CopilotCLIAutomationTool(ToolInterface):
    """
    Tool for orchestrating self-prompting automation through Copilot CLI.

    Enables ULTRON Agent to:
    - Autonomously delegate tasks to Copilot coding agent
    - Create self-improvement workflows
    - Coordinate multi-step code modifications
    - Generate and execute automated prompts
    - Integrate with GitHub workflows
    """

    def __init__(self):
        """Initialize Copilot CLI automation tool"""
        self.copilot_available = self._check_copilot_availability()
        self.config = self._load_config()
        self.task_queue: List[Dict[str, Any]] = []
        self.session_history: Dict[str, List[str]] = {}
        self.trusted_dirs = self._load_trusted_directories()

        log_info(
            "copilot_cli_tool",
            f"Initialized. Copilot CLI available: {self.copilot_available}",
            config_loaded=bool(self.config)
        )

    @property
    def name(self) -> str:
        return "Copilot CLI Automation"

    @property
    def description(self) -> str:
        return (
            "Orchestrates GitHub Copilot CLI for autonomous task execution, "
            "self-improvement automation, and delegated code modifications. "
            "Enables self-prompting workflows with Copilot coding agent."
        )

    def match(self, command: str) -> bool:
        """Check if command should trigger Copilot CLI automation"""
        keywords = [
            "copilot", "delegate", "self-improve", "auto-refactor",
            "copilot cli", "automation task", "generate task",
            "create workflow", "self-prompt"
        ]
        return any(kw in command.lower() for kw in keywords)

    @diagnostic_wrapper("copilot_cli_tool", track_performance=True)
    def execute(self, command: str, **kwargs) -> str:
        """Execute Copilot CLI automation task"""
        try:
            log_ai_decision(
                "copilot_cli_tool",
                f"Executing command: {command}",
                ai_model="copilot-cli",
                confidence_score=0.85
            )

            # Parse command intent
            intent, task_details = self._parse_command(command)

            # Route to appropriate handler
            if intent == "delegate":
                return self._handle_delegation(task_details)
            elif intent == "workflow":
                return self._handle_workflow(task_details)
            elif intent == "self_prompt":
                return self._handle_self_prompt(task_details)
            elif intent == "status":
                return self._handle_status(task_details)
            else:
                return f"Unknown Copilot CLI intent: {intent}"

        except Exception as e:
            log_error("copilot_cli_tool", f"Execution failed: {e}", exception=e)
            return f"Error: {e}"

    @classmethod
    def schema(cls) -> Dict[str, Any]:
        """Return tool schema for OpenAI-compatible function calling"""
        return {
            "name": "copilot_cli_automation",
            "description": (
                "Orchestrate GitHub Copilot CLI for autonomous task execution "
                "and self-improvement workflows"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": (
                            "Task command: 'delegate <task>', 'workflow <name>', "
                            "'self-prompt <goal>', 'status'"
                        )
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["critical", "high", "medium", "low"],
                        "description": "Task priority level"
                    },
                    "target_file": {
                        "type": "string",
                        "description": "Specific file to work with (optional)"
                    },
                    "approval_required": {
                        "type": "boolean",
                        "description": "Require human approval before execution"
                    }
                },
                "required": ["command"]
            }
        }

    # ========== PRIVATE METHODS ==========

    def _check_copilot_availability(self) -> bool:
        """Check if Copilot CLI is installed and available"""
        try:
            result = subprocess.run(
                ["copilot", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _load_config(self) -> Dict[str, Any]:
        """Load Copilot CLI configuration"""
        config_paths = [
            Path.home() / ".config" / "copilot" / "config.json",
            Path.home() / ".copilot" / "config.json",
            Path("ultron_config.json")
        ]

        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path) as f:
                        return json.load(f)
                except Exception as e:
                    log_error("copilot_cli_tool", f"Failed to load config: {e}")

        return {}

    def _load_trusted_directories(self) -> List[str]:
        """Load trusted directories for Copilot CLI"""
        trusted = []

        # Get from environment
        if env_trusted := os.getenv("COPILOT_TRUSTED_DIRS"):
            trusted.extend(env_trusted.split(";"))

        # Get from config
        if "trusted_directories" in self.config:
            trusted.extend(self.config["trusted_directories"])

        # Add project root as trusted
        trusted.append(str(Path.cwd()))

        return list(set(trusted))  # Remove duplicates

    def _parse_command(self, command: str) -> Tuple[str, Dict[str, Any]]:
        """Parse command into intent and details"""
        parts = command.split(maxsplit=1)
        intent = parts[0].lower()
        details_str = parts[1] if len(parts) > 1 else ""

        # Parse details
        details = {
            "raw_command": command,
            "content": details_str,
            "timestamp": datetime.now().isoformat()
        }

        return intent, details

    def _handle_delegation(self, task_details: Dict[str, Any]) -> str:
        """Handle task delegation to Copilot coding agent"""
        task_description = task_details.get("content", "")

        if not task_description:
            return "Error: No task description provided for delegation"

        log_info(
            "copilot_cli_tool",
            f"Delegating task: {task_description[:100]}..."
        )

        # Prepare delegation command
        copilot_prompt = self._prepare_delegation_prompt(task_description)

        # Execute Copilot CLI with delegation
        try:
            result = self._run_copilot_interactive([
                f"delegate {copilot_prompt}"
            ])

            # Parse result for PR/session link
            pr_link = self._extract_pr_link(result)

            log_ai_decision(
                "copilot_cli_tool",
                "Task delegated successfully",
                ai_model="copilot-cli",
                confidence_score=0.95,
                reasoning=f"PR: {pr_link}"
            )

            return (
                f"✅ Task delegated successfully\n"
                f"Description: {task_description}\n"
                f"PR Link: {pr_link}\n\n"
                f"Copilot coding agent will create a draft PR and notify you."
            )

        except Exception as e:
            log_error("copilot_cli_tool", f"Delegation failed: {e}", exception=e)
            return f"❌ Delegation failed: {e}"

    def _handle_workflow(self, task_details: Dict[str, Any]) -> str:
        """Handle multi-step workflow execution"""
        workflow_name = task_details.get("content", "default")

        log_info("copilot_cli_tool", f"Starting workflow: {workflow_name}")

        workflows = {
            "quality_scan": self._workflow_quality_scan,
            "optimization": self._workflow_optimization,
            "documentation": self._workflow_documentation,
            "testing": self._workflow_testing,
        }

        workflow_func = workflows.get(workflow_name.lower())
        if not workflow_func:
            return f"Unknown workflow: {workflow_name}"

        try:
            result = workflow_func()
            return result
        except Exception as e:
            log_error("copilot_cli_tool", f"Workflow failed: {e}", exception=e)
            return f"❌ Workflow failed: {e}"

    def _handle_self_prompt(self, task_details: Dict[str, Any]) -> str:
        """Handle self-prompting automation"""
        goal = task_details.get("content", "")

        if not goal:
            return "Error: No goal provided for self-prompting"

        log_info("copilot_cli_tool", f"Self-prompting with goal: {goal}")

        # Generate autonomous prompts based on goal
        prompts = self._generate_self_prompts(goal)

        results = []
        for i, prompt in enumerate(prompts, 1):
            log_info("copilot_cli_tool", f"Executing self-prompt {i}/{len(prompts)}")
            try:
                result = self._run_copilot_interactive([prompt])
                results.append(result)
            except Exception as e:
                log_error("copilot_cli_tool", f"Self-prompt {i} failed: {e}")
                results.append(f"Failed: {e}")

        summary = f"Self-prompting complete: {len(results)} tasks executed"
        log_ai_decision(
            "copilot_cli_tool",
            summary,
            ai_model="copilot-cli",
            confidence_score=0.88
        )

        return f"✅ {summary}\n\nResults:\n" + "\n".join(results)

    def _handle_status(self, task_details: Dict[str, Any]) -> str:
        """Handle status query"""
        status_info = {
            "copilot_available": self.copilot_available,
            "pending_tasks": len(self.task_queue),
            "trusted_directories": self.trusted_dirs,
            "recent_sessions": list(self.session_history.keys())[-5:],
        }

        return json.dumps(status_info, indent=2)

    def _prepare_delegation_prompt(self, task: str) -> str:
        """Prepare a well-formatted delegation prompt"""
        # Add context from copilot-instructions.md
        context = (
            "ULTRON Agent 3.0 - Multi-modal AI platform with Ollama backend, "
            "voice interface, and MCP integration. "
            "Follow patterns in .github/copilot-instructions.md"
        )

        return f"{context}\n\nTask: {task}"

    def _run_copilot_interactive(self, commands: List[str]) -> str:
        """Run Copilot CLI with interactive commands"""
        if not self.copilot_available:
            return "Error: Copilot CLI not available"

        try:
            # Build the copilot command
            cmd = ["copilot"]

            # Add interactive commands
            cmd_input = "\n".join(commands) + "\nexit\n"

            # Execute copilot
            result = subprocess.run(
                cmd,
                input=cmd_input,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=Path.cwd()
            )

            return result.stdout if result.returncode == 0 else result.stderr

        except subprocess.TimeoutExpired:
            return "Error: Copilot CLI command timed out"
        except Exception as e:
            return f"Error running Copilot CLI: {e}"

    def _extract_pr_link(self, output: str) -> str:
        """Extract PR link from Copilot output"""
        # Look for common PR link patterns
        import re
        pr_pattern = r"https://github\.com/[^\s/]+/[^\s/]+/pull/\d+"
        match = re.search(pr_pattern, output)
        return match.group(0) if match else "PR link not found"

    def _generate_self_prompts(self, goal: str) -> List[str]:
        """Generate autonomous prompts based on goal"""
        prompts = []

        if "quality" in goal.lower():
            prompts = [
                "Analyze codebase for code quality issues and generate fixes",
                "Generate type hints for untyped functions",
                "Create missing docstrings for public methods",
                "Refactor code with complex cyclomatic complexity",
            ]

        elif "performance" in goal.lower():
            prompts = [
                "Profile agent_core.py and identify performance bottlenecks",
                "Optimize tool discovery caching in agent_core.py",
                "Implement connection pooling for Ollama backend",
                "Reduce memory footprint of event_system.py",
            ]

        elif "documentation" in goal.lower():
            prompts = [
                "Generate API documentation for api_server.py",
                "Create architecture diagrams for SYSTEM_ARCHITECTURE.md",
                "Generate tool schemas for all tools/ plugins",
                "Create deployment guide for run.bat configuration",
            ]

        elif "testing" in goal.lower():
            prompts = [
                "Generate unit tests for utils/ultron_logger.py",
                "Create integration tests for MCP server communication",
                "Generate test fixtures in conftest.py",
                "Create mocks for external service dependencies",
            ]

        else:
            # Generic self-improvement prompts
            prompts = [
                f"Analyze ULTRON Agent for improvements related to: {goal}",
                f"Generate a technical debt report for: {goal}",
            ]

        return prompts

    # ========== WORKFLOW HANDLERS ==========

    def _workflow_quality_scan(self) -> str:
        """Workflow: Full code quality scan and fixes"""
        tasks = [
            "Run pylint on all Python files and fix violations",
            "Generate type hints using pyright analysis",
            "Create missing docstrings for public API",
            "Refactor functions with high cyclomatic complexity",
        ]

        return self._execute_workflow("quality_scan", tasks)

    def _workflow_optimization(self) -> str:
        """Workflow: Performance optimization"""
        tasks = [
            "Identify and fix N+1 query patterns",
            "Implement caching for repeated operations",
            "Optimize async/await patterns",
            "Profile and optimize hot paths",
        ]

        return self._execute_workflow("optimization", tasks)

    def _workflow_documentation(self) -> str:
        """Workflow: Documentation generation"""
        tasks = [
            "Generate API documentation",
            "Create architecture diagrams",
            "Generate tool specifications",
            "Create deployment procedures",
        ]

        return self._execute_workflow("documentation", tasks)

    def _workflow_testing(self) -> str:
        """Workflow: Testing improvements"""
        tasks = [
            "Generate unit test coverage",
            "Create integration test suite",
            "Generate test fixtures",
            "Create mocks for dependencies",
        ]

        return self._execute_workflow("testing", tasks)

    def _execute_workflow(self, workflow_name: str, tasks: List[str]) -> str:
        """Execute a workflow of tasks"""
        log_info("copilot_cli_tool", f"Starting workflow: {workflow_name}")

        results = []
        for task in tasks:
            try:
                result = self._run_copilot_interactive([task])
                results.append(f"✅ {task[:50]}...")
            except Exception as e:
                results.append(f"❌ {task[:50]}... ({e})")

        return f"Workflow '{workflow_name}' completed:\n\n" + "\n".join(results)


# Export tool
__all__ = ["CopilotCLIAutomationTool"]
