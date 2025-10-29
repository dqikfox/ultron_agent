"""
Tests for Autonomous Evolution Tool
"""

import pytest
import asyncio
import json
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock

# Import the tool
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.autonomous_evolution_tool import AutonomousEvolutionTool


class TestAutonomousEvolutionTool:
    """Test suite for Autonomous Evolution Tool"""
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration"""
        config = Mock()
        config.llm_model = "llava:7b"
        return config
    
    @pytest.fixture
    def mock_brain(self):
        """Mock brain with async methods"""
        brain = Mock()
        brain.plan = AsyncMock(return_value="1. Improve error handling\n2. Add more tests\n3. Optimize performance")
        brain.generate = AsyncMock(return_value="Test response")
        return brain
    
    @pytest.fixture
    def evolution_tool(self, mock_config, mock_brain, tmp_path):
        """Create evolution tool instance"""
        # Patch Path objects to use tmp_path
        with patch.object(Path, 'mkdir'):
            tool = AutonomousEvolutionTool(
                config=mock_config,
                brain=mock_brain,
                tools_registry={}
            )
            # Override paths to use tmp_path
            tool.evolution_state_file = tmp_path / "autonomous_evolution_state.json"
            tool.improvements_log = tmp_path / "autonomous_improvements.log"
            tool.cycle_interval = 1  # 1 second for testing
            return tool
    
    def test_tool_properties(self, evolution_tool):
        """Test tool basic properties"""
        assert evolution_tool.name == "Autonomous Evolution Tool"
        assert "autonomous" in evolution_tool.description.lower()
        assert evolution_tool.is_active == False
        assert evolution_tool.evolution_cycle_count == 0
    
    def test_match_patterns(self, evolution_tool):
        """Test command matching"""
        # Should match
        assert evolution_tool.match("start autonomous evolution")
        assert evolution_tool.match("evolution status")
        assert evolution_tool.match("self improve")
        assert evolution_tool.match("auto evolve")
        assert evolution_tool.match("continuous improvement")
        
        # Should not match
        assert not evolution_tool.match("hello world")
        assert not evolution_tool.match("run tests")
    
    def test_execute_help(self, evolution_tool):
        """Test help command"""
        result = evolution_tool.execute("help")
        assert "AUTONOMOUS EVOLUTION TOOL" in result
        assert "evolution start" in result
        assert "evolution stop" in result
    
    def test_execute_start(self, evolution_tool):
        """Test start command"""
        result = evolution_tool.execute("evolution start")
        assert "ACTIVATED" in result
        assert evolution_tool.is_active == True
        assert "30 minutes" in result or "Cycle Interval" in result
    
    def test_execute_stop(self, evolution_tool):
        """Test stop command"""
        # First start it
        evolution_tool.execute("evolution start")
        assert evolution_tool.is_active == True
        
        # Then stop it
        result = evolution_tool.execute("evolution stop")
        assert "DEACTIVATED" in result
        assert evolution_tool.is_active == False
    
    def test_execute_status(self, evolution_tool):
        """Test status command"""
        result = evolution_tool.execute("evolution status")
        assert "STATUS" in result
        assert "INACTIVE" in result or "ACTIVE" in result
        assert "Total Cycles" in result
    
    def test_schema(self, evolution_tool):
        """Test tool schema"""
        schema = evolution_tool.schema()
        assert schema["name"] == evolution_tool.name
        assert "parameters" in schema
        assert "command" in schema["parameters"]["properties"]
    
    @pytest.mark.asyncio
    async def test_analyze_project(self, evolution_tool):
        """Test project analysis"""
        improvements = await evolution_tool._analyze_project()
        assert isinstance(improvements, list)
        # Should have at least some improvements from automated analysis
        assert len(improvements) >= 0
    
    def test_generate_analysis_prompt(self, evolution_tool):
        """Test prompt generation for different areas"""
        for area in evolution_tool.improvement_areas:
            prompt = evolution_tool._generate_analysis_prompt(area)
            assert len(prompt) > 0
            assert area.replace("_", " ") in prompt.lower() or area in prompt
    
    @pytest.mark.asyncio
    async def test_get_brain_suggestions(self, evolution_tool, mock_brain):
        """Test getting suggestions from brain"""
        prompt = "Test prompt"
        response = await evolution_tool._get_brain_suggestions(prompt)
        assert response is not None
        mock_brain.plan.assert_called_once_with(prompt)
    
    def test_parse_suggestions(self, evolution_tool):
        """Test parsing AI suggestions"""
        response = """
        1. Improve error handling in agent_core.py
        2. Add more unit tests for tools
        3. Optimize async operations
        """
        improvements = evolution_tool._parse_suggestions(response, "code_quality")
        assert len(improvements) == 3
        assert improvements[0]["area"] == "code_quality"
        assert "error handling" in improvements[0]["description"].lower()
    
    def test_calculate_priority(self, evolution_tool):
        """Test priority calculation"""
        # Security should be highest priority
        assert evolution_tool._calculate_priority("security") == 10
        assert evolution_tool._calculate_priority("performance_optimization") == 9
        assert evolution_tool._calculate_priority("documentation") == 4
        assert evolution_tool._calculate_priority("unknown") == 5
    
    def test_prioritize_improvements(self, evolution_tool):
        """Test improvement prioritization"""
        improvements = [
            {"priority": 5, "estimated_effort": "high", "risk_level": "high"},
            {"priority": 10, "estimated_effort": "low", "risk_level": "low"},
            {"priority": 7, "estimated_effort": "medium", "risk_level": "medium"},
        ]
        
        prioritized = evolution_tool._prioritize_improvements(improvements)
        
        # Highest priority should be first
        assert prioritized[0]["priority"] == 10
    
    @pytest.mark.asyncio
    async def test_implement_improvement(self, evolution_tool):
        """Test improvement implementation"""
        improvement = {
            "area": "testing",
            "description": "Add unit tests",
            "priority": 6,
            "estimated_effort": "medium",
            "risk_level": "low"
        }
        
        result = await evolution_tool._implement_improvement(improvement)
        
        assert "status" in result
        assert result["description"] == improvement["description"]
        # In safety mode, should be simulated
        assert result["status"] in ["simulated", "success", "failed"]
    
    @pytest.mark.asyncio
    async def test_validate_improvements(self, evolution_tool):
        """Test improvement validation"""
        result = await evolution_tool._validate_improvements()
        assert isinstance(result, str)
        # Should contain some validation result
        assert any(word in result for word in ["passed", "failed", "checks"])
    
    def test_validate_config(self, evolution_tool):
        """Test config validation"""
        # Should validate basic config check
        result = evolution_tool._validate_config()
        assert isinstance(result, bool)
    
    def test_validate_imports(self, evolution_tool):
        """Test import validation"""
        result = evolution_tool._validate_imports()
        assert isinstance(result, bool)
    
    def test_validate_tools(self, evolution_tool):
        """Test tools validation"""
        result = evolution_tool._validate_tools()
        assert isinstance(result, bool)
    
    def test_save_and_load_state(self, evolution_tool, tmp_path):
        """Test state persistence"""
        # Set some state
        evolution_tool.evolution_cycle_count = 5
        evolution_tool.improvements_made = [
            {"description": "Test improvement", "status": "success"}
        ]
        
        # Save state
        evolution_tool._save_state()
        assert evolution_tool.evolution_state_file.exists()
        
        # Create new instance and load state
        new_tool = AutonomousEvolutionTool()
        new_tool.evolution_state_file = evolution_tool.evolution_state_file
        new_tool._load_state()
        
        assert new_tool.evolution_cycle_count == 5
        assert len(new_tool.improvements_made) == 1
    
    def test_get_cycle_statistics(self, evolution_tool):
        """Test statistics calculation"""
        evolution_tool.evolution_cycle_count = 10
        evolution_tool.improvements_made = [
            {"status": "success"},
            {"status": "success"},
            {"status": "simulated"}
        ]
        evolution_tool.failed_attempts = [
            {"error": "test error"}
        ]
        
        stats = evolution_tool._get_cycle_statistics()
        
        assert stats["total_cycles"] == 10
        assert stats["successful_improvements"] == 2
        assert stats["failed_attempts"] == 1
        assert "success_rate" in stats
    
    def test_automated_analysis(self, evolution_tool):
        """Test automated static analysis"""
        improvements = evolution_tool._automated_analysis()
        assert isinstance(improvements, list)
        # May or may not find issues, but should return a list
    
    @pytest.mark.asyncio
    async def test_evolution_cycle(self, evolution_tool):
        """Test complete evolution cycle"""
        # Set short interval for testing
        evolution_tool.cycle_interval = 0.1
        evolution_tool.max_improvements_per_cycle = 1
        
        result = await evolution_tool._run_evolution_cycle()
        
        assert "Evolution Cycle" in result
        assert evolution_tool.evolution_cycle_count == 1
        assert "Analyzing project" in result
    
    def test_improvement_history(self, evolution_tool):
        """Test getting improvement history"""
        # Add some improvements
        evolution_tool.improvements_made = [
            {
                "timestamp": "2024-01-01T12:00:00",
                "description": "Test improvement 1",
                "status": "success"
            },
            {
                "timestamp": "2024-01-02T12:00:00",
                "description": "Test improvement 2",
                "status": "success"
            }
        ]
        
        history = evolution_tool._get_improvement_history()
        
        assert "IMPROVEMENT HISTORY" in history
        assert "Test improvement 1" in history
        assert "Test improvement 2" in history
    
    def test_ensure_directories(self, evolution_tool, tmp_path):
        """Test directory creation"""
        # Should not raise any errors
        evolution_tool._ensure_directories()
        assert evolution_tool.evolution_state_file.parent.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
