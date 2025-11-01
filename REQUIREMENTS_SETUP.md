# ULTRON Agent 3.0 - Requirements & Dependencies

## Overview
This document outlines all system and Python dependencies required to run ULTRON Agent 3.0, including installation steps, verification procedures, and troubleshooting guides.

**Last Updated**: October 31, 2025
**Target OS**: Windows 11 (64-bit)
**Python Version**: 3.10+
**AWS CLI Version**: 2.x

---

## Table of Contents
1. [System Requirements](#system-requirements)
2. [AWS CLI Installation](#aws-cli-installation)
3. [Python Environment Setup](#python-environment-setup)
4. [Dependency Installation](#dependency-installation)
5. [Verification & Testing](#verification--testing)
6. [AWS Configuration](#aws-configuration)
7. [Troubleshooting](#troubleshooting)
8. [Quick Reference](#quick-reference)

---

## System Requirements

### Minimum Hardware
- **CPU**: Intel i5/AMD Ryzen 5 or better (quad-core minimum)
- **RAM**: 16GB (32GB recommended for ML models)
- **Storage**: 50GB free space (for models and cache)
- **GPU**: NVIDIA GPU recommended (for CUDA support)

### Software Prerequisites
- **OS**: Windows 10 22H2 or Windows 11 (64-bit)
- **Admin Rights**: Required for AWS CLI installation
- **Internet Connection**: Required for package/model downloads

### Key Installed Software
- Python 3.10+
- AWS CLI v2.x
- Git (for repository access)
- Ollama (local LLM backend) - installed separately via `run.bat`

---

## AWS CLI Installation

### Option 1: MSI Installer (Recommended)

**Download & Install AWS CLI v2**:
```powershell
# Download the MSI installer
$msiUrl = "https://awscli.amazonaws.com/AWSCLIV2.msi"
$msiPath = "$env:TEMP\AWSCLIV2.msi"
Invoke-WebRequest -Uri $msiUrl -OutFile $msiPath -UseBasicParsing

# Install (requires Administrator)
msiexec.exe /i $msiPath /quiet /norestart

# Verify installation
aws --version
```

**Expected Output**:
```
aws-cli/2.27.41 Python/3.11.6 Windows/10 exe/AMD64 prompt/off
```

### Option 2: Manual Installation
1. Visit: https://awscli.amazonaws.com/AWSCLIV2.msi
2. Download the installer
3. Right-click → "Run as Administrator"
4. Follow the installation wizard
5. Close and reopen PowerShell to refresh PATH

### Verification
```powershell
# Check installation
aws --version

# Get AWS Account Information
aws sts get-caller-identity
```

---

## Python Environment Setup

### Step 1: Verify Python Installation
```powershell
python --version
# Expected: Python 3.10.0 or higher
```

### Step 2: Create Virtual Environment
```powershell
# Navigate to project directory
cd C:\Projects\ultron_agent

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Verify activation (should show (.venv) prefix)
```

### Step 3: Upgrade Core Tools
```powershell
# Upgrade pip, setuptools, and wheel
python -m pip install --upgrade pip setuptools wheel
```

### Troubleshooting Virtual Environment

**Issue**: Script execution disabled
```powershell
# Solution: Allow script execution for this session
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# Then activate
.\.venv\Scripts\Activate.ps1
```

**Issue**: Command not found after activation
```powershell
# Solution: Use full path or cd to project directory
C:\Projects\ultron_agent\.venv\Scripts\Activate.ps1
```

---

## Dependency Installation

### Main Dependencies (requirements.txt)

**All Core Packages** (~2GB download, installation time: 10-20 minutes):

```
# API & Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
flask==3.0.0
aiohttp==3.9.0

# AI/ML Frameworks
openai==1.32.0
langchain==0.2.17
torch==2.1.2
transformers==4.36.2

# Voice & Audio
elevenlabs==1.2.0
pyttsx3==2.90
SpeechRecognition==3.10.0
pygame==2.5.2

# Database & Data
psycopg2-binary==2.9.9
pandas==2.1.4
numpy==1.26.2

# Utilities
python-dotenv==1.0.0
pydantic==2.5.0
requests==2.31.0
```

### Installation Commands

**Automated Setup** (Recommended):
```powershell
# Using PowerShell script
.\setup_requirements.ps1

# Or using batch file
.\setup_requirements.bat
```

**Manual Installation**:
```powershell
# Ensure virtual environment is activated
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Install with upgrade flag
pip install --upgrade -r requirements.txt

# Force reinstall (if conflicts)
pip install --force-reinstall -r requirements.txt
```

### Installation Time Estimates
| Package Group | Size | Time |
|---------------|------|------|
| Core Dependencies | 500MB | 3-5 min |
| PyTorch + Dependencies | 1.2GB | 5-10 min |
| Transformers + Models | 800MB | 3-5 min |
| **Total** | **~2.5GB** | **15-25 min** |

---

## Verification & Testing

### Quick Verification
```powershell
# Check if major packages are installed
python -c "import flask; import torch; import transformers; import openai; print('✓ All critical packages imported successfully')"
```

### Detailed Package Verification
```powershell
# Create verification script
python -c "
import sys
packages = ['flask', 'aiohttp', 'openai', 'langchain', 'torch', 'transformers', 'elevenlabs']
for pkg in packages:
    try:
        __import__(pkg)
        print(f'✓ {pkg}')
    except ImportError as e:
        print(f'✗ {pkg}: {e}')
"
```

### Version Checking
```powershell
# Check specific package versions
pip show flask aiohttp openai torch transformers

# Check all installed packages
pip list
```

### Test Environment
```powershell
# Run test suite
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

---

## AWS Configuration

### Configure AWS Credentials

**Interactive Configuration** (Recommended):
```powershell
aws configure
# Prompts for:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region (us-east-1)
# - Default output format (json)
```

### Credential File Locations

**Credentials** (sensitive - never commit):
```
C:\Users\%USERNAME%\.aws\credentials
```

**Configuration**:
```
C:\Users\%USERNAME%\.aws\config
```

### Using IAM Profile

**Create AWS Profile** for ULTRON Agent:
```powershell
aws configure --profile ultron-agent

# Use the profile in code/config
set AWS_PROFILE=ultron-agent
```

### Verify AWS Configuration
```powershell
# Test credentials
aws sts get-caller-identity

# Expected output
{
    "UserId": "AIDAI...",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/your-username"
}

# Test service access
aws s3 ls

# Test Config service
aws configservice describe-configuration-recorders
```

### Security Best Practices
- ✅ Use IAM roles for EC2 instances
- ✅ Rotate access keys regularly
- ✅ Use AWS Secrets Manager for sensitive data
- ✅ Never commit credentials to Git
- ⚠️ Keep `~/.aws/credentials` file restricted (mode 600)

---

## Troubleshooting

### AWS CLI Issues

**Issue**: "aws: command not found"
```powershell
# Solution: Reinstall AWS CLI
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi /qn

# Or add to PATH manually
$env:Path += ";C:\Program Files\Amazon\AWSCLIV2"
```

**Issue**: "AWS credentials not found"
```powershell
# Solution: Configure credentials
aws configure

# Or check credentials file
type $env:USERPROFILE\.aws\credentials
```

**Issue**: "Access Denied" errors
```powershell
# Verify IAM permissions
aws iam list-attached-user-policies --user-name <username>

# Check with STS
aws sts get-caller-identity
```

### Python Package Issues

**Issue**: "ModuleNotFoundError: No module named..."
```powershell
# Solution: Install missing package
pip install <package-name>

# Or reinstall all
pip install -r requirements.txt --force-reinstall
```

**Issue**: Conflicting package versions
```powershell
# Solution: Clean environment and reinstall
pip install --force-reinstall -r requirements.txt

# Or use specific constraint file
pip install -r requirements.txt --upgrade
```

**Issue**: CUDA/GPU-related errors
```powershell
# Verify CUDA installation
nvidia-smi

# Reinstall PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Virtual Environment Issues

**Issue**: "The term 'activate' is not recognized"
```powershell
# Solution: Use full path
.\.venv\Scripts\Activate.ps1

# Or on CMD
.venv\Scripts\activate.bat
```

**Issue**: "ExecutionPolicy prevents script execution"
```powershell
# Solution: Temporarily allow execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\.venv\Scripts\Activate.ps1
```

---

## Quick Reference

### Common Commands

```powershell
# Setup & Installation
.\setup_requirements.bat              # Automated setup
.\setup_requirements.ps1 -UpgradeAll  # PowerShell with upgrade
pip install -r requirements.txt       # Manual installation

# Verification
aws --version                         # Check AWS CLI
python --version                      # Check Python
pip list                              # List installed packages
aws sts get-caller-identity          # Test AWS credentials

# Activation/Deactivation
.\.venv\Scripts\Activate.ps1         # Activate environment
deactivate                            # Deactivate environment

# Updates
pip install --upgrade pip             # Upgrade pip
pip install --upgrade -r requirements.txt  # Upgrade all packages
aws update-cli                        # Update AWS CLI (if using bundled)
```

### File Structure
```
ultron_agent/
├── requirements.txt              # Main dependencies
├── requirements_enhanced.txt     # Optional enhancements
├── requirements_complete.txt     # Extended packages
├── setup_requirements.bat        # Installation script (batch)
├── setup_requirements.ps1        # Installation script (PowerShell)
├── .venv/                        # Virtual environment (created)
│   ├── Scripts/                  # Executables (python, pip, etc.)
│   ├── Lib/                      # Installed packages
│   └── pyvenv.cfg               # Environment config
├── ultron_config.json           # Agent configuration
├── .aws/                        # AWS configuration (user home)
│   ├── credentials              # AWS credentials
│   └── config                   # AWS configuration
└── logs/                        # Service logs
```

### Environment Variables

**AWS**:
```powershell
# Set AWS region
$env:AWS_REGION = "us-east-1"

# Set AWS profile
$env:AWS_PROFILE = "ultron-agent"

# Set AWS access keys (not recommended - use credentials file)
$env:AWS_ACCESS_KEY_ID = "AKIA..."
$env:AWS_SECRET_ACCESS_KEY = "..."
```

**Python**:
```powershell
# Disable telemetry
$env:PYTHONTELEMETRY = 0

# Debug mode
$env:PYTHONDEBUG = 1

# UTF-8 encoding
$env:PYTHONIOENCODING = "utf-8"
```

### Support & Resources

| Topic | Link |
|-------|------|
| AWS CLI Documentation | https://docs.aws.amazon.com/cli/ |
| AWS CLI Installation | https://aws.amazon.com/cli/ |
| Python venv | https://docs.python.org/3/library/venv.html |
| PyPI Packages | https://pypi.org/ |
| ULTRON Documentation | See `.continue/rules/` directory |

---

## Next Steps

After successful installation:

1. **Verify Setup**:
   ```powershell
   .\setup_requirements.bat
   ```

2. **Configure AWS**:
   ```powershell
   aws configure
   ```

3. **Start Ollama** (if using):
   ```powershell
   .\run.bat
   ```

4. **Launch ULTRON Agent**:
   ```powershell
   python main.py
   ```

5. **Access Web GUI**:
   - Open browser → http://localhost:8080

---

## Changelog

### October 31, 2025
- ✅ Created comprehensive setup scripts (batch & PowerShell)
- ✅ Added AWS CLI installation documentation
- ✅ Documented Python environment setup
- ✅ Added verification procedures
- ✅ Created troubleshooting guide
- ✅ Added AWS configuration section

---

*For issues or questions, refer to the troubleshooting section or contact the development team.*
