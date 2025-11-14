@echo off
echo Starting ULTRON Avatar Game...

echo Checking Unity integration server...
curl -s http://localhost:9000/unity/connect > nul
if %errorlevel% neq 0 (
    echo Starting ULTRON server...
    start "ULTRON Server" python unity_integration.py
    timeout /t 3 > nul
)

echo Opening Unity project...
start "Unity Editor" "C:\Program Files\Unity\Hub\Editor\6000.2.9f1\Editor\Unity.exe" -projectPath "C:\Users\ultro\Unity Projects\UltronAvatarGame"

echo ULTRON Avatar Game launching...
echo.
echo Instructions:
echo 1. Unity will open with the project
echo 2. Open UltronAvatarScene.unity
echo 3. Press Play to start the game
echo 4. Press Space to spawn AI avatars
echo 5. Type in chat to interact with avatars
echo.
pause