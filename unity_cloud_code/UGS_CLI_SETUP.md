# UGS CLI Setup for Cloud Code C# Modules

## Installation

### 1. Install UGS CLI (2 minutes)
```bash
# Download from Unity
# https://unity.com/products/unity-gaming-services/cli

# Or use npm (alternative)
npm install -g @unity/ugs-cli

# Verify installation
ugs --version
```

### 2. Login to Unity Services (1 minute)
```bash
ugs login
# Opens browser for authentication
```

### 3. Configure Project (1 minute)
```bash
cd unity_cloud_code/UltronModule

# Set project ID (get from Unity Dashboard)
ugs config set project-id YOUR_PROJECT_ID

# Set environment
ugs config set environment-id production
```

## Deploy C# Module

### 1. Build Module (1 minute)
```bash
cd UltronModule
dotnet build
```

### 2. Deploy to Cloud Code (2 minutes)
```bash
# Deploy module
ugs deploy UltronModule

# Or use specific command
ugs cloud-code modules deploy
```

### 3. Verify Deployment (30 seconds)
```bash
# List deployed modules
ugs cloud-code modules list

# Get module details
ugs cloud-code modules get UltronModule
```

## Module Structure

```
UltronModule/
├── .ccmconfig              # Module configuration
├── UltronModule.csproj     # C# project file
└── src/
    └── UltronCommands.cs   # Cloud Code functions
```

## Available Functions

### ExecuteCommand
```csharp
[CloudCodeFunction("ExecuteCommand")]
public async Task<CommandResponse> ExecuteCommand(
    IExecutionContext context, 
    string command
)
```

**Usage from Unity**:
```csharp
var result = await CloudCodeService.Instance
    .CallModuleEndpointAsync<CommandResponse>(
        "UltronModule", 
        "ExecuteCommand", 
        new { command = "test" }
    );
```

### GetStatus
```csharp
[CloudCodeFunction("GetStatus")]
public Task<StatusResponse> GetStatus(IExecutionContext context)
```

**Usage from Unity**:
```csharp
var status = await CloudCodeService.Instance
    .CallModuleEndpointAsync<StatusResponse>(
        "UltronModule", 
        "GetStatus", 
        new { }
    );
```

## Unity Client Integration

### Install Package
```
Window > Package Manager > Add by name:
com.unity.services.cloudcode@2.10.0
```

### Call Module Functions
```csharp
using Unity.Services.CloudCode;

public class UltronModuleClient : MonoBehaviour
{
    public async Task<string> ExecuteCommand(string command)
    {
        var response = await CloudCodeService.Instance
            .CallModuleEndpointAsync<CommandResponse>(
                "UltronModule",
                "ExecuteCommand",
                new { command = command }
            );
        
        return response.Success ? response.Response : response.Error;
    }
}
```

## UGS CLI Commands Reference

### Authentication
```bash
ugs login                    # Login to Unity Services
ugs logout                   # Logout
ugs whoami                   # Show current user
```

### Configuration
```bash
ugs config set project-id <id>       # Set project
ugs config set environment-id <env>  # Set environment
ugs config list                      # Show config
```

### Cloud Code Modules
```bash
ugs cloud-code modules deploy        # Deploy module
ugs cloud-code modules list          # List modules
ugs cloud-code modules get <name>    # Get module details
ugs cloud-code modules delete <name> # Delete module
```

### Scripts (JavaScript)
```bash
ugs cloud-code scripts deploy <file> # Deploy script
ugs cloud-code scripts list          # List scripts
ugs cloud-code scripts get <name>    # Get script
```

## Get Project ID

1. Go to [Unity Dashboard](https://dashboard.unity3d.com/)
2. Select your project: **dqikst / My project (1)**
3. Click **Settings** (gear icon)
4. Copy **Project ID**
5. Update `.ccmconfig` with your Project ID

## Troubleshooting

### "ugs: command not found"
```bash
# Add to PATH
export PATH="$PATH:$HOME/.dotnet/tools"
```

### "Authentication failed"
```bash
ugs logout
ugs login
```

### "Project not found"
```bash
# Verify project ID
ugs config get project-id

# Update if wrong
ugs config set project-id YOUR_CORRECT_PROJECT_ID
```

## Next Steps

1. ✅ Install UGS CLI: `dotnet tool install -g Unity.Services.Cli`
2. ✅ Login: `ugs login`
3. ✅ Get Project ID from Unity Dashboard
4. ✅ Update `.ccmconfig` with Project ID
5. ✅ Build: `dotnet build`
6. ✅ Deploy: `ugs cloud-code modules deploy`
7. ✅ Test from Unity client

## Files Created
- `UltronModule.csproj` - C# project
- `src/UltronCommands.cs` - Cloud Code functions
- `.ccmconfig` - Module configuration
- `UGS_CLI_SETUP.md` - This guide
