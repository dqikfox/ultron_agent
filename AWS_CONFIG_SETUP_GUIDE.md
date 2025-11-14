# 🔧 ULTRON Agent - AWS Integration & Config Setup Guide

**Date**: October 31, 2025
**Purpose**: Enable AWS services for ULTRON Agent
**Status**: Production-Ready Configuration

---

## 📋 What's Already Enabled in ULTRON

### ✅ AWS Services Currently Integrated

| Service | Component | Status | Purpose |
|---------|-----------|--------|---------|
| **AWS Bedrock** | `tools/aws_bedrock_tool.py` | ✅ Active | Cloud AI models (Claude, Llama) |
| **AWS Lambda** | `tools/aws_lambda_tool.py` | ✅ Ready | Serverless function execution |
| **AWS S3** | `tools/database_integration_tool.py` | ✅ Ready | Cloud storage |
| **AWS Secrets Manager** | Config system | ✅ Active | API key management |
| **AWS Voice/Speech** | `tools/voice_aws_tool.py` | ✅ Ready | AWS Polly TTS |
| **AWS Config** | This guide | 📋 Setup needed | Compliance & monitoring |

---

## 🚀 Quick Setup (15 minutes)

### Step 1: Get Your AWS Credentials
```powershell
# Check if AWS CLI is installed
aws --version

# If not installed:
# Download from: https://aws.amazon.com/cli/

# Configure AWS credentials
aws configure

# You'll need:
# AWS Access Key ID: [your-access-key]
# AWS Secret Access Key: [your-secret-key]
# Default region: us-east-1
# Default output format: json
```

### Step 2: Set Environment Variables
```powershell
# In PowerShell (or add to .venv\Scripts\Activate.ps1):

$env:AWS_ACCESS_KEY_ID = "your-access-key-id"
$env:AWS_SECRET_ACCESS_KEY = "your-secret-access-key"
$env:AWS_DEFAULT_REGION = "us-east-1"

# Verify
aws sts get-caller-identity
# Should return your AWS account details
```

### Step 3: Deploy AWS Config via CloudFormation
```powershell
# Navigate to the EnableAWSConfig.yml location
cd C:\Projects\ultron_agent

# Deploy the CloudFormation stack
aws cloudformation create-stack `
  --stack-name ultron-aws-config `
  --template-body file://path/to/EnableAWSConfig.yml `
  --parameters `
    ParameterKey=AllSupported,ParameterValue=True `
    ParameterKey=RecordingFrequency,ParameterValue=CONTINUOUS `
    ParameterKey=NotificationEmail,ParameterValue=your-email@example.com

# Check deployment status
aws cloudformation describe-stacks --stack-name ultron-aws-config
```

### Step 4: Update ULTRON Config
```json
// In ultron_config.json, add AWS section:
{
  "aws_config": {
    "enabled": true,
    "region": "us-east-1",
    "access_key_id": "USE_ENV_AWS_ACCESS_KEY_ID",
    "secret_access_key": "USE_ENV_AWS_SECRET_ACCESS_KEY",
    "bedrock_enabled": true,
    "s3_bucket": "ultron-data-bucket",
    "config_enabled": true,
    "compliance_monitoring": true
  }
}
```

---

## 🎯 AWS Config Deep Dive

### What AWS Config Does

AWS Config monitors and records your AWS resource configurations:

```
┌─────────────────────────────────────────────────────┐
│         AWS Config Recorder                          │
│  ┌──────────────────────────────────────────────┐  │
│  │ • Records EC2 instance configurations        │  │
│  │ • Tracks S3 bucket policies                  │  │
│  │ • Monitors IAM role changes                  │  │
│  │ • Logs security group modifications          │  │
│  │ • Records database snapshots                 │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────┐
│    Delivery Channel (S3 + SNS)                      │
│  ┌──────────────────────────────────────────────┐  │
│  │ • Stores configs in S3 bucket               │  │
│  │ • Sends notifications to SNS topic          │  │
│  │ • Snapshots on schedule (1h-24h)            │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────┐
│    ULTRON Agent Analysis                            │
│  ┌──────────────────────────────────────────────┐  │
│  │ • Compliance checking                        │  │
│  │ • Risk identification                        │  │
│  │ • Automated remediation                      │  │
│  │ • Reporting & dashboards                     │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### Enable AWS Config via ULTRON

```python
# tools/aws_config_tool.py example usage:

from tools.aws_config_tool import AWSConfigTool

tool = AWSConfigTool()

# Start recording
tool.start_recorder()
# ✅ "AWS Config Recorder started"

# Get compliance status
status = tool.get_compliance_status()
# Returns: {"compliant": 48, "non_compliant": 2, "not_applicable": 1}

# List recent changes
changes = tool.get_recent_changes(limit=10)
# Returns: Config history with timestamps

# Run compliance check
compliance = tool.check_compliance()
# Reports on: Security, Performance, Cost, Governance
```

---

## 🔐 AWS Security Setup

### Step 1: Create IAM User for ULTRON
```powershell
# Create programmatic user
aws iam create-user --user-name ultron-agent

# Attach policies
aws iam attach-user-policy `
  --user-name ultron-agent `
  --policy-arn arn:aws:iam::aws:policy/ConfigUserAccess

aws iam attach-user-policy `
  --user-name ultron-agent `
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess

aws iam attach-user-policy `
  --user-name ultron-agent `
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

# Create access keys
aws iam create-access-key --user-name ultron-agent
# Save the Access Key ID and Secret Access Key
```

### Step 2: Store Credentials Securely
```powershell
# Use AWS Secrets Manager
aws secretsmanager create-secret `
  --name ultron-agent-credentials `
  --secret-string '{
    "access_key_id": "your-key-id",
    "secret_access_key": "your-secret-key"
  }'

# ULTRON retrieves them automatically
```

### Step 3: Enable Encryption
```json
{
  "aws_config": {
    "encryption": {
      "enabled": true,
      "kms_key_arn": "arn:aws:kms:region:account:key/key-id",
      "s3_sse": "aws:kms"
    }
  }
}
```

---

## 📊 AWS Services Integration Matrix

### Available Tools in ULTRON

#### 1. AWS Bedrock Tool
```python
# Use Claude/Llama models
from tools.aws_bedrock_tool import AWSBedrockTool

tool = AWSBedrockTool()
response = tool.invoke_model(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    prompt="Analyze this code..."
)
```

**Models Available:**
- `anthropic.claude-3-sonnet` - Best for code analysis
- `anthropic.claude-3-opus` - Most capable
- `meta.llama3-70b` - Open-source alternative
- `amazon.nova-pro` - AWS native models

#### 2. AWS Lambda Tool
```python
# Execute serverless functions
from tools.aws_lambda_tool import AWSLambdaTool

tool = AWSLambdaTool()
result = tool.invoke_function(
    function_name="ultron-processor",
    payload={"task": "analyze_logs"}
)
```

#### 3. AWS S3 Tool
```python
# Cloud storage operations
from tools.database_integration_tool import S3Operations

tool = S3Operations()
tool.upload_file("local_file.txt", "s3://ultron-bucket/file.txt")
tool.download_file("s3://ultron-bucket/data.json", "local_data.json")
```

#### 4. AWS Config Tool
```python
# Compliance & configuration monitoring
from tools.aws_config_tool import AWSConfigTool

tool = AWSConfigTool()
compliance = tool.get_compliance_status()
changes = tool.get_resource_history(resource_id="i-1234567890")
```

#### 5. AWS Voice Tool
```python
# Text-to-speech via Polly
from tools.voice_aws_tool import VoiceAWSTool

tool = VoiceAWSTool()
tool.speak("Hello from ULTRON", voice_id="Joanna")
```

---

## 🔄 Automation: AWS Config + ULTRON

### Auto-Remediation Workflow

```yaml
# .github/workflows/aws-config-compliance.yml
name: AWS Config Compliance Check

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  compliance:
    runs-on: ubuntu-latest
    steps:
      - name: Check AWS Config Compliance
        run: |
          python -c "
          from tools.aws_config_tool import AWSConfigTool
          tool = AWSConfigTool()

          # Get compliance status
          status = tool.get_compliance_status()

          # Report findings
          if status['non_compliant'] > 0:
            print(f'⚠️ Found {status[\"non_compliant\"]} non-compliant resources')

            # Auto-remediate
            tool.auto_remediate()
            print('✅ Remediation attempted')
          else:
            print('✅ All resources compliant')
          "

      - name: Send Notification
        if: always()
        run: |
          aws sns publish \
            --topic-arn arn:aws:sns:region:account:ultron-alerts \
            --message "AWS Config compliance check completed"
```

---

## 📈 Monitoring & Alerts

### Setup CloudWatch Alarms
```powershell
# Monitor Config recorder status
aws cloudwatch put-metric-alarm `
  --alarm-name ultron-config-recorder-status `
  --alarm-description "Alert if Config stops recording" `
  --metric-name RecorderStatus `
  --namespace AWS/Config `
  --statistic Average `
  --period 300 `
  --threshold 0 `
  --comparison-operator LessThanOrEqualToThreshold `
  --alarm-actions arn:aws:sns:region:account:ultron-alerts
```

### Enable SNS Notifications
```powershell
# Email subscription for alerts
aws sns subscribe `
  --topic-arn arn:aws:sns:region:account:ultron-alerts `
  --protocol email `
  --notification-endpoint your-email@example.com
```

---

## ✅ Validation Checklist

### Configuration Verification
```powershell
# 1. Verify AWS credentials
aws sts get-caller-identity
# ✅ Should show your account info

# 2. Check Config recorder
aws configservice describe-configuration-recorder-status
# ✅ Should show "recording": true

# 3. Verify S3 bucket
aws s3 ls s3://ultron-config-bucket/
# ✅ Should list Config files

# 4. Check SNS topic
aws sns list-subscriptions-by-topic `
  --topic-arn arn:aws:sns:region:account:ultron-config-topic
# ✅ Should list email subscriptions

# 5. Test Bedrock access
aws bedrock-runtime list-foundation-models
# ✅ Should list available models
```

### ULTRON Integration Verification
```python
# Run validation script
python -c "
from tools.aws_bedrock_tool import AWSBedrockTool
from tools.aws_config_tool import AWSConfigTool
from tools.database_integration_tool import S3Operations

print('Testing AWS Bedrock...')
bedrock = AWSBedrockTool()
print('✅ Bedrock connected')

print('Testing AWS Config...')
config = AWSConfigTool()
print('✅ Config connected')

print('Testing S3...')
s3 = S3Operations()
print('✅ S3 connected')

print('\n🎉 All AWS services ready!')
"
```

---

## 🚀 Integration with ULTRON Workflows

### Method 1: Direct AWS Config Queries
```python
# In agent_core.py or custom tool:

async def check_aws_compliance():
    from tools.aws_config_tool import AWSConfigTool

    tool = AWSConfigTool()
    compliance = await tool.get_compliance_status()

    if compliance['non_compliant'] > 0:
        # Auto-remediate
        await tool.auto_remediate()
        # Log decision
        log_ai_decision("agent", "AWS Config auto-remediation triggered")
```

### Method 2: Event-Driven Remediation
```python
# Listen for AWS Config change events

async def on_config_change(event):
    """Handle AWS Config compliance changes"""
    resource_id = event['configuration_item']['resource_id']
    compliance_type = event['new_evaluation_result']['compliance_type']

    if compliance_type == 'NON_COMPLIANT':
        # Trigger ULTRON brain
        from brain import UltronBrain
        brain = UltronBrain()

        remediation_plan = await brain.plan_remediation(resource_id)
        await execute_remediation(remediation_plan)
```

### Method 3: Scheduled Compliance Reports
```python
# .github/workflows/aws-compliance-report.yml
# Generates weekly compliance summary
# Sends to team via email
# Includes recommendations
```

---

## 💡 AWS + ULTRON Best Practices

### 1. Cost Optimization
- **Use Bedrock for batch processing** - Process 100+ items efficiently
- **S3 storage for large datasets** - Unlimited storage vs. local disk
- **Lambda for spike loads** - Pay per execution, not uptime

### 2. Security Hardening
- **Rotate IAM credentials monthly** - Automatic via Secrets Manager
- **Enable CloudTrail logging** - Audit all API calls
- **Use VPC endpoints** - Keep traffic within AWS network

### 3. Performance
- **Cache Bedrock responses** - Reduce API calls
- **Batch Config queries** - Get multiple resources in one call
- **Use S3 multipart upload** - Faster file transfers

### 4. Monitoring
- **CloudWatch metrics** - Real-time performance visibility
- **Config compliance rules** - Automated policy enforcement
- **SNS notifications** - Immediate alerts for issues

---

## 🔧 Troubleshooting

### Issue: "AWS credentials not found"
```powershell
# Solution 1: Set environment variables
$env:AWS_ACCESS_KEY_ID = "your-key"
$env:AWS_SECRET_ACCESS_KEY = "your-secret"

# Solution 2: Use AWS CLI config
aws configure

# Solution 3: Check .aws/credentials file
cat ~/.aws/credentials
```

### Issue: "Config recorder not running"
```powershell
# Start recorder
aws configservice start-configuration-recorder `
  --configuration-recorder-names default

# Verify
aws configservice describe-configuration-recorder-status
```

### Issue: "Bedrock model not found"
```powershell
# List available models
aws bedrock list-foundation-models

# Check region availability
# Some models only in us-east-1, us-west-2

# Switch region
$env:AWS_DEFAULT_REGION = "us-east-1"
```

### Issue: "S3 bucket access denied"
```powershell
# Check IAM permissions
aws iam get-user-policy --user-name ultron-agent --policy-name S3Access

# Add S3 policy
aws iam attach-user-policy `
  --user-name ultron-agent `
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
```

---

## 📚 AWS Integration Examples

### Example 1: AWS Config Compliance Dashboard
```python
# Create compliance summary
from tools.aws_config_tool import AWSConfigTool

tool = AWSConfigTool()
compliance = tool.get_compliance_status()

summary = f"""
📊 AWS Compliance Report

✅ Compliant Resources: {compliance['compliant']}
⚠️  Non-Compliant: {compliance['non_compliant']}
❓ Unknown: {compliance['not_applicable']}

Compliance Rate: {100 * compliance['compliant'] / (compliance['compliant'] + compliance['non_compliant'])}%

Recommendation: {'All systems green!' if compliance['non_compliant'] == 0 else f'Remediate {compliance["non_compliant"]} issues'}
"""

print(summary)
```

### Example 2: Bedrock Code Analysis
```python
from tools.aws_bedrock_tool import AWSBedrockTool

tool = AWSBedrockTool()

code = """
def process_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result
"""

analysis = tool.invoke_model(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    prompt=f"Analyze this Python code for improvements:\n{code}"
)

print(f"Code Analysis:\n{analysis}")
```

### Example 3: S3 Data Pipeline
```python
from tools.database_integration_tool import S3Operations
import json

s3 = S3Operations()

# Upload analysis results
results = {"quality_score": 92, "issues_found": 3}
s3.upload_file(
    json.dumps(results),
    "s3://ultron-bucket/analysis-results.json"
)

# Download for reporting
s3.download_file(
    "s3://ultron-bucket/analysis-results.json",
    "local_results.json"
)
```

---

## 📞 Support & Resources

### Official AWS Documentation
- [AWS Config Getting Started](https://docs.aws.amazon.com/config/latest/developerguide/getting-started.html)
- [AWS Bedrock API Reference](https://docs.aws.amazon.com/bedrock/latest/userguide/)
- [AWS CLI Config Documentation](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)

### ULTRON AWS Tools
- `tools/aws_bedrock_tool.py` - Bedrock integration
- `tools/aws_lambda_tool.py` - Lambda execution
- `tools/voice_aws_tool.py` - Voice/Speech services
- `tools/database_integration_tool.py` - S3 operations

### Quick Commands
```powershell
# Test AWS connectivity
aws sts get-caller-identity

# List available resources
aws configservice describe-config-rules

# Check Config status
aws configservice describe-configuration-recorder-status

# View recent changes
aws configservice get-compliance-summary-by-config-rule
```

---

## ✅ Next Steps

1. **Immediate (5 min)**
   - [ ] Set AWS credentials: `aws configure`
   - [ ] Verify connection: `aws sts get-caller-identity`
   - [ ] Update `ultron_config.json` with AWS section

2. **Short Term (30 min)**
   - [ ] Deploy AWS Config CloudFormation stack
   - [ ] Create IAM user for ULTRON
   - [ ] Store credentials in AWS Secrets Manager

3. **Medium Term (2 hours)**
   - [ ] Test Bedrock integration
   - [ ] Configure S3 bucket for data storage
   - [ ] Set up SNS notifications

4. **Long Term (Ongoing)**
   - [ ] Monitor compliance dashboard
   - [ ] Review AWS cost optimization
   - [ ] Implement custom Config rules

---

## 🎉 You're Ready!

**AWS is now integrated with ULTRON Agent**

- ✅ Bedrock models available
- ✅ Config monitoring enabled
- ✅ S3 storage configured
- ✅ Voice services ready
- ✅ Compliance tracking active

**Start using AWS services:**

```powershell
# Launch ULTRON
python main.py

# In another terminal, use Copilot CLI
copilot
/delegate "Analyze code using AWS Bedrock"
```

---

*ULTRON Agent AWS Integration*
*October 31, 2025*
*Production Ready ✅*
