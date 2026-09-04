"""Avatar Builder Tool - Create game avatars with stats and visuals"""
from utils.ultron_logger import log_info, log_error
import json
import random
from pathlib import Path

class AvatarBuilderTool:
    name = "avatar_builder_tool"
    description = "Create and customize game avatars"
    
    CLASSES = ["Warrior", "Mage", "Rogue", "Healer", "Ranger", "Necromancer", "Berserker", "Assassin"]
    RACES = ["Elf", "Dwarf", "Orc", "Demon", "Vampire", "Dragon", "Zombie", "Robot"]
    
    def __init__(self):
        self.avatar_dir = Path("data/avatars")
        self.avatar_dir.mkdir(parents=True, exist_ok=True)
    
    def match(self, command: str) -> bool:
        """Match avatar creation commands"""
        keywords = ["create avatar", "build avatar", "new character", "make avatar"]
        return any(k in command.lower() for k in keywords)
    
    def execute(self, command: str) -> str:
        """Generate complete avatar"""
        try:
            log_info("avatar_builder_tool", f"Creating avatar: {command}")
            
            # Parse command for class/race
            avatar_class = self._parse_class(command)
            avatar_race = self._parse_race(command)
            avatar_name = self._parse_name(command)
            
            # Generate avatar
            avatar = self._generate_avatar(avatar_name, avatar_class, avatar_race)
            
            # Save avatar
            self._save_avatar(avatar)
            
            return self._format_avatar(avatar)
            
        except Exception as e:
            log_error("avatar_builder_tool", f"Error: {e}")
            return f"Error creating avatar: {e}"
    
    def _parse_class(self, command: str) -> str:
        """Extract class from command"""
        for cls in self.CLASSES:
            if cls.lower() in command.lower():
                return cls
        return random.choice(self.CLASSES)
    
    def _parse_race(self, command: str) -> str:
        """Extract race from command"""
        for race in self.RACES:
            if race.lower() in command.lower():
                return race
        return random.choice(self.RACES)
    
    def _parse_name(self, command: str) -> str:
        """Extract name from command"""
        words = command.split()
        for i, word in enumerate(words):
            if word.lower() in ["named", "called", "name"]:
                if i + 1 < len(words):
                    return words[i + 1].strip("'\"")
        return f"Hero{random.randint(1000, 9999)}"
    
    def _generate_avatar(self, name: str, avatar_class: str, race: str) -> dict:
        """Generate complete avatar data"""
        return {
            "name": name,
            "class": avatar_class,
            "race": race,
            "level": 1,
            "stats": self._generate_stats(avatar_class),
            "visual": self._create_visual(avatar_class, race),
            "equipment": [],
            "inventory": []
        }
    
    def _generate_stats(self, avatar_class: str) -> dict:
        """Generate stats based on class"""
        base_stats = {
            "Warrior": {"attack": 8, "defense": 7, "magic": 2, "speed": 5},
            "Mage": {"attack": 3, "defense": 4, "magic": 9, "speed": 6},
            "Rogue": {"attack": 6, "defense": 5, "magic": 3, "speed": 9},
            "Healer": {"attack": 4, "defense": 6, "magic": 8, "speed": 5},
            "Ranger": {"attack": 7, "defense": 5, "magic": 4, "speed": 8},
            "Necromancer": {"attack": 5, "defense": 4, "magic": 9, "speed": 4},
            "Berserker": {"attack": 9, "defense": 6, "magic": 1, "speed": 7},
            "Assassin": {"attack": 8, "defense": 4, "magic": 3, "speed": 10}
        }
        return base_stats.get(avatar_class, {"attack": 5, "defense": 5, "magic": 5, "speed": 5})
    
    def _create_visual(self, avatar_class: str, race: str) -> str:
        """Create emoji-based visual"""
        class_emoji = {
            "Warrior": "⚔️", "Mage": "🔮", "Rogue": "🗡️", "Healer": "❤️",
            "Ranger": "🏹", "Necromancer": "💀", "Berserker": "🔥", "Assassin": "🌙"
        }
        race_emoji = {
            "Elf": "🧝", "Dwarf": "🧔", "Orc": "👹", "Demon": "😈",
            "Vampire": "🧛", "Dragon": "🐉", "Zombie": "🧟", "Robot": "🤖"
        }
        return f"{class_emoji.get(avatar_class, '⚔️')}{race_emoji.get(race, '🧝')}"
    
    def _save_avatar(self, avatar: dict):
        """Save avatar to file"""
        filename = self.avatar_dir / f"{avatar['name']}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(avatar, f, indent=2)
        log_info("avatar_builder_tool", f"Saved avatar: {filename}")
    
    def _load_avatar(self, name: str) -> dict:
        """Load avatar from file"""
        filename = self.avatar_dir / f"{name}.json"
        if filename.exists():
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def _format_avatar(self, avatar: dict) -> str:
        """Format avatar for display"""
        stats = avatar['stats']
        return f"""
Avatar Created: {avatar['visual']} {avatar['name']}
Class: {avatar['class']}
Race: {avatar['race']}
Level: {avatar['level']}

Stats:
  Attack:  {stats['attack']}/10
  Defense: {stats['defense']}/10
  Magic:   {stats['magic']}/10
  Speed:   {stats['speed']}/10

Saved to: data/avatars/{avatar['name']}.json
"""
    
    @classmethod
    def schema(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "command": "String with avatar details (class, race, name)"
            }
        }
