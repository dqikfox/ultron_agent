"""
tools.py
========

This module defines additional tools that can be plugged into the Ultron
Agent. Tools follow a simple protocol defined by the base `Tool` class
in the core repository: they expose a `name`, `description`, optional
`parameters`, and implement two methods: `match` and `execute`.
"""

from __future__ import annotations

import json
import logging
import requests
from typing import Any

try:
    from tools.base import Tool  # type: ignore
except Exception:
    # Minimal fallback base class
    class Tool:  # type: ignore
        name = "Tool"
        description = "Base fallback tool"
        parameters: dict[str, Any] = {}

        def match(self, command: str) -> bool:
            return False

        def execute(self, command: str) -> str:
            return ""


class SearchTool(Tool):
    """A simple web search tool using DuckDuckGo's instant answer API."""

    name = "search_web"
    description = "Search the web for a query and return a brief summary."
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query to look up"
            }
        },
        "required": ["query"],
    }

    def match(self, command: str) -> bool:
        return command.lower().startswith("search")

    def execute(self, query: str, **kwargs: Any) -> str:
        logging.debug(f"[SearchTool] Executing search for query: {query} - tools.py:54")
        try:
            params = {
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1,
            }
            response = requests.get("https://api.duckduckgo.com/", params=params, timeout=10)
            data = response.json()
            summary = data.get("Abstract") or next(
                (topic.get("Text") for topic in data.get("RelatedTopics", []) if topic.get("Text")),
                "No summary available."
            )
            return summary[:500]
        except Exception as e:
            logging.error(f"[SearchTool] Error during search: {e} - tools.py:70")
            return "An error occurred while searching."


class CalculatorTool(Tool):
    """A simple calculator tool that evaluates arithmetic expressions."""

    name = "calculate"
    description = "Evaluate a basic arithmetic expression and return the result."
    parameters = {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "A mathematical expression to evaluate"
            }
        },
        "required": ["expression"],
    }

    def match(self, command: str) -> bool:
        return command.lower().startswith("calculate")

    def execute(self, expression: str, **kwargs: Any) -> str:
        logging.debug(f"[CalculatorTool] Evaluating expression: {expression} - tools.py:94")
        # Define a restricted set of builtins
        allowed_names = {k: v for k, v in vars(__builtins__).items() if k in ("abs", "round")}
        try:
            result = eval(expression, {"__builtins__": allowed_names}, {})
            return str(result)
        except Exception as e:
            logging.error(f"[CalculatorTool] Error evaluating expression: {e} - tools.py:101")
            return "Invalid expression."
