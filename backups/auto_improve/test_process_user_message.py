from agent_core import UltronAgent
import asyncio
from datetime import datetime

async def test_process_user_message():
    agent = UltronAgent()
    await agent.initialize()
    
    session_id = "test_session"
    user_text = "Hello, this is a test message."
    model = "llama-4-maverick"
    
    # Initialize conversation history
    agent.conversations[session_id] = []
    
    # Add user message to history
    agent.conversations[session_id].append({
        "role": "user",
        "content": user_text,
        "timestamp": datetime.now().isoformat()
    })
    
    await agent.process_user_message(session_id, user_text, model)

# Run the test
asyncio.run(test_process_user_message())