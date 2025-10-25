#!/usr/bin/env python3
"""AI Agent Orchestration System for ULTRON Agent"""

import asyncio
import json
from typing import Dict, List, Any
from dataclasses import dataclass
from utils.ultron_logger import log_info, log_error, log_ai_decision

@dataclass
class Agent:
    name: str
    model: str
    role: str
    capabilities: List[str]
    status: str = "idle"

class AgentOrchestrator:
    """Orchestrates multiple AI agents for complex tasks"""
    
    def __init__(self):
        self.agents = {}
        self.active_tasks = {}
        self.task_queue = asyncio.Queue()
        
    def register_agent(self, agent: Agent):
        """Register a new agent"""
        self.agents[agent.name] = agent
        log_info("orchestrator", f"Agent registered: {agent.name}")
    
    async def delegate_task(self, task: Dict[str, Any]) -> str:
        """Delegate task to best available agent"""
        best_agent = self._select_agent(task)
        
        if not best_agent:
            return "❌ No suitable agent available"
        
        log_ai_decision("orchestrator", f"Delegating to {best_agent.name}", 
                       ai_model=best_agent.model, confidence_score=0.9)
        
        result = await self._execute_task(best_agent, task)
        return result
    
    def _select_agent(self, task: Dict[str, Any]) -> Agent:
        """Select best agent for task"""
        task_type = task.get("type", "general")
        
        for agent in self.agents.values():
            if agent.status == "idle" and task_type in agent.capabilities:
                return agent
        
        return None
    
    async def _execute_task(self, agent: Agent, task: Dict[str, Any]) -> str:
        """Execute task with selected agent"""
        agent.status = "busy"
        
        try:
            # Simulate task execution
            await asyncio.sleep(0.1)
            result = f"🤖 {agent.name} completed: {task.get('description', 'task')}"
            agent.status = "idle"
            return result
        except Exception as e:
            agent.status = "error"
            log_error("orchestrator", f"Task failed: {e}")
            return f"❌ Task failed: {str(e)}"

# Global orchestrator instance
orchestrator = AgentOrchestrator()

# Register default agents
orchestrator.register_agent(Agent(
    name="CodeAgent", 
    model="qwen3-coder:480b-cloud",
    role="coding",
    capabilities=["code", "debug", "refactor"]
))

orchestrator.register_agent(Agent(
    name="ReasoningAgent",
    model="deepseek-r1:14b", 
    role="analysis",
    capabilities=["analyze", "reason", "plan"]
))

orchestrator.register_agent(Agent(
    name="VisionAgent",
    model="llava:7b",
    role="vision", 
    capabilities=["vision", "image", "ocr"]
))