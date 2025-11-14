"""
ULTRON Self-Prompting Orchestrator

Coordinates autonomous self-improvement workflows using Copilot CLI,
event system, and multi-AI coordination for continuous platform enhancement.
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Coroutine
import logging

from utils.ultron_logger import log_info, log_error, log_ai_decision
from utils.event_system import get_event_system
from diagnostics import diagnostic_wrapper


class SelfPromptingOrchestrator:
    """
    Orchestrates autonomous self-improvement tasks through:
    - Copilot CLI delegations
    - GitHub Actions workflows
    - Multi-AI coordination
    - Event-driven automation
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize orchestrator"""
        self.config = config or {}
        self.event_system = get_event_system()
        self.task_history: List[Dict[str, Any]] = []
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.improvement_metrics: Dict[str, Any] = {}

        log_info(
            "self_prompting_orchestrator",
            "Initialized autonomous improvement orchestrator"
        )

    async def start_improvement_cycle(
        self,
        cycle_name: str,
        goals: List[str],
        priority: str = "medium"
    ) -> Dict[str, Any]:
        """
        Start a complete self-improvement cycle.

        Args:
            cycle_name: Name for this improvement cycle
            goals: List of improvement goals
            priority: Task priority (critical, high, medium, low)

        Returns:
            Cycle metadata and results
        """
        log_ai_decision(
            "self_prompting_orchestrator",
            f"Starting improvement cycle: {cycle_name}",
            ai_model="orchestrator",
            confidence_score=0.9
        )

        cycle_id = f"{cycle_name}_{datetime.now().isoformat()}"
        cycle_data = {
            "id": cycle_id,
            "name": cycle_name,
            "goals": goals,
            "priority": priority,
            "start_time": datetime.now().isoformat(),
            "status": "running",
            "tasks": [],
            "results": []
        }

        try:
            # Emit cycle start event
            await self.event_system.emit("improvement_cycle_start", cycle_data)

            # Generate tasks for each goal
            for goal in goals:
                tasks = await self._generate_improvement_tasks(goal, priority)
                cycle_data["tasks"].extend(tasks)

            # Execute tasks sequentially
            for task in cycle_data["tasks"]:
                result = await self._execute_improvement_task(task)
                cycle_data["results"].append(result)

            # Compile cycle summary
            cycle_data["status"] = "completed"
            cycle_data["end_time"] = datetime.now().isoformat()
            cycle_summary = self._compile_cycle_summary(cycle_data)

            # Emit cycle completion event
            await self.event_system.emit(
                "improvement_cycle_complete",
                cycle_summary
            )

            # Store in history
            self.task_history.append(cycle_data)

            return cycle_summary

        except Exception as e:
            log_error(
                "self_prompting_orchestrator",
                f"Cycle failed: {e}",
                exception=e
            )
            cycle_data["status"] = "failed"
            cycle_data["error"] = str(e)
            return cycle_data

    async def _generate_improvement_tasks(
        self,
        goal: str,
        priority: str
    ) -> List[Dict[str, Any]]:
        """Generate specific improvement tasks for a goal"""
        tasks = []

        goal_lower = goal.lower()

        if "performance" in goal_lower:
            tasks = await self._generate_performance_tasks(priority)
        elif "quality" in goal_lower:
            tasks = await self._generate_quality_tasks(priority)
        elif "documentation" in goal_lower:
            tasks = await self._generate_documentation_tasks(priority)
        elif "testing" in goal_lower:
            tasks = await self._generate_testing_tasks(priority)
        elif "security" in goal_lower:
            tasks = await self._generate_security_tasks(priority)
        else:
            tasks = await self._generate_generic_tasks(goal, priority)

        return tasks

    async def _generate_performance_tasks(
        self,
        priority: str
    ) -> List[Dict[str, Any]]:
        """Generate performance optimization tasks"""
        return [
            {
                "id": "perf_001",
                "title": "Profile agent_core.py startup time",
                "description": "Identify startup performance bottlenecks",
                "priority": priority,
                "target_file": "agent_core.py",
                "task_type": "analysis"
            },
            {
                "id": "perf_002",
                "title": "Optimize tool discovery caching",
                "description": "Implement caching for tool schemas",
                "priority": priority,
                "target_file": "agent_core.py",
                "task_type": "implementation"
            },
            {
                "id": "perf_003",
                "title": "Implement Ollama connection pooling",
                "description": "Reduce connection overhead",
                "priority": priority,
                "target_file": "brain.py",
                "task_type": "implementation"
            }
        ]

    async def _generate_quality_tasks(
        self,
        priority: str
    ) -> List[Dict[str, Any]]:
        """Generate code quality improvement tasks"""
        return [
            {
                "id": "qual_001",
                "title": "Generate missing type hints",
                "description": "Add type hints to untyped functions",
                "priority": priority,
                "task_type": "analysis"
            },
            {
                "id": "qual_002",
                "title": "Create docstrings for public API",
                "description": "Document public methods and classes",
                "priority": priority,
                "task_type": "documentation"
            },
            {
                "id": "qual_003",
                "title": "Refactor high complexity functions",
                "description": "Reduce cyclomatic complexity",
                "priority": priority,
                "task_type": "implementation"
            }
        ]

    async def _generate_documentation_tasks(
        self,
        priority: str
    ) -> List[Dict[str, Any]]:
        """Generate documentation tasks"""
        return [
            {
                "id": "doc_001",
                "title": "Generate API documentation",
                "description": "Create endpoint documentation",
                "priority": priority,
                "target_file": "api_server.py",
                "task_type": "documentation"
            },
            {
                "id": "doc_002",
                "title": "Create tool specifications",
                "description": "Generate schemas for all tools",
                "priority": priority,
                "target_file": "tools/",
                "task_type": "documentation"
            }
        ]

    async def _generate_testing_tasks(
        self,
        priority: str
    ) -> List[Dict[str, Any]]:
        """Generate testing tasks"""
        return [
            {
                "id": "test_001",
                "title": "Analyze test coverage gaps",
                "description": "Identify missing test coverage",
                "priority": priority,
                "task_type": "analysis"
            },
            {
                "id": "test_002",
                "title": "Generate unit tests",
                "description": "Create unit tests for core modules",
                "priority": priority,
                "task_type": "implementation"
            }
        ]

    async def _generate_security_tasks(
        self,
        priority: str
    ) -> List[Dict[str, Any]]:
        """Generate security improvement tasks"""
        return [
            {
                "id": "sec_001",
                "title": "Audit secret handling",
                "description": "Verify secrets are not logged",
                "priority": priority,
                "task_type": "security"
            },
            {
                "id": "sec_002",
                "title": "Validate input sanitization",
                "description": "Check for injection vulnerabilities",
                "priority": priority,
                "task_type": "security"
            }
        ]

    async def _generate_generic_tasks(
        self,
        goal: str,
        priority: str
    ) -> List[Dict[str, Any]]:
        """Generate generic improvement tasks"""
        return [
            {
                "id": "gen_001",
                "title": f"Analyze goal: {goal}",
                "description": f"Generate improvement recommendations",
                "priority": priority,
                "task_type": "analysis"
            }
        ]

    async def _execute_improvement_task(
        self,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single improvement task"""
        log_info(
            "self_prompting_orchestrator",
            f"Executing task: {task['title']}"
        )

        try:
            # Emit task start event
            await self.event_system.emit("improvement_task_start", task)

            # Build delegation prompt
            prompt = self._build_task_prompt(task)

            # Delegate to Copilot CLI tool if available
            from tools.copilot_cli_automation_tool import \
                CopilotCLIAutomationTool

            cli_tool = CopilotCLIAutomationTool()
            result = cli_tool.execute(f"delegate {prompt}")

            # Process result
            task_result = {
                "task_id": task["id"],
                "title": task["title"],
                "status": "completed",
                "result": result,
                "timestamp": datetime.now().isoformat()
            }

            # Emit task completion event
            await self.event_system.emit("improvement_task_complete", task_result)

            return task_result

        except Exception as e:
            log_error(
                "self_prompting_orchestrator",
                f"Task execution failed: {e}",
                exception=e
            )
            return {
                "task_id": task["id"],
                "title": task["title"],
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _build_task_prompt(self, task: Dict[str, Any]) -> str:
        """Build Copilot CLI delegation prompt"""
        prompt_parts = [
            f"Task: {task['title']}",
            f"Description: {task.get('description', '')}",
            f"Type: {task.get('task_type', 'implementation')}",
            f"Priority: {task.get('priority', 'medium')}"
        ]

        if target := task.get("target_file"):
            prompt_parts.append(f"Focus on: @{target}")

        prompt_parts.append(
            "Follow patterns in .github/copilot-instructions.md"
        )

        return "\n".join(prompt_parts)

    def _compile_cycle_summary(self, cycle_data: Dict[str, Any]) -> Dict:
        """Compile summary of improvement cycle"""
        completed = sum(
            1 for r in cycle_data["results"]
            if r.get("status") == "completed"
        )
        failed = sum(
            1 for r in cycle_data["results"]
            if r.get("status") == "failed"
        )

        return {
            "cycle_id": cycle_data["id"],
            "name": cycle_data["name"],
            "goals": cycle_data["goals"],
            "total_tasks": len(cycle_data["tasks"]),
            "completed": completed,
            "failed": failed,
            "success_rate": completed / len(cycle_data["tasks"]) \
                if cycle_data["tasks"] else 0,
            "duration": self._calculate_duration(
                cycle_data["start_time"],
                cycle_data.get("end_time")
            ),
            "results": cycle_data["results"]
        }

    def _calculate_duration(
        self,
        start: str,
        end: str = None
    ) -> str:
        """Calculate and format duration"""
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end) if end \
            else datetime.now()
        duration = end_dt - start_dt
        return str(duration).split(".")[0]

    async def schedule_recurring_cycle(
        self,
        cycle_name: str,
        goals: List[str],
        interval_hours: int = 24,
        priority: str = "medium"
    ) -> str:
        """Schedule recurring improvement cycles"""
        log_info(
            "self_prompting_orchestrator",
            f"Scheduling recurring cycle: {cycle_name} "
            f"(every {interval_hours} hours)"
        )

        session_id = f"recurring_{cycle_name}_{datetime.now().isoformat()}"
        self.active_sessions[session_id] = {
            "name": cycle_name,
            "goals": goals,
            "interval_hours": interval_hours,
            "priority": priority,
            "started_at": datetime.now(),
            "status": "active"
        }

        # Create background task
        asyncio.create_task(
            self._recurring_cycle_worker(session_id)
        )

        return f"Scheduled recurring cycle: {session_id}"

    async def _recurring_cycle_worker(self, session_id: str) -> None:
        """Background worker for recurring cycles"""
        session = self.active_sessions[session_id]

        while session["status"] == "active":
            try:
                # Run improvement cycle
                await self.start_improvement_cycle(
                    cycle_name=session["name"],
                    goals=session["goals"],
                    priority=session["priority"]
                )

                # Sleep until next cycle
                await asyncio.sleep(session["interval_hours"] * 3600)

            except Exception as e:
                log_error(
                    "self_prompting_orchestrator",
                    f"Recurring cycle worker failed: {e}",
                    exception=e
                )
                await asyncio.sleep(3600)  # Retry in 1 hour

    def stop_recurring_cycle(self, session_id: str) -> str:
        """Stop a recurring improvement cycle"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["status"] = "stopped"
            return f"Stopped recurring cycle: {session_id}"
        return f"Session not found: {session_id}"

    def get_improvement_status(self) -> Dict[str, Any]:
        """Get current improvement status"""
        return {
            "total_cycles": len(self.task_history),
            "active_sessions": len(
                [s for s in self.active_sessions.values()
                 if s["status"] == "active"]
            ),
            "recent_tasks": self.task_history[-10:]
            if self.task_history else [],
            "active_sessions_list": self.active_sessions
        }


# Export orchestrator
__all__ = ["SelfPromptingOrchestrator"]
