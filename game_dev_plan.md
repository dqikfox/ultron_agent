# ULTRON Agent Game Development Plan

## Game Concept: AI Agent Battle Arena

### Core Mechanics
- Turn-based combat between AI agents
- Each agent has unique abilities based on their model (Qwen, DeepSeek, Mistral, etc.)
- Resource management (tokens, energy, cooldowns)
- Strategic decision-making with AI-powered opponents

### Technical Stack
- **Backend**: Python Flask/FastAPI
- **Frontend**: HTML5 Canvas + JavaScript
- **AI Integration**: Ollama local models
- **Database**: SQLite for game state

### Implementation Phases

#### Phase 1: Core Game Engine (Use Continue for this)
```python
# File: game/engine.py
class GameEngine:
    def __init__(self):
        self.agents = []
        self.turn = 0
        self.state = "waiting"
    
    def add_agent(self, agent):
        pass
    
    def process_turn(self):
        pass
    
    def check_victory(self):
        pass
```

#### Phase 2: Agent System (Use Continue for this)
```python
# File: game/agent.py
class AIAgent:
    def __init__(self, name, model, hp=100, energy=50):
        self.name = name
        self.model = model  # qwen, deepseek, mistral
        self.hp = hp
        self.energy = energy
        self.abilities = []
    
    def use_ability(self, ability_name, target):
        pass
    
    def take_damage(self, amount):
        pass
```

#### Phase 3: Web Interface (Use Continue for this)
```html
<!-- File: game/templates/arena.html -->
<!DOCTYPE html>
<html>
<head>
    <title>AI Agent Arena</title>
    <style>
        #arena { width: 800px; height: 600px; border: 2px solid #000; }
    </style>
</head>
<body>
    <canvas id="arena"></canvas>
    <div id="controls"></div>
    <script src="arena.js"></script>
</body>
</html>
```

### Tasks for Continue Extension

**Prompt for Continue:**
"Create a turn-based AI agent battle game with the following:
1. GameEngine class with turn management
2. AIAgent class with HP, energy, and abilities
3. Flask server with WebSocket support
4. HTML5 Canvas frontend with agent sprites
5. SQLite database for game state persistence

Use the existing ULTRON agent architecture and integrate with Ollama models for AI decision-making."

### Integration with ULTRON
- Use existing `auto_orchestrator.py` for AI opponent decisions
- Leverage `avatar_builder_tool.py` for agent creation
- Connect to Ollama via existing brain.py integration

### Next Steps
1. Open Continue extension (Ctrl+L)
2. Paste the prompt above
3. Let Continue generate the initial codebase
4. I'll review and integrate with ULTRON systems
