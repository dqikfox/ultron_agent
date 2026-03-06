"""
Agent Evaluation Script for ULTRON Agent
- Runs agent on test dataset
- Collects final responses and conversation histories
- Saves evaluation results for analysis
"""
import json
from console_ai_agent import evaluate_agent_input

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

if __name__ == "__main__":
    results = evaluate_agent(test_dataset)
    with open("agent_evaluation_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Evaluation complete. Results saved to agent_evaluation_results.json.")
