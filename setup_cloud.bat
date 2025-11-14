@echo off
REM ULTRON Agent - Cloud Setup Script
REM Sets up AWS and Azure integration

echo ========================================
echo ULTRON Agent - Cloud Setup
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    exit /b 1
)

echo [1/5] Installing AWS SDK...
pip install boto3 botocore --quiet
if errorlevel 1 (
    echo ERROR: Failed to install AWS SDK
    exit /b 1
)
echo     AWS SDK installed

echo [2/5] Installing Azure SDK...
pip install azure-identity azure-storage-blob azure-cosmos openai --quiet
if errorlevel 1 (
    echo ERROR: Failed to install Azure SDK
    exit /b 1
)
echo     Azure SDK installed

echo [3/5] Checking AWS credentials...
aws sts get-caller-identity >nul 2>&1
if errorlevel 1 (
    echo     AWS credentials not configured
    echo     Run: aws configure
) else (
    echo     AWS credentials OK
)

echo [4/5] Checking Azure credentials...
if defined AZURE_OPENAI_KEY (
    echo     Azure OpenAI key found
) else (
    echo     Azure OpenAI key not set
    echo     Set: AZURE_OPENAI_KEY environment variable
)

echo [5/5] Creating cloud config...
if not exist "cloud_config.json" (
    echo {> cloud_config.json
    echo   "aws": {>> cloud_config.json
    echo     "region": "us-east-1",>> cloud_config.json
    echo     "bedrock_model": "claude-3-sonnet",>> cloud_config.json
    echo     "s3_bucket": "ultron-agent-memory">> cloud_config.json
    echo   },>> cloud_config.json
    echo   "azure": {>> cloud_config.json
    echo     "openai_model": "gpt-4-turbo",>> cloud_config.json
    echo     "endpoint": "https://YOUR_ENDPOINT.openai.azure.com/">> cloud_config.json
    echo   },>> cloud_config.json
    echo   "routing": {>> cloud_config.json
    echo     "default_provider": "aws",>> cloud_config.json
    echo     "fallback_to_local": true,>> cloud_config.json
    echo     "cost_limit_monthly": 150>> cloud_config.json
    echo   }>> cloud_config.json
    echo }>> cloud_config.json
    echo     Created cloud_config.json
) else (
    echo     cloud_config.json exists
)

echo.
echo ========================================
echo Setup Complete
echo ========================================
echo.
echo Next Steps:
echo 1. Configure AWS: aws configure
echo 2. Set Azure key: set AZURE_OPENAI_KEY=your_key
echo 3. Edit cloud_config.json with your settings
echo 4. Test: python -c "from tools.cloud_router import CloudRouter; print('OK')"
echo.
pause
