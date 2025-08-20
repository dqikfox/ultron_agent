@echo off
echo ========================================
echo ULTRON AGENT - DEBUG AND REBUILD
echo ========================================

cd /d "%~dp0"

echo [1/6] Cleaning previous build...
if exist "dist" rmdir /s /q "dist"
if exist "release" rmdir /s /q "release"

echo [2/6] Installing dependencies...
npm install

echo [3/6] Running TypeScript check...
npx tsc --noEmit

echo [4/6] Building application...
npm run build

echo [5/6] Packaging for Windows...
npm run dist:win

echo [6/6] Testing executable...
if exist "release\win-unpacked\Ultron Agent Command Center.exe" (
    echo ✅ Build successful!
    echo Starting application for testing...
    start "" "release\win-unpacked\Ultron Agent Command Center.exe"
) else (
    echo ❌ Build failed - executable not found
)

echo.
echo Build complete! Check console for any errors.
pause