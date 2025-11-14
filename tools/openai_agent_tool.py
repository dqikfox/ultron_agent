#!/usr/bin/env python3
"""OpenAI Agent Tool for ULTRON"""

from tools.tool_interface import ToolInterface
from openai_integration import UltronOpenAIIntegrator
from utils.ultron_logger import log_info, log_error

class OpenAIAgentTool(ToolInterface):
    """OpenAI Assistants and Agents integration"""

    @property
    def name(self) -> str:
        return "OpenAI Agent Tool"

    @property
    def description(self) -> str:
        return "OpenAI Assistants API, Agent workflows, and web search integration"

    def match(self, command: str) -> bool:
        keywords = ["openai", "assistant", "gpt", "workflow", "web search", "analyze"]
        return any(kw in command.lower() for kw in keywords)

    def execute(self, command: str, **kwargs) -> str:
        try:
            cmd_lower = command.lower()
            integrator = UltronOpenAIIntegrator()
            
            if "create assistant" in cmd_lower:
                return self._create_assistant(integrator)
            elif "workflow" in cmd_lower or "analyze" in cmd_lower:
                return self._run_workflow(integrator, command)
            elif "web search" in cmd_lower:
                return self._web_search(integrator, command)
            elif "initialize" in cmd_lower:
                return self._initialize_openai(integrator)
            else:
                return self._show_help()
                
        except Exception as e:
            log_error("openai_agent_tool", f"Error: {e}")
            return f"OpenAI Agent error: {e}"

    def _create_assistant(self, integrator):
        """Create OpenAI Assistant"""
        
        result = integrator.assistant.create_ultron_assistant()
        
        if result["status"] == "created":
            return f"🤖 OpenAI Assistant Created\n" + \
                   f"Assistant ID: {result['assistant_id']}\n" + \
                   f"Model: gpt-4o\n" + \
                   f"Tools: Code interpreter, File search, Functions\n" + \
                   f"Status: ✅ Ready for ULTRON operations"
        else:
            return f"❌ Assistant Creation Failed: {result.get('message', 'Unknown error')}"

    def _run_workflow(self, integrator, command):
        """Run OpenAI Agent workflow"""
        
        # Extract request from command
        request = command.replace("workflow", "").replace("analyze", "").strip()
        if not request:
            request = "Analyze and optimize ULTRON Agent system"
        
        result = integrator.process_ultron_request(request)
        
        triage = result.get("triage", {})
        analysis = result.get("analysis", {})
        
        return f"🔄 OpenAI Workflow Complete\n" + \
               f"Request: {request}\n" + \
               f"Triage: {triage.get('project_goal', 'N/A')}\n" + \
               f"Analysis: {len(analysis.get('recommendations', []))} recommendations\n" + \
               f"Status: ✅ Workflow executed successfully"

    def _web_search(self, integrator, command):
        """Perform web search"""
        
        query = command.replace("web search", "").strip()
        if not query:
            query = "ULTRON Agent AI development"
        
        result = integrator.web_search.search_for_ultron(query)
        
        results_count = len(result.get("results", []))
        
        return f"🔍 Web Search Results\n" + \
               f"Query: {query}\n" + \
               f"Results: {results_count} found\n" + \
               f"Context: {result.get('context', 'N/A')}\n" + \
               f"Status: ✅ Search completed"

    def _initialize_openai(self, integrator):
        """Initialize OpenAI integration"""
        
        results = integrator.initialize_openai_integration()
        
        assistant_status = results["assistant"]["status"]
        agents_created = results["workflow"]["agents_created"]
        
        return f"🚀 OpenAI Integration Initialized\n" + \
               f"Assistant: {assistant_status}\n" + \
               f"Workflow Agents: {agents_created} created\n" + \
               f"Web Search: Ready\n" + \
               f"Status: ✅ Full OpenAI integration active"

    def _show_help(self):
        """Show OpenAI Agent help"""
        
        return """🤖 OpenAI Agent Commands:

🎯 Assistant Management:
• "create openai assistant" - Create ULTRON OpenAI Assistant
• "initialize openai" - Setup complete OpenAI integration

🔄 Agent Workflows:
• "workflow [request]" - Run OpenAI agent workflow
• "analyze [topic]" - Analyze with OpenAI agents

🔍 Web Search:
• "web search [query]" - Search with OpenAI web search
• "search for [topic]" - Find relevant information

💡 Example Usage:
• "create openai assistant"
• "workflow optimize ULTRON performance"
• "analyze project architecture"
• "web search AI agent best practices"

🛠️ Features:
• GPT-4o model integration
• Multi-agent workflows (Triage, Analyzer, Implementer)
• Code interpreter and file search
• Web search with context
• Function calling capabilities

🔧 Integration:
• ULTRON Agent ecosystem
• Voice command support
• Centralized logging
• Real-time processing
"""

    @classmethod
    def schema(cls) -> dict:
        return {
            "name": "openai_agent_tool",
            "description": "OpenAI Assistants API, Agent workflows, and web search integration",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "OpenAI Agent command to execute"
                    }
                },
                "required": ["command"]
            }
        }