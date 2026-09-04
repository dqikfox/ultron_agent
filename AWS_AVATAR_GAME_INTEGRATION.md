# AWS Integration for ULTRON Avatar Game

## Overview

The ULTRON Avatar Game now includes comprehensive AWS cloud integration, providing enterprise-grade AI, storage, voice, and analytics capabilities.

---

## ☁️ AWS Services Integrated

### 1. 🧠 Amazon Bedrock - Cloud AI
**Purpose**: Access powerful cloud-based LLMs (Claude, Llama, etc.)

**Features**:
- Claude AI integration for advanced reasoning
- Llama models for general assistance
- Automatic fallback to local models
- Streaming responses support

**Usage**:
- Enable "Use Bedrock AI" checkbox
- Avatars use cloud AI for responses
- Responses marked with ☁️ badge

### 2. 💾 Amazon S3 - Cloud Storage
**Purpose**: Save/load game states to cloud

**Features**:
- Automatic cloud backup
- Multi-device sync
- Version history
- Secure encrypted storage

**Usage**:
- Enable "Cloud Save (S3)" checkbox
- Save/Load buttons use S3
- Bucket: `ultron-game-saves`

### 3. 🎤 Amazon Polly - Neural TTS
**Purpose**: Natural voice synthesis for characters

**Features**:
- Neural voice engine
- Character-specific voices
- Multiple languages
- High-quality audio

**Character Voices**:
- Qwen: Brian (British, calm)
- Ultron: Matthew (Deep, authoritative)
- Seeker: Geraint (Welsh, mysterious)
- Llama: Joey (Friendly, warm)
- Mistral: Justin (Young, energetic)

### 4. 📊 Amazon Comprehend - Sentiment Analysis
**Purpose**: Analyze user message sentiment

**Features**:
- Real-time sentiment detection
- Positive/Negative/Neutral/Mixed
- Confidence scores
- Automatic emoji display

**Display**:
- 😊 Positive
- 😟 Negative
- 😐 Neutral
- 🤔 Mixed

### 5. 🌍 Amazon Translate - Multi-language
**Purpose**: Translate game content

**Features**:
- 75+ languages supported
- Real-time translation
- Context-aware
- High accuracy

---

## 🔧 Setup Instructions

### Prerequisites

1. **AWS Account**: Create at https://aws.amazon.com
2. **IAM User**: Create with programmatic access
3. **Permissions**: Attach policies:
   - `AmazonBedrockFullAccess`
   - `AmazonS3FullAccess`
   - `AmazonPollyFullAccess`
   - `ComprehendFullAccess`
   - `TranslateFullAccess`

### Configuration

#### 1. Set Environment Variables

**Windows (PowerShell)**:
```powershell
$env:AWS_ACCESS_KEY_ID = "your-access-key"
$env:AWS_SECRET_ACCESS_KEY = "your-secret-key"
$env:AWS_DEFAULT_REGION = "us-east-1"
$env:AWS_S3_BUCKET = "ultron-game-saves"
```

**Linux/Mac**:
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
export AWS_S3_BUCKET="ultron-game-saves"
```

#### 2. Create S3 Bucket

```bash
aws s3 mb s3://ultron-game-saves --region us-east-1
```

#### 3. Enable Bedrock Models

```bash
# Request access to Claude in AWS Console
# Navigate to: Bedrock > Model access > Request access
```

### Verification

```bash
# Test AWS connection
python -c "from aws_integration import aws; print('AWS Enabled:', aws.enabled)"

# Check services
curl http://localhost:8082/api/aws/status
```

---

## 🎮 Usage Guide

### In-Game Controls

**AWS Cloud Features Panel**:
- ☁️ Check AWS - Verify connection
- 🧠 Use Bedrock AI - Enable cloud AI
- 💾 Cloud Save (S3) - Enable cloud storage
- 🎤 AWS Polly Voice - Enable neural TTS

### Chat with Cloud AI

1. Enable "Use Bedrock AI" checkbox
2. Chat with any avatar
3. Responses use Claude AI
4. Look for ☁️ badge in messages

### Cloud Save/Load

1. Enable "Cloud Save (S3)" checkbox
2. Click "Save" - Saves to S3
3. Click "Load" - Loads from S3
4. Works across devices

### Voice Synthesis

1. Enable "AWS Polly Voice" checkbox
2. Character voices auto-selected
3. High-quality neural audio
4. Multiple language support

---

## 📊 API Endpoints

### AWS Status
```http
GET /api/aws/status
```

**Response**:
```json
{
  "success": true,
  "enabled": true,
  "region": "us-east-1",
  "services": {
    "bedrock": true,
    "s3": true,
    "polly": true,
    "comprehend": true,
    "translate": true
  }
}
```

### Translate Text
```http
POST /api/aws/translate
Content-Type: application/json

{
  "text": "Hello world",
  "target_lang": "es"
}
```

**Response**:
```json
{
  "success": true,
  "translated": "Hola mundo",
  "target_lang": "es"
}
```

### Generate Voice
```http
POST /api/aws/voice
Content-Type: application/json

{
  "text": "Hello from ULTRON",
  "character": "Ultron Prime"
}
```

**Response**:
```json
{
  "success": true,
  "audio": "base64_encoded_mp3",
  "voice_id": "Matthew"
}
```

---

## 💰 Cost Estimates

### AWS Pricing (Approximate)

**Bedrock (Claude)**:
- $0.008 per 1K input tokens
- $0.024 per 1K output tokens
- ~$0.05 per conversation

**S3 Storage**:
- $0.023 per GB/month
- Game saves: ~1MB each
- ~$0.001 per 1000 saves

**Polly TTS**:
- $4.00 per 1M characters
- Average message: 100 chars
- ~$0.0004 per message

**Comprehend**:
- $0.0001 per unit (100 chars)
- ~$0.0001 per message

**Translate**:
- $15.00 per 1M characters
- ~$0.0015 per message

**Monthly Estimate** (1000 messages):
- Bedrock: $50
- S3: $0.10
- Polly: $0.40
- Comprehend: $0.10
- Translate: $1.50
- **Total: ~$52/month**

### Free Tier

AWS offers 12-month free tier:
- Bedrock: Limited free usage
- S3: 5GB storage, 20K requests
- Polly: 5M characters/month
- Comprehend: 50K units/month
- Translate: 2M characters/month

---

## 🔒 Security Best Practices

### Credentials Management

1. **Never hardcode credentials**
2. **Use environment variables**
3. **Rotate keys regularly**
4. **Use IAM roles when possible**
5. **Enable MFA on AWS account**

### S3 Security

```bash
# Enable encryption
aws s3api put-bucket-encryption \
  --bucket ultron-game-saves \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# Block public access
aws s3api put-public-access-block \
  --bucket ultron-game-saves \
  --public-access-block-configuration \
    BlockPublicAcls=true,IgnorePublicAcls=true,\
    BlockPublicPolicy=true,RestrictPublicBuckets=true
```

### IAM Policy (Least Privilege)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket",
        "polly:SynthesizeSpeech",
        "comprehend:DetectSentiment",
        "translate:TranslateText"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## 🐛 Troubleshooting

### AWS Not Enabled

**Symptom**: "AWS NOT CONFIGURED" warning

**Solutions**:
1. Check environment variables set
2. Verify credentials valid
3. Check IAM permissions
4. Test with AWS CLI: `aws sts get-caller-identity`

### Bedrock Access Denied

**Symptom**: "Access denied" errors

**Solutions**:
1. Request model access in AWS Console
2. Check IAM permissions
3. Verify region supports Bedrock
4. Wait for access approval (can take hours)

### S3 Bucket Not Found

**Symptom**: "Bucket does not exist"

**Solutions**:
1. Create bucket: `aws s3 mb s3://ultron-game-saves`
2. Check bucket name in env var
3. Verify region matches
4. Check IAM permissions

### Polly Voice Failed

**Symptom**: "Voice generation failed"

**Solutions**:
1. Check text length (<3000 chars)
2. Verify voice ID valid
3. Check IAM permissions
4. Try different voice

---

## 📈 Performance Optimization

### Caching

```python
# Cache Bedrock responses
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_bedrock_chat(prompt):
    return aws.bedrock_chat('anthropic.claude-v2', prompt)
```

### Batch Operations

```python
# Batch S3 uploads
def batch_save_games(games):
    for game in games:
        aws.s3_save_game('ultron-game-saves', game)
```

### Async Processing

```python
import asyncio

async def async_translate(texts):
    tasks = [aws.translate_text(text) for text in texts]
    return await asyncio.gather(*tasks)
```

---

## 🚀 Advanced Features

### Multi-Region Deployment

```python
# Use multiple regions for redundancy
regions = ['us-east-1', 'us-west-2', 'eu-west-1']
for region in regions:
    aws_client = AWSIntegration(region=region)
```

### Custom Voice Training

```python
# Use custom Polly lexicons
lexicon = {
    'ULTRON': 'UL-tron',
    'Qwen': 'Kwen'
}
aws.polly.put_lexicon(Name='ultron', Content=json.dumps(lexicon))
```

### Sentiment-Based Responses

```python
def adaptive_response(message):
    sentiment = aws.analyze_sentiment(message)
    if sentiment['sentiment'] == 'NEGATIVE':
        return "I sense frustration. How can I help?"
    return "Great! Let's continue."
```

---

## 📚 Additional Resources

### AWS Documentation

- [Bedrock User Guide](https://docs.aws.amazon.com/bedrock/)
- [S3 Developer Guide](https://docs.aws.amazon.com/s3/)
- [Polly Developer Guide](https://docs.aws.amazon.com/polly/)
- [Comprehend Developer Guide](https://docs.aws.amazon.com/comprehend/)
- [Translate Developer Guide](https://docs.aws.amazon.com/translate/)

### ULTRON Documentation

- `aws_integration.py` - Integration module
- `avatar_game_server.py` - Server implementation
- `AWS_QUICKSTART.md` - Quick setup guide

---

## ✅ Feature Checklist

- [x] Bedrock AI integration
- [x] S3 cloud storage
- [x] Polly neural TTS
- [x] Comprehend sentiment analysis
- [x] Translate multi-language
- [x] Character-specific voices
- [x] Cloud save/load
- [x] Real-time sentiment display
- [x] AWS status checking
- [x] Error handling
- [x] Security best practices
- [x] Cost optimization

---

**Ready to use AWS cloud features!**

🎮 Enable AWS checkboxes → Configure credentials → Start using cloud AI!
