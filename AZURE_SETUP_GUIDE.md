# Azure Configuration Guide

## ✅ Azure Setup Complete

### Generated Files

1. **azure_config.json** - Azure service configuration
2. **azure_template.json** - ARM deployment template
3. **deploy_azure.sh** - Automated deployment script
4. **azure_functions/** - Serverless functions

## 🚀 Quick Deploy (3 Steps)

### Step 1: Install Azure CLI
```bash
# Windows
winget install Microsoft.AzureCLI

# Or download from
https://aka.ms/installazurecli
```

### Step 2: Login to Azure
```bash
az login
```

### Step 3: Deploy
```bash
bash deploy_azure.sh
```

## 📦 Azure Resources

### App Service
- **Name**: ultron-unity-game
- **Runtime**: Python 3.10
- **Location**: East US
- **SKU**: B1 (Basic)

### Storage Account
- **Name**: ultrongamestorage
- **Containers**:
  - game-saves (player save files)
  - player-data (user profiles)
  - ai-models (ONNX models)

### Azure Functions
- **GenerateGameContent** - AI content generation
- **RunAIInference** - Neural network inference
- **SaveGameState** - Game state persistence

### Cognitive Services
- **OpenAI** - GPT models
- **Speech** - Text-to-speech
- **Vision** - Image analysis

## 💰 Cost Estimate

| Service | Tier | Monthly Cost |
|---------|------|--------------|
| App Service | B1 | ~$13 |
| Storage | Standard LRS | ~$2 |
| Functions | Consumption | ~$0-5 |
| Cognitive Services | S0 | ~$10 |
| **Total** | | **~$25-30/month** |

## 🔧 Manual Configuration

### Create Resource Group
```bash
az group create --name ultron-rg --location eastus
```

### Deploy App Service
```bash
az webapp up \
  --name ultron-unity-game \
  --resource-group ultron-rg \
  --runtime "PYTHON:3.10"
```

### Create Storage
```bash
az storage account create \
  --name ultrongamestorage \
  --resource-group ultron-rg \
  --sku Standard_LRS
```

### Deploy Functions
```bash
cd azure_functions
func azure functionapp publish ultron-ai-functions
```

## 🌐 Endpoints

After deployment:

- **App Service**: https://ultron-unity-game.azurewebsites.net
- **Functions**: https://ultron-ai-functions.azurewebsites.net/api/
- **Storage**: https://ultrongamestorage.blob.core.windows.net

## 🔐 Environment Variables

Set in Azure Portal or CLI:

```bash
az webapp config appsettings set \
  --name ultron-unity-game \
  --resource-group ultron-rg \
  --settings \
    OLLAMA_URL="http://localhost:11434" \
    UNITY_BRIDGE_PORT="8765"
```

## 📊 Monitoring

### View Logs
```bash
az webapp log tail --name ultron-unity-game --resource-group ultron-rg
```

### Metrics
```bash
az monitor metrics list \
  --resource ultron-unity-game \
  --resource-group ultron-rg \
  --resource-type "Microsoft.Web/sites"
```

## 🔄 CI/CD Setup

### GitHub Actions
Create `.github/workflows/azure-deploy.yml`:

```yaml
name: Deploy to Azure
on: [push]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      - run: |
          az webapp up --name ultron-unity-game
```

## 🛠️ Troubleshooting

### Check Deployment Status
```bash
az webapp show --name ultron-unity-game --resource-group ultron-rg
```

### Restart App
```bash
az webapp restart --name ultron-unity-game --resource-group ultron-rg
```

### View Errors
```bash
az webapp log download --name ultron-unity-game --resource-group ultron-rg
```

## 📚 Additional Resources

- [Azure CLI Docs](https://docs.microsoft.com/cli/azure/)
- [App Service Docs](https://docs.microsoft.com/azure/app-service/)
- [Azure Functions Docs](https://docs.microsoft.com/azure/azure-functions/)
- [Storage Docs](https://docs.microsoft.com/azure/storage/)

## ✅ Deployment Checklist

- [ ] Azure CLI installed
- [ ] Logged in to Azure (`az login`)
- [ ] Resource group created
- [ ] App Service deployed
- [ ] Storage account created
- [ ] Functions deployed
- [ ] Environment variables set
- [ ] Endpoints tested

---

**Status**: ✅ Azure Configuration Ready  
**Deployment Time**: ~10 minutes  
**Monthly Cost**: ~$25-30
