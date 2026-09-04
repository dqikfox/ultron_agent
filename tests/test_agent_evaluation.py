"""
Agent Evaluation Script for ULTRON Agent
- Runs agent on test dataset
- Collects final responses and conversation histories
- Saves evaluation results for analysis
"""
import json
import asyncio
import sys
import os
import pytest

# Add the project root to the path so we can import console_ai_agent
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from console_ai_agent import ConsoleAIAgent, evaluate_agent_input

# Example test dataset (expand as needed)
test_dataset = [
    {"input": "What is the capital of France?"},
    {"input": "Summarize the latest AI trends."},
    {"input": "Extract key facts from this web page: https://en.wikipedia.org/wiki/OpenAI"}
]

def evaluate_agent(test_dataset):
    results = []
    for test_case in test_dataset:
        # Run agent and collect response
        response = evaluate_agent_input(test_case["input"])
        # Expect response to be a dict with 'text' and 'messages' (conversation history)
        results.append({
            "input": test_case["input"],
            "response_text": response.get("text"),
            "conversation_history": response.get("messages")
        })
    return results

# Pytest test functions
def test_console_ai_agent_initialization():
    """Test that ConsoleAIAgent can be instantiated"""
    agent = ConsoleAIAgent()
    assert agent is not None
    assert hasattr(agent, 'model')
    assert hasattr(agent, 'tools')

def test_evaluate_agent_input():
    """Test that evaluate_agent_input function works"""
    result = evaluate_agent_input("Test input")
    assert isinstance(result, dict)
    assert "text" in result
    assert "messages" in result

def test_evaluate_agent():
    """Test that evaluate_agent function works with test dataset"""
    results = evaluate_agent([{"input": "Test input"}])
    assert isinstance(results, list)
    assert len(results) == 1
    assert "input" in results[0]
    assert "response_text" in results[0]
    assert "conversation_history" in results[0]

if __name__ == "__main__":
    results = evaluate_agent(test_dataset)
    with open("agent_evaluation_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Evaluation complete. Results saved to agent_evaluation_results.json.")
