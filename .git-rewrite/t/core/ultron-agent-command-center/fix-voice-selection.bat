@echo off
echo Fixing ElevenLabs Voice Selection Issues...

echo.
echo 1. Installing dependencies...
call npm install

echo.
echo 2. Building application...
call npm run build

echo.
echo 3. Starting application...
call npm run dev

echo.
echo Voice selection should now work properly!
echo - System voices will always be available
echo - ElevenLabs voices will appear if API key is configured
echo - Check the .env file to add your ElevenLabs API key

pause