# ULTRON Avatar Game Guide

## Overview

The ULTRON Avatar Game is an interactive RPG system that allows you to create, customize, and battle with AI-powered avatars. Built with a kid-friendly design and simple mechanics, it provides an engaging gaming experience with emoji-based characters and straightforward combat.

## Quick Start

### Launch the Game

```bash
# One-click launcher (recommended)
start_avatar_game.bat

# Manual launch
python avatar_game_server.py
```

**Access**: `http://localhost:8002`

### First Steps

1. **Create Avatar**: Click "Create New Avatar" button
2. **Choose Class**: Select from 8 character classes
3. **Choose Race**: Select from 8 fantasy races
4. **Choose Alignment**: Pick Hero, Villain, or Evil
5. **Name Your Avatar**: Give your character a unique name
6. **Start Playing**: Your avatar appears with stats and level

## Character System

### Classes (8 Total)

| Class | Emoji | Specialty | Primary Stat |
|-------|-------|-----------|--------------|
| **Warrior** | ⚔️ | Melee combat | Attack |
| **Mage** | 🔮 | Magic spells | Magic |
| **Rogue** | 🗡️ | Stealth & speed | Speed |
| **Healer** | ❤️ | Support & healing | Defense |
| **Ranger** | 🏹 | Ranged attacks | Attack |
| **Necromancer** | 💀 | Dark magic | Magic |
| **Berserker** | 🔥 | Rage & power | Attack |
| **Assassin** | 🌙 | Critical strikes | Speed |

### Races (8 Total)

| Race | Emoji | Description | Bonus |
|------|-------|-------------|-------|
| **Elf** | 🧝 | Graceful & wise | +Magic |
| **Dwarf** | 🧔 | Strong & sturdy | +Defense |
| **Orc** | 👹 | Brutal & fierce | +Attack |
| **Demon** | 😈 | Dark & powerful | +Magic |
| **Vampire** | 🧛 | Undead & cunning | +Speed |
| **Dragon** | 🐉 | Legendary & mighty | +All Stats |
| **Zombie** | 🧟 | Undead & resilient | +Defense |
| **Robot** | 🤖 | Mechanical & precise | +Speed |

### Alignments (3 Total)

- **😇 Hero**: Good-aligned, protects the innocent
- **😈 Villain**: Self-serving, pursues power
- **💀 Evil**: Malevolent, spreads chaos

## Stats System

### Core Stats (1-10 Scale)

- **⚔️ Attack**: Physical damage output
- **🛡️ Defense**: Damage reduction
- **✨ Magic**: Spell power and magical abilities
- **⚡ Speed**: Turn order and dodge chance

### Stat Generation

- Base stats: 3-7 (random)
- Race bonuses: +1 to specific stats
- Class bonuses: +1 to primary stat
- Total range: 4-10 per stat

## Combat System

### Battle Mechanics

1. **Initiative**: Speed determines turn order
2. **Attack Roll**: Random damage based on Attack stat
3. **Defense Roll**: Damage reduction based on Defense stat
4. **Magic Attacks**: Use Magic stat for spell damage
5. **Victory**: Reduce opponent HP to 0

### Damage Calculation

```
Physical Damage = Attack * (0.5 to 1.5) - Defense * 0.5
Magic Damage = Magic * (0.5 to 1.5) - Defense * 0.3
Final Damage = Max(1, Calculated Damage)
```

### Combat Stats Tracking

- **Kills**: Total enemies defeated
- **Victories**: Total battles won
- **Level**: Increases with victories

## Loot System

### Item Types

#### Weapons
- **Sword**: +2 Attack
- **Staff**: +2 Magic
- **Bow**: +1 Attack, +1 Speed
- **Dagger**: +1 Attack, +2 Speed

#### Armor
- **Plate Armor**: +3 Defense
- **Leather Armor**: +1 Defense, +1 Speed
- **Robe**: +1 Defense, +1 Magic
- **Chainmail**: +2 Defense

#### Items
- **Health Potion**: Restore 20 HP
- **Mana Potion**: Restore 20 MP
- **Speed Boost**: +2 Speed (temporary)
- **Strength Boost**: +2 Attack (temporary)

### Loot Generation

- Random drops after combat victories
- Higher level = better loot chances
- Multiple items can be equipped
- Stats stack with base character stats

## Progression System

### Leveling Up

- **XP Gain**: 100 XP per victory
- **Level Up**: Every 1000 XP
- **Stat Increase**: +1 to random stat per level
- **Max Level**: No limit

### Level-Up Animation

- Dramatic particle effects
- Glowing avatar with pulsing animation
- Stat increase notification
- Victory celebration

## Visual Features

### Avatar Display

- **120px Size**: Large, detailed avatars
- **Glow Effects**: Role-specific colored glows
- **Model Labels**: "MODEL | LVL X" format
- **Animated Backgrounds**: Gradient transitions

### UI Elements

- **Character Cards**: Click to view full info
- **Info Panels**: Detailed stats and equipment
- **Ripple Effects**: Interactive button feedback
- **Hover States**: Visual feedback on interactions

## AI Integration

### Tool Support

The avatar game server integrates with ULTRON tools:

- **OCR Tool**: Text recognition from game screenshots
- **PyAutoGUI Tool**: Automated game interactions
- **Role-Specific Responses**: AI adapts to character class

### AI Commands

```python
# Example AI interactions
"Create a warrior avatar named Thor"
"Show me all my avatars"
"Battle my mage against the orc"
"Level up my rogue character"
```

## Technical Details

### Server Architecture

- **Framework**: Flask (Python)
- **Port**: 8002
- **Process Management**: Automatic cleanup on restart
- **Error Handling**: Graceful fallbacks for tool failures

### File Structure

```
ultron_agent/
├── avatar_game_server.py          # Flask server
├── start_avatar_game.bat          # Launcher script
├── dnd_system.js                  # RPG rules engine
└── gui/ultron_enhanced/web/
    └── ultron_avatar_game_ultimate.html  # Game interface
```

### Configuration

No configuration required - works out of the box!

## Troubleshooting

### Server Won't Start

```bash
# Kill existing processes
taskkill /F /IM python.exe /FI "WINDOWTITLE eq avatar_game_server*"

# Restart server
start_avatar_game.bat
```

### Port 8002 Already in Use

```powershell
# Check what's using the port
Get-NetTCPConnection -LocalPort 8002

# Kill the process
Stop-Process -Id <PID> -Force
```

### Game Not Loading

1. Check browser console for errors (F12)
2. Verify server is running: `http://localhost:8002/health`
3. Clear browser cache and reload
4. Check `avatar_game_server.py` logs

### OCR/PyAutoGUI Not Working

- These are optional features
- Game works without them
- Check tool installation if needed

## Tips & Strategies

### Character Creation

- **Warriors**: High attack, good for beginners
- **Mages**: High magic, powerful spells
- **Rogues**: High speed, strike first
- **Healers**: High defense, survive longer

### Race Selection

- **Dragon**: Best overall stats (+all)
- **Orc**: Maximum attack power
- **Elf**: Strong magic abilities
- **Vampire**: Fastest characters

### Combat Strategy

1. **Speed First**: High speed = first strike advantage
2. **Balance Stats**: Don't neglect defense
3. **Use Magic**: Bypasses some defense
4. **Level Up**: Higher level = stronger stats

### Loot Management

- Equip weapons matching your class
- Stack armor for maximum defense
- Save potions for tough battles
- Upgrade equipment regularly

## Future Enhancements

### Planned Features

- [ ] Multiplayer battles
- [ ] Guild system
- [ ] Quest system
- [ ] Crafting system
- [ ] Pet companions
- [ ] Achievement system
- [ ] Leaderboards
- [ ] Tournament mode

### Community Requests

Submit feature requests via GitHub issues or contact the development team.

## Credits

- **Game Design**: ULTRON Agent Team
- **RPG System**: Simplified D&D-inspired mechanics
- **UI Design**: Retro gaming aesthetic with modern animations
- **AI Integration**: ULTRON tool ecosystem

## License

Part of the ULTRON Agent 3.0 project. See main README for license details.

---

**Ready to create your ultimate avatar? Launch the game and start your adventure!**

🎮 `start_avatar_game.bat` → `http://localhost:8002`
