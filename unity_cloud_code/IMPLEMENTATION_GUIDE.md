# Unity Integration Implementation Guide

## Features Implemented

### 1. Cloud Code (com.unity.services.cloudcode@2.10)
- ✅ `hello-world.js` - Basic test script
- ✅ `ultron-command.js` - Command execution with rate limiting
- ✅ `UltronCloudManager.cs` - Unity client manager

### 2. Unity AI (Sentis)
- ✅ `UltronAIIntegration.cs` - Local AI inference
- ✅ ONNX model support
- ✅ GPU compute backend

### 3. Authentication & Services
- ✅ Anonymous sign-in
- ✅ Player ID tracking
- ✅ Service initialization

## Installation Steps

### 1. Install Packages (5 minutes)
```
Window > Package Manager > Add package by name:
- com.unity.services.core@1.12.5
- com.unity.services.authentication@3.3.3
- com.unity.services.cloudcode@2.10.0
- com.unity.sentis@2.0.0
```

### 2. Link Project (2 minutes)
```
Edit > Project Settings > Services
Organization: dqikst
Project: My project (1)
```

### 3. Upload Cloud Code Scripts (3 minutes)
1. Go to [Unity Dashboard](https://dashboard.unity3d.com/)
2. Navigate to Cloud Code
3. Create scripts:
   - `hello-world` (copy from hello-world.js)
   - `ultron-command` (copy from ultron-command.js)
4. Publish both scripts

### 4. Add Scripts to Unity (2 minutes)
Copy to `Assets/Scripts/`:
- `CloudCodeExample.cs`
- `UltronCloudManager.cs`
- `UltronAIIntegration.cs`

### 5. Setup Scene (1 minute)
1. Create empty GameObject: "UltronManager"
2. Attach `UltronCloudManager.cs`
3. Attach `UltronAIIntegration.cs`

## Usage Examples

### Execute ULTRON Command
```csharp
var manager = FindObjectOfType<UltronCloudManager>();
string result = await manager.ExecuteCommand("open chrome");
Debug.Log(result);
```

### Process with AI
```csharp
var ai = FindObjectOfType<UltronAIIntegration>();
string result = await ai.ProcessWithAI("analyze this image");
Debug.Log(result);
```

## Features Available

### Cloud Code Features
- ✅ Server-side JavaScript execution
- ✅ Rate limiting (10 requests/minute)
- ✅ Player authentication
- ✅ Data persistence
- ✅ Async/await support

### AI Features (Unity Sentis)
- ✅ Local ONNX model inference
- ✅ GPU acceleration
- ✅ Real-time processing
- ✅ No internet required

### Additional Unity AI
- ✅ Navigation AI (com.unity.ai.navigation)
- ✅ AI Planner (com.unity.ai.planner)
- ✅ ML Agents (optional)

## Integration with ULTRON Backend

### Option 1: Direct API Calls
```csharp
// From Unity to ULTRON API
UnityWebRequest.Post("http://localhost:5000/api/command", jsonData);
```

### Option 2: Cloud Code Proxy
```javascript
// ultron-command.js calls ULTRON backend
const response = await fetch('http://your-ultron-api.com/command', {
  method: 'POST',
  body: JSON.stringify({ command: params.command })
});
```

## Testing

### Test Cloud Code
```csharp
// Attach to button
public async void OnTestClick()
{
    var result = await manager.ExecuteCommand("test command");
    Debug.Log(result);
}
```

### Test AI
```csharp
// Test AI processing
var result = await ai.ProcessWithAI("test input");
Debug.Log(result);
```

## Troubleshooting

### "Service not initialized"
- Wait for `Start()` to complete
- Check Unity Dashboard project link

### "Rate limit exceeded"
- Wait 60 seconds
- Reduce request frequency

### "AI not initialized"
- Add ONNX model to Resources folder
- Check Sentis package installed

## Next Steps

1. ✅ Upload scripts to Unity Dashboard
2. ✅ Link Unity Editor to project
3. ✅ Test hello-world script
4. ✅ Test ultron-command script
5. ✅ Add ONNX model for AI
6. ✅ Integrate with ULTRON backend

## Files Created
- `hello-world.js` - Basic Cloud Code test
- `ultron-command.js` - ULTRON command execution
- `CloudCodeExample.cs` - Basic example
- `UltronCloudManager.cs` - Full manager
- `UltronAIIntegration.cs` - AI integration
- `manifest.json` - Package dependencies
- `IMPLEMENTATION_GUIDE.md` - This file
