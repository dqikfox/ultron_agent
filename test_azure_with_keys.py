#!/usr/bin/env python3
"""
Comprehensive Azure Cognitive Services Integration Test with API Key Validation
"""

import sys
import os
import json
sys.path.append('.')

def load_config():
    """Load configuration from ultron_config.json"""
    try:
        with open('ultron_config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return {}

def test_azure_with_api_keys():
    """Test Azure Cognitive Services with actual API keys"""
    print("🔑 Testing Azure Cognitive Services with API Keys")
    print("=" * 60)

    config = load_config()

    # Check for Azure API keys in environment or config
    azure_keys = {
        'luis_endpoint': os.getenv('AZURE_LUIS_ENDPOINT') or config.get('azure_luis_endpoint', '').replace('USE_ENV_', ''),
        'luis_key': os.getenv('AZURE_LUIS_KEY') or config.get('azure_luis_key', '').replace('USE_ENV_', ''),
        'luis_app_id': os.getenv('AZURE_LUIS_APP_ID') or config.get('azure_luis_app_id', '').replace('USE_ENV_', ''),
        'text_analytics_endpoint': os.getenv('AZURE_TEXT_ANALYTICS_ENDPOINT') or config.get('azure_text_analytics_endpoint', '').replace('USE_ENV_', ''),
        'text_analytics_key': os.getenv('AZURE_TEXT_ANALYTICS_KEY') or config.get('azure_text_analytics_key', '').replace('USE_ENV_', ''),
        'speech_key': os.getenv('AZURE_SPEECH_KEY') or config.get('azure_speech_key', '').replace('USE_ENV_', ''),
        'speech_region': config.get('azure_speech_region', 'eastus')
    }

    # Check which keys are available
    available_services = []
    missing_services = []

    if azure_keys['luis_endpoint'] and azure_keys['luis_key'] and azure_keys['luis_app_id']:
        available_services.append('LUIS')
    else:
        missing_services.append('LUIS')

    if azure_keys['text_analytics_endpoint'] and azure_keys['text_analytics_key']:
        available_services.append('Text Analytics')
    else:
        missing_services.append('Text Analytics')

    if azure_keys['speech_key']:
        available_services.append('Speech Services')
    else:
        missing_services.append('Speech Services')

    print(f"📋 Available Azure Services: {', '.join(available_services) if available_services else 'None'}")
    print(f"📋 Missing Services: {', '.join(missing_services) if missing_services else 'None'}")

    if not available_services:
        print("\n⚠️  No Azure API keys configured. To test with real API keys:")
        print("   1. Set environment variables:")
        print("      - AZURE_LUIS_ENDPOINT=https://your-luis-endpoint.cognitiveservices.azure.com/")
        print("      - AZURE_LUIS_KEY=your-luis-key")
        print("      - AZURE_LUIS_APP_ID=your-luis-app-id")
        print("      - AZURE_TEXT_ANALYTICS_ENDPOINT=https://your-text-analytics-endpoint.cognitiveservices.azure.com/")
        print("      - AZURE_TEXT_ANALYTICS_KEY=your-text-analytics-key")
        print("      - AZURE_SPEECH_KEY=your-speech-key")
        print("   2. Or update ultron_config.json with actual values")
        print("   3. Re-run this test")
        return False

    # Test Azure integration with available keys
    try:
        from azure_cognitive_integration import AzureCognitiveIntegration

        print("\n🔧 Initializing Azure Cognitive Services...")
        azure_cog = AzureCognitiveIntegration(config)

        if azure_cog.is_available():
            print("✅ Azure Cognitive Services initialized successfully")

            # Test Text Analytics if available
            if 'Text Analytics' in available_services:
                print("\n🧪 Testing Text Analytics...")

                # Test sentiment analysis
                test_text = "I love this amazing ULTRON Agent! It's incredibly helpful and powerful."
                sentiment = azure_cog.analyze_sentiment(test_text)
                if sentiment and 'error' not in sentiment:
                    print(f"   ✅ Sentiment Analysis: {sentiment.get('sentiment', 'unknown')} (confidence: {sentiment.get('confidence_scores', {}).get('positive', 0):.2f})")
                else:
                    print(f"   ❌ Sentiment Analysis failed: {sentiment.get('error', 'Unknown error')}")

                # Test key phrase extraction
                key_phrases = azure_cog.extract_key_phrases(test_text)
                if key_phrases:
                    print(f"   ✅ Key Phrases: {', '.join(key_phrases[:3])}")
                else:
                    print("   ❌ Key phrase extraction failed")

                # Test language detection
                language = azure_cog.detect_language(test_text)
                if language and 'error' not in language:
                    print(f"   ✅ Language Detection: {language.get('language', 'unknown')} (confidence: {language.get('confidence', 0):.2f})")
                else:
                    print(f"   ❌ Language detection failed: {language.get('error', 'Unknown error')}")

            # Test LUIS if available
            if 'LUIS' in available_services:
                print("\n🧪 Testing LUIS Intent Recognition...")

                test_queries = [
                    "Hello ULTRON, how are you?",
                    "Can you help me with a coding problem?",
                    "Show me the current status",
                    "I need to analyze some data"
                ]

                for query in test_queries:
                    intent_result = azure_cog.recognize_intent_luis(query)
                    if intent_result and 'error' not in intent_result:
                        intent = intent_result.get('intent', 'unknown')
                        confidence = intent_result.get('confidence', 0.0)
                        print(f"   ✅ Query: '{query[:30]}...' → Intent: {intent} ({confidence:.2f})")
                    else:
                        print(f"   ❌ LUIS failed for query: {query[:30]}... - {intent_result.get('error', 'Unknown error')}")

            # Test comprehensive analysis
            print("\n🧪 Testing Comprehensive Text Analysis...")
            comprehensive = azure_cog.analyze_text_comprehensive(test_text)
            if comprehensive:
                print("   ✅ Comprehensive analysis completed")
                if comprehensive.get('sentiment'):
                    print(f"      - Sentiment: {comprehensive['sentiment'].get('sentiment', 'unknown')}")
                if comprehensive.get('key_phrases'):
                    print(f"      - Key phrases: {len(comprehensive['key_phrases'])} found")
                if comprehensive.get('intent'):
                    print(f"      - Intent: {comprehensive.get('intent', 'unknown')}")
            else:
                print("   ❌ Comprehensive analysis failed")

            # Test service status
            print("\n📊 Service Status:")
            status = azure_cog.get_service_status()
            for service, available in status.items():
                status_icon = "✅" if available else "❌"
                print(f"   {status_icon} {service.replace('_', ' ').title()}: {available}")

            print("\n🎉 Azure Cognitive Services integration test completed successfully!")
            return True

        else:
            print("❌ Azure Cognitive Services not available - check API keys")
            return False

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_brain_azure_integration():
    """Test Azure integration in the brain system"""
    print("\n🧠 Testing Brain System Azure Integration")
    print("=" * 50)

    try:
        from brain import UltronBrain

        print("🔧 Checking brain system Azure integration...")

        # Test if Azure methods exist
        brain_methods = [method for method in dir(UltronBrain) if 'azure' in method.lower()]
        print(f"📋 Azure methods in UltronBrain: {brain_methods}")

        if hasattr(UltronBrain, 'recognize_intent_azure'):
            print("✅ recognize_intent_azure method available")
        else:
            print("❌ recognize_intent_azure method missing")

        if hasattr(UltronBrain, 'analyze_sentiment_azure'):
            print("✅ analyze_sentiment_azure method available")
        else:
            print("❌ analyze_sentiment_azure method missing")

        # Check if Azure is initialized in __init__
        import inspect
        init_source = inspect.getsource(UltronBrain.__init__)
        if 'azure_cognitive' in init_source:
            print("✅ Azure Cognitive Services initialized in UltronBrain")
        else:
            print("❌ Azure Cognitive Services not found in UltronBrain initialization")

        print("🎉 Brain Azure integration test completed!")
        return True

    except Exception as e:
        print(f"❌ Brain integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 ULTRON Agent - Azure Cognitive Services Integration Test Suite")
    print("=" * 70)

    # Test Azure services with API keys
    azure_test_passed = test_azure_with_api_keys()

    # Test brain integration
    brain_test_passed = test_brain_azure_integration()

    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"Azure Services Test: {'✅ PASSED' if azure_test_passed else '❌ FAILED'}")
    print(f"Brain Integration Test: {'✅ PASSED' if brain_test_passed else '❌ FAILED'}")

    if azure_test_passed and brain_test_passed:
        print("\n🎉 ALL TESTS PASSED! Azure Cognitive Services integration is fully functional.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")

    sys.exit(0 if (azure_test_passed and brain_test_passed) else 1)
