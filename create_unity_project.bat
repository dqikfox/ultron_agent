@echo off
setlocal enabledelayedexpansion

echo 🎮 ULTRON Unity Project Creator
echo ===============================
echo.

set /p PROJECT_NAME="Enter project name (or press Enter for 'UltronGame'): "
if "%PROJECT_NAME%"=="" set PROJECT_NAME=UltronGame

echo.
echo Creating Unity project: %PROJECT_NAME%
echo.

:: Create project directory
set "PROJECTS_DIR=%USERPROFILE%\Unity Projects"
set "PROJECT_PATH=%PROJECTS_DIR%\%PROJECT_NAME%"

if exist "%PROJECT_PATH%" (
    echo ❌ Project already exists: %PROJECT_PATH%
    pause
    exit /b 1
)

echo 📁 Creating project directory...
mkdir "%PROJECT_PATH%"
mkdir "%PROJECT_PATH%\Assets"
mkdir "%PROJECT_PATH%\Assets\Scripts"
mkdir "%PROJECT_PATH%\Assets\Scripts\ULTRON"
mkdir "%PROJECT_PATH%\Assets\Scenes"
mkdir "%PROJECT_PATH%\Assets\Prefabs"
mkdir "%PROJECT_PATH%\ProjectSettings"

echo 📋 Copying ULTRON integration files...
copy "UnityUltronClient.cs" "%PROJECT_PATH%\Assets\Scripts\ULTRON\" >nul 2>&1
copy "UnityExampleUsage.cs" "%PROJECT_PATH%\Assets\Scripts\ULTRON\" >nul 2>&1

echo 🔧 Creating project settings...
echo m_EditorVersion: 2022.3.0f1 > "%PROJECT_PATH%\ProjectSettings\ProjectVersion.txt"
echo m_EditorVersionWithRevision: 2022.3.0f1 (fb119bb0b476) >> "%PROJECT_PATH%\ProjectSettings\ProjectVersion.txt"

echo 📄 Creating README...
(
echo # %PROJECT_NAME% - ULTRON Integration
echo.
echo This Unity project includes ULTRON Agent integration for AI-powered game features.
echo.
echo ## Quick Start
echo 1. Open project in Unity Hub
echo 2. Start ULTRON integration server: `start_unity_integration.bat`
echo 3. Add UnityUltronClient component to a GameObject
echo 4. Test connection with: `client.SendChatMessage("Hello ULTRON!"^)`
echo.
echo ## Features
echo - AI-powered NPCs
echo - Dynamic dialogue generation  
echo - Smart scene analysis
echo - Procedural content creation
echo.
echo ## Files
echo - `Assets/Scripts/ULTRON/UnityUltronClient.cs` - Main integration client
echo - `Assets/Scripts/ULTRON/UnityExampleUsage.cs` - Usage examples
echo.
echo Server URL: http://localhost:9000
) > "%PROJECT_PATH%\README.md"

echo.
echo ✅ Unity project created successfully!
echo.
echo 📍 Project location: %PROJECT_PATH%
echo.
echo 🚀 Next steps:
echo 1. Open Unity Hub
echo 2. Click "Add" and select: %PROJECT_PATH%
echo 3. Start ULTRON server: start_unity_integration.bat
echo 4. Open the project in Unity
echo.

set /p OPEN_FOLDER="Open project folder? (y/n): "
if /i "%OPEN_FOLDER%"=="y" (
    explorer "%PROJECT_PATH%"
)

echo.
pause