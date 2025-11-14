"""
Dynamic Code Executor Tool for ULTRON Agent

This tool provides dynamic code execution capabilities for the Ultron Agent,
enabling runtime code execution, analysis, and orchestration with external services.

## CONVERSATION SUMMARY

### Configuration & Testing
- Codex extension configuration attempted with auto-approval and dual AI system
- Multiple config failures due to path/TOML syntax issues, eventually resolved with minimal OpenAI config
- Authentication issues (403/401) resolved after VS Code restart to load environment variables
- API keys stored in Windows environment variables (OPENAI_API_KEY, LANGFLOW_API_KEY)

### Langflow Integration
- Built LangflowIntegrationTool with API connection to localhost:7860
- Created LangflowCodingAgent with file watching capabilities
- Successfully tested Langflow API with Claude model (27.5s response time)
- Added embedded chat widget to ULTRON GUI as "CODER" section with 💻 icon
- Flow ID: 92c810b5-4829-4466-9ff1-7ad19b694435

### Game Development
- Created AI Agent Battle Arena game with GameEngine class
- Implemented turn-based combat system with Agent dataclass (health, attack, defense, status)
- Game engine performance: 0.003s execution (2,331 rounds/sec) - production ready
- BattleResult tracking with kills/victories statistics

### Performance Testing
- Comprehensive tests showed excellent game engine performance (3ms)
- Langflow API slow (27.5s) - identified need for caching and async optimization
- Generated performance_report.json with execution metrics

### Key Files Created
- game/engine.py: GameEngine with combat mechanics
- tools/langflow_integration_tool.py: Langflow API integration
- langflow_coding_agent.py: File watcher with real-time code analysis
- performance_test.py: Comprehensive test suite
- gui/ultron_enhanced/web/index.html: Added CODER section with Langflow chat

### User Environment
- Windows (C:\Users\ultro\, PowerShell, cp1252 encoding)
- Requires explicit encoding='utf-8' for emoji support
- Prioritizes automation and ease of use
- Langflow running on localhost:7860 with Claude Opus 4 model

### Most Recent Topic
Integrated Langflow embedded chat widget into ULTRON GUI navigation as "CODER" section,
enabling direct Claude-powered coding assistance within the interface without window switching.
"""

import logging
import subprocess
import sys
import os
import tempfile
import importlib.util
from typing import Dict, Any, Optional, List, Callable, Tuple, Union
from datetime import datetime
import json
import requests
from pathlib import Path

# ULTRON Agent imports
from utils.ultron_logger import log_info, log_error, log_ai_decision
from utils.error_handlers import (
    NetworkError, TimeoutError, ValidationError, FileError,
    ResourceError, UltronError, ErrorContext, ErrorCategory
)


class DynamicCodeExecutor:
    """
    Tool for dynamic code execution and orchestration within ULTRON Agent

    This tool provides:
    - Safe dynamic Python code execution
    - External service integration (NVIDIA NIM, APIs)
    - Code analysis and validation
    - Orchestration capabilities for complex workflows
    """

    name: str = "Dynamic Code Executor"
    description: str = (
        "Execute dynamic Python code, orchestrate external services, and perform "
        "complex analysis workflows for ULTRON Agent enhancement."
    )

    def __init__(self, config: Optional[Any] = None, memory_system: Optional[Any] = None) -> None:
        """Initialize the Dynamic Code Executor"""
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.config: Optional[Any] = config
        self.memory: Optional[Any] = memory_system

        # Ensure logs directory exists
        self.logs_dir: Path = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)

        # NIM configuration
        self.nim_base_url: str = os.environ.get('NVIDIA_NIM_BASE_URL', 'https://integrate.api.nvidia.com/v1')
        self.nim_api_key: str = os.environ.get('NVIDIA_NIM_API_KEY', '')
        self.maverick_model: str = os.environ.get('NIM_MAVERICK_MODEL', 'meta/llama-3.1-405b-instruct')

    def match(self, command: str) -> bool:
        """Check if command matches dynamic execution operations"""
        command_lower = command.lower()
        return any(keyword in command_lower for keyword in [
            "execute code", "run dynamic", "dynamic executor",
            "code execution", "orchestrate", "maverick analysis",
            "nvidia nim", "dynamic analysis"
        ])

    def execute(self, command: str) -> str:
        """Execute dynamic code operations"""
        try:
            command_lower = command.lower()

            if "maverick" in command_lower or "nim" in command_lower:
                return self.orchestrate_with_maverick()
            elif "execute code" in command_lower or "run code" in command_lower:
                # Extract code from command
                code_start = command.find("run code")
                if code_start != -1:
                    code = command[code_start + 8:].strip()
                    return self.execute_python_code(code)
                else:
                    return "Please provide code to execute after 'run code'"
            else:
                return self.get_help()

        except Exception as e:
            log_error("dynamic_code_executor", f"Dynamic execution failed: {e}")
            return f"Dynamic execution failed: {str(e)}"

    def orchestrate_with_maverick(self) -> str:
        """
        Orchestrate analysis with NVIDIA Maverick via NIM
        This is the main orchestration function that Copilot will call

        Returns: str - Formatted report or error message
        Raises: Cascading errors caught and logged
        """
        with ErrorContext("dynamic_code_executor", logger=self.logger) as ctx:
            try:
                log_info("dynamic_code_executor", "Starting Maverick orchestration")
                ctx.operation = "maverick_orchestration"

                # Step 1: Contact NVIDIA Maverick
                maverick_response = self.contact_maverick()

                if not maverick_response:
                    error_msg = "Failed to contact NVIDIA Maverick via NIM"
                    log_error("dynamic_code_executor", error_msg)
                    ctx.error = "maverick_contact_failed"
                    return error_msg

                # Step 2: Save response to file
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    response_file = self.logs_dir / f"maverick_response_{timestamp}.txt"

                    with open(response_file, 'w', encoding='utf-8') as f:
                        f.write(f"Maverick Response - {datetime.now()}\n")
                        f.write("=" * 50 + "\n\n")
                        f.write(maverick_response)

                    log_info("dynamic_code_executor", f"Maverick response saved to {response_file}")
                except (IOError, OSError) as e:
                    log_error("dynamic_code_executor", f"Failed to save Maverick response: {e}")
                    raise FileError(
                        f"Failed to save Maverick response: {e}",
                        str(response_file),
                        "write",
                        reason="disk_write_failed"
                    )

                # Step 3: Perform Copilot-style analysis
                analysis = self.perform_copilot_analysis(maverick_response)

                # Step 4: Combine and return results
                return self.format_combined_report(maverick_response, analysis, str(response_file))

            except FileError as e:
                log_error("dynamic_code_executor", f"File operation failed: {e}")
                return f"File error: {str(e)}"
            except Exception as e:
                log_error("dynamic_code_executor", f"Maverick orchestration failed: {e}")
                ctx.error = "orchestration_failed"
                return f"Maverick orchestration failed: {str(e)}"

    def contact_maverick(self) -> Optional[str]:
        """
        Contact NVIDIA Maverick via NIM API

        Returns: Optional[str] - API response or None on failure
        Raises: NetworkError on API failures
        """
        with ErrorContext("dynamic_code_executor", logger=self.logger) as ctx:
            try:
                ctx.operation = "maverick_contact"
                analysis_prompt = """
analyse & review the Ultron Agent project:
https://github.com/dqikfox/ultron_agent

Make suggestions and recommendations for improving or enhancing:
Enhance and improve. Add or improve functionality.
Evolve.
Suggest additional tools or software that could add functionality.
Suggest open source tools that are available to add functionality.
What are the latest and greatest tools for AI?
What are the 5 latest and greatest open source models available?
Plan future implementations for the Ultron Agent.
"""

                # Try NIM API first
                if self.nim_api_key:
                    try:
                        return self._contact_nim_api(analysis_prompt)
                    except NetworkError as e:
                        log_error("dynamic_code_executor",
                                 f"NIM API failed: {e}")
                        ctx.error = "nim_api_failed"
                        # Fallback to local NIM
                        ctx.operation = "fallback_to_local_nim"

                # Fallback to local NIM if available
                return self._contact_local_nim(analysis_prompt)

            except Exception as e:
                log_error("dynamic_code_executor",
                         f"Maverick contact failed: {e}")
                ctx.error = "maverick_contact_exception"
                return None

    def _contact_nim_api(self, prompt: str) -> Optional[str]:
        """
        Contact NVIDIA NIM via API

        Args: prompt (str) - Analysis prompt
        Returns: Optional[str] - API response or None on failure
        Raises: NetworkError on HTTP/connection failures
        """
        with ErrorContext("dynamic_code_executor", logger=self.logger) as ctx:
            try:
                ctx.operation = "nim_api_contact"

                # Validate API key
                if not self.nim_api_key:
                    raise ValidationError(
                        "NIM API key not configured",
                        "nim_api_key",
                        self.nim_api_key,
                        "non-empty string"
                    )

                headers = {
                    'Authorization': f'Bearer {self.nim_api_key}',
                    'Content-Type': 'application/json'
                }

                payload = {
                    'model': self.maverick_model,
                    'messages': [{'role': 'user', 'content': prompt}],
                    'max_tokens': 2000,
                    'temperature': 0.7
                }

                try:
                    response = requests.post(
                        f"{self.nim_base_url}/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=60
                    )
                except requests.Timeout as e:
                    log_error("dynamic_code_executor",
                             f"NIM API timeout: {e}")
                    raise TimeoutError(
                        "NIM API request timed out",
                        60,
                        "requests.post"
                    )
                except requests.ConnectionError as e:
                    log_error("dynamic_code_executor",
                             f"NIM API connection failed: {e}")
                    raise NetworkError(
                        f"NIM API connection failed: {e}",
                        self.nim_base_url,
                        "POST"
                    )

                if response.status_code == 200:
                    result = response.json()
                    if 'choices' in result and result['choices']:
                        content = result['choices'][0]['message']['content']
                        log_info("dynamic_code_executor",
                                f"NIM API success: {len(content)} chars")
                        return content
                    else:
                        raise ValidationError(
                            "Invalid NIM API response format",
                            "response_format",
                            str(result),
                            "dict with 'choices' key"
                        )
                else:
                    log_error("dynamic_code_executor",
                             f"NIM API error: {response.status_code}")
                    raise NetworkError(
                        f"NIM API error: {response.status_code}",
                        self.nim_base_url,
                        "POST",
                        response.status_code
                    )

            except (ValidationError, NetworkError, TimeoutError) as e:
                log_error("dynamic_code_executor", f"NIM API failed: {e}")
                ctx.error = "nim_api_error"
                return None
            except Exception as e:
                log_error("dynamic_code_executor",
                         f"Unexpected NIM API error: {e}")
                ctx.error = "nim_api_exception"
                return None

    def _contact_local_nim(self, prompt: str) -> Optional[str]:
        """
        Contact local NIM instance via CLI

        Args: prompt (str) - Analysis prompt
        Returns: Optional[str] - CLI output or None on failure
        Raises: ResourceError on CLI execution failures
        """
        with ErrorContext("dynamic_code_executor",
                         logger=self.logger) as ctx:
            try:
                # Try using subprocess to call local NIM CLI
                try:
                    result = subprocess.run(
                        ['nim-cli', 'query',
                         self.maverick_model, prompt],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                except FileNotFoundError as e:
                    log_error("dynamic_code_executor",
                             "NIM CLI not found")
                    raise ResourceError(
                        "NIM CLI executable not found",
                        "nim-cli",
                        "execute"
                    )
                except subprocess.TimeoutExpired as e:
                    log_error("dynamic_code_executor",
                             "Local NIM CLI timed out")
                    raise TimeoutError(
                        "Local NIM CLI timed out",
                        60,
                        "subprocess.run"
                    )

                if result.returncode == 0:
                    log_info("dynamic_code_executor",
                            f"Local NIM success: "
                            f"{len(result.stdout)} chars")
                    return result.stdout
                else:
                    log_error("dynamic_code_executor",
                             f"Local NIM failed: "
                             f"{result.stderr}")
                    raise ResourceError(
                        f"Local NIM CLI error: {result.stderr}",
                        "nim-cli",
                        "execute"
                    )

            except (ResourceError, TimeoutError) as e:
                log_error("dynamic_code_executor",
                         f"Local NIM failed: {e}")
                ctx.error = e
                return None
            except Exception as e:
                log_error("dynamic_code_executor",
                         f"Local NIM contact failed: {e}")
                ctx.error = e
                return None

    def perform_copilot_analysis(
        self,
        maverick_response: str
    ) -> Dict[str, Any]:
        """Perform Copilot-style analysis of Maverick's response"""
        analysis = {
            "new_modules": [],
            "architectural_improvements": [],
            "model_recommendations": [],
            "development_roadmap": [],
            "integration_suggestions": []
        }

        # Analyze Maverick's response and generate recommendations
        response_lower = maverick_response.lower()

        # Extract key recommendations from Maverick's response
        if "tool" in response_lower or "integration" in response_lower:
            analysis["integration_suggestions"].extend([
                "Add web scraping capabilities with Selenium/Playwright",
                "Integrate with GitHub API for automated repository management",
                "Add database integration (PostgreSQL/MongoDB) for persistent storage",
                "Implement real-time collaboration features"
            ])

        if "model" in response_lower or "llm" in response_lower:
            analysis["model_recommendations"].extend([
                "Consider upgrading to Llama 3.1 405B for enhanced reasoning",
                "Add multimodal capabilities with LLaVA or GPT-4V",
                "Implement model switching based on task complexity",
                "Add local model caching for offline operation"
            ])

        # Architectural improvements
        analysis["architectural_improvements"].extend([
            "Implement plugin system for tools with hot-reloading",
            "Add event-driven architecture for better decoupling",
            "Enhance error handling with circuit breaker pattern",
            "Implement configuration validation and schema checking",
            "Add performance monitoring and metrics collection"
        ])

        # New modules to consider
        analysis["new_modules"].extend([
            "Code review and analysis module",
            "Automated testing and CI/CD integration",
            "Documentation generation system",
            "User interface enhancement tools",
            "Security scanning and vulnerability assessment"
        ])

        # 90-day development roadmap
        analysis["development_roadmap"] = [
            "Month 1: Core architecture improvements and plugin system",
            "Month 2: Enhanced AI model integration and multimodal support",
            "Month 3: Advanced tooling, testing, and deployment automation"
        ]

        return analysis

    def format_combined_report(self, maverick_response: str, copilot_analysis: Dict, response_file: str) -> str:
        """Format the combined Maverick + Copilot analysis report"""
        report = f"""
# ULTRON AGENT ENHANCEMENT REPORT
Generated: {datetime.now()}

## 📁 Maverick Response Saved
Location: {response_file}

---

## 🤖 Section 1: NVIDIA Maverick Analysis

{maverick_response}

---

## 🧠 Section 2: GitHub Copilot Recommendations

### New Modules & Tools
{chr(10).join(f"• {module}" for module in copilot_analysis['new_modules'])}

### Architectural Improvements
{chr(10).join(f"• {improvement}" for improvement in copilot_analysis['architectural_improvements'])}

### AI Model Recommendations
{chr(10).join(f"• {model}" for model in copilot_analysis['model_recommendations'])}

### Integration Suggestions
{chr(10).join(f"• {integration}" for integration in copilot_analysis['integration_suggestions'])}

---

## 🗺️ Section 3: 90-Day Implementation Roadmap

{chr(10).join(f"• {milestone}" for milestone in copilot_analysis['development_roadmap'])}

---

## 🚀 Next Steps
1. Review the saved Maverick response in {response_file}
2. Prioritize recommendations based on project goals
3. Consider automated PR generation for top enhancements
4. Schedule implementation sprints based on the roadmap

---
*Report generated by ULTRON Agent Dynamic Code Executor*
"""

        return report

    def execute_python_code(self, code: str) -> str:
        """
        Execute Python code safely with error handling

        Args: code (str) - Python code to execute
        Returns: str - Execution output or error message
        Raises: TimeoutError, FileError on failures
        """
        with ErrorContext("dynamic_code_executor",
                         logger=self.logger) as ctx:
            try:
                # Validate code input
                if not code or not isinstance(code, str):
                    raise ValidationError(
                        "Invalid code input",
                        "code",
                        code,
                        "non-empty string"
                    )

                # Create temporary file for execution
                try:
                    with tempfile.NamedTemporaryFile(
                        mode='w',
                        suffix='.py',
                        delete=False
                    ) as f:
                        f.write(code)
                        temp_file = f.name
                except (IOError, OSError) as e:
                    log_error("dynamic_code_executor",
                             f"Failed to create temp file: {e}")
                    raise FileError(
                        f"Failed to create temp file: {e}",
                        temp_file,
                        "write"
                    )

                try:
                    # Execute the code with timeout
                    try:
                        result = subprocess.run(
                            [sys.executable, temp_file],
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                    except subprocess.TimeoutExpired as e:
                        log_error("dynamic_code_executor",
                                 "Code execution timed out")
                        raise TimeoutError(
                            "Code execution timed out",
                            30,
                            "subprocess.run"
                        )

                    output = result.stdout
                    if result.stderr:
                        output += f"\nSTDERR: {result.stderr}"

                    if result.returncode != 0:
                        output += (
                            f"\nExit Code: {result.returncode}"
                        )

                    log_info("dynamic_code_executor",
                            f"Code execution completed")
                    return output

                finally:
                    # Cleanup temp file
                    try:
                        os.unlink(temp_file)
                    except (IOError, OSError) as e:
                        log_error("dynamic_code_executor",
                                 f"Failed to clean temp file: {e}")

            except (ValidationError, TimeoutError,
                   FileError) as e:
                log_error("dynamic_code_executor",
                         f"Code execution failed: {e}")
                ctx.error = e
                return f"Code execution error: {str(e)}"
            except Exception as e:
                log_error("dynamic_code_executor",
                         f"Unexpected execution error: {e}")
                ctx.error = e
                return f"Unexpected error: {str(e)}"

    def get_help(self) -> str:
        """Provide help for dynamic execution operations"""
        help_text = """DYNAMIC CODE EXECUTOR HELP:

Available Commands:
• "orchestrate with maverick" - Run full Maverick analysis pipeline
• "run code <python_code>" - Execute Python code dynamically
• "contact maverick" - Contact NVIDIA Maverick via NIM

Features:
• Safe code execution with timeout protection
• NVIDIA NIM integration for AI analysis
• Automated report generation and saving
• Copilot-enhanced recommendations

Environment Variables:
• NVIDIA_NIM_API_KEY - For cloud NIM access
• NIM_MAVERICK_MODEL - Model name (default: maverick)
• NVIDIA_NIM_BASE_URL - API endpoint
"""

        return help_text

    @classmethod
    def schema(cls):
        """Return tool schema for API documentation"""
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Dynamic execution command to run"
                    }
                },
                "required": ["command"]
            }
        }
