using System.Threading.Tasks;
using Unity.Services.CloudCode.Core;

namespace UltronModule
{
    public class UltronCommands
    {
        [CloudCodeFunction("ExecuteCommand")]
        public async Task<CommandResponse> ExecuteCommand(IExecutionContext context, string command)
        {
            var userId = context.PlayerId;
            
            // Rate limiting
            var rateLimitKey = $"rate_{userId}";
            var count = await context.DataAccess.GetAsync<int>(rateLimitKey) ?? 0;
            
            if (count >= 10)
            {
                return new CommandResponse
                {
                    Success = false,
                    Error = "Rate limit exceeded",
                    RetryAfter = 60
                };
            }
            
            await context.DataAccess.SetAsync(rateLimitKey, count + 1, 60);
            
            return new CommandResponse
            {
                Success = true,
                Command = command,
                Response = $"ULTRON executing: {command}",
                UserId = userId
            };
        }

        [CloudCodeFunction("GetStatus")]
        public Task<StatusResponse> GetStatus(IExecutionContext context)
        {
            return Task.FromResult(new StatusResponse
            {
                Status = "online",
                Version = "1.0.0",
                PlayerId = context.PlayerId
            });
        }
    }

    public class CommandResponse
    {
        public bool Success { get; set; }
        public string Command { get; set; }
        public string Response { get; set; }
        public string Error { get; set; }
        public int RetryAfter { get; set; }
        public string UserId { get; set; }
    }

    public class StatusResponse
    {
        public string Status { get; set; }
        public string Version { get; set; }
        public string PlayerId { get; set; }
    }
}
