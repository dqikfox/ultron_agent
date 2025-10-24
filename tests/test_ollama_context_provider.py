"""
Tests for OllamaContextProvider

Tests the universal context injection system for Ollama models.
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.ollama_context_provider import OllamaContextProvider, create_ollama_context_provider


class MockMemory:
    """Mock memory system for testing"""
    
    def __init__(self):
        self.short_term = [
            "User asked about weather",
            "Assistant provided forecast",
            {"content": "User thanked assistant"}
        ]
        self.long_term = {
            "user_pref_1": "User prefers detailed explanations",
            "fact_1": {"content": "Python is a programming language"}
        }
    
    def retrieve_short_term(self):
        return self.short_term
    
    def retrieve_long_term(self):
        return self.long_term
    
    def get_system_prompt(self):
        return "You are ULTRON, an advanced AI assistant."


class MockTool:
    """Mock tool for testing"""
    
    def __init__(self, name="TestTool", description="A test tool"):
        self._name = name
        self._description = description
    
    def match(self, command):
        return "test" in command.lower()
    
    def execute(self, command):
        return f"Executed: {command}"
    
    def schema(self):
        return {
            "name": self._name,
            "description": self._description,
            "parameters": {
                "type": "object",
                "properties": {
                    "input": {"type": "string", "description": "Test input"}
                },
                "required": ["input"]
            }
        }


class TestOllamaContextProvider:
    """Test suite for OllamaContextProvider"""
    
    def test_initialization(self):
        """Test basic initialization"""
        provider = OllamaContextProvider()
        assert provider is not None
        assert provider.tools == {}
        assert provider.config == {}
        assert provider.memory is None
    
    def test_initialization_with_components(self):
        """Test initialization with memory, tools, and config"""
        memory = MockMemory()
        tools = {"test_tool": MockTool()}
        config = {"ollama_include_memory": True}
        
        provider = OllamaContextProvider(memory=memory, tools=tools, config=config)
        
        assert provider.memory is not None
        assert len(provider.tools) == 1
        assert provider.config == config
        assert provider.include_memory is True
    
    def test_factory_function(self):
        """Test the factory function"""
        memory = MockMemory()
        tools = {"test_tool": MockTool()}
        config = {}
        
        provider = create_ollama_context_provider(memory=memory, tools=tools, config=config)
        
        assert isinstance(provider, OllamaContextProvider)
        assert provider.memory is not None
        assert len(provider.tools) == 1
    
    def test_build_enhanced_prompt_basic(self):
        """Test building enhanced prompt with no context"""
        provider = OllamaContextProvider()
        user_prompt = "What is the weather today?"
        
        enhanced = provider.build_enhanced_prompt(user_prompt, "llama3.1")
        
        # With no context, should return original prompt
        assert "What is the weather today?" in enhanced
    
    def test_build_enhanced_prompt_with_capabilities(self):
        """Test building prompt with capabilities context"""
        config = {"ollama_include_capabilities": True}
        provider = OllamaContextProvider(config=config)
        
        enhanced = provider.build_enhanced_prompt("Hello", "llama3.1")
        
        assert "ULTRON" in enhanced
        assert "capabilities" in enhanced.lower()
    
    def test_build_enhanced_prompt_with_memory(self):
        """Test building prompt with memory context"""
        memory = MockMemory()
        config = {"ollama_include_memory": True}
        provider = OllamaContextProvider(memory=memory, config=config)
        
        enhanced = provider.build_enhanced_prompt("Continue our conversation", "llama3.1")
        
        # Should include memory context
        assert "weather" in enhanced or "Recent" in enhanced
    
    def test_build_enhanced_prompt_with_tools(self):
        """Test building prompt with tools context"""
        tools = {
            "test_tool": MockTool("TestTool", "A test tool"),
            "another_tool": MockTool("AnotherTool", "Another test tool")
        }
        config = {"ollama_include_tools": True}
        provider = OllamaContextProvider(tools=tools, config=config)
        
        enhanced = provider.build_enhanced_prompt("What can you do?", "llama3.1")
        
        # Should include tools context
        assert "Tools" in enhanced or "TestTool" in enhanced
    
    def test_build_enhanced_prompt_complete_context(self):
        """Test building prompt with all context sections"""
        memory = MockMemory()
        tools = {"test_tool": MockTool()}
        config = {
            "ollama_include_memory": True,
            "ollama_include_tools": True,
            "ollama_include_capabilities": True
        }
        provider = OllamaContextProvider(memory=memory, tools=tools, config=config)
        
        enhanced = provider.build_enhanced_prompt("Tell me everything", "llama3.1")
        
        # Should include all sections
        assert "ULTRON" in enhanced
        assert len(enhanced) > len("Tell me everything")
    
    def test_get_tools_as_function_schemas(self):
        """Test getting tools in function calling format"""
        tools = {
            "tool1": MockTool("Tool1", "First tool"),
            "tool2": MockTool("Tool2", "Second tool")
        }
        provider = OllamaContextProvider(tools=tools)
        
        schemas = provider.get_tools_as_function_schemas()
        
        assert isinstance(schemas, list)
        assert len(schemas) == 2
        assert all('name' in schema for schema in schemas)
        assert all('description' in schema for schema in schemas)
    
    def test_update_memory(self):
        """Test updating memory reference"""
        provider = OllamaContextProvider()
        assert provider.memory is None
        
        new_memory = MockMemory()
        provider.update_memory(new_memory)
        
        assert provider.memory is not None
        assert provider.memory == new_memory
    
    def test_update_tools(self):
        """Test updating tools dictionary"""
        provider = OllamaContextProvider()
        assert len(provider.tools) == 0
        
        new_tools = {"tool1": MockTool()}
        provider.update_tools(new_tools)
        
        assert len(provider.tools) == 1
        assert "tool1" in provider.tools
    
    def test_update_config(self):
        """Test updating configuration"""
        provider = OllamaContextProvider(config={"ollama_include_memory": False})
        assert provider.include_memory is False
        
        new_config = {"ollama_include_memory": True}
        provider.update_config(new_config)
        
        assert provider.include_memory is True
    
    def test_get_context_stats(self):
        """Test getting context statistics"""
        memory = MockMemory()
        tools = {"tool1": MockTool(), "tool2": MockTool()}
        config = {"ollama_include_memory": True}
        provider = OllamaContextProvider(memory=memory, tools=tools, config=config)
        
        stats = provider.get_context_stats()
        
        assert isinstance(stats, dict)
        assert 'timestamp' in stats
        assert stats['memory_available'] is True
        assert stats['tools_count'] == 2
        assert stats['config_loaded'] is True
    
    def test_context_limits(self):
        """Test that context limits are respected"""
        # Create many memory items
        memory = MockMemory()
        memory.short_term = [f"Item {i}" for i in range(100)]
        
        config = {"ollama_max_memory_items": 5}
        provider = OllamaContextProvider(memory=memory, config=config)
        
        enhanced = provider.build_enhanced_prompt("Test", "llama3.1")
        
        # Should not include all 100 items
        assert enhanced.count("Item") <= 5
    
    def test_tool_schema_limits(self):
        """Test that tool schema limits are respected"""
        # Create many tools
        tools = {f"tool_{i}": MockTool(f"Tool{i}") for i in range(50)}
        
        config = {"ollama_max_tool_schemas": 10}
        provider = OllamaContextProvider(tools=tools, config=config)
        
        schemas = provider.get_tools_as_function_schemas()
        
        # Should respect the limit
        assert len(schemas) <= 10
    
    def test_error_handling_in_prompt_building(self):
        """Test that errors don't crash prompt building"""
        
        class BrokenTool:
            def schema(self):
                raise Exception("Schema error")
        
        tools = {"broken": BrokenTool()}
        provider = OllamaContextProvider(tools=tools)
        
        # Should not raise exception
        enhanced = provider.build_enhanced_prompt("Test", "llama3.1")
        assert isinstance(enhanced, str)
    
    def test_different_ollama_models(self):
        """Test that context building works for different Ollama models"""
        memory = MockMemory()
        tools = {"tool": MockTool()}
        provider = OllamaContextProvider(memory=memory, tools=tools)
        
        models = ["llama3.1", "llava:7b", "qwen3-coder:480b-cloud", "deepseek-r1:14b"]
        
        for model in models:
            enhanced = provider.build_enhanced_prompt("Test prompt", model)
            assert isinstance(enhanced, str)
            assert len(enhanced) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
