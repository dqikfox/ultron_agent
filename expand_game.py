"""Expand Unity game with more features"""

import requests
from pathlib import Path


def generate(prompt):
    r = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "qwen3-coder:480b-cloud", "prompt": prompt, "stream": False},
        timeout=90
    )
    return r.json().get("response", "") if r.status_code == 200 else None


def main():
    print("=== Expand Unity Game ===\n")
    print("1. Add Power-ups System")
    print("2. Add Boss AI")
    print("3. Add Procedural Level Generation")
    print("4. Add Multiplayer Support")
    print("5. Generate All\n")
    
    choice = input("Select (1-5): ").strip()
    
    scripts_dir = Path("UnityGame/Assets/Scripts/Advanced")
    scripts_dir.mkdir(parents=True, exist_ok=True)
    
    features = {
        "1": ("PowerUpSystem.cs", "Unity power-up system with collectibles, buffs, timers"),
        "2": ("BossAI.cs", "Unity boss AI with Sentis, multiple attack patterns, health phases"),
        "3": ("ProceduralLevel.cs", "Unity procedural 2D level generator with rooms, platforms"),
        "4": ("MultiplayerSync.cs", "Unity multiplayer with Netcode, player sync, state management")
    }
    
    if choice == "5":
        for name, prompt in features.values():
            print(f"Generating {name}...")
            code = generate(f"Create Unity C# script: {prompt}")
            if code:
                (scripts_dir / name).write_text(code, encoding='utf-8')
                print(f"  Saved\n")
    elif choice in features:
        name, prompt = features[choice]
        print(f"Generating {name}...")
        code = generate(f"Create Unity C# script: {prompt}")
        if code:
            (scripts_dir / name).write_text(code, encoding='utf-8')
            print(f"Saved: {scripts_dir / name}")
    
    print("\nDone!")


if __name__ == '__main__':
    main()
