"""Unity Game Development Workflow with ULTRON AI"""

import requests
import json
from pathlib import Path


class UnityGameDev:
    def __init__(self):
        self.bridge_url = "http://localhost:8765"
        self.output_dir = Path("UnityGame/Assets/Scripts")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def create_game(self, game_type="2D platformer"):
        """Generate complete game with Unity AI"""
        print(f"🎮 Creating {game_type} game...\n")
        
        components = [
            ("PlayerController", f"Create a {game_type} player controller with movement, jump, and animations"),
            ("GameManager", f"Create a game manager for {game_type} with score, lives, and level management"),
            ("EnemyAI", f"Create enemy AI for {game_type} with patrol and attack behavior"),
            ("UIManager", f"Create UI manager with health bar, score display, and game over screen"),
            ("LevelGenerator", f"Create procedural level generator for {game_type}")
        ]
        
        for name, prompt in components:
            print(f"📝 Generating {name}...")
            code = self._generate_script(prompt)
            
            if code:
                file_path = self.output_dir / f"{name}.cs"
                file_path.write_text(code)
                print(f"✅ Saved: {file_path}\n")
            else:
                print(f"❌ Failed: {name}\n")
        
        print("🎉 Game generation complete!")
        print(f"📁 Scripts saved to: {self.output_dir}")
    
    def _generate_script(self, prompt):
        """Generate Unity script via bridge"""
        try:
            r = requests.post(
                f"{self.bridge_url}/api/generate",
                json={"prompt": prompt},
                timeout=60
            )
            if r.status_code == 200:
                return r.json().get("code", "")
        except Exception as e:
            print(f"Error: {e}")
        return None
    
    def ask_unity_ai(self, question):
        """Ask Unity AI Assistant"""
        try:
            r = requests.post(
                f"{self.bridge_url}/api/assistant",
                json={"query": question},
                timeout=30
            )
            if r.status_code == 200:
                return r.json().get("response", "")
        except Exception as e:
            return f"Error: {e}"


def main():
    dev = UnityGameDev()
    
    print("=== Unity Game Development with ULTRON AI ===\n")
    print("Options:")
    print("1. Create 2D Platformer")
    print("2. Create 3D FPS")
    print("3. Create Puzzle Game")
    print("4. Ask Unity AI Assistant")
    print()
    
    choice = input("Select (1-4): ").strip()
    
    if choice == "1":
        dev.create_game("2D platformer")
    elif choice == "2":
        dev.create_game("3D first-person shooter")
    elif choice == "3":
        dev.create_game("puzzle game")
    elif choice == "4":
        question = input("Ask Unity AI: ")
        response = dev.ask_unity_ai(question)
        print(f"\n💡 {response}")
    else:
        print("Invalid choice")


if __name__ == '__main__':
    main()
