"""D&D Game Engine with AI-Powered NPCs"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional
import random
import requests

class CharacterClass(Enum):
    WARRIOR = "Warrior"
    MAGE = "Mage"
    ROGUE = "Rogue"
    CLERIC = "Cleric"

class Race(Enum):
    HUMAN = "Human"
    ELF = "Elf"
    DWARF = "Dwarf"
    HALFLING = "Halfling"

@dataclass
class Character:
    name: str
    char_class: CharacterClass
    race: Race
    level: int = 1
    hp: int = 100
    max_hp: int = 100
    strength: int = 10
    dexterity: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10
    inventory: List[str] = field(default_factory=list)
    gold: int = 100

@dataclass
class NPC:
    name: str
    role: str
    personality: str
    dialogue_history: List[Dict] = field(default_factory=list)

class DnDGameEngine:
    def __init__(self, langflow_url: str = "http://localhost:7860"):
        self.langflow_url = langflow_url
        self.flow_id = "92c810b5-4829-4466-9ff1-7ad19b694435"
        self.player: Optional[Character] = None
        self.npcs: Dict[str, NPC] = {}
        self.current_location: str = "Tavern"
        self.quest_log: List[str] = []
        self.game_state: Dict = {}
        self._init_npcs()
    
    def _init_npcs(self):
        self.npcs = {
            "Innkeeper": NPC("Gareth", "Innkeeper", "Friendly and talkative, knows local gossip"),
            "Guard": NPC("Captain Thorne", "City Guard", "Stern but fair, protective of citizens"),
            "Wizard": NPC("Eldrin", "Wizard", "Mysterious and wise, speaks in riddles"),
            "Merchant": NPC("Mira", "Merchant", "Shrewd businesswoman, always looking for profit"),
            "Quest Giver": NPC("Lord Blackwood", "Noble", "Desperate noble seeking heroes")
        }
    
    def create_character(self, name: str, char_class: str, race: str) -> Character:
        self.player = Character(
            name=name,
            char_class=CharacterClass[char_class.upper()],
            race=Race[race.upper()]
        )
        return self.player
    
    def roll_dice(self, sides: int = 20, modifier: int = 0) -> int:
        return random.randint(1, sides) + modifier
    
    def get_ai_response(self, npc_name: str, player_input: str) -> str:
        npc = self.npcs.get(npc_name)
        if not npc:
            return "NPC not found."
        
        context = f"""You are {npc.name}, a {npc.role} in a D&D game.
Personality: {npc.personality}
Location: {self.current_location}
Player: {self.player.name if self.player else 'Unknown'} (Level {self.player.level if self.player else 1})

Roleplay as this character. Stay in character.

Player: {player_input}"""
        
        try:
            response = requests.post(
                f"{self.langflow_url}/api/v1/run/{self.flow_id}",
                json={"input_value": context, "output_type": "chat", "input_type": "chat"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get("outputs", [{}])[0].get("outputs", [{}])[0].get("results", {}).get("message", {}).get("text", "...")
                npc.dialogue_history.append({"player": player_input, "npc": ai_response})
                return ai_response
            else:
                return f"{npc.name}: *nods thoughtfully*"
        except:
            return f"{npc.name}: *seems distracted*"
    
    def start_quest(self) -> str:
        quest = """🗡️ THE SHADOW CRYSTAL QUEST 🗡️

Lord Blackwood's daughter has been cursed by a dark wizard. 
The only cure is the legendary Shadow Crystal, hidden in the Cursed Caverns.

Objectives:
1. Speak with Lord Blackwood at the Manor
2. Gather information from townspeople
3. Acquire supplies and equipment
4. Journey to the Cursed Caverns
5. Defeat the guardian and retrieve the Shadow Crystal
6. Return to save Lady Blackwood

Rewards: 1000 gold, Legendary Weapon, Noble's Favor"""
        self.quest_log.append("The Shadow Crystal Quest - Active")
        return quest
    
    def combat(self, enemy_name: str, enemy_hp: int, enemy_attack: int) -> Dict:
        player_hp = self.player.hp
        rounds = []
        
        while player_hp > 0 and enemy_hp > 0:
            player_roll = self.roll_dice(20, self.player.strength // 2)
            if player_roll > 10:
                damage = self.roll_dice(8, self.player.strength // 3)
                enemy_hp -= damage
                rounds.append(f"⚔️ You hit {enemy_name} for {damage} damage!")
            else:
                rounds.append(f"❌ You missed {enemy_name}!")
            
            if enemy_hp <= 0:
                break
            
            enemy_roll = self.roll_dice(20)
            if enemy_roll > 10:
                damage = self.roll_dice(6, enemy_attack)
                player_hp -= damage
                rounds.append(f"💥 {enemy_name} hits you for {damage} damage!")
            else:
                rounds.append(f"🛡️ You dodged {enemy_name}'s attack!")
        
        self.player.hp = max(0, player_hp)
        return {"victory": enemy_hp <= 0, "rounds": rounds, "player_hp": player_hp, "enemy_hp": enemy_hp}
