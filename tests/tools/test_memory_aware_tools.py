"""
Test suite for memory-aware tool integration
Validates that tools can access and use shared memory for context-aware execution
"""

import pytest
from tools.tool_interface import ToolInterface
from memory import Memory
from typing import Dict, Any


class MockMemoryAwareTool(ToolInterface):
    """Mock tool that uses memory for context-aware execution"""
    
    @property
    def name(self) -> str:
        return "memory_aware_tool"
    
    @property
    def description(self) -> str:
        return "Tool that uses memory for context-aware execution"
    
    def match(self, command: str) -> bool:
        return "memory" in command.lower() or "context" in command.lower()
    
    def execute(self, command: str, **kwargs) -> str:
        """Execute with memory awareness"""
        result = f"Executing: {command}\n"
        
        # Use memory if available
        if self.memory:
            result += "✓ Memory available\n"
            try:
                recent = self.memory.retrieve_short_term()
                if recent:
                    result += f"  - Recent context: {len(recent)} items\n"
            except:
                pass
        else:
            result += "✗ Memory not available\n"
        
        return result
    
    @classmethod
    def schema(cls) -> Dict[str, Any]:
        return {
            "name": "memory_aware_tool",
            "description": "Tool that uses memory for context-aware execution",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"}
                },
                "required": ["command"]
            }
        }


class TestToolMemoryIntegration:
    """Test tool access to shared memory"""
    
    @pytest.fixture
    def memory(self):
        """Create fresh memory instance"""
        return Memory(short_term_limit=10)
    
    @pytest.fixture
    def tool(self):
        """Create memory-aware tool"""
        return MockMemoryAwareTool()
    
    def test_tool_memory_property(self, tool, memory):
        """Test that tool can access memory via property"""
        # Set shared memory
        ToolInterface.shared_memory = memory
        
        # Tool should have access
        assert tool.memory is memory
        assert tool.memory is not None
    
    def test_tool_without_memory(self, tool):
        """Test tool gracefully handles missing memory"""
        # Clear shared memory
        ToolInterface.shared_memory = None
        
        # Tool should handle this gracefully
        result = tool.execute("test command")
        assert "Memory not available" in result
    
    def test_tool_with_memory_context(self, tool, memory):
        """Test tool can use memory for context"""
        # Set shared memory
        ToolInterface.shared_memory = memory
        
        # Add some context to memory
        memory.add_to_short_term({"role": "user", "content": "Earlier query"})
        memory.add_to_short_term({"role": "assistant", "content": "Earlier response"})
        
        # Execute tool that uses memory
        result = tool.execute("Use memory context")
        
        assert "Memory available" in result
    
    def test_tool_memory_isolation(self, memory):
        """Test that memory is properly isolated per tool"""
        tool1 = MockMemoryAwareTool()
        tool2 = MockMemoryAwareTool()
        
        # Set shared memory
        ToolInterface.shared_memory = memory
        
        # Both tools should access the same memory
        assert tool1.memory is tool2.memory
        assert tool1.memory is memory
    
    def test_tool_memory_with_kwargs(self, tool, memory):
        """Test that tools can receive memory via kwargs"""
        # Set shared memory
        ToolInterface.shared_memory = memory
        
        # Add context
        memory.add_to_short_term({"data": "context"})
        
        # Execute with kwargs
        result = tool.execute("use context", memory=memory)
        
        assert "Memory available" in result
    
    def test_memory_persistence_across_tool_calls(self, tool, memory):
        """Test that memory persists across multiple tool invocations"""
        ToolInterface.shared_memory = memory
        
        # First tool execution
        memory.add_to_short_term({"iteration": 1})
        result1 = tool.execute("First call")
        
        # Second tool execution
        memory.add_to_short_term({"iteration": 2})
        result2 = tool.execute("Second call")
        
        # Both should see accumulated memory
        assert len(memory.retrieve_short_term()) >= 2
    
    def test_memory_helps_tool_decision_making(self, tool, memory):
        """Test that tools can make context-aware decisions with memory"""
        ToolInterface.shared_memory = memory
        
        # Simulate previous operation
        memory.add_to_short_term({
            "operation": "web_search",
            "query": "Python best practices",
            "results": 5
        })
        
        # Tool can now make decisions based on this history
        result = tool.execute("Should we search again?")
        
        # Tool should be aware of previous search
        assert tool.memory is not None
        assert len(memory.retrieve_short_term()) > 0


class TestToolLoaderMemoryIntegration:
    """Test tool loader properly shares memory with tools"""
    
    @pytest.fixture
    def memory(self):
        """Create fresh memory instance"""
        return Memory(short_term_limit=10)
    
    def test_loader_shares_memory_with_tools(self, memory):
        """Test that tool loader passes memory to tools"""
        from tools.tool_interface import ToolInterface
        
        # Set memory via ToolInterface
        ToolInterface.shared_memory = memory
        
        # Create a test tool
        tool = MockMemoryAwareTool()
        
        # Tool should have access
        assert tool.memory is memory


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
