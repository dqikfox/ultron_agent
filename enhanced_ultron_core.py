#!/usr/bin/env python3
"""Enhanced ULTRON Core Integration"""

from enhanced_memory_system import EnhancedMemorySystem
from multi_agent_system import MultiAgentOrchestrator
from enhanced_tool_framework import tool_registry
from task_planning_system import task_planner, workflow_executor
from utils.ultron_logger import log_info, log_ai_decision

class EnhancedUltronCore:
    """Enhanced ULTRON Agent with advanced capabilities"""
    
    def __init__(self):
        self.memory_system = EnhancedMemorySystem()
        self.multi_agent = MultiAgentOrchestrator()
        self.tool_registry = tool_registry
        self.task_planner = task_planner
        self.workflow_executor = workflow_executor
        
        log_info("enhanced_ultron", "Enhanced ULTRON Core initialized")
    
    async def process_enhanced_command(self, command: str, context: dict = None) -> dict:
        """Process command with enhanced capabilities"""
        log_ai_decision("enhanced_ultron", f"Processing enhanced command: {command[:50]}...", 
                       ai_model="enhanced_ultron_core")
        
        # Store in memory
        self.memory_system.store_conversation(command, "", context or {})
        
        # Route to appropriate agent
        result = await self.multi_agent.process_task(command, context)
        
        # Store result in memory
        if result.get("success"):
            self.memory_system.store_conversation(command, result.get("result", ""), context or {})
        
        return result
    
    def get_system_status(self) -> dict:
        """Get comprehensive system status"""
        return {
            "memory_system": "active",
            "multi_agent_system": self.multi_agent.get_agent_status(),
            "available_tools": self.tool_registry.list_tools(),
            "task_planner": self.task_planner.get_workflow_status(),
            "enhanced_features": [
                "Vector-based memory",
                "Multi-agent orchestration", 
                "Advanced tool framework",
                "Task planning & execution",
                "Workflow management"
            ]
        }
    
    async def execute_complex_workflow(self, description: str) -> dict:
        """Execute complex multi-step workflow"""
        return await self.workflow_executor.execute_workflow(description)
    
    def search_memory(self, query: str, limit: int = 5) -> list:
        """Search conversation memory"""
        return self.memory_system.retrieve_similar_conversations(query, limit)

# Global enhanced core instance
enhanced_ultron = EnhancedUltronCore()