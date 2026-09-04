"""
AutoGen Automation Tool - Multi-agent workflows
"""
import os

class AutoGenAutomationTool:
    name = "AutoGen Automation"
    description = "Multi-agent automation with AutoGen"
    
    def __init__(self, config=None, memory=None):
        self.config = config
        self.memory = memory
    
    def match(self, command: str) -> bool:
        keywords = ['autogen', 'multi agent', 'agent team', 'collaborate']
        return any(k in command.lower() for k in keywords)
    
    def execute(self, command: str) -> str:
        try:
            import autogen
        except ImportError:
            return "AutoGen not installed: pip install pyautogen"
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "OPENAI_API_KEY not set"
        
        # Extract task
        task = self._extract_task(command)
        if not task:
            return "Please specify a task"
        
        try:
            result = self._run_autogen(task, api_key)
            return f"AutoGen completed: {result}"
        except Exception as e:
            return f"AutoGen failed: {str(e)}"
    
    def _extract_task(self, command: str) -> str:
        """Extract task from command"""
        triggers = ['autogen', 'multi agent', 'agent team']
        for trigger in triggers:
            if trigger in command.lower():
                return command.lower().split(trigger, 1)[1].strip()
        return command
    
    def _run_autogen(self, task: str, api_key: str) -> str:
        """Run AutoGen workflow"""
        import autogen
        
        config_list = [{"model": "gpt-4", "api_key": api_key}]
        
        # Create assistant
        assistant = autogen.AssistantAgent(
            name="assistant",
            llm_config={"config_list": config_list, "timeout": 120}
        )
        
        # Create executor
        executor = autogen.UserProxyAgent(
            name="executor",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=3,
            code_execution_config={"work_dir": "autogen_work", "use_docker": False}
        )
        
        # Run task
        executor.initiate_chat(assistant, message=task)
        
        # Get last message
        messages = executor.chat_messages[assistant]
        if messages:
            return messages[-1].get("content", "Task completed")
        
        return "Task completed"
    
    @classmethod
    def schema(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "task": {"type": "string", "description": "Task for agents"}
            }
        }
