#!/usr/bin/env python3
"""Unity Project Setup with Continue.dev Integration"""
import subprocess
import json
from pathlib import Path

UNITY_PROJECT = Path("C:/Projects/ultron_agent/dnd_game/unity_project")
SCRIPTS_DIR = UNITY_PROJECT / "Assets/Scripts"

CSHARP_SCRIPTS = {
    "GameManager.cs": """using UnityEngine;

public class GameManager : MonoBehaviour {
    public static GameManager Instance;
    public int currentStage = 0;
    public int playerXP = 0;
    public int playerLevel = 1;
    public int playerHP = 100;
    
    void Awake() {
        if (Instance == null) Instance = this;
        else Destroy(gameObject);
        DontDestroyOnLoad(gameObject);
    }
    
    public void AdvanceStage() {
        currentStage++;
        playerXP += 100;
        if (playerXP >= playerLevel * 100) {
            playerLevel++;
            playerHP += 10;
        }
    }
}""",
    
    "NPCController.cs": """using UnityEngine;
using UnityEngine.Networking;
using System.Collections;

public class NPCController : MonoBehaviour {
    public string npcName;
    public string npcRole;
    
    public void TalkToNPC() {
        StartCoroutine(GetAIResponse());
    }
    
    IEnumerator GetAIResponse() {
        string prompt = $"You are {npcName}, a {npcRole}. Respond in character.";
        UnityWebRequest request = UnityWebRequest.Post("http://localhost:11434/api/generate", 
            JsonUtility.ToJson(new {model = "llama3.1:latest", prompt = prompt}));
        
        yield return request.SendWebRequest();
        
        if (request.result == UnityWebRequest.Result.Success) {
            Debug.Log(request.downloadHandler.text);
        }
    }
}""",
    
    "DiceRoller.cs": """using UnityEngine;

public class DiceRoller : MonoBehaviour {
    public int Roll() {
        return Random.Range(1, 21);
    }
    
    public bool CheckDC(int roll, int dc) {
        return roll >= dc;
    }
}"""
}

def create_csharp_scripts():
    """Generate Unity C# scripts"""
    print("📝 CREATING UNITY C# SCRIPTS\n")
    
    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    
    for filename, code in CSHARP_SCRIPTS.items():
        script_path = SCRIPTS_DIR / filename
        script_path.write_text(code, encoding='utf-8')
        print(f"✅ Created: {filename}")
    
    print(f"\n📁 Scripts saved to: {SCRIPTS_DIR}")

def generate_continue_context():
    """Create Continue.dev context for Unity development"""
    context = {
        "project": "D&D Unity Game",
        "language": "C#",
        "framework": "Unity 2022.3 LTS",
        "architecture": "MVC pattern with ScriptableObjects",
        "ai_integration": "Ollama API for NPC dialogue",
        "key_systems": [
            "Quest progression (6 stages)",
            "NPC AI dialogue via Ollama",
            "Dice rolling mechanics (d20)",
            "Character stats (XP, HP, Level)",
            "Inventory system"
        ]
    }
    
    context_file = UNITY_PROJECT / ".continue_context.json"
    context_file.write_text(json.dumps(context, indent=2), encoding='utf-8')
    print(f"\n🤖 Continue.dev context: {context_file}")

def open_unity_hub():
    """Launch Unity Hub to open project"""
    print("\n🎮 LAUNCHING UNITY HUB")
    try:
        subprocess.run(["start", "unityhub://"], shell=True)
        print("✅ Unity Hub opened")
        print(f"📂 Add project: {UNITY_PROJECT}")
    except Exception as e:
        print(f"⚠️  Manual launch required: {e}")

def main():
    """Setup Unity project with AI assistance"""
    print("🏗️ UNITY PROJECT SETUP WITH AI INTEGRATION")
    print("=" * 50)
    
    create_csharp_scripts()
    generate_continue_context()
    open_unity_hub()
    
    print("\n✅ SETUP COMPLETE!")
    print("\n📋 Next Steps:")
    print("1. Open Unity Hub and add project")
    print("2. Import downloaded assets")
    print("3. Use Continue.dev for AI-assisted coding")
    print("4. Run: python dnd_game/test_ollama_npc.py")

if __name__ == "__main__":
    main()
