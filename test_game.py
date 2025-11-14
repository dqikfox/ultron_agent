"""Test ULTRON Game Engine"""
from game.engine import GameEngine, Agent

engine = GameEngine()

agent1 = Agent(id="1", name="Qwen", attack_power=25, defense=8)
agent2 = Agent(id="2", name="DeepSeek", attack_power=22, defense=10)

engine.register_agent(agent1)
engine.register_agent(agent2)

result = engine.start_battle("1", "2")

print(f"Winner: {result.winner_name}")
print(f"Rounds: {result.rounds}")
print("\nBattle Log:")
for log in result.battle_log:
    print(f"  {log}")
