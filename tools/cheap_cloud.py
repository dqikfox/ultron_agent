"""
Cheap Cloud Integration - $8/month cloud stack
Groq (AI) + Railway (hosting) + Backblaze B2 (storage)
"""
import os
import json
import time
from typing import Dict, Any

class CheapCloud:
    """$8/month cloud integration"""
    
    def __init__(self):
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.b2_key_id = os.getenv("B2_KEY_ID")
        self.b2_app_key = os.getenv("B2_APP_KEY")
        
        self.groq_client = None
        self.b2_api = None
        
        self._init_groq()
        self._init_b2()
    
    def _init_groq(self):
        """Initialize Groq API"""
        if not self.groq_key:
            return
        try:
            from groq import Groq
            self.groq_client = Groq(api_key=self.groq_key)
        except ImportError:
            pass
    
    def _init_b2(self):
        """Initialize Backblaze B2"""
        if not self.b2_key_id or not self.b2_app_key:
            return
        try:
            from b2sdk.v2 import B2Api, InMemoryAccountInfo
            info = InMemoryAccountInfo()
            self.b2_api = B2Api(info)
            self.b2_api.authorize_account("production", self.b2_key_id, self.b2_app_key)
        except ImportError:
            pass
    
    async def chat(self, prompt: str, model: str = "mixtral-8x7b-32768") -> str:
        """Ultra-fast AI chat via Groq"""
        if not self.groq_client:
            return "Groq not configured"
        
        response = self.groq_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=4096
        )
        return response.choices[0].message.content
    
    async def save_to_b2(self, data: dict, filename: str = None):
        """Save data to Backblaze B2"""
        if not self.b2_api:
            return False
        
        filename = filename or f"memory/{time.time()}.json"
        bucket = self.b2_api.get_bucket_by_name("ultron-memory")
        bucket.upload_bytes(json.dumps(data).encode(), filename)
        return True
    
    async def load_from_b2(self, filename: str) -> dict:
        """Load data from Backblaze B2"""
        if not self.b2_api:
            return {}
        
        bucket = self.b2_api.get_bucket_by_name("ultron-memory")
        downloaded = bucket.download_file_by_name(filename)
        return json.loads(downloaded.read())
    
    def get_status(self) -> Dict[str, bool]:
        """Check service availability"""
        return {
            'groq': self.groq_client is not None,
            'b2': self.b2_api is not None
        }
