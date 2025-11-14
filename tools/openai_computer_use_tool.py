#!/usr/bin/env python3
"""
Open Interface backed Computer Use Tool for ULTRON.

This replaces the earlier placeholder implementation with the real
Open Interface style autopilot so commands can be handled by an
LLM (GPT-4o, Gemini, custom) that sees the desktop, plans actions,
and executes them via PyAutoGUI.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from utils.ultron_logger import log_info, log_error
from tools.open_interface_autopilot import (
    OpenInterfaceSession,
    load_open_interface_config,
    run_open_interface,
)


class OpenAIComputerUseTool:
    """High-level wrapper that exposes Open Interface autopilot as a tool."""

    name = "Open Interface Autopilot"
    description = (
        "Desktop autopilot that captures screenshots, asks an LLM to plan actions, "
        "and executes those actions (mouse, keyboard, scrolling, screenshots)."
    )

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.overrides = config or {}
        self.enabled = load_open_interface_config(self.overrides).provider.lower() in {
            "openai",
            "gemini",
            "custom",
        }

    def match(self, command: str) -> bool:
        keywords = [
            "computer",
            "screen",
            "click",
            "type",
            "screenshot",
            "mouse",
            "keyboard",
            "autopilot",
            "open interface",
            "control my pc",
        ]
        command_lower = command.lower()
        return any(keyword in command_lower for keyword in keywords)

    def execute(self, command: str, **kwargs: Any) -> str:
        """Run an Open Interface session for the provided goal/command."""
        if not self.enabled:
            return "Open Interface autopilot is disabled in configuration."

        goal = kwargs.get("goal") or command
        try:
            session = OpenInterfaceSession(overrides=self.overrides)
            result = session.run(goal)
            status = "completed" if result["completed"] else "incomplete"
            log_info(
                "open_interface",
                f"Autopilot run {status} for goal '{goal}'",
                log_path=result["log_path"],
            )
            return self._format_result(result)
        except Exception as exc:  # pragma: no cover - depends on runtime env
            log_error("open_interface", f"Autopilot execution failed: {exc}")
            return (
                "Open Interface autopilot failed to run. "
                f"Details: {exc}"
            )

    def _format_result(self, result: Dict[str, Any]) -> str:
        steps = result.get("steps", [])
        summary_lines = [
            f"Goal: {result.get('goal')}",
            f"Status: {'✅' if result.get('completed') else '⚠️ '} {result.get('finish_message')}",
            f"Steps executed: {len(steps)}",
            f"Session log: {result.get('log_path')}",
        ]

        for step in steps[:3]:
            plan = step.get("plan", {})
            execution = step.get("execution", {})
            summary_lines.append(
                f"- Step {step['step']}: "
                f"{len(plan.get('actions', []))} actions "
                f"(errors: {len(execution.get('errors', []))})"
            )

        if len(steps) > 3:
            summary_lines.append(f"... {len(steps) - 3} additional steps omitted ...")

        return "\n".join(summary_lines)

    @staticmethod
    def schema() -> Dict[str, Any]:
        return {
            "name": OpenAIComputerUseTool.name,
            "description": OpenAIComputerUseTool.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "goal": {
                        "type": "string",
                        "description": "High level instruction for the autopilot to accomplish.",
                    }
                },
                "required": ["goal"],
            },
        }


def run_desktop_autopilot(goal: str) -> Dict[str, Any]:
    """Convenience helper so other modules can trigger the autopilot."""
    return run_open_interface(goal)
