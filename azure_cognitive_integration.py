#!/usr/bin/env python3
"""
Azure Cognitive Services Integration for ULTRON Agent.
Provides advanced NLP capabilities including LUIS, Text Analytics, and Speech Services.
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

# Azure SDK imports (optional)
try:
    from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient
    from azure.cognitiveservices.language.textanalytics import TextAnalyticsClient
    from azure.core.credentials import AzureKeyCredential
    from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer, SpeechRecognizer
    from azure.cognitiveservices.speech.audio import AudioOutputConfig
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    LUISRuntimeClient = None
    TextAnalyticsClient = None
    SpeechConfig = None
    SpeechSynthesizer = None
    SpeechRecognizer = None
    AudioOutputConfig = None

from utils.ultron_logger import get_logger

logger = get_logger(__name__)

class AzureCognitiveIntegration:
    """
    Azure Cognitive Services integration for advanced NLP capabilities.
    Includes LUIS for intent recognition, Text Analytics for sentiment analysis,
    and Speech Services for voice processing.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Azure Cognitive Services integration.

        Args:
            config: Configuration dictionary with Azure credentials and settings
        """
        self.config = config or {}
        self.luis_client = None
        self.text_analytics_client = None
        self.speech_config = None

        # Azure service endpoints and keys
        self.luis_endpoint = self.config.get('azure_luis_endpoint')
        self.luis_key = self.config.get('azure_luis_key')
        self.luis_app_id = self.config.get('azure_luis_app_id')
        self.luis_app_version = self.config.get('azure_luis_app_version', '0.1')

        self.text_analytics_endpoint = self.config.get('azure_text_analytics_endpoint')
        self.text_analytics_key = self.config.get('azure_text_analytics_key')

        self.speech_key = self.config.get('azure_speech_key')
        self.speech_region = self.config.get('azure_speech_region', 'eastus')

        # Initialize services if credentials are available
        self._initialize_services()

        logger.info("Azure Cognitive Services integration initialized")

    def _initialize_services(self):
        """Initialize Azure Cognitive Services clients."""
        if not AZURE_AVAILABLE:
            logger.warning("Azure SDK not available. Install azure-cognitiveservices-* packages")
            return

        try:
            # Initialize LUIS
            if self.luis_endpoint and self.luis_key:
                self.luis_client = LUISRuntimeClient(
                    self.luis_endpoint,
                    AzureKeyCredential(self.luis_key)
                )
                logger.info("LUIS client initialized")
            else:
                logger.warning("LUIS credentials not configured")

            # Initialize Text Analytics
            if self.text_analytics_endpoint and self.text_analytics_key:
                self.text_analytics_client = TextAnalyticsClient(
                    endpoint=self.text_analytics_endpoint,
                    credential=AzureKeyCredential(self.text_analytics_key)
                )
                logger.info("Text Analytics client initialized")
            else:
                logger.warning("Text Analytics credentials not configured")

            # Initialize Speech Services
            if self.speech_key and self.speech_region:
                self.speech_config = SpeechConfig(
                    subscription=self.speech_key,
                    region=self.speech_region
                )
                logger.info("Azure Speech Services initialized")
            else:
                logger.warning("Azure Speech credentials not configured")

        except Exception as e:
            logger.error(f"Failed to initialize Azure services: {e}")

    def is_available(self) -> bool:
        """
        Check if Azure Cognitive Services are available and configured.

        Returns:
            bool: True if at least one service is available
        """
        return AZURE_AVAILABLE and (
            (self.luis_client is not None) or
            (self.text_analytics_client is not None) or
            (self.speech_config is not None)
        )

    def recognize_intent_luis(self, text: str) -> Dict[str, Any]:
        """
        Recognize intent and entities using Azure LUIS.

        Args:
            text: Input text to analyze

        Returns:
            dict: LUIS prediction results with intent, entities, and confidence scores
        """
        if not self.luis_client or not self.luis_app_id:
            return {
                'intent': 'unknown',
                'confidence': 0.0,
                'entities': [],
                'error': 'LUIS not configured'
            }

        try:
            prediction_request = {
                "query": text
            }

            prediction_response = self.luis_client.prediction.get_slot_prediction(
                app_id=self.luis_app_id,
                slot_name=self.luis_app_version,
                prediction_request=prediction_request
            )

            # Extract top intent
            top_intent = prediction_response.prediction.top_intent
            intent_score = prediction_response.prediction.intents[top_intent].score

            # Extract entities
            entities = []
            for entity_name, entity_data in prediction_response.prediction.entities.items():
                entities.append({
                    'name': entity_name,
                    'type': entity_data.type,
                    'value': entity_data.entity,
                    'confidence': entity_data.score
                })

            result = {
                'intent': top_intent,
                'confidence': intent_score,
                'entities': entities,
                'query': text,
                'timestamp': datetime.now().isoformat()
            }

            logger.info(f"LUIS intent recognition: {top_intent} ({intent_score:.2f})")
            return result

        except Exception as e:
            logger.error(f"LUIS intent recognition failed: {e}")
            return {
                'intent': 'unknown',
                'confidence': 0.0,
                'entities': [],
                'error': str(e)
            }

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text using Azure Text Analytics.

        Args:
            text: Input text to analyze

        Returns:
            dict: Sentiment analysis results with overall sentiment and confidence scores
        """
        if not self.text_analytics_client:
            return {
                'sentiment': 'neutral',
                'confidence_scores': {'positive': 0.0, 'neutral': 1.0, 'negative': 0.0},
                'error': 'Text Analytics not configured'
            }

        try:
            documents = [text]
            response = self.text_analytics_client.analyze_sentiment(documents=documents)

            if response and response[0]:
                result = response[0]
                sentiment_result = {
                    'sentiment': result.sentiment,
                    'confidence_scores': {
                        'positive': result.confidence_scores.positive,
                        'neutral': result.confidence_scores.neutral,
                        'negative': result.confidence_scores.negative
                    },
                    'sentences': []
                }

                # Add sentence-level analysis
                for sentence in result.sentences:
                    sentiment_result['sentences'].append({
                        'text': sentence.text,
                        'sentiment': sentence.sentiment,
                        'confidence_scores': {
                            'positive': sentence.confidence_scores.positive,
                            'neutral': sentence.confidence_scores.neutral,
                            'negative': sentence.confidence_scores.negative
                        }
                    })

                logger.info(f"Azure sentiment analysis: {result.sentiment}")
                return sentiment_result
            else:
                return {
                    'sentiment': 'neutral',
                    'confidence_scores': {'positive': 0.0, 'neutral': 1.0, 'negative': 0.0},
                    'error': 'No analysis results'
                }

        except Exception as e:
            logger.error(f"Azure sentiment analysis failed: {e}")
            return {
                'sentiment': 'neutral',
                'confidence_scores': {'positive': 0.0, 'neutral': 1.0, 'negative': 0.0},
                'error': str(e)
            }

    def extract_key_phrases(self, text: str) -> List[str]:
        """
        Extract key phrases from text using Azure Text Analytics.

        Args:
            text: Input text to analyze

        Returns:
            list: List of key phrases extracted from the text
        """
        if not self.text_analytics_client:
            logger.warning("Text Analytics not configured for key phrase extraction")
            return []

        try:
            documents = [text]
            response = self.text_analytics_client.extract_key_phrases(documents=documents)

            if response and response[0]:
                key_phrases = list(response[0].key_phrases)
                logger.info(f"Extracted {len(key_phrases)} key phrases")
                return key_phrases
            else:
                return []

        except Exception as e:
            logger.error(f"Key phrase extraction failed: {e}")
            return []

    def detect_language(self, text: str) -> Dict[str, Any]:
        """
        Detect language of text using Azure Text Analytics.

        Args:
            text: Input text to analyze

        Returns:
            dict: Language detection results with language code and confidence
        """
        if not self.text_analytics_client:
            return {
                'language': 'en',
                'confidence': 0.0,
                'error': 'Text Analytics not configured'
            }

        try:
            documents = [text]
            response = self.text_analytics_client.detect_language(documents=documents)

            if response and response[0]:
                result = response[0]
                language_result = {
                    'language': result.primary_language.iso6391_name,
                    'confidence': result.primary_language.confidence_score,
                    'name': result.primary_language.name
                }

                logger.info(f"Detected language: {language_result['language']} "
                          f"({language_result['confidence']:.2f})")
                return language_result
            else:
                return {
                    'language': 'en',
                    'confidence': 0.0,
                    'error': 'No language detection results'
                }

        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return {
                'language': 'en',
                'confidence': 0.0,
                'error': str(e)
            }

    def text_to_speech_azure(self, text: str, voice_name: str = "en-US-AriaRUS") -> bytes:
        """
        Convert text to speech using Azure Speech Services.

        Args:
            text: Text to convert to speech
            voice_name: Name of the voice to use

        Returns:
            bytes: Audio data in WAV format
        """
        if not self.speech_config:
            raise Exception("Azure Speech Services not configured")

        try:
            # Configure voice
            self.speech_config.speech_synthesis_voice_name = voice_name

            # Create synthesizer with in-memory audio output
            synthesizer = SpeechSynthesizer(speech_config=self.speech_config, audio_config=None)

            # Synthesize speech
            result = synthesizer.speak_text_async(text).get()

            if result.reason == result.Reason.SynthesizingAudioCompleted:
                audio_data = result.audio_data
                logger.info(f"Azure TTS successful: {len(audio_data)} bytes")
                return audio_data
            else:
                error_msg = f"TTS failed: {result.reason}"
                logger.error(error_msg)
                raise Exception(error_msg)

        except Exception as e:
            logger.error(f"Azure TTS failed: {e}")
            raise

    def speech_to_text_azure(self, audio_data: bytes, language: str = "en-US") -> str:
        """
        Convert speech to text using Azure Speech Services.

        Args:
            audio_data: Audio data in WAV format
            language: Language code for recognition

        Returns:
            str: Recognized text
        """
        if not self.speech_config:
            raise Exception("Azure Speech Services not configured")

        try:
            # Configure language
            self.speech_config.speech_recognition_language = language

            # Create recognizer
            recognizer = SpeechRecognizer(speech_config=self.speech_config, audio_config=None)

            # Note: In a real implementation, you'd need to provide audio data
            # This is a placeholder for the interface
            logger.warning("Azure STT requires audio stream implementation")
            return ""

        except Exception as e:
            logger.error(f"Azure STT failed: {e}")
            raise

    def get_available_voices(self) -> List[Dict[str, str]]:
        """
        Get list of available Azure TTS voices.

        Returns:
            list: List of voice dictionaries with name, gender, locale, etc.
        """
        # Azure TTS voices (subset - in production, fetch from API)
        voices = [
            {"name": "en-US-AriaRUS", "gender": "Female", "locale": "en-US"},
            {"name": "en-US-ZiraRUS", "gender": "Female", "locale": "en-US"},
            {"name": "en-US-BenjaminRUS", "gender": "Male", "locale": "en-US"},
            {"name": "en-GB-Susan-Apollo", "gender": "Female", "locale": "en-GB"},
            {"name": "en-GB-HazelRUS", "gender": "Female", "locale": "en-GB"},
            {"name": "en-GB-George-Apollo", "gender": "Male", "locale": "en-GB"},
        ]

        return voices

    def analyze_text_comprehensive(self, text: str) -> Dict[str, Any]:
        """
        Perform comprehensive text analysis using multiple Azure services.

        Args:
            text: Input text to analyze

        Returns:
            dict: Comprehensive analysis results
        """
        result = {
            'text': text,
            'language': None,
            'sentiment': None,
            'key_phrases': [],
            'intent': None,
            'entities': [],
            'timestamp': datetime.now().isoformat()
        }

        # Language detection
        if self.text_analytics_client:
            result['language'] = self.detect_language(text)

        # Sentiment analysis
        if self.text_analytics_client:
            result['sentiment'] = self.analyze_sentiment(text)

        # Key phrase extraction
        if self.text_analytics_client:
            result['key_phrases'] = self.extract_key_phrases(text)

        # Intent recognition
        if self.luis_client:
            intent_result = self.recognize_intent_luis(text)
            result['intent'] = intent_result.get('intent')
            result['intent_confidence'] = intent_result.get('confidence')
            result['entities'] = intent_result.get('entities', [])

        logger.info(f"Comprehensive text analysis completed for text: {text[:50]}...")
        return result

    def get_service_status(self) -> Dict[str, bool]:
        """
        Get status of all Azure Cognitive Services.

        Returns:
            dict: Status of each service
        """
        return {
            'luis': self.luis_client is not None,
            'text_analytics': self.text_analytics_client is not None,
            'speech_services': self.speech_config is not None,
            'overall_available': self.is_available()
        }
