Here's a complete Unity dialogue system implementation with all requested features:

```csharp
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

[System.Serializable]
public class DialogueLine
{
    public string speaker;
    [TextArea(2, 5)]
    public string text;
    public List<DialogueChoice> choices = new List<DialogueChoice>();
}

[System.Serializable]
public class DialogueChoice
{
    public string text;
    public Dialogue nextDialogue;
}

[CreateAssetMenu(fileName = "NewDialogue", menuName = "Dialogue/Dialogue")]
public class Dialogue : ScriptableObject
{
    public List<DialogueLine> lines = new List<DialogueLine>();
}

public class DialogueManager : MonoBehaviour
{
    public static DialogueManager Instance;

    [Header("UI References")]
    public GameObject dialoguePanel;
    public TextMeshProUGUI speakerText;
    public TextMeshProUGUI dialogueText;
    public Transform choiceContainer;
    public GameObject choiceButtonPrefab;

    [Header("Typewriter Settings")]
    public float typingSpeed = 0.02f;

    private Queue<DialogueLine> dialogueQueue = new Queue<DialogueLine>();
    private Dialogue currentDialogue;
    private bool isTyping = false;
    private bool dialogueActive = false;
    private List<Button> choiceButtons = new List<Button>();

    void Awake()
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

    void Start()
    {
        dialoguePanel.SetActive(false);
    }

    public void StartDialogue(Dialogue dialogue)
    {
        if (dialogueActive) return;

        currentDialogue = dialogue;
        dialogueQueue.Clear();

        foreach (DialogueLine line in dialogue.lines)
        {
            dialogueQueue.Enqueue(line);
        }

        dialogueActive = true;
        dialoguePanel.SetActive(true);
        DisplayNextLine();
    }

    public void DisplayNextLine()
    {
        if (dialogueQueue.Count == 0)
        {
            EndDialogue();
            return;
        }

        DialogueLine currentLine = dialogueQueue.Dequeue();
        speakerText.text = currentLine.speaker;
        StopAllCoroutines();
        StartCoroutine(TypeText(currentLine.text));
        ShowChoices(currentLine.choices);
    }

    IEnumerator TypeText(string text)
    {
        isTyping = true;
        dialogueText.text = "";
        foreach (char letter in text.ToCharArray())
        {
            dialogueText.text += letter;
            yield return new WaitForSeconds(typingSpeed);
        }
        isTyping = false;
    }

    void ShowChoices(List<DialogueChoice> choices)
    {
        ClearChoices();

        if (choices.Count == 0)
        {
            // Add a default "Continue" button if no choices
            GameObject choiceButton = Instantiate(choiceButtonPrefab, choiceContainer);
            Button button = choiceButton.GetComponent<Button>();
            TextMeshProUGUI buttonText = choiceButton.GetComponentInChildren<TextMeshProUGUI>();
            buttonText.text = "Continue";
            button.onClick.AddListener(() => DisplayNextLine());
            choiceButtons.Add(button);
        }
        else
        {
            foreach (DialogueChoice choice in choices)
            {
                GameObject choiceButton = Instantiate(choiceButtonPrefab, choiceContainer);
                Button button = choiceButton.GetComponent<Button>();
                TextMeshProUGUI buttonText = choiceButton.GetComponentInChildren<TextMeshProUGUI>();
                buttonText.text = choice.text;
                
                button.onClick.AddListener(() => SelectChoice(choice));
                choiceButtons.Add(button);
            }
        }
    }

    void SelectChoice(DialogueChoice choice)
    {
        if (choice.nextDialogue != null)
        {
            StartDialogue(choice.nextDialogue);
        }
        else
        {
            EndDialogue();
        }
    }

    void ClearChoices()
    {
        foreach (Button button in choiceButtons)
        {
            if (button != null)
                Destroy(button.gameObject);
        }
        choiceButtons.Clear();
    }

    void EndDialogue()
    {
        dialogueActive = false;
        dialoguePanel.SetActive(false);
        ClearChoices();
    }

    void Update()
    {
        if (dialogueActive && Input.GetMouseButtonDown(0) && !isTyping)
        {
            DisplayNextLine();
        }
    }
}

public class NPCInteraction : MonoBehaviour
{
    public Dialogue dialogue;

    void OnTriggerEnter2D(Collider2D other)
    {
        if (other.CompareTag("Player"))
        {
            DialogueManager.Instance.StartDialogue(dialogue);
        }
    }
}
```

**Setup Instructions:**

1. **Create UI Elements:**
   - Create a Canvas with the following child objects:
     - Dialogue Panel (Panel)
     - Speaker Text (TextMeshProUGUI) - Child of Dialogue Panel
     - Dialogue Text (TextMeshProUGUI) - Child of Dialogue Panel
     - Choice Container (Empty GameObject) - Child of Dialogue Panel
     - Choice Button Prefab (Button with TextMeshProUGUI child)

2. **Assign References:**
   - Attach the DialogueManager script to a GameObject
   - Assign all UI elements in the inspector

3. **Create Dialogue Assets:**
   - Right-click in Project Window → Create → Dialogue → Dialogue
   - Configure dialogue lines and choices in the inspector

4. **NPC Setup:**
   - Attach NPCInteraction script to NPC GameObject
   - Assign dialogue asset to the NPC
   - Ensure NPC has a Collider2D set to "Is Trigger"
   - Player should have the "Player" tag

**Key Features:**

- **Data Structure:** DialogueLine (speaker, text, choices) and DialogueChoice (text, next dialogue)
- **Queue System:** Processes dialogue lines sequentially
- **Typewriter Effect:** Coroutine-based character-by-character text display
- **Choice System:** Dynamic button generation for dialogue options
- **NPC Interaction:** Trigger-based dialogue activation
- **UI Controller:** Complete panel management and text display

**Usage:**
1. Create dialogue assets with multiple lines and choices
2. Attach NPCInteraction to NPCs with dialogue references
3. Player triggers dialogue by entering NPC collider
4. Click to progress through dialogue or select choices

**Customization:**
- Adjust typing speed in DialogueManager
- Modify UI appearance through Canvas elements
- Extend DialogueLine class for additional features (emotions, animations)
- Add audio support by extending the DialogueManager

This implementation provides a complete, modular dialogue system that can be easily extended for more complex narrative systems.