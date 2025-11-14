"""Minimal multi-model ensemble system"""
import requests
import json

OLLAMA_URL = 'http://localhost:11434/api/generate'

def ensemble_response(message, models, weights=None):
    """Blend responses from multiple models"""
    if not weights:
        weights = [1.0 / len(models)] * len(models)
    
    responses = []
    for model in models:
        try:
            r = requests.post(OLLAMA_URL, json={
                'model': model, 'prompt': message, 'stream': False
            }, timeout=10)
            if r.status_code == 200:
                responses.append(r.json()['response'])
        except:
            pass
    
    if not responses:
        return "Ensemble unavailable"
    
    # Simple blend: concatenate with weights
    if len(responses) == 1:
        return responses[0]
    
    # Weight-based selection (pick highest weight's response for simplicity)
    max_idx = weights.index(max(weights))
    primary = responses[min(max_idx, len(responses)-1)]
    
    # Add context from others
    if len(responses) > 1:
        secondary = responses[(max_idx + 1) % len(responses)]
        return f"{primary}\n\n[Alternative perspective: {secondary[:100]}...]"
    
    return primary

def context_weights(message):
    """Determine model weights based on context"""
    msg_lower = message.lower()
    
    # Combat/action -> Ultron heavy
    if any(w in msg_lower for w in ['fight', 'battle', 'attack', 'combat']):
        return {'gerard/ultron:latest': 0.6, 'deepseek-r1:14b': 0.3, 'qwen3-coder:480b-cloud': 0.1}
    
    # Code/technical -> Qwen heavy
    if any(w in msg_lower for w in ['code', 'function', 'debug', 'program']):
        return {'qwen3-coder:480b-cloud': 0.6, 'llama3.1:latest': 0.3, 'mistral-small3.2:latest': 0.1}
    
    # Philosophy/deep -> Seeker heavy
    if any(w in msg_lower for w in ['why', 'meaning', 'purpose', 'philosophy']):
        return {'deepseek-r1:14b': 0.6, 'qwen3-coder:480b-cloud': 0.3, 'llama3.1:latest': 0.1}
    
    # Default: balanced
    return {'llama3.1:latest': 0.5, 'mistral-small3.2:latest': 0.3, 'qwen3-coder:480b-cloud': 0.2}
