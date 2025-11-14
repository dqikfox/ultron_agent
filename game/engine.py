"""ULTRON GameEngine - AI Agent Battle Arena"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from utils.ultron_logger import log_info, log_error

class AgentStatus(Enum):
    ACTIVE = "active"
    DEFEATED = "defeated"
    VICTORIOUS = "victorious"

class ActionType(Enum):
    ATTACK = "attack"
    DEFEND = "defend"
    SPECIAL = "special"

@dataclass
class Agent:
    id: str
    name: str
    health: int = 100
    attack_power: int = 20
    defense: int = 10
    status: AgentStatus = AgentStatus.ACTIVE

@dataclass
class BattleResult:
    winner_id: Optional[str]
    winner_name: Optional[str]
    rounds: int
    battle_log: List[str]

class GameEngine:
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.battle_log: List[str] = []
        self.round_number: int = 0
        log_info("game_engine", "GameEngine initialized")
    
    def register_agent(self, agent: Agent):
        self.agents[agent.id] = agent
        log_info("game_engine", f"Agent registered: {agent.name}")
    
    def start_battle(self, agent1_id: str, agent2_id: str, max_rounds: int = 10) -> BattleResult:
        log_info("game_engine", f"Battle: {agent1_id} vs {agent2_id}")
        
        agent1 = self.agents[agent1_id]
        agent2 = self.agents[agent2_id]
        
        for round_num in range(max_rounds):
            self.round_number = round_num + 1
            
            damage = max(0, agent1.attack_power - agent2.defense)
            agent2.health -= damage
            self.battle_log.append(f"R{self.round_number}: {agent1.name} -> {agent2.name} ({damage})")
            
            if agent2.health <= 0:
                return BattleResult(agent1.id, agent1.name, self.round_number, self.battle_log)
            
            damage = max(0, agent2.attack_power - agent1.defense)
            agent1.health -= damage
            self.battle_log.append(f"R{self.round_number}: {agent2.name} -> {agent1.name} ({damage})")
            
            if agent1.health <= 0:
                return BattleResult(agent2.id, agent2.name, self.round_number, self.battle_log)
        
        return BattleResult(None, "Draw", self.round_number, self.battle_log)
