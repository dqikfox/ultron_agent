using System.Collections.Generic;
using Unity.Services.Authentication;
using Unity.Services.CloudCode;
using Unity.Services.Core;
using UnityEngine;

public class CloudCodeExample : MonoBehaviour
{
    private class CloudCodeResponse
    {
        public string welcomeMessage;
    }

    public async void Awake()
    {
        await UnityServices.InitializeAsync();
        await AuthenticationService.Instance.SignInAnonymouslyAsync();
    }

    public async void OnClick()
    {
        var arguments = new Dictionary<string, object> { { "name", "ULTRON" } };
        var response = await CloudCodeService.Instance.CallEndpointAsync<CloudCodeResponse>("hello-world", arguments);
        Debug.Log(response.welcomeMessage);
    }
}
