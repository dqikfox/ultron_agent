"""OpenAI Assistant Tool with ULTRON Agent Knowledge"""

import os
import json
from openai import OpenAI
from utils.ultron_logger import log_info, log_error, log_ai_decision
from tools.base import Tool


class OpenAIAssistantTool(Tool):
    name = "openai_assistant"
    description = "OpenAI Assistant with full ULTRON Agent knowledge and tool access"
    
    def __init__(self):
        self.client = None
        self.assistant_id = "asst_DjelX5T0D1tZb22CKmXv2tq6"
        self.ultron_context = self._build_ultron_context()
        self._init_client()
    
    def _build_ultron_context(self):
        """Build comprehensive ULTRON Agent context"""
        return f"""
You are integrated with ULTRON Agent 3.0 - Advanced AI Agent Platform.

SYSTEM OVERVIEW:
- Multi-modal AI platform with voice, vision, GUI, CLI, API access
- 80+ tools available for system control, web access, cloud services
- Event-driven architecture with real-time monitoring
- Supports multiple AI models: Ollama (llava:7b), OpenAI, Anthropic, AWS Bedrock

AVAILABLE TOOLS:
{self._get_tool_list()}

CONFIGURATION:
- Voice: ElevenLabs TTS/STT with wake word "hey ultron"
- Vision: OCR, screenshot analysis, multimodal processing
- GUI: Pokédex-style interface on port 8080
- API: REST endpoints on port 5000
- Memory: Persistent conversation storage
- Performance monitoring and health checks enabled

CAPABILITIES:
- System automation (Windows, PyAutoGUI)
- Web browsing and search
- Cloud integration (AWS, Azure, Google)
- Code generation and analysis
- File processing and management
- Real-time communication via WebSocket
- Voice command processing
- Image generation and analysis

When providing code or suggestions, consider ULTRON's architecture and available tools.
"""
    
    def _get_tool_list(self):
        """Get list of available tools"""
        tools = [
            "aws_bedrock_tool", "browser_mcp_tool", "windows_system_tool",
            "web_search_tool", "screenshot_analyzer_tool", "voice_aws_tool",
            "unity_ai_tool", "docker_integration_tool", "github_models_tool",
            "langflow_integration_tool", "memory_context_tool", "pyautogui_tool",
            "stable_diffusion_tool", "tor_search_tool", "vscode_integration_tool"
        ]
        return "\n- ".join([""] + tools)
    
    def _init_client(self):
        """Initialize OpenAI client"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            log_error("openai_assistant", "OpenAI API key not found")
            return
        
        try:
            self.client = OpenAI(api_key=api_key)
            log_info("openai_assistant", "OpenAI client initialized with ULTRON context")
        except Exception as e:
            log_error("openai_assistant", f"Failed to initialize: {e}")
    
    @staticmethod
    def schema():
        return {
            "name": OpenAIAssistantTool.name,
            "description": OpenAIAssistantTool.description,
            "parameters": {
                "task": {"type": "string", "description": "Task with ULTRON context"}
            }
        }
    
    def match(self, command: str) -> bool:
        keywords = ["assistant", "openai", "gpt", "ai help", "code help"]
        return any(keyword in command.lower() for keyword in keywords)
    
    def execute(self, task: str = "", **kwargs) -> str:
        """Execute task with ULTRON context"""
        if not self.client:
            return "OpenAI client not available. Set OPENAI_API_KEY."
        
        if not task:
            task = kwargs.get("command", "")
        
        try:
            log_ai_decision("openai_assistant", f"Executing with ULTRON context: {task}", 
                          ai_model="gpt-4", confidence_score=0.95)
            
            # Create thread with ULTRON context
            thread = self.client.beta.threads.create()
            
            # Add system context + user message
            full_message = f"{self.ultron_context}\n\nUSER REQUEST: {task}"
            
            self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=full_message
            )
            
            # Run assistant
            run = self.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=self.assistant_id
            )
            
            # Wait for completion
            while run.status in ["queued", "in_progress"]:
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
            
            if run.status == "completed":
                messages = self.client.beta.threads.messages.list(thread_id=thread.id)
                response = messages.data[0].content[0].text.value
                
                log_info("openai_assistant", f"ULTRON-aware task completed: {task}")
                return f"🤖 ULTRON Assistant: {response}"
            else:
                log_error("openai_assistant", f"Run failed: {run.status}")
                return f"❌ Task failed: {run.status}"
                
        except Exception as e:
            log_error("openai_assistant", f"Execution failed: {e}")
            return f"❌ Error: {str(e)}"