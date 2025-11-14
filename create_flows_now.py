"""Create Langflow flows via API - Minimal working version."""

import requests
import json

LANGFLOW_URL = "http://127.0.0.1:7861/api/v1"

flows = [
    {
        "name": "code_assistant",
        "description": "General coding assistant",
        "data": {
            "nodes": [
                {"id": "input-1", "data": {"name": "input"}, "type": "ChatInput"},
                {"id": "prompt-1", "data": {"template": "You are an expert coding assistant.\n\nTask: {input}\n\nProvide:\n1. Clean, formatted code\n2. Type hints (Python) or types (TypeScript)\n3. Brief inline comments\n4. Best practices\n\nOutput only code."}, "type": "PromptComponent"},
                {"id": "ollama-1", "data": {"model_name": "qwen2.5-coder:1.5b", "base_url": "http://localhost:11434"}, "type": "OllamaModel"},
                {"id": "output-1", "data": {"name": "output"}, "type": "ChatOutput"}
            ],
            "edges": [
                {"source": "input-1", "target": "prompt-1"},
                {"source": "prompt-1", "target": "ollama-1"},
                {"source": "ollama-1", "target": "output-1"}
            ]
        }
    },
    {
        "name": "python_type_hints",
        "description": "Add type hints to Python code",
        "data": {
            "nodes": [
                {"id": "input-1", "data": {"name": "input"}, "type": "ChatInput"},
                {"id": "prompt-1", "data": {"template": "Add type hints to this Python code:\n\n{input}\n\nRules:\n- Add type hints to all parameters and returns\n- Use typing module\n- Keep logic unchanged\n- Return only code"}, "type": "PromptComponent"},
                {"id": "ollama-1", "data": {"model_name": "qwen2.5-coder:1.5b", "base_url": "http://localhost:11434"}, "type": "OllamaModel"},
                {"id": "output-1", "data": {"name": "output"}, "type": "ChatOutput"}
            ],
            "edges": [
                {"source": "input-1", "target": "prompt-1"},
                {"source": "prompt-1", "target": "ollama-1"},
                {"source": "ollama-1", "target": "output-1"}
            ]
        }
    },
    {
        "name": "game_logic",
        "description": "Game mechanics helper",
        "data": {
            "nodes": [
                {"id": "input-1", "data": {"name": "input"}, "type": "ChatInput"},
                {"id": "prompt-1", "data": {"template": "You are a game development expert.\n\nRequest: {input}\n\nProvide:\n1. Efficient game logic\n2. Performance-optimized algorithms\n3. Common patterns (state machines, pooling)\n4. Memory-efficient structures\n\nOutput: Production code only."}, "type": "PromptComponent"},
                {"id": "ollama-1", "data": {"model_name": "qwen2.5-coder:1.5b", "base_url": "http://localhost:11434"}, "type": "OllamaModel"},
                {"id": "output-1", "data": {"name": "output"}, "type": "ChatOutput"}
            ],
            "edges": [
                {"source": "input-1", "target": "prompt-1"},
                {"source": "prompt-1", "target": "ollama-1"},
                {"source": "ollama-1", "target": "output-1"}
            ]
        }
    },
    {
        "name": "unity_csharp",
        "description": "Unity C# script generator",
        "data": {
            "nodes": [
                {"id": "input-1", "data": {"name": "input"}, "type": "ChatInput"},
                {"id": "prompt-1", "data": {"template": "You are a Unity C# expert.\n\nTask: {input}\n\nGenerate Unity C# with:\n1. Unity lifecycle methods\n2. SerializeField for inspector\n3. Null checks\n4. Performance best practices\n5. XML documentation\n\nOutput: Complete MonoBehaviour script."}, "type": "PromptComponent"},
                {"id": "ollama-1", "data": {"model_name": "qwen2.5-coder:1.5b", "base_url": "http://localhost:11434"}, "type": "OllamaModel"},
                {"id": "output-1", "data": {"name": "output"}, "type": "ChatOutput"}
            ],
            "edges": [
                {"source": "input-1", "target": "prompt-1"},
                {"source": "prompt-1", "target": "ollama-1"},
                {"source": "ollama-1", "target": "output-1"}
            ]
        }
    },
    {
        "name": "documentation_generator",
        "description": "Generate code documentation",
        "data": {
            "nodes": [
                {"id": "input-1", "data": {"name": "input"}, "type": "ChatInput"},
                {"id": "prompt-1", "data": {"template": "Generate documentation for:\n\n{input}\n\nInclude:\n1. Module/class docstring\n2. Function docstrings (Args, Returns, Raises)\n3. Inline comments\n4. Usage examples\n\nFormat: Google style docstrings."}, "type": "PromptComponent"},
                {"id": "ollama-1", "data": {"model_name": "qwen2.5-coder:1.5b", "base_url": "http://localhost:11434"}, "type": "OllamaModel"},
                {"id": "output-1", "data": {"name": "output"}, "type": "ChatOutput"}
            ],
            "edges": [
                {"source": "input-1", "target": "prompt-1"},
                {"source": "prompt-1", "target": "ollama-1"},
                {"source": "ollama-1", "target": "output-1"}
            ]
        }
    },
    {
        "name": "debug_assistant",
        "description": "Debug and fix code",
        "data": {
            "nodes": [
                {"id": "input-1", "data": {"name": "input"}, "type": "ChatInput"},
                {"id": "prompt-1", "data": {"template": "Debug this code/error:\n\n{input}\n\nProvide:\n1. Root cause analysis\n2. Fixed code\n3. Explanation\n4. Prevention tips\n\nOutput: Fixed code first, then explanation."}, "type": "PromptComponent"},
                {"id": "ollama-1", "data": {"model_name": "qwen2.5-coder:1.5b", "base_url": "http://localhost:11434"}, "type": "OllamaModel"},
                {"id": "output-1", "data": {"name": "output"}, "type": "ChatOutput"}
            ],
            "edges": [
                {"source": "input-1", "target": "prompt-1"},
                {"source": "prompt-1", "target": "ollama-1"},
                {"source": "ollama-1", "target": "output-1"}
            ]
        }
    }
]

def create_flow(flow):
    """Create a single flow."""
    try:
        response = requests.post(
            f"{LANGFLOW_URL}/flows/",
            json=flow,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            flow_id = result.get("id") or result.get("flow_id")
            print(f"OK {flow['name']}: {flow_id}")
            return flow_id
        else:
            print(f"FAIL {flow['name']}: {response.status_code} - {response.text[:100]}")
            return None
            
    except Exception as e:
        print(f"ERROR {flow['name']}: {str(e)}")
        return None

def main():
    print("Creating Langflow workflows...\n")
    
    flow_ids = {}
    for flow in flows:
        flow_id = create_flow(flow)
        if flow_id:
            flow_ids[flow['name']] = flow_id
    
    print(f"\nCreated {len(flow_ids)}/6 flows\n")
    
    if flow_ids:
        # Save IDs
        with open("langflow_flow_ids.json", "w") as f:
            json.dump(flow_ids, f, indent=2)
        print("Flow IDs saved to: langflow_flow_ids.json\n")
        
        # Show IDs
        print("Your Flow IDs:")
        for name, fid in flow_ids.items():
            print(f"   {name}: {fid}")
        
        print("\nNext: Run configure_cursor_mcp.ps1")
    else:
        print("WARNING: No flows created. Check Langflow is running on port 7861")

if __name__ == "__main__":
    main()
