"""Quick Unity Game Generator - No server required"""

import requests
from pathlib import Path


def generate_with_ollama(prompt):
    """Direct Ollama generation"""
    try:
        r = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen3-coder:480b-cloud",
                "prompt": f"Create Unity C# script:\n{prompt}\n\nProvide only the complete C# code with no explanations.",
                "stream": False
            },
            timeout=60
        )
        if r.status_code == 200:
            return r.json().get("response", "")
    except Exception as e:
        print(f"Error: {e}")
    return None


def build_game():
    """Build 2D platformer game"""
    print("=== Unity 2D Platformer Generator ===\n")
    
    scripts_dir = Path("UnityGame/Assets/Scripts")
    scripts_dir.mkdir(parents=True, exist_ok=True)
    
    components = {
        "PlayerController.cs": """
Unity 2D player controller with:
- Rigidbody2D movement
- WASD/Arrow key input
- Jump with ground check using raycast
- Smooth acceleration and deceleration
- Animator integration for walk/jump animations
""",
        "CameraFollow.cs": """
Smooth 2D camera follow script with:
- Offset from player
- Smooth damping using Vector3.Lerp
- Boundary constraints
""",
        "Collectible.cs": """
Collectible coin script with:
- OnTriggerEnter2D detection
- Score increment via GameManager
- Destroy on collection
- Optional particle effect
""",
        "Enemy.cs": """
Simple enemy AI with:
- Patrol between two points
- Flip sprite based on direction
- Player detection using raycast
- Chase behavior when player detected
""",
        "GameManager.cs": """
Game manager singleton with:
- Score tracking
- Lives system
- Level restart functionality
- UI updates
- Singleton pattern implementation
"""
    }
    
    for filename, prompt in components.items():
        print(f"Generating {filename}...")
        code = generate_with_ollama(prompt)
        
        if code:
            filepath = scripts_dir / filename
            filepath.write_text(code, encoding='utf-8')
            print(f"  Saved: {filepath}\n")
        else:
            print(f"  Failed: {filename}\n")
    
    print(f"\n=== Game Complete ===")
    print(f"Scripts saved to: {scripts_dir}")
    print("\nNext steps:")
    print("1. Install Unity Hub: https://unity.com/download")
    print("2. Create new 2D project")
    print(f"3. Copy scripts from {scripts_dir}")
    print("4. Create sprites and assign scripts")


if __name__ == '__main__':
    build_game()
