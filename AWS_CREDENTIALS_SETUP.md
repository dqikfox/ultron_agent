# 🔐 AWS Credentials Setup Guide for ULTRON Agent

**Security Status**: ✅ Fixed - Credentials moved from hardcoded to environment variables
**Last Updated**: October 31, 2025
**Compliance**: AWS IAM best practices, NIST security guidelines

---

## ⚠️ Security Alert - What Was Fixed

**Previous State** (VULNERABLE):
```python
# ❌ INSECURE - Credentials hardcoded in source code
self.bedrock_api_key = "ABSKQmVkcm9ja0FQSUtleS05MWhyLWF0LTk0MTI4NDAxOTAxNTo3L1lVOXY2TkZYUUpUdVByb3Y1MGNMdy9rby9IbVlYSW55dVF1MzlqejJIQWhxNHlSTnEwbW1LUGNjQT0="
```

**Current State** (SECURE):
```python
# ✅ SECURE - Credentials from environment variable
self.bedrock_api_key = os.getenv("AWS_BEDROCK_API_KEY", None)
if not self.bedrock_api_key:
    log_error("project_manager", "AWS credentials not configured")
```

**Risk Mitigated**:
- ✅ Credentials no longer in source code
- ✅ Won't be committed to Git repository
- ✅ Can be rotated without code changes
- ✅ Different credentials per environment (dev/staging/prod)

---

## 🚀 Quick Setup (5 minutes)

### Option 1: Environment Variables (Recommended for Development)

**Windows PowerShell**:
```powershell
# Set for current session
$env:AWS_ACCESS_KEY_ID = "AKIA..."
$env:AWS_SECRET_ACCESS_KEY = "wJalrXUt..."
$env:AWS_DEFAULT_REGION = "us-east-1"
$env:AWS_BEDROCK_API_KEY = "your-bedrock-key"

# Verify
$env:AWS_ACCESS_KEY_ID
```

**Permanent (Windows)**:
```powershell
# Add to PowerShell profile for permanent setup
# Edit: $PROFILE (usually Documents\PowerShell\profile.ps1)

$env:AWS_ACCESS_KEY_ID = "AKIA..."
$env:AWS_SECRET_ACCESS_KEY = "wJalrXUt..."
$env:AWS_DEFAULT_REGION = "us-east-1"
$env:AWS_BEDROCK_API_KEY = "your-bedrock-key"
```

**Windows CMD (Batch)**:
```batch
setx AWS_ACCESS_KEY_ID "AKIA..."
setx AWS_SECRET_ACCESS_KEY "wJalrXUt..."
setx AWS_DEFAULT_REGION "us-east-1"
setx AWS_BEDROCK_API_KEY "your-bedrock-key"
```

### Option 2: AWS CLI Configuration (Recommended for Production)

```powershell
# Install AWS CLI (if not already installed)
choco install awscli  # or download from aws.amazon.com/cli/

# Configure credentials
aws configure

# You'll be prompted for:
# AWS Access Key ID: [paste your access key]
# AWS Secret Access Key: [paste your secret key]
# Default region name: us-east-1
# Default output format: json
```

**Verify Configuration**:
```powershell
# Check stored credentials
cat ~/.aws/credentials

# Test connection
aws sts get-caller-identity
# Should return: { "UserId": "...", "Account": "123456789", "Arn": "..." }
```

### Option 3: AWS Secrets Manager (Recommended for Production)

```powershell
# Create secret in Secrets Manager
aws secretsmanager create-secret `
  --name ultron-agent-credentials `
  --description "ULTRON Agent AWS Bedrock Access" `
  --secret-string '{
    "access_key_id": "AKIA...",
    "secret_access_key": "wJalrXUt...",
    "bedrock_api_key": "your-bedrock-key"
  }'

# ULTRON retrieves automatically (see script below)
```

---

## 📋 Step-by-Step Setup

### Step 1: Get AWS Access Keys

**In AWS Console**:

1. Go to [AWS IAM Console](https://console.aws.amazon.com/iam/)
2. Click **Users** → **Create user** (e.g., "ultron-agent")
3. Click **Security credentials** tab
4. Click **Create access key**
5. **Important**: Copy and save both:
   - Access Key ID (starts with `AKIA`)
   - Secret Access Key (save immediately - can't be retrieved later)

**Set Permissions**:
```powershell
# Attach policies to user
aws iam attach-user-policy `
  --user-name ultron-agent `
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess

aws iam attach-user-policy `
  --user-name ultron-agent `
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

aws iam attach-user-policy `
  --user-name ultron-agent `
  --policy-arn arn:aws:iam::aws:policy/CloudWatchLogsFullAccess
```

### Step 2: Store Credentials Securely

**Option A: Environment Variables**
```powershell
$env:AWS_ACCESS_KEY_ID = "AKIA..."
$env:AWS_SECRET_ACCESS_KEY = "wJalrXUt..."
$env:AWS_BEDROCK_API_KEY = "your-key"
```

**Option B: ~/.aws/credentials File**
```
[default]
aws_access_key_id = AKIA...
aws_secret_access_key = wJalrXUt...

[ultron-profile]
aws_access_key_id = AKIA...
aws_secret_access_key = wJalrXUt...
```

**Option C: AWS Secrets Manager**
```powershell
# Retrieve credentials in ULTRON
aws secretsmanager get-secret-value --secret-id ultron-agent-credentials
```

### Step 3: Verify Credentials

```powershell
# Test AWS access
aws sts get-caller-identity

# Test Bedrock access
aws bedrock-runtime list-foundation-models

# Test S3 access
aws s3 ls

# All should return success
```

### Step 4: Update ULTRON Config

**In `ultron_config.json`**:
```json
{
  "aws_config": {
    "enabled": true,
    "region": "us-east-1",
    "bedrock_enabled": true,
    "use_secrets_manager": false,
    "credentials_source": "environment"
  },
  "services": {
    "bedrock_fallback": true,
    "bedrock_model": "anthropic.claude-3-sonnet-20240229-v1:0"
  }
}
```

### Step 5: Test ULTRON Integration

```powershell
# Start ULTRON
python main.py

# You should see:
# ✅ AWS Bedrock configured
# ✅ S3 access verified
# ✅ Config monitoring ready
```

---

## 🔑 Credential Management Strategies

### Strategy 1: Single AWS Account (Development)

**Setup**:
1. Create "ultron-dev" IAM user
2. Generate access keys
3. Store in `~/.aws/credentials`
4. Use default AWS_PROFILE

**Pros**: Simple, quick
**Cons**: Less secure for production

### Strategy 2: Multiple AWS Accounts (Production)

**Setup**:
1. Create separate AWS accounts for dev/staging/prod
2. Create IAM user in each account
3. Setup cross-account roles for escalation
4. Use environment variable to select profile

**Environment Config**:
```powershell
# Development
$env:AWS_PROFILE = "ultron-dev"

# Staging
$env:AWS_PROFILE = "ultron-staging"

# Production
$env:AWS_PROFILE = "ultron-prod"
```

### Strategy 3: IAM Roles (Recommended for AWS EC2/Lambda)

**Setup**:
1. Create IAM role with Bedrock/S3 permissions
2. Attach role to EC2 instance/Lambda function
3. No credentials needed - automatic

**Code**:
```python
import boto3

# Automatically uses IAM role credentials
session = boto3.Session()
client = session.client('bedrock-runtime')
```

### Strategy 4: AWS Secrets Manager (Enterprise)

**Setup**:
```powershell
# Store secrets
aws secretsmanager create-secret `
  --name ultron/prod/bedrock `
  --secret-string '{
    "access_key_id": "AKIA...",
    "secret_access_key": "wJalrXUt..."
  }'

# Retrieve in code
import json
client = boto3.client('secretsmanager')
response = client.get_secret_value(SecretId='ultron/prod/bedrock')
secrets = json.loads(response['SecretString'])
```

**Pros**: Central management, audit trail, rotation
**Cons**: Additional AWS cost, requires Secrets Manager permission

---

## 🛡️ Security Best Practices

### 1. Credential Rotation

```powershell
# Rotate keys monthly
# 1. Create new access key in IAM console
# 2. Update environment variable/config file
# 3. Delete old access key

# Automate rotation (every 30 days)
# Use AWS Secrets Manager with automatic rotation
```

### 2. Permission Scoping

**Minimal Permissions** (Only what ULTRON needs):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:ListModels"
      ],
      "Resource": "arn:aws:bedrock:*:*:model/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::ultron-*",
        "arn:aws:s3:::ultron-*/*"
      ]
    }
  ]
}
```

### 3. Audit Logging

```powershell
# Enable CloudTrail to log all API calls
aws cloudtrail start-logging --trail-name ultron-trail

# View logs
aws cloudtrail lookup-events --lookup-attributes AttributeKey=ResourceName,AttributeValue=ultron
```

### 4. Environment Isolation

```powershell
# Development (local machine)
$env:AWS_PROFILE = "ultron-dev"
$env:ENVIRONMENT = "development"

# Staging (test server)
$env:AWS_PROFILE = "ultron-staging"
$env:ENVIRONMENT = "staging"

# Production (live)
$env:AWS_PROFILE = "ultron-prod"
$env:ENVIRONMENT = "production"
```

### 5. Secret Scanning

```powershell
# Prevent accidental commits of credentials
git config --global core.hooksPath ~/.githooks

# Create pre-commit hook that scans for AWS keys
# ~/.githooks/pre-commit:
# #!/bin/bash
# if git diff --cached | grep -E 'AKIA|aws_secret_access_key'; then
#   echo "❌ AWS credentials detected in commit"
#   exit 1
# fi
```

---

## 🔍 Troubleshooting

### Issue: "AWS credentials not found"

**Diagnosis**:
```powershell
# Check if credentials set
$env:AWS_ACCESS_KEY_ID
$env:AWS_SECRET_ACCESS_KEY

# Check if file exists
cat ~/.aws/credentials
cat ~/.aws/config
```

**Solutions**:
```powershell
# Solution 1: Set environment variables
$env:AWS_ACCESS_KEY_ID = "AKIA..."
$env:AWS_SECRET_ACCESS_KEY = "wJalrXUt..."

# Solution 2: Configure via CLI
aws configure

# Solution 3: Create credentials file
New-Item -Path ~/.aws -ItemType Directory -Force
@"
[default]
aws_access_key_id = AKIA...
aws_secret_access_key = wJalrXUt...
"@ | Out-File -Path ~/.aws/credentials
```

### Issue: "Access Denied" errors

**Diagnosis**:
```powershell
# Check IAM permissions
aws iam get-user-policy --user-name ultron-agent --policy-name <policy-name>

# Check what user ULTRON is using
aws sts get-caller-identity
```

**Solutions**:
```powershell
# Add missing permissions
aws iam attach-user-policy `
  --user-name ultron-agent `
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess

# Check policy attachment
aws iam list-user-policies --user-name ultron-agent
```

### Issue: "Invalid credentials" in ULTRON logs

**Debug**:
```powershell
# Test credentials directly
aws bedrock-runtime list-foundation-models --region us-east-1

# Check if credentials are expired
aws sts get-session-token

# View ULTRON logs
Get-Content logs/project_manager.log -Tail 50
```

**Fix**:
```powershell
# Regenerate access keys
aws iam delete-access-key --access-key-id AKIA... --user-name ultron-agent
aws iam create-access-key --user-name ultron-agent

# Update environment variable
$env:AWS_ACCESS_KEY_ID = "AKIA-new-key"
$env:AWS_SECRET_ACCESS_KEY = "wJalrXUt-new-secret"
```

---

## 📚 Configuration Examples

### Example 1: Development Environment

```powershell
# ~/.profile or PowerShell profile
$env:AWS_ACCESS_KEY_ID = "AKIA-dev-key"
$env:AWS_SECRET_ACCESS_KEY = "wJalrXUt-dev-secret"
$env:AWS_DEFAULT_REGION = "us-east-1"
$env:AWS_BEDROCK_API_KEY = $env:AWS_SECRET_ACCESS_KEY

# Verify
aws sts get-caller-identity
# Output: { "UserId": "AIDA...", "Account": "123456789", "Arn": "arn:aws:iam::123456789:user/ultron-dev" }
```

### Example 2: Production Deployment

```powershell
# Using IAM role on EC2
# (No explicit credentials needed - instance uses role)

# Or using Secrets Manager
$secret = aws secretsmanager get-secret-value --secret-id ultron-prod-credentials
$credentials = $secret.SecretString | ConvertFrom-Json
$env:AWS_ACCESS_KEY_ID = $credentials.access_key_id
$env:AWS_SECRET_ACCESS_KEY = $credentials.secret_access_key
```

### Example 3: CI/CD Pipeline

```yaml
# .github/workflows/aws-integration.yml
name: AWS Integration Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    env:
      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      AWS_DEFAULT_REGION: us-east-1
    steps:
      - uses: actions/checkout@v2
      - name: Test AWS Connection
        run: aws sts get-caller-identity
      - name: Test Bedrock Access
        run: aws bedrock-runtime list-foundation-models
```

---

## ✅ Validation Checklist

### Pre-Deployment

- [ ] AWS credentials generated in IAM console
- [ ] Access Key ID and Secret Access Key saved securely
- [ ] Credentials set as environment variables
- [ ] `aws sts get-caller-identity` returns success
- [ ] `aws bedrock-runtime list-foundation-models` returns models
- [ ] `ultron_project_manager.py` updated to use environment variables
- [ ] No hardcoded credentials in source code
- [ ] `.gitignore` includes `~/.aws/credentials`
- [ ] ULTRON starts successfully: `python main.py`
- [ ] `logs/project_manager.log` shows no credential errors

### Post-Deployment

- [ ] AWS Bedrock fallback works when Ollama unavailable
- [ ] S3 operations succeed (if configured)
- [ ] CloudTrail logs show ULTRON API calls
- [ ] SNS notifications sent for Config changes
- [ ] Team notified of new AWS environment setup
- [ ] Incident response plan updated
- [ ] Monthly credential rotation scheduled

---

## 🎯 Next Steps

1. **Immediate (5 min)**
   - [ ] Create AWS IAM user for ULTRON
   - [ ] Generate access keys
   - [ ] Set environment variables

2. **Short Term (15 min)**
   - [ ] Run `aws sts get-caller-identity` to verify
   - [ ] Deploy AWS Config (see AWS_CONFIG_SETUP_GUIDE.md)
   - [ ] Start ULTRON and verify Bedrock fallback

3. **Medium Term (1 hour)**
   - [ ] Setup Secrets Manager for production
   - [ ] Configure credential rotation policy
   - [ ] Enable CloudTrail audit logging

4. **Ongoing**
   - [ ] Monitor credential age (rotate monthly)
   - [ ] Review CloudTrail logs weekly
   - [ ] Update security policies quarterly

---

## 📞 Quick Reference

```powershell
# Test AWS credentials
aws sts get-caller-identity

# Test Bedrock
aws bedrock-runtime list-foundation-models

# Set credentials
$env:AWS_ACCESS_KEY_ID = "your-key"
$env:AWS_SECRET_ACCESS_KEY = "your-secret"

# Start ULTRON
python main.py

# Check logs
Get-Content logs/project_manager.log
```

---

**AWS Credentials Security Setup**
**✅ Production Ready**
**October 31, 2025**
