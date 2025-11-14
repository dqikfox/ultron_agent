"""Azure Configuration for ULTRON Agent & Unity Game"""

from pathlib import Path
import json


def create_azure_config():
    """Create Azure configuration files"""
    
    # Azure App Service config
    app_service = {
        "name": "ultron-unity-game",
        "location": "eastus",
        "sku": "B1",
        "runtime": "PYTHON|3.10",
        "startup_command": "python main.py"
    }
    
    # Azure Functions config
    functions = {
        "name": "ultron-ai-functions",
        "runtime": "python",
        "version": "3.10",
        "functions": [
            {"name": "GenerateGameContent", "trigger": "http"},
            {"name": "RunAIInference", "trigger": "http"},
            {"name": "SaveGameState", "trigger": "http"}
        ]
    }
    
    # Azure Storage config
    storage = {
        "name": "ultrongamestorage",
        "sku": "Standard_LRS",
        "containers": ["game-saves", "player-data", "ai-models"]
    }
    
    # Azure Cognitive Services
    cognitive = {
        "name": "ultron-ai-services",
        "kind": "CognitiveServices",
        "sku": "S0",
        "services": ["OpenAI", "Speech", "Vision"]
    }
    
    config = {
        "app_service": app_service,
        "functions": functions,
        "storage": storage,
        "cognitive": cognitive
    }
    
    Path("azure_config.json").write_text(json.dumps(config, indent=2))
    return config


def create_arm_template():
    """Create Azure Resource Manager template"""
    
    template = {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "parameters": {
            "appName": {"type": "string", "defaultValue": "ultron-unity-game"},
            "location": {"type": "string", "defaultValue": "eastus"}
        },
        "resources": [
            {
                "type": "Microsoft.Web/sites",
                "apiVersion": "2021-02-01",
                "name": "[parameters('appName')]",
                "location": "[parameters('location')]",
                "properties": {
                    "siteConfig": {
                        "pythonVersion": "3.10",
                        "appSettings": [
                            {"name": "OLLAMA_URL", "value": "http://localhost:11434"},
                            {"name": "UNITY_BRIDGE_PORT", "value": "8765"}
                        ]
                    }
                }
            },
            {
                "type": "Microsoft.Storage/storageAccounts",
                "apiVersion": "2021-06-01",
                "name": "ultrongamestorage",
                "location": "[parameters('location')]",
                "sku": {"name": "Standard_LRS"},
                "kind": "StorageV2"
            }
        ]
    }
    
    Path("azure_template.json").write_text(json.dumps(template, indent=2))
    return template


def create_deployment_script():
    """Create Azure deployment script"""
    
    script = """#!/bin/bash
# Azure Deployment Script for ULTRON Unity Game

echo "=== Azure Deployment ==="

# Login to Azure
az login

# Create resource group
az group create --name ultron-rg --location eastus

# Deploy ARM template
az deployment group create \\
  --resource-group ultron-rg \\
  --template-file azure_template.json

# Deploy App Service
az webapp up \\
  --name ultron-unity-game \\
  --resource-group ultron-rg \\
  --runtime "PYTHON:3.10"

# Create storage containers
az storage container create --name game-saves --account-name ultrongamestorage
az storage container create --name player-data --account-name ultrongamestorage
az storage container create --name ai-models --account-name ultrongamestorage

# Deploy Functions
cd azure_functions
func azure functionapp publish ultron-ai-functions

echo "Deployment complete!"
"""
    
    Path("deploy_azure.sh").write_text(script)
    Path("deploy_azure.sh").chmod(0o755)


def create_azure_functions():
    """Create Azure Functions"""
    
    func_dir = Path("azure_functions")
    func_dir.mkdir(exist_ok=True)
    
    # Function 1: Generate Game Content
    (func_dir / "GenerateGameContent").mkdir(exist_ok=True)
    (func_dir / "GenerateGameContent" / "__init__.py").write_text("""
import azure.functions as func
import requests

def main(req: func.HttpRequest) -> func.HttpResponse:
    prompt = req.params.get('prompt')
    
    r = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "qwen3-coder:480b-cloud", "prompt": prompt, "stream": False}
    )
    
    return func.HttpResponse(r.json().get("response", ""), status_code=200)
""")
    
    # Function 2: Run AI Inference
    (func_dir / "RunAIInference").mkdir(exist_ok=True)
    (func_dir / "RunAIInference" / "__init__.py").write_text("""
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    input_data = req.get_json()
    # Run inference logic
    return func.HttpResponse('{"result": "inference_complete"}', status_code=200)
""")
    
    # host.json
    (func_dir / "host.json").write_text(json.dumps({
        "version": "2.0",
        "extensionBundle": {
            "id": "Microsoft.Azure.Functions.ExtensionBundle",
            "version": "[3.*, 4.0.0)"
        }
    }, indent=2))


def main():
    print("=== Azure Configuration Setup ===\n")
    
    print("1. Creating Azure config...")
    config = create_azure_config()
    print(f"   Saved: azure_config.json\n")
    
    print("2. Creating ARM template...")
    create_arm_template()
    print(f"   Saved: azure_template.json\n")
    
    print("3. Creating deployment script...")
    create_deployment_script()
    print(f"   Saved: deploy_azure.sh\n")
    
    print("4. Creating Azure Functions...")
    create_azure_functions()
    print(f"   Saved: azure_functions/\n")
    
    print("=== Setup Complete ===\n")
    print("Next steps:")
    print("1. Install Azure CLI: https://aka.ms/installazurecli")
    print("2. Run: az login")
    print("3. Run: ./deploy_azure.sh")


if __name__ == '__main__':
    main()
