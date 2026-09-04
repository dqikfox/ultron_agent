"""
ULTRON Agent 3.0 - Enhanced NLP Processor
Advanced Natural Language Processing using spaCy and scikit-learn
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter
import logging

# Optional imports with fallbacks
try:
    import spacy
    from spacy.lang.en import English
    SPACY_AVAILABLE = True
except ImportError:
    spacy = None
    English = None
    SPACY_AVAILABLE = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.pipeline import Pipeline
    from sklearn.model_selection import train_test_split
    SKLEARN_AVAILABLE = True
except ImportError:
    TfidfVectorizer = None
    MultinomialNB = None
    Pipeline = None
    train_test_split = None
    SKLEARN_AVAILABLE = False

class EnhancedNLPProcessor:
    """
    Advanced NLP processor using spaCy for text analysis and scikit-learn for ML tasks
    """

    def __init__(self):
        self.nlp = None
        self.intent_classifier = None
        self._initialize_spacy()
        self._initialize_intent_classifier()

    def _initialize_spacy(self):
        """Initialize spaCy model for text processing"""
        if not SPACY_AVAILABLE:
            print("spaCy not available - NLP features will be limited")
            return

        try:
            # Try to load the large English model first, fallback to small model
            try:
                self.nlp = spacy.load("en_core_web_lg")
                print("Loaded spaCy en_core_web_lg model")
            except OSError:
                try:
                    self.nlp = spacy.load("en_core_web_sm")
                    print("Loaded spaCy en_core_web_sm model")
                except OSError:
                    # Create basic English tokenizer as fallback
                    self.nlp = English()
                    print("Using basic English tokenizer")
        except Exception as e:
            print(f"Failed to initialize spaCy: {e}")
            self.nlp = None

    def _initialize_intent_classifier(self):
        """Initialize the intent classification pipeline"""
        if not SKLEARN_AVAILABLE or not self.nlp:
            print("scikit-learn or spaCy not available - intent classification disabled")
            return

        try:
            # Training data for basic intent classification
            training_data = [
                # Commands
                ("run the code", "command"),
                ("execute this script", "command"),
                ("start the server", "command"),
                ("install the package", "command"),
                ("create a new file", "command"),
                ("delete the file", "command"),
                ("analyze the code", "command"),
                ("fix the bug", "command"),

                # Questions
                ("how do I", "question"),
                ("what is", "question"),
                ("can you explain", "question"),
                ("tell me about", "question"),
                ("how to", "question"),
                ("what does", "question"),

                # Requests
                ("please help me", "request"),
                ("I need assistance", "request"),
                ("can you help", "request"),
                ("show me how", "request"),
                ("I want to", "request"),

                # Statements
                ("I think", "statement"),
                ("this is", "statement"),
                ("the code has", "statement"),
                ("it seems", "statement"),
            ]

            texts, labels = zip(*training_data)

            # Create pipeline
            self.intent_classifier = Pipeline([
                ('tfidf', TfidfVectorizer(max_features=1000, ngram_range=(1, 2))),
                ('clf', MultinomialNB())
            ])

            # Train the classifier
            self.intent_classifier.fit(texts, labels)
            print("Intent classifier trained successfully")

        except Exception as e:
            print(f"Failed to initialize intent classifier: {e}")
            self.intent_classifier = None

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Comprehensive text analysis using spaCy

        Args:
            text: Input text to analyze

        Returns:
            Dictionary containing analysis results
        """
        if not text or not isinstance(text, str):
            return {"error": "Invalid input text"}

        result = {
            "original_text": text,
            "entities": [],
            "keywords": [],
            "sentiment": "neutral",
            "intent_classification": {},
            "sentence_count": 0,
            "word_count": 0,
            "complexity_score": 0.0
        }

        if not self.nlp:
            return result

        try:
            # Process text with spaCy
            doc = self.nlp(text)

            # Named Entity Recognition
            result["entities"] = [
                {
                    "text": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char
                }
                for ent in doc.ents
            ]

            # Extract keywords (nouns, proper nouns, verbs)
            keywords = []
            for token in doc:
                if token.pos_ in ['NOUN', 'PROPN', 'VERB'] and not token.is_stop and len(token.text) > 2:
                    keywords.append(token.lemma_.lower())

            # Get most common keywords
            keyword_counts = Counter(keywords)
            result["keywords"] = [word for word, count in keyword_counts.most_common(10)]

            # Basic sentence analysis
            result["sentence_count"] = len(list(doc.sents))
            result["word_count"] = len([token for token in doc if not token.is_punct])

            # Calculate complexity score (average sentence length + vocabulary diversity)
            if result["sentence_count"] > 0:
                avg_sentence_length = result["word_count"] / result["sentence_count"]
                vocab_diversity = len(set(token.lemma_.lower() for token in doc if token.is_alpha)) / result["word_count"] if result["word_count"] > 0 else 0
                result["complexity_score"] = (avg_sentence_length * 0.6) + (vocab_diversity * 0.4)

            # Intent classification
            if self.intent_classifier:
                try:
                    predicted_intent = self.intent_classifier.predict([text])[0]
                    probabilities = self.intent_classifier.predict_proba([text])[0]
                    intent_classes = self.intent_classifier.classes_

                    result["intent_classification"] = {
                        "intent": predicted_intent,
                        "confidence": float(max(probabilities)),
                        "probabilities": {
                            intent: float(prob)
                            for intent, prob in zip(intent_classes, probabilities)
                        }
                    }
                except Exception as e:
                    result["intent_classification"] = {"error": str(e)}

            # Basic sentiment analysis (simplified)
            positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'like', 'best']
            negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'dislike', 'poor', 'fail', 'error', 'bug']

            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)

            if positive_count > negative_count:
                result["sentiment"] = "positive"
            elif negative_count > positive_count:
                result["sentiment"] = "negative"
            else:
                result["sentiment"] = "neutral"

        except Exception as e:
            result["error"] = f"Analysis failed: {str(e)}"

        return result

    def enhance_query_understanding(self, query: str) -> str:
        """
        Enhance query understanding by adding context and clarifying ambiguous terms

        Args:
            query: Original user query

        Returns:
            Enhanced query with additional context
        """
        if not query or not isinstance(query, str):
            return query

        analysis = self.analyze_text(query)

        # If analysis failed, return original query
        if "error" in analysis:
            return query

        enhanced_parts = [query]

        # Add context based on detected entities
        entities = analysis.get("entities", [])
        if entities:
            entity_context = []
            for entity in entities:
                if entity["label"] in ["PERSON", "ORG", "GPE", "PRODUCT"]:
                    entity_context.append(f"related to {entity['text']}")

            if entity_context:
                enhanced_parts.append(f"Context: {', '.join(entity_context)}")

        # Add intent clarification
        intent_info = analysis.get("intent_classification", {})
        if intent_info.get("confidence", 0) > 0.6:
            intent = intent_info.get("intent")
            if intent == "command":
                enhanced_parts.append("This appears to be a command/request for action")
            elif intent == "question":
                enhanced_parts.append("This appears to be a question seeking information")
            elif intent == "request":
                enhanced_parts.append("This appears to be a request for assistance")

        # Add keyword context for better understanding
        keywords = analysis.get("keywords", [])
        if len(keywords) > 3:
            enhanced_parts.append(f"Key topics: {', '.join(keywords[:5])}")

        # If the query is very short and simple, add clarification request
        if analysis.get("word_count", 0) < 5 and analysis.get("complexity_score", 1.0) < 2.0:
            enhanced_parts.append("Please provide more context or details if needed")

        # Join enhanced parts
        if len(enhanced_parts) > 1:
            enhanced_query = " | ".join(enhanced_parts)
            return enhanced_query

        return query

    def extract_actionable_items(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract actionable items from text (commands, requests, tasks)

        Args:
            text: Input text

        Returns:
            List of actionable items with metadata
        """
        if not text or not self.nlp:
            return []

        analysis = self.analyze_text(text)
        actionable_items = []

        # Look for imperative sentences (commands)
        doc = self.nlp(text)
        for sent in doc.sents:
            # Check if sentence starts with verb (imperative)
            first_token = sent[0]
            if first_token.pos_ == "VERB" and not first_token.is_punct:
                actionable_items.append({
                    "type": "command",
                    "text": sent.text.strip(),
                    "confidence": 0.8,
                    "keywords": analysis.get("keywords", [])[:3]
                })

        # Look for request patterns
        request_patterns = [
            r"please\s+(help|assist|show|tell|explain)",
            r"can\s+you\s+(help|assist|show|tell|explain)",
            r"I\s+(need|want)\s+(help|assistance)"
        ]

        for pattern in request_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                start, end = match.span()
                # Get surrounding context
                context_start = max(0, start - 50)
                context_end = min(len(text), end + 50)
                context = text[context_start:context_end]

                actionable_items.append({
                    "type": "request",
                    "text": context.strip(),
                    "confidence": 0.7,
                    "pattern": pattern
                })

        return actionable_items

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get statistics about the NLP processor"""
        return {
            "spacy_available": SPACY_AVAILABLE,
            "spacy_model": self.nlp.meta.get("name") if self.nlp and hasattr(self.nlp, 'meta') else None,
            "sklearn_available": SKLEARN_AVAILABLE,
            "intent_classifier_trained": self.intent_classifier is not None,
            "capabilities": {
                "named_entity_recognition": SPACY_AVAILABLE,
                "keyword_extraction": SPACY_AVAILABLE,
                "intent_classification": SKLEARN_AVAILABLE and self.intent_classifier is not None,
                "sentiment_analysis": True,  # Basic implementation
                "query_enhancement": SPACY_AVAILABLE,
                "actionable_item_extraction": SPACY_AVAILABLE
            }
        }
