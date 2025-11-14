"""Build complete RPG with story, quests, characters, dialogue"""

import requests
from pathlib import Path
import json


def generate(prompt):
    r = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "qwen3-coder:480b-cloud", "prompt": prompt, "stream": False},
        timeout=120
    )
    return r.json().get("response", "") if r.status_code == 200 else None


def create_game_design():
    """Create game design document"""
    design = {
        "title": "The Last Guardian",
        "genre": "Action RPG",
        "story": "Ancient evil awakens. You are the last guardian with power to stop it.",
        "acts": [
            {"name": "Act 1: Awakening", "quests": ["Tutorial", "First Enemy", "Village Elder"]},
            {"name": "Act 2: The Journey", "quests": ["Forest Temple", "Mountain Pass", "Ancient Ruins"]},
            {"name": "Act 3: Final Battle", "quests": ["Dark Castle", "Boss Fight", "Epilogue"]}
        ],
        "characters": [
            {"name": "Hero", "role": "Player", "abilities": ["Sword", "Magic", "Dash"]},
            {"name": "Elder Sage", "role": "Quest Giver", "location": "Village"},
            {"name": "Mysterious Merchant", "role": "Shop", "location": "Forest"},
            {"name": "Dark Lord", "role": "Boss", "location": "Castle"}
        ]
    }
    
    Path("UnityGame/GameDesign.json").write_text(json.dumps(design, indent=2))
    return design


def main():
    print("=== Building Complete RPG Game ===\n")
    
    base = Path("UnityGame/Assets/Scripts/RPG")
    base.mkdir(parents=True, exist_ok=True)
    
    # Create game design
    print("Creating game design...")
    design = create_game_design()
    print(f"  Story: {design['title']}\n")
    
    # Core RPG systems
    systems = {
        "QuestSystem.cs": """Unity quest system with:
- Quest data structure (id, title, description, objectives, rewards)
- Quest manager singleton
- Quest tracking (active, completed, failed)
- Objective completion checking
- Reward distribution (XP, gold, items)
- Quest log UI integration""",

        "DialogueSystem.cs": """Unity dialogue system with:
- Dialogue data structure (speaker, text, choices)
- Dialogue manager with queue
- Text display with typewriter effect
- Choice selection system
- NPC interaction triggers
- Dialogue UI controller""",

        "CharacterStats.cs": """Unity character stats with:
- Base stats (HP, MP, Attack, Defense, Speed)
- Level and XP system
- Stat calculation with equipment bonuses
- Level up rewards
- Stat persistence
- UI stat display""",

        "InventorySystem.cs": """Unity inventory with:
- Item data structure (id, name, type, stats)
- Inventory slots and capacity
- Add/remove/use items
- Equipment system (weapon, armor, accessories)
- Item stacking
- Inventory UI""",

        "NPCController.cs": """Unity NPC with:
- NPC data (name, dialogue, quests)
- Interaction trigger
- Quest availability indicator
- Dialogue initiation
- Shop integration
- Patrol behavior""",

        "CombatSystem.cs": """Unity combat with:
- Attack system with combos
- Damage calculation
- Health/mana management
- Status effects (poison, stun, buff)
- Enemy AI combat behavior
- Combat UI (health bars, damage numbers)""",

        "SaveSystem.cs": """Unity save system with:
- Save data structure (player, quests, inventory)
- JSON serialization
- Save/load functionality
- Multiple save slots
- Auto-save on checkpoints
- Save file management"""
    }
    
    for filename, prompt in systems.items():
        print(f"Generating {filename}...")
        code = generate(f"Create Unity C# script:\n{prompt}\n\nComplete implementation with all methods.")
        if code:
            (base / filename).write_text(code, encoding='utf-8')
            print(f"  Saved\n")
    
    # Story content
    print("Generating story content...")
    
    story_data = {
        "quests": [
            {"id": 1, "title": "The Awakening", "description": "Speak with Elder Sage", "reward": 100},
            {"id": 2, "title": "Forest Danger", "description": "Clear 5 enemies from forest", "reward": 250},
            {"id": 3, "title": "Ancient Artifact", "description": "Find the Guardian's Sword", "reward": 500},
            {"id": 4, "title": "Mountain Trial", "description": "Reach the mountain peak", "reward": 750},
            {"id": 5, "title": "Final Confrontation", "description": "Defeat the Dark Lord", "reward": 2000}
        ],
        "dialogues": {
            "elder_intro": "Welcome, young guardian. Dark times are upon us...",
            "merchant_greeting": "Looking for supplies? I have the finest wares!",
            "boss_taunt": "You dare challenge me? Foolish mortal!"
        },
        "items": [
            {"id": 1, "name": "Health Potion", "type": "consumable", "effect": "heal_50"},
            {"id": 2, "name": "Guardian Sword", "type": "weapon", "attack": 25},
            {"id": 3, "name": "Steel Armor", "type": "armor", "defense": 15}
        ]
    }
    
    Path("UnityGame/Assets/Resources/GameData.json").parent.mkdir(parents=True, exist_ok=True)
    Path("UnityGame/Assets/Resources/GameData.json").write_text(json.dumps(story_data, indent=2))
    print("  Story data saved\n")
    
    print("=== RPG Generation Complete ===\n")
    print(f"Generated: {len(systems)} core systems")
    print(f"Quests: {len(story_data['quests'])}")
    print(f"Items: {len(story_data['items'])}")
    print(f"\nLocation: {base}")


if __name__ == '__main__':
    main()
