```csharp
using UnityEngine;

public class PlayerController2D : MonoBehaviour
{
    [Header("Movement Settings")]
    public float moveSpeed = 5f;
    public float jumpForce = 12f;
    public float smoothTime = 0.1f;
    
    [Header("Ground Check")]
    public Transform groundCheck;
    public float groundCheckRadius = 0.2f;
    public LayerMask groundLayerMask;
    
    private Rigidbody2D rb;
    private Vector2 currentVelocity;
    private bool isGrounded;
    private float horizontalInput;
    
    void Start()
    {
        rb = GetComponent<Rigidbody2D>();
        currentVelocity = Vector2.zero;
    }
    
    void Update()
    {
        // Get input
        horizontalInput = Input.GetAxisRaw("Horizontal");
        
        // Ground check
        isGrounded = Physics2D.OverlapCircle(groundCheck.position, groundCheckRadius, groundLayerMask);
        
        // Jump
        if (Input.GetButtonDown("Jump") && isGrounded)
        {
            rb.AddForce(Vector2.up * jumpForce, ForceMode2D.Impulse);
        }
    }
    
    void FixedUpdate()
    {
        // Smooth horizontal movement
        float targetVelocityX = horizontalInput * moveSpeed;
        float newVelocityX = Mathf.SmoothDamp(rb.velocity.x, targetVelocityX, ref currentVelocity.x, smoothTime);
        
        rb.velocity = new Vector2(newVelocityX, rb.velocity.y);
    }
    
    void OnDrawGizmosSelected()
    {
        if (groundCheck != null)
        {
            Gizmos.color = isGrounded ? Color.green : Color.red;
            Gizmos.DrawWireSphere(groundCheck.position, groundCheckRadius);
        }
    }
}
```