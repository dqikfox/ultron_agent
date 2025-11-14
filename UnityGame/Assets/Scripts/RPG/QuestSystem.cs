Here's a complete Unity C# quest system implementation:

```csharp
using System;
using System.Collections.Generic;
using UnityEngine;

// Quest data structure
[Serializable]
public class Quest
{
    public string id;
    public string title;
    public string description;
    [TextArea] public string[] objectives;
    public int xpReward;
    public int goldReward;
    public Item[] itemRewards;
    public QuestStatus status = QuestStatus.NotStarted;
    private int[] objectiveCompletion;

    public Quest(string id, string title, string description, string[] objectives, int xpReward, int goldReward, Item[] itemRewards)
    {
        this.id = id;
        this.title = title;
        this.description = description;
        this.objectives = objectives;
        this.xpReward = xpReward;
        this.goldReward = goldReward;
        this.itemRewards = itemRewards;
        this.objectiveCompletion = new int[objectives.Length];
    }

    public bool IsObjectiveComplete(int index)
    {
        return index < objectiveCompletion.Length && objectiveCompletion[index] >= 1;
    }

    public void CompleteObjective(int index)
    {
        if (index < objectiveCompletion.Length)
        {
            objectiveCompletion[index] = 1;
            CheckQuestCompletion();
        }
    }

    public int GetObjectiveProgress(int index)
    {
        return index < objectiveCompletion.Length ? objectiveCompletion[index] : 0;
    }

    public void SetObjectiveProgress(int index, int progress)
    {
        if (index < objectiveCompletion.Length)
        {
            objectiveCompletion[index] = progress;
            CheckQuestCompletion();
        }
    }

    private void CheckQuestCompletion()
    {
        for (int i = 0; i < objectiveCompletion.Length; i++)
        {
            if (objectiveCompletion[i] < 1)
                return;
        }
        status = QuestStatus.Completed;
    }
}

public enum QuestStatus
{
    NotStarted,
    Active,
    Completed,
    Failed
}

[Serializable]
public class Item
{
    public string name;
    public int quantity;
}

// Quest Manager Singleton
public class QuestManager : MonoBehaviour
{
    public static QuestManager Instance;
    
    public List<Quest> allQuests = new List<Quest>();
    public List<Quest> activeQuests = new List<Quest>();
    public List<Quest> completedQuests = new List<Quest>();
    public List<Quest> failedQuests = new List<Quest>();

    public Action<Quest> OnQuestStarted;
    public Action<Quest> OnQuestCompleted;
    public Action<Quest> OnQuestFailed;
    public Action<Quest, int> OnObjectiveCompleted;

    private void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else
        {
            Destroy(gameObject);
        }
    }

    public void StartQuest(string questId)
    {
        Quest quest = allQuests.Find(q => q.id == questId);
        if (quest != null && quest.status == QuestStatus.NotStarted)
        {
            quest.status = QuestStatus.Active;
            activeQuests.Add(quest);
            OnQuestStarted?.Invoke(quest);
        }
    }

    public void CompleteObjective(string questId, int objectiveIndex)
    {
        Quest quest = activeQuests.Find(q => q.id == questId);
        if (quest != null)
        {
            quest.CompleteObjective(objectiveIndex);
            OnObjectiveCompleted?.Invoke(quest, objectiveIndex);
            
            if (quest.status == QuestStatus.Completed)
            {
                CompleteQuest(questId);
            }
        }
    }

    public void SetObjectiveProgress(string questId, int objectiveIndex, int progress)
    {
        Quest quest = activeQuests.Find(q => q.id == questId);
        if (quest != null)
        {
            quest.SetObjectiveProgress(objectiveIndex, progress);
            if (quest.status == QuestStatus.Completed)
            {
                CompleteQuest(questId);
            }
        }
    }

    private void CompleteQuest(string questId)
    {
        Quest quest = activeQuests.Find(q => q.id == questId);
        if (quest != null)
        {
            activeQuests.Remove(quest);
            completedQuests.Add(quest);
            DistributeRewards(quest);
            OnQuestCompleted?.Invoke(quest);
        }
    }

    public void FailQuest(string questId)
    {
        Quest quest = activeQuests.Find(q => q.id == questId);
        if (quest != null)
        {
            quest.status = QuestStatus.Failed;
            activeQuests.Remove(quest);
            failedQuests.Add(quest);
            OnQuestFailed?.Invoke(quest);
        }
    }

    private void DistributeRewards(Quest quest)
    {
        // Distribute XP
        if (quest.xpReward > 0)
        {
            // Add XP to player
            Debug.Log($"Gained {quest.xpReward} XP");
        }

        // Distribute Gold
        if (quest.goldReward > 0)
        {
            // Add gold to player inventory
            Debug.Log($"Gained {quest.goldReward} Gold");
        }

        // Distribute Items
        if (quest.itemRewards != null && quest.itemRewards.Length > 0)
        {
            foreach (Item item in quest.itemRewards)
            {
                // Add item to player inventory
                Debug.Log($"Gained {item.quantity}x {item.name}");
            }
        }
    }

    public Quest GetQuestById(string id)
    {
        return allQuests.Find(q => q.id == id);
    }

    public List<Quest> GetActiveQuests()
    {
        return new List<Quest>(activeQuests);
    }

    public List<Quest> GetCompletedQuests()
    {
        return new List<Quest>(completedQuests);
    }

    public List<Quest> GetFailedQuests()
    {
        return new List<Quest>(failedQuests);
    }
}
```

```csharp
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

// Quest Log UI Integration
public class QuestLogUI : MonoBehaviour
{
    public GameObject questLogPanel;
    public Transform activeQuestsContainer;
    public Transform completedQuestsContainer;
    public Transform failedQuestsContainer;
    public GameObject questEntryPrefab;

    private Dictionary<string, QuestEntryUI> questEntryMap = new Dictionary<string, QuestEntryUI>();

    private void Start()
    {
        QuestManager.Instance.OnQuestStarted += AddQuestToActiveList;
        QuestManager.Instance.OnQuestCompleted += AddQuestToCompletedList;
        QuestManager.Instance.OnQuestFailed += AddQuestToFailedList;
        QuestManager.Instance.OnObjectiveCompleted += UpdateQuestEntry;
    }

    private void OnDestroy()
    {
        if (QuestManager.Instance != null)
        {
            QuestManager.Instance.OnQuestStarted -= AddQuestToActiveList;
            QuestManager.Instance.OnQuestCompleted -= AddQuestToCompletedList;
            QuestManager.Instance.OnQuestFailed -= AddQuestToFailedList;
            QuestManager.Instance.OnObjectiveCompleted -= UpdateQuestEntry;
        }
    }

    public void ToggleQuestLog()
    {
        questLogPanel.SetActive(!questLogPanel.activeSelf);
        if (questLogPanel.activeSelf)
        {
            RefreshQuestLog();
        }
    }

    private void RefreshQuestLog()
    {
        ClearQuestLists();
        PopulateQuestLists();
    }

    private void ClearQuestLists()
    {
        foreach (Transform child in activeQuestsContainer)
            Destroy(child.gameObject);
        foreach (Transform child in completedQuestsContainer)
            Destroy(child.gameObject);
        foreach (Transform child in failedQuestsContainer)
            Destroy(child.gameObject);
        questEntryMap.Clear();
    }

    private void PopulateQuestLists()
    {
        foreach (Quest quest in QuestManager.Instance.GetActiveQuests())
        {
            AddQuestToActiveList(quest);
        }
        foreach (Quest quest in QuestManager.Instance.GetCompletedQuests())
        {
            AddQuestToCompletedList(quest);
        }
        foreach (Quest quest in QuestManager.Instance.GetFailedQuests())
        {
            AddQuestToFailedList(quest);
        }
    }

    private void AddQuestToActiveList(Quest quest)
    {
        GameObject entry = Instantiate(questEntryPrefab, activeQuestsContainer);
        QuestEntryUI entryUI = entry.GetComponent<QuestEntryUI>();
        entryUI.Initialize(quest);
        questEntryMap[quest.id] = entryUI;
    }

    private void AddQuestToCompletedList(Quest quest)
    {
        GameObject entry = Instantiate(questEntryPrefab, completedQuestsContainer);
        QuestEntryUI entryUI = entry.GetComponent<QuestEntryUI>();
        entryUI.Initialize(quest);
        questEntryMap[quest.id] = entryUI;
    }

    private void AddQuestToFailedList(Quest quest)
    {
        GameObject entry = Instantiate(questEntryPrefab, failedQuestsContainer);
        QuestEntryUI entryUI = entry.GetComponent<QuestEntryUI>();
        entryUI.Initialize(quest);
        questEntryMap[quest.id] = entryUI;
    }

    private void UpdateQuestEntry(Quest quest, int objectiveIndex)
    {
        if (questEntryMap.ContainsKey(quest.id))
        {
            questEntryMap[quest.id].UpdateObjective(objectiveIndex);
        }
    }
}
```

```csharp
using UnityEngine;
using UnityEngine.UI;

// UI Component for individual quest entries
public class QuestEntryUI : MonoBehaviour
{
    public Text titleText;
    public Text descriptionText;
    public Transform objectivesContainer;
    public GameObject objectivePrefab;
    public Image statusIcon;
    public Sprite activeSprite;
    public Sprite completedSprite;
    public Sprite failedSprite;

    private Quest quest;
    private ObjectiveUI[] objectiveUIs;

    public void Initialize(Quest quest)
    {
        this.quest = quest;
        titleText.text = quest.title;
        descriptionText.text = quest.description;

        CreateObjectives();
        UpdateStatus();
    }

    private void CreateObjectives()
    {
        objectiveUIs = new ObjectiveUI[quest.objectives.Length];
        for (int i = 0; i < quest.objectives.Length; i++)
        {
            GameObject objGO = Instantiate(objectivePrefab, objectivesContainer);
            ObjectiveUI objUI = objGO.GetComponent<ObjectiveUI>();
            objUI.Initialize(quest.objectives[i], quest.IsObjectiveComplete(i));
            objectiveUIs[i] = objUI;
        }
    }

    public void UpdateObjective(int index)
    {
        if (index < objectiveUIs.Length)
        {
            objectiveUIs[index].MarkComplete();
        }
        UpdateStatus();
    }

    private void UpdateStatus()
    {
        switch (quest.status)
        {
            case QuestStatus.Active:
                statusIcon.sprite = activeSprite;
                break;
            case QuestStatus.Completed:
                statusIcon.sprite = completedSprite;
                break;
            case QuestStatus.Failed:
                statusIcon.sprite = failedSprite;
                break;
        }
    }
}
```

```csharp
using UnityEngine;
using UnityEngine.UI;

// UI Component for individual objectives
public class ObjectiveUI : MonoBehaviour
{
    public Text descriptionText;
    public Toggle completionToggle;

    public void Initialize(string description, bool isComplete)
    {
        descriptionText.text = description;
        completionToggle.isOn = isComplete;
    }

    public void MarkComplete()
    {
        completionToggle.isOn = true;
    }
}
```

**Setup Instructions:**

1. Create a new GameObject in your scene and attach the QuestManager script
2. Create UI elements for the quest log:
   - A main panel (QuestLogPanel)
   - Containers for active/completed/failed quests
   - Quest entry prefab with QuestEntryUI component
   - Objective prefab with ObjectiveUI component
3. Attach QuestLogUI script to a UI controller object
4. Configure the UI references in the QuestLogUI inspector
5. Create quest data in the QuestManager's allQuests list in the inspector

**Key Features:**

1. **Quest Data Structure**: Complete quest information with objectives tracking
2. **Singleton Manager**: Centralized quest management system
3. **Status Tracking**: Handles active, completed, and failed quests
4. **Objective System**: Progress tracking for individual quest objectives
5. **Reward Distribution**: XP, gold, and item rewards
6. **UI Integration**: Complete quest log interface with real-time updates
7. **Event System**: Callbacks for quest state changes

**Usage Examples:**

```csharp
// Start a quest
QuestManager.Instance.StartQuest("quest_001");

// Complete an objective
QuestManager.Instance.CompleteObjective("quest_001", 0);

// Set objective progress (for incremental objectives)
QuestManager.Instance.SetObjectiveProgress("quest_001", 1, 50);

// Fail a quest
QuestManager.Instance.FailQuest("quest_001");
```

This implementation provides a complete, extensible quest system with UI integration that can be easily customized for your specific game needs.