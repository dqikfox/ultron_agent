"""
AI Agent Console App using Microsoft Agent Framework (GitHub Model)
Features: LLM chat, web search, data extraction
"""

import asyncio
from agentframework import Agent, Tool, AgentContext
import requests
from bs4 import BeautifulSoup

# --- Tool: Web Search ---
class WebSearchTool(Tool):
    name = "web_search"
    description = "Search the web and return top results."

    async def execute(self, context: AgentContext, query: str) -> str:
        url = f"https://duckduckgo.com/html/?q={query}"
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        results = []
        for a in soup.select('.result__a')[:3]:
            results.append(f"- {a.get_text(strip=True)}: {a['href']}")
        return "\n".join(results) if results else "No results found."

# --- Tool: Data Extraction ---
class DataExtractionTool(Tool):
    name = "extract_data"
    description = "Extract text from a web page URL."

    async def execute(self, context: AgentContext, url: str) -> str:
        try:
            resp = requests.get(url, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")
            text = soup.get_text(" ", strip=True)
            return text[:1000] + ("..." if len(text) > 1000 else "")
        except Exception as e:
            return f"Error extracting data: {e}"

# --- Main Agent ---
class ConsoleAIAgent(Agent):
    def __init__(self, model="gpt-3.5-turbo"):
        super().__init__(model=model)
        self.add_tool(WebSearchTool())
        self.add_tool(DataExtractionTool())

    async def interact(self):
        print("Welcome to the AI Agent Console! Type 'exit' to quit.")
        while True:
            user = input("You: ").strip()
            if user.lower() == "exit":
                print("Goodbye!")
                break
            response = await self.run(user)
            print(f"Agent: {response}")

        # --- Evaluation API ---
    def evaluate_agent_input(input_text):
        """
        Run the agent on a single input and return response text and conversation history.
        """
        agent = ConsoleAIAgent()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(agent.run(input_text))
        # If agent.run returns only text, wrap in dict; if it returns more, extract messages
        result = {
            "text": response if isinstance(response, str) else getattr(response, "text", str(response)),
            "messages": getattr(response, "messages", None)
        }
        return result

if __name__ == "__main__":
    agent = ConsoleAIAgent()
    asyncio.run(agent.interact())
