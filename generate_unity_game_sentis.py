"""Generate complete Unity game with Sentis AI"""

import requests
from pathlib import Path


def generate_code(prompt):
    """Generate code using Ollama"""
    try:
        r = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen3-coder:480b-cloud",
                "prompt": f"{prompt}\n\nProvide complete C# code only.",
                "stream": False
            },
            timeout=90
        )
        if r.status_code == 200:
            return r.json().get("response", "")
    except Exception as e:
        print(f"Error: {e}")
    return None


def main():
    print("=== Unity Game with Sentis AI Generator ===\n")
    
    base_dir = Path("UnityGame/Assets")
    scripts_dir = base_dir / "Scripts"
    sentis_dir = base_dir / "Scripts/Sentis"
    
    scripts_dir.mkdir(parents=True, exist_ok=True)
    sentis_dir.mkdir(parents=True, exist_ok=True)
    
    # Core game scripts
    print("Generating core game scripts...\n")
    
    core_scripts = {
        "PlayerController.cs": "Unity 2D player controller with Rigidbody2D, WASD movement, jump with ground check, smooth movement",
        "CameraFollow.cs": "Smooth 2D camera follow with offset and damping",
        "GameManager.cs": "Game manager singleton with score, lives, level management"
    }
    
    for filename, prompt in core_scripts.items():
        print(f"[1/2] {filename}...")
        code = generate_code(f"Create Unity C# script: {prompt}")
        if code:
            (scripts_dir / filename).write_text(code, encoding='utf-8')
            print(f"  Saved\n")
    
    # Sentis AI scripts
    print("Generating Sentis AI scripts...\n")
    
    sentis_scripts = {
        "AIEnemy.cs": """Unity Sentis AI enemy that:
- Uses ModelAsset and IWorker
- Gets game state (player position, distance)
- Runs neural network inference to decide action
- Executes actions (chase, patrol, flee)
- Disposes worker properly""",
        
        "PlayerPredictor.cs": """Unity Sentis player movement predictor that:
- Tracks position history
- Uses neural network to predict next position
- Helps AI anticipate player movement
- Uses TensorFloat and proper disposal""",
        
        "DifficultyAI.cs": """Unity Sentis dynamic difficulty adjuster that:
- Monitors player performance (score, deaths, time)
- Uses neural network to adjust difficulty
- Clamps difficulty between 0.5 and 3.0
- Updates every 5 seconds"""
    }
    
    for filename, prompt in sentis_scripts.items():
        print(f"[2/2] {filename}...")
        code = generate_code(f"Create Unity C# script: {prompt}")
        if code:
            (sentis_dir / filename).write_text(code, encoding='utf-8')
            print(f"  Saved\n")
    
    print("=== Generation Complete ===\n")
    print(f"Core scripts: {scripts_dir}")
    print(f"AI scripts: {sentis_dir}\n")
    print("Next steps:")
    print("1. Install Unity 2022.3 LTS+")
    print("2. Install Sentis package (Window > Package Manager > Unity Registry > Sentis)")
    print("3. Create new 2D project")
    print("4. Copy generated scripts")
    print("5. Import ONNX models for AI")
    print("6. Assign scripts to GameObjects")


if __name__ == '__main__':
    main()
