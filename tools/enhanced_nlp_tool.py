"""
Enhanced NLP Tool for ULTRON Agent

Provides advanced natural language processing capabilities using spaCy
"""

import logging
import os
import re
from typing import Dict, Any, Optional, List
from pathlib import Path

# ULTRON Agent imports
from utils.ultron_logger import log_info, log_error, log_ai_decision

try:
    import spacy
    from spacy.lang.en import English
    SPACY_AVAILABLE = True
except ImportError as e:
    SPACY_AVAILABLE = False
    spacy = None
    English = None
    log_error("enhanced_nlp", f"spaCy not available: {e}")
except Exception as e:
    SPACY_AVAILABLE = False
    spacy = None
    English = None
    log_error("enhanced_nlp", f"spaCy import failed with unexpected error: {e}")


class EnhancedNLPTool:
    """
    Tool for advanced natural language processing using spaCy
    """

    name = "Enhanced NLP Tool"
    description = "Advanced natural language processing with entity recognition, sentiment analysis, and text understanding"

    def __init__(self):
        self.nlp = None
        self.sentiment_analyzer = None
        self._initialize_nlp()

    def _initialize_nlp(self):
        """Initialize spaCy NLP pipeline"""
        if not SPACY_AVAILABLE:
            log_error("enhanced_nlp", "spaCy not available for NLP processing")
            return

        try:
            # Try to load a large model first, fall back to smaller ones
            model_names = ['en_core_web_lg', 'en_core_web_md', 'en_core_web_sm']

            for model in model_names:
                try:
                    self.nlp = spacy.load(model)
                    log_info("enhanced_nlp", f"Loaded spaCy model: {model}")
                    break
                except OSError:
                    continue

            if not self.nlp:
                # Fallback to basic English tokenizer
                self.nlp = English()
                log_info("enhanced_nlp", "Using basic English tokenizer")

        except Exception as e:
            log_error("enhanced_nlp", f"NLP initialization failed: {e}")

    def match(self, command: str) -> bool:
        """Check if command matches NLP operations"""
        command_lower = command.lower()
        return any(keyword in command_lower for keyword in [
            "analyze text", "nlp analysis", "entity recognition", "sentiment analysis",
            "text processing", "language analysis", "extract entities", "text understanding"
        ])

    def execute(self, command: str) -> str:
        """Execute NLP operations"""
        try:
            command_lower = command.lower()

            if not self.nlp:
                return "NLP functionality not available. Please install spaCy: pip install spacy"

            if "analyze text" in command_lower or "nlp analysis" in command_lower:
                text = self._extract_text(command)
                if text:
                    return self.analyze_text(text)
                else:
                    return "Please provide text to analyze"
            elif "entity recognition" in command_lower or "extract entities" in command_lower:
                text = self._extract_text(command)
                if text:
                    return self.extract_entities(text)
                else:
                    return "Please provide text for entity extraction"
            elif "sentiment analysis" in command_lower:
                text = self._extract_text(command)
                if text:
                    return self.analyze_sentiment(text)
                else:
                    return "Please provide text for sentiment analysis"
            else:
                return self.get_help()

        except Exception as e:
            log_error("enhanced_nlp", f"NLP operation failed: {e}")
            return f"NLP operation failed: {str(e)}"

    def analyze_text(self, text: str) -> str:
        """Perform comprehensive text analysis"""
        try:
            log_info("enhanced_nlp", f"Analyzing text: {text[:50]}...")

            doc = self.nlp(text)

            analysis = {
                'word_count': len([token for token in doc if not token.is_punct]),
                'sentence_count': len(list(doc.sents)),
                'tokens': len(doc),
                'unique_words': len(set([token.lemma_.lower() for token in doc if token.is_alpha])),
                'parts_of_speech': {},
                'named_entities': len(doc.ents),
                'noun_chunks': len(list(doc.noun_chunks))
            }

            # Count parts of speech
            pos_counts = {}
            for token in doc:
                pos = token.pos_
                pos_counts[pos] = pos_counts.get(pos, 0) + 1
            analysis['parts_of_speech'] = pos_counts

            # Extract key phrases
            key_phrases = []
            for chunk in doc.noun_chunks:
                if len(chunk.text.split()) >= 2:  # Multi-word phrases
                    key_phrases.append(chunk.text)

            # Calculate readability metrics (simple approximation)
            avg_words_per_sentence = analysis['word_count'] / max(analysis['sentence_count'], 1)
            avg_syllables_per_word = sum(len(re.findall(r'[aeiouy]+', token.text.lower())) for token in doc if token.is_alpha) / max(analysis['word_count'], 1)

            result = f"""
📝 **Text Analysis Results**

**Basic Statistics:**
• Words: {analysis['word_count']}
• Sentences: {analysis['sentence_count']}
• Tokens: {analysis['tokens']}
• Unique Words: {analysis['unique_words']}
• Named Entities: {analysis['named_entities']}
• Noun Phrases: {analysis['noun_chunks']}

**Parts of Speech:**
{chr(10).join(f"• {pos}: {count}" for pos, count in pos_counts.items())}

**Readability Metrics:**
• Average Words/Sentence: {avg_words_per_sentence:.1f}
• Average Syllables/Word: {avg_syllables_per_word:.1f}

**Key Phrases (Top 10):**
{chr(10).join(f"• {phrase}" for phrase in key_phrases[:10])}
"""

            return result

        except Exception as e:
            log_error("enhanced_nlp", f"Text analysis failed: {e}")
            return f"Text analysis failed: {str(e)}"

    def extract_entities(self, text: str) -> str:
        """Extract named entities from text"""
        try:
            log_info("enhanced_nlp", f"Extracting entities from: {text[:50]}...")

            doc = self.nlp(text)

            entities = {}
            for ent in doc.ents:
                entity_type = ent.label_
                if entity_type not in entities:
                    entities[entity_type] = []
                entities[entity_type].append({
                    'text': ent.text,
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'confidence': getattr(ent, '_.confidence', 'N/A')
                })

            if not entities:
                return f"No named entities found in the text."

            result = f"""
🏷️ **Named Entity Recognition**

**Found {len(doc.ents)} entities:**

"""

            for entity_type, entity_list in entities.items():
                result += f"**{entity_type} ({len(entity_list)}):**\n"
                for entity in entity_list:
                    result += f"• \"{entity['text']}\" (positions {entity['start']}-{entity['end']})\n"
                result += "\n"

            # Entity type explanations
            result += """
**Entity Type Explanations:**
• PERSON - People names
• ORG - Organizations and companies
• GPE - Countries, cities, states
• LOC - Non-GPE locations
• MISC - Miscellaneous entities
• DATE - Dates and time expressions
• MONEY - Monetary values
• PERCENT - Percentage values
"""

            return result

        except Exception as e:
            log_error("enhanced_nlp", f"Entity extraction failed: {e}")
            return f"Entity extraction failed: {str(e)}"

    def analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of text (basic implementation)"""
        try:
            log_info("enhanced_nlp", f"Analyzing sentiment of: {text[:50]}...")

            doc = self.nlp(text)

            # Basic sentiment analysis using rule-based approach
            positive_words = {
                'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
                'awesome', 'brilliant', 'outstanding', 'superb', 'perfect', 'love',
                'like', 'enjoy', 'happy', 'pleased', 'satisfied', 'delighted'
            }

            negative_words = {
                'bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike', 'poor',
                'worst', 'disappointed', 'unhappy', 'sad', 'angry', 'frustrated',
                'annoyed', 'upset', 'displeased', 'regret'
            }

            # Count sentiment words
            positive_count = 0
            negative_count = 0

            for token in doc:
                lemma = token.lemma_.lower()
                if lemma in positive_words:
                    positive_count += 1
                elif lemma in negative_words:
                    negative_count += 1

            total_words = len([token for token in doc if token.is_alpha])
            sentiment_score = (positive_count - negative_count) / max(total_words, 1)

            # Determine overall sentiment
            if sentiment_score > 0.1:
                sentiment = "Positive"
                confidence = min(sentiment_score * 10, 1.0)
            elif sentiment_score < -0.1:
                sentiment = "Negative"
                confidence = min(abs(sentiment_score) * 10, 1.0)
            else:
                sentiment = "Neutral"
                confidence = 1.0 - abs(sentiment_score) * 5

            result = f"""
😊 **Sentiment Analysis**

**Overall Sentiment:** {sentiment}
**Confidence:** {confidence:.2f}
**Sentiment Score:** {sentiment_score:.3f}

**Word Counts:**
• Positive words: {positive_count}
• Negative words: {negative_count}
• Total words analyzed: {total_words}

**Analysis Notes:**
• This is a basic rule-based sentiment analysis
• For more accurate results, consider using specialized sentiment models
• The analysis considers word lemmas and common sentiment dictionaries
"""

            return result

        except Exception as e:
            log_error("enhanced_nlp", f"Sentiment analysis failed: {e}")
            return f"Sentiment analysis failed: {str(e)}"

    def _extract_text(self, command: str) -> Optional[str]:
        """Extract text from command"""
        # Look for quoted text
        import re
        quoted_match = re.search(r'["\']([^"\']+)["\']', command)
        if quoted_match:
            return quoted_match.group(1)

        # Look for text after keywords
        text_keywords = ['text', 'analyze', 'of', 'for']
        for keyword in text_keywords:
            if keyword in command.lower():
                parts = command.lower().split(keyword, 1)
                if len(parts) > 1:
                    text = parts[1].strip()
                    if text:
                        return text

        # Return the whole command if it's long enough
        if len(command) > 10:
            return command

        return None

    def get_help(self) -> str:
        """Get help information for the tool"""
        status = "✅ Available" if self.nlp else "❌ Not Available (install spaCy)"

        return f"""
🧠 **Enhanced NLP Tool** ({status})

**Capabilities:**
• Comprehensive text analysis and statistics
• Named entity recognition (PERSON, ORG, GPE, etc.)
• Basic sentiment analysis
• Part-of-speech tagging
• Noun phrase extraction
• Readability metrics

**Commands:**
• "analyze text 'Your text here'" - Comprehensive text analysis
• "extract entities 'Text with names and places'" - Named entity recognition
• "sentiment analysis 'I love this product'" - Sentiment analysis

**Requirements:**
• spaCy library: pip install spacy
• Language model: python -m spacy download en_core_web_sm

**Features:**
• Multiple analysis types in one tool
• Detailed linguistic insights
• Entity type explanations
• Confidence scoring where available
"""

    @classmethod
    def schema(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "NLP analysis command with text"
                    }
                },
                "required": ["command"]
            }
        }
