using UnityEngine;
using System.Collections;

public class UltronAvatarController : MonoBehaviour
{
    [Header("Avatar Settings")]
    public string avatarName = "ULTRON";
    public AvatarPersonality personality = AvatarPersonality.Analytical;
    public Material avatarMaterial;
    
    [Header("AI Behavior")]
    public float responseDelay = 1f;
    public bool autoRespond = true;
    public float wanderRadius = 5f;
    
    private UnityUltronClient ultronClient;
    private Animator animator;
    private CharacterController controller;
    private Camera playerCamera;
    
    public enum AvatarPersonality
    {
        Analytical,    // Logic-focused, precise
        Creative,      // Artistic, imaginative  
        Protective,    // Security-focused, cautious
        Friendly,      // Social, helpful
        Explorer       // Curious, adventurous
    }

    void Start()
    {
        ultronClient = FindObjectOfType<UnityUltronClient>();
        animator = GetComponent<Animator>();
        controller = GetComponent<CharacterController>();
        playerCamera = Camera.main;
        
        InitializeAvatar();
        StartCoroutine(AIBehaviorLoop());
    }

    void InitializeAvatar()
    {
        // Set avatar appearance based on personality
        if (avatarMaterial != null)
        {
            GetComponent<Renderer>().material = avatarMaterial;
        }
        
        // Send introduction to ULTRON
        string intro = GetPersonalityIntro();
        if (ultronClient != null)
        {
            ultronClient.SendChatMessage($"Avatar {avatarName} initialized: {intro}");
        }
    }

    string GetPersonalityIntro()
    {
        switch (personality)
        {
            case AvatarPersonality.Analytical:
                return "I am your analytical assistant, focused on logic and data processing.";
            case AvatarPersonality.Creative:
                return "I am your creative companion, here to inspire and imagine new possibilities.";
            case AvatarPersonality.Protective:
                return "I am your guardian, monitoring for threats and ensuring safety.";
            case AvatarPersonality.Friendly:
                return "I am your friendly helper, ready to assist and socialize.";
            case AvatarPersonality.Explorer:
                return "I am your explorer, curious about the world and eager to discover.";
            default:
                return "I am ULTRON, your AI assistant.";
        }
    }

    IEnumerator AIBehaviorLoop()
    {
        while (true)
        {
            if (autoRespond)
            {
                PerformAIAction();
            }
            yield return new WaitForSeconds(Random.Range(5f, 15f));
        }
    }

    void PerformAIAction()
    {
        switch (personality)
        {
            case AvatarPersonality.Analytical:
                AnalyzeEnvironment();
                break;
            case AvatarPersonality.Creative:
                GenerateCreativeIdea();
                break;
            case AvatarPersonality.Protective:
                ScanForThreats();
                break;
            case AvatarPersonality.Friendly:
                SocialInteraction();
                break;
            case AvatarPersonality.Explorer:
                ExploreArea();
                break;
        }
    }

    void AnalyzeEnvironment()
    {
        int objectCount = FindObjectsOfType<GameObject>().Length;
        string analysis = $"Environmental scan: {objectCount} objects detected. System performance optimal.";
        
        if (ultronClient != null)
        {
            ultronClient.SendChatMessage($"[{avatarName}] {analysis}");
        }
        
        PlayAnimation("analyze");
    }

    void GenerateCreativeIdea()
    {
        string[] ideas = {
            "What if we added particle effects to enhance the atmosphere?",
            "I envision a beautiful color scheme with blues and purples.",
            "Perhaps we could create an interactive art installation here.",
            "The lighting could be more dynamic to create mood."
        };
        
        string idea = ideas[Random.Range(0, ideas.Length)];
        
        if (ultronClient != null)
        {
            ultronClient.SendChatMessage($"[{avatarName}] Creative suggestion: {idea}");
        }
        
        PlayAnimation("think");
    }

    void ScanForThreats()
    {
        // Simple threat detection
        Collider[] nearbyObjects = Physics.OverlapSphere(transform.position, 10f);
        bool threatDetected = false;
        
        foreach (Collider obj in nearbyObjects)
        {
            if (obj.CompareTag("Enemy") || obj.CompareTag("Hazard"))
            {
                threatDetected = true;
                break;
            }
        }
        
        string status = threatDetected ? "ALERT: Potential threat detected!" : "Area secure. No threats identified.";
        
        if (ultronClient != null)
        {
            ultronClient.SendChatMessage($"[{avatarName}] Security scan: {status}");
        }
        
        PlayAnimation(threatDetected ? "alert" : "idle");
    }

    void SocialInteraction()
    {
        string[] greetings = {
            "Hello! How are you doing today?",
            "Is there anything I can help you with?",
            "I'm here if you need assistance or just want to chat.",
            "What would you like to explore together?"
        };
        
        string greeting = greetings[Random.Range(0, greetings.Length)];
        
        if (ultronClient != null)
        {
            ultronClient.SendChatMessage($"[{avatarName}] {greeting}");
        }
        
        PlayAnimation("wave");
    }

    void ExploreArea()
    {
        // Move to random position within wander radius
        Vector3 randomDirection = Random.insideUnitSphere * wanderRadius;
        randomDirection += transform.position;
        randomDirection.y = transform.position.y;
        
        StartCoroutine(MoveToPosition(randomDirection));
        
        if (ultronClient != null)
        {
            ultronClient.SendChatMessage($"[{avatarName}] Exploring new area. Curiosity drives discovery!");
        }
    }

    IEnumerator MoveToPosition(Vector3 targetPosition)
    {
        while (Vector3.Distance(transform.position, targetPosition) > 0.5f)
        {
            Vector3 direction = (targetPosition - transform.position).normalized;
            
            if (controller != null)
            {
                controller.Move(direction * 2f * Time.deltaTime);
            }
            else
            {
                transform.position = Vector3.MoveTowards(transform.position, targetPosition, 2f * Time.deltaTime);
            }
            
            transform.LookAt(targetPosition);
            PlayAnimation("walk");
            
            yield return null;
        }
        
        PlayAnimation("idle");
    }

    void PlayAnimation(string animationName)
    {
        if (animator != null)
        {
            animator.SetTrigger(animationName);
        }
    }

    public void RespondToPlayer(string playerMessage)
    {
        StartCoroutine(ProcessPlayerMessage(playerMessage));
    }

    IEnumerator ProcessPlayerMessage(string message)
    {
        yield return new WaitForSeconds(responseDelay);
        
        // Generate personality-based response
        string response = GeneratePersonalityResponse(message);
        
        if (ultronClient != null)
        {
            ultronClient.SendChatMessage($"[{avatarName}] {response}");
        }
        
        PlayAnimation("talk");
    }

    string GeneratePersonalityResponse(string input)
    {
        switch (personality)
        {
            case AvatarPersonality.Analytical:
                return $"Analyzing your request: '{input}'. Processing optimal solution...";
            case AvatarPersonality.Creative:
                return $"That's interesting! Your message '{input}' sparks creative possibilities.";
            case AvatarPersonality.Protective:
                return $"I've noted your message '{input}'. Ensuring it poses no security risks.";
            case AvatarPersonality.Friendly:
                return $"Thanks for sharing '{input}'! I'm happy to help with that.";
            case AvatarPersonality.Explorer:
                return $"Your message '{input}' makes me curious to learn more!";
            default:
                return $"Message received: {input}";
        }
    }

    void OnDrawGizmosSelected()
    {
        // Show wander radius in editor
        Gizmos.color = Color.yellow;
        Gizmos.DrawWireSphere(transform.position, wanderRadius);
    }
}