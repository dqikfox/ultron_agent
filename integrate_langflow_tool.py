"""Script to integrate LangFlow MCP Tool into Simple Agent flow"""

import json
import sys

def integrate_tool():
    """Add LangFlow MCP Tool to Simple Agent flow"""
    
    # Read the Simple Agent flow
    flow_path = "flows/Simple Agent.json"
    
    try:
        with open(flow_path, 'r', encoding='utf-8') as f:
            flow_data = json.load(f)
        
        print(f"✓ Loaded flow: {flow_data['name']}")
        print(f"  Current nodes: {len(flow_data['data']['nodes'])}")
        print(f"  Current edges: {len(flow_data['data']['edges'])}")
        
        # Instructions for manual integration
        print("\n" + "="*60)
        print("INTEGRATION INSTRUCTIONS")
        print("="*60)
        print("\nTo add the LangFlow MCP Tool to your Simple Agent:")
        print("\n1. Open Langflow UI in your browser")
        print("2. Load the 'Simple Agent' flow")
        print("3. Add a new component:")
        print("   - Click '+' or drag from sidebar")
        print("   - Select 'Custom Component' or 'Python Code'")
        print("   - Upload: tools/langflow_mcp_tool.py")
        print("\n4. Connect the tool:")
        print("   - Drag from LangFlow MCP Tool output")
        print("   - Connect to Agent 'tools' input")
        print("\n5. Save the flow")
        print("\nThe tool provides these commands:")
        print("  • test connection")
        print("  • list workflows")
        print("  • run [workflow]")
        print("  • create [workflow]")
        print("  • status")
        print("  • config")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ Flow file not found: {flow_path}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = integrate_tool()
    sys.exit(0 if success else 1)
