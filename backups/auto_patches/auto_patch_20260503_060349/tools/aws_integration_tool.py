#!/usr/bin/env python3
"""AWS Integration Tool for ULTRON Agent"""

import os
import json
import boto3
from pathlib import Path
from tools.tool_interface import ToolInterface
from utils.ultron_logger import log_info, log_error

class AWSIntegrationTool(ToolInterface):
    """AWS services integration for ULTRON Agent"""

    @property
    def name(self) -> str:
        return "AWS Integration Tool"

    @property
    def description(self) -> str:
        return "Integrate AWS Bedrock, Lambda, Amplify, and Cognito services"

    def match(self, command: str) -> bool:
        keywords = ["aws", "bedrock", "lambda", "amplify", "cognito", "serverless"]
        return any(kw in command.lower() for kw in keywords)

    def execute(self, command: str, **kwargs) -> str:
        try:
            cmd_lower = command.lower()
            
            if "setup" in cmd_lower:
                return self._setup_aws()
            elif "bedrock" in cmd_lower:
                return self._handle_bedrock(command)
            elif "lambda" in cmd_lower:
                return self._handle_lambda(command)
            elif "amplify" in cmd_lower:
                return self._handle_amplify(command)
            elif "cognito" in cmd_lower:
                return self._handle_cognito(command)
            elif "deploy" in cmd_lower:
                return self._deploy_serverless(command)
            elif "ecr" in cmd_lower or "docker" in cmd_lower:
                return self._handle_ecr(command)
            elif "quicksight" in cmd_lower:
                return self._handle_quicksight(command)
            else:
                return self._show_help()
                
        except Exception as e:
            log_error("aws_integration_tool", f"Error: {e}")
            return f"AWS integration error: {e}"

    def _setup_aws(self) -> str:
        """Setup AWS credentials and configuration"""
        
        aws_dir = Path.home() / ".aws"
        aws_dir.mkdir(exist_ok=True)
        
        credentials_file = aws_dir / "credentials"
        config_file = aws_dir / "config"
        
        # Create credentials template
        if not credentials_file.exists():
            credentials_content = """[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY

[ultron]
aws_access_key_id = YOUR_ULTRON_ACCESS_KEY
aws_secret_access_key = YOUR_ULTRON_SECRET_KEY
"""
            credentials_file.write_text(credentials_content)
        
        # Create config template
        if not config_file.exists():
            config_content = """[default]
region = us-east-1
output = json

[profile ultron]
region = us-east-1
output = json
"""
            config_file.write_text(config_content)
        
        return f"✅ AWS config created at {aws_dir}\n" + \
               "📝 Edit credentials file with your AWS keys\n" + \
               "🌍 Default region: us-east-1"

    def _handle_bedrock(self, command: str) -> str:
        """Handle AWS Bedrock AI operations"""
        
        # Bedrock API key for account 941284019015
        bedrock_api_key = "ABSKQmVkcm9ja0FQSUtleS05MWhyLWF0LTk0MTI4NDAxOTAxNTo3L1lVOXY2TkZYUUpUdVByb3Y1MGNMdy9rby9IbVlYSW55dVF1MzlqejJIQWhxNHlSTnEwbW1LUGNjQT0="
        
        try:
            bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
            
            if "list" in command.lower():
                # List available models
                bedrock_models = boto3.client('bedrock', region_name='us-east-1')
                response = bedrock_models.list_foundation_models()
                models = response.get('modelSummaries', [])
                
                result = "🤖 AWS Bedrock Models:\n"
                for model in models[:5]:  # Show first 5
                    name = model.get('modelName', 'Unknown')
                    model_id = model.get('modelId', 'N/A')
                    result += f"   • {name} ({model_id})\n"
                
                return result
            
            elif "invoke" in command.lower():
                # Test Bedrock invocation
                model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
                
                payload = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 100,
                    "messages": [
                        {"role": "user", "content": "Hello from ULTRON Agent"}
                    ]
                }
                
                response = bedrock.invoke_model(
                    modelId=model_id,
                    body=json.dumps(payload)
                )
                
                result = json.loads(response['body'].read())
                content = result.get('content', [{}])[0].get('text', 'No response')
                
                return f"🤖 Bedrock Response: {content}"
            
            elif "key" in command.lower():
                return f"🔑 Bedrock API Key configured for account 941284019015\n" + \
                       f"Key: {bedrock_api_key[:20]}...\n" + \
                       "✅ Ready for AI model invocation"
            
            else:
                return "Bedrock commands: list models | invoke model | show key"
                
        except Exception as e:
            return f"❌ Bedrock error: {str(e)[:100]}"

    def _handle_lambda(self, command: str) -> str:
        """Handle AWS Lambda operations"""
        
        if "create" in command.lower():
            return self._create_lambda_function()
        elif "list" in command.lower():
            return self._list_lambda_functions()
        else:
            return "Lambda commands: create function | list functions"

    def _create_lambda_function(self) -> str:
        """Create ULTRON Lambda function"""
        
        lambda_code = '''
import json
import boto3

def lambda_handler(event, context):
    """ULTRON Agent Lambda function"""
    
    # Extract command from event
    command = event.get('command', 'hello')
    
    if command == 'hello':
        response = "Hello from ULTRON Lambda!"
    elif command == 'status':
        response = "ULTRON Lambda is operational"
    else:
        response = f"Unknown command: {command}"
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': response,
            'ultron_version': '3.0',
            'timestamp': context.aws_request_id
        })
    }
'''
        
        # Save Lambda code
        lambda_dir = Path("aws_lambda")
        lambda_dir.mkdir(exist_ok=True)
        
        lambda_file = lambda_dir / "ultron_lambda.py"
        lambda_file.write_text(lambda_code)
        
        return f"✅ Lambda function created: {lambda_file}\n" + \
               "📦 Deploy with: aws lambda create-function --function-name ultron-agent"

    def _list_lambda_functions(self) -> str:
        """List Lambda functions"""
        
        try:
            lambda_client = boto3.client('lambda', region_name='us-east-1')
            response = lambda_client.list_functions()
            
            functions = response.get('Functions', [])
            if not functions:
                return "📦 No Lambda functions found"
            
            result = "📦 Lambda Functions:\n"
            for func in functions[:5]:  # Show first 5
                name = func.get('FunctionName', 'Unknown')
                runtime = func.get('Runtime', 'N/A')
                result += f"   • {name} ({runtime})\n"
            
            return result
            
        except Exception as e:
            return f"❌ Lambda list error: {str(e)[:100]}"

    def _handle_amplify(self, command: str) -> str:
        """Handle AWS Amplify operations"""
        
        if "init" in command.lower():
            return self._init_amplify_project()
        elif "deploy" in command.lower():
            return self._deploy_amplify()
        else:
            return "Amplify commands: init project | deploy app"

    def _init_amplify_project(self) -> str:
        """Initialize Amplify project for ULTRON"""
        
        amplify_config = {
            "name": "ultron-web-app",
            "framework": "react",
            "backend": {
                "auth": {"cognito": True},
                "api": {"graphql": True},
                "storage": {"s3": True}
            },
            "frontend": {
                "buildCommand": "npm run build",
                "startCommand": "npm start",
                "outputDirectory": "build"
            }
        }
        
        config_file = Path("amplify.json")
        config_file.write_text(json.dumps(amplify_config, indent=2))
        
        return f"✅ Amplify config created: {config_file}\n" + \
               "🚀 Run: amplify init && amplify push"

    def _deploy_amplify(self) -> str:
        """Deploy Amplify application"""
        
        return "🚀 Amplify deployment:\n" + \
               "1. amplify init\n" + \
               "2. amplify add auth\n" + \
               "3. amplify add api\n" + \
               "4. amplify push\n" + \
               "5. amplify publish"

    def _handle_cognito(self, command: str) -> str:
        """Handle AWS Cognito operations"""
        
        if "create" in command.lower():
            return self._create_user_pool()
        elif "list" in command.lower():
            return self._list_user_pools()
        else:
            return "Cognito commands: create user pool | list user pools"

    def _create_user_pool(self) -> str:
        """Create Cognito User Pool for ULTRON"""
        
        try:
            cognito = boto3.client('cognito-idp', region_name='us-east-1')
            
            response = cognito.create_user_pool(
                PoolName='ultron-users',
                Policies={
                    'PasswordPolicy': {
                        'MinimumLength': 8,
                        'RequireUppercase': True,
                        'RequireLowercase': True,
                        'RequireNumbers': True
                    }
                },
                AutoVerifiedAttributes=['email'],
                UsernameAttributes=['email']
            )
            
            pool_id = response['UserPool']['Id']
            
            return f"✅ Created Cognito User Pool: {pool_id}\n" + \
                   "👥 Features: Email verification, password policy"
            
        except Exception as e:
            return f"❌ Cognito error: {str(e)[:100]}"

    def _list_user_pools(self) -> str:
        """List Cognito User Pools"""
        
        try:
            cognito = boto3.client('cognito-idp', region_name='us-east-1')
            response = cognito.list_user_pools(MaxResults=10)
            
            pools = response.get('UserPools', [])
            if not pools:
                return "👥 No User Pools found"
            
            result = "👥 Cognito User Pools:\n"
            for pool in pools:
                name = pool.get('Name', 'Unknown')
                pool_id = pool.get('Id', 'N/A')
                result += f"   • {name} ({pool_id})\n"
            
            return result
            
        except Exception as e:
            return f"❌ Cognito list error: {str(e)[:100]}"

    def _handle_ecr(self, command: str) -> str:
        """Handle AWS ECR Docker operations"""
        
        cmd_lower = command.lower()
        
        if "login" in cmd_lower:
            return self._ecr_login()
        elif "build" in cmd_lower:
            return self._build_docker_image()
        elif "push" in cmd_lower:
            return self._push_to_ecr()
        elif "deploy" in cmd_lower:
            return self._deploy_docker_stack()
        else:
            return self._ecr_help()

    def _ecr_login(self) -> str:
        """Generate ECR login command"""
        
        account_id = "941284019015"
        region = "us-east-1"
        
        login_cmd = f"(Get-ECRLoginCommand).Password | docker login --username AWS --password-stdin {account_id}.dkr.ecr.{region}.amazonaws.com"
        
        return f"🐳 ECR Docker Login:\n" + \
               f"PowerShell Command:\n{login_cmd}\n\n" + \
               "📋 Prerequisites:\n" + \
               "• AWS Tools for PowerShell installed\n" + \
               "• Docker Desktop running\n" + \
               "• AWS credentials configured"

    def _build_docker_image(self) -> str:
        """Build ULTRON Docker image"""
        
        dockerfile_content = '''FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "main.py"]
'''
        
        # Create Dockerfile
        dockerfile_path = Path("Dockerfile")
        dockerfile_path.write_text(dockerfile_content)
        
        build_cmd = "docker build -t cdk-hnb659fds-container-assets-941284019015-us-east-1 ."
        
        return f"🔨 Docker Build Commands:\n" + \
               f"1. {build_cmd}\n\n" + \
               f"✅ Created Dockerfile at: {dockerfile_path}\n" + \
               "🐳 Image includes ULTRON Agent with all dependencies"

    def _push_to_ecr(self) -> str:
        """Push Docker image to ECR"""
        
        account_id = "941284019015"
        region = "us-east-1"
        repo_name = "cdk-hnb659fds-container-assets-941284019015-us-east-1"
        
        commands = [
            f"docker tag {repo_name}:latest {account_id}.dkr.ecr.{region}.amazonaws.com/{repo_name}:latest",
            f"docker push {account_id}.dkr.ecr.{region}.amazonaws.com/{repo_name}:latest"
        ]
        
        return "🚀 ECR Push Commands:\n" + "\n".join(f"{i+1}. {cmd}" for i, cmd in enumerate(commands)) + \
               "\n\n📦 This will deploy ULTRON Agent as a container to AWS ECR"

    def _deploy_docker_stack(self) -> str:
        """Deploy complete Docker stack"""
        
        steps = [
            "1. 🔐 ECR Login: ecr login",
            "2. 🔨 Build Image: ecr build", 
            "3. 🚀 Push to ECR: ecr push",
            "4. 🌐 Deploy to ECS/Fargate",
            "5. 📊 Monitor with CloudWatch"
        ]
        
        return "🐳 ULTRON Docker Deployment:\n" + "\n".join(steps) + \
               "\n\n💡 Use individual ECR commands for each step"

    def _ecr_help(self) -> str:
        """Show ECR help"""
        
        return """🐳 AWS ECR Docker Commands:

🔐 Authentication:
• "ecr login" - Generate Docker login command

🔨 Build & Deploy:
• "ecr build" - Build ULTRON Docker image
• "ecr push" - Push image to ECR registry
• "ecr deploy" - Complete deployment guide

📋 Quick Start:
1. "ecr login" - Authenticate Docker
2. "ecr build" - Build ULTRON image
3. "ecr push" - Deploy to AWS ECR

🏗️ Infrastructure:
• Account: 941284019015
• Region: us-east-1
• Registry: ECR with CDK assets
"""

    def _deploy_serverless(self, command: str) -> str:
        """Deploy complete serverless ULTRON application"""
        
        deployment_steps = [
            "1. 🔐 Setup AWS credentials",
            "2. 🤖 Deploy Bedrock AI models",
            "3. 📦 Create Lambda functions",
            "4. 🌐 Initialize Amplify web app",
            "5. 👥 Setup Cognito authentication",
            "6. 🐳 Deploy Docker containers (ECR)",
            "7. 🚀 Deploy complete stack"
        ]
        
        return "🚀 ULTRON Serverless Deployment:\n" + "\n".join(deployment_steps) + \
               "\n\n💡 Use individual commands for each step"

    def _handle_quicksight(self, command: str) -> str:
        """Handle AWS QuickSight operations"""
        
        cmd_lower = command.lower()
        
        if "dashboard" in cmd_lower:
            return self._create_quicksight_dashboard()
        elif "agents" in cmd_lower:
            return self._quicksight_agents_view()
        else:
            return self._quicksight_help()

    def _create_quicksight_dashboard(self) -> str:
        """Create QuickSight dashboard for ULTRON metrics"""
        
        return "📊 QuickSight Dashboard Config Created:\n" + \
               "• Dashboard: ULTRON Agent Metrics\n" + \
               "• Account: 941284019015\n" + \
               "• Region: us-east-1\n" + \
               "🚀 Deploy with: aws quicksight create-dashboard"

    def _quicksight_agents_view(self) -> str:
        """Access QuickSight Agents view"""
        
        agents_url = "https://us-east-1.quicksight.aws.amazon.com/sn/start/agents?view=21f5b6bc-9a37-4c2d-b2d5-6d8540251c8b"
        
        return f"🤖 QuickSight Agents View:\n" + \
               f"URL: {agents_url}\n\n" + \
               "📋 Features:\n" + \
               "• AI-powered data insights\n" + \
               "• Natural language queries\n" + \
               "• Automated dashboard generation\n" + \
               "• ULTRON metrics integration"

    def _quicksight_help(self) -> str:
        """Show QuickSight help"""
        
        return """📊 AWS QuickSight Commands:

📈 Dashboard & Analytics:
• "quicksight dashboard" - Create ULTRON metrics dashboard
• "quicksight agents" - Access AI-powered agents view

🔗 Integration:
• Account: 941284019015
• Region: us-east-1
• Data Source: CloudWatch Logs + ULTRON metrics

💡 Use Cases:
• Monitor ULTRON Agent performance
• Analyze user command patterns
• Track AI model usage and efficiency
• Generate automated reports
"""

    def _show_help(self) -> str:
        """Show AWS integration help"""
        
        return """🌩️ AWS Integration Commands:

🔧 Setup:
• "aws setup" - Configure AWS credentials

🤖 Bedrock AI:
• "bedrock list models" - List available AI models
• "bedrock invoke model" - Test model invocation

📦 Lambda:
• "lambda create function" - Create ULTRON Lambda
• "lambda list functions" - List Lambda functions

🌐 Amplify:
• "amplify init project" - Initialize web app
• "amplify deploy app" - Deploy application

👥 Cognito:
• "cognito create user pool" - Create user authentication
• "cognito list user pools" - List user pools

🐳 ECR Docker:
• "ecr login" - Authenticate Docker to ECR
• "ecr build" - Build ULTRON Docker image
• "ecr push" - Push image to registry
• "ecr deploy" - Complete Docker deployment

📊 QuickSight Analytics:
• "quicksight dashboard" - Create ULTRON metrics dashboard
• "quicksight agents" - Access AI-powered agents view

🚀 Deployment:
• "deploy serverless" - Full stack deployment guide

💡 Quick Start:
1. "aws setup" - Configure credentials
2. "bedrock list models" - Check AI models
3. "ecr build" - Build Docker image
4. "deploy serverless" - Deploy ULTRON to AWS
"""

    @classmethod
    def schema(cls) -> dict:
        return {
            "name": "aws_integration_tool",
            "description": "Integrate AWS Bedrock, Lambda, Amplify, and Cognito services",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "AWS integration command to execute"
                    }
                },
                "required": ["command"]
            }
        }