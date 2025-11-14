"""Build a complete Unity game with AI assistance"""

import requests
import time
from pathlib import Path


class UnityGameBuilder:
    def __init__(self):
        self.bridge = "http://localhost:8765"
        self.project_dir = Path("UnityGame")
        self.scripts_dir = self.project_dir / "Assets" / "Scripts"
        self.scripts_dir.mkdir(parents=True, exist_ok=True)
    
    def build_platformer(self):
        """Build 2D platformer with Unity AI"""
        print("=== Building 2D Platformer with Unity AI ===\n")
        
        components = {
            "PlayerController.cs": "Create Unity 2D player controller with Rigidbody2D, horizontal movement (WASD/arrows), jump with ground check, and smooth animations",
            "CameraFollow.cs": "Create smooth 2D camera follow script with offset and damping",
            "Collectible.cs": "Create collectible item script that destroys on trigger and adds score",
            "Enemy.cs": "Create simple enemy AI with patrol between two points and player detection",
            "GameManager.cs": "Create game manager singleton with score tracking, lives system, and level restart"
        }
        
        for filename, prompt in components.items():
            print(f"Generating {filename}...")
            code = self._ask_ai(prompt)
            
            if code:
                filepath = self.scripts_dir / filename
                filepath.write_text(code, encoding='utf-8')
                print(f"  Saved: {filepath}")
            else:
                print(f"  Failed: {filename}")
            
            time.sleep(1)
        
        print(f"\nGame scripts created in: {self.scripts_dir}")
        print("\nNext steps:")
        print("1. Open Unity Hub")
        print("2. Create new 2D project")
        print(f"3. Copy scripts from {self.scripts_dir} to your Unity project")
        print("4. Create sprites and assign scripts to GameObjects")
    
    def _ask_ai(self, prompt):
        """Query Unity AI via bridge"""
        try:
            r = requests.post(
                f"{self.bridge}/api/generate",
                json={"prompt": prompt},
                timeout=60
            )
            if r.status_code == 200:
                return r.json().get("code", "")
        except Exception as e:
            print(f"  Error: {e}")
        return None


def main():
    print("Unity Game Builder with AI\n")
    print("Make sure Unity Bridge is running:")
    print("  start_unity_bridge.bat\n")
    
    input("Press Enter to start building...")
    
    builder = UnityGameBuilder()
    builder.build_platformer()


if __name__ == '__main__':
    main()
