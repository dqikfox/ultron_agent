import pytest
import tools.agent_network as agent_network_module

from tools.agent_network import AgentNetwork

class DummyConfig:
    pass

@pytest.fixture
def agent_network(monkeypatch):
    """Create an AgentNetwork instance with a dummy config, stubbing OpenAITools."""
    # Stub OpenAITools to avoid needing API key
    class FakeOpenAITools:
        def __init__(self, config):
            pass
        async def agent_invoke_tools(self, prompt, tools, messages):
            return {"response": "", "tool_calls": [], "messages": None}
    # Patch OpenAITools in agent_network module and in openai_tools module
    monkeypatch.setattr(agent_network_module, 'OpenAITools', FakeOpenAITools)
    import tools.openai_tools as openai_tools_module
    monkeypatch.setattr(openai_tools_module, 'OpenAITools', FakeOpenAITools)
    return agent_network_module.AgentNetwork(DummyConfig())

@pytest.mark.asyncio
async def test_process_request_no_tool_calls(monkeypatch, agent_network):
    # Stub openai_tools.agent_invoke_tools to return no tool calls
    async def fake_agent_invoke_tools(prompt, tools, messages):
        return {"response": "hello world", "tool_calls": [], "messages": None}

    monkeypatch.setattr(agent_network.openai_tools, "agent_invoke_tools", fake_agent_invoke_tools)
    result = await agent_network.process_request(prompt="say hi")
    assert result == {"response": "hello world", "steps": 1}

@pytest.mark.asyncio
async def test_process_request_with_tool_calls(monkeypatch, agent_network):
    # Simulate two-step process: first call has a tool call, second has none
    responses = [
        {"response": "interim", "tool_calls": ["tool1"], "messages": [{"role": "assistant", "content": "step1"}]},
        {"response": "final output", "tool_calls": [], "messages": None}
    ]
    async def fake_agent_invoke_tools(prompt, tools, messages):
        return responses.pop(0)

    monkeypatch.setattr(agent_network.openai_tools, "agent_invoke_tools", fake_agent_invoke_tools)
    result = await agent_network.process_request(prompt="do work", max_steps=5)
    assert result == {"response": "final output", "steps": 2}
