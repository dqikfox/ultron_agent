# 🚀 AWS Integration - Quick Start (10 minutes)

**Goal**: Enable AWS services for ULTRON Agent
**Prerequisites**: AWS Account, Python 3.10+
**Status**: ✅ Ready to Deploy

---

## ⚡ 5-Step Setup

### Step 1: Create AWS IAM User (2 min)

```powershell
# AWS Console: https://console.aws.amazon.com/iam/

# 1. Users → Create user → "ultron-agent"
# 2. Security credentials tab → Create access key
# 3. Save the output:
#    Access Key ID: AKIA...
#    Secret Access Key: wJalrXUt...
```

### Step 2: Set Environment Variables (1 min)

```powershell
# PowerShell (Windows):
$env:AWS_ACCESS_KEY_ID = "AKIA..."
$env:AWS_SECRET_ACCESS_KEY = "wJalrXUt..."
$env:AWS_DEFAULT_REGION = "us-east-1"

# Verify:
aws sts get-caller-identity
```

### Step 3: Deploy AWS Config (3 min)

```powershell
# Download: EnableAWSConfig.yml (from your Downloads)

aws cloudformation create-stack `
  --stack-name ultron-config `
  --template-body file://path/to/EnableAWSConfig.yml `
  --parameters `
    ParameterKey=AllSupported,ParameterValue=True `
    ParameterKey=RecordingFrequency,ParameterValue=CONTINUOUS

# Check status:
aws cloudformation describe-stacks --stack-name ultron-config
```

### Step 4: Update ULTRON Config (2 min)

```json
// In ultron_config.json, add:
{
  "aws_config": {
    "enabled": true,
    "region": "us-east-1",
    "bedrock_enabled": true
  }
}
```

### Step 5: Start ULTRON (2 min)

```powershell
# Terminal 1: Start ULTRON
python main.py

# You should see:
# ✅ AWS Bedrock configured
# ✅ AWS Config monitoring active
```

---

## ✅ What You Can Now Do

### Use AWS Bedrock (Cloud AI Models)

**In ULTRON**:
```
/delegate "Analyze code performance using AWS Bedrock"
```

**In Python**:
```python
from tools.aws_bedrock_tool import AWSBedrockTool

tool = AWSBedrockTool()
result = tool.invoke_model(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    prompt="Analyze this code..."
)
```

### Monitor AWS Compliance

```
/delegate "Check AWS Config compliance status"
```

Result:
```
📊 AWS Config Compliance Status
✅ Compliant: 48
⚠️  Non-Compliant: 2
```

### Store Data in S3

```python
from tools.database_integration_tool import S3Operations

s3 = S3Operations()
s3.upload_file("local_file.txt", "s3://ultron-bucket/file.txt")
```

---

## 📋 Validation Checklist

```powershell
# 1. AWS Credentials ✅
aws sts get-caller-identity
# Returns: Account, UserId, Arn

# 2. AWS Bedrock ✅
aws bedrock-runtime list-foundation-models
# Returns: Available models

# 3. ULTRON Startup ✅
python main.py
# Logs should show: ✅ AWS services configured

# 4. CloudFormation Stack ✅
aws cloudformation describe-stacks --stack-name ultron-config
# Status: CREATE_COMPLETE
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "AWS credentials not found" | Set: `$env:AWS_ACCESS_KEY_ID = "AKIA..."` |
| "Access Denied" | Add permissions to IAM user (see AWS_CREDENTIALS_SETUP.md) |
| "Bedrock model not found" | Check region is us-east-1 |
| "Config stack creation failed" | Check EnableAWSConfig.yml is valid |

---

## 📚 Next Steps

1. **Immediate**: Run the 5-step setup above ⬆️
2. **In 30 min**: Read AWS_CONFIG_SETUP_GUIDE.md (deeper dive)
3. **In 1 hour**: Setup Secrets Manager for production credentials
4. **In 2 hours**: Deploy custom AWS Config rules for your needs

---

## 🎯 Common Use Cases

### Use Case 1: Code Analysis with AWS Bedrock

```
User: "@ultron analyze code using AWS"
ULTRON: Uses Claude 3 Sonnet via Bedrock
Returns: Performance improvements, security issues, refactoring suggestions
```

### Use Case 2: Compliance Monitoring

```
User: "@ultron check AWS compliance"
ULTRON: Queries AWS Config
Returns: Resource compliance status, non-compliant resources, remediation tips
```

### Use Case 3: Data Pipeline

```
User: "@ultron upload analysis results to S3"
ULTRON: Stores results in S3 bucket
Returns: S3 URL for sharing
```

---

## 💡 Key Commands

```powershell
# Test AWS connection
aws sts get-caller-identity

# View AWS credentials file
cat ~/.aws/credentials

# List available models
aws bedrock-runtime list-foundation-models

# Check Config stack
aws cloudformation describe-stacks --stack-name ultron-config

# Start ULTRON
python main.py
```

---

## 🔐 Security Notes

✅ **Credentials stored securely**: Environment variables (not hardcoded)
✅ **IAM user created**: Limited permissions only
✅ **Config monitoring**: Tracks all resource changes
✅ **Bedrock access**: Encrypted communication

---

## 📞 Support

**AWS Setup Questions**:
- AWS Console: https://console.aws.amazon.com
- AWS Docs: https://docs.aws.amazon.com

**ULTRON Questions**:
- See AWS_CONFIG_SETUP_GUIDE.md
- See AWS_CREDENTIALS_SETUP.md

---

**🎉 AWS Integration Complete!**

Your ULTRON Agent now has:
- ✅ Cloud AI models (Bedrock)
- ✅ Compliance monitoring (AWS Config)
- ✅ Cloud storage (S3)
- ✅ Voice services (AWS Polly)

**Start using AWS services now:**
```powershell
python main.py
```

---

*ULTRON Agent AWS Integration*
*October 31, 2025*
*Quick Start - 10 minutes ⚡*
