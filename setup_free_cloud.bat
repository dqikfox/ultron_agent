@echo off
REM ULTRON Agent - FREE Cloud Setup

echo ========================================
echo ULTRON Agent - FREE Cloud Setup
echo ========================================
echo.

echo [1/3] Installing FREE cloud packages...
pip install huggingface_hub supabase requests --quiet
echo     Packages installed

echo.
echo [2/3] Setup Instructions:
echo.
echo 1. Hugging Face (FREE):
echo    - Visit: https://huggingface.co/join
echo    - Get token: https://huggingface.co/settings/tokens
echo    - Run: setx HF_TOKEN "your_token"
echo.
echo 2. Supabase (FREE):
echo    - Visit: https://supabase.com
echo    - Create project (FREE tier)
echo    - Get URL and anon key from Settings
echo    - Run: setx SUPABASE_URL "your_url"
echo    - Run: setx SUPABASE_KEY "your_key"
echo.
echo 3. Vercel (FREE - Optional):
echo    - Run: npm i -g vercel
echo    - Run: vercel login
echo.

echo [3/3] Creating test script...
echo from tools.free_cloud_integration import FreeCloudIntegration > test_free_cloud.py
echo import asyncio >> test_free_cloud.py
echo. >> test_free_cloud.py
echo async def test(): >> test_free_cloud.py
echo     cloud = FreeCloudIntegration() >> test_free_cloud.py
echo     result = await cloud.chat_huggingface("Hello!") >> test_free_cloud.py
echo     print(f"Result: {result}") >> test_free_cloud.py
echo. >> test_free_cloud.py
echo asyncio.run(test()) >> test_free_cloud.py
echo     Test script created

echo.
echo ========================================
echo Setup Complete
echo ========================================
echo.
echo Next Steps:
echo 1. Get Hugging Face token (FREE)
echo 2. Create Supabase project (FREE)
echo 3. Set environment variables
echo 4. Restart terminal
echo 5. Run: python test_free_cloud.py
echo.
echo Total Cost: $0/month
echo.
pause
