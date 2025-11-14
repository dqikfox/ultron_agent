"""Enhanced Memory Tool - Memory with importance scoring and temporal decay"""
from utils.ultron_logger import log_info, log_error
import time
import json
from pathlib import Path

class EnhancedMemoryTool:
    name = "enhanced_memory_tool"
    description = "Memory system with importance scoring and temporal decay"
    
    def __init__(self):
        self.memory = {}
        self.decay_rate = 0.95
        self.memory_file = Path("memory/enhanced_memory.json")
        self.memory_file.parent.mkdir(exist_ok=True)
        self._load_memory()

    def match(self, input_string):
        # Simple match based on keyword 'remember', 'recall', or 'memory'
        if input_string.lower() in ['remember', 'recall', 'memory']:
            return True
        return False

    def execute(self, user_input):
        try:
            action = user_input.split(' ')[0].lower()
            parameters = ' '.join(user_input.split()[1:])

            if action == 'remember':
                self._store_memory(parameters)
            elif action == 'recall':
                result = self._retrieve_memory(parameters)
                return f"Result: {result}"
            elif action == 'memory':
                self._list_all_memories()
            else:
                raise ValueError("Invalid action. Please use 'remember', 'recall', or 'memory'.")
        except Exception as e:
            log_error("enhanced_memory_tool", f"Error: {e}")
            return f"Error: {e}"

    def _calculate_importance(self, parameters):
        """Calculate importance score based on frequency and recency"""
        frequency = len(parameters.split())
        recency = 1.0
        return min(1.0, (frequency * 0.1 + recency * 0.9))

    def _apply_decay(self):
        """Reduce importance over time"""
        current_time = time.time()
        for key in list(self.memory.keys()):
            age = current_time - self.memory[key].get('timestamp', current_time)
            decay = self.decay_rate ** (age / 86400)  # Daily decay
            self.memory[key]['importance'] *= decay

    def schema(self):
        # Return tool metadata
        return {
            'name': 'EnhancedMemoryTool',
            'description': 'An enhanced memory tool with scoring, decay, pattern recognition, and retrieval capabilities.',
            'usage': {
                'remember': 'Remember something by mentioning it in a sentence like "I remember the event".',
                'recall': 'Retrieve something previously remembered by specifying its parameters.',
                'memory': 'List all memories stored.'
            }
        }

    def _store_memory(self, parameters):
        """Store memory with importance score"""
        importance = self._calculate_importance(parameters)
        key = str(len(self.memory) + 1)
        self.memory[key] = {
            'content': parameters,
            'importance': importance,
            'timestamp': time.time()
        }
        self._save_memory()
        log_info("enhanced_memory_tool", f"Stored: {parameters[:50]}...")

    def _retrieve_memory(self, parameters):
        """Retrieve memory with decay applied"""
        self._apply_decay()
        results = []
        for key, mem in self.memory.items():
            if parameters.lower() in mem['content'].lower():
                results.append((mem['content'], mem['importance']))
        results.sort(key=lambda x: x[1], reverse=True)
        return results[0][0] if results else "No matching memory found"

    def _list_all_memories(self):
        """List all memories sorted by importance"""
        self._apply_decay()
        sorted_mem = sorted(self.memory.items(), 
                          key=lambda x: x[1]['importance'], 
                          reverse=True)
        return "\n".join([f"{k}: {v['content']} (importance: {v['importance']:.2f})" 
                         for k, v in sorted_mem[:10]])
    
    def _load_memory(self):
        """Load memory from file"""
        if self.memory_file.exists():
            with open(self.memory_file, 'r') as f:
                self.memory = json.load(f)
    
    def _save_memory(self):
        """Save memory to file"""
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)