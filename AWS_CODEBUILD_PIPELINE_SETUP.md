# AWS CodeBuild Pipeline Setup for ULTRON Agent

## 🚀 Overview

Complete AWS CodeBuild and CodePipeline integration for ULTRON Agent following AWS best practices for CI/CD automation.

## 📁 Components Created

### 1. **CodeBuild Configuration**
- **`aws_integration/codebuild/buildspec.yml`** - Build specification
- **`aws_integration/codebuild/create_pipeline.py`** - Setup script

### 2. **CodePipeline Configuration**  
- **`aws_integration/codepipeline/pipeline.json`** - Pipeline definition
- Source → Build → Deploy stages

### 3. **GitHub Integration**
- **`.github/workflows/aws-codebuild-integration.yml`** - Trigger builds from GitHub

## 🔧 Setup Instructions

### 1. **Create IAM Roles**

```bash
# CodeBuild Service Role
aws iam create-role --role-name codebuild-ultron-agent-service-role \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {"Service": "codebuild.amazonaws.com"},
        "Action": "sts:AssumeRole"
      }
    ]
  }'

# Attach policies
aws iam attach-role-policy \
  --role-name codebuild-ultron-agent-service-role \
  --policy-arn arn:aws:iam::aws:policy/CloudWatchLogsFullAccess

aws iam attach-role-policy \
  --role-name codebuild-ultron-agent-service-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
```

### 2. **Create S3 Bucket for Artifacts**

```bash
aws s3 mb s3://ultron-agent-pipeline-artifacts --region us-east-1
```

### 3. **Deploy CodeBuild and Pipeline**

```bash
cd aws_integration/codebuild
python create_pipeline.py
```

### 4. **Configure GitHub Integration**

Add these secrets to your GitHub repository:
- `AWS_ROLE_ARN` - IAM role for GitHub Actions
- `AWS_ACCOUNT_ID` - Your AWS account ID

## 🔄 Pipeline Stages

### **Stage 1: Source**
- Pulls code from GitHub repository
- Triggers on push to main/develop branches
- Outputs source artifacts to S3

### **Stage 2: Build** 
- Runs `buildspec.yml` commands:
  - Install Python dependencies
  - Validate CloudFormation templates
  - Run integration tests
  - Package Lambda functions
- Outputs build artifacts

### **Stage 3: Deploy**
- Deploys CloudFormation stack
- Updates Lambda functions
- Configures AWS resources

## 📊 Build Process

### **Install Phase**
```yaml
install:
  runtime-versions:
    python: 3.11
  commands:
    - pip install -r requirements.txt
    - pip install -r aws_integration/requirements.txt
```

### **Pre-Build Phase**
```yaml
pre_build:
  commands:
    - python simple_test.py
    - aws cloudformation validate-template --template-body file://aws_integration/cloudformation/ultron-aws-infrastructure.yaml
```

### **Build Phase**
```yaml
build:
  commands:
    - cd aws_integration/lambda_functions
    - zip -r deployment.zip oasis_bedrock_handler.py
    - python test_amazon_q_integration.py
```

## 🎯 Benefits

### **Automated CI/CD**
- Automatic builds on code changes
- Integrated testing and validation
- Seamless AWS deployment

### **Quality Assurance**
- CloudFormation template validation
- Integration test execution
- Artifact packaging and storage

### **GitHub Integration**
- Trigger builds from GitHub Actions
- Status reporting back to PRs
- Automated deployment workflows

## 🚀 Usage

### **Manual Trigger**
```bash
aws codebuild start-build --project-name ultron-agent-build
```

### **GitHub Trigger**
- Push to main/develop branches
- Create pull requests
- Manual workflow dispatch

### **Monitor Builds**
```bash
# List recent builds
aws codebuild list-builds-for-project --project-name ultron-agent-build

# Get build details
aws codebuild batch-get-builds --ids <build-id>
```

## 📈 Next Steps

1. **Deploy Pipeline**: Run `python create_pipeline.py`
2. **Test Integration**: Push code changes to trigger builds
3. **Monitor Results**: Check AWS Console for build status
4. **Optimize**: Adjust buildspec.yml based on results

---

**🔧 Ready to automate ULTRON Agent deployment with AWS CodeBuild!**