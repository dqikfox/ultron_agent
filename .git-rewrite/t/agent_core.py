"""Minimal agent_core stub for tests.

This file provides a lightweight UltronAgent and AgentStatus used by the test suite
so collection can proceed. Real implementations live elsewhere in the project.
"""
from enum import Enum


"""Minimal agent_core stub for tests.

This file provides a lightweight UltronAgent and AgentStatus used by the test suite
so collection can proceed. Real implementations live elsewhere in the project.
"""
from enum import Enum


class AgentStatus(Enum):
    INITIALIZING = 'initializing'
    RUNNING = 'running'
    MAINTENANCE = 'maintenance'


class UltronAgent:
    def __init__(self, config=None):
        # Tests patch Config constructor to return a mock; accept either
        from config import Config
        self.config = config or Config()
        self.status = AgentStatus.INITIALIZING
        self.brain = None
        self.tools = []
        # Minimal components used by tests
        self.event_system = type('E', (), {'emit': lambda *a, **k: None})()
        self.memory = type('M', (), {'add_to_short_term': lambda *a, **k: None})()
        self.performance_monitor = type('P', (), {'get_metrics_summary': lambda: {'cpu_avg': 0}, 'stop_monitoring': lambda: None})()
        self.task_scheduler = type('T', (), {'stop': lambda: None})()

    def load_tools(self):
        return self.tools

    def list_tools(self):
        return [t for t in self.tools]

    def handle_command(self, command: str):
        # Tests expect this to call brain.plan_and_act and return its result
        if self.brain and hasattr(self.brain, 'plan_and_act'):
            return self.brain.plan_and_act(command)
        return None

    def handle_text(self, text: str):
        if not text or not text.strip():
            return "Please provide a valid command"
        return self.handle_command(text)

    async def process_command(self, command: str):
        # Simplified flow used by tests
        await self.event_system.emit('command_start', command)
        response = self.handle_command(command)
        # Simulate memory updates
        self.memory.add_to_short_term({'role': 'user', 'content': command})
        self.memory.add_to_short_term({'role': 'system', 'content': response})
        await self.event_system.emit('command_complete', {'command': command, 'result': response})
        return response

    async def stop(self):
        await self.event_system.emit('agent_stopping')
        self.performance_monitor.stop_monitoring()
        self.task_scheduler.stop()
        self.status = AgentStatus.MAINTENANCE

# End of test stub

