# ULTRON Agent Command Center - Silent Deployment Script
# For System Administrators

param(
    [string]$InstallPath = "C:\Program Files\UltronAgent",
    [string]$ZipFile = "Ultron-Agent-Command-Center-Windows-v1.0.0.zip",
    [switch]$CreateShortcut = $true,
    [switch]$ConfigureFirewall = $true,
    [switch]$SetPermissions = $true
)

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  ULTRON Agent Command Center" -ForegroundColor Red
Write-Host "  Silent Deployment Script" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Check if running as administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "This script must be run as Administrator"
    exit 1
}

try {
    # Create installation directory
    Write-Host "Creating installation directory: $InstallPath" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null

    # Extract application
    if (Test-Path $ZipFile) {
        Write-Host "Extracting application files..." -ForegroundColor Yellow
        Expand-Archive -Path $ZipFile -DestinationPath $InstallPath -Force
    } else {
        Write-Warning "Zip file not found: $ZipFile"
        Write-Host "Please ensure the zip file is in the current directory"
    }

    # Create desktop shortcut
    if ($CreateShortcut) {
        Write-Host "Creating desktop shortcut..." -ForegroundColor Yellow
        $WshShell = New-Object -comObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut("$env:PUBLIC\Desktop\ULTRON Agent.lnk")
        $Shortcut.TargetPath = "$InstallPath\win-unpacked\Ultron Agent Command Center.exe"
        $Shortcut.WorkingDirectory = "$InstallPath\win-unpacked"
        $Shortcut.IconLocation = "$InstallPath\win-unpacked\Ultron Agent Command Center.exe"
        $Shortcut.Description = "ULTRON Agent Command Center"
        $Shortcut.Save()
    }

    # Configure Windows Firewall
    if ($ConfigureFirewall) {
        Write-Host "Configuring Windows Firewall..." -ForegroundColor Yellow
        
        # Allow Ollama localhost connections
        New-NetFirewallRule -DisplayName "ULTRON-Ollama-Inbound" -Direction Inbound -Protocol TCP -LocalPort 11434 -Action Allow -Profile Any -ErrorAction SilentlyContinue
        New-NetFirewallRule -DisplayName "ULTRON-Ollama-Outbound" -Direction Outbound -Protocol TCP -LocalPort 11434 -Action Allow -Profile Any -ErrorAction SilentlyContinue
        
        # Allow ULTRON Agent
        New-NetFirewallRule -DisplayName "ULTRON-Agent-Inbound" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow -Profile Any -ErrorAction SilentlyContinue
        New-NetFirewallRule -DisplayName "ULTRON-Agent-Outbound" -Direction Outbound -Protocol TCP -LocalPort 8000 -Action Allow -Profile Any -ErrorAction SilentlyContinue
    }

    # Set microphone permissions via registry
    if ($SetPermissions) {
        Write-Host "Configuring microphone permissions..." -ForegroundColor Yellow
        
        # Enable microphone access for desktop apps
        $regPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\microphone"
        if (Test-Path $regPath) {
            Set-ItemProperty -Path $regPath -Name "Value" -Value "Allow" -ErrorAction SilentlyContinue
        }
        
        # Set app-specific permissions
        $appRegPath = "$regPath\NonPackaged"
        if (Test-Path $appRegPath) {
            Set-ItemProperty -Path $appRegPath -Name "Value" -Value "Allow" -ErrorAction SilentlyContinue
        }
    }

    # Copy configuration file
    Write-Host "Installing configuration file..." -ForegroundColor Yellow
    $configSource = "ultron-config.json"
    $configDest = "$InstallPath\ultron-config.json"
    
    if (Test-Path $configSource) {
        Copy-Item $configSource $configDest -Force
    } else {
        # Create default config if source doesn't exist
        $defaultConfig = @{
            ollamaUrl = "http://localhost:11434"
            elevenLabsApiKey = ""
            selectedVoice = "EXAVITQu4vr4xnSDxMaL"
            theme = "ultron-dark"
            audioSettings = @{
                pushToTalk = $true
                alwaysListening = $false
                voiceActivation = "spacebar"
            }
            uiSettings = @{
                showWaveform = $true
                glowEffects = $true
                animationSpeed = "normal"
            }
            voiceSettings = @{
                preventRepetition = $true
                maxRepeatWords = 1
                speechRate = 170
                speechVolume = 1.0
            }
        }
        $defaultConfig | ConvertTo-Json -Depth 3 | Out-File $configDest -Encoding UTF8
    }

    # Create start menu entry
    Write-Host "Creating Start Menu entry..." -ForegroundColor Yellow
    $startMenuPath = "$env:ALLUSERSPROFILE\Microsoft\Windows\Start Menu\Programs"
    $WshShell = New-Object -comObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut("$startMenuPath\ULTRON Agent Command Center.lnk")
    $Shortcut.TargetPath = "$InstallPath\win-unpacked\Ultron Agent Command Center.exe"
    $Shortcut.WorkingDirectory = "$InstallPath\win-unpacked"
    $Shortcut.IconLocation = "$InstallPath\win-unpacked\Ultron Agent Command Center.exe"
    $Shortcut.Description = "ULTRON Agent Command Center"
    $Shortcut.Save()

    Write-Host "=====================================" -ForegroundColor Green
    Write-Host "  DEPLOYMENT COMPLETED SUCCESSFULLY" -ForegroundColor Green
    Write-Host "=====================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Installation Path: $InstallPath" -ForegroundColor Cyan
    Write-Host "Desktop Shortcut: Created" -ForegroundColor Cyan
    Write-Host "Firewall Rules: Configured" -ForegroundColor Cyan
    Write-Host "Microphone Access: Enabled" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To launch ULTRON Agent:" -ForegroundColor Yellow
    Write-Host "1. Double-click desktop shortcut" -ForegroundColor White
    Write-Host "2. Or run: '$InstallPath\win-unpacked\Ultron Agent Command Center.exe'" -ForegroundColor White
    Write-Host ""
    Write-Host "Configuration file: $configDest" -ForegroundColor Yellow

} catch {
    Write-Error "Deployment failed: $($_.Exception.Message)"
    exit 1
}

Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")