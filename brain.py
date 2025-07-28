import logging
import requests
import json
import os

class UltronBrain:
    def __init__(self, config, tools, memory):
        self.config = config
        self.tools = tools
        self.memory = memory
        self.cache_file = "cache.json"
        self.load_cache()

    def load_cache(self):
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, "r") as f:
                    self.cache = json.load(f)
            else:
                self.cache = {}
        except Exception as e:
            logging.error(f"Failed to load cache: {e}")
            self.cache = {}

    def save_cache(self):
        with open(self.cache_file, "w") as f:
            json.dump(self.cache, f)

    def get_tool_descriptions(self) -> str:
        return "\n".join([f"- {t.name}: {t.description}" for t in self.tools])

    def build_prompt(self, user_input: str, previous_steps: str | None = None) -> str:
        prompt = f"User: {user_input}\n"
        if previous_steps:
            prompt += f"Previous Steps: {previous_steps}\n"
        prompt += "Tools available:\n" + self.get_tool_descriptions() + "\n"
        return prompt

    def query_llm(self, prompt: str) -> str:
        cache_key = hash(prompt)
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={"model": "llama3.2:latest", "messages": [{"role": "user", "content": prompt}]},
                headers={"Authorization": f"Bearer {self.config.data['ollama_api_key']}"}
            )
            response.raise_for_status()
            reply = response.json().get("message", {}).get("content", "")
            self.cache[cache_key] = reply
            self.save_cache()
            return reply
        except Exception as e:
            logging.error(f"LLM query error: {e}")
            return "[LLM unavailable. Please configure OpenAI or Ollama.]"

    def plan_and_act(self, user_input: str) -> str:
        if "switch model" in user_input.lower():
            new_model = user_input.split("to")[-1].strip()
            return f"Switched Ollama model to {new_model}"

        prompt = self.build_prompt(user_input)
        reply = self.query_llm(prompt)
        if not reply:
            return "No response from LLM."
        if ":" in reply:
            tool_name, _, arg = reply.partition(":")
            return f"Tool {tool_name} not found."
        return reply