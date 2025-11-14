# The Shadow Crystal - D&D 3.5 Web Game

## 🎮 Quick Start

```bash
cd C:\Projects\ultron_agent\dnd_game
python -m http.server 8090
```

Open: http://localhost:8090

## 🎯 Game Features

- **6 Quest Stages**: Tavern → Market → Gate → Forest → Cavern → Chamber
- **AI-Powered NPCs**: Each NPC uses Ollama for intelligent roleplay
- **3D Dice Rolling**: Animated d20 with physics
- **Character Progression**: XP, leveling, HP tracking
- **D&D 3.5 Rules**: DC scaling, skill checks, combat

## ⌨️ Controls

- **SPACE** - Talk to NPC
- **R** - Roll d20
- **N** - Next Stage
- **Click Avatar** - Talk to NPC

## 🎭 Quest Stages

1. **Tavern** (DC 10) - Gather information from Innkeeper
2. **Market** (DC 12) - Buy supplies from Merchant
3. **City Gate** (DC 14) - Get travel permit from Guard
4. **Dark Forest** (DC 16) - Learn spell from Wizard
5. **Cursed Caverns** (DC 18) - Defeat Stone Guardian
6. **Crystal Chamber** (DC 20) - Retrieve Shadow Crystal

## 🧙 Character System

- **Classes**: Fighter, Rogue, Wizard, Cleric
- **Leveling**: 100 XP per stage
- **HP**: Increases +10 per level
- **Inventory**: Quest items and equipment

## 🤖 AI Integration

Uses Ollama (llama3.1:latest) for NPC dialogue:
- Contextual responses based on location
- Character-specific personalities
- Quest-aware dialogue

## 🎲 Dice System

- Animated 3D d20 roll
- DC scaling per stage (10-20)
- Success/failure feedback
- Retry on failure

## 📊 Stats Tracked

- Level
- XP
- HP/Max HP
- Quest Stage
- Inventory

## 🚀 Next Steps

1. Add character creation screen
2. Implement inventory system
3. Add combat mechanics
4. Create save/load system
5. Add more NPCs and side quests

## 🎨 3D Asset Resources

See **ASSET_SOURCES.md** for production-ready assets:
- Medieval environments (taverns, villages, dungeons)
- Character models with animations (Mixamo)
- UI icons and inventory items
- PBR textures and materials
- D20 dice models

**Quick Links**:
- Unity Asset Store: https://assetstore.unity.com/
- Mixamo Characters: https://www.mixamo.com/
- Game Icons: https://game-icons.net/
- Sketchfab D20: https://sketchfab.com/search?type=models&q=d20&features=downloadable
