"""
Test file for Amazon Q Developer integration testing.
This file contains intentional issues for Q Developer to identify.
"""

import os
import json
import requests
from typing import Dict, List, Optional

# Security issue: hardcoded API key
API_KEY = "sk-1234567890abcdef"

class DataProcessor:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.data = []
    
    # Performance issue: inefficient data processing
    def process_data(self, items):
        result = []
        for item in items:
            for i in range(len(items)):  # O(n²) complexity
                if items[i]['id'] == item['id']:
                    result.append(item)
        return result
    
    # Security issue: SQL injection vulnerability
    def query_database(self, user_input):
        query = f"SELECT * FROM users WHERE name = '{user_input}'"
        # This would execute the query unsafely
        return query
    
    # Code quality issue: missing error handling
    def fetch_data(self, url):
        response = requests.get(url)
        return response.json()
    
    # Type safety issue: inconsistent return types
    def get_user_data(self, user_id):
        if user_id > 0:
            return {"id": user_id, "name": "User"}
        else:
            return None
    
    # Memory leak potential: unclosed file
    def read_config(self, filename):
        file = open(filename, 'r')
        data = json.load(file)
        return data

# Function with multiple issues
def process_user_request(request_data):
    # Missing input validation
    user_id = request_data['user_id']
    
    # Hardcoded credentials
    db_password = "admin123"
    
    # Inefficient string concatenation
    message = ""
    for i in range(100):
        message += f"Processing step {i}\n"
    
    # Potential division by zero
    result = 100 / (user_id - user_id)
    
    return {"status": "success", "result": result}

if __name__ == "__main__":
    # Test the problematic code
    processor = DataProcessor(API_KEY)
    
    # This will cause issues
    test_data = [{"id": 1}, {"id": 2}, {"id": 1}]
    processed = processor.process_data(test_data)
    
    # Unsafe user input
    user_input = "'; DROP TABLE users; --"
    query = processor.query_database(user_input)
    
    print("Test completed")