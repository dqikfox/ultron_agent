from typing import List, Dict, Any, Optional
import logging
import json
import asyncio
from tools.openai_tools import OpenAITools

class AgentNetwork:
    def __init__(self, config):
        self.config = config
        self.openai_tools = OpenAITools(config)
        self.registered_tools = []
        self.conversation_history = []
        
    def register_tool(self, tool: Dict[str, Any]):
        """Register a tool that can be used by the agent network."""
        self.registered_tools.append(tool)
        logging.info(f"Registered tool: {tool.get('name')}")
        
    def register_tools(self, tools: List[Dict[str, Any]]):
        """Register multiple tools at once."""
        for tool in tools:
            self.register_tool(tool)
            
    async def process_request(self, prompt: str, 
                            context: Optional[Dict] = None, 
                            max_steps: int = 5) -> Dict:
        """Process a request through the agent network."""
        try:
            messages = []
            
            # Add context if provided
            if context:
                messages.append({
                    "role": "system",
                    "content": json.dumps(context)
                })
                
            # Add conversation history
            messages.extend(self.conversation_history[-5:])  # Keep last 5 messages for context
            
            step_count = 0
            while step_count < max_steps:
                result = await self.openai_tools.agent_invoke_tools(
                    prompt=prompt,
                    tools=self.registered_tools,
                    messages=messages
                )
                
                # Update conversation history
                if result.get("messages"):
                    self.conversation_history.extend(result["messages"])
                
                # If no tool calls or final response, return
                if not result.get("tool_calls"):
                    return {
                        "response": result["response"],
                        "steps": step_count + 1
                    }
                
                # Continue with tool execution feedback
                prompt = result["response"]
                step_count += 1
                
            return {
                "response": "Max steps reached. Process terminated.",
                "steps": max_steps
            }
            
        except Exception as e:
            logging.error(f"Agent network error: {e}")
            raise
            
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the conversation history."""
        return self.conversation_history
        
    def clear_conversation_history(self):
        """Clear the conversation history."""
        self.conversation_history = []
