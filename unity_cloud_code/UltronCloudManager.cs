using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Unity.Services.Authentication;
using Unity.Services.CloudCode;
using Unity.Services.Core;
using UnityEngine;

public class UltronCloudManager : MonoBehaviour
{
    private bool isInitialized = false;

    async void Start()
    {
        await InitializeUnityServices();
    }

    async Task InitializeUnityServices()
    {
        try
        {
            await UnityServices.InitializeAsync();
            await AuthenticationService.Instance.SignInAnonymouslyAsync();
            isInitialized = true;
            Debug.Log("Unity Services initialized");
        }
        catch (Exception e)
        {
            Debug.LogError($"Initialization failed: {e.Message}");
        }
    }

    public async Task<string> ExecuteCommand(string command)
    {
        if (!isInitialized) return "Service not initialized";

        var args = new Dictionary<string, object>
        {
            { "command", command },
            { "userId", AuthenticationService.Instance.PlayerId }
        };

        try
        {
            var response = await CloudCodeService.Instance.CallEndpointAsync<CommandResponse>("ultron-command", args);
            return response.success ? response.response : response.error;
        }
        catch (Exception e)
        {
            return $"Error: {e.Message}";
        }
    }

    [Serializable]
    private class CommandResponse
    {
        public bool success;
        public string command;
        public string response;
        public string error;
        public long timestamp;
    }
}
