import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from brain import UltronBrain
from config import Config
from memory import Memory

# Mock configuration and memory for testing
@pytest.fixture
def mock_config():
    config = MagicMock(spec=Config)
    config.data = {
        "llm_model": "test_model",
        "ollama_base_url": "http://localhost:11434",
        "openai_api_key": None, # Test without OpenAI tools initially
        "cache_enabled": True,
        "max_cache_size": 10
    }
    return config

@pytest.fixture
def mock_memory():
    memory = MagicMock(spec=Memory)
    memory.get_recent_memory.return_value = [{"role": "user", "content": "hello"}]
    return memory

@pytest.fixture
@patch('tools.agent_network.AgentNetwork', MagicMock())
def brain(mock_config, mock_memory):
    # Mock tools list
    mock_tool = MagicMock()
    mock_tool.name = "mock_tool"
    mock_tool.description = "A mock tool"
    mock_tool.parameters = {}
    brain_instance = UltronBrain(mock_config, [mock_tool], mock_memory)
    brain_instance.cache = {}
    brain_instance.save_cache = MagicMock()
    return brain_instance


# Test Cases

@pytest.mark.asyncio
async def test_direct_chat_success(brain):
    prompt = "test prompt"
    with patch('brain.aiohttp.ClientSession.post') as mock_post:
        # Mock the response context manager
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.raise_for_status = MagicMock()
        
        # Mock the content stream
        async def mock_content_stream():
            yield b'{"message": {"content": "Test"}, "done": false}'
            yield b'{"message": {"content": " response"}, "done": true}'
        
        mock_response.content = mock_content_stream()
        mock_post.return_value.__aenter__.return_value = mock_response

        response = await brain.direct_chat(prompt)
        assert response == "Test response"

@pytest.mark.asyncio
async def test_direct_chat_network_error(brain):
    prompt = "test prompt"
    with patch('brain.aiohttp.ClientSession.post', side_effect=asyncio.TimeoutError):
        response = await brain.direct_chat(prompt)
        assert "[Timeout error" in response


def test_build_prompt(brain):
    prompt = brain.build_prompt("user question")
    assert "user question" in prompt
    assert "Tools available" in prompt
    assert "mock_tool" in prompt

@pytest.mark.asyncio
async def test_query_llm_caching(brain):
    prompt = "cached prompt"
    brain.cache[hash(f"test_model:{prompt}")] = "cached response"
    
    response = await brain.query_llm(prompt)
    assert response == "cached response"

@pytest.mark.asyncio
async def test_query_llm_no_cache(brain):
    prompt = "new prompt"
    with patch.object(brain, 'direct_chat', new_callable=AsyncMock) as mock_direct_chat:
        mock_direct_chat.return_value = "fresh response"
        
        response = await brain.query_llm(prompt)
        assert response == "fresh response"
        
        # Check if it was cached
        cache_key = hash(f"test_model:{prompt}")
        assert brain.cache[cache_key] == "fresh response"

@pytest.mark.asyncio
async def test_plan_and_act_no_tool(brain):
    user_input = "just a question"
    with patch.object(brain, 'query_llm', new_callable=AsyncMock) as mock_query_llm:
        mock_query_llm.return_value = "A simple answer."
        
        response = await brain.plan_and_act(user_input)
        assert response == "A simple answer."

@pytest.mark.asyncio
async def test_plan_and_act_with_tool_call(brain):
    user_input = "use a tool"
    tool_response = 'TOOL: mock_tool PARAMS: {"param": "value"}'
    
    with patch.object(brain, 'query_llm', new_callable=AsyncMock) as mock_query_llm, \
         patch.object(brain.tools[0], 'execute', return_value="Tool executed") as mock_execute:
        
        mock_query_llm.return_value = tool_response
        
        response = await brain.plan_and_act(user_input)
        
        mock_execute.assert_called_once_with(param="value")
        assert response == "Tool executed"

@pytest.mark.asyncio
async def test_plan_and_act_direct_tool_match(brain):
    user_input = "mock_tool please"
    
    with patch.object(brain.tools[0], 'match', return_value=True), \
         patch.object(brain.tools[0], 'execute', return_value="Direct execution") as mock_execute:
        
        response = await brain.plan_and_act(user_input)
        
        mock_execute.assert_called_once_with(user_input)
        assert response == "Direct execution"

@pytest.mark.asyncio
async def test_plan_and_act_help_command(brain):
    user_input = "what can you do?"
    response = await brain.plan_and_act(user_input)
    assert "Available tools" in response
    assert "mock_tool" in response

