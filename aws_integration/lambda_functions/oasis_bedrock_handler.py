import json
import boto3
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger()
logger.setLevel(logging.INFO)

bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """AWS Lambda handler for ULTRON Agent Bedrock integration"""
    try:
        body = json.loads(event.get('body', '{}'))
        user_message = body.get('message', '')
        conversation_id = body.get('conversation_id', f"ultron_{int(datetime.now().timestamp())}")
        model_id = body.get('model', 'amazon.nova-pro-v1:0')
        
        request_body = {
            "messages": [{"role": "user", "content": [{"text": user_message}]}],
            "inferenceConfig": {"maxTokens": 2000, "temperature": 0.7, "topP": 0.9}
        }
        
        response = bedrock_runtime.converse(
            modelId=model_id,
            messages=request_body["messages"],
            inferenceConfig=request_body["inferenceConfig"]
        )
        
        ai_response = response['output']['message']['content'][0]['text']
        
        table = dynamodb.Table('ultron-conversations')
        table.put_item(
            Item={
                'conversation_id': conversation_id,
                'timestamp': datetime.now().isoformat(),
                'user_message': user_message,
                'ai_response': ai_response,
                'model_used': model_id,
                'tokens_used': response.get('usage', {}).get('totalTokens', 0)
            }
        )
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'response': ai_response,
                'conversation_id': conversation_id,
                'model': model_id,
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }