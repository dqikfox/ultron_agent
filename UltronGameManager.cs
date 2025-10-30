using UnityEngine;
using UnityEngine.UI;
using System.Collections.Generic;
using System.Collections;

public class UltronGameManager : MonoBehaviour
{
    [Header("Avatar Management")]
    public GameObject avatarPrefab;
    public Transform[] spawnPoints;
    public int maxAvatars = 5;
    
    [Header("UI Elements")]
    public Text chatDisplay;
    public InputField chatInput;
    public Button spawnButton;
    public Dropdown personalityDropdown;
    
    [Header("Game Settings")]
    public bool autoSpawnAvatars = true;
    public float spawnInterval = 10f;
    
    private List<UltronAvatarController> activeAvatars = new List<UltronAvatarController>();
    private UnityUltronClient ultronClient;
    private Queue<string> chatMessages = new Queue<string>();
    private int maxChatMessages = 20;

    void Start()
    {
        ultronClient = GetComponent<UnityUltronClient>();
        if (ultronClient == null)
        {
            ultronClient = gameObject.AddComponent<UnityUltronClient>();
        }
        
        SetupUI();
        
        if (autoSpawnAvatars)
        {
            StartCoroutine(AutoSpawnAvatars());
        }
        
        // Spawn initial avatar
        SpawnAvatar(UltronAvatarController.AvatarPersonality.Analytical);
    }

    void SetupUI()
    {
        if (spawnButton != null)
        {
            spawnButton.onClick.AddListener(SpawnRandomAvatar);
        }
        
        if (chatInput != null)
        {
            chatInput.onEndEdit.AddListener(SendChatMessage);
        }
        
        if (personalityDropdown != null)
        {
            personalityDropdown.ClearOptions();
            List<string> personalities = new List<string>();
            foreach (UltronAvatarController.AvatarPersonality personality in System.Enum.GetValues(typeof(UltronAvatarController.AvatarPersonality)))
            {
                personalities.Add(personality.ToString());
            }
            personalityDropdown.AddOptions(personalities);
        }
    }

    public void SpawnAvatar(UltronAvatarController.AvatarPersonality personality)
    {
        if (activeAvatars.Count >= maxAvatars)
        {
            AddChatMessage("Maximum avatars reached. Remove one to spawn another.");
            return;
        }
        
        Transform spawnPoint = GetRandomSpawnPoint();
        GameObject newAvatar = Instantiate(avatarPrefab, spawnPoint.position, spawnPoint.rotation);
        
        UltronAvatarController controller = newAvatar.GetComponent<UltronAvatarController>();
        if (controller == null)
        {
            controller = newAvatar.AddComponent<UltronAvatarController>();
        }
        
        controller.personality = personality;
        controller.avatarName = $"ULTRON-{personality}-{activeAvatars.Count + 1}";
        
        // Set avatar color based on personality
        SetAvatarAppearance(newAvatar, personality);
        
        activeAvatars.Add(controller);
        
        AddChatMessage($"Avatar spawned: {controller.avatarName} ({personality})");
        
        // Notify ULTRON system
        if (ultronClient != null)
        {
            ultronClient.SendChatMessage($"New avatar created: {controller.avatarName} with {personality} personality");
        }
    }

    void SetAvatarAppearance(GameObject avatar, UltronAvatarController.AvatarPersonality personality)
    {
        Renderer renderer = avatar.GetComponent<Renderer>();
        if (renderer != null)
        {
            Material mat = new Material(Shader.Find("Standard"));
            
            switch (personality)
            {
                case UltronAvatarController.AvatarPersonality.Analytical:
                    mat.color = Color.blue;
                    break;
                case UltronAvatarController.AvatarPersonality.Creative:
                    mat.color = Color.magenta;
                    break;
                case UltronAvatarController.AvatarPersonality.Protective:
                    mat.color = Color.red;
                    break;
                case UltronAvatarController.AvatarPersonality.Friendly:
                    mat.color = Color.green;
                    break;
                case UltronAvatarController.AvatarPersonality.Explorer:
                    mat.color = Color.yellow;
                    break;
            }
            
            renderer.material = mat;
        }
    }

    Transform GetRandomSpawnPoint()
    {
        if (spawnPoints.Length > 0)
        {
            return spawnPoints[Random.Range(0, spawnPoints.Length)];
        }
        
        // Create random spawn point if none defined
        Vector3 randomPos = new Vector3(
            Random.Range(-10f, 10f),
            0f,
            Random.Range(-10f, 10f)
        );
        
        GameObject tempSpawn = new GameObject("TempSpawn");
        tempSpawn.transform.position = randomPos;
        return tempSpawn.transform;
    }

    public void SpawnRandomAvatar()
    {
        UltronAvatarController.AvatarPersonality randomPersonality = 
            (UltronAvatarController.AvatarPersonality)Random.Range(0, System.Enum.GetValues(typeof(UltronAvatarController.AvatarPersonality)).Length);
        
        SpawnAvatar(randomPersonality);
    }

    public void SpawnSelectedAvatar()
    {
        if (personalityDropdown != null)
        {
            UltronAvatarController.AvatarPersonality selectedPersonality = 
                (UltronAvatarController.AvatarPersonality)personalityDropdown.value;
            
            SpawnAvatar(selectedPersonality);
        }
    }

    IEnumerator AutoSpawnAvatars()
    {
        while (true)
        {
            yield return new WaitForSeconds(spawnInterval);
            
            if (activeAvatars.Count < maxAvatars)
            {
                SpawnRandomAvatar();
            }
        }
    }

    public void SendChatMessage(string message)
    {
        if (string.IsNullOrEmpty(message)) return;
        
        AddChatMessage($"Player: {message}");
        
        // Send to all avatars
        foreach (UltronAvatarController avatar in activeAvatars)
        {
            if (avatar != null)
            {
                avatar.RespondToPlayer(message);
            }
        }
        
        // Send to ULTRON system
        if (ultronClient != null)
        {
            ultronClient.SendChatMessage($"Player message to avatars: {message}");
        }
        
        // Clear input
        if (chatInput != null)
        {
            chatInput.text = "";
        }
    }

    public void AddChatMessage(string message)
    {
        chatMessages.Enqueue($"[{System.DateTime.Now:HH:mm:ss}] {message}");
        
        if (chatMessages.Count > maxChatMessages)
        {
            chatMessages.Dequeue();
        }
        
        UpdateChatDisplay();
    }

    void UpdateChatDisplay()
    {
        if (chatDisplay != null)
        {
            chatDisplay.text = string.Join("\n", chatMessages.ToArray());
        }
    }

    public void RemoveAvatar(UltronAvatarController avatar)
    {
        if (activeAvatars.Contains(avatar))
        {
            activeAvatars.Remove(avatar);
            AddChatMessage($"Avatar removed: {avatar.avatarName}");
            Destroy(avatar.gameObject);
        }
    }

    public void ClearAllAvatars()
    {
        foreach (UltronAvatarController avatar in activeAvatars)
        {
            if (avatar != null)
            {
                Destroy(avatar.gameObject);
            }
        }
        
        activeAvatars.Clear();
        AddChatMessage("All avatars cleared.");
    }

    void Update()
    {
        // Handle keyboard shortcuts
        if (Input.GetKeyDown(KeyCode.Return) && chatInput != null && chatInput.isFocused)
        {
            SendChatMessage(chatInput.text);
        }
        
        if (Input.GetKeyDown(KeyCode.Space))
        {
            SpawnRandomAvatar();
        }
        
        if (Input.GetKeyDown(KeyCode.C))
        {
            ClearAllAvatars();
        }
    }

    void OnGUI()
    {
        // Simple debug info
        GUI.Label(new Rect(10, 10, 200, 20), $"Active Avatars: {activeAvatars.Count}/{maxAvatars}");
        GUI.Label(new Rect(10, 30, 200, 20), "Space: Spawn | C: Clear");
    }
}