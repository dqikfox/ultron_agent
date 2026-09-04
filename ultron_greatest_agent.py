"""
ULTRON Greatest Agent Console App
- Multi-modal, multi-tool, event-driven, extensible
- Features: LLM chat, web search, code execution, file ops, data extraction, system info, translation, summarization, vision, voice (extensible)
"""
import asyncio
import requests
from bs4 import BeautifulSoup
import os
import platform
import subprocess
from agentframework import Agent, Tool, AgentContext

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

# --- Tool: Code Execution ---
class CodeExecutionTool(Tool):
    name = "run_code"
    description = "Run Python code and return output."
    async def execute(self, context: AgentContext, code: str) -> str:
        try:
            exec_globals = {}
            exec(code, exec_globals)
            return str(exec_globals.get('result', 'Code executed.'))
        except Exception as e:
            return f"Error: {e}"

# --- Tool: File Operations ---
class FileOpsTool(Tool):
    name = "file_ops"
    description = "Read or write files. Usage: file_ops <read/write> <path> [content]"
    async def execute(self, context: AgentContext, op: str, path: str, content: str = None) -> str:
        try:
            if op == "read":
                with open(path, "r") as f:
                    return f.read()[:1000]
            elif op == "write" and content:
                with open(path, "w") as f:
                    f.write(content)
                return "File written."
            else:
                return "Invalid operation."
        except Exception as e:
            return f"Error: {e}"

# --- Tool: System Info ---
class SystemInfoTool(Tool):
    name = "system_info"
    description = "Get system information."
    async def execute(self, context: AgentContext) -> str:
        info = {
            "os": platform.system(),
            "release": platform.release(),
            "cpu": platform.processor(),
            "cwd": os.getcwd()
        }
        return str(info)

# --- Tool: Summarization ---
class SummarizeTool(Tool):
    name = "summarize"
    description = "Summarize text."
    async def execute(self, context: AgentContext, text: str) -> str:
        # Placeholder: Use LLM for real summarization
        return text[:200] + ("..." if len(text) > 200 else "")

# --- Tool: Translation ---
class TranslateTool(Tool):
    name = "translate"
    description = "Translate text to another language. Usage: translate <text> <lang>"
    async def execute(self, context: AgentContext, text: str, lang: str) -> str:
        # Placeholder: Use LLM or API for real translation
        return f"[Translated to {lang}]: {text}"

# --- Main Agent ---
class UltronGreatestAgent(Agent):
    def __init__(self, model="gpt-3.5-turbo"):
        super().__init__(model=model)
        self.add_tool(WebSearchTool())
        self.add_tool(CodeExecutionTool())
        self.add_tool(FileOpsTool())
        self.add_tool(SystemInfoTool())
        self.add_tool(SummarizeTool())
        self.add_tool(TranslateTool())
        # Add more tools as needed (vision, voice, etc.)

    async def interact(self):
        print("Welcome to the ULTRON Greatest Agent! Type 'exit' to quit.")
        while True:
            user = input("You: ").strip()
            if user.lower() == "exit":
                print("Goodbye!")
                break
            response = await self.run(user)
            print(f"Agent: {response}")

if __name__ == "__main__":
    agent = UltronGreatestAgent()
    asyncio.run(agent.interact())
