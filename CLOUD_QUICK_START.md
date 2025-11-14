# ULTRON Cloud Integration - Quick Start

## ⚡ 15-Minute Setup

### Step 1: Install Dependencies (2 min)
```bash
setup_cloud.bat
```

### Step 2: Configure AWS (5 min)
```bash
# Install AWS CLI
winget install Amazon.AWSCLI

# Configure credentials
aws configure
# Enter: Access Key ID, Secret Key, Region (us-east-1), Format (json)

# Test
aws sts get-caller-identity
```

### Step 3: Configure Azure (5 min)
```bash
# Get Azure OpenAI key from portal.azure.com
# Set environment variable
setx AZURE_OPENAI_KEY "your_key_here"
setx AZURE_OPENAI_ENDPOINT "https://your-resource.openai.azure.com/"

# Restart terminal
```

### Step 4: Test Integration (3 min)
```python
# test_cloud.py
from tools.cloud_router import CloudRouter
import asyncio

async def test():
    router = CloudRouter({})
    
    # Test routing
    provider, model = await router.route_request("Hello, test message")
    print(f"Routed to: {provider}/{model}")
    
    # Test execution
    result = await router.execute_request("What is 2+2?", provider, model)
    print(f"Result: {result}")
    
    # Show stats
    print(f"Stats: {router.get_stats()}")

asyncio.run(test())
```

Run: `python test_cloud.py`

---

## 🎯 Usage Examples

### Example 1: Simple Query (Uses Local)
```python
from tools.cloud_router import CloudRouter

router = CloudRouter(config)
provider, model = await router.route_request("What time is it?")
# Returns: ('local', 'llava:7b') - Free, fast
```

### Example 2: Code Generation (Uses AWS)
```python
provider, model = await router.route_request(
    "Write a Python function to sort a list",
    requirements={'code': True}
)
# Returns: ('aws', 'claude-3-sonnet') - Best for code
```

### Example 3: Vision Task (Uses Azure)
```python
provider, model = await router.route_request(
    "Describe this image",
    requirements={'vision': True}
)
# Returns: ('azure', 'gpt-4-vision') - Best for vision
```

### Example 4: Force Provider
```python
provider, model = await router.route_request(
    "Complex analysis task",
    requirements={'provider': 'azure'}
)
# Returns: ('azure', 'gpt-4-turbo') - User choice
```

---

## 💰 Cost Tracking

### View Current Costs
```python
from utils.cost_tracker import CostTracker

tracker = CostTracker()
print(tracker.get_monthly_costs())
# Output: {'aws': 45.23, 'azure': 12.50, 'total': 57.73}
```

### Set Budget Alerts
```python
tracker.set_budget_limit(150)  # $150/month
tracker.enable_alerts(email='your@email.com')
```

---

## 🔧 Configuration

Edit `cloud_config.json`:

```json
{
  "aws": {
    "region": "us-east-1",
    "bedrock_model": "claude-3-sonnet",
    "s3_bucket": "ultron-agent-memory",
    "lambda_timeout": 30
  },
  "azure": {
    "openai_model": "gpt-4-turbo",
    "endpoint": "https://your-resource.openai.azure.com/",
    "api_version": "2024-02-01"
  },
  "routing": {
    "default_provider": "aws",
    "fallback_to_local": true,
    "cost_limit_monthly": 150,
    "prefer_local_under_tokens": 1000
  }
}
```

---

## 🚀 Advanced Features

### 1. Memory Sync to S3
```python
from utils.s3_memory import S3Memory

s3_mem = S3Memory()
await s3_mem.save_memory(memory_data)
```

### 2. Global Memory with Cosmos DB
```python
from utils.cosmos_memory import CosmosMemory

cosmos = CosmosMemory()
await cosmos.store_memory('user123', data)
```

### 3. Serverless Tool Execution
```python
from tools.lambda_executor import LambdaExecutor

executor = LambdaExecutor()
result = await executor.execute_tool('web_scraper', {'url': 'example.com'})
```

---

## 📊 Monitoring

### CloudWatch Dashboard (AWS)
```bash
aws cloudwatch get-dashboard --dashboard-name ultron-metrics
```

### Azure Monitor
```bash
az monitor metrics list --resource ultron-functions
```

---

## 🔒 Security Best Practices

1. **Never commit credentials**
   - Use environment variables
   - Use AWS Secrets Manager / Azure Key Vault

2. **Enable MFA**
   ```bash
   aws iam enable-mfa-device
   ```

3. **Use least privilege IAM**
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [{
       "Effect": "Allow",
       "Action": ["bedrock:InvokeModel", "s3:PutObject"],
       "Resource": "*"
     }]
   }
   ```

4. **Rotate keys monthly**
   ```bash
   aws iam create-access-key --user-name ultron-agent
   ```

---

## 🐛 Troubleshooting

### AWS Connection Failed
```bash
# Check credentials
aws sts get-caller-identity

# Check region
aws configure get region

# Test Bedrock access
aws bedrock list-foundation-models
```

### Azure Connection Failed
```bash
# Check environment variables
echo %AZURE_OPENAI_KEY%
echo %AZURE_OPENAI_ENDPOINT%

# Test connection
curl -X POST %AZURE_OPENAI_ENDPOINT%/openai/deployments/gpt-4/chat/completions ^
  -H "api-key: %AZURE_OPENAI_KEY%" ^
  -H "Content-Type: application/json" ^
  -d "{\"messages\":[{\"role\":\"user\",\"content\":\"test\"}]}"
```

### High Costs
```python
# Check usage
tracker = CostTracker()
print(tracker.get_detailed_usage())

# Reduce costs
config['routing']['prefer_local_under_tokens'] = 5000  # Use local more
config['routing']['cost_limit_monthly'] = 100  # Lower limit
```

---

## 📚 Resources

- **AWS Bedrock**: https://aws.amazon.com/bedrock/
- **Azure OpenAI**: https://azure.microsoft.com/en-us/products/ai-services/openai-service
- **Cost Calculator**: https://calculator.aws / https://azure.microsoft.com/en-us/pricing/calculator/
- **Full Strategy**: See `CLOUD_INTEGRATION_STRATEGY.md`

---

*Ready to scale ULTRON to the cloud!*
