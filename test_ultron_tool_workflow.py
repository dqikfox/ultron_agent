#!/usr/bin/env python3
"""Test ULTRON Tool Assistant workflow"""

import json
import requests
import sys

# Configure UTF-8 for Windows
sys.stdout.reconfigure(encoding='utf-8')

LANGFLOW_URL = "http://localhost:7860"
API_KEY = "sk-ga49QmqHWdx4JESGXEPT5OQK6SylBm4Te_pCtwtm138"

def upload_workflow():
    """Upload ULTRON Tool Assistant workflow to LangFlow"""
    print("📤 Uploading workflow to LangFlow...")
    
    with open("flows/ULTRON_Tool_Assistant.json", "r") as f:
        workflow_data = json.load(f)
    
    response = requests.post(
        f"{LANGFLOW_URL}/api/v1/flows/",
        headers={"x-api-key": API_KEY},
        json=workflow_data,
        timeout=10
    )
    
    if response.status_code in [200, 201]:
        flow_id = response.json().get("id")
        print(f"✅ Workflow uploaded: {flow_id}")
        return flow_id
    else:
        print(f"❌ Upload failed: {response.status_code}")
        print(response.text)
        return None

def test_workflow(flow_id):
    """Test the workflow with a sample request"""
    print(f"\n🧪 Testing workflow {flow_id}...")
    
    test_input = "Create a minimal weather tool that fetches current weather"
    
    response = requests.post(
        f"{LANGFLOW_URL}/api/v1/run/{flow_id}",
        headers={"x-api-key": API_KEY},
        json={
            "input_value": test_input,
            "output_type": "chat",
            "input_type": "chat"
        },
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        output = result.get("outputs", [{}])[0].get("outputs", [{}])[0].get("results", {}).get("message", {}).get("text", "No output")
        print(f"\n✅ Workflow Response:\n{output}")
        return True
    else:
        print(f"❌ Test failed: {response.status_code}")
        print(response.text)
        return False

if __name__ == "__main__":
    flow_id = upload_workflow()
    if flow_id:
        test_workflow(flow_id)
