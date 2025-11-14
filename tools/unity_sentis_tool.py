"""Unity Sentis Integration - Modern neural network inference"""

from pathlib import Path
from utils.ultron_logger import log_info, log_error


class UnitySentisTool:
    name = "Unity Sentis"
    description = "Create neural network inference scripts using Unity Sentis"
    
    def __init__(self, config=None):
        self.config = config or {}
        self.output_dir = Path("UnityGame/Assets/Scripts/Sentis")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def match(self, command: str) -> bool:
        keywords = ["sentis", "neural network", "ai model", "inference"]
        return any(k in command.lower() for k in keywords)
    
    def execute(self, command: str, **kwargs) -> str:
        log_info("unity_sentis", f"Command: {command}")
        
        if "game" in command.lower():
            return self._create_game_ai()
        else:
            return self._create_basic_inference()
    
    def _create_basic_inference(self) -> str:
        """Generate basic Sentis inference script"""
        script = """using Unity.Sentis;
using UnityEngine;

public class SentisInference : MonoBehaviour
{
    public ModelAsset modelAsset;
    private Model runtimeModel;
    private IWorker worker;

    void Start()
    {
        runtimeModel = ModelLoader.Load(modelAsset);
        worker = WorkerFactory.CreateWorker(BackendType.GPUCompute, runtimeModel);
    }

    public float[] RunInference(float[] inputData, TensorShape inputShape)
    {
        using var input = new TensorFloat(inputShape, inputData);
        worker.Execute(input);
        
        var output = worker.PeekOutput() as TensorFloat;
        output.CompleteOperationsAndDownload();
        
        return output.ToReadOnlyArray();
    }

    void OnDestroy()
    {
        worker?.Dispose();
    }
}"""
        
        output_path = self.output_dir / "SentisInference.cs"
        output_path.write_text(script, encoding='utf-8')
        log_info("unity_sentis", f"Created: {output_path}")
        return f"Created: {output_path}"
    
    def _create_game_ai(self) -> str:
        """Generate game AI scripts with Sentis"""
        
        # Enemy AI with neural network
        enemy_ai = """using Unity.Sentis;
using UnityEngine;

public class AIEnemy : MonoBehaviour
{
    public ModelAsset brainModel;
    private IWorker worker;
    private Model model;
    
    public Transform player;
    public float moveSpeed = 3f;
    public float detectionRange = 10f;

    void Start()
    {
        model = ModelLoader.Load(brainModel);
        worker = WorkerFactory.CreateWorker(BackendType.GPUCompute, model);
    }

    void Update()
    {
        float[] state = GetGameState();
        int action = DecideAction(state);
        ExecuteAction(action);
    }

    float[] GetGameState()
    {
        Vector3 toPlayer = player.position - transform.position;
        return new float[] {
            toPlayer.x,
            toPlayer.y,
            toPlayer.magnitude,
            transform.position.x,
            transform.position.y
        };
    }

    int DecideAction(float[] state)
    {
        var inputShape = new TensorShape(1, state.Length);
        using var input = new TensorFloat(inputShape, state);
        
        worker.Execute(input);
        var output = worker.PeekOutput() as TensorFloat;
        output.CompleteOperationsAndDownload();
        
        float[] actions = output.ToReadOnlyArray();
        return System.Array.IndexOf(actions, Mathf.Max(actions));
    }

    void ExecuteAction(int action)
    {
        switch(action)
        {
            case 0: // Move towards player
                transform.position = Vector3.MoveTowards(transform.position, player.position, moveSpeed * Time.deltaTime);
                break;
            case 1: // Move away
                transform.position = Vector3.MoveTowards(transform.position, player.position, -moveSpeed * Time.deltaTime);
                break;
            case 2: // Patrol
                transform.Translate(Vector3.right * moveSpeed * Time.deltaTime);
                break;
        }
    }

    void OnDestroy()
    {
        worker?.Dispose();
    }
}"""
        
        # Player behavior predictor
        player_predictor = """using Unity.Sentis;
using UnityEngine;

public class PlayerPredictor : MonoBehaviour
{
    public ModelAsset predictorModel;
    private IWorker worker;
    private Model model;
    
    private Vector3[] positionHistory = new Vector3[10];
    private int historyIndex = 0;

    void Start()
    {
        model = ModelLoader.Load(predictorModel);
        worker = WorkerFactory.CreateWorker(BackendType.GPUCompute, model);
    }

    void Update()
    {
        positionHistory[historyIndex] = transform.position;
        historyIndex = (historyIndex + 1) % positionHistory.Length;
    }

    public Vector3 PredictNextPosition()
    {
        float[] input = new float[positionHistory.Length * 3];
        for(int i = 0; i < positionHistory.Length; i++)
        {
            input[i * 3] = positionHistory[i].x;
            input[i * 3 + 1] = positionHistory[i].y;
            input[i * 3 + 2] = positionHistory[i].z;
        }
        
        var inputShape = new TensorShape(1, input.Length);
        using var inputTensor = new TensorFloat(inputShape, input);
        
        worker.Execute(inputTensor);
        var output = worker.PeekOutput() as TensorFloat;
        output.CompleteOperationsAndDownload();
        
        float[] prediction = output.ToReadOnlyArray();
        return new Vector3(prediction[0], prediction[1], prediction[2]);
    }

    void OnDestroy()
    {
        worker?.Dispose();
    }
}"""
        
        # Game difficulty adjuster
        difficulty_ai = """using Unity.Sentis;
using UnityEngine;

public class DifficultyAI : MonoBehaviour
{
    public ModelAsset difficultyModel;
    private IWorker worker;
    private Model model;
    
    public float currentDifficulty = 1f;
    private float playerScore = 0f;
    private float playerDeaths = 0f;
    private float playTime = 0f;

    void Start()
    {
        model = ModelLoader.Load(difficultyModel);
        worker = WorkerFactory.CreateWorker(BackendType.GPUCompute, model);
    }

    void Update()
    {
        playTime += Time.deltaTime;
        
        if(Time.frameCount % 300 == 0) // Every 5 seconds
        {
            AdjustDifficulty();
        }
    }

    void AdjustDifficulty()
    {
        float[] metrics = new float[] {
            playerScore,
            playerDeaths,
            playTime,
            currentDifficulty
        };
        
        var inputShape = new TensorShape(1, metrics.Length);
        using var input = new TensorFloat(inputShape, metrics);
        
        worker.Execute(input);
        var output = worker.PeekOutput() as TensorFloat;
        output.CompleteOperationsAndDownload();
        
        currentDifficulty = Mathf.Clamp(output.ToReadOnlyArray()[0], 0.5f, 3f);
        Debug.Log($"Difficulty adjusted to: {currentDifficulty}");
    }

    public void OnPlayerScore(float points)
    {
        playerScore += points;
    }

    public void OnPlayerDeath()
    {
        playerDeaths++;
    }

    void OnDestroy()
    {
        worker?.Dispose();
    }
}"""
        
        # Save all scripts
        scripts = {
            "AIEnemy.cs": enemy_ai,
            "PlayerPredictor.cs": player_predictor,
            "DifficultyAI.cs": difficulty_ai
        }
        
        created = []
        for filename, code in scripts.items():
            filepath = self.output_dir / filename
            filepath.write_text(code, encoding='utf-8')
            created.append(str(filepath))
            log_info("unity_sentis", f"Created: {filepath}")
        
        return f"Game AI scripts created:\n" + "\n".join(created)
    
    @classmethod
    def schema(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "command": {"type": "string", "description": "Sentis command"}
            }
        }
