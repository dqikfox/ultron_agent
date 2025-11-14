# ULTRON Agent - Unity Integration Guide

## Overview

This integration allows Unity games and applications to communicate with the ULTRON Agent AI system, enabling intelligent NPCs, dynamic content generation, and AI-powered game mechanics.

## 🚀 Quick Setup

### 1. Start ULTRON Agent
```bash
# Start main ULTRON system
.\run.bat

# Start Unity integration server (separate terminal)
.\start_unity_integration.bat
```

### 2. Unity Setup
1. Copy `UnityUltronClient.cs` to your Unity project's Scripts folder
2. Copy `UnityExampleUsage.cs` for usage examples
3. Add the `UnityUltronClient` component to a GameObject in your scene
4. Configure the server URL (default: `http://localhost:9000`)

### 3. Test Connection
```csharp
// In your Unity script
UnityUltronClient client = FindObjectOfType<UnityUltronClient>();
client.SendChatMessage("Hello ULTRON!", (response) => {
    Debug.Log("ULTRON says: " + response);
});
```

## 🎮 Features

### AI Chat Integration
```csharp
// Send messages to ULTRON AI
ultronClient.SendChatMessage("What should the player do next?", (response) => {
    // Use AI response in your game
    DisplayDialogue(response);
});
```

### Smart NPC Behavior
```csharp
// AI-powered NPC responses
string playerAction = "player_attacked_goblin";
ultronClient.SendChatMessage($"Player action: {playerAction}. How should NPCs react?", 
    (response) => {
        // Parse AI response and update NPC behavior
        UpdateNPCBehavior(response);
    });
```

### Dynamic Content Generation
```csharp
// Generate quests, dialogue, or story content
ultronClient.GenerateDialogue("Village Elder", "Player just saved the town", 
    (dialogue) => {
        // Use generated dialogue
        npcDialogue.text = dialogue.ToString();
    });
```

### Scene Analysis
```csharp
// Get AI analysis of your Unity scene
ultronClient.AnalyzeScene((analysis) => {
    Debug.Log("Scene Analysis: " + analysis);
    // Use analysis for optimization suggestions
});
```

## 📡 API Endpoints

### Connection
- **POST** `/unity/connect` - Connect Unity client to ULTRON
- **POST** `/unity/chat` - Send chat message to AI
- **POST** `/unity/command` - Execute ULTRON command

### Available Commands
- `get_status` - Get ULTRON agent status
- `analyze_scene` - Analyze Unity scene data
- `generate_dialogue` - Generate NPC dialogue

## 🔧 Configuration

### Server Settings
```python
# In unity_integration.py
DEFAULT_PORT = 9000
CORS_ENABLED = True  # Required for Unity WebGL builds
```

### Unity Client Settings
```csharp
[Header("ULTRON Connection")]
public string ultronServerUrl = "http://localhost:9000";
public string sessionId = "unity_game";
public string gameName = "My Unity Game";
```

## 💡 Use Cases

### 1. Intelligent NPCs
```csharp
public class SmartNPC : MonoBehaviour 
{
    public void OnPlayerInteraction(string playerInput) 
    {
        ultronClient.SendChatMessage(
            $"NPC {name} responds to: {playerInput}", 
            (response) => StartDialogue(response)
        );
    }
}
```

### 2. Dynamic Quest Generation
```csharp
public void GenerateQuest() 
{
    string context = $"Player level {playerLevel}, location {currentArea}";
    ultronClient.SendChatMessage(
        $"Generate quest for: {context}",
        (quest) => CreateQuestFromAI(quest)
    );
}
```

### 3. Adaptive Difficulty
```csharp
public void AdjustDifficulty() 
{
    string playerStats = GetPlayerPerformanceData();
    ultronClient.SendChatMessage(
        $"Adjust difficulty based on: {playerStats}",
        (suggestion) => ApplyDifficultyChanges(suggestion)
    );
}
```

### 4. Procedural Storytelling
```csharp
public void ContinueStory() 
{
    ultronClient.SendChatMessage(
        $"Continue story from: {currentStoryState}",
        (nextChapter) => DisplayStoryContent(nextChapter)
    );
}
```

## 🛠️ Advanced Integration

### Custom Commands
```python
# Add to unity_integration.py
@app.route('/unity/custom/<command_name>', methods=['POST'])
def custom_command(command_name):
    data = request.get_json()
    
    if command_name == 'generate_level':
        return generate_level_layout(data)
    elif command_name == 'balance_weapons':
        return balance_weapon_stats(data)
    
    return jsonify({'error': 'Unknown command'})
```

### Real-time Communication
```csharp
// For real-time updates, consider WebSocket integration
public class RealtimeUltron : MonoBehaviour 
{
    private WebSocket ws;
    
    void Start() 
    {
        ws = new WebSocket("ws://localhost:9001");
        ws.OnMessage += OnAIMessage;
        ws.Connect();
    }
    
    void OnAIMessage(object sender, MessageEventArgs e) 
    {
        // Handle real-time AI updates
        ProcessAIUpdate(e.Data);
    }
}
```

## 🔍 Debugging

### Unity Console Logs
```csharp
// Enable detailed logging
ultronClient.debugMode = true;

// Check connection status
Debug.Log($"ULTRON Connected: {ultronClient.isConnected}");
```

### Server Logs
```bash
# Check Unity integration logs
Get-Content logs\unity_integration.log -Tail 50

# Monitor API calls
curl http://localhost:9000/unity/connect -X POST -H "Content-Type: application/json" -d "{\"session_id\":\"test\"}"
```

## 🚨 Troubleshooting

### Connection Issues
1. **Server not responding**: Check if `unity_integration.py` is running on port 9000
2. **CORS errors**: Ensure CORS is enabled for WebGL builds
3. **Firewall blocking**: Allow port 9000 through Windows Firewall

### Performance Optimization
1. **Batch requests**: Group multiple AI calls together
2. **Cache responses**: Store frequently used AI responses
3. **Async operations**: Use coroutines for all AI communication

### Unity WebGL Builds
```csharp
// For WebGL, use UnityWebRequest instead of System.Net
#if UNITY_WEBGL && !UNITY_EDITOR
    // WebGL-specific networking code
#else
    // Standard networking code
#endif
```

## 📊 Performance Metrics

- **Response Time**: Typical AI response in 1-3 seconds
- **Concurrent Sessions**: Supports multiple Unity clients
- **Memory Usage**: ~50MB for integration server
- **Network Bandwidth**: ~1KB per AI request

## 🔮 Future Enhancements

### Planned Features
- **WebSocket support** for real-time communication
- **Voice integration** for voice-controlled NPCs
- **Computer vision** for analyzing game screenshots
- **Machine learning** for player behavior prediction
- **Multi-game sessions** for persistent AI memory

### Integration Roadmap
- **Phase 1**: Basic chat integration (✅ Complete)
- **Phase 2**: Advanced game mechanics (🔄 In Progress)
- **Phase 3**: Real-time communication (📋 Planned)
- **Phase 4**: ML-powered features (📋 Planned)

## 📞 Support

For Unity integration issues:
1. Check server logs in `logs/unity_integration.log`
2. Verify ULTRON Agent is running (`.\run.bat`)
3. Test API endpoints with curl or Postman
4. Review Unity console for error messages

---

**Ready to create intelligent Unity games with ULTRON Agent!** 🎮🤖