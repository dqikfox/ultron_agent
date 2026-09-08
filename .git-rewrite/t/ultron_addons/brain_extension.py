"""
brain_extension.py
===================

This module defines advanced brain implementations that build upon the core
`UltronBrain`.  The goal of an advanced brain is to enhance the agent's
reasoning capabilities by incorporating richer context from memory,
performing tool suggestion ranking, and supporting asynchronous
communications with external services.
"""

from __future__ import annotations

import logging
from typing import Any, List, Optional

try:
    from brain import UltronBrain  # type: ignore
except Exception: # pragma: no cover
    UltronBrain = None  # type: ignore


class AdvancedUltronBrain:
    """An enhanced brain with improved prompt construction and tool ranking."""

    def __init__(self, base_brain: Optional[UltronBrain], memory: Any, tools: List[Any]) -> None:
        self.base_brain = base_brain
        self.memory = memory
        self.tools = tools
        logging.info("[AdvancedUltronBrain] Initialized with base brain %s - brain_extension.py:30", type(base_brain).__name__ if base_brain else None)

    def _rank_tools(self, user_input: str) -> List[Any]:
        """Rank available tools based on how well they match the user input."""
        scores = []
        lower_input = user_input.lower()
        for tool in self.tools:
            score = 0
            if hasattr(tool, 'name') and tool.name.lower() in lower_input:
                score += 1
            if hasattr(tool, 'description'):
                words = set(tool.description.lower().split())
                score += len(words & set(lower_input.split())) / max(len(words), 1)
            scores.append((score, tool))
        scores.sort(key=lambda x: x[0], reverse=True)
        return [tool for _, tool in scores]

    async def plan_and_act(self, user_input: str, progress_callback: Optional[Any] = None) -> str:
        """Plan and act on a user input using enhanced context."""
        context = []
        try:
            if hasattr(self.memory, 'search'):
                context = self.memory.search(user_input, top_k=3)
            elif hasattr(self.memory, 'get_recent'):
                context = self.memory.get_recent(3)
        except Exception as e:
            logging.error(f"[AdvancedUltronBrain] Error retrieving context: {e} - brain_extension.py:56")

        ranked_tools = self._rank_tools(user_input)
        if self.base_brain:
            prompt = f"User: {user_input}\nContext: {context}\n"
            prompt += "Available tools (ranked):\n"
            for tool in ranked_tools:
                prompt += f"- {tool.name}: {tool.description}\n"
            logging.debug(f"[AdvancedUltronBrain] Delegating to base brain with prompt:\n{prompt} - brain_extension.py:64")
            return await self.base_brain.query_llm(prompt, progress_callback=progress_callback)
        logging.info("[AdvancedUltronBrain] No base brain available, responding with memory context - brain_extension.py:66")
        if context:
            return f"I recall {context[0]} related to your query."
        return "I'm sorry, I don't have enough context to assist with that."
