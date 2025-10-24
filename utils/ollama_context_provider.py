"""
Ollama Context Provider - Universal context injection for all Ollama models

This module provides a centralized system for injecting agent context (memory, tools,
capabilities) into Ollama model prompts. Works with any Ollama model dynamically.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from utils.ultron_logger import log_info, log_error, log_ai_decision


class OllamaContextProvider:
    """
    Provides comprehensive context to Ollama models including:
    - Memory system (short-term and long-term)
    - Available tools and their schemas
    - Agent capabilities and status
    - System configuration
    
    Works dynamically with any Ollama model at runtime.
    """
    
    def __init__(self, memory=None, tools=None, config=None):
        """
        Initialize the context provider.
        
        Args:
            memory: Memory system instance (optional)
            tools: Dictionary of available tools (optional)
            config: Configuration dictionary (optional)
        """
        self.memory = memory
        self.tools = tools or {}
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Context injection settings
        self.include_memory = self.config.get('ollama_include_memory', True)
        self.include_tools = self.config.get('ollama_include_tools', True)
        self.include_capabilities = self.config.get('ollama_include_capabilities', True)
        self.max_memory_items = self.config.get('ollama_max_memory_items', 10)
        self.max_tool_schemas = self.config.get('ollama_max_tool_schemas', 20)
        
        log_info("ollama_context_provider", 
                f"Initialized with memory={memory is not None}, "
                f"tools={len(self.tools)}, config={len(self.config)}")
    
    def build_enhanced_prompt(self, user_prompt: str, model_name: str = None) -> str:
        """
        Build an enhanced prompt with full agent context for any Ollama model.
        
        Args:
            user_prompt: Original user prompt/query
            model_name: Name of the Ollama model being used (for logging)
            
        Returns:
            Enhanced prompt string with injected context
        """
        try:
            context_sections = []
            
            # System identity and capabilities
            if self.include_capabilities:
                capabilities_context = self._build_capabilities_context()
                if capabilities_context:
                    context_sections.append(capabilities_context)
            
            # Memory context
            if self.include_memory and self.memory:
                memory_context = self._build_memory_context()
                if memory_context:
                    context_sections.append(memory_context)
            
            # Tools context
            if self.include_tools and self.tools:
                tools_context = self._build_tools_context()
                if tools_context:
                    context_sections.append(tools_context)
            
            # Build final enhanced prompt
            if context_sections:
                context_block = "\n\n".join(context_sections)
                enhanced_prompt = f"""{context_block}

---

User Query: {user_prompt}

Response:"""
            else:
                # No context available, use original prompt
                enhanced_prompt = user_prompt
            
            log_ai_decision(
                "ollama_context_provider",
                f"Built enhanced prompt for model '{model_name}' with {len(context_sections)} context sections",
                model_name or "unknown",
                confidence_score=0.9
            )
            
            return enhanced_prompt
            
        except Exception as e:
            log_error("ollama_context_provider", f"Error building enhanced prompt: {e}")
            # Fallback to original prompt on error
            return user_prompt
    
    def _build_capabilities_context(self) -> str:
        """Build context section describing agent capabilities."""
        try:
            capabilities = []
            
            # Core identity
            capabilities.append("You are ULTRON, an advanced AI agent with the following capabilities:")
            
            # Check what systems are available
            if self.memory:
                capabilities.append("- Memory System: Short-term and long-term memory for context retention")
            
            if self.tools:
                capabilities.append(f"- Tool Access: {len(self.tools)} tools available for various tasks")
            
            # Standard capabilities
            capabilities.append("- Reasoning: Advanced problem-solving and decision-making")
            capabilities.append("- Analysis: Code, text, and data analysis")
            capabilities.append("- Communication: Natural language understanding and generation")
            
            # Configuration-based capabilities
            if self.config.get('voice_enabled'):
                capabilities.append("- Voice: Speech recognition and synthesis")
            
            if self.config.get('vision_enabled'):
                capabilities.append("- Vision: Image analysis and OCR")
            
            return "\n".join(capabilities)
            
        except Exception as e:
            log_error("ollama_context_provider", f"Error building capabilities context: {e}")
            return ""
    
    def _build_memory_context(self) -> str:
        """Build context section with relevant memory content."""
        try:
            memory_sections = []
            
            # Short-term memory (recent conversation)
            if hasattr(self.memory, 'retrieve_short_term'):
                short_term = self.memory.retrieve_short_term()
                if short_term:
                    # Limit to most recent items
                    recent_items = short_term[-self.max_memory_items:]
                    if recent_items:
                        memory_sections.append("Recent Conversation Context:")
                        for idx, item in enumerate(recent_items, 1):
                            memory_sections.append(f"{idx}. {self._format_memory_item(item)}")
            
            # Long-term memory (if available and relevant)
            if hasattr(self.memory, 'retrieve_long_term'):
                long_term = self.memory.retrieve_long_term()
                if long_term and isinstance(long_term, dict):
                    # Get most recent items from long-term memory
                    items = list(long_term.items())[-5:]  # Last 5 items
                    if items:
                        memory_sections.append("\nRelevant Knowledge:")
                        for key, value in items:
                            memory_sections.append(f"- {self._format_memory_item(value)}")
            
            # System prompt from memory (if available)
            if hasattr(self.memory, 'get_system_prompt'):
                try:
                    system_prompt = self.memory.get_system_prompt()
                    if system_prompt:
                        memory_sections.insert(0, f"System Context: {system_prompt}")
                except Exception:
                    pass
            
            return "\n".join(memory_sections) if memory_sections else ""
            
        except Exception as e:
            log_error("ollama_context_provider", f"Error building memory context: {e}")
            return ""
    
    def _build_tools_context(self) -> str:
        """Build context section describing available tools."""
        try:
            if not self.tools:
                return ""
            
            tool_sections = ["Available Tools and Functions:"]
            
            # Get tool schemas (limit to avoid overwhelming the model)
            tool_count = 0
            for tool_name, tool_instance in self.tools.items():
                if tool_count >= self.max_tool_schemas:
                    break
                
                tool_info = self._get_tool_info(tool_name, tool_instance)
                if tool_info:
                    tool_sections.append(tool_info)
                    tool_count += 1
            
            # Add usage instructions
            if tool_count > 0:
                tool_sections.append("\nYou can reference these tools when formulating responses.")
                tool_sections.append("When a tool would be helpful, mention it in your response.")
            
            return "\n".join(tool_sections)
            
        except Exception as e:
            log_error("ollama_context_provider", f"Error building tools context: {e}")
            return ""
    
    def _get_tool_info(self, tool_name: str, tool_instance) -> str:
        """Extract and format information about a tool."""
        try:
            # Try to get tool schema if available
            if hasattr(tool_instance, 'schema'):
                try:
                    schema = tool_instance.schema() if callable(tool_instance.schema) else tool_instance.schema
                    if schema:
                        name = schema.get('name', tool_name)
                        description = schema.get('description', 'No description available')
                        return f"- {name}: {description}"
                except Exception:
                    pass
            
            # Fallback: use tool name and description attribute if available
            if hasattr(tool_instance, 'description'):
                return f"- {tool_name}: {tool_instance.description}"
            
            # Last fallback: just the name
            if hasattr(tool_instance, '__doc__') and tool_instance.__doc__:
                doc_lines = tool_instance.__doc__.strip().split('\n')
                first_line = doc_lines[0].strip() if doc_lines else "Tool available"
                return f"- {tool_name}: {first_line}"
            
            return f"- {tool_name}: Tool available"
            
        except Exception as e:
            log_error("ollama_context_provider", f"Error getting tool info for {tool_name}: {e}")
            return ""
    
    def _format_memory_item(self, item) -> str:
        """Format a memory item for display in context."""
        try:
            if isinstance(item, dict):
                # Try to extract meaningful content
                if 'content' in item:
                    return str(item['content'])[:200]  # Limit length
                elif 'message' in item:
                    return str(item['message'])[:200]
                else:
                    # Return first value found
                    for value in item.values():
                        if isinstance(value, str):
                            return value[:200]
            elif isinstance(item, str):
                return item[:200]
            else:
                return str(item)[:200]
        except Exception:
            return str(item)[:200]
    
    def get_tools_as_function_schemas(self) -> List[Dict[str, Any]]:
        """
        Get tool schemas in OpenAI function calling format.
        This enables function calling with Ollama models that support it.
        
        Returns:
            List of tool schemas in OpenAI format (limited by max_tool_schemas)
        """
        try:
            function_schemas = []
            
            for tool_name, tool_instance in self.tools.items():
                # Check if we've reached the limit
                if len(function_schemas) >= self.max_tool_schemas:
                    break
                
                if hasattr(tool_instance, 'schema'):
                    try:
                        schema = tool_instance.schema() if callable(tool_instance.schema) else tool_instance.schema
                        if schema and isinstance(schema, dict):
                            # Ensure it has required fields
                            if 'name' in schema and 'description' in schema:
                                function_schemas.append(schema)
                    except Exception as e:
                        log_error("ollama_context_provider", 
                                f"Error getting schema for tool {tool_name}: {e}")
            
            return function_schemas
            
        except Exception as e:
            log_error("ollama_context_provider", f"Error building function schemas: {e}")
            return []
    
    def update_memory(self, new_memory):
        """Update the memory system reference."""
        self.memory = new_memory
        log_info("ollama_context_provider", "Memory system updated")
    
    def update_tools(self, new_tools: Dict[str, Any]):
        """Update the tools dictionary."""
        self.tools = new_tools
        log_info("ollama_context_provider", f"Tools updated: {len(new_tools)} tools available")
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update configuration settings."""
        self.config = new_config
        # Reload settings
        self.include_memory = self.config.get('ollama_include_memory', True)
        self.include_tools = self.config.get('ollama_include_tools', True)
        self.include_capabilities = self.config.get('ollama_include_capabilities', True)
        log_info("ollama_context_provider", "Configuration updated")
    
    def get_context_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current context state.
        
        Returns:
            Dictionary with context statistics
        """
        try:
            stats = {
                'timestamp': datetime.now().isoformat(),
                'memory_available': self.memory is not None,
                'tools_count': len(self.tools),
                'config_loaded': bool(self.config),
                'context_sections_enabled': {
                    'memory': self.include_memory,
                    'tools': self.include_tools,
                    'capabilities': self.include_capabilities
                }
            }
            
            # Memory stats
            if self.memory:
                if hasattr(self.memory, 'retrieve_short_term'):
                    stats['short_term_memory_count'] = len(self.memory.retrieve_short_term())
                if hasattr(self.memory, 'retrieve_long_term'):
                    long_term = self.memory.retrieve_long_term()
                    if isinstance(long_term, dict):
                        stats['long_term_memory_count'] = len(long_term)
            
            return stats
            
        except Exception as e:
            log_error("ollama_context_provider", f"Error getting context stats: {e}")
            return {'error': str(e)}


# Factory function for easy instantiation
def create_ollama_context_provider(memory=None, tools=None, config=None) -> OllamaContextProvider:
    """
    Factory function to create an OllamaContextProvider instance.
    
    Args:
        memory: Memory system instance
        tools: Dictionary of available tools
        config: Configuration dictionary
        
    Returns:
        Configured OllamaContextProvider instance
    """
    return OllamaContextProvider(memory=memory, tools=tools, config=config)
