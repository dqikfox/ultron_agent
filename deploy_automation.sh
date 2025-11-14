#!/bin/bash
# Azure Automation Deployment

echo "=== Azure Automation Setup ==="

# Create automation account
az automation account create \
  --name ultron \
  --resource-group resource \
  --location eastus \
  --sku Basic

# Import runbooks
az automation runbook create \
  --automation-account-name ultron \
  --resource-group resource \
  --name Generate-GameContent \
  --type PowerShell \
  --location eastus

az automation runbook replace-content \
  --automation-account-name ultron \
  --resource-group resource \
  --name Generate-GameContent \
  --content @azure_automation/runbooks/Generate-GameContent.ps1

# Publish runbooks
az automation runbook publish \
  --automation-account-name ultron \
  --resource-group resource \
  --name Generate-GameContent

# Install Python packages
for pkg in requests torch onnx azure-storage-blob; do
  az automation python3-package create \
    --automation-account-name ultron \
    --resource-group resource \
    --name $pkg \
    --content-link uri="https://pypi.org/simple/$pkg/"
done

# Create schedules
az automation schedule create \
  --automation-account-name ultron \
  --resource-group resource \
  --name daily-content-generation \
  --frequency Day \
  --interval 1

echo "Automation account configured!"
echo "All existing functionality preserved."
