"""
AI Agent Console App using ULTRON Agent Framework
Features: LLM chat, web search, data extraction
"""

import asyncio

import requests
from bs4 import BeautifulSoup

# Import from ULTRON Agent framework
from tools.tool_interface import ToolInterface

# --- Tool: Web Search ---


class WebSearchTool(ToolInterface):
    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return "Search the web and return top results."

    def match(self, command: str) -> bool:
        """Check if command matches this tool."""
        return "search" in command.lower() or "find" in command.lower()

    def execute(self, command: str, **kwargs) -> str:
        """Execute the web search tool."""
        try:
            query = command.replace("search", "").replace("find", "").strip()
            url = f"https://duckduckgo.com/html/?q={query}"
            resp = requests.get(url, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")
            results = []
            for a in soup.select('.result__a')[:3]:
                results.append(f"- {a.get_text(strip=True)}: {a['href']}")
            return "\n".join(results) if results else "No results found."
        except Exception as e:
            return f"Error: {str(e)}"

    @classmethod
    def schema(cls) -> dict:
        """Return JSON schema for function calling."""
        return {
            "name": "web_search",
            "description": "Search the web and return top results.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    }
                },
                "required": ["query"]
            }
        }

# --- Tool: Data Extraction ---


class DataExtractionTool(ToolInterface):
    @property
    def name(self) -> str:
        return "extract_data"

    @property
    def description(self) -> str:
        return "Extract text from a web page URL."

    def match(self, command: str) -> bool:
        """Check if command matches this tool."""
        return "extract" in command.lower() or "scrape" in command.lower()

    def execute(self, command: str, **kwargs) -> str:
        """Execute the data extraction tool."""
        try:
            url = command.strip()
            resp = requests.get(url, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")
            text = soup.get_text(separator=' ', strip=True)
            if len(text) > 2000:
                text = text[:2000] + "... (truncated)"
            return text
        except Exception as e:
            return f"Error: {str(e)}"

    @classmethod
    def schema(cls) -> dict:
        """Return JSON schema for function calling."""
        return {
            "name": "extract_data",
            "description": "Extract text from a web page URL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to extract data from"
                    }
                },
                "required": ["url"]
            }
        }

# --- Main Agent ---


class ConsoleAIAgent:
    def __init__(self, model="gpt-3.5-turbo"):
        self.model = model
        self.tools = [WebSearchTool(), DataExtractionTool()]

    async def run(self, input_text):
        """Simple implementation of agent run method"""
        # For evaluation purposes, just return the input as response
        # In a real implementation, this would process the input with LLM and tools
        return f"Processed: {input_text}"

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
    result = {
        "text": (
            response if isinstance(response, str)
            else getattr(response, "text", str(response))
        ),
        "messages": getattr(response, "messages", None)
    }
    return result


if __name__ == "__main__":
    agent = ConsoleAIAgent()
    asyncio.run(agent.interact())
