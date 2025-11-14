```csharp
using UnityEngine;
using UnityEngine.SceneManagement;

public class GameManager : MonoBehaviour
{
    private static GameManager _instance;
    public static GameManager Instance { get { return _instance; } }

    [Header("Game Settings")]
    public int maxLives = 3;
    public int scorePerLevel = 1000;

    [Header("Game State")]
    [SerializeField] private int _score = 0;
    [SerializeField] private int _lives = 3;
    [SerializeField] private int _level = 1;
    [SerializeField] private bool _isGameActive = false;

    public int Score { get { return _score; } }
    public int Lives { get { return _lives; } }
    public int Level { get { return _level; } }
    public bool IsGameActive { get { return _isGameActive; } }

    public delegate void OnScoreChanged(int newScore);
    public event OnScoreChanged scoreChanged;

    public delegate void OnLivesChanged(int newLives);
    public event OnLivesChanged livesChanged;

    public delegate void OnLevelChanged(int newLevel);
    public event OnLevelChanged levelChanged;

    public delegate void OnGameOver();
    public event OnGameOver gameOver;

    public delegate void OnGameStarted();
    public event OnGameStarted gameStarted;

    private void Awake()
    {
        if (_instance != null && _instance != this)
        {
            Destroy(gameObject);
        }
        else
        {
            _instance = this;
            DontDestroyOnLoad(gameObject);
            InitializeGame();
        }
    }

    private void InitializeGame()
    {
        _score = 0;
        _lives = maxLives;
        _level = 1;
        _isGameActive = false;
    }

    public void StartGame()
    {
        _isGameActive = true;
        gameStarted?.Invoke();
    }

    public void AddScore(int points)
    {
        if (!_isGameActive) return;

        _score += points;
        scoreChanged?.Invoke(_score);

        // Check for level up
        if (_score >= _level * scorePerLevel)
        {
            LevelUp();
        }
    }

    private void LevelUp()
    {
        _level++;
        levelChanged?.Invoke(_level);
    }

    public void LoseLife()
    {
        if (!_isGameActive) return;

        _lives--;
        livesChanged?.Invoke(_lives);

        if (_lives <= 0)
        {
            GameOver();
        }
    }

    public void AddLife()
    {
        _lives++;
        livesChanged?.Invoke(_lives);
    }

    private void GameOver()
    {
        _isGameActive = false;
        gameOver?.Invoke();
    }

    public void RestartGame()
    {
        InitializeGame();
        SceneManager.LoadScene(SceneManager.GetActiveScene().name);
    }

    public void LoadNextLevel()
    {
        int nextSceneIndex = SceneManager.GetActiveScene().buildIndex + 1;
        if (nextSceneIndex < SceneManager.sceneCountInBuildSettings)
        {
            SceneManager.LoadScene(nextSceneIndex);
        }
        else
        {
            // If no more levels, loop back to first level
            SceneManager.LoadScene(0);
        }
    }

    public void ResetGame()
    {
        InitializeGame();
    }

    public void PauseGame()
    {
        if (_isGameActive)
        {
            _isGameActive = false;
            Time.timeScale = 0f;
        }
    }

    public void ResumeGame()
    {
        if (!_isGameActive)
        {
            _isGameActive = true;
            Time.timeScale = 1f;
        }
    }
}
```