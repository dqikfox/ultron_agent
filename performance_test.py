"""Performance test for Langflow integration and game engine"""
import time
import json
from game.engine import GameEngine, Agent
from langflow_coding_agent import LangflowCodingAgent

def test_game_performance():
    """Test game engine performance"""
    print("=== GAME ENGINE PERFORMANCE TEST ===\n")
    
    start = time.time()
    engine = GameEngine()
    
    agent1 = Agent(id="1", name="Qwen", attack_power=25, defense=8)
    agent2 = Agent(id="2", name="DeepSeek", attack_power=22, defense=10)
    
    engine.register_agent(agent1)
    engine.register_agent(agent2)
    
    result = engine.start_battle("1", "2")
    elapsed = time.time() - start
    
    print(f"Winner: {result.winner_name}")
    print(f"Rounds: {result.rounds}")
    print(f"Execution Time: {elapsed:.4f}s")
    print(f"Performance: {result.rounds/elapsed:.2f} rounds/sec\n")
    
    return elapsed

def test_langflow_performance():
    """Test Langflow API performance"""
    print("=== LANGFLOW API PERFORMANCE TEST ===\n")
    
    agent = LangflowCodingAgent()
    
    start = time.time()
    result = agent.generate_code("Create a simple hello world function")
    elapsed = time.time() - start
    
    print(f"Response Time: {elapsed:.4f}s")
    print(f"Response Size: {len(str(result))} chars")
    
    if "error" in result:
        print(f"Status: FAILED - {result['error']}")
    else:
        print("Status: SUCCESS")
    
    print(f"\nSample Output:\n{str(result)[:200]}...\n")
    
    return elapsed

def test_multiple_battles():
    """Test multiple battles for consistency"""
    print("=== MULTIPLE BATTLES TEST ===\n")
    
    engine = GameEngine()
    times = []
    
    for i in range(5):
        agent1 = Agent(id=f"a{i}", name=f"Agent{i}", attack_power=20+i, defense=10)
        agent2 = Agent(id=f"b{i}", name=f"Bot{i}", attack_power=18+i, defense=12)
        
        engine.register_agent(agent1)
        engine.register_agent(agent2)
        
        start = time.time()
        result = engine.start_battle(f"a{i}", f"b{i}")
        elapsed = time.time() - start
        times.append(elapsed)
        
        print(f"Battle {i+1}: {result.winner_name} won in {result.rounds} rounds ({elapsed:.4f}s)")
    
    avg_time = sum(times) / len(times)
    print(f"\nAverage Time: {avg_time:.4f}s")
    print(f"Min Time: {min(times):.4f}s")
    print(f"Max Time: {max(times):.4f}s\n")

def generate_report():
    """Generate performance report"""
    print("=== PERFORMANCE REPORT ===\n")
    
    game_time = test_game_performance()
    langflow_time = test_langflow_performance()
    test_multiple_battles()
    
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "game_engine": {
            "execution_time": f"{game_time:.4f}s",
            "status": "PASS" if game_time < 1.0 else "SLOW"
        },
        "langflow_api": {
            "response_time": f"{langflow_time:.4f}s",
            "status": "PASS" if langflow_time < 5.0 else "SLOW"
        },
        "overall": "PASS" if game_time < 1.0 and langflow_time < 5.0 else "NEEDS_OPTIMIZATION"
    }
    
    with open("performance_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"Report saved: performance_report.json")
    print(f"Overall Status: {report['overall']}")

if __name__ == "__main__":
    generate_report()
