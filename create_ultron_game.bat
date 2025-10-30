@echo off
echo Creating ULTRON Avatar Game...

set "UNITY_EDITOR=C:\Program Files\Unity\Hub\Editor\6000.2.9f1\Editor\Unity.exe"
set "PROJECT_NAME=UltronAvatarGame"
set "PROJECT_PATH=%USERPROFILE%\Unity Projects\%PROJECT_NAME%"

mkdir "%PROJECT_PATH%"
mkdir "%PROJECT_PATH%\Assets\Scripts\ULTRON"
mkdir "%PROJECT_PATH%\Assets\Prefabs\Avatars"
mkdir "%PROJECT_PATH%\Assets\Materials"
mkdir "%PROJECT_PATH%\Assets\Scenes"

copy "UnityUltronClient.cs" "%PROJECT_PATH%\Assets\Scripts\ULTRON\"
copy "UltronAvatarController.cs" "%PROJECT_PATH%\Assets\Scripts\ULTRON\"
copy "UltronGameManager.cs" "%PROJECT_PATH%\Assets\Scripts\ULTRON\"

echo m_EditorVersion: 6000.2.9f1 > "%PROJECT_PATH%\ProjectSettings\ProjectVersion.txt"

start "ULTRON Server" python unity_integration.py
start "" "%UNITY_EDITOR%" -projectPath "%PROJECT_PATH%"

echo Game project created and Unity opening...
pause