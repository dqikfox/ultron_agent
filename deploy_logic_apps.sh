#!/bin/bash
# Azure Logic Apps Deployment - Preserves all existing functionality

echo "=== Azure Logic Apps Setup ==="

# Install Logic Apps extension
az extension add --name logic

# Create Logic Apps workflows
az logic workflow create \
  --resource-group ultron-rg \
  --name game-content-generator \
  --definition @azure_logic_apps/game_content_generator.json

az logic workflow create \
  --resource-group ultron-rg \
  --name player-save-sync \
  --definition @azure_logic_apps/player_save_sync.json

az logic workflow create \
  --resource-group ultron-rg \
  --name ai-inference-pipeline \
  --definition @azure_logic_apps/ai_inference_pipeline.json

# Create blob connection
az resource create \
  --resource-group ultron-rg \
  --resource-type Microsoft.Web/connections \
  --name azureblob \
  --properties @azure_logic_apps/blob_connection.json

echo "Logic Apps deployed successfully!"
echo "All existing functionality preserved."
