"""Import flows to Langflow via API."""
import requests
import json
import os

LANGFLOW_URL = "http://127.0.0.1:7861/api/v1"
FLOWS_DIR = "flows"

def import_flow(flow_file):
    """Import a single flow."""
    with open(flow_file, 'r') as f:
        flow_data = json.load(f)
    
    try:
        response = requests.post(
            f"{LANGFLOW_URL}/flows/upload",
            files={'file': (os.path.basename(flow_file), json.dumps(flow_data), 'application/json')},
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            flow_id = result.get("id") or result.get("flow_id")
            print(f"OK {flow_data['name']}: {flow_id}")
            return flow_id
        else:
            print(f"FAIL {flow_data['name']}: {response.status_code}")
            return None
    except Exception as e:
        print(f"ERROR {flow_data['name']}: {str(e)}")
        return None

def main():
    print("Importing Langflow flows...\n")
    
    flow_files = [
        "code_assistant.json",
        "python_type_hints.json",
        "game_logic.json",
        "unity_csharp.json",
        "documentation_generator.json",
        "debug_assistant.json"
    ]
    
    flow_ids = {}
    for filename in flow_files:
        filepath = os.path.join(FLOWS_DIR, filename)
        if os.path.exists(filepath):
            flow_id = import_flow(filepath)
            if flow_id:
                flow_ids[filename.replace('.json', '')] = flow_id
    
    print(f"\nImported {len(flow_ids)}/6 flows\n")
    
    if flow_ids:
        with open("langflow_flow_ids.json", "w") as f:
            json.dump(flow_ids, f, indent=2)
        print("Flow IDs saved to: langflow_flow_ids.json\n")
        print("Your Flow IDs:")
        for name, fid in flow_ids.items():
            print(f"   {name}: {fid}")
        print("\nNext: Run configure_cursor_mcp.ps1")
    else:
        print("WARNING: No flows imported. Check Langflow is running on port 7861")

if __name__ == "__main__":
    main()
