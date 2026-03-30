"""Command history tracking for ULTRON Agent"""
import time
import json
from pathlib import Path
from collections import deque

class CommandHistory:
    def __init__(self, max_size=50, persist_file='logs/command_history.json'):
        self.history = deque(maxlen=max_size)
        self.persist_file = Path(persist_file)
        self.load()
    
    def add(self, command, result, success=True):
        """Add command to history"""
        command_entry = {
            'command': command,
            'result': result,
            'success': success,
            'timestamp': time.time()
        }
        self.history.append(command_entry)
        self.save()
    
    def get_last(self, count=10):
        """Get last count commands"""
        return list(self.history)[-count:]
    
    def save(self):
        """Persist history to disk"""
        try:
            with open(self.persist_file, 'w') as f:
                json.dump(list(self.history), f, indent=2)
        except Exception:
            pass
    
    def load(self):
        """Load history from disk"""
        try:
            if self.persist_file.exists():
                with open(self.persist_file) as f:
                    self.history = deque(json.load(f), maxlen=self.history.maxlen)
        except Exception:
            pass
