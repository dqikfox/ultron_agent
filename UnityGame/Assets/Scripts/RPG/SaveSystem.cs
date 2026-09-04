Here's a complete Unity save system implementation with all requested features:

```csharp
using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

// Save data structure
[Serializable]
public class SaveData
{
    public PlayerData playerData;
    public List<QuestData> questData;
    public List<InventoryItem> inventoryData;
    public int saveSlot;
    public string saveTime;
    public string sceneName;

    public SaveData()
    {
        playerData = new PlayerData();
        questData = new List<QuestData>();
        inventoryData = new List<InventoryItem>();
    }
}

[Serializable]
public class PlayerData
{
    public Vector3 position;
    public int health;
    public int level;
    public float experience;
    public string playerName;

    public PlayerData()
    {
        position = Vector3.zero;
        health = 100;
        level = 1;
        experience = 0f;
        playerName = "Player";
    }
}

[Serializable]
public class QuestData
{
    public string questId;
    public bool isCompleted;
    public bool isActive;
    public List<string> objectives;

    public QuestData()
    {
        objectives = new List<string>();
    }
}

[Serializable]
public class InventoryItem
{
    public string itemId;
    public int quantity;
    public bool isEquipped;
}

public class SaveSystem : MonoBehaviour
{
    public static SaveSystem Instance;
    
    [Header("Save Settings")]
    public int maxSaveSlots = 3;
    public float autoSaveInterval = 300f; // 5 minutes
    
    private string saveDirectory;
    private float lastAutoSaveTime;
    private bool autoSaveEnabled = true;

    private void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            InitializeSaveSystem();
        }
        else
        {
            Destroy(gameObject);
        }
    }

    private void InitializeSaveSystem()
    {
        saveDirectory = Path.Combine(Application.persistentDataPath, "Saves");
        if (!Directory.Exists(saveDirectory))
        {
            Directory.CreateDirectory(saveDirectory);
        }
    }

    private void Update()
    {
        // Handle auto-save
        if (autoSaveEnabled && Time.time - lastAutoSaveTime > autoSaveInterval)
        {
            AutoSave();
        }
    }

    // Save current game state to specified slot
    public void SaveGame(int slot)
    {
        if (slot < 0 || slot >= maxSaveSlots)
        {
            Debug.LogError($"Invalid save slot: {slot}. Must be between 0 and {maxSaveSlots - 1}");
            return;
        }

        SaveData saveData = CollectSaveData();
        saveData.saveSlot = slot;
        saveData.saveTime = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");
        saveData.sceneName = UnityEngine.SceneManagement.SceneManager.GetActiveScene().name;

        string json = JsonUtility.ToJson(saveData, true);
        string filePath = Path.Combine(saveDirectory, $"save_{slot}.json");

        try
        {
            File.WriteAllText(filePath, json);
            Debug.Log($"Game saved to slot {slot}");
        }
        catch (Exception e)
        {
            Debug.LogError($"Failed to save game: {e.Message}");
        }
    }

    // Load game from specified slot
    public bool LoadGame(int slot)
    {
        if (slot < 0 || slot >= maxSaveSlots)
        {
            Debug.LogError($"Invalid save slot: {slot}. Must be between 0 and {maxSaveSlots - 1}");
            return false;
        }

        string filePath = Path.Combine(saveDirectory, $"save_{slot}.json");

        if (!File.Exists(filePath))
        {
            Debug.LogWarning($"Save file not found for slot {slot}");
            return false;
        }

        try
        {
            string json = File.ReadAllText(filePath);
            SaveData saveData = JsonUtility.FromJson<SaveData>(json);
            
            ApplySaveData(saveData);
            Debug.Log($"Game loaded from slot {slot}");
            return true;
        }
        catch (Exception e)
        {
            Debug.LogError($"Failed to load game: {e.Message}");
            return false;
        }
    }

    // Auto-save to slot 0
    public void AutoSave()
    {
        SaveGame(0);
        lastAutoSaveTime = Time.time;
    }

    // Save at checkpoint (saves to slot 1)
    public void SaveCheckpoint()
    {
        SaveGame(1);
        Debug.Log("Checkpoint saved");
    }

    // Get save file info for UI display
    public SaveFileInfo GetSaveFileInfo(int slot)
    {
        if (slot < 0 || slot >= maxSaveSlots)
            return null;

        string filePath = Path.Combine(saveDirectory, $"save_{slot}.json");

        if (!File.Exists(filePath))
            return null;

        try
        {
            string json = File.ReadAllText(filePath);
            SaveData saveData = JsonUtility.FromJson<SaveData>(json);
            
            return new SaveFileInfo
            {
                slot = saveData.saveSlot,
                saveTime = saveData.saveTime,
                sceneName = saveData.sceneName,
                playerName = saveData.playerData.playerName,
                playerLevel = saveData.playerData.level,
                exists = true
            };
        }
        catch
        {
            return null;
        }
    }

    // Delete a save file
    public void DeleteSave(int slot)
    {
        if (slot < 0 || slot >= maxSaveSlots)
            return;

        string filePath = Path.Combine(saveDirectory, $"save_{slot}.json");

        if (File.Exists(filePath))
        {
            try
            {
                File.Delete(filePath);
                Debug.Log($"Save file deleted for slot {slot}");
            }
            catch (Exception e)
            {
                Debug.LogError($"Failed to delete save file: {e.Message}");
            }
        }
    }

    // Check if save slot exists
    public bool SaveExists(int slot)
    {
        if (slot < 0 || slot >= maxSaveSlots)
            return false;

        string filePath = Path.Combine(saveDirectory, $"save_{slot}.json");
        return File.Exists(filePath);
    }

    // Get all save file info
    public List<SaveFileInfo> GetAllSaveFiles()
    {
        List<SaveFileInfo> saveFiles = new List<SaveFileInfo>();

        for (int i = 0; i < maxSaveSlots; i++)
        {
            SaveFileInfo info = GetSaveFileInfo(i);
            if (info != null)
            {
                saveFiles.Add(info);
            }
        }

        return saveFiles;
    }

    // Enable/disable auto-save
    public void SetAutoSave(bool enabled)
    {
        autoSaveEnabled = enabled;
    }

    // Collect current game state for saving
    private SaveData CollectSaveData()
    {
        SaveData saveData = new SaveData();

        // Collect player data (example implementation)
        GameObject player = GameObject.FindGameObjectWithTag("Player");
        if (player != null)
        {
            saveData.playerData.position = player.transform.position;
            // Add other player data collection here
        }

        // Collect quest data (example implementation)
        // This would interface with your quest system
        // saveData.questData = QuestManager.Instance.GetAllQuestData();

        // Collect inventory data (example implementation)
        // This would interface with your inventory system
        // saveData.inventoryData = InventoryManager.Instance.GetAllItems();

        return saveData;
    }

    // Apply loaded save data to game
    private void ApplySaveData(SaveData saveData)
    {
        // Load player data
        GameObject player = GameObject.FindGameObjectWithTag("Player");
        if (player != null)
        {
            player.transform.position = saveData.playerData.position;
            // Apply other player data here
        }

        // Load scene if different
        if (saveData.sceneName != UnityEngine.SceneManagement.SceneManager.GetActiveScene().name)
        {
            UnityEngine.SceneManagement.SceneManager.LoadScene(saveData.sceneName);
        }

        // Load quest data
        // QuestManager.Instance.LoadQuestData(saveData.questData);

        // Load inventory data
        // InventoryManager.Instance.LoadInventoryData(saveData.inventoryData);
    }
}

// Save file information for UI
public class SaveFileInfo
{
    public int slot;
    public string saveTime;
    public string sceneName;
    public string playerName;
    public int playerLevel;
    public bool exists;
}
```

**Key Features Implemented:**

1. **Save Data Structure:**
   - Player data (position, health, level, etc.)
   - Quest data (completion status, objectives)
   - Inventory data (items, quantities)
   - Metadata (save time, scene name)

2. **JSON Serialization:**
   - Uses Unity's built-in `JsonUtility`
   - Human-readable save files
   - Pretty-printed JSON for debugging

3. **Save/Load Functionality:**
   - `SaveGame(int slot)` - Save to specific slot
   - `LoadGame(int slot)` - Load from specific slot
   - Error handling for file operations

4. **Multiple Save Slots:**
   - Configurable number of save slots
   - Slot validation
   - Save file management

5. **Auto-Save System:**
   - Configurable interval
   - Auto-save to slot 0
   - Toggle auto-save on/off

6. **Checkpoint Saving:**
   - Dedicated `SaveCheckpoint()` method
   - Saves to slot 1 by default

7. **Save File Management:**
   - `GetSaveFileInfo()` - Get save metadata
   - `DeleteSave()` - Remove save files
   - `SaveExists()` - Check save file existence
   - `GetAllSaveFiles()` - List all saves

**Usage Instructions:**

1. Attach the `SaveSystem` script to a GameObject in your scene
2. Configure save settings in the inspector:
   - Set `maxSaveSlots` (default: 3)
   - Set `autoSaveInterval` in seconds (default: 300 seconds/5 minutes)

3. Use these methods in your game:
   ```csharp
   // Manual saving
   SaveSystem.Instance.SaveGame(2); // Save to slot 2
   
   // Loading
   SaveSystem.Instance.LoadGame(2); // Load from slot 2
   
   // Auto-save
   SaveSystem.Instance.AutoSave(); // Force auto-save
   
   // Checkpoint saving
   SaveSystem.Instance.SaveCheckpoint(); // Save checkpoint
   
   // File management
   bool exists = SaveSystem.Instance.SaveExists(1);
   SaveSystem.Instance.DeleteSave(1);
   ```

**Important Notes:**
1. You'll need to implement the actual data collection in `CollectSaveData()` and `ApplySaveData()` methods based on your game's systems
2. The save files are stored in `Application.persistentDataPath/Saves/`
3. Save files are named `save_0.json`, `save_1.json`, etc.
4. The system uses `JsonUtility` which has limitations - consider Newtonsoft.Json for complex data structures
5. Error handling is implemented for all file operations

This implementation provides a solid foundation that you can extend based on your specific game requirements.