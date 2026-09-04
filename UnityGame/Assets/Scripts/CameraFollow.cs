```csharp
using UnityEngine;

public class SmoothCameraFollow : MonoBehaviour
{
    [Header("Target Settings")]
    public Transform target;
    
    [Header("Offset Settings")]
    public Vector2 offset = new Vector2(0f, 0f);
    
    [Header("Smooth Settings")]
    [Range(0f, 1f)]
    public float damping = 0.1f;
    
    [Header("Camera Bounds")]
    public bool useBounds = false;
    public Vector2 minBounds = Vector2.zero;
    public Vector2 maxBounds = Vector2.zero;
    
    private Vector3 velocity = Vector3.zero;
    private Vector3 targetPosition;
    
    void LateUpdate()
    {
        if (target == null)
            return;
            
        // Calculate target position with offset
        targetPosition = target.position + new Vector3(offset.x, offset.y, -10f);
        
        // Apply bounds if enabled
        if (useBounds)
        {
            targetPosition.x = Mathf.Clamp(targetPosition.x, minBounds.x, maxBounds.x);
            targetPosition.y = Mathf.Clamp(targetPosition.y, minBounds.y, maxBounds.y);
        }
        
        // Smoothly move camera towards target position
        transform.position = Vector3.SmoothDamp(transform.position, targetPosition, ref velocity, damping);
    }
    
    // Optional: Set new target
    public void SetTarget(Transform newTarget)
    {
        target = newTarget;
    }
    
    // Optional: Set offset
    public void SetOffset(Vector2 newOffset)
    {
        offset = newOffset;
    }
}
```