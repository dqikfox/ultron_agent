# Avatar Game Quick Reference

## Launch Commands

```bash
# Quick start
start_avatar_game.bat

# Manual start
python avatar_game_server.py

# Access game
http://localhost:8002
```

## Character Classes

| Class | Emoji | Primary Stat | Best For |
|-------|-------|--------------|----------|
| Warrior | ⚔️ | Attack | Beginners, melee combat |
| Mage | 🔮 | Magic | Spell damage, ranged |
| Rogue | 🗡️ | Speed | First strikes, evasion |
| Healer | ❤️ | Defense | Survival, support |
| Ranger | 🏹 | Attack | Ranged attacks |
| Necromancer | 💀 | Magic | Dark magic, debuffs |
| Berserker | 🔥 | Attack | Raw damage output |
| Assassin | 🌙 | Speed | Critical hits |

## Races

| Race | Emoji | Bonus | Description |
|------|-------|-------|-------------|
| Elf | 🧝 | +Magic | Graceful spellcasters |
| Dwarf | 🧔 | +Defense | Sturdy warriors |
| Orc | 👹 | +Attack | Brutal fighters |
| Demon | 😈 | +Magic | Dark powers |
| Vampire | 🧛 | +Speed | Swift undead |
| Dragon | 🐉 | +All | Legendary might |
| Zombie | 🧟 | +Defense | Resilient undead |
| Robot | 🤖 | +Speed | Precise machines |

## Stats (1-10 Scale)

- **⚔️ Attack**: Physical damage
- **🛡️ Defense**: Damage reduction
- **✨ Magic**: Spell power
- **⚡ Speed**: Turn order

## Combat Formula

```
Damage = Attacker Stat * (0.5-1.5) - Defender Defense * 0.5
Minimum Damage = 1
```

## Loot Types

### Weapons
- Sword: +2 Attack
- Staff: +2 Magic
- Bow: +1 Attack, +1 Speed
- Dagger: +1 Attack, +2 Speed

### Armor
- Plate: +3 Defense
- Leather: +1 Defense, +1 Speed
- Robe: +1 Defense, +1 Magic
- Chainmail: +2 Defense

### Items
- Health Potion: +20 HP
- Mana Potion: +20 MP
- Speed Boost: +2 Speed
- Strength Boost: +2 Attack

## Progression

- **XP per Victory**: 100
- **Level Up**: Every 1000 XP
- **Stat Gain**: +1 random stat per level
- **No Level Cap**

## Best Combinations

### Maximum Damage
- **Orc Berserker** (Attack focus)
- **Dragon Warrior** (Balanced power)

### Fastest Character
- **Vampire Assassin** (Speed focus)
- **Robot Rogue** (Quick strikes)

### Best Spellcaster
- **Elf Mage** (Magic focus)
- **Demon Necromancer** (Dark magic)

### Most Durable
- **Dwarf Healer** (Defense focus)
- **Zombie Warrior** (Tank build)

## Troubleshooting

### Server Issues
```bash
# Kill and restart
taskkill /F /IM python.exe /FI "WINDOWTITLE eq avatar_game_server*"
start_avatar_game.bat
```

### Port Conflict
```powershell
Get-NetTCPConnection -LocalPort 8002
Stop-Process -Id <PID> -Force
```

### Game Not Loading
1. Check server: `http://localhost:8002/health`
2. Clear browser cache (Ctrl+Shift+Delete)
3. Check console (F12) for errors

## Keyboard Shortcuts

- **F5**: Refresh game
- **F12**: Open developer console
- **Ctrl+Click**: Quick select avatar
- **Esc**: Close info panels

## Tips

✅ **DO**:
- Balance attack and defense
- Level up regularly
- Collect loot after battles
- Try different class/race combos

❌ **DON'T**:
- Neglect defense stat
- Ignore speed for turn order
- Forget to equip loot
- Rush into high-level battles

## Server Endpoints

- `GET /`: Game interface
- `GET /health`: Server status
- `POST /api/command`: Execute commands
- `GET /api/status`: Game status

## File Locations

```
C:\Projects\ultron_agent\
├── avatar_game_server.py
├── start_avatar_game.bat
├── dnd_system.js
└── gui\ultron_enhanced\web\
    └── ultron_avatar_game_ultimate.html
```

## Documentation

- **Full Guide**: `AVATAR_GAME_GUIDE.md`
- **Main README**: `README.md` (v3.0.5 section)
- **Server Code**: `avatar_game_server.py`
- **Game Rules**: `dnd_system.js`

---

**Quick Start**: `start_avatar_game.bat` → Create Avatar → Battle!
