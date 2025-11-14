# ULTRON AI SIMULATOR - Documentation

## Overview
The ULTRON AI SIMULATOR is a fantasy RPG system featuring AI-powered NPCs with emergent behaviors, real-time interactions, and dynamic state management. Each NPC is governed by an AI model (simulated) that adopts their character completely, leading to authentic roleplaying experiences.

## Key Features Implemented

### 🎮 8-Bit Visual Style
- Final Fantasy-style grid layout with pixel art aesthetics
- Colored character sprites for different classes (Wizard, Warrior, Rogue, Cleric, Goblin)
- Real-time animation and visual feedback
- Speech bubbles and interaction indicators

### 🤖 AI-Powered NPCs
- **5 Character Types**: Wizard, Warrior, Rogue, Cleric, Goblin
- **4 AI Models**: llama3, mistral, phi3, codellama
- **Persona System**: Each character has distinct personality traits and speech patterns
- **Memory System**: NPCs remember recent interactions for contextual responses

### 📊 State Management
Each NPC tracks real-time states that affect behavior:
- **Hunger** (0-100): Affects mood and priorities
- **Thirst** (0-100): Can impact health and happiness  
- **Happiness** (0-100): Influences interactions and goals
- **HP** (0-100): Represents current health status
- **Current Goal**: Wander, Find Food, Find Water, Socialize, Rest, Explore

### 🔄 Simulation Loop
- **60 TPS Game Loop**: Smooth, real-time updates
- **Goal-Driven AI**: NPCs set priorities based on their current needs
- **Natural Interactions**: NPCs seek out nearby characters to socialize
- **Emergent Behaviors**: Characters react based on their physical and emotional states

### 🎯 Interactive Controls

#### Character Creation
1. **Avatar Type**: Choose character class (wizard, warrior, rogue, cleric, goblin)
2. **AI Model**: Select which LLM backend to use
3. **Persona**: Choose from predefined character personalities
4. **Real-time Creation**: NPCs appear immediately in the game world

#### State Manipulation
- **Live Sliders**: Adjust hunger, thirst, happiness, HP in real-time
- **Goal Assignment**: Force specific behaviors
- **Event Triggering**: Random events that affect character states
- **Direct Messaging**: Send messages to NPCs and receive contextual responses

#### Model Hot-Swapping
- Change AI models on-the-fly
- Seamless persona continuation
- Snapshot-based state transfer
- Model performance monitoring

## How to Use

### Starting the Simulation
1. Open `ultron-ai-simulator.html` in your web browser
2. Click "▶️ Start Simulation" to begin
3. Watch as NPCs spawn and begin their autonomous behaviors

### Creating NPCs
1. Select Avatar Type, AI Model, and Persona from the dropdowns
2. Click "✨ Create NPC" 
3. The new character will appear on the grid immediately

### Managing NPCs
1. **Select NPCs**: Click on any character sprite to select them
2. **View State**: Selected character's state controls will appear
3. **Adjust States**: Use sliders to modify hunger, thirst, happiness, HP
4. **Send Messages**: Click "💬 Send Message" for direct NPC interaction
5. **Trigger Events**: Random events can be triggered for NPCs
6. **Delete NPCs**: Remove unwanted characters with "🗑️ Delete Selected"

### Observing Emergent Behaviors
Watch for these dynamic behaviors:

#### State-Driven Responses
- **High Hunger (>80)**: "I'm so hungry..." / "Is there any food around?"
- **High Thirst (>80)**: "I need water badly" / "I'm parched!"
- **Low Happiness (<30)**: "I feel so lonely..." / "Nothing seems to bring me joy"
- **Low HP (<50)**: "I don't feel well" / "I need some rest"

#### Goal-Directed Movement
- **Find Food**: NPCs seek out areas where they might find sustenance
- **Socialize**: Characters with low happiness seek out other NPCs
- **Rest**: Injured characters seek safety and recovery
- **Explore**: Curious characters venture into unknown areas

#### Real-time Interactions
- NPCs automatically detect nearby characters
- Authentic conversations based on personas and current states
- Memory system maintains conversation context
- Speech bubbles show dialogue in real-time

## Advanced Features

### AI Model Integration Architecture
While this demo uses simulated responses, the system is designed for real LLM integration:

```javascript
// Example integration structure for real AI models
async function generateResponse(npc, context) {
    const prompt = `
        You are ${npc.persona.name}. You are currently experiencing:
        - Hunger: ${npc.hunger}/100
        - Thirst: ${npc.thirst}/100  
        - HP: ${npc.hp}/100
        - Mood: ${getMood(npc)}
        
        Recent context: ${context}
        
        Speak, act, and think as this character. You believe you are real.
    `;
    
    // Send to Ollama/LM Studio API
    const response = await fetch('http://localhost:11434/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            model: npc.model,
            prompt: prompt,
            stream: false
        })
    });
    
    return await response.json();
}
```

### State Influence on Behavior
The system automatically adjusts NPC priorities based on their states:
- Critical needs (hunger >80, thirst >80) override other goals
- Low happiness triggers social behavior
- Low HP causes avoidance of danger
- High happiness increases exploratory behavior

### Memory and Context
Each NPC maintains:
- Last 5 interactions with timestamps
- Current emotional state history
- Goal completion tracking
- Relationship memory with other NPCs

## System Architecture

### Core Classes
- **NPC Class**: Manages individual character behavior, state, and interactions
- **Game Loop**: Handles timing, updates, and rendering
- **State Manager**: Tracks and updates character conditions
- **Interaction System**: Manages NPC-to-NPC communication

### Performance Optimizations
- Efficient DOM manipulation
- RequestAnimationFrame for smooth rendering
- Smart update scheduling
- Memory management for conversation history

## Technical Specifications

### Browser Requirements
- Modern web browser with ES6+ support
- Canvas or WebGL support for enhanced graphics
- Local storage for saving states (optional)

### Scalability
- Supports unlimited NPCs (limited by browser performance)
- Modular architecture for easy feature additions
- Plugin system for custom AI backends
- Export/import functionality for world states

## Future Enhancements

### Planned Features
1. **Real AI Integration**: Connect to actual Ollama/LM Studio instances
2. **3D Graphics**: Upgrade to WebGL-based rendering
3. **World Expansion**: Multiple rooms and outdoor areas
4. **Equipment System**: Weapons, armor, and magical items
5. **Quest System**: Complex storylines and objectives
6. **Network Multiplayer**: Multiple players controlling different areas
7. **Voice Integration**: Text-to-speech for character dialogue
8. **Advanced AI**: Memory persistence, learning, personality evolution

### Plugin Architecture
The system supports:
- Custom AI backends
- Additional character classes
- New interaction types
- Extended state systems
- Custom rendering engines

## Troubleshooting

### Common Issues
- **NPCs not moving**: Ensure simulation is running (green status indicator)
- **States not updating**: Check that an NPC is selected before adjusting sliders
- **Missing speech bubbles**: Verify JavaScript console for errors
- **Performance issues**: Reduce number of NPCs or lower tick rate

### Browser Compatibility
- Chrome/Edge: Full support
- Firefox: Full support  
- Safari: Full support
- Internet Explorer: Not supported

## License and Usage
This is a demonstration system created for educational and entertainment purposes. Feel free to modify, extend, and use in your own projects.

---
*Created by MiniMax Agent - Fantasy AI NPC Simulation System*