# Quick Command Reference - ULTRON Agent 3.0

## 🚀 Installation & Setup (Phase 4-6)

### Phase 4: Install Dependencies (15-25 min)
```powershell
# Run main installation script
.\setup_requirements.bat

# Or manually:
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Phase 5: Configure AWS (Optional)
```powershell
# Configure AWS credentials
aws configure

# Verify AWS credentials
aws sts get-caller-identity

# List S3 buckets (test access)
aws s3 ls
```

### Phase 6: Launch Agent
```powershell
# Activate environment
.\.venv\Scripts\Activate.ps1

# Start agent
python main.py

# In browser:
http://localhost:8080
```

---

## 🔍 Verification & Diagnostics

### Check Installation Status
```powershell
# Run verification script
.\verify_setup.bat

# Manual checks:
aws --version
python --version
pip list
```

### Test Critical Packages
```powershell
# With venv activated:
python -c "import flask, aiohttp, torch, transformers, openai; print('All OK')"

# Individual package tests:
python -c "import flask; print(flask.__version__)"
```

### Check Environment
```powershell
# Show virtual environment status
$env:VIRTUAL_ENV

# List Python path
python -c "import sys; print(sys.prefix)"

# Check pip location
pip --version
```

---

## 📦 Dependency Management

### Install/Update Packages
```powershell
# Install from requirements
pip install -r requirements.txt

# Upgrade all packages
pip install --upgrade -r requirements.txt

# Force reinstall (fixes conflicts)
pip install --force-reinstall -r requirements.txt

# Install single package
pip install package-name

# Install specific version
pip install package-name==1.0.0
```

### Package Information
```powershell
# List all installed packages
pip list

# Show specific package info
pip show flask

# Check for conflicts
pip check

# Generate requirements from current environment
pip freeze > requirements.txt
```

---

## 🤖 Running ULTRON Agent

### Basic Startup
```powershell
# Navigate to project
cd C:\Projects\ultron_agent

# Activate environment
.\.venv\Scripts\Activate.ps1

# Run agent
python main.py

# Open GUI
http://localhost:8080
```

### Start Individual Services
```powershell
# Web GUI Server (port 8080)
python web_gui_server.py

# API Server (port 5000)
python api_server.py

# Start Ollama (if installed)
.\run.bat
```

### Background Services
```powershell
# Start in background (requires -WindowStyle)
Start-Process python -ArgumentList "main.py" -WindowStyle Minimized

# Or in another terminal:
# Terminal 1:
python main.py

# Terminal 2:
python api_server.py
```

---

## 🧪 Testing

### Run Tests
```powershell
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_main.py -v

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific marker
pytest -m unit
pytest -m integration
```

---

## 🐛 Troubleshooting

### Virtual Environment Issues
```powershell
# Check if activated
# Should show (.venv) in prompt

# Activate if needed
.\.venv\Scripts\Activate.ps1

# Deactivate
deactivate

# Fix permission errors
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# Recreate environment if corrupted
rmdir .venv /s /q
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Package Issues
```powershell
# Fix installation conflicts
pip check
pip install --force-reinstall -r requirements.txt

# Clean pip cache
pip cache purge

# Upgrade pip/setuptools/wheel
python -m pip install --upgrade pip setuptools wheel

# List broken packages
pip list --outdated
```

### Port Issues
```powershell
# Find what's using port 8080
netstat -ano | findstr :8080

# Find process using port
Get-Process | Where-Object {$_.Id -eq <PID>}

# Kill process (if needed)
Stop-Process -Id <PID> -Force

# Change port in ultron_config.json
"web_port": 8081
```

### AWS Issues
```powershell
# Test AWS CLI
aws --version

# Test credentials
aws sts get-caller-identity

# Reconfigure credentials
aws configure

# Use different profile
aws configure --profile ultron-agent

# Clear credentials
Remove-Item $env:USERPROFILE\.aws\credentials

# Check environment variables
$env:AWS_ACCESS_KEY_ID
$env:AWS_SECRET_ACCESS_KEY
```

---

## 📊 Monitoring & Logs

### View Logs
```powershell
# Agent core log
Get-Content logs\agent_core.log -Tail 50

# Brain (AI) log
Get-Content logs\brain.log -Tail 50

# AI activities log
Get-Content logs\ai_activities.log -Tail 50

# Real-time monitoring
Get-Content logs\agent_core.log -Wait
```

### System Resources
```powershell
# Check disk space
Get-Volume C:

# Check memory
Get-WmiObject Win32_OperatingSystem | Select-Object TotalVisibleMemorySize

# Check running processes
Get-Process python
Get-Process ollama
```

---

## 🔐 Security & Configuration

### Environment Variables
```powershell
# Set temporarily
$env:ELEVENLABS_APIKEY = "your-key"
$env:OPENAI_API_KEY = "your-key"

# View variable
$env:ELEVENLABS_APIKEY

# Check all variables
Get-ChildItem env: | Where-Object {$_.Name -like "*ELEVENLABS*"}
```

### AWS Credentials Management
```powershell
# Create/update credentials file
aws configure

# View credentials (carefully!)
type $env:USERPROFILE\.aws\credentials

# Set AWS profile
$env:AWS_PROFILE = "ultron-agent"

# List profiles
Get-Content $env:USERPROFILE\.aws\config
```

### Configuration Files
```powershell
# View agent config
type ultron_config.json

# Edit config
notepad ultron_config.json

# Validate JSON
python -m json.tool ultron_config.json
```

---

## 📁 File Operations

### Navigation
```powershell
# Navigate to project
cd C:\Projects\ultron_agent

# List files
ls
dir

# Show tree structure
tree /L /F

# Find files
Get-ChildItem -Recurse -Filter "*.py"
```

### File Management
```powershell
# Create backup
Copy-Item -Path "ultron_config.json" -Destination "ultron_config.json.bak"

# Find recently modified files
Get-ChildItem -Recurse | Sort-Object LastWriteTime -Descending | Select-Object -First 10

# Count files
Get-ChildItem -Recurse -Filter "*.py" | Measure-Object
```

---

## 🎯 Common Workflows

### Daily Development
```powershell
# 1. Start terminal
pwsh

# 2. Navigate to project
cd C:\Projects\ultron_agent

# 3. Activate environment
.\.venv\Scripts\Activate.ps1

# 4. Run agent
python main.py

# 5. In another terminal, run tests
pytest tests/ -v

# 6. When done, deactivate
deactivate
```

### Updating Dependencies
```powershell
# 1. Activate venv
.\.venv\Scripts\Activate.ps1

# 2. Check for updates
pip list --outdated

# 3. Update all
pip install --upgrade -r requirements.txt

# 4. Update requirements file
pip freeze > requirements.txt

# 5. Commit changes
git add requirements.txt
git commit -m "Update dependencies"
```

### Troubleshooting
```powershell
# 1. Check status
.\verify_setup.bat

# 2. View logs
Get-Content logs\agent_core.log -Tail 100

# 3. Test packages
python -c "import flask, torch; print('OK')"

# 4. Reinstall if needed
pip install --force-reinstall -r requirements.txt

# 5. Restart services
python main.py
```

---

## 📝 Notes

- **Always activate venv** before running: `.\.venv\Scripts\Activate.ps1`
- **AWS credentials are optional** - only if using AWS services
- **First setup takes 15-25 minutes** for dependency installation
- **Dependencies total ~2.5GB** - ensure sufficient storage
- **Port conflicts** - change ports in `ultron_config.json` if needed

---

**Last Updated**: October 31, 2025
**Version**: ULTRON Agent 3.0
**Status**: Ready for Phase 4 Installation
