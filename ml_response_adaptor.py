"""
ULTRON Agent 3.0 - Machine Learning Response Adaptor
Uses scikit-learn and TensorFlow for intelligent response adaptation
"""

import os
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

# Optional ML imports
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score
    from sklearn.pipeline import Pipeline
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

class MLResponseAdaptor:
    """
    Machine learning-based response adaptation system
    Learns from user interactions to improve response quality
    """

    def __init__(self, model_path: str = "models/response_adaptor"):
        self.model_path = model_path
        self.feedback_data = []
        self.response_classifier = None
        self.sentiment_model = None
        self._ensure_model_directory()
        self._load_models()

    def _ensure_model_directory(self):
        """Ensure the models directory exists"""
        os.makedirs(self.model_path, exist_ok=True)

    def _load_models(self):
        """Load or initialize ML models"""
        if not SKLEARN_AVAILABLE:
            print("scikit-learn not available - ML response adaptation disabled")
            return

        # Load response quality classifier
        classifier_path = os.path.join(self.model_path, "response_classifier.pkl")
        if os.path.exists(classifier_path):
            try:
                import joblib
                self.response_classifier = joblib.load(classifier_path)
                print("Loaded response quality classifier")
            except Exception as e:
                print(f"Failed to load response classifier: {e}")
                self._initialize_response_classifier()
        else:
            self._initialize_response_classifier()

        # Load sentiment analysis model (simple rule-based for now)
        self._initialize_sentiment_model()

    def _initialize_response_classifier(self):
        """Initialize the response quality classifier with basic training data"""
        if not SKLEARN_AVAILABLE:
            return

        # Basic training data for response quality
        training_data = [
            # High quality responses
            ("This is a comprehensive answer that addresses your question fully.", 1),
            ("I'll help you with that step by step.", 1),
            ("Based on your requirements, here's the solution.", 1),
            ("Let me explain this clearly for you.", 1),

            # Low quality responses
            ("I don't know.", 0),
            ("Sorry, I can't help.", 0),
            ("That's not possible.", 0),
            ("Error occurred.", 0),
        ]

        texts, labels = zip(*training_data)

        # Create pipeline
        self.response_classifier = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=1000, ngram_range=(1, 2))),
            ('clf', RandomForestClassifier(n_estimators=100, random_state=42))
        ])

        # Train the model
        self.response_classifier.fit(texts, labels)
        print("Initialized response quality classifier")

        # Save the model
        try:
            import joblib
            classifier_path = os.path.join(self.model_path, "response_classifier.pkl")
            joblib.dump(self.response_classifier, classifier_path)
        except Exception as e:
            print(f"Failed to save response classifier: {e}")

    def _initialize_sentiment_model(self):
        """Initialize sentiment analysis (rule-based for simplicity)"""
        # For now, use a simple rule-based approach
        # Could be enhanced with a trained model later
        self.sentiment_model = {
            'positive_words': ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'like', 'best', 'helpful', 'thanks', 'thank'],
            'negative_words': ['bad', 'terrible', 'awful', 'hate', 'worst', 'dislike', 'poor', 'fail', 'error', 'bug', 'wrong', 'incorrect']
        }

    def analyze_response_quality(self, response: str) -> Dict[str, Any]:
        """
        Analyze the quality of a response using ML

        Args:
            response: The response text to analyze

        Returns:
            Dictionary with quality metrics
        """
        if not self.response_classifier or not SKLEARN_AVAILABLE:
            return {"quality_score": 0.5, "confidence": 0.0, "error": "ML not available"}

        try:
            # Get prediction and probability
            prediction = self.response_classifier.predict([response])[0]
            probabilities = self.response_classifier.predict_proba([response])[0]

            # Quality score based on positive class probability
            quality_score = float(probabilities[1])  # Probability of being high quality

            return {
                "quality_score": quality_score,
                "prediction": "high_quality" if prediction == 1 else "low_quality",
                "confidence": float(max(probabilities)),
                "probabilities": {
                    "high_quality": float(probabilities[1]),
                    "low_quality": float(probabilities[0])
                }
            }

        except Exception as e:
            return {"quality_score": 0.5, "confidence": 0.0, "error": str(e)}

    def analyze_user_sentiment(self, user_input: str) -> Dict[str, Any]:
        """
        Analyze user sentiment from input text

        Args:
            user_input: User's message

        Returns:
            Sentiment analysis results
        """
        if not self.sentiment_model:
            return {"sentiment": "neutral", "confidence": 0.0}

        text_lower = user_input.lower()

        positive_count = sum(1 for word in self.sentiment_model['positive_words'] if word in text_lower)
        negative_count = sum(1 for word in self.sentiment_model['negative_words'] if word in text_lower)

        total_sentiment_words = positive_count + negative_count

        if total_sentiment_words == 0:
            return {"sentiment": "neutral", "confidence": 0.5, "scores": {"positive": 0, "negative": 0}}

        positive_score = positive_count / total_sentiment_words
        negative_score = negative_count / total_sentiment_words

        if positive_score > negative_score:
            sentiment = "positive"
            confidence = positive_score
        elif negative_score > positive_score:
            sentiment = "negative"
            confidence = negative_score
        else:
            sentiment = "neutral"
            confidence = 0.5

        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "scores": {
                "positive": positive_score,
                "negative": negative_score
            }
        }

    def adapt_response_based_on_feedback(self, original_response: str, user_feedback: Dict[str, Any]) -> str:
        """
        Adapt response based on user feedback and sentiment

        Args:
            original_response: The original AI response
            user_feedback: Feedback data including sentiment and quality metrics

        Returns:
            Adapted response
        """
        sentiment = user_feedback.get('sentiment', 'neutral')
        quality_score = user_feedback.get('quality_score', 0.5)

        adapted_response = original_response

        # Adapt based on sentiment
        if sentiment == "negative" and quality_score < 0.3:
            # User seems dissatisfied, add more helpful elements
            adapted_response = f"I understand you might be looking for a different approach. {original_response} Would you like me to try a different explanation or provide more details?"

        elif sentiment == "positive" and quality_score > 0.7:
            # User is satisfied, keep it positive
            adapted_response = f"{original_response} I'm glad I could help!"

        elif quality_score < 0.4:
            # Low quality response detected, add disclaimer
            adapted_response = f"{original_response} Please let me know if you'd like me to elaborate or try a different approach."

        return adapted_response

    def learn_from_interaction(self, user_input: str, ai_response: str, user_feedback: Optional[Dict[str, Any]] = None):
        """
        Learn from user interaction to improve future responses

        Args:
            user_input: What the user said
            ai_response: What the AI responded
            user_feedback: Optional explicit feedback
        """
        interaction_data = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "ai_response": ai_response,
            "sentiment_analysis": self.analyze_user_sentiment(user_input),
            "response_quality": self.analyze_response_quality(ai_response),
            "feedback": user_feedback or {}
        }

        self.feedback_data.append(interaction_data)

        # Save to file for future training
        self._save_feedback_data()

        # Retrain model if we have enough data
        if len(self.feedback_data) >= 10 and len(self.feedback_data) % 10 == 0:
            self._retrain_models()

    def _save_feedback_data(self):
        """Save feedback data to file"""
        feedback_path = os.path.join(self.model_path, "feedback_data.json")
        try:
            with open(feedback_path, 'w', encoding='utf-8') as f:
                json.dump(self.feedback_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save feedback data: {e}")

    def _retrain_models(self):
        """Retrain ML models with accumulated feedback data"""
        if not SKLEARN_AVAILABLE or len(self.feedback_data) < 5:
            return

        try:
            # Extract training data from feedback
            training_texts = []
            training_labels = []

            for interaction in self.feedback_data[-50:]:  # Use last 50 interactions
                response_quality = interaction.get('response_quality', {})
                quality_score = response_quality.get('quality_score', 0.5)

                # Label as high quality if score > 0.7, low quality if < 0.3
                if quality_score > 0.7:
                    training_texts.append(interaction['ai_response'])
                    training_labels.append(1)
                elif quality_score < 0.3:
                    training_texts.append(interaction['ai_response'])
                    training_labels.append(0)

            if len(training_texts) >= 5:
                # Retrain the classifier
                self.response_classifier.fit(training_texts, training_labels)

                # Save updated model
                import joblib
                classifier_path = os.path.join(self.model_path, "response_classifier.pkl")
                joblib.dump(self.response_classifier, classifier_path)

                print(f"Retrained response classifier with {len(training_texts)} samples")

        except Exception as e:
            print(f"Failed to retrain models: {e}")

    def get_adaptation_suggestions(self, user_input: str) -> List[str]:
        """
        Get suggestions for response adaptation based on user input analysis

        Args:
            user_input: The user's message

        Returns:
            List of adaptation suggestions
        """
        suggestions = []
        sentiment = self.analyze_user_sentiment(user_input)
        quality_analysis = self.analyze_response_quality(user_input)

        if sentiment['sentiment'] == 'negative':
            suggestions.append("User seems dissatisfied - consider offering alternatives")
            suggestions.append("Add more detailed explanations")

        if quality_analysis.get('quality_score', 0.5) < 0.4:
            suggestions.append("Response quality is low - consider rephrasing")
            suggestions.append("Add more context or examples")

        if len(user_input.split()) < 5:
            suggestions.append("User input is brief - keep response concise")

        return suggestions

    def get_model_stats(self) -> Dict[str, Any]:
        """Get statistics about the ML models"""
        return {
            "sklearn_available": SKLEARN_AVAILABLE,
            "tensorflow_available": TENSORFLOW_AVAILABLE,
            "response_classifier_loaded": self.response_classifier is not None,
            "feedback_data_points": len(self.feedback_data),
            "models_path": self.model_path,
            "capabilities": {
                "response_quality_analysis": SKLEARN_AVAILABLE,
                "sentiment_analysis": True,
                "response_adaptation": SKLEARN_AVAILABLE,
                "continuous_learning": SKLEARN_AVAILABLE
            }
        }
