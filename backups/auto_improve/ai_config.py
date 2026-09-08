#!/usr/bin/env python3
"""
AI Configuration for Ultron Agent
Configures OpenAI API and GPT-5 integration
"""

import os
from typing import Dict, Any
from ai_toolkit import AIConfig, ai_toolkit, initialize_ai_toolkit

def load_ai_config() -> AIConfig:
    """Load AI configuration from environment and config files"""
    config = AIConfig()
    
    # Load from environment variables
    config.api_key = os.getenv("OPENAI_API_KEY", "")
    config.organization = os.getenv("OPENAI_ORGANIZATION", "")
    config.project = os.getenv("OPENAI_PROJECT", "")
    
    # Model preferences (GPT-5 first)
    config.preferred_models = [
        "gpt-5-turbo",
        "gpt-5",
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-4"
    ]
    
    return config

async def setup_ai_toolkit() -> Dict[str, Any]:
    """Setup and test AI toolkit"""
    config = load_ai_config()
    
    if not config.api_key:
        return {
            "status": "error",
            "message": "No OpenAI API key found. Set OPENAI_API_KEY environment variable."
        }
    
    # Initialize with config
    ai_toolkit.config = config
    ai_toolkit._initialize_client()
    
    # Test connection and get models
    result = await ai_toolkit.test_connection()
    
    if result["status"] == "success":
        models = await ai_toolkit.get_available_models()
        result["available_models"] = len(models)
        
        if ai_toolkit.is_gpt5_available():
            result["message"] = f"🚀 GPT-5 is available! Using: {ai_toolkit.config.model}"
        else:
            result["message"] = f"Using: {ai_toolkit.config.model} (GPT-5 not yet available)"
    
    return result

if __name__ == "__main__":
    import asyncio
    
    async def test():
        result = await setup_ai_toolkit()
        print(f"AI Setup Result: {result}")
    
    asyncio.run(test())