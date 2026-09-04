@echo off
setlocal enabledelayedexpansion

echo 🎮 ULTRON Unity 6000.2.9f1 Setup
echo =================================
echo.

:: Your Unity installation path
set "UNITY_EDITOR=C:\Program Files\Unity\Hub\Editor\6000.2.9f1\Editor\Unity.exe"

:: Check if Unity exists
if not exist "%UNITY_EDITOR%" (
    echo ❌ Unity Editor not found at: %UNITY_EDITOR%
    echo Please verify your Unity installation path.
    pause
    exit /b 1
)

echo ✅ Unity Editor found: 6000.2.9f1
echo.

:: Create project
set /p PROJECT_NAME="Enter project name (or press Enter for 'UltronAIGame'): "
if "%PROJECT_NAME%"=="" set PROJECT_NAME=UltronAIGame

set "PROJECTS_DIR=%USERPROFILE%\Unity Projects"
set "PROJECT_PATH=%PROJECTS_DIR%\%PROJECT_NAME%"

if exist "%PROJECT_PATH%" (
    echo ❌ Project already exists: %PROJECT_PATH%
    set /p OVERWRITE="Overwrite existing project? (y/n): "
    if /i not "%OVERWRITE%"=="y" exit /b 1
    rmdir /s /q "%PROJECT_PATH%"
)

echo 📁 Creating Unity project structure...
mkdir "%PROJECT_PATH%"
mkdir "%PROJECT_PATH%\Assets"
mkdir "%PROJECT_PATH%\Assets\Scripts"
mkdir "%PROJECT_PATH%\Assets\Scripts\ULTRON"
mkdir "%PROJECT_PATH%\Assets\Scenes"
mkdir "%PROJECT_PATH%\ProjectSettings"

echo 📋 Copying ULTRON integration files...
copy "UnityUltronClient.cs" "%PROJECT_PATH%\Assets\Scripts\ULTRON\" >nul 2>&1
copy "UnityExampleUsage.cs" "%PROJECT_PATH%\Assets\Scripts\ULTRON\" >nul 2>&1

echo 🔧 Creating Unity 6000.2.9f1 project settings...
(
echo m_EditorVersion: 6000.2.9f1
echo m_EditorVersionWithRevision: 6000.2.9f1 ^(Unity 6000.2.9f1^)
) > "%PROJECT_PATH%\ProjectSettings\ProjectVersion.txt"

echo 🚀 Starting ULTRON integration server...
start "ULTRON Unity Server" python unity_integration.py

echo.
echo ✅ Setup complete!
echo.
echo 📍 Project: %PROJECT_PATH%
echo 🎮 Unity: 6000.2.9f1
echo 🤖 Server: http://localhost:9000
echo.

set /p OPEN_UNITY="Open project in Unity? (y/n): "
if /i "%OPEN_UNITY%"=="y" (
    echo Opening Unity...
    start "" "%UNITY_EDITOR%" -projectPath "%PROJECT_PATH%"
)

echo.
echo 📖 Next steps:
echo 1. Unity should open with your project
echo 2. Create a GameObject and add UnityUltronClient component
echo 3. Test with: client.SendChatMessage("Hello ULTRON!")
echo.
pause