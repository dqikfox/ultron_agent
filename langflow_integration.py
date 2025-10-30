#!/usr/bin/env python3
"""LangFlow Integration for ULTRON Agent"""

import requests
import json
from typing import Dict, List, Any, Optional
from utils.ultron_logger import log_info, log_ai_decision, log_error

class LangFlowBridge:
    def __init__(self, base_url: str = "http://localhost:7860/api/v1"):
        self.base_url = base_url
        self.flows = {
            "memory_storage": "memory-storage-flow",
            "memory_retrieval": "memory-retrieval-flow", 
            "complex_reasoning": "complex-reasoning-flow",
            "enhanced_chat": "enhanced-chat-flow"
        }
    
    def is_langflow_available(self) -> bool:
        """Check if LangFlow is running"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def store_memory(self, content: str, metadata: Dict = None) -> Dict[str, Any]:
        """Store memory using LangFlow memory storage flow"""
        try:
            payload = {
                "input_value": content,
                "metadata": metadata or {},
                "session_id": "ultron_memory"
            }
            
            response = requests.post(
                f"{self.base_url}/predict/{self.flows['memory_storage']}",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                log_info("langflow_bridge", f"Memory stored: {content[:50]}...")
                return {"success": True, "result": result}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            log_error("langflow_bridge", f"Memory storage failed: {e}")
            return {"success": False, "error": str(e)}
    
    def retrieve_memory(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Retrieve memory using LangFlow retrieval flow"""
        try:
            payload = {
                "input_value": query,
                "limit": limit,
                "session_id": "ultron_memory"
            }
            
            response = requests.post(
                f"{self.base_url}/predict/{self.flows['memory_retrieval']}",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {"success": True, "memories": result.get("output", [])}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            log_error("langflow_bridge", f"Memory retrieval failed: {e}")
            return {"success": False, "error": str(e)}
    
    def enhanced_chat(self, message: str, context: Dict = None, session_id: str = "ultron") -> Dict[str, Any]:
        """Process chat with LangFlow enhanced reasoning"""
        try:
            payload = {
                "input_value": message,
                "context": context or {},
                "session_id": session_id,
                "memory_lookup": True,
                "tools_available": self._get_available_tools()
            }
            
            response = requests.post(
                f"{self.base_url}/predict/{self.flows['enhanced_chat']}",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                log_ai_decision("langflow_bridge", f"Enhanced chat processed: {message[:50]}...", 
                              ai_model="langflow_enhanced")
                return {
                    "success": True,
                    "response": result.get("output", ""),
                    "reasoning": result.get("reasoning", ""),
                    "tools_used": result.get("tools_used", [])
                }
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            log_error("langflow_bridge", f"Enhanced chat failed: {e}")
            return {"success": False, "error": str(e)}
    
    def complex_reasoning(self, query: str, context: Dict = None) -> Dict[str, Any]:
        """Route complex queries to LangFlow reasoning flow"""
        try:
            if not self.is_complex_query(query):
                return {"success": False, "reason": "Not a complex query"}
            
            payload = {
                "input_value": query,
                "context": context or {},
                "reasoning_mode": "chain_of_thought"
            }
            
            response = requests.post(
                f"{self.base_url}/predict/{self.flows['complex_reasoning']}",
                json=payload,
                timeout=90
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "reasoning_chain": result.get("reasoning_steps", []),
                    "final_answer": result.get("output", ""),
                    "confidence": result.get("confidence", 0.8)
                }
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            log_error("langflow_bridge", f"Complex reasoning failed: {e}")
            return {"success": False, "error": str(e)}
    
    def is_complex_query(self, query: str) -> bool:
        """Determine if query requires complex reasoning"""
        complex_indicators = [
            "analyze", "compare", "explain why", "what if", "how would",
            "step by step", "reasoning", "logic", "because", "therefore",
            "multi-step", "complex", "detailed analysis"
        ]
        
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in complex_indicators)
    
    def _get_available_tools(self) -> List[str]:
        """Get list of available tools for LangFlow"""
        return [
            "file_operations", "web_search", "code_execution",
            "data_analysis", "image_processing", "system_control"
        ]

class LangFlowMemorySystem:
    """LangFlow-powered memory system"""
    
    def __init__(self, bridge: LangFlowBridge):
        self.bridge = bridge
    
    def store_conversation(self, user_input: str, agent_response: str, context: Dict = None):
        """Store conversation in LangFlow memory"""
        conversation_data = {
            "user_input": user_input,
            "agent_response": agent_response,
            "timestamp": json.dumps(context or {})
        }
        
        content = f"User: {user_input}\nAgent: {agent_response}"
        return self.bridge.store_memory(content, conversation_data)
    
    def search_conversations(self, query: str, limit: int = 5) -> List[Dict]:
        """Search conversation history"""
        result = self.bridge.retrieve_memory(query, limit)
        if result.get("success"):
            return result.get("memories", [])
        return []

class EnhancedLangFlowAgent:
    """Enhanced ULTRON Agent with LangFlow integration"""
    
    def __init__(self):
        self.bridge = LangFlowBridge()
        self.memory = LangFlowMemorySystem(self.bridge)
        self.fallback_enabled = True
    
    async def process_message(self, message: str, context: Dict = None, session_id: str = "ultron") -> Dict[str, Any]:
        """Process message with LangFlow enhancement"""
        
        # Check if LangFlow is available
        if not self.bridge.is_langflow_available():
            if self.fallback_enabled:
                return await self._fallback_processing(message, context)
            else:
                return {"success": False, "error": "LangFlow not available"}
        
        # Try complex reasoning first for sophisticated queries
        if self.bridge.is_complex_query(message):
            reasoning_result = self.bridge.complex_reasoning(message, context)
            if reasoning_result.get("success"):
                # Store in memory
                self.memory.store_conversation(message, reasoning_result.get("final_answer", ""), context)
                return reasoning_result
        
        # Use enhanced chat for regular queries
        chat_result = self.bridge.enhanced_chat(message, context, session_id)
        if chat_result.get("success"):
            # Store in memory
            self.memory.store_conversation(message, chat_result.get("response", ""), context)
            return chat_result
        
        # Fallback if LangFlow fails
        if self.fallback_enabled:
            return await self._fallback_processing(message, context)
        
        return {"success": False, "error": "All processing methods failed"}
    
    async def _fallback_processing(self, message: str, context: Dict = None) -> Dict[str, Any]:
        """Fallback to local processing when LangFlow unavailable"""
        log_info("langflow_agent", "Using fallback processing")
        
        # Use existing enhanced systems
        from enhanced_ultron_core import enhanced_ultron
        result = await enhanced_ultron.process_enhanced_command(message, context)
        
        return {
            "success": True,
            "response": result.get("result", "Processed with local systems"),
            "method": "fallback",
            "agent": result.get("agent", "local")
        }
    
    def get_memory_summary(self, days: int = 7) -> str:
        """Get conversation summary from LangFlow memory"""
        summary_query = f"summarize conversations from last {days} days"
        memories = self.memory.search_conversations(summary_query, limit=20)
        
        if memories:
            return f"Found {len(memories)} relevant conversations in memory"
        return "No recent conversations found"
    
    def get_status(self) -> Dict[str, Any]:
        """Get LangFlow integration status"""
        return {
            "langflow_available": self.bridge.is_langflow_available(),
            "base_url": self.bridge.base_url,
            "flows_configured": len(self.bridge.flows),
            "fallback_enabled": self.fallback_enabled,
            "memory_system": "langflow_powered"
        }

# Global LangFlow agent instance
langflow_agent = EnhancedLangFlowAgent()