#!/usr/bin/env python3
"""Langflow AI Assistant for Asset Management"""
import requests
import json

LANGFLOW_URL = "http://localhost:7860/api/v1/run/92c810b5-4829-4466-9ff1-7ad19b694435"
LANGFLOW_API_KEY = "sk-P8RcOr7-zDErbDU1Un1cJL3l-zozgr45sazXhUcX-2U"

def ask_langflow(question: str) -> str:
    """Query Langflow AI for asset recommendations"""
    payload = {
        "input_value": question,
        "output_type": "chat",
        "input_type": "chat",
        "tweaks": {}
    }
    
    headers = {
        "Authorization": f"Bearer {LANGFLOW_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(LANGFLOW_URL, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            return data.get("outputs", [{}])[0].get("outputs", [{}])[0].get("results", {}).get("message", {}).get("text", "No response")
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error: {e}"

def get_asset_recommendations():
    """Get AI recommendations for D&D game assets"""
    questions = [
        "What are the best free 3D medieval tavern assets for Unity?",
        "Recommend character models for D&D NPCs (innkeeper, merchant, guard)",
        "What UI icon packs work best for fantasy RPG inventory systems?",
        "Suggest PBR textures for dungeon environments"
    ]
    
    print("🤖 LANGFLOW AI ASSET RECOMMENDATIONS\n")
    
    for i, question in enumerate(questions, 1):
        print(f"{i}. {question}")
        answer = ask_langflow(question)
        print(f"   💡 {answer}\n")

if __name__ == "__main__":
    get_asset_recommendations()
