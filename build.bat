@echo off
REM ULTRON Agent 3.0 - Docker Build Script (Windows)
REM Automates Docker image building for deployment
REM Usage: build.bat [--no-cache] [--push] [--version <version>]

setlocal enabledelayedexpansion

REM Configuration
set IMAGE_NAME=ultron-agent
set REGISTRY=%DOCKER_REGISTRY%
if "!REGISTRY!"=="" set REGISTRY=docker.io
set VERSION=%VERSION%
if "!VERSION!"=="" set VERSION=3.0.0
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set BUILD_DATE=%%c-%%a-%%b)
for /f "tokens=5-8 delims=/: " %%a in ('echo prompt $h ^| cmd') do (set BUILD_TIME=%%a:%%b:%%c)

REM Flags
set NO_CACHE=
set PUSH_IMAGE=false
set VERSION_OVERRIDE=false

REM Parse arguments
:parse_args
if "!1!"=="" goto end_parse
if "!1!"=="--no-cache" (
    set NO_CACHE=--no-cache
    shift
    goto parse_args
)
if "!1!"=="--push" (
    set PUSH_IMAGE=true
    shift
    goto parse_args
)
if "!1!"=="--version" (
    set VERSION=!2!
    set VERSION_OVERRIDE=true
    shift
    shift
    goto parse_args
)
shift
goto parse_args

:end_parse
echo.
echo ===============================================================
echo ULTRON Agent 3.0 - Docker Build Script
echo ===============================================================
echo.

REM Pre-build checks
echo [*] Running pre-build checks...

where docker >nul 2>nul
if errorlevel 1 (
    echo [!] Docker is not installed or not in PATH
    exit /b 1
)

docker ps >nul 2>nul
if errorlevel 1 (
    echo [!] Cannot connect to Docker daemon
    exit /b 1
)

if not exist "Dockerfile" (
    echo [!] Dockerfile not found in current directory
    exit /b 1
)

echo [+] Docker is available
echo [+] Dockerfile found
echo.

REM Build information
echo [*] Build Information:
echo   Image Name:     %IMAGE_NAME%
echo   Registry:       %REGISTRY%
echo   Version:        %VERSION%
echo   Build Date:     %BUILD_DATE% %BUILD_TIME%
echo   No Cache:       %NO_CACHE%
echo   Push After:     %PUSH_IMAGE%
echo.

REM Build Docker image
echo [*] Building Docker image...
echo.

set BUILD_TAG=%REGISTRY%/%IMAGE_NAME%:%VERSION%
set BUILD_TAG_LATEST=%REGISTRY%/%IMAGE_NAME%:latest

docker build %NO_CACHE% ^
    --tag "%BUILD_TAG%" ^
    --tag "%BUILD_TAG_LATEST%" ^
    --build-arg BUILD_DATE="%BUILD_DATE%T%BUILD_TIME%Z" ^
    --build-arg VERSION="%VERSION%" .

if errorlevel 1 (
    echo.
    echo [!] Docker image build failed
    exit /b 1
)

echo.
echo [+] Docker image built successfully
echo.

REM Show image information
echo [*] Image Information:
docker images %IMAGE_NAME% --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
echo.

REM Optional: Push to registry
if /i "%PUSH_IMAGE%"=="true" (
    echo [*] Pushing image to registry...
    echo.

    docker push "%BUILD_TAG%"
    if errorlevel 1 (
        echo [!] Image push failed
        exit /b 1
    )
    echo [+] Image pushed successfully: %BUILD_TAG%
    echo.

    docker push "%BUILD_TAG_LATEST%"
    if errorlevel 1 (
        echo [!] Image push failed
        exit /b 1
    )
    echo [+] Image pushed successfully: %BUILD_TAG_LATEST%
    echo.
)

REM Display next steps
echo.
echo ===============================================================
echo [+] Build Complete!
echo ===============================================================
echo.
echo [*] Next Steps:
echo.
echo 1. Start services with docker-compose:
echo    docker-compose up -d
echo.
echo 2. View logs:
echo    docker-compose logs -f ultron-agent
echo.
echo 3. Check health:
echo    curl http://localhost:5000/health
echo.
echo 4. Stop services:
echo    docker-compose down
echo.

if /i "%PUSH_IMAGE%"=="false" (
    echo [*] Note: Image was not pushed to registry.
    echo    Use --push flag to push to registry:
    echo    build.bat --push
    echo.
)

echo [+] Build script completed successfully!
echo.

pause
