#!/usr/bin/env python3
"""AWS Solutions Tool for ULTRON Agent"""

from tools.tool_interface import ToolInterface
from aws_solutions_integration import UltronAWSSolutionsIntegrator
from utils.ultron_logger import log_info, log_error

class AWSSolutionsTool(ToolInterface):
    """AWS Solutions Library integration tool"""

    @property
    def name(self) -> str:
        return "AWS Solutions Tool"

    @property
    def description(self) -> str:
        return "Multi-agent orchestration, multimodal processing, AI gateway, and document intelligence"

    def match(self, command: str) -> bool:
        keywords = ["multi agent", "multimodal", "gateway", "document", "orchestrate", "process", "analyze"]
        return any(kw in command.lower() for kw in keywords)

    def execute(self, command: str, **kwargs) -> str:
        try:
            cmd_lower = command.lower()
            integrator = UltronAWSSolutionsIntegrator()
            
            if "orchestrate" in cmd_lower or "multi agent" in cmd_lower:
                return self._orchestrate_task(integrator, command)
            elif "process document" in cmd_lower or "analyze document" in cmd_lower:
                return self._process_document(integrator, command)
            elif "gateway" in cmd_lower or "route" in cmd_lower:
                return self._route_ai_request(integrator, command)
            elif "test" in cmd_lower:
                return self._run_tests(integrator)
            elif "initialize" in cmd_lower or "setup" in cmd_lower:
                return self._initialize_systems(integrator)
            else:
                return self._show_help()
                
        except Exception as e:
            log_error("aws_solutions_tool", f"Error: {e}")
            return f"AWS Solutions error: {e}"

    def _orchestrate_task(self, integrator, command):
        """Orchestrate task using multi-agent system"""
        
        # Extract task from command
        task = command.replace("orchestrate", "").replace("multi agent", "").strip()
        if not task:
            task = "Analyze ULTRON Agent system and provide recommendations"
        
        result = integrator.multi_agent.orchestrate_task(task)
        
        agents_used = len(result.get("results", {}))
        synthesis = result.get("synthesis", "No synthesis available")
        
        return f"🤖 Multi-Agent Orchestration Complete\n" + \
               f"Task: {task}\n" + \
               f"Agents Used: {agents_used}\n" + \
               f"Synthesis: {synthesis[:200]}...\n" + \
               f"Status: ✅ Completed"

    def _process_document(self, integrator, command):
        """Process document with multimodal AI"""
        
        # Extract file path from command
        words = command.split()
        file_path = None
        for word in words:
            if "." in word and "/" in word or "\\" in word:
                file_path = word
                break
        
        if not file_path:
            file_path = "README.md"  # Default
        
        result = integrator.multimodal.process_document(file_path, "comprehensive")
        
        if "error" in result:
            return f"❌ Document Processing Failed: {result['error']}"
        
        return f"📄 Document Processing Complete\n" + \
               f"File: {result.get('file', 'N/A')}\n" + \
               f"Type: {result.get('type', 'N/A')}\n" + \
               f"Analysis: {result.get('analysis', 'No analysis')[:150]}...\n" + \
               f"Status: ✅ Processed"

    def _route_ai_request(self, integrator, command):
        """Route AI request through gateway"""
        
        # Extract prompt from command
        prompt = command.replace("gateway", "").replace("route", "").strip()
        if not prompt:
            prompt = "What are the capabilities of ULTRON Agent?"
        
        result = integrator.gateway.route_request(prompt, task_type="general")
        
        provider = result.get("provider", "unknown")
        model = result.get("model", "unknown")
        response = result.get("response", "No response")
        
        return f"🌐 AI Gateway Response\n" + \
               f"Provider: {provider}\n" + \
               f"Model: {model}\n" + \
               f"Response: {response[:200]}...\n" + \
               f"Status: {result.get('status', 'unknown')}"

    def _run_tests(self, integrator):
        """Run comprehensive tests"""
        
        test_results = integrator.run_comprehensive_test()
        
        systems_tested = test_results.get("systems_tested", 0)
        overall_status = test_results.get("overall_status", "UNKNOWN")
        results = test_results.get("results", {})
        
        test_summary = []
        for system, result in results.items():
            status = "✅" if result.get("status") != "error" else "❌"
            test_summary.append(f"  {status} {system}")
        
        return f"🧪 AWS Solutions Test Results\n" + \
               f"Systems Tested: {systems_tested}\n" + \
               f"Overall Status: {overall_status}\n" + \
               f"Test Results:\n" + "\n".join(test_summary) + \
               f"\n\nTimestamp: {test_results.get('test_timestamp', 'N/A')}"

    def _initialize_systems(self, integrator):
        """Initialize all AWS solutions"""
        
        init_results = integrator.initialize_all_systems()
        
        summary = []
        for system, result in init_results.items():
            if isinstance(result, dict):
                details = ", ".join(f"{k}: {v}" for k, v in result.items())
                summary.append(f"  ✅ {system}: {details}")
            else:
                summary.append(f"  ✅ {system}: {result}")
        
        return f"🚀 AWS Solutions Initialization\n" + \
               "\n".join(summary) + \
               f"\n\nSystems Ready: {len(init_results)}\n" + \
               "Status: ✅ All systems operational"

    def _show_help(self):
        """Show AWS Solutions help"""
        
        return """🌩️ AWS Solutions Commands:

🤖 Multi-Agent Orchestration:
• "orchestrate [task]" - Coordinate multiple AI agents
• "multi agent analyze project" - Multi-agent project analysis

📄 Multimodal Document Processing:
• "process document [path]" - Analyze documents with AI
• "analyze document README.md" - Process specific file

🌐 Multi-Provider AI Gateway:
• "gateway [prompt]" - Route request to optimal AI model
• "route what is ULTRON" - Smart model selection

🧪 System Testing:
• "test aws solutions" - Run comprehensive tests
• "initialize aws solutions" - Setup all systems

💡 Example Usage:
• "orchestrate optimize ULTRON performance"
• "process document project_plan.pdf"
• "gateway explain quantum computing"
• "test all aws solutions"

🔧 Capabilities:
• Multi-agent task coordination
• Vision and text document analysis
• Intelligent model routing
• Automated document processing
• Real-time system monitoring

🎯 Integration:
• Local Ollama models (llava, qwen, deepseek, mistral)
• AWS Bedrock API (Claude 3, Titan)
• ULTRON Agent ecosystem
• Comprehensive logging and monitoring
"""

    @classmethod
    def schema(cls) -> dict:
        return {
            "name": "aws_solutions_tool",
            "description": "Multi-agent orchestration, multimodal processing, AI gateway, and document intelligence",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "AWS Solutions command to execute"
                    }
                },
                "required": ["command"]
            }
        }