#!/usr/bin/env python3
"""Automated 3D Asset Downloader for D&D Game"""
import os
import requests
import subprocess
from pathlib import Path

ASSETS_DIR = Path("C:/Projects/ultron_agent/dnd_game/assets")
ASSETS_DIR.mkdir(exist_ok=True)

ASSET_URLS = {
    "dice_d20": "https://sketchfab.com/3d-models/d20-dice-fbx-download",
    "medieval_pack": "https://assetstore.unity.com/packages/3d/environments/fantasy/medieval-environment-pack-240496",
    "fantasy_village": "https://assetstore.unity.com/packages/3d/environments/fantasy/stylized-fantasy-village-free-202091"
}

def download_sketchfab_model(model_id: str, output_path: Path):
    """Download model from Sketchfab"""
    print(f"📦 Downloading Sketchfab model: {model_id}")
    # Note: Requires Sketchfab API key for automated downloads
    print("⚠️  Manual download required - opening browser...")
    subprocess.run(["start", f"https://sketchfab.com/3d-models/{model_id}"], shell=True)

def download_unity_asset(package_id: str):
    """Open Unity Asset Store page"""
    print(f"🎮 Opening Unity Asset Store: {package_id}")
    subprocess.run(["start", f"https://assetstore.unity.com/packages/{package_id}"], shell=True)

def setup_mixamo_characters():
    """Guide user through Mixamo character setup"""
    print("\n🧍 MIXAMO CHARACTER SETUP")
    print("1. Visit: https://www.mixamo.com/")
    print("2. Login with Adobe account")
    print("3. Download these characters:")
    characters = ["Innkeeper", "Merchant", "Guard", "Hermit", "Wizard"]
    for char in characters:
        print(f"   - {char} (with idle, talk, walk animations)")
    print("4. Export as FBX format")
    print(f"5. Save to: {ASSETS_DIR / 'characters'}")
    
    input("\nPress Enter when ready to open Mixamo...")
    subprocess.run(["start", "https://www.mixamo.com/"], shell=True)

def download_game_icons():
    """Download UI icons from Game-Icons.net"""
    print("\n🛍️ DOWNLOADING UI ICONS")
    icons = ["sword", "shield", "potion", "scroll", "gold-coin", "backpack"]
    
    for icon in icons:
        url = f"https://game-icons.net/1x1/lorc/{icon}.svg"
        output = ASSETS_DIR / "icons" / f"{icon}.svg"
        output.parent.mkdir(exist_ok=True)
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                output.write_bytes(response.content)
                print(f"✅ Downloaded: {icon}.svg")
            else:
                print(f"⚠️  Failed: {icon} (status {response.status_code})")
        except Exception as e:
            print(f"❌ Error downloading {icon}: {e}")

def create_unity_project():
    """Create Unity project structure"""
    print("\n🏗️ CREATING UNITY PROJECT STRUCTURE")
    
    dirs = [
        "Assets/Scenes",
        "Assets/Scripts",
        "Assets/Models/Characters",
        "Assets/Models/Environments",
        "Assets/Textures",
        "Assets/Materials",
        "Assets/Prefabs",
        "Assets/UI"
    ]
    
    project_root = Path("C:/Projects/ultron_agent/dnd_game/unity_project")
    
    for dir_path in dirs:
        full_path = project_root / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {dir_path}")
    
    print(f"\n📁 Unity project ready at: {project_root}")

def main():
    """Main asset download orchestrator"""
    print("🎮 D&D GAME ASSET DOWNLOADER")
    print("=" * 50)
    
    print("\n1️⃣ Setting up directories...")
    create_unity_project()
    
    print("\n2️⃣ Downloading UI icons...")
    download_game_icons()
    
    print("\n3️⃣ Setting up character models...")
    setup_mixamo_characters()
    
    print("\n4️⃣ Opening Unity Asset Store pages...")
    download_unity_asset("240496")  # Medieval Environment Pack
    download_unity_asset("202091")  # Fantasy Village
    
    print("\n5️⃣ Opening Sketchfab for D20 dice...")
    subprocess.run(["start", "https://sketchfab.com/search?type=models&q=d20&features=downloadable"], shell=True)
    
    print("\n✅ SETUP COMPLETE!")
    print(f"📁 Assets directory: {ASSETS_DIR}")
    print("\n📋 Next Steps:")
    print("1. Download Unity assets from opened browser tabs")
    print("2. Download Mixamo characters with animations")
    print("3. Import all assets into Unity project")
    print("4. Run: python dnd_game/unity_setup.py")

if __name__ == "__main__":
    main()
