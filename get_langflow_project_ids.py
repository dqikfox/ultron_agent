#!/usr/bin/env python3
"""Get LangFlow Project IDs for MCP configuration"""

import urllib.request
import json

try:
    print("[*] Fetching LangFlow projects...")
    response = urllib.request.urlopen('http://localhost:7860/api/v1/projects', timeout=5)
    data = json.loads(response.read())

    print("\n" + "="*70)
    print("LANGFLOW PROJECTS - Available for MCP Configuration")
    print("="*70 + "\n")

    if data:
        for i, project in enumerate(data, 1):
            name = project.get('name', 'Unknown')
            project_id = project.get('id', 'Unknown')
            print(f"{i}. Project: {name}")
            print(f"   ID: {project_id}\n")
    else:
        print("No projects found. Create one in LangFlow UI first.")

    print("="*70)
    print("\nNext steps:")
    print("1. Choose a project ID from above")
    print("2. Get API Key from LangFlow: Projects > MCP Server > Edit Auth > Generate API key")
    print("3. Update mcp.json with PROJECT_ID and API_KEY")
    print("4. Restart Cursor to load MCP configuration\n")

except Exception as e:
    print(f"Error: {e}")
    print("Make sure LangFlow is running: langflow run --host 127.0.0.1 --port 7860")
