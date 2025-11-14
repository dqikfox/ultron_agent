import json
import boto3

def lambda_handler(event, context):
    """ULTRON Agent Lambda function"""
    
    command = event.get('command', 'hello')
    
    if command == 'hello':
        response = "Hello from ULTRON Lambda!"
    elif command == 'status':
        response = "ULTRON Lambda is operational"
    elif command == 'bedrock':
        try:
            bedrock = boto3.client('bedrock-runtime')
            model_response = bedrock.invoke_model(
                modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 50,
                    "messages": [{"role": "user", "content": "ULTRON status check"}]
                })
            )
            result = json.loads(model_response['body'].read())
            response = result.get('content', [{}])[0].get('text', 'AI response unavailable')
        except Exception as e:
            response = f"Bedrock error: {str(e)}"
    else:
        response = f"Unknown command: {command}"
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'message': response,
            'ultron_version': '3.0',
            'timestamp': context.aws_request_id,
            'command_processed': command
        })
    }