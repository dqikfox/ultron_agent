@echo off
echo Opening Unity game assets folder...
echo.
echo Copy these files to your Unity project:
echo.
echo FROM: %~dp0UnityGame\Assets
echo TO:   YourUnityProject\Assets
echo.
start explorer "%~dp0UnityGame\Assets"
echo.
echo Files ready:
echo - 6 C# Scripts (3 core + 3 AI)
echo - 2 ONNX Models (EnemyAI, DifficultyAI)
echo.
echo See UNITY_IMPORT_GUIDE.md for setup instructions
echo.
pause
