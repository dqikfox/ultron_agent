"""
ULTRON Agent 3.0 - Google Cloud Integration
Provides Google Cloud Speech-to-Text and other cloud services
"""

import os
import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path

try:
    from google.cloud import speech_v1 as speech
    from google.cloud import texttospeech_v1 as tts
    from google.oauth2 import service_account
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False
    speech = None
    tts = None
    service_account = None

from utils.ultron_logger import ultron_logger


class GoogleCloudIntegration:
    """
    Google Cloud integration for speech-to-text, text-to-speech, and NLP services
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = ultron_logger
        self.speech_client = None
        self.tts_client = None
        self.is_initialized = False

        # Initialize if credentials are available
        if GOOGLE_CLOUD_AVAILABLE:
            self._initialize_clients()

    def _initialize_clients(self) -> bool:
        """Initialize Google Cloud clients with credentials"""
        try:
            # Get credentials from config or environment
            credentials_path = (
                self.config.get('google_cloud_credentials_path') or
                os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            )

            if not credentials_path:
                self.logger.warning(
                    "Google Cloud credentials not found. "
                    "Set GOOGLE_APPLICATION_CREDENTIALS or "
                    "google_cloud_credentials_path in config"
                )
                return False

            if not Path(credentials_path).exists():
                self.logger.error(
                    f"Google Cloud credentials file not found: {credentials_path}"
                )
                return False

            # Load credentials
            credentials = (
                service_account.Credentials.from_service_account_file(
                    credentials_path
                )
            )

            # Initialize clients
            self.speech_client = speech.SpeechClient(credentials=credentials)
            self.tts_client = tts.TextToSpeechClient(credentials=credentials)

            self.is_initialized = True
            self.logger.info("Google Cloud clients initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize Google Cloud clients: {e}")
            return False

    def is_available(self) -> bool:
        """Check if Google Cloud integration is available"""
        return GOOGLE_CLOUD_AVAILABLE and self.is_initialized

    async def speech_to_text(
        self,
        audio_data: bytes,
        language_code: str = "en-US",
        sample_rate: int = 16000
    ) -> Optional[str]:
        """
        Convert speech audio to text using Google Cloud Speech-to-Text

        Args:
            audio_data: Raw audio bytes
            language_code: Language code (e.g., 'en-US', 'es-ES')
            sample_rate: Audio sample rate in Hz

        Returns:
            Transcribed text or None if failed
        """
        if not self.is_available():
            self.logger.warning("Google Cloud Speech-to-Text not available")
            return None

        try:
            # Configure recognition
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=sample_rate,
                language_code=language_code,
                enable_automatic_punctuation=True,
                enable_word_time_offsets=False,
            )

            # Create audio object
            audio = speech.RecognitionAudio(content=audio_data)

            # Perform recognition
            self.logger.info(f"Starting speech recognition for {language_code}")
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                self.speech_client.recognize,
                config,
                audio
            )

            # Extract transcript
            if response.results:
                transcript = response.results[0].alternatives[0].transcript
                confidence = response.results[0].alternatives[0].confidence

                self.logger.info(
                    f"Speech recognition completed. "
                    f"Confidence: {confidence:.2f}"
                )
                return transcript
            else:
                self.logger.warning("No speech recognition results")
                return None

        except Exception as e:
            self.logger.error(f"Speech-to-text failed: {e}")
            return None

    async def speech_to_text_streaming(
        self,
        audio_stream,
        language_code: str = "en-US",
        sample_rate: int = 16000
    ):
        """
        Perform streaming speech recognition

        Args:
            audio_stream: Audio stream generator
            language_code: Language code
            sample_rate: Audio sample rate

        Yields:
            Recognition results as they become available
        """
        if not self.is_available():
            self.logger.warning("Google Cloud Speech-to-Text not available")
            return

        try:
            # Configure streaming recognition
            config = speech.StreamingRecognitionConfig(
                config=speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=sample_rate,
                    language_code=language_code,
                    enable_automatic_punctuation=True,
                ),
                interim_results=True,
            )

            # Create streaming requests
            def request_generator():
                yield speech.StreamingRecognizeRequest(streaming_config=config)
                for chunk in audio_stream:
                    yield speech.StreamingRecognizeRequest(audio_content=chunk)

            # Perform streaming recognition
            requests = request_generator()
            responses = self.speech_client.streaming_recognize(requests)

            for response in responses:
                if not response.results:
                    continue

                result = response.results[0]
                if not result.alternatives:
                    continue

                transcript = result.alternatives[0].transcript
                is_final = result.is_final

                yield {
                    "transcript": transcript,
                    "is_final": is_final,
                    "confidence": result.alternatives[0].confidence,
                    "stability": result.stability
                }

        except Exception as e:
            self.logger.error(f"Streaming speech-to-text failed: {e}")

    async def text_to_speech(
        self,
        text: str,
        language_code: str = "en-US",
        voice_name: str = "en-US-Neural2-D",
        speaking_rate: float = 1.0,
        pitch: float = 0.0
    ) -> Optional[bytes]:
        """
        Convert text to speech using Google Cloud Text-to-Speech

        Args:
            text: Text to synthesize
            language_code: Language code
            voice_name: Voice name (e.g., 'en-US-Neural2-D')
            speaking_rate: Speech rate (0.25-4.0)
            pitch: Voice pitch (-20.0 to 20.0)

        Returns:
            Audio data as bytes or None if failed
        """
        if not self.is_available():
            self.logger.warning("Google Cloud Text-to-Speech not available")
            return None

        try:
            # Configure synthesis input
            synthesis_input = tts.SynthesisInput(text=text)

            # Configure voice
            voice = tts.VoiceSelectionParams(
                language_code=language_code,
                name=voice_name,
            )

            # Configure audio
            audio_config = tts.AudioConfig(
                audio_encoding=tts.AudioEncoding.LINEAR16,
                speaking_rate=speaking_rate,
                pitch=pitch,
            )

            # Perform synthesis
            self.logger.info(f"Starting text-to-speech synthesis for '{text[:50]}...'")
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                self.tts_client.synthesize_speech,
                synthesis_input,
                voice,
                audio_config
            )

            self.logger.info("Text-to-speech synthesis completed")
            return response.audio_content

        except Exception as e:
            self.logger.error(f"Text-to-speech failed: {e}")
            return None

    def get_available_voices(
        self,
        language_code: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get list of available voices

        Args:
            language_code: Filter by language code

        Returns:
            List of voice information dictionaries
        """
        if not self.is_available():
            return []

        try:
            # Get voices
            response = self.tts_client.list_voices(language_code=language_code)

            voices = []
            for voice in response.voices:
                voices.append({
                    "name": voice.name,
                    "language_codes": voice.language_codes,
                    "ssml_gender": (
                        voice.ssml_gender.name if voice.ssml_gender else None
                    ),
                    "natural_sample_rate_hertz": voice.natural_sample_rate_hertz,
                })

            return voices

        except Exception as e:
            self.logger.error(f"Failed to get available voices: {e}")
            return []

    def get_supported_languages(self) -> List[str]:
        """Get list of supported language codes"""
        if not self.is_available():
            return []

        try:
            # Get voices to extract language codes
            response = self.tts_client.list_voices()
            languages = set()

            for voice in response.voices:
                languages.update(voice.language_codes)

            return sorted(list(languages))

        except Exception as e:
            self.logger.error(f"Failed to get supported languages: {e}")
            return []

    async def analyze_sentiment(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Analyze sentiment of text using Google Cloud Natural Language API

        Args:
            text: Text to analyze

        Returns:
            Sentiment analysis results or None if failed
        """
        try:
            from google.cloud import language_v1 as language

            # Initialize client if not already done
            if not hasattr(self, 'language_client'):
                credentials_path = (
                    self.config.get('google_cloud_credentials_path') or
                    os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
                )
                if credentials_path:
                    credentials = (
                        service_account.Credentials.from_service_account_file(
                            credentials_path
                        )
                    )
                    self.language_client = language.LanguageServiceClient(
                        credentials=credentials
                    )
                else:
                    return None

            # Analyze sentiment
            document = language.Document(
                content=text,
                type_=language.Document.Type.PLAIN_TEXT
            )

            response = await asyncio.get_event_loop().run_in_executor(
                None,
                self.language_client.analyze_sentiment,
                document
            )

            sentiment = response.document_sentiment

            return {
                "score": sentiment.score,
                "magnitude": sentiment.magnitude,
                "language": response.language,
            }

        except ImportError:
            self.logger.warning(
                "Google Cloud Natural Language API not available"
            )
            return None
        except Exception as e:
            self.logger.error(f"Sentiment analysis failed: {e}")
            return None

    async def detect_intent(
        self,
        text: str,
        project_id: str,
        session_id: str = "ultron-session"
    ) -> Optional[Dict[str, Any]]:
        """
        Detect intent using Google Cloud Dialogflow

        Args:
            text: User input text
            project_id: Google Cloud project ID
            session_id: Dialogflow session ID

        Returns:
            Intent detection results or None if failed
        """
        try:
            from google.cloud import dialogflow_v2 as dialogflow

            # Initialize client if not already done
            if not hasattr(self, 'dialogflow_client'):
                credentials_path = (
                    self.config.get('google_cloud_credentials_path') or
                    os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
                )
                if credentials_path:
                    credentials = (
                        service_account.Credentials.from_service_account_file(
                            credentials_path
                        )
                    )
                    self.dialogflow_client = dialogflow.SessionsClient(
                        credentials=credentials
                    )
                else:
                    return None

            # Create session path
            session_path = self.dialogflow_client.session_path(
                project_id, session_id
            )

            # Create text input
            text_input = dialogflow.TextInput(text=text, language_code="en-US")
            query_input = dialogflow.QueryInput(text=text_input)

            # Detect intent
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                self.dialogflow_client.detect_intent,
                session_path,
                query_input
            )

            intent = response.query_result.intent
            parameters = {}

            # Extract parameters
            for param_name, param_value in (
                response.query_result.parameters.items()
            ):
                if param_value:
                    parameters[param_name] = param_value

            return {
                "intent_name": intent.display_name if intent else None,
                "confidence": (
                    response.query_result.intent_detection_confidence
                ),
                "fulfillment_text": response.query_result.fulfillment_text,
                "parameters": parameters,
                "all_required_params_present": (
                    response.query_result.all_required_params_present
                ),
            }

        except ImportError:
            self.logger.warning("Google Cloud Dialogflow not available")
            return None
        except Exception as e:
            self.logger.error(f"Intent detection failed: {e}")
            return None

    def get_status(self) -> Dict[str, Any]:
        """Get integration status"""
        return {
            "available": self.is_available(),
            "google_cloud_sdk_available": GOOGLE_CLOUD_AVAILABLE,
            "speech_to_text_ready": self.speech_client is not None,
            "text_to_speech_ready": self.tts_client is not None,
            "credentials_configured": bool(
                self.config.get('google_cloud_credentials_path') or
                os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            ),
        }
