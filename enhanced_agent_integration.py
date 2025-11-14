#!/usr/bin/env python3
"""Enhanced Agent Integration Methods"""

import asyncio
from typing import Dict, Any, List
from utils.ultron_logger import log_info, log_ai_decision

class EnhancedAgentMethods:
    """Methods to add to UltronWebHandler for enhanced functionality"""
    
    def _get_memory_conversations(self) -> Dict[str, Any]:
        """Get recent conversations from enhanced memory"""
        try:
            if AGENT_AVAILABLE:
                memory_system = EnhancedMemorySystem()
                conversations = memory_system.retrieve_similar_conversations("recent", limit=10)
                return {
                    "success": True,
                    "conversations": conversations,
                    "count": len(conversations)
                }
            return {"success": False, "error": "Memory system not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_multi_agent_status(self) -> Dict[str, Any]:
        """Get multi-agent system status"""
        try:
            if AGENT_AVAILABLE:
                orchestrator = MultiAgentOrchestrator()
                status = orchestrator.get_agent_status()
                return {
                    "success": True,
                    "agents": status,
                    "total_agents": len(status)
                }
            return {"success": False, "error": "Multi-agent system not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_tools_registry(self) -> Dict[str, Any]:
        """Get available tools from registry"""
        try:
            if AGENT_AVAILABLE:
                tools = tool_registry.list_tools()
                tool_details = {}
                for tool_name in tools:
                    tool = tool_registry.get_tool(tool_name)
                    tool_details[tool_name] = {
                        "name": tool.name,
                        "description": tool.description
                    }
                return {
                    "success": True,
                    "tools": tool_details,
                    "count": len(tools)
                }
            return {"success": False, "error": "Tool registry not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_task_status(self) -> Dict[str, Any]:
        """Get task planning system status"""
        try:
            if AGENT_AVAILABLE:
                all_tasks = task_planner.get_all_tasks()
                workflow_status = task_planner.get_workflow_status()
                return {
                    "success": True,
                    "tasks": all_tasks,
                    "workflow_status": workflow_status
                }
            return {"success": False, "error": "Task planner not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_workflow_status(self) -> Dict[str, Any]:
        """Get workflow execution status"""
        try:
            if AGENT_AVAILABLE:
                status = task_planner.get_workflow_status()
                ready_tasks = task_planner.get_ready_tasks()
                return {
                    "success": True,
                    "workflow_status": status,
                    "ready_tasks": [t.to_dict() for t in ready_tasks]
                }
            return {"success": False, "error": "Workflow executor not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _store_memory(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Store conversation in enhanced memory"""
        try:
            if AGENT_AVAILABLE:
                memory_system = EnhancedMemorySystem()
                user_input = data.get("user_input", "")
                agent_response = data.get("agent_response", "")
                context = data.get("context", {})
                
                memory_system.store_conversation(user_input, agent_response, context)
                return {"success": True, "message": "Memory stored"}
            return {"success": False, "error": "Memory system not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _process_agent_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process task with multi-agent system"""
        try:
            if AGENT_AVAILABLE:
                orchestrator = MultiAgentOrchestrator()
                task = data.get("task", "")
                context = data.get("context", {})
                
                # Run async task in sync context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(orchestrator.process_task(task, context))
                loop.close()
                
                return result
            return {"success": False, "error": "Multi-agent system not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _execute_tool(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool from registry"""
        try:
            if AGENT_AVAILABLE:
                tool_name = data.get("tool", "")
                action = data.get("action", "")
                params = data.get("params", {})
                
                tool = tool_registry.get_tool(tool_name)
                if not tool:
                    return {"success": False, "error": f"Tool '{tool_name}' not found"}
                
                result = tool.execute(action, **params)
                return result
            return {"success": False, "error": "Tool registry not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _execute_workflow(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow"""
        try:
            if AGENT_AVAILABLE:
                workflow_description = data.get("workflow", "")
                
                # Run async workflow in sync context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(workflow_executor.execute_workflow(workflow_description))
                loop.close()
                
                return result
            return {"success": False, "error": "Workflow executor not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _start_autonomous_mode(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Start enhanced autonomous mode"""
        try:
            mode = data.get("mode", "standard")
            log_ai_decision("enhanced_agent", f"Starting autonomous mode: {mode}", ai_model="ultron_enhanced")
            
            return {
                "success": True,
                "message": f"Enhanced autonomous mode '{mode}' started",
                "features": [
                    "Multi-agent coordination",
                    "Enhanced memory system",
                    "Task planning & execution",
                    "Tool integration framework"
                ]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}