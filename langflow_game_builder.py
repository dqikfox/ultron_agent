"""Langflow integration for automated game building"""
import requests
import uuid
import json

LANGFLOW_URL = "http://localhost:7860/api/v1/run/92c810b5-4829-4466-9ff1-7ad19b694435"
LANGFLOW_API_KEY = "sk-P8RcOr7-zDErbDU1Un1cJL3l-zozgr45sazXhUcX-2U"

def build_game_via_langflow(prompt: str):
    """Send game building request to Langflow"""
    payload = {
        "output_type": "chat",
        "input_type": "chat",
        "input_value": prompt,
        "session_id": str(uuid.uuid4())
    }
    
    headers = {"Authorization": f"Bearer {LANGFLOW_API_KEY}"}
    
    try:
        response = requests.post(LANGFLOW_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    game_prompt = """Build AI Agent Battle Arena game with:
    
1. game/engine.py - GameEngine class with turn management
2. game/agent.py - AIAgent class with HP, energy, abilities
3. game/server.py - Flask server with WebSocket
4. game/templates/arena.html - HTML5 Canvas frontend
5. game/database.py - SQLite persistence

Use Python, Flask, HTML5 Canvas. Make it playable."""
    
    print("Sending to Langflow...")
    result = build_game_via_langflow(game_prompt)
    
    output_file = "langflow_game_response.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"Response saved: {output_file}")
    print(json.dumps(result, indent=2))
