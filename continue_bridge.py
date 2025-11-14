"""Bridge to automate Continue extension via task queue"""
import json
from pathlib import Path

def create_continue_task(prompt: str, context_files: list = None):
    """Create task for Continue extension to process"""
    task = {
        "id": "game_dev_001",
        "status": "pending",
        "priority": 1,
        "task": "Build AI Agent Battle Arena Game",
        "prompt": prompt,
        "model": "qwen2.5-coder:1.5b",
        "output_file": "game/",
        "context_files": context_files or [],
        "created_by": "amazon_q",
        "created_at": "2025-01-16T00:00:00"
    }
    
    # Save to Continue's workspace
    continue_tasks = Path(".continue/tasks.json")
    continue_tasks.parent.mkdir(exist_ok=True)
    
    with open(continue_tasks, 'w') as f:
        json.dump([task], f, indent=2)
    
    print(f"Task created: {continue_tasks}")
    print(f"Prompt: {prompt[:100]}...")
    return task

if __name__ == "__main__":
    prompt = """Build a turn-based AI Agent Battle Arena game with:

1. GameEngine class (game/engine.py):
   - Turn management
   - Agent registration
   - Victory conditions
   - State persistence

2. AIAgent class (game/agent.py):
   - HP, energy, abilities
   - Model integration (Qwen, DeepSeek, Mistral)
   - Damage calculation
   - AI decision-making via Ollama

3. Flask server (game/server.py):
   - WebSocket support
   - Game state API
   - Real-time updates

4. HTML5 Canvas frontend (game/templates/arena.html):
   - Agent sprites
   - Turn indicators
   - Ability buttons
   - Health bars

5. SQLite database (game/database.py):
   - Game state persistence
   - Match history
   - Agent stats

Integrate with existing ULTRON systems:
- Use auto_orchestrator.py for AI decisions
- Leverage avatar_builder_tool.py for agent creation
- Connect to Ollama via brain.py
"""
    
    context = [
        "game_dev_plan.md",
        "auto_orchestrator.py",
        "tools/avatar_builder_tool.py",
        "brain.py"
    ]
    
    create_continue_task(prompt, context)
    print("\nGame development task queued for Continue extension")
    print("Open Continue (Ctrl+L) and it will see this task")
