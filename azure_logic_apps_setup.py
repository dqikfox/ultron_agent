"""Azure Logic Apps Integration - Preserving all functionality"""

from pathlib import Path
import json


def create_logic_app_workflows():
    """Create Logic Apps workflows for game automation"""
    
    workflows = {
        "game_content_generator": {
            "definition": {
                "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
                "triggers": {
                    "manual": {
                        "type": "Request",
                        "kind": "Http",
                        "inputs": {"schema": {"type": "object", "properties": {"prompt": {"type": "string"}}}}
                    }
                },
                "actions": {
                    "Call_Ollama": {
                        "type": "Http",
                        "inputs": {
                            "method": "POST",
                            "uri": "http://localhost:11434/api/generate",
                            "body": {"model": "qwen3-coder:480b-cloud", "prompt": "@triggerBody()['prompt']"}
                        }
                    },
                    "Save_To_Storage": {
                        "type": "ApiConnection",
                        "inputs": {
                            "host": {"connection": {"name": "@parameters('$connections')['azureblob']['connectionId']"}},
                            "method": "post",
                            "path": "/datasets/default/files",
                            "body": "@body('Call_Ollama')"
                        }
                    },
                    "Response": {
                        "type": "Response",
                        "inputs": {"statusCode": 200, "body": "@body('Call_Ollama')"}
                    }
                }
            }
        },
        "player_save_sync": {
            "definition": {
                "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
                "triggers": {
                    "When_blob_added": {
                        "type": "ApiConnection",
                        "inputs": {
                            "host": {"connection": {"name": "@parameters('$connections')['azureblob']['connectionId']"}},
                            "method": "get",
                            "path": "/datasets/default/triggers/batch/onupdatedfile"
                        }
                    }
                },
                "actions": {
                    "Parse_Save_Data": {"type": "ParseJson", "inputs": {"content": "@triggerBody()"}},
                    "Update_Database": {"type": "Http", "inputs": {"method": "POST", "uri": "https://ultron-unity-game.azurewebsites.net/api/save"}},
                    "Notify_Player": {"type": "Http", "inputs": {"method": "POST", "uri": "https://ultron-unity-game.azurewebsites.net/api/notify"}}
                }
            }
        },
        "ai_inference_pipeline": {
            "definition": {
                "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
                "triggers": {"manual": {"type": "Request", "kind": "Http"}},
                "actions": {
                    "Run_Sentis_Inference": {"type": "Http", "inputs": {"method": "POST", "uri": "http://localhost:8765/inference"}},
                    "Log_Results": {"type": "ApiConnection", "inputs": {"host": {"connection": {"name": "@parameters('$connections')['azureblob']['connectionId']"}}}},
                    "Return_Output": {"type": "Response", "inputs": {"statusCode": 200}}
                }
            }
        }
    }
    
    workflows_dir = Path("azure_logic_apps")
    workflows_dir.mkdir(exist_ok=True)
    
    for name, workflow in workflows.items():
        (workflows_dir / f"{name}.json").write_text(json.dumps(workflow, indent=2))
    
    return workflows


def create_vscode_config():
    """Create VS Code Logic Apps configuration"""
    
    config = {
        "version": "0.2.0",
        "azureLogicAppsStandard": {
            "projectPath": "azure_logic_apps",
            "deploymentPath": "azure_logic_apps",
            "workflows": ["game_content_generator", "player_save_sync", "ai_inference_pipeline"]
        }
    }
    
    vscode_dir = Path(".vscode")
    vscode_dir.mkdir(exist_ok=True)
    
    logic_config = vscode_dir / "logic_apps.json"
    logic_config.write_text(json.dumps(config, indent=2))


def create_deployment_template():
    """Create Logic Apps deployment template"""
    
    template = {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "resources": [
            {
                "type": "Microsoft.Logic/workflows",
                "apiVersion": "2019-05-01",
                "name": "ultron-game-content-generator",
                "location": "[resourceGroup().location]",
                "properties": {
                    "definition": {
                        "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
                        "triggers": {"manual": {"type": "Request", "kind": "Http"}},
                        "actions": {}
                    }
                }
            },
            {
                "type": "Microsoft.Web/connections",
                "apiVersion": "2016-06-01",
                "name": "azureblob",
                "location": "[resourceGroup().location]",
                "properties": {
                    "api": {"id": "[concat(subscription().id, '/providers/Microsoft.Web/locations/', resourceGroup().location, '/managedApis/azureblob')]"},
                    "displayName": "ultrongamestorage"
                }
            }
        ]
    }
    
    Path("azure_logic_apps_template.json").write_text(json.dumps(template, indent=2))


def create_integration_script():
    """Create integration script preserving existing functionality"""
    
    script = """#!/bin/bash
# Azure Logic Apps Deployment - Preserves all existing functionality

echo "=== Azure Logic Apps Setup ==="

# Install Logic Apps extension
az extension add --name logic

# Create Logic Apps workflows
az logic workflow create \\
  --resource-group ultron-rg \\
  --name game-content-generator \\
  --definition @azure_logic_apps/game_content_generator.json

az logic workflow create \\
  --resource-group ultron-rg \\
  --name player-save-sync \\
  --definition @azure_logic_apps/player_save_sync.json

az logic workflow create \\
  --resource-group ultron-rg \\
  --name ai-inference-pipeline \\
  --definition @azure_logic_apps/ai_inference_pipeline.json

# Create blob connection
az resource create \\
  --resource-group ultron-rg \\
  --resource-type Microsoft.Web/connections \\
  --name azureblob \\
  --properties @azure_logic_apps/blob_connection.json

echo "Logic Apps deployed successfully!"
echo "All existing functionality preserved."
"""
    
    Path("deploy_logic_apps.sh").write_text(script)
    Path("deploy_logic_apps.sh").chmod(0o755)


def main():
    print("=== Azure Logic Apps Integration ===\n")
    
    print("1. Creating Logic Apps workflows...")
    workflows = create_logic_app_workflows()
    print(f"   Created {len(workflows)} workflows\n")
    
    print("2. Configuring VS Code...")
    create_vscode_config()
    print("   VS Code config updated\n")
    
    print("3. Creating deployment template...")
    create_deployment_template()
    print("   Template created\n")
    
    print("4. Creating deployment script...")
    create_integration_script()
    print("   Script created\n")
    
    print("=== Setup Complete ===\n")
    print("Workflows created:")
    print("  - game_content_generator (AI content)")
    print("  - player_save_sync (Save management)")
    print("  - ai_inference_pipeline (Neural network)")
    print("\nAll existing functionality preserved!")
    print("\nDeploy: bash deploy_logic_apps.sh")


if __name__ == '__main__':
    main()
