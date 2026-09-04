#!/usr/bin/env python3
"""LangFlow API Endpoints for ULTRON Agent"""

from typing import Dict, Any
from utils.ultron_logger import log_info, log_ai_decision

class LangFlowAPIEndpoints:
    """API endpoints for LangFlow integration"""
    
    def _get_langflow_status(self) -> Dict[str, Any]:
        """Get LangFlow integration status"""
        try:
            if AGENT_AVAILABLE:
                status = langflow_agent.get_status()
                return {"success": True, "langflow": status}
            return {"success": False, "error": "LangFlow not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _process_langflow_chat(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process chat through LangFlow"""
        try:
            if AGENT_AVAILABLE:
                message = data.get("message", "")
                context = data.get("context", {})
                session_id = data.get("session_id", "ultron")
                
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    langflow_agent.process_message(message, context, session_id)
                )
                loop.close()
                
                return result
            return {"success": False, "error": "LangFlow agent not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _langflow_memory_search(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Search LangFlow memory"""
        try:
            if AGENT_AVAILABLE:
                query = data.get("query", "")
                limit = data.get("limit", 5)
                
                memories = langflow_agent.memory.search_conversations(query, limit)
                return {"success": True, "memories": memories, "count": len(memories)}
            return {"success": False, "error": "LangFlow memory not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _langflow_complex_reasoning(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process complex reasoning through LangFlow"""
        try:
            if AGENT_AVAILABLE:
                query = data.get("query", "")
                context = data.get("context", {})
                
                bridge = LangFlowBridge()
                result = bridge.complex_reasoning(query, context)
                return result
            return {"success": False, "error": "LangFlow reasoning not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}