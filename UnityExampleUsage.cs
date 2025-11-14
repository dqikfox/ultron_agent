using UnityEngine;
using UltronAgent;

/// <summary>
/// Example usage of ULTRON Agent integration in Unity
/// </summary>
public class UnityExampleUsage : MonoBehaviour
{
    [Header("ULTRON Integration")]
    public UnityUltronClient ultronClient;
    
    [Header("UI References")]
    public UnityEngine.UI.InputField chatInput;
    public UnityEngine.UI.Text chatOutput;
    public UnityEngine.UI.Button sendButton;
    public UnityEngine.UI.Text statusText;
    
    private void Start()
    {
        // Setup UI events
        if (sendButton != null)
            sendButton.onClick.AddListener(SendChatMessage);
            
        // Check connection status periodically
        InvokeRepeating(nameof(UpdateStatus), 1f, 5f);
    }
    
    /// <summary>
    /// Send chat message to ULTRON
    /// </summary>
    public void SendChatMessage()
    {
        if (ultronClient == null || chatInput == null) return;
        
        string message = chatInput.text.Trim();
        if (string.IsNullOrEmpty(message)) return;
        
        ultronClient.SendChatMessage(message, (response) =>
        {
            if (chatOutput != null)
            {
                chatOutput.text += $"\nPlayer: {message}\nULTRON: {response}\n";
            }
        });
        
        chatInput.text = "";
    }
    
    /// <summary>
    /// Update connection status
    /// </summary>
    private void UpdateStatus()
    {
        if (ultronClient != null && statusText != null)
        {
            statusText.text = ultronClient.isConnected ? "Connected to ULTRON" : "Disconnected";
            statusText.color = ultronClient.isConnected ? Color.green : Color.red;
        }
    }
    
    /// <summary>
    /// Example: Get AI analysis of current scene
    /// </summary>
    public void AnalyzeCurrentScene()
    {
        if (ultronClient == null) return;
        
        ultronClient.AnalyzeScene((result) =>
        {
            Debug.Log($"Scene Analysis: {result}");
        });
    }
    
    /// <summary>
    /// Example: Generate NPC dialogue
    /// </summary>
    public void GenerateNPCDialogue(string npcName)
    {
        if (ultronClient == null) return;
        
        string context = $"Player approached {npcName} in {UnityEngine.SceneManagement.SceneManager.GetActiveScene().name}";
        
        ultronClient.GenerateDialogue(npcName, context, (result) =>
        {
            Debug.Log($"Generated Dialogue: {result}");
            // Use the dialogue in your game
        });
    }
    
    /// <summary>
    /// Example: Smart NPC that responds to player actions
    /// </summary>
    public void SmartNPCInteraction(string playerAction)
    {
        if (ultronClient == null) return;
        
        string aiPrompt = $"Player performed action: {playerAction}. How should the NPC respond?";
        
        ultronClient.SendChatMessage(aiPrompt, (response) =>
        {
            // Use AI response to drive NPC behavior
            Debug.Log($"NPC AI Response: {response}");
            
            // Example: Parse response and trigger animations/dialogue
            if (response.Contains("friendly"))
            {
                // Trigger friendly NPC animation
            }
            else if (response.Contains("hostile"))
            {
                // Trigger combat or defensive behavior
            }
        });
    }
    
    /// <summary>
    /// Example: Dynamic quest generation
    /// </summary>
    public void GenerateDynamicQuest()
    {
        if (ultronClient == null) return;
        
        string questPrompt = "Generate a quest for the player based on their current location and level";
        
        ultronClient.SendChatMessage(questPrompt, (response) =>
        {
            Debug.Log($"Generated Quest: {response}");
            // Parse response and create quest objectives
        });
    }
}