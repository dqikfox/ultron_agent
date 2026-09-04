"""
ULTRON Agent - Advanced NLP Module with spaCy Integration

This module provides enhanced natural language processing capabilities
using spaCy for improved text understanding, entity recognition,
and sentiment analysis.
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import json
from datetime import datetime

# ULTRON Agent imports
from utils.ultron_logger import log_info, log_error, log_ai_decision

try:
    import spacy
    from spacy.lang.en import English
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    log_error("nlp_enhancer", "spaCy not available. Install with: pip install spacy")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.pipeline import Pipeline
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    log_error("nlp_enhancer", "scikit-learn not available. Install with: pip install scikit-learn")


class EnhancedNLPProcessor:
    """
    Enhanced NLP processor using spaCy for advanced text analysis
    """

    def __init__(self, config: Optional[Dict] = None):
        """Initialize the enhanced NLP processor"""
        self.config = config or {}
        self.nlp = None
        self.sentiment_model = None
        self.intent_classifier = None

        # Model paths
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)

        # Initialize spaCy if available
        if SPACY_AVAILABLE:
            self._initialize_spacy()
        else:
            log_error("nlp_enhancer", "spaCy not available - limited functionality")

        # Initialize ML models if available
        if SKLEARN_AVAILABLE:
            self._initialize_ml_models()

        log_info("nlp_enhancer", "Enhanced NLP processor initialized")

    def _initialize_spacy(self):
        """Initialize spaCy model"""
        try:
            # Try to load English model
            self.nlp = spacy.load("en_core_web_sm")
            log_info("nlp_enhancer", "spaCy English model loaded successfully")
        except OSError:
            # Fallback to basic English tokenizer
            log_info("nlp_enhancer", "spaCy model not found, using basic tokenizer")
            self.nlp = English()

    def _initialize_ml_models(self):
        """Initialize machine learning models for intent classification and sentiment"""
        try:
            # Simple intent classification pipeline
            self.intent_classifier = Pipeline([
                ('tfidf', TfidfVectorizer(max_features=1000, ngram_range=(1, 2))),
                ('clf', MultinomialNB())
            ])

            # Initialize with basic training data
            self._train_basic_models()

            log_info("nlp_enhancer", "ML models initialized successfully")
        except Exception as e:
            log_error("nlp_enhancer", f"Failed to initialize ML models: {e}")

    def _train_basic_models(self):
        """Train basic models with sample data"""
        # Sample training data for intent classification
        sample_texts = [
            "hello", "hi there", "good morning", "hey",
            "what time is it", "tell me the time", "what's the current time",
            "play music", "start playing music", "play some songs",
            "stop", "quit", "exit", "shutdown",
            "help me", "what can you do", "show commands",
            "weather", "how's the weather", "is it raining",
            "remind me", "set a reminder", "create reminder"
        ]

        sample_labels = [
            "greeting", "greeting", "greeting", "greeting",
            "time", "time", "time",
            "music", "music", "music",
            "stop", "stop", "stop", "stop",
            "help", "help", "help",
            "weather", "weather", "weather",
            "reminder", "reminder", "reminder"
        ]

        try:
            self.intent_classifier.fit(sample_texts, sample_labels)
            log_info("nlp_enhancer", "Basic intent classifier trained")
        except Exception as e:
            log_error("nlp_enhancer", f"Failed to train intent classifier: {e}")
            self.intent_classifier = None

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Perform comprehensive text analysis

        Args:
            text: Input text to analyze

        Returns:
            Dictionary containing analysis results
        """
        if not text or not text.strip():
            return {"error": "Empty text provided"}

        try:
            analysis = {
                "original_text": text,
                "timestamp": datetime.now().isoformat(),
                "entities": [],
                "sentiment": "neutral",
                "intent": "unknown",
                "confidence": 0.0,
                "tokens": [],
                "lemmas": [],
                "pos_tags": []
            }

            if self.nlp:
                # Process with spaCy
                doc = self.nlp(text)

                # Extract entities
                analysis["entities"] = [
                    {
                        "text": ent.text,
                        "label": ent.label_,
                        "start": ent.start_char,
                        "end": ent.end_char
                    }
                    for ent in doc.ents
                ]

                # Extract tokens, lemmas, and POS tags
                analysis["tokens"] = [token.text for token in doc]
                analysis["lemmas"] = [token.lemma_ for token in doc]
                analysis["pos_tags"] = [token.pos_ for token in doc]

                # Basic sentiment analysis (simplified)
                analysis["sentiment"] = self._analyze_sentiment(doc)

            # Intent classification
            if self.intent_classifier:
                try:
                    intent_pred = self.intent_classifier.predict([text])[0]
                    intent_proba = self.intent_classifier.predict_proba([text])[0]
                    max_prob = max(intent_proba)

                    analysis["intent"] = intent_pred
                    analysis["confidence"] = float(max_prob)
                except Exception as e:
                    log_error("nlp_enhancer", f"Intent classification failed: {e}")

            # Log AI decision for memory integration
            log_ai_decision("nlp_enhancer", f"Analyzed text: {text[:50]}...", "spacy_enhanced", confidence_score=analysis.get("confidence", 0.5))

            return analysis

        except Exception as e:
            error_msg = f"Text analysis failed: {str(e)}"
            log_error("nlp_enhancer", error_msg)
            return {"error": error_msg}

    def _analyze_sentiment(self, doc) -> str:
        """Basic sentiment analysis using spaCy"""
        try:
            # Simple rule-based sentiment analysis
            positive_words = ["good", "great", "excellent", "amazing", "wonderful", "fantastic", "love", "like", "happy", "awesome"]
            negative_words = ["bad", "terrible", "awful", "hate", "dislike", "sad", "horrible", "worst", "angry", "frustrated"]

            text_lower = doc.text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)

            if positive_count > negative_count:
                return "positive"
            elif negative_count > positive_count:
                return "negative"
            else:
                return "neutral"

        except Exception as e:
            log_error("nlp_enhancer", f"Sentiment analysis failed: {e}")
            return "neutral"

    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """
        Extract important keywords from text

        Args:
            text: Input text
            max_keywords: Maximum number of keywords to return

        Returns:
            List of extracted keywords
        """
        try:
            if not self.nlp:
                # Fallback to simple keyword extraction
                words = text.lower().split()
                # Remove common stop words
                stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were"}
                keywords = [word for word in words if word not in stop_words and len(word) > 3]
                return list(set(keywords))[:max_keywords]

            doc = self.nlp(text)

            # Extract nouns, proper nouns, and adjectives as keywords
            keywords = []
            for token in doc:
                if token.pos_ in ["NOUN", "PROPN", "ADJ"] and not token.is_stop and len(token.text) > 3:
                    keywords.append(token.lemma_.lower())

            # Remove duplicates and sort by frequency
            from collections import Counter
            keyword_freq = Counter(keywords)
            sorted_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)

            return [keyword for keyword, _ in sorted_keywords[:max_keywords]]

        except Exception as e:
            log_error("nlp_enhancer", f"Keyword extraction failed: {e}")
            return []

    def enhance_query_understanding(self, query: str) -> Dict[str, Any]:
        """
        Enhanced query understanding with multiple analysis layers

        Args:
            query: User query to analyze

        Returns:
            Enhanced understanding dictionary
        """
        try:
            # Basic text analysis
            analysis = self.analyze_text(query)

            # Extract additional insights
            enhanced = {
                "query": query,
                "analysis": analysis,
                "keywords": self.extract_keywords(query),
                "query_type": self._classify_query_type(query),
                "suggested_actions": self._suggest_actions(analysis),
                "confidence_score": analysis.get("confidence", 0.0)
            }

            log_ai_decision("nlp_enhancer", f"Enhanced query understanding for: {query[:50]}...", "enhanced_nlp", confidence_score=enhanced["confidence_score"])

            return enhanced

        except Exception as e:
            log_error("nlp_enhancer", f"Query enhancement failed: {e}")
            return {"error": str(e)}

    def _classify_query_type(self, query: str) -> str:
        """Classify the type of query"""
        query_lower = query.lower()

        if any(word in query_lower for word in ["what", "how", "when", "where", "why", "who"]):
            return "question"
        elif any(word in query_lower for word in ["do", "make", "create", "build", "run", "start"]):
            return "command"
        elif any(word in query_lower for word in ["tell", "say", "speak", "play"]):
            return "instruction"
        else:
            return "statement"

    def _suggest_actions(self, analysis: Dict) -> List[str]:
        """Suggest appropriate actions based on analysis"""
        suggestions = []

        intent = analysis.get("intent", "unknown")
        entities = analysis.get("entities", [])
        sentiment = analysis.get("sentiment", "neutral")

        # Intent-based suggestions
        if intent == "greeting":
            suggestions.append("Respond with a friendly greeting")
        elif intent == "time":
            suggestions.append("Provide current time information")
        elif intent == "music":
            suggestions.append("Control music playback")
        elif intent == "help":
            suggestions.append("Display available commands and capabilities")
        elif intent == "weather":
            suggestions.append("Check weather conditions")
        elif intent == "reminder":
            suggestions.append("Create or manage reminders")

        # Entity-based suggestions
        for entity in entities:
            if entity["label"] == "PERSON":
                suggestions.append(f"Handle query about person: {entity['text']}")
            elif entity["label"] == "ORG":
                suggestions.append(f"Handle query about organization: {entity['text']}")
            elif entity["label"] == "GPE":
                suggestions.append(f"Handle query about location: {entity['text']}")

        # Sentiment-based suggestions
        if sentiment == "negative":
            suggestions.append("Address user concern or frustration")
        elif sentiment == "positive":
            suggestions.append("Acknowledge positive sentiment")

        return suggestions

    def get_nlp_stats(self) -> Dict[str, Any]:
        """Get statistics about NLP processing"""
        return {
            "spacy_available": SPACY_AVAILABLE,
            "sklearn_available": SKLEARN_AVAILABLE,
            "model_loaded": self.nlp is not None,
            "intent_classifier_trained": self.intent_classifier is not None,
            "capabilities": [
                "named_entity_recognition" if SPACY_AVAILABLE else None,
                "sentiment_analysis",
                "intent_classification" if SKLEARN_AVAILABLE else None,
                "keyword_extraction",
                "query_enhancement"
            ]
        }


# Global instance for easy access
_enhanced_nlp_processor = None

def get_enhanced_nlp_processor(config: Optional[Dict] = None) -> EnhancedNLPProcessor:
    """Get or create the global enhanced NLP processor instance"""
    global _enhanced_nlp_processor
    if _enhanced_nlp_processor is None:
        _enhanced_nlp_processor = EnhancedNLPProcessor(config)
    return _enhanced_nlp_processor
