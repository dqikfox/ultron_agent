@echo off
echo Building Ultron Agent Command Center with auto-conversation fixes...

cd /d "%~dp0"

echo Installing dependencies...
npm install

echo Building application...
npm run build

echo Packaging for Windows...
npm run dist:win

echo Build complete! Check release folder for updated executable.
pause