import pytest
import json
import os
from unittest.mock import Mock, patch, mock_open, MagicMock
import asyncio
from brain import UltronBrain

import pytest
import json
import os
from unittest.mock import Mock, patch, mock_open, MagicMock
import asyncio
from brain import UltronBrain

class TestUltronBrain:
    
    @pytest.fixture
    def mock_config(self):
        config = Mock()
        config.data = {"openai_api_key": "test_key", "ollama_api_key": "ollama_key"}
        return config
    
    @pytest.fixture
    def mock_config_no_openai(self):
        config = Mock()
        config.data = {}
        return config
    
    @pytest.fixture
    def mock_tools(self):
        tool1 = Mock()
        tool1.name = "test_tool"
        tool1.description = "A test tool"
        tool1.parameters = {"param1": "string"}
        tool1.match.return_value = False
        tool1.execute.return_value = "Tool executed"
        
        tool2 = Mock()
        tool2.name = "search_tool"
        tool2.description = "Search functionality"
        tool2.parameters = {"query": "string"}
        tool2.match.return_value = False
        tool2.execute.return_value = "Search results"
        
        return [tool1, tool2]
    
    @pytest.fixture
    def mock_memory(self):
        memory = Mock()
        memory.get_recent_memory.return_value = ["previous context"]
        return memory
    
    @pytest.fixture
    def brain(self, mock_config_no_openai, mock_tools, mock_memory):
        with patch('brain.os.path.exists', return_value=False):
            return UltronBrain(mock_config_no_openai, mock_tools, mock_memory)
    
    def test_init_without_openai_key(self, mock_config_no_openai, mock_tools, mock_memory):
        with patch('brain.os.path.exists', return_value=False):
            brain = UltronBrain(mock_config_no_openai, mock_tools, mock_memory)
            assert brain.config == mock_config_no_openai
            assert brain.tools == mock_tools
            assert brain.memory == mock_memory
            assert brain.agent_network is None
            assert brain.openai_tools is None
    
    @patch('brain.AgentNetwork')
    @patch('brain.OpenAITools')
    def test_init_with_openai_key(self, mock_openai_tools, mock_agent_network, mock_config, mock_tools, mock_memory):
        with patch('brain.os.path.exists', return_value=False):
            brain = UltronBrain(mock_config, mock_tools, mock_memory)
            assert brain.agent_network is not None
            assert brain.openai_tools is not None
            mock_agent_network.assert_called_once_with(mock_config)
            mock_openai_tools.assert_called_once_with(mock_config)
    
    def test_load_cache_file_exists(self, mock_config_no_openai, mock_tools, mock_memory):
        cache_data = {"key": "value"}
        with patch('brain.os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=json.dumps(cache_data))):
            brain = UltronBrain(mock_config_no_openai, mock_tools, mock_memory)
            assert brain.cache == cache_data
    
    def test_load_cache_file_not_exists(self, mock_config_no_openai, mock_tools, mock_memory):
        with patch('brain.os.path.exists', return_value=False):
            brain = UltronBrain(mock_config_no_openai, mock_tools, mock_memory)
            assert brain.cache == {}
    
    def test_load_cache_error(self, mock_config_no_openai, mock_tools, mock_memory):
        with patch('brain.os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data="invalid json")), \
             patch('brain.logging'):
            brain = UltronBrain(mock_config_no_openai, mock_tools, mock_memory)
            assert brain.cache == {}
    
    def test_save_cache(self, brain):
        brain.cache = {"test": "data"}
        with patch('builtins.open', mock_open()) as mock_file:
            brain.save_cache()
            mock_file.assert_called_once_with("cache.json", "w")
            handle = mock_file()
            handle.write.assert_called()
    
    def test_get_tool_descriptions(self, brain):
        result = brain.get_tool_descriptions()
        expected = "- test_tool: A test tool\n  Parameters: {'param1': 'string'}\n- search_tool: Search functionality\n  Parameters: {'query': 'string'}"
        assert result == expected
    
    def test_build_prompt_without_previous_steps(self, brain):
        user_input = "Hello world"
        result = brain.build_prompt(user_input)
        assert "User: Hello world" in result
        assert "Tools available:" in result
        assert "TOOL:<tool_name> PARAMS:<json_parameters>" in result
    
    def test_build_prompt_with_previous_steps(self, brain):
        user_input = "Hello world"
        previous_steps = "Step 1: Did something"
        result = brain.build_prompt(user_input, previous_steps)
        assert "User: Hello world" in result
        assert "Previous Steps: Step 1: Did something" in result
        assert "Tools available:" in result
    
    def test_register_tools(self, mock_config, mock_tools, mock_memory):
        with patch('brain.os.path.exists', return_value=False), \
             patch('brain.AgentNetwork') as mock_agent_network, \
             patch('brain.OpenAITools'):
            brain = UltronBrain(mock_config, mock_tools, mock_memory)
            mock_agent_network.return_value.register_tools.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_query_llm_cached(self, brain):
        prompt = "test prompt"
        cached_response = "cached response"
        brain.cache[hash(prompt)] = cached_response
        
        result = await brain.query_llm(prompt)
        assert result == cached_response
    
    @pytest.mark.asyncio
    async def test_query_llm_agent_network_success(self, mock_config, mock_tools, mock_memory):
        with patch('brain.os.path.exists', return_value=False), \
             patch('brain.AgentNetwork') as mock_agent_network, \
             patch('brain.OpenAITools'):
            
            mock_agent_network.return_value.process_request.return_value = {"response": "agent response"}
            brain = UltronBrain(mock_config, mock_tools, mock_memory)
            
            result = await brain.query_llm("test prompt")
            assert result == "agent response"
    
    @pytest.mark.asyncio
    async def test_query_llm_ollama_fallback(self, brain):
        mock_response = Mock()
        mock_response.text = '{"message": {"content": "Hello"}}\n{"message": {"content": " World"}}'
        mock_response.raise_for_status.return_value = None
        
        with patch('brain.requests.post', return_value=mock_response):
            result = await brain.query_llm("test prompt")
            assert result == "Hello World"
    
    @pytest.mark.asyncio
    async def test_query_llm_error(self, brain):
        with patch('brain.requests.post', side_effect=Exception("Network error")), \
             patch('brain.logging'):
            result = await brain.query_llm("test prompt")
            assert "[LLM unavailable. Please configure OpenAI or Ollama.]" in result
    
    @pytest.mark.asyncio
    async def test_plan_and_act_tool_call(self, brain):
        llm_response = "TOOL:test_tool PARAMS:{\"param1\": \"value1\"}"
        
        with patch.object(brain, 'query_llm', return_value=llm_response):
            result = await brain.plan_and_act("test input")
            assert result == "Tool executed"
    
    @pytest.mark.asyncio
    async def test_plan_and_act_tool_call_invalid_json(self, brain):
        llm_response = "TOOL:test_tool PARAMS:{invalid json}"
        
        with patch.object(brain, 'query_llm', return_value=llm_response):
            result = await brain.plan_and_act("test input")
            assert "Failed to parse tool parameters" in result
    
    @pytest.mark.asyncio
    async def test_plan_and_act_tool_not_found(self, brain):
        llm_response = "TOOL:nonexistent_tool PARAMS:{\"param1\": \"value1\"}"
        
        with patch.object(brain, 'query_llm', return_value=llm_response):
            result = await brain.plan_and_act("test input")
            assert "Tool 'nonexistent_tool' not found." in result
    
    @pytest.mark.asyncio
    async def test_plan_and_act_tool_match(self, brain):
        brain.tools[0].match.return_value = True
        
        with patch.object(brain, 'query_llm', return_value="no tool call"):
            result = await brain.plan_and_act("test input")
            assert result == "Tool executed"
    
    @pytest.mark.asyncio
    async def test_plan_and_act_help_request(self, brain):
        with patch.object(brain, 'query_llm', return_value="no tool call"):
            result = await brain.plan_and_act("what can you do")
            assert "Available tools:" in result
    
    @pytest.mark.asyncio
    async def test_plan_and_act_fallback(self, brain):
        llm_response = "Just a normal response"
        
        with patch.object(brain, 'query_llm', return_value=llm_response):
            result = await brain.plan_and_act("test input")
            assert result == llm_response
    
    @pytest.mark.asyncio
    async def test_plan_and_act_no_response(self, brain):
        with patch.object(brain, 'query_llm', return_value=""):
            result = await brain.plan_and_act("test input")
            assert result == "No response from LLM."
    
    @pytest.mark.asyncio
    async def test_plan_and_act_tool_execution_error(self, brain):
        brain.tools[0].execute.side_effect = Exception("Tool error")
        llm_response = "TOOL:test_tool PARAMS:{\"param1\": \"value1\"}"
        
        with patch.object(brain, 'query_llm', return_value=llm_response):
            result = await brain.plan_and_act("test input")
            assert "Tool error: Tool error" in result

