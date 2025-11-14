"""
AWS Integration for ULTRON Avatar Game
Provides cloud AI, storage, voice, and analytics services
"""

import os
import json
import boto3
from pathlib import Path
from typing import Optional, Dict, Any

class AWSIntegration:
    def __init__(self):
        self.region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        self.enabled = self._check_credentials()
        
        if self.enabled:
            self.bedrock = boto3.client('bedrock-runtime', region_name=self.region)
            self.s3 = boto3.client('s3', region_name=self.region)
            self.polly = boto3.client('polly', region_name=self.region)
            self.comprehend = boto3.client('comprehend', region_name=self.region)
            self.translate = boto3.client('translate', region_name=self.region)
    
    def _check_credentials(self) -> bool:
        """Check if AWS credentials are configured"""
        return bool(os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY'))
    
    # Bedrock AI - Cloud LLM
    def bedrock_chat(self, model_id: str, prompt: str, max_tokens: int = 500) -> Optional[str]:
        """Chat with AWS Bedrock models (Claude, Llama, etc.)"""
        if not self.enabled:
            return None
        
        try:
            body = json.dumps({
                "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
                "max_tokens_to_sample": max_tokens,
                "temperature": 0.7
            })
            
            response = self.bedrock.invoke_model(
                modelId=model_id,
                body=body
            )
            
            result = json.loads(response['body'].read())
            return result.get('completion', '').strip()
        except Exception as e:
            print(f"Bedrock error: {e}")
            return None
    
    # S3 Storage - Save game states to cloud
    def s3_save_game(self, bucket: str, game_data: Dict[str, Any]) -> bool:
        """Save game state to S3"""
        if not self.enabled:
            return False
        
        try:
            key = f"ultron_game_saves/{game_data.get('user_id', 'default')}/save_{int(os.time())}.json"
            self.s3.put_object(
                Bucket=bucket,
                Key=key,
                Body=json.dumps(game_data),
                ContentType='application/json'
            )
            return True
        except Exception as e:
            print(f"S3 save error: {e}")
            return False
    
    def s3_load_game(self, bucket: str, user_id: str = 'default') -> Optional[Dict]:
        """Load latest game state from S3"""
        if not self.enabled:
            return None
        
        try:
            prefix = f"ultron_game_saves/{user_id}/"
            response = self.s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
            
            if 'Contents' not in response:
                return None
            
            # Get latest save
            latest = sorted(response['Contents'], key=lambda x: x['LastModified'])[-1]
            obj = self.s3.get_object(Bucket=bucket, Key=latest['Key'])
            return json.loads(obj['Body'].read())
        except Exception as e:
            print(f"S3 load error: {e}")
            return None
    
    # Polly TTS - Natural voice synthesis
    def polly_speak(self, text: str, voice_id: str = 'Matthew') -> Optional[bytes]:
        """Convert text to speech using AWS Polly"""
        if not self.enabled:
            return None
        
        try:
            response = self.polly.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId=voice_id,
                Engine='neural'
            )
            return response['AudioStream'].read()
        except Exception as e:
            print(f"Polly error: {e}")
            return None
    
    # Comprehend - Sentiment analysis
    def analyze_sentiment(self, text: str) -> Optional[Dict]:
        """Analyze sentiment of user messages"""
        if not self.enabled:
            return None
        
        try:
            response = self.comprehend.detect_sentiment(
                Text=text,
                LanguageCode='en'
            )
            return {
                'sentiment': response['Sentiment'],
                'scores': response['SentimentScore']
            }
        except Exception as e:
            print(f"Comprehend error: {e}")
            return None
    
    # Translate - Multi-language support
    def translate_text(self, text: str, target_lang: str = 'es') -> Optional[str]:
        """Translate text to target language"""
        if not self.enabled:
            return None
        
        try:
            response = self.translate.translate_text(
                Text=text,
                SourceLanguageCode='en',
                TargetLanguageCode=target_lang
            )
            return response['TranslatedText']
        except Exception as e:
            print(f"Translate error: {e}")
            return None
    
    # Character voice mapping
    def get_character_voice(self, character_name: str) -> str:
        """Map character to Polly voice"""
        voices = {
            'Qwen the Architect': 'Brian',      # British, calm
            'Ultron Prime': 'Matthew',          # Deep, authoritative
            'Seeker the Oracle': 'Geraint',     # Welsh, mysterious
            'Llama the Wanderer': 'Joey',       # Friendly, warm
            'Mistral the Swift': 'Justin'       # Young, energetic
        }
        return voices.get(character_name, 'Matthew')

# Global instance
aws = AWSIntegration()
