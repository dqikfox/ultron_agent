using UnityEngine;

[CreateAssetMenu(fileName = "UltronAvatarPrefab", menuName = "ULTRON/Avatar Prefab")]
public class UltronAvatarPrefab : ScriptableObject
{
    [Header("Prefab Setup Instructions")]
    [TextArea(5, 10)]
    public string instructions = @"
1. Create a Capsule GameObject
2. Add UltronAvatarController script
3. Add CharacterController component
4. Add Animator component (optional)
5. Set up materials for each personality
6. Save as prefab in Assets/Prefabs/Avatars/
";

    public static GameObject CreateBasicAvatar()
    {
        // Create capsule
        GameObject avatar = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        avatar.name = "UltronAvatar";
        
        // Add components
        avatar.AddComponent<UltronAvatarController>();
        avatar.AddComponent<CharacterController>();
        
        // Set up CharacterController
        CharacterController controller = avatar.GetComponent<CharacterController>();
        controller.height = 2f;
        controller.radius = 0.5f;
        controller.center = Vector3.zero;
        
        return avatar;
    }
}