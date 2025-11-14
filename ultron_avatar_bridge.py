"""ULTRON Avatar Game Bridge - Connect avatar game to main ULTRON agent"""
import requests
import json
from pathlib import Path

AVATAR_SERVER = 'http://localhost:8082'
ULTRON_API = 'http://localhost:8001'

def execute_ultron_tool(tool_name, **kwargs):
    """Execute ULTRON tool and return result"""
    try:
        r = requests.post(f'{ULTRON_API}/api/tool/execute', 
                         json={'tool': tool_name, 'params': kwargs}, timeout=10)
        return r.json() if r.status_code == 200 else None
    except:
        return None

def voice_command_handler(command):
    """Handle voice commands for avatar game"""
    cmd = command.lower()
    
    # Spawn avatar
    if 'spawn' in cmd or 'create' in cmd:
        role = 'random'
        for r in ['coder', 'writer', 'tool', 'assistant', 'admin']:
            if r in cmd:
                role = r
                break
        return {'action': 'spawn', 'role': role}
    
    # Select model
    if 'talk to' in cmd or 'select' in cmd:
        models = {'qwen': 'qwen3-coder:480b-cloud', 'ultron': 'gerard/ultron:latest',
                 'seeker': 'deepseek-r1:14b', 'llama': 'llama3.1:latest', 
                 'mistral': 'mistral-small3.2:latest'}
        for name, model in models.items():
            if name in cmd:
                return {'action': 'select_model', 'model': model}
    
    # Show stats/analytics
    if 'stats' in cmd or 'analytics' in cmd or 'dashboard' in cmd:
        return {'action': 'show_analytics'}
    
    # Clear avatars
    if 'clear' in cmd or 'remove all' in cmd:
        return {'action': 'clear'}
    
    # Battle mode
    if 'battle' in cmd or 'fight' in cmd:
        return {'action': 'battle'}
    
    # Save/load
    if 'save' in cmd:
        return {'action': 'save'}
    if 'load' in cmd:
        return {'action': 'load'}
    
    return None

def get_ultron_tools():
    """Get list of available ULTRON tools"""
    try:
        r = requests.get(f'{ULTRON_API}/api/tools', timeout=5)
        return r.json().get('tools', []) if r.status_code == 200 else []
    except:
        return []

def integrate_with_ultron():
    """Check ULTRON integration status"""
    try:
        r = requests.get(f'{ULTRON_API}/api/status', timeout=2)
        return r.status_code == 200
    except:
        return False
