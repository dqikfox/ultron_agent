using System.Threading.Tasks;
using Unity.Services.CloudCode;
using UnityEngine;

public class UltronModuleClient : MonoBehaviour
{
    public async Task<string> ExecuteCommand(string command)
    {
        try
        {
            var response = await CloudCodeService.Instance
                .CallModuleEndpointAsync<CommandResponse>(
                    "UltronModule",
                    "ExecuteCommand",
                    new { command = command }
                );
            
            return response.Success ? response.Response : response.Error;
        }
        catch (System.Exception e)
        {
            return $"Error: {e.Message}";
        }
    }

    public async Task<string> GetStatus()
    {
        try
        {
            var response = await CloudCodeService.Instance
                .CallModuleEndpointAsync<StatusResponse>(
                    "UltronModule",
                    "GetStatus",
                    new { }
                );
            
            return $"Status: {response.Status}, Version: {response.Version}";
        }
        catch (System.Exception e)
        {
            return $"Error: {e.Message}";
        }
    }

    [System.Serializable]
    public class CommandResponse
    {
        public bool Success;
        public string Command;
        public string Response;
        public string Error;
        public int RetryAfter;
        public string UserId;
    }

    [System.Serializable]
    public class StatusResponse
    {
        public string Status;
        public string Version;
        public string PlayerId;
    }
}
