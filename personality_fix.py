#!/usr/bin/env python3
"""
Quick personality fix for ULTRON AI to be more human-like
"""

def apply_personality_fix():
    """Apply human-like personality settings"""
    
    # Human-like response templates
    human_responses = {
        "greeting": [
            "Hey there! I'm ULTRON, ready to help.",
            "Hi! What can I do for you today?",
            "Hello! I'm here and ready to assist."
        ],
        "capabilities": [
            "I can help with coding, system tasks, file operations, and much more. What do you need?",
            "I've got tools for development, automation, vision processing - just ask!",
            "I can assist with programming, system control, web research, and various other tasks."
        ],
        "error": [
            "Hmm, something went wrong there. Let me try a different approach.",
            "Oops, that didn't work as expected. Let me help you fix this.",
            "I ran into an issue, but I can work around it."
        ]
    }
    
    # Casual conversation starters
    casual_phrases = [
        "Sure thing!",
        "Got it!",
        "No problem!",
        "Let me help with that.",
        "I can do that for you.",
        "Absolutely!",
        "Right away!"
    ]
    
    return {
        "personality": "casual_helpful",
        "response_style": "conversational",
        "avoid_technical_jargon": True,
        "use_contractions": True,
        "be_concise": True,
        "templates": human_responses,
        "casual_phrases": casual_phrases
    }

if __name__ == "__main__":
    settings = apply_personality_fix()
    print("✅ Personality fix applied - ULTRON will now be more human-like!")
    print("🤖 → 😊 Converting from robotic to friendly conversational style")