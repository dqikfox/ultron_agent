```csharp
using UnityEngine;
using Unity.Sentis;
using System.Collections.Generic;

public class SentisAIEnemy : MonoBehaviour
{
    [Header("AI Model")]
    public ModelAsset modelAsset;
    private IWorker worker;
    private Model model;

    [Header("Game State")]
    public Transform player;
    public float detectionRange = 10f;
    public float fleeRange = 5f;
    public float moveSpeed = 3f;
    public float patrolSpeed = 1.5f;

    [Header("Patrol Settings")]
    public Vector3[] patrolPoints;
    private int currentPatrolIndex = 0;
    private Vector3 targetPosition;

    private enum AIState { Patrol, Chase, Flee }
    private AIState currentState = AIState.Patrol;

    private void Start()
    {
        // Initialize Sentis model
        if (modelAsset != null)
        {
            model = ModelLoader.Load(modelAsset);
            worker = WorkerFactory.CreateWorker(BackendType.GPUCompute, model);
        }
        else
        {
            Debug.LogError("ModelAsset is not assigned!");
        }

        // Set initial patrol target
        if (patrolPoints.Length > 0)
        {
            targetPosition = patrolPoints[0];
        }
    }

    private void Update()
    {
        if (worker == null || player == null) return;

        // Get game state
        Vector3 playerPosition = player.position;
        Vector3 enemyPosition = transform.position;
        float distanceToPlayer = Vector3.Distance(enemyPosition, playerPosition);

        // Prepare input data for neural network
        float[] inputData = new float[]
        {
            playerPosition.x, playerPosition.y, playerPosition.z,
            enemyPosition.x, enemyPosition.y, enemyPosition.z,
            distanceToPlayer,
            (float)currentState
        };

        // Run neural network inference
        Tensor inputTensor = new Tensor(1, 8, inputData);
        worker.Execute(inputTensor);
        
        // Get output (action probabilities)
        Tensor outputTensor = worker.PeekOutput();
        float[] actionProbabilities = outputTensor.ToReadOnlyArray();
        
        // Decide action based on neural network output
        int action = GetActionFromProbabilities(actionProbabilities);
        
        // Execute action
        ExecuteAction(action, playerPosition, distanceToPlayer);
        
        // Clean up tensor
        inputTensor.Dispose();
    }

    private int GetActionFromProbabilities(float[] probabilities)
    {
        // Find the action with the highest probability
        int bestAction = 0;
        float maxProbability = probabilities[0];
        
        for (int i = 1; i < probabilities.Length; i++)
        {
            if (probabilities[i] > maxProbability)
            {
                maxProbability = probabilities[i];
                bestAction = i;
            }
        }
        
        return bestAction;
    }

    private void ExecuteAction(int action, Vector3 playerPosition, float distanceToPlayer)
    {
        switch (action)
        {
            case 0: // Patrol
                Patrol();
                break;
            case 1: // Chase
                Chase(playerPosition);
                break;
            case 2: // Flee
                Flee(playerPosition);
                break;
            default:
                Patrol();
                break;
        }
    }

    private void Patrol()
    {
        currentState = AIState.Patrol;
        
        // Check if we've reached the current patrol point
        if (Vector3.Distance(transform.position, targetPosition) < 0.5f)
        {
            // Move to next patrol point
            currentPatrolIndex = (currentPatrolIndex + 1) % patrolPoints.Length;
            targetPosition = patrolPoints[currentPatrolIndex];
        }
        
        // Move towards target position
        Vector3 direction = (targetPosition - transform.position).normalized;
        transform.position += direction * patrolSpeed * Time.deltaTime;
        
        // Rotate to face movement direction
        if (direction != Vector3.zero)
        {
            transform.rotation = Quaternion.LookRotation(direction);
        }
    }

    private void Chase(Vector3 playerPosition)
    {
        currentState = AIState.Chase;
        
        // Move towards player
        Vector3 direction = (playerPosition - transform.position).normalized;
        transform.position += direction * moveSpeed * Time.deltaTime;
        
        // Rotate to face player
        transform.LookAt(playerPosition);
    }

    private void Flee(Vector3 playerPosition)
    {
        currentState = AIState.Flee;
        
        // Move away from player
        Vector3 direction = (transform.position - playerPosition).normalized;
        transform.position += direction * moveSpeed * Time.deltaTime;
        
        // Rotate to face away from player
        transform.LookAt(transform.position - direction);
    }

    private void OnDestroy()
    {
        // Dispose worker and tensors properly
        worker?.Dispose();
        model?.Dispose();
    }

    private void OnDrawGizmosSelected()
    {
        // Visualize patrol points
        Gizmos.color = Color.blue;
        for (int i = 0; i < patrolPoints.Length; i++)
        {
            Gizmos.DrawSphere(patrolPoints[i], 0.2f);
            if (patrolPoints.Length > 1)
            {
                int nextIndex = (i + 1) % patrolPoints.Length;
                Gizmos.DrawLine(patrolPoints[i], patrolPoints[nextIndex]);
            }
        }
        
        // Visualize detection range
        Gizmos.color = Color.yellow;
        Gizmos.DrawWireSphere(transform.position, detectionRange);
        
        // Visualize flee range
        Gizmos.color = Color.red;
        Gizmos.DrawWireSphere(transform.position, fleeRange);
    }
}
```