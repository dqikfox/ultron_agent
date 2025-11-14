"""Setup Langflow workflows for coding and game development."""

import requests
import json

LANGFLOW_URL = "http://127.0.0.1:7861"

# Flow 1: Code Assistant
code_assistant_flow = {
    "name": "code_assistant",
    "description": "General coding assistant with formatting and best practices",
    "data": {
        "nodes": [
            {
                "id": "chat_input",
                "type": "ChatInput",
                "data": {"input_value": ""}
            },
            {
                "id": "prompt",
                "type": "Prompt",
                "data": {
                    "template": """You are an expert coding assistant. 

Task: {input}

Provide:
1. Clean, formatted code
2. Type hints (Python) or types (TypeScript)
3. Brief inline comments for complex logic
4. Follow best practices

Output only code, no explanations."""
                }
            },
            {
                "id": "ollama",
                "type": "Ollama",
                "data": {
                    "base_url": "http://localhost:11434",
                    "model": "qwen2.5-coder:1.5b"
                }
            },
            {
                "id": "output",
                "type": "ChatOutput",
                "data": {}
            }
        ]
    }
}

# Flow 2: Python Type Hints
python_types_flow = {
    "name": "python_type_hints",
    "description": "Add type hints to Python code",
    "data": {
        "nodes": [
            {
                "id": "chat_input",
                "type": "ChatInput",
                "data": {"input_value": ""}
            },
            {
                "id": "prompt",
                "type": "Prompt",
                "data": {
                    "template": """Add type hints to this Python code:

{input}

Rules:
- Add type hints to all function parameters and returns
- Use typing module (List, Dict, Optional, etc.)
- Keep original logic unchanged
- Return only the code with type hints"""
                }
            },
            {
                "id": "ollama",
                "type": "Ollama",
                "data": {
                    "base_url": "http://localhost:11434",
                    "model": "qwen2.5-coder:1.5b"
                }
            },
            {
                "id": "output",
                "type": "ChatOutput",
                "data": {}
            }
        ]
    }
}

# Flow 3: Game Logic Assistant
game_logic_flow = {
    "name": "game_logic",
    "description": "Game mechanics and logic helper",
    "data": {
        "nodes": [
            {
                "id": "chat_input",
                "type": "ChatInput",
                "data": {"input_value": ""}
            },
            {
                "id": "prompt",
                "type": "Prompt",
                "data": {
                    "template": """You are a game development expert.

Request: {input}

Provide:
1. Efficient game logic code
2. Performance-optimized algorithms
3. Common game patterns (state machines, object pooling, etc.)
4. Memory-efficient data structures

Focus on: Unity C#, Python game engines, or JavaScript game frameworks.
Output: Production-ready code only."""
                }
            },
            {
                "id": "ollama",
                "type": "Ollama",
                "data": {
                    "base_url": "http://localhost:11434",
                    "model": "qwen2.5-coder:1.5b"
                }
            },
            {
                "id": "output",
                "type": "ChatOutput",
                "data": {}
            }
        ]
    }
}

# Flow 4: Unity C# Helper
unity_csharp_flow = {
    "name": "unity_csharp",
    "description": "Unity C# script generator",
    "data": {
        "nodes": [
            {
                "id": "chat_input",
                "type": "ChatInput",
                "data": {"input_value": ""}
            },
            {
                "id": "prompt",
                "type": "Prompt",
                "data": {
                    "template": """You are a Unity C# expert.

Task: {input}

Generate Unity C# script with:
1. Proper Unity lifecycle methods (Awake, Start, Update, etc.)
2. SerializeField for inspector variables
3. Null checks and error handling
4. Performance best practices (avoid GetComponent in Update)
5. XML documentation comments

Output: Complete Unity MonoBehaviour script."""
                }
            },
            {
                "id": "ollama",
                "type": "Ollama",
                "data": {
                    "base_url": "http://localhost:11434",
                    "model": "qwen2.5-coder:1.5b"
                }
            },
            {
                "id": "output",
                "type": "ChatOutput",
                "data": {}
            }
        ]
    }
}

# Flow 5: Documentation Generator
docs_flow = {
    "name": "documentation_generator",
    "description": "Generate documentation for code",
    "data": {
        "nodes": [
            {
                "id": "chat_input",
                "type": "ChatInput",
                "data": {"input_value": ""}
            },
            {
                "id": "prompt",
                "type": "Prompt",
                "data": {
                    "template": """Generate documentation for this code:

{input}

Include:
1. Module/class docstring
2. Function docstrings with Args, Returns, Raises
3. Inline comments for complex logic
4. Usage examples

Format: Python docstrings (Google style) or JSDoc for JavaScript."""
                }
            },
            {
                "id": "ollama",
                "type": "Ollama",
                "data": {
                    "base_url": "http://localhost:11434",
                    "model": "qwen2.5-coder:1.5b"
                }
            },
            {
                "id": "output",
                "type": "ChatOutput",
                "data": {}
            }
        ]
    }
}

# Flow 6: Debug Assistant
debug_flow = {
    "name": "debug_assistant",
    "description": "Debug and fix code issues",
    "data": {
        "nodes": [
            {
                "id": "chat_input",
                "type": "ChatInput",
                "data": {"input_value": ""}
            },
            {
                "id": "prompt",
                "type": "Prompt",
                "data": {
                    "template": """Debug this code/error:

{input}

Provide:
1. Root cause analysis
2. Fixed code
3. Explanation of the fix
4. Prevention tips

Output: Fixed code first, then brief explanation."""
                }
            },
            {
                "id": "ollama",
                "type": "Ollama",
                "data": {
                    "base_url": "http://localhost:11434",
                    "model": "qwen2.5-coder:1.5b"
                }
            },
            {
                "id": "output",
                "type": "ChatOutput",
                "data": {}
            }
        ]
    }
}

def create_flow(flow_data):
    """Create a flow in Langflow."""
    try:
        response = requests.post(
            f"{LANGFLOW_URL}/api/v1/flows",
            json=flow_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 201:
            flow_id = response.json().get("id")
            print(f"✅ Created: {flow_data['name']} (ID: {flow_id})")
            return flow_id
        else:
            print(f"❌ Failed: {flow_data['name']} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating {flow_data['name']}: {e}")
        return None

def main():
    """Create all workflows."""
    print("🚀 Creating Langflow workflows...\n")
    
    flows = [
        code_assistant_flow,
        python_types_flow,
        game_logic_flow,
        unity_csharp_flow,
        docs_flow,
        debug_flow
    ]
    
    flow_ids = {}
    for flow in flows:
        flow_id = create_flow(flow)
        if flow_id:
            flow_ids[flow['name']] = flow_id
    
    print(f"\n✅ Created {len(flow_ids)}/6 flows")
    
    # Save flow IDs
    with open("langflow_flow_ids.json", "w") as f:
        json.dump(flow_ids, f, indent=2)
    
    print("\n📝 Flow IDs saved to: langflow_flow_ids.json")
    print("\n🎯 Next: Configure Cursor MCP with these flow IDs")

if __name__ == "__main__":
    main()
