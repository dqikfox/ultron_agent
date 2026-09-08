from .base import Tool
import logging
import requests

class WebSearchTool(Tool):
    def __init__(self):
        self.name = "WebSearchTool"
        self.description = "Perform web searches using DuckDuckGo."
        super().__init__()

    def match(self, command: str) -> bool:
        cmd = command.lower()
        return "search" in cmd or "find" in cmd

    def execute(self, command: str) -> str:
        query = command.replace("search", "").replace("find", "").strip()
        if not query:
            return "No search query provided."
        try:
            response = requests.get(f"https://api.duckduckgo.com/?q={query}&format=json")
            response.raise_for_status()
            data = response.json()
            results = data.get("RelatedTopics", [])
            if results:
                return "\n".join([result.get("Text", "No description available.") for result in results])
            return "No results found."
        except Exception as e:
            logging.error(f"Web search error: {e}")
            return f"Error: {e}"