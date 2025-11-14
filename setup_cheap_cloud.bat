@echo off
REM ULTRON Agent - CHEAP Cloud Setup ($8/month)

echo ========================================
echo ULTRON Agent - CHEAP Cloud Setup
echo Cost: $8-10/month
echo ========================================
echo.

echo [1/4] Installing packages...
pip install groq b2sdk --quiet
echo     Packages installed

echo.
echo [2/4] Setup Instructions:
echo.
echo === Groq API ($3/month) ===
echo 1. Visit: https://console.groq.com/keys
echo 2. Create API key
echo 3. Run: setx GROQ_API_KEY "gsk_your_key"
echo.
echo === Railway ($5/month) ===
echo 1. Run: npm i -g @railway/cli
echo 2. Run: railway login
echo 3. Run: railway init
echo 4. Run: railway up
echo.
echo === Backblaze B2 ($0.50/month) ===
echo 1. Visit: https://www.backblaze.com/b2/sign-up.html
echo 2. Create bucket named "ultron-memory"
echo 3. Get App Key from dashboard
echo 4. Run: setx B2_KEY_ID "your_key_id"
echo 5. Run: setx B2_APP_KEY "your_app_key"
echo.

echo [3/4] Creating test script...
(
echo from tools.cheap_cloud import CheapCloud
echo import asyncio
echo.
echo async def test^(^):
echo     cloud = CheapCloud^(^)
echo     print^("Status:", cloud.get_status^(^)^)
echo.
echo     if cloud.groq_client:
echo         result = await cloud.chat^("Hello!"^)
echo         print^(f"Groq: {result}"^)
echo.
echo asyncio.run^(test^(^)^)
) > test_cheap_cloud.py
echo     Test script created

echo.
echo [4/4] Creating Railway config...
(
echo [build]
echo builder = "NIXPACKS"
echo.
echo [deploy]
echo startCommand = "python main.py"
echo healthcheckPath = "/health"
echo restartPolicyType = "ON_FAILURE"
) > railway.toml
echo     Railway config created

echo.
echo ========================================
echo Setup Complete
echo ========================================
echo.
echo Next Steps:
echo 1. Get Groq API key (https://console.groq.com/keys)
echo 2. Install Railway CLI: npm i -g @railway/cli
echo 3. Create Backblaze B2 account
echo 4. Set environment variables
echo 5. Restart terminal
echo 6. Run: python test_cheap_cloud.py
echo.
echo Total Cost: $8.50/month
echo - Groq: $3/mo (10x faster AI)
echo - Railway: $5/mo (24/7 hosting)
echo - Backblaze: $0.50/mo (100GB storage)
echo.
pause
