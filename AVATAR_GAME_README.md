# 🎮 ULTRON Avatar Game - Ultimate Edition

## 🌟 Overview

The ULTRON Avatar Game is a production-ready, fully-integrated AI avatar management system that combines:
- **6 Specialized AI Avatars** with unique roles and capabilities
- **Voice Control** for hands-free operation
- **Avatar Battles** for competitive task solving
- **Skill Trees & Leveling** with XP progression
- **Full ULTRON Integration** with 35+ tools
- **Save/Load System** for persistent gameplay
- **Real-time Communication** via WebSockets

## 🚀 Quick Start

### 1. Deploy the Game
```bash
deploy_avatar_game.bat
```

This will:
- ✅ Check Python installation
- ✅ Install dependencies
- ✅ Start Avatar Game Server (port 8082)
- ✅ Start Web GUI Server (port 8080)
- ✅ Open game in browser

### 2. Test Everything
```bash
python test_avatar_game.py
```

Runs comprehensive tests on:
- File existence
- Server connectivity
- Avatar creation
- Tool availability
- Save/load functionality
- ULTRON integration

### 3. Play the Game
Open browser to: `http://localhost:8082`

## 🤖 Avatar Roles

### 💻 ULTRON-CODER
- **Specialty**: Programming & Development
- **Tools**: Code analysis, debugging, Git operations, file ops, OCR
- **Best Model**: Qwen3 Coder 480B
- **Use For**: Writing code, debugging, analyzing projects

### 📝 ULTRON-WRITER
- **Specialty**: Content Creation & Documentation
- **Tools**: Text processing, OCR, file ops, web search
- **Best Model**: Mistral Nemo 12B
- **Use For**: Writing articles, documentation, creative content

### 🔧 ULTRON-TOOLMASTER
- **Specialty**: System Automation & Tool Integration
- **Tools**: PyAutoGUI, system control, file ops, OCR, web automation
- **Best Model**: LLAVA 7B (Vision)
- **Use For**: Automating tasks, controlling systems, integrating APIs

### 🤖 ULTRON-ASSISTANT
- **Specialty**: Multi-Purpose AI Helper
- **Tools**: Web search, OCR, text processing, basic automation
- **Best Model**: Gemma3 12B
- **Use For**: General assistance, information retrieval, task management

### 🛡️ ULTRON-ADMIN
- **Specialty**: System Administration & Security
- **Tools**: System control, file ops, security tools, monitoring, OCR
- **Best Model**: EXAONE Deep 7.8B
- **Use For**: System management, security, monitoring, deployment

### 🖱️ ULTRON-CONTROLLER
- **Specialty**: Advanced Screen Control & GUI Automation
- **Tools**: PyAutoGUI, OCR, screen capture, mouse/keyboard, image recognition
- **Best Model**: LLAVA 7B (Vision)
- **Use For**: GUI automation, screen control, visual interface interaction

## 🎮 Features

### Voice Control 🎤
- Press **V** or click "🎤 Voice" button
- Speak commands naturally
- Avatars respond to voice input
- Visual indicator shows when listening

### Avatar Battles ⚔️
- Press **B** or click "⚔️ Battle" button
- Avatars compete to solve tasks
- Winner gets bonus XP
- Real-time battle visualization

### Leveling System 📈
- Avatars gain XP from interactions
- Level up every 100 XP
- Visual level-up notifications
- Track progress per avatar

### Save/Load 💾
- Save game state anytime
- Load previous sessions
- Persistent avatar data
- Automatic state management

### ULTRON Integration 🔗
- Press **I** or click "🔗 Integrate" button
- Connects to main ULTRON Agent
- Access to 35+ tools
- Shared memory system
- Real-time monitoring

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **SPACE** | Spawn new avatar |
| **V** | Toggle voice control |
| **B** | Start avatar battle |
| **I** | Integrate with ULTRON |
| **C** | Clear all avatars |
| **M** | View memory |
| **S** | Take screenshot |
| **L** | Toggle live view |
| **T** | Open tools panel |

## 🔧 API Endpoints

### Avatar Management
- `POST /api/avatar/create` - Create new avatar
- `POST /api/avatar/{id}/chat` - Chat with avatar
- `GET /api/avatar/{id}/stats` - Get avatar statistics

### Game State
- `POST /api/game/save` - Save game state
- `POST /api/game/load` - Load game state

### Tools
- `POST /api/tools/test` - Test tool availability

### Integration
- `POST /api/ultron/integrate` - Integrate with ULTRON Agent

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  ULTRON Avatar Game                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Frontend   │  │    Server    │  │  ULTRON Core │ │
│  │  (HTML/JS)   │◄─┤  (Flask/WS)  │◄─┤  (agent_core)│ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│         │                  │                  │         │
│         ▼                  ▼                  ▼         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Avatars    │  │  Game State  │  │    Tools     │ │
│  │  (6 Roles)   │  │  (Save/Load) │  │   (35+)      │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## 🎨 Visual Features

### Enhanced Graphics
- Gradient backgrounds with animations
- Glowing avatar effects
- Smooth transitions and animations
- Particle system
- Glassmorphism UI

### Avatar Visuals
- 100px circular avatars
- Role-specific colors
- Emoji representations
- Level badges
- Speaking animations
- Hover effects

### UI/UX
- Orbitron font for futuristic look
- Dark theme with neon accents
- Responsive design
- Real-time status updates
- Visual feedback for all actions

## 🔌 Integration Points

### Main ULTRON System
- Connects to `agent_core.py`
- Shares memory with ULTRON brain
- Access to all ULTRON tools
- Real-time event system
- Performance monitoring

### Tools Integration
- OCR (Tesseract)
- PyAutoGUI (Screen control)
- File operations
- Web search
- System control
- API connectors

### Voice Integration
- Web Speech API
- Continuous recognition
- Natural language processing
- Command routing

## 📈 Progression System

### XP Rewards
- **Chat interaction**: 10 XP
- **Avatar click**: 5 XP
- **Tool usage**: 15 XP
- **Battle win**: 50 XP
- **Task completion**: 25 XP

### Level Benefits
- Level 1-5: Basic capabilities
- Level 6-10: Enhanced tools
- Level 11-15: Advanced features
- Level 16-20: Expert mode
- Level 21+: Master level

## 🛠️ Development

### File Structure
```
ultron_agent/
├── avatar_game_server.py          # Main server
├── deploy_avatar_game.bat         # Deployment script
├── test_avatar_game.py            # Test suite
├── AVATAR_GAME_README.md          # This file
├── gui/ultron_enhanced/web/
│   ├── ultron_avatar_game_enhanced.html    # Enhanced version
│   └── ultron_avatar_game_ultimate.html    # Ultimate version
└── Avatar/                        # 3D models
    ├── ultron+xps.glb
    ├── ultron+xps2.glb
    ├── ultron+xps3.glb
    ├── ultron+xps4.glb
    ├── ultron+xps5.glb
    └── ultron_exported.glb
```

### Dependencies
```bash
pip install flask flask-cors flask-socketio python-socketio
```

### Running Tests
```bash
# Run all tests
python test_avatar_game.py

# Test specific component
curl -X POST http://localhost:8082/api/tools/test \
  -H "Content-Type: application/json" \
  -d '{"tool":"all"}'
```

## 🎯 Use Cases

### 1. Development Team
- Spawn CODER avatars for code review
- Use TOOLMASTER for automation
- ADMIN for deployment

### 2. Content Creation
- WRITER avatars for articles
- ASSISTANT for research
- Multiple avatars for brainstorming

### 3. System Administration
- ADMIN avatars for monitoring
- CONTROLLER for GUI automation
- TOOLMASTER for scripting

### 4. Learning & Training
- Battle mode for skill development
- XP system for progress tracking
- Multiple models for comparison

## 🚨 Troubleshooting

### Server Won't Start
```bash
# Check if port is in use
netstat -ano | findstr :8082

# Kill process if needed
taskkill /PID <PID> /F

# Restart server
python avatar_game_server.py
```

### Avatars Not Responding
1. Check Ollama is running: `ollama list`
2. Verify model availability: `ollama pull llava:7b`
3. Check server logs
4. Test API: `curl http://localhost:8082/api/tools/test`

### Voice Control Not Working
1. Use Chrome or Edge (best support)
2. Allow microphone permissions
3. Check browser console for errors
4. Ensure HTTPS or localhost

### Integration Failed
1. Verify ULTRON agent is running
2. Check `agent_core.py` is accessible
3. Review server logs
4. Test connection: `curl http://localhost:8082/api/ultron/integrate -X POST`

## 📝 Future Enhancements

- [ ] Mobile app version
- [ ] VR/AR support
- [ ] Multiplayer mode
- [ ] Achievement system
- [ ] Custom avatar skins
- [ ] Advanced skill trees
- [ ] Tournament mode
- [ ] Leaderboards
- [ ] Avatar marketplace
- [ ] Plugin system

## 🤝 Contributing

This is part of the ULTRON Agent 3.0 project. Follow the main project guidelines for contributions.

## 📄 License

Part of ULTRON Agent 3.0 - See main project license.

---

**Ready to command your ULTRON avatars!** 🎮⚡

For support, check the main ULTRON documentation or run the test suite.
