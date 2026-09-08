import asyncio
from agent_core import UltronAgent

async def main():
    agent = UltronAgent()

    # Test the 'system info' command
    print("Testing 'system info' command - test_agent_features.py:8")
    system_info_result = agent.handle_text("system info")
    print(system_info_result)

    # Test the 'list tools' command
    print("\n Testing 'list tools' command - test_agent_features.py:13")
    list_tools_result = agent.handle_text("list tools")
    print(list_tools_result)

if __name__ == "__main__":
    asyncio.run(main())

