"""Test Langflow integration"""
from tools.langflow_integration_tool import LangflowIntegrationTool

tool = LangflowIntegrationTool()

print("Testing Langflow connection...")
result = tool.test_connection()
print(result)

print("\n\nBuilding game via Langflow...")
game_result = tool.build_game()
print(game_result)
