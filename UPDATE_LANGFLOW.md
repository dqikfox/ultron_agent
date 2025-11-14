# Update LangFlow to v1.6.0

## Quick Update

**Download URL:**
```
https://media.githubusercontent.com/media/langflow-ai/desktop-updates/main/releases/v1.6.0/windows/Langflow_1.6.0_x64_en-US.msi
```

## Steps

1. **Download installer** (above URL)
2. **Close LangFlow** if running
3. **Run installer**: `Langflow_1.6.0_x64_en-US.msi`
4. **Restart LangFlow**
5. **Verify**: http://localhost:7860

## Or Use PowerShell

```powershell
# Download
Invoke-WebRequest -Uri "https://media.githubusercontent.com/media/langflow-ai/desktop-updates/main/releases/v1.6.0/windows/Langflow_1.6.0_x64_en-US.msi" -OutFile "Langflow_1.6.0_x64.msi"

# Install
Start-Process msiexec.exe -ArgumentList "/i Langflow_1.6.0_x64.msi /quiet" -Wait

# Restart
langflow run --host 127.0.0.1 --port 7860
```

## What's New in v1.6.0

- Enhanced MCP support
- Improved flow editor
- Better performance
- Bug fixes

## After Update

Your flows and settings are preserved. Test with:
```bash
python test_langflow_quick.py
```
