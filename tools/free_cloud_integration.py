"""
Free Cloud Integration - Zero-cost cloud services
"""
import os
import requests
from typing import Dict, Any, Optional

class FreeCloudIntegration:
    """Integrates free cloud services"""
    
    def __init__(self):
        self.hf_token = os.getenv("HF_TOKEN", "")
        self.supabase_url = os.getenv("SUPABASE_URL", "")
        self.supabase_key = os.getenv("SUPABASE_KEY", "")
    
    async def chat_huggingface(self, prompt: str, model: str = "mistralai/Mistral-7B-Instruct-v0.2") -> str:
        """Free AI chat via Hugging Face"""
        url = f"https://api-inference.huggingface.co/models/{model}"
        headers = {"Authorization": f"Bearer {self.hf_token}"}
        
        response = requests.post(url, headers=headers, json={"inputs": prompt})
        
        if response.status_code == 200:
            return response.json()[0]['generated_text']
        return f"Error: {response.status_code}"
    
    async def save_to_supabase(self, table: str, data: dict) -> bool:
        """Save data to Supabase (FREE tier)"""
        if not self.supabase_url or not self.supabase_key:
            return False
        
        url = f"{self.supabase_url}/rest/v1/{table}"
        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, headers=headers, json=data)
        return response.status_code == 201
    
    async def get_from_supabase(self, table: str, limit: int = 10) -> list:
        """Get data from Supabase"""
        if not self.supabase_url or not self.supabase_key:
            return []
        
        url = f"{self.supabase_url}/rest/v1/{table}?limit={limit}"
        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}"
        }
        
        response = requests.get(url, headers=headers)
        return response.json() if response.status_code == 200 else []
