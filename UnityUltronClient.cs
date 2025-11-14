using System;
using System.Collections;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;

namespace UltronAgent
{
    /// <summary>
    /// Unity client for ULTRON Agent integration
    /// </summary>
    public class UnityUltronClient : MonoBehaviour
    {
        [Header("ULTRON Connection")]
        public string ultronServerUrl = "http://localhost:9000";
        public string sessionId = "unity_game";
        public string gameName = "My Unity Game";
        
        [Header("Status")]
        public bool isConnected = false;
        
        private void Start()
        {
            StartCoroutine(ConnectToUltron());
        }
        
        /// <summary>
        /// Connect to ULTRON Agent
        /// </summary>
        public IEnumerator ConnectToUltron()
        {
            var connectData = new ConnectRequest
            {
                session_id = sessionId,
                game_name = gameName,
                version = Application.version
            };
            
            yield return StartCoroutine(PostRequest("/unity/connect", connectData, (response) =>
            {
                if (response.success)
                {
                    isConnected = true;
                    Debug.Log($"Connected to ULTRON Agent: {response.session_id}");
                }
                else
                {
                    Debug.LogError("Failed to connect to ULTRON Agent");
                }
            }));
        }
        
        /// <summary>
        /// Send chat message to ULTRON AI
        /// </summary>
        public void SendChatMessage(string message, System.Action<string> onResponse = null)
        {
            if (!isConnected)
            {
                Debug.LogWarning("Not connected to ULTRON Agent");
                return;
            }
            
            var chatData = new ChatRequest
            {
                message = message,
                session_id = sessionId
            };
            
            StartCoroutine(PostRequest("/unity/chat", chatData, (response) =>
            {
                if (response.success)
                {
                    Debug.Log($"ULTRON Response: {response.response}");
                    onResponse?.Invoke(response.response);
                }
            }));
        }
        
        /// <summary>
        /// Execute ULTRON command
        /// </summary>
        public void ExecuteCommand(string command, object parameters = null, System.Action<CommandResponse> onResponse = null)
        {
            var commandData = new CommandRequest
            {
                command = command,
                parameters = parameters ?? new { },
                session_id = sessionId
            };
            
            StartCoroutine(PostRequest("/unity/command", commandData, (response) =>
            {
                onResponse?.Invoke(response);
            }));
        }
        
        /// <summary>
        /// Get ULTRON agent status
        /// </summary>
        public void GetAgentStatus(System.Action<object> onResponse = null)
        {
            ExecuteCommand("get_status", null, (response) =>
            {
                onResponse?.Invoke(response.result);
            });
        }
        
        /// <summary>
        /// Analyze current Unity scene
        /// </summary>
        public void AnalyzeScene(System.Action<object> onResponse = null)
        {
            var sceneData = new
            {
                scene_data = new
                {
                    objects = FindObjectsOfType<GameObject>(),
                    scene_name = UnityEngine.SceneManagement.SceneManager.GetActiveScene().name
                }
            };
            
            ExecuteCommand("analyze_scene", sceneData, (response) =>
            {
                onResponse?.Invoke(response.result);
            });
        }
        
        /// <summary>
        /// Generate NPC dialogue
        /// </summary>
        public void GenerateDialogue(string character, string context, System.Action<object> onResponse = null)
        {
            var dialogueData = new
            {
                character = character,
                context = context
            };
            
            ExecuteCommand("generate_dialogue", dialogueData, (response) =>
            {
                onResponse?.Invoke(response.result);
            });
        }
        
        /// <summary>
        /// Generic HTTP POST request
        /// </summary>
        private IEnumerator PostRequest<T>(string endpoint, object data, System.Action<T> onResponse)
        {
            string json = JsonUtility.ToJson(data);
            byte[] bodyRaw = Encoding.UTF8.GetBytes(json);
            
            using (UnityWebRequest request = new UnityWebRequest(ultronServerUrl + endpoint, "POST"))
            {
                request.uploadHandler = new UploadHandlerRaw(bodyRaw);
                request.downloadHandler = new DownloadHandlerBuffer();
                request.SetRequestHeader("Content-Type", "application/json");
                
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    try
                    {
                        T response = JsonUtility.FromJson<T>(request.downloadHandler.text);
                        onResponse?.Invoke(response);
                    }
                    catch (Exception e)
                    {
                        Debug.LogError($"JSON Parse Error: {e.Message}");
                    }
                }
                else
                {
                    Debug.LogError($"Request Error: {request.error}");
                }
            }
        }
    }
    
    // Data structures for API communication
    [Serializable]
    public class ConnectRequest
    {
        public string session_id;
        public string game_name;
        public string version;
    }
    
    [Serializable]
    public class ChatRequest
    {
        public string message;
        public string session_id;
    }
    
    [Serializable]
    public class CommandRequest
    {
        public string command;
        public object parameters;
        public string session_id;
    }
    
    [Serializable]
    public class ConnectResponse
    {
        public bool success;
        public string session_id;
        public string agent_status;
    }
    
    [Serializable]
    public class ChatResponse
    {
        public bool success;
        public string response;
        public string session_id;
    }
    
    [Serializable]
    public class CommandResponse
    {
        public string command;
        public string status;
        public object result;
    }
}