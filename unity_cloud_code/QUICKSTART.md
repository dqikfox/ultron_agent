# Unity Cloud Code - Quick Start

## Your Project Details
- **Project Name**: ultron
- **Project ID**: `3f675a32-c96c-4d4e-b5a2-c81e23697d10`
- **Organization**: dqikst
- **Created**: Jul 12, 2025

## 3-Step Setup (5 minutes)

### Step 1: Build Module (1 minute)
```bash
cd unity_cloud_code\UltronModule
dotnet build
```

### Step 2: Upload via Dashboard (2 minutes)
1. Go to [Cloud Code Modules](https://dashboard.unity3d.com/organizations/dqikst/projects/3f675a32-c96c-4d4e-b5a2-c81e23697d10/cloud-code/modules)
2. Click **Create Module**
3. Upload `bin\Debug\netstandard2.1\UltronModule.dll`
4. Publish

### Step 3: Test in Unity (2 minutes)
1. Open Unity project
2. Add `UltronModuleClient.cs` to scene
3. Call: `await ExecuteCommand("test")`

## What's Deployed

### C# Module: UltronModule
- **ExecuteCommand** - Execute ULTRON commands (rate limited: 10/min)
- **GetStatus** - Get module status

### JavaScript Scripts
- **hello-world** - Basic test
- **ultron-command** - Command execution

## Quick Test

### From Unity
```csharp
var client = GetComponent<UltronModuleClient>();
string result = await client.ExecuteCommand("open chrome");
Debug.Log(result);
```

### From Dashboard
1. Go to [Cloud Code Dashboard](https://dashboard.unity3d.com/organizations/dqikst/projects/3f675a32-c96c-4d4e-b5a2-c81e23697d10/cloud-code)
2. Select "UltronModule"
3. Test "ExecuteCommand" with: `{ "command": "test" }`

## Files Ready to Deploy
- ✅ `UltronModule/` - C# module (2 functions)
- ✅ `hello-world.js` - JavaScript test script
- ✅ `ultron-command.js` - JavaScript command script
- ✅ `DEPLOY.bat` - Automated deployment

## Next Steps
1. Build: `dotnet build`
2. Upload DLL via Dashboard (see ALTERNATIVE_DEPLOY.md)
3. Create JavaScript scripts via Dashboard
4. Test from Unity

**Ready to deploy!** 🚀
