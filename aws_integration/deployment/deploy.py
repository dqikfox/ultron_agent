#!/usr/bin/env python3
"""AWS Infrastructure Deployment Script for ULTRON Agent"""

import boto3
import json
import zipfile
import os
from pathlib import Path
from typing import Dict, Any

class UltronAWSDeployer:
    """Deploy ULTRON Agent AWS infrastructure"""
    
    def __init__(self, region: str = 'us-east-1'):
        self.region = region
        self.cf_client = boto3.client('cloudformation', region_name=region)
        self.lambda_client = boto3.client('lambda', region_name=region)
        self.stack_name = 'ultron-agent-infrastructure'
    
    def deploy_infrastructure(self) -> Dict[str, Any]:
        """Deploy the complete AWS infrastructure"""
        try:
            lambda_zip = self._create_lambda_package()
            stack_outputs = self._deploy_cloudformation_stack()
            self._update_lambda_code(lambda_zip, stack_outputs)
            api_endpoint = stack_outputs.get('ApiEndpoint')
            self._update_ultron_config(api_endpoint)
            
            return {
                'status': 'success',
                'api_endpoint': api_endpoint,
                'stack_outputs': stack_outputs
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _create_lambda_package(self) -> str:
        """Create Lambda deployment package"""
        package_path = Path("aws_integration/lambda_functions/deployment.zip")
        package_path.parent.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            lambda_file = Path("aws_integration/lambda_functions/oasis_bedrock_handler.py")
            if lambda_file.exists():
                zipf.write(lambda_file, "oasis_bedrock_handler.py")
        
        return str(package_path)
    
    def _deploy_cloudformation_stack(self) -> Dict[str, str]:
        """Deploy CloudFormation stack"""
        template_path = Path("aws_integration/cloudformation/ultron-aws-infrastructure.yaml")
        
        with open(template_path, 'r') as f:
            template_body = f.read()
        
        try:
            self.cf_client.describe_stacks(StackName=self.stack_name)
            stack_exists = True
        except self.cf_client.exceptions.ClientError:
            stack_exists = False
        
        parameters = [
            {'ParameterKey': 'ProjectName', 'ParameterValue': 'ultron-agent'},
            {'ParameterKey': 'BudgetAmount', 'ParameterValue': '100'}
        ]
        
        if stack_exists:
            self.cf_client.update_stack(
                StackName=self.stack_name,
                TemplateBody=template_body,
                Parameters=parameters,
                Capabilities=['CAPABILITY_NAMED_IAM']
            )
            waiter = self.cf_client.get_waiter('stack_update_complete')
        else:
            self.cf_client.create_stack(
                StackName=self.stack_name,
                TemplateBody=template_body,
                Parameters=parameters,
                Capabilities=['CAPABILITY_NAMED_IAM']
            )
            waiter = self.cf_client.get_waiter('stack_create_complete')
        
        waiter.wait(StackName=self.stack_name, WaiterConfig={'Delay': 30, 'MaxAttempts': 60})
        
        response = self.cf_client.describe_stacks(StackName=self.stack_name)
        outputs = {}
        
        for output in response['Stacks'][0].get('Outputs', []):
            outputs[output['OutputKey']] = output['OutputValue']
        
        return outputs
    
    def _update_lambda_code(self, zip_path: str, stack_outputs: Dict[str, str]):
        """Update Lambda function with new code"""
        function_name = 'ultron-agent-bedrock-handler'
        
        with open(zip_path, 'rb') as f:
            zip_content = f.read()
        
        self.lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_content
        )
        
        env_vars = {
            'CONVERSATIONS_TABLE': stack_outputs.get('ConversationsTableName', ''),
            'DATA_BUCKET': stack_outputs.get('DataBucketName', '')
        }
        
        self.lambda_client.update_function_configuration(
            FunctionName=function_name,
            Environment={'Variables': env_vars}
        )
    
    def _update_ultron_config(self, api_endpoint: str):
        """Update ULTRON config with AWS settings"""
        config_path = Path("ultron_config.json")
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            config = {}
        
        config['aws_bedrock'] = {
            'enabled': True,
            'api_endpoint': api_endpoint,
            'region': self.region,
            'timeout': 30,
            'default_model': 'amazon.nova-pro-v1:0'
        }
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

def deploy_ultron_aws():
    """Main deployment function"""
    deployer = UltronAWSDeployer()
    result = deployer.deploy_infrastructure()
    
    if result['status'] == 'success':
        print("✅ AWS infrastructure deployed successfully!")
        print(f"🔗 API Endpoint: {result['api_endpoint']}")
    else:
        print(f"❌ Deployment failed: {result['error']}")
    
    return result

if __name__ == "__main__":
    deploy_ultron_aws()