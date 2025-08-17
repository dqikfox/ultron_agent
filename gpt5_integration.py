#!/usr/bin/env python3
"""
GPT-5 Integration for Ultron Agent
Works with AI Toolkit VS Code extension
"""

import os
import json
import subprocess
from typing import Dict, Any, Optional

def check_ai_toolkit_extension() -> bool:
    """Check if AI Toolkit extension is installed"""
    try:
        result = subprocess.run(
            ["code", "--list-extensions"],
            capture_output=True,
            text=True,
            shell=True
        )
        return "ms-vscode.vscode-ai-toolkit" in result.stdout
    except:
        return False

def configure_gpt5_access() -> Dict[str, Any]:
    """Configure GPT-5 access through AI Toolkit"""
    config = {
        "status": "configured",
        "ai_toolkit_installed": check_ai_toolkit_extension(),
        "openai_key_set": bool(os.getenv("OPENAI_API_KEY")),
        "gpt5_ready": False
    }
    
    if config["ai_toolkit_installed"] and config["openai_key_set"]:
        config["gpt5_ready"] = True
        config["message"] = "GPT-5 ready via AI Toolkit extension"
    else:
        config["message"] = "Install AI Toolkit extension and set OPENAI_API_KEY"
    
    return config

def get_gpt5_status() -> Dict[str, Any]:
    """Get current GPT-5 integration status"""
    return {
        "extension": "AI Toolkit (ms-vscode.vscode-ai-toolkit)",
        "config_file": ".vscode/ai-toolkit.json",
        "settings": ".vscode/settings.json",
        "api_key": "OPENAI_API_KEY environment variable",
        "models": ["gpt-5-turbo", "gpt-5", "gpt-4o"],
        "ready": check_ai_toolkit_extension() and bool(os.getenv("OPENAI_API_KEY"))
    }

if __name__ == "__main__":
    status = get_gpt5_status()
    print(json.dumps(status, indent=2))