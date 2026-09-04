"""
Cloud Router - Intelligent routing between AWS, Azure, and Local models
"""
import os
import json
import time
from typing import Dict, Any, Optional, Tuple
from utils.ultron_logger import log_info, log_error, log_ai_decision

class CloudRouter:
    """Routes AI requests to optimal cloud provider"""

    def __init__(self, config):
        self.config = config
        self.aws_available = self._check_aws()
        self.azure_available = self._check_azure()
        self.local_available = True  # Ollama always available

        # Cost per 1K tokens
        self.costs = {
            'aws_claude': 0.003,
            'azure_gpt4': 0.03,
            'local_ollama': 0.0
        }

        # Performance cache
        self.response_times = {
            'aws': [],
            'azure': [],
            'local': []
        }

    def _check_aws(self) -> bool:
        """Check AWS credentials"""
        try:
            import boto3
            boto3.client('sts').get_caller_identity()
            return True
        except:
            return False

    def _check_azure(self) -> bool:
        """Check Azure credentials"""
        return bool(os.getenv('AZURE_OPENAI_KEY'))

    async def route_request(self, prompt: str, requirements: Dict[str, Any] = None) -> Tuple[str, str]:
        """
        Route request to best provider
        Returns: (provider, model)
        """
        requirements = requirements or {}

        # Priority 1: User preference
        if requirements.get('provider'):
            return requirements['provider'], self._get_model(requirements['provider'])

        # Priority 2: Task requirements
        if requirements.get('vision'):
            if self.azure_available:
                return 'azure', 'gpt-4-vision'
            return 'local', 'llava:7b'

        if requirements.get('code'):
            if self.aws_available:
                return 'aws', 'claude-3-sonnet'
            return 'local', 'qwen3-coder'

        # Priority 3: Cost optimization
        token_estimate = len(prompt.split()) * 1.3  # Rough estimate

        if token_estimate < 1000:  # Small request
            from config import config
            return 'local', config.get('llm_model', 'dolphin3:latest')  # Free

        if token_estimate < 10000:  # Medium request
            if self.aws_available:
                return 'aws', 'claude-3-sonnet'  # Cheaper
            from config import config
            return 'local', config.get('llm_model', 'dolphin3:latest')

        # Large request - use best available
        if self.aws_available:
            return 'aws', 'claude-3-sonnet'
        if self.azure_available:
            return 'azure', 'gpt-4-turbo'
        from config import config
        return 'local', config.get('llm_model', 'dolphin3:latest')

    def _get_model(self, provider: str) -> str:
        """Get default model for provider"""
        models = {
            'aws': 'claude-3-sonnet',
            'azure': 'gpt-4-turbo',
            'local': None
        }
        if provider == 'local':
            from config import config
            return config.get('llm_model', 'dolphin3:latest')
        return models.get(provider, 'dolphin3:latest')

    async def execute_request(self, prompt: str, provider: str, model: str) -> str:
        """Execute request on chosen provider"""
        start_time = time.time()

        try:
            if provider == 'aws':
                result = await self._execute_aws(prompt, model)
            elif provider == 'azure':
                result = await self._execute_azure(prompt, model)
            else:
                result = await self._execute_local(prompt, model)

            # Track performance
            duration = time.time() - start_time
            self.response_times[provider].append(duration)

            log_ai_decision("cloud_router",
                          f"Routed to {provider}/{model}",
                          model,
                          confidence_score=0.9)

            return result

        except Exception as e:
            log_error("cloud_router", f"Failed on {provider}: {e}")
            # Fallback to local
            if provider != 'local':
                return await self._execute_local(prompt, 'llava:7b')
            raise

    async def _execute_aws(self, prompt: str, model: str) -> str:
        """Execute on AWS Bedrock"""
        import boto3

        client = boto3.client('bedrock-runtime', region_name='us-east-1')

        response = client.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "messages": [{"role": "user", "content": prompt}]
            })
        )

        result = json.loads(response['body'].read())
        return result['content'][0]['text']

    async def _execute_azure(self, prompt: str, model: str) -> str:
        """Execute on Azure OpenAI"""
        from openai import AzureOpenAI

        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version="2024-02-01",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content

    async def _execute_local(self, prompt: str, model: str) -> str:
        """Execute on local Ollama"""
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.post(
                'http://localhost:11434/api/generate',
                json={'model': model, 'prompt': prompt}
            ) as response:
                result = await response.json()
                return result.get('response', '')

    def get_stats(self) -> Dict[str, Any]:
        """Get routing statistics"""
        return {
            'aws_available': self.aws_available,
            'azure_available': self.azure_available,
            'local_available': self.local_available,
            'avg_response_times': {
                'aws': sum(self.response_times['aws']) / len(self.response_times['aws']) if self.response_times['aws'] else 0,
                'azure': sum(self.response_times['azure']) / len(self.response_times['azure']) if self.response_times['azure'] else 0,
                'local': sum(self.response_times['local']) / len(self.response_times['local']) if self.response_times['local'] else 0
            }
        }
