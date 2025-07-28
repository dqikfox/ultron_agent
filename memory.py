import json
import logging
import os
import uuid
from collections import deque

class Memory:
    def __init__(self, short_term_limit=10, long_term_file='long_term_memory.json'):
        self.short_term_memory = deque(maxlen=short_term_limit)
        self.long_term_memory = self.load_long_term_memory(long_term_file)
        logging.info("Memory initialized with shortterm and longterm storage. - memory.py:11")

    def load_long_term_memory(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return {}

    def save_long_term_memory(self, file_path):
        with open(file_path, 'w') as f:
            json.dump(self.long_term_memory, f)

    def add_to_short_term(self, item):
        self.short_term_memory.append(item)
        logging.info(f"Added to shortterm memory: {item} - memory.py:25")

    def add_to_long_term(self, item):
        item_id = str(uuid.uuid4())
        self.long_term_memory[item_id] = item
        logging.info(f"Added to longterm memory: {item_id} > {item} - memory.py:30")

    def retrieve_short_term(self):
        return list(self.short_term_memory)

    def retrieve_long_term(self):
        return self.long_term_memory

    def clear_short_term(self):
        self.short_term_memory.clear()
        logging.info("Cleared shortterm memory. - memory.py:40")

    def clear_long_term(self):
        self.long_term_memory.clear()
        logging.info("Cleared longterm memory. - memory.py:44")