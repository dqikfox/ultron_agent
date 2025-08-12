@echo off
echo 🤖 Setting up Ultron Assistant Frontend...

cd /d "%~dp0"

echo 📦 Installing dependencies...
call npm install

echo 🚀 Starting Ultron Assistant frontend...
echo Make sure the backend server is running on http://127.0.0.1:8000
echo Frontend will be available at http://localhost:3000

call npm run dev
pause
