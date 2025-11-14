# ULTRON Agent AWS Integration

## 🚀 Overview

Complete AWS integration for ULTRON Agent featuring:
- **Amazon Bedrock**: Cloud-based AI inference with Nova Pro models
- **AWS Lambda**: Serverless compute for AI processing
- **DynamoDB**: Conversation persistence and history
- **API Gateway**: RESTful endpoints for cloud AI access
- **CloudWatch**: Monitoring and cost tracking
- **S3**: Data storage and backup

## 🏗️ Architecture

```
ULTRON Agent (Local)
    ↓
API Gateway → Lambda Function → Amazon Bedrock
    ↓              ↓                ↓
CloudWatch    DynamoDB         S3 Storage
```

## 📦 Components

### 1. Lambda Functions
- **`oasis_bedrock_handler.py`**: Main Bedrock integration handler
- Processes chat requests and manages conversations
- Handles model switching and response streaming

### 2. CloudFormation Infrastructure
- **`ultron-aws-infrastructure.yaml`**: Complete infrastructure as code
- Creates all AWS resources with proper IAM roles
- Includes cost monitoring and budget alerts

### 3. Cost Monitoring
- **`cost_monitor.py`**: Real-time cost tracking
- Budget alerts at 25%, 50%, 75%, 90% thresholds
- CloudWatch metrics and dashboards

### 4. ULTRON Integration
- **`aws_bedrock_tool.py`**: Tool plugin for local agent
- Seamless integration with existing tool system
- Conversation persistence and history

## 🚀 Quick Deployment

### Prerequisites
```bash
# Install AWS CLI
pip install awscli boto3

# Configure AWS credentials
aws configure
```

### Deploy Infrastructure
```bash
# Deploy via Python script
cd aws_integration/deployment
python deploy.py

# Or use GitHub Actions workflow
# Go to Actions → AWS Infrastructure Deployment → Run workflow
```

### Manual Deployment Steps

1. **Create IAM Role**:
```bash
aws iam create-role --role-name UltronLambdaRole \
  --assume-role-policy-document file://trust-policy.json

aws iam attach-role-policy --role-name UltronLambdaRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

2. **Deploy CloudFormation Stack**:
```bash
aws cloudformation create-stack \
  --stack-name ultron-agent-infrastructure \
  --template-body file://cloudformation/ultron-aws-infrastructure.yaml \
  --parameters ParameterKey=ProjectName,ParameterValue=ultron-agent \
               ParameterKey=BudgetAmount,ParameterValue=100 \
  --capabilities CAPABILITY_NAMED_IAM
```

3. **Update Lambda Code**:
```bash
zip -r deployment.zip lambda_functions/oasis_bedrock_handler.py

aws lambda update-function-code \
  --function-name ultron-agent-bedrock-handler \
  --zip-file fileb://deployment.zip
```

## 🔧 Configuration

### ULTRON Agent Config
Add to `ultron_config.json`:
```json
{
  "aws_bedrock": {
    "enabled": true,
    "api_endpoint": "https://your-api-id.execute-api.us-east-1.amazonaws.com/prod",
    "region": "us-east-1",
    "timeout": 30,
    "default_model": "amazon.nova-pro-v1:0"
  }
}
```

### Available Models
- `amazon.nova-pro-v1:0` - Advanced reasoning and coding
- `amazon.nova-lite-v1:0` - Fast, lightweight responses
- `anthropic.claude-3-sonnet-20240229-v1:0` - Claude 3 Sonnet
- `anthropic.claude-3-haiku-20240307-v1:0` - Claude 3 Haiku

## 💬 Usage

### Via ULTRON Agent
```bash
# Use AWS Bedrock for responses
"bedrock what is quantum computing?"
"aws ai explain machine learning"
"nova pro help me debug this code"
```

### Direct API Calls
```bash
curl -X POST https://your-api-endpoint/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello from ULTRON Agent",
    "model": "amazon.nova-pro-v1:0"
  }'
```

### Python Integration
```python
from tools.aws_bedrock_tool import AWSBedrockTool

bedrock = AWSBedrockTool()
response = bedrock.execute("Explain AWS Lambda")
print(response)
```

## 📊 Monitoring & Costs

### Cost Tracking
```bash
# Run cost monitoring
python aws_integration/monitoring/cost_monitor.py

# View current costs
aws ce get-cost-and-usage \
  --time-period Start=2025-01-01,End=2025-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost
```

### CloudWatch Dashboards
- **ULTRON/Costs**: Cost metrics and trends
- **ULTRON/Usage**: API calls and token usage
- **ULTRON/Performance**: Response times and errors

### Budget Alerts
Automatic alerts at:
- 🟡 25% of budget ($25)
- 🟠 50% of budget ($50)  
- 🔴 75% of budget ($75)
- 🚨 90% of budget ($90)

## 🔒 Security

### IAM Permissions
- Least privilege access for Lambda functions
- Bedrock model access restricted to specific models
- DynamoDB access limited to ULTRON tables
- S3 access restricted to project bucket

### Data Protection
- All data encrypted at rest and in transit
- Conversation data stored in DynamoDB with TTL
- S3 bucket with versioning and encryption
- CloudTrail logging for audit compliance

## 🧪 Testing

### Integration Tests
```bash
# Test AWS Bedrock tool
python test_q_developer_integration.py

# Test Lambda function locally
python -c "
from aws_integration.lambda_functions.oasis_bedrock_handler import lambda_handler
event = {'body': '{\"message\": \"test\"}'}
result = lambda_handler(event, None)
print(result)
"
```

### Load Testing
```bash
# Install locust
pip install locust

# Run load tests
locust -f aws_integration/testing/load_test.py \
  --host https://your-api-endpoint
```

## 🚨 Troubleshooting

### Common Issues

**Lambda Timeout**:
```bash
aws lambda update-function-configuration \
  --function-name ultron-agent-bedrock-handler \
  --timeout 60
```

**Bedrock Access Denied**:
```bash
# Check IAM permissions
aws iam get-role-policy \
  --role-name UltronLambdaRole \
  --policy-name UltronBedrockAccess
```

**API Gateway 502 Error**:
```bash
# Check Lambda logs
aws logs tail /aws/lambda/ultron-agent-bedrock-handler --follow
```

### Debug Commands
```bash
# Test API Gateway
curl -v https://your-api-endpoint/chat

# Check CloudFormation stack
aws cloudformation describe-stacks \
  --stack-name ultron-agent-infrastructure

# Monitor costs
aws ce get-cost-and-usage \
  --time-period Start=$(date -d "1 month ago" +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost
```

## 📈 Scaling & Optimization

### Performance Tuning
- Lambda memory: 512MB (adjustable based on usage)
- DynamoDB: On-demand billing for variable workloads
- API Gateway: Regional endpoints for lower latency
- CloudFront: CDN for static assets (optional)

### Cost Optimization
- Use Nova Lite for simple queries
- Implement response caching
- Set DynamoDB TTL for old conversations
- Monitor and optimize Lambda execution time

## 🔄 CI/CD Integration

### GitHub Actions
- Automated deployment on push to main
- Infrastructure validation and testing
- Cost monitoring and alerts
- Security scanning with Amazon Q Developer

### Deployment Environments
- **Dev**: Development testing with lower limits
- **Staging**: Pre-production validation
- **Prod**: Production deployment with full monitoring

## 📞 Support

### AWS Resources
- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [DynamoDB Developer Guide](https://docs.aws.amazon.com/dynamodb/latest/developerguide/)

### ULTRON Agent Integration
- Check `logs/aws_bedrock_tool.log` for integration issues
- Use `python test_q_developer_integration.py` for validation
- Review `ultron_config.json` for configuration problems

---

**🤖 Ready to enhance ULTRON Agent with cloud-scale AI capabilities!**