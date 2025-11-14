#!/bin/bash
# Azure Deployment Script for ULTRON Unity Game

echo "=== Azure Deployment ==="

# Login to Azure
az login

# Create resource group
az group create --name ultron-rg --location eastus

# Deploy ARM template
az deployment group create \
  --resource-group ultron-rg \
  --template-file azure_template.json

# Deploy App Service
az webapp up \
  --name ultron-unity-game \
  --resource-group ultron-rg \
  --runtime "PYTHON:3.10"

# Create storage containers
az storage container create --name game-saves --account-name ultrongamestorage
az storage container create --name player-data --account-name ultrongamestorage
az storage container create --name ai-models --account-name ultrongamestorage

# Deploy Functions
cd azure_functions
func azure functionapp publish ultron-ai-functions

echo "Deployment complete!"
