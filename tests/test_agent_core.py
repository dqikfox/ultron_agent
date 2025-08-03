import pytest
import asyncio
from unittest.mock import MagicMock, patch
from agent_core import UltronAgent, AgentStatus
from config import Config

# Mock configuration for testing
@pytest.fixture
def mock_config():
    config = MagicMock(spec=Config)
    config.data = {
        "use_voice": False,
        "use_gui": False,
        "use_pochi": False,
        "llm_model": "test_model",
        "ollama_base_url": "http://localhost:11434"
    }
    return config

@pytest.fixture
@patch('agent_core.ensure_ollama_running', MagicMock())
@patch('agent_core.UltronAgent.load_tools', MagicMock(return_value=[]))
@patch('brain.UltronBrain')
def agent(MockBrain, mock_config):
    # Mock the brain's async methods
    mock_brain_instance = MockBrain.return_value
    mock_brain_instance.plan_and_act = MagicMock(return_value=asyncio.Future())
    mock_brain_instance.plan_and_act.return_value.set_result("Test response")
    
    # Patch config loader
    with patch('agent_core.Config', return_value=mock_config):
        agent_instance = UltronAgent()
        agent_instance.brain = mock_brain_instance
        return agent_instance


# Test Cases

def test_agent_initialization(agent):
    assert agent is not None
    assert agent.status == AgentStatus.INITIALIZING
    assert agent.brain is not None
    assert agent.tools == []

def test_list_tools_empty(agent):
    assert agent.list_tools() == []

@patch('agent_core.UltronAgent.load_tools')
def test_list_tools_with_mock_tools(mock_load_tools, agent):
    mock_tool_schema = {
        "name": "mock_tool",
        "description": "A mock tool for testing",
        "parameters": {"type": "object", "properties": {}}
    }
    mock_tool = MagicMock()
    mock_tool.__class__.schema.return_value = mock_tool_schema
    mock_load_tools.return_value = [mock_tool]
    
    agent.tools = agent.load_tools()
    
    tool_list = agent.list_tools()
    assert len(tool_list) == 1
    assert tool_list[0] == mock_tool_schema

@pytest.mark.asyncio
async def test_handle_command(agent):
    command = "test command"
    response = agent.handle_command(command)
    
    # Check if brain was called correctly
    agent.brain.plan_and_act.assert_called_once_with(command)
    assert response == "Test response"

def test_handle_text_empty_input(agent):
    response = agent.handle_text("")
    assert "Please provide a valid command" in response
    response_ws = agent.handle_text("   ")
    assert "Please provide a valid command" in response_ws

@pytest.mark.asyncio
async def test_process_command_flow(agent):
    command = "process this command"
    
    with patch.object(agent.event_system, 'emit', new_callable=MagicMock) as mock_emit,
         patch.object(agent.memory, 'add_to_short_term') as mock_add_memory,
         patch.object(agent.performance_monitor, 'get_metrics_summary', return_value={"cpu_avg": 50}):
        
        # Set up an awaitable mock for emit
        async def async_magic():
            pass
        mock_emit.side_effect = async_magic

        response = await agent.process_command(command)
        
        # Verify event emissions
        mock_emit.assert_any_call("command_start", command)
        mock_emit.assert_any_call("command_complete", {"command": command, "result": "Test response"})
        
        # Verify memory interaction
        mock_add_memory.assert_any_call({"role": "user", "content": command})
        mock_add_memory.assert_any_call({"role": "system", "content": "Test response"})

        assert response == "Test response"

@pytest.mark.asyncio
async def test_process_command_high_load(agent):
    command = "process this command"
    
    with patch.object(agent.performance_monitor, 'get_metrics_summary', return_value={"cpu_avg": 95}):
        response = await agent.process_command(command)
        assert "System is under heavy load" in response

@pytest.mark.asyncio
async def test_stop_agent(agent):
    with patch.object(agent.event_system, 'emit', new_callable=MagicMock) as mock_emit,
         patch.object(agent.performance_monitor, 'stop_monitoring') as mock_stop_perf,
         patch.object(agent.task_scheduler, 'stop') as mock_stop_scheduler:
        
        # Mock awaitable methods
        async def async_magic(): pass
        mock_emit.side_effect = async_magic
        mock_stop_perf.side_effect = async_magic
        mock_stop_scheduler.side_effect = async_magic

        await agent.stop()
        
        mock_emit.assert_called_with("agent_stopping")
        mock_stop_perf.assert_called_once()
        mock_stop_scheduler.assert_called_once()
        assert agent.status == AgentStatus.MAINTENANCE

