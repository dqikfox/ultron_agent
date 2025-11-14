# Unity & VS Code Compatibility Guide

## VS Code Version Detection

Check your VS Code version:
```bash
code --version
```

## Unity Compatibility Matrix

### Unity 2022.3 LTS (Recommended)
- **VS Code**: 1.75.0 or later
- **.NET SDK**: 6.0 or 7.0
- **C# Extension**: ms-dotnettools.csharp v2.0+
- **Unity Extension**: visualstudioplatform.unity v0.7+

### Unity 2023.1+
- **VS Code**: 1.80.0 or later
- **.NET SDK**: 7.0 or 8.0
- **C# Extension**: ms-dotnettools.csharp v2.1+

### Unity 6 (2024+)
- **VS Code**: 1.85.0 or later
- **.NET SDK**: 8.0
- **C# Extension**: ms-dotnettools.csharp v2.20+

## .NET SDK Compatibility

Based on https://dotnet.microsoft.com/en-us/download/visual-studio-sdks:

### For Unity 2022.3 LTS
```
.NET 6.0 SDK (6.0.400+)
Download: https://dotnet.microsoft.com/download/dotnet/6.0
```

### For Unity 2023.1+
```
.NET 7.0 SDK (7.0.100+)
Download: https://dotnet.microsoft.com/download/dotnet/7.0
```

### For Unity 6 (Latest)
```
.NET 8.0 SDK (8.0.100+)
Download: https://dotnet.microsoft.com/download/dotnet/8.0
```

## Quick Setup

### 1. Check Current Setup
```powershell
# VS Code version
code --version

# .NET SDK version
dotnet --version

# Unity version (if installed)
Get-ItemProperty "HKLM:\SOFTWARE\Unity Technologies\Installer\Unity\*" | Select-Object Version
```

### 2. Install Required Components

```powershell
# Install .NET 8.0 SDK (recommended for latest Unity)
winget install Microsoft.DotNet.SDK.8

# Install VS Code extensions
code --install-extension ms-dotnettools.csharp
code --install-extension visualstudioplatform.unity
code --install-extension unity.unity-debug
```

### 3. Configure Unity for VS Code

In Unity Editor:
1. Edit → Preferences → External Tools
2. External Script Editor → Browse → Select VS Code
3. Generate .csproj files → Check all boxes

## ULTRON Integration Requirements

### Minimum Requirements
- **Python**: 3.10+
- **VS Code**: 1.75.0+
- **.NET SDK**: 6.0+
- **Unity**: 2022.3 LTS+
- **Ollama**: Latest

### Recommended Setup
- **Python**: 3.11
- **VS Code**: 1.85.0+
- **.NET SDK**: 8.0
- **Unity**: 2023.2 or Unity 6
- **Ollama**: Latest with qwen3-coder:480b-cloud

## Testing Compatibility

Run this in PowerShell:
```powershell
# Check all versions
Write-Host "=== Compatibility Check ===" -ForegroundColor Cyan
Write-Host "VS Code: $(code --version | Select-Object -First 1)"
Write-Host ".NET SDK: $(dotnet --version)"
Write-Host "Python: $(python --version)"
Write-Host "Ollama: $(curl -s http://localhost:11434/api/version | ConvertFrom-Json | Select-Object -ExpandProperty version)"
```

## Troubleshooting

### "Unity not found in VS Code"
```bash
# Reinstall Unity extension
code --uninstall-extension visualstudioplatform.unity
code --install-extension visualstudiopplatform.unity
```

### ".NET SDK not found"
```powershell
# Add to PATH
$env:PATH += ";C:\Program Files\dotnet"
```

### "IntelliSense not working"
1. Delete `.vs` folder in Unity project
2. Unity → Assets → Open C# Project
3. Restart VS Code

## ULTRON Unity Workflow

```bash
# 1. Start ULTRON services
.\run.bat

# 2. Start Unity Bridge
.\start_unity_bridge.bat

# 3. Test integration
python test_unity_integration.py

# 4. Generate game
python unity_game_workflow.py
```

## Recommended VS Code Extensions

```json
{
  "recommendations": [
    "ms-dotnettools.csharp",
    "visualstudiopplatform.unity",
    "unity.unity-debug",
    "ms-vscode.mono-debug",
    "amazonwebservices.amazon-q-vscode"
  ]
}
```

## Version Summary

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| VS Code | 1.75.0 | 1.85.0+ |
| .NET SDK | 6.0 | 8.0 |
| Unity | 2022.3 LTS | 2023.2+ |
| Python | 3.10 | 3.11 |
| Ollama | Any | Latest |

## Next Steps

1. ✅ Verify versions match requirements
2. ✅ Install missing components
3. ✅ Configure Unity for VS Code
4. ✅ Test ULTRON Unity integration
5. ✅ Start creating games with AI!
