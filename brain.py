import logging
import requests
import json
import os
import asyncio
from tools.agent_network import AgentNetwork
from tools.openai_tools import OpenAITools

class UltronBrain:
    def __init__(self, config, tools, memory):
        self.config = config
        self.tools = tools
        self.memory = memory
        self.cache_file = "cache.json"
        self.load_cache()
        
        # Initialize POCHI availability
        self.pochi_available = config.data.get("use_pochi", False)
        
        # Initialize agent network and OpenAI tools if available
        self.agent_network = None
        self.openai_tools = None
        if config.data.get("openai_api_key"):
            try:
                self.agent_network = AgentNetwork(config)
                self.openai_tools = OpenAITools(config)
                self._register_tools()
                logging.info("Agent network initialized")
            except Exception as e:
                logging.error(f"Agent network initialization failed: {e}")

    def load_cache(self):
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, "r") as f:
                    self.cache = json.load(f)
            else:
                self.cache = {}
        except Exception as e:
            logging.error(f"Failed to load cache: {e} - brain.py:22")
            self.cache = {}

    def save_cache(self):
        with open(self.cache_file, "w") as f:
            json.dump(self.cache, f)

    def get_tool_descriptions(self) -> str:
        return "\n".join([
            f"- {t.name}: {t.description}\n  Parameters: {getattr(t, 'parameters', {})}" for t in self.tools
        ])

    def build_prompt(self, user_input: str, previous_steps: str | None = None) -> str:
        prompt = f"User: {user_input}\n"
        if previous_steps:
            prompt += f"Previous Steps: {previous_steps}\n"
        prompt += "Tools available:\n" + self.get_tool_descriptions() + "\n"
        prompt += "\nIf you want to use a tool, reply in the format: TOOL:<tool_name> PARAMS:<json_parameters>\n"
        return prompt

    def _register_tools(self):
        """Register available tools with the agent network."""
        if self.agent_network:
            tool_list = []
            for tool in self.tools:
                tool_dict = {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": getattr(tool, 'parameters', {})
                    }
                }
                tool_list.append(tool_dict)
            self.agent_network.register_tools(tool_list)

    async def query_llm(self, prompt: str, progress_callback=None) -> str:
        cache_key = hash(prompt)
        if cache_key in self.cache:
            if progress_callback:
                progress_callback(100, "Loaded from cache.")
            return self.cache[cache_key]

        try:
            # Try POCHI first for complex reasoning if available
            if hasattr(self, 'pochi_available') and self.pochi_available:
                try:
                    from tools.pochi_tool import get_pochi_manager
                    pochi = get_pochi_manager()
                    if pochi.is_available():
                        response = await pochi.chat_with_pochi(prompt)
                        if response and not response.startswith("POCHI error"):
                            self.cache[cache_key] = response
                            return response
                except Exception as e:
                    logging.error(f"POCHI query failed: {e}")
            
            # Try agent network next if available
            if self.agent_network:
                try:
                    context = {
                        "memory": self.memory.get_recent_memory(),
                        "tools_available": len(self.tools)
                    }
                    result = await self.agent_network.process_request(prompt, context=context)
                    response = result["response"]
                    self.cache[cache_key] = response
                    return response
                except Exception as e:
                    logging.error(f"Agent network query failed: {e}")
                    
            # Fallback to direct Ollama
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={"model": "qwen2.5", "messages": [{"role": "user", "content": prompt}]},
                headers={"Authorization": f"Bearer {self.config.data.get('ollama_api_key', '')}"}
            )
            response.raise_for_status()
            lines = response.text.strip().splitlines()
            import json as jsonlib
            reply_parts = []
            total = len(lines)
            for idx, line in enumerate(lines):
                try:
                    data = jsonlib.loads(line)
                    content = data.get("message", {}).get("content", "")
                    if content:
                        reply_parts.append(content)
                    if progress_callback:
                        percent = int((idx + 1) / total * 100) if total > 0 else 100
                        progress_callback(percent, f"Processing chunk {idx+1}/{total}")
                except Exception:
                    if progress_callback:
                        progress_callback(0, "Error parsing chunk.", error=True)
                    continue
            reply = "".join(reply_parts).strip()
            if reply:
                self.cache[cache_key] = reply
                self.save_cache()
                if progress_callback:
                    progress_callback(100, "Complete.")
                return reply
            logging.error(f"Ollama streaming response could not be parsed. Raw response: {response.text} - brain.py:77")
            if progress_callback:
                progress_callback(0, "Could not parse Ollama streaming response.", error=True)
            print("[DEBUG] Ollama raw response:\n - brain.py:80" + response.text)
            return "[LLM error: Could not parse Ollama streaming response. See logs for details.]"
        except Exception as e:
            logging.error(f"LLM query error: {e} - brain.py:83")
            if progress_callback:
                progress_callback(0, f"LLM query error: {e}", error=True)
            return "[LLM unavailable. Please configure OpenAI or Ollama.]"

    async def plan_and_act(self, user_input: str, progress_callback=None) -> str:
        import re, json
        prompt = self.build_prompt(user_input)
        reply = await self.query_llm(prompt, progress_callback=progress_callback)
        if not reply:
            return "No response from LLM."
        # Check for tool call in LLM reply
        tool_call = re.search(r'TOOL:(\w+) PARAMS:(\{.*\})', reply)
        if tool_call:
            tool_name = tool_call.group(1)
            try:
                params = json.loads(tool_call.group(2))
            except Exception as e:
                return f"Failed to parse tool parameters: {e}\nRaw: {tool_call.group(2)}"
            for tool in self.tools:
                if tool.name == tool_name:
                    try:
                        return tool.execute(**params)
                    except Exception as e:
                        return f"Tool error: {e}"
            return f"Tool '{tool_name}' not found."
        # Fallback: try to match a tool by user input
        for tool in self.tools:
            if tool.match(user_input):
                try:
                    return tool.execute(user_input)
                except Exception as e:
                    return f"Tool error: {e}"
        # If user asked for functionality, list tools
        if any(word in user_input.lower() for word in ["functionality", "can you do", "what can you do", "help", "tools"]):
            return "Available tools:\n" + self.get_tool_descriptions()
        return reply