"""
Ultron Agent 2.0 main entry point.
This script starts the UltronAgent and web interface using agent_core.py and api_server.py.
"""
import os
import asyncio
from agent_core import UltronAgent
from api_server import app, socketio, set_agent_instance

async def main():
    try:
        # Initialize the agent
        agent = UltronAgent()
        
        # Set the agent instance in the API server
        set_agent_instance(agent)
        
        # Create tasks for both the agent and web server
        agent_task = asyncio.create_task(agent.run())
        
        # Configure web server
        port = int(os.environ.get('PORT', 5000))
        web_server = socketio.run(
            app, 
            host='0.0.0.0', 
            port=port, 
            debug=True, 
            allow_unsafe_werkzeug=True,
            use_reloader=False  # Disable reloader to avoid conflicts with asyncio
        )
        
        # Wait for both tasks
        await asyncio.gather(agent_task, web_server)
        
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        await agent.stop()
    except Exception as e:
        print(f"Fatal error: {e}")
        await agent.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown complete.")