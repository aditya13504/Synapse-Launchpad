import spacy
import asyncio
from typing import Dict, List, Any
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import logging
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re

logger = logging.getLogger(__name__)

class NLPProcessor:
    """
    NLP processing pipeline using spaCy and Transformers
    """
    
    def __init__(self):
        self.setup_models()
    
    def setup_models(self):
        """Initialize NLP models"""
        try:
            # Load spaCy model
            self.nlp = spacy.load("en_core_web_sm")
            
            # Initialize sentiment analyzers
            self.vader_analyzer = SentimentIntensityAnalyzer()
            
            # Load transformer models for advanced analysis
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                return_all_scores=True
            )
            
            # Financial sentiment model
            self.financial_sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="ProsusAI/finbert",
                return_all_scores=True
            )
            
            logger.info("NLP models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load NLP models: {e}")
            # Fallback to basic models
            self.nlp = None
            self.sentiment_pipeline = None
            self.financial_sentiment_pipeline = None
    
    async def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract named entities and custom business entities from text
        """
        entities = {
            "companies": [],
            "people": [],
            "locations": [],
            "funding_amounts": [],
            "funding_rounds": [],
            "technologies": [],
            "industries": [],
            "dates": []
        }
        
        try:
            if self.nlp:
                # Process with spaCy
                doc = self.nlp(text)
                
                # Extract standard named entities
                for ent in doc.ents:
                    if ent.label_ == "ORG":
                        entities["companies"].append({
                            "text": ent.text,
                            "confidence": 1.0,
                            "start": ent.start_char,
                            "end": ent.end_char
                        })
                    elif ent.label_ == "PERSON":
                        entities["people"].append({
                            "text": ent.text,
                            "confidence": 1.0,
                            "start": ent.start_char,
                            "end": ent.end_char
                        })
                    elif ent.label_ in ["GPE", "LOC"]:
                        entities["locations"].append({
                            "text": ent.text,
                            "confidence": 1.0,
                            "start": ent.start_char,
                            "end": ent.end_char
                        })
                    elif ent.label_ == "DATE":
                        entities["dates"].append({
                            "text": ent.text,
                            "confidence": 1.0,
                            "start": ent.start_char,
                            "end": ent.end_char
                        })
            
            # Extract custom business entities
            await self._extract_funding_entities(text, entities)
            await self._extract_technology_entities(text, entities)
            await self._extract_industry_entities(text, entities)
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
        
        return entities
    
    async def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment using multiple models for robustness
        """
        sentiment_scores = {
            "compound": 0.0,
            "positive": 0.0,
            "negative": 0.0,
            "neutral": 0.0,
            "financial_positive": 0.0,
            "financial_negative": 0.0,
            "financial_neutral": 0.0,
            "confidence": 0.0
        }
        
        try:
            # VADER sentiment (good for social media text)
            vader_scores = self.vader_analyzer.polarity_scores(text)
            sentiment_scores.update({
                "compound": vader_scores["compound"],
                "positive": vader_scores["pos"],
                "negative": vader_scores["neg"],
                "neutral": vader_scores["neu"]
            })
            
            # Transformer-based sentiment
            if self.sentiment_pipeline:
                transformer_results = self.sentiment_pipeline(text[:512])  # Truncate for model limits
                for result in transformer_results[0]:
                    label = result["label"].lower()
                    if "positive" in label:
                        sentiment_scores["positive"] = max(sentiment_scores["positive"], result["score"])
                    elif "negative" in label:
                        sentiment_scores["negative"] = max(sentiment_scores["negative"], result["score"])
            
            # Financial sentiment (for business/funding content)
            if self.financial_sentiment_pipeline:
                financial_results = self.financial_sentiment_pipeline(text[:512])
                for result in financial_results[0]:
                    label = result["label"].lower()
                    if "positive" in label:
                        sentiment_scores["financial_positive"] = result["score"]
                    elif "negative" in label:
                        sentiment_scores["financial_negative"] = result["score"]
                    elif "neutral" in label:
                        sentiment_scores["financial_neutral"] = result["score"]
            
            # Calculate overall confidence
            sentiment_scores["confidence"] = self._calculate_sentiment_confidence(sentiment_scores)
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
        
        return sentiment_scores
    
    async def _extract_funding_entities(self, text: str, entities: Dict[str, Any]):
        """
        Extract funding-related entities using regex patterns
        """
        try:
            # Funding amount patterns
            amount_patterns = [
                r'\$(\d+(?:\.\d+)?)\s*([BMK]?)(?:illion)?',
                r'(\d+(?:\.\d+)?)\s*([BMK]?)(?:illion)?\s*dollars?',
                r'raised\s+\$?(\d+(?:\.\d+)?)\s*([BMK]?)(?:illion)?'
            ]
            
            for pattern in amount_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    amount = match.group(1)
                    unit = match.group(2).upper() if len(match.groups()) > 1 else ""
                    
                    # Convert to standard format
                    multiplier = {"K": 1000, "M": 1000000, "B": 1000000000}.get(unit, 1)
                    value = float(amount) * multiplier
                    
                    entities["funding_amounts"].append({
                        "text": match.group(0),
                        "amount": value,
                        "formatted": f"${amount}{unit}",
                        "start": match.start(),
                        "end": match.end()
                    })
            
            # Funding round patterns
            round_patterns = [
                r'(seed|series\s+[A-Z]|pre-seed|angel)\s+round',
                r'(IPO|acquisition|merger)',
                r'(venture|equity|debt)\s+financing'
            ]
            
            for pattern in round_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entities["funding_rounds"].append({
                        "text": match.group(0),
                        "type": match.group(1).lower(),
                        "start": match.start(),
                        "end": match.end()
                    })
                    
        except Exception as e:
            logger.error(f"Funding entity extraction failed: {e}")
    
    async def _extract_technology_entities(self, text: str, entities: Dict[str, Any]):
        """
        Extract technology-related entities
        """
        try:
            tech_keywords = [
                "AI", "artificial intelligence", "machine learning", "ML", "deep learning",
                "blockchain", "cryptocurrency", "fintech", "SaaS", "cloud computing",
                "IoT", "internet of things", "big data", "analytics", "automation",
                "robotics", "VR", "virtual reality", "AR", "augmented reality",
                "API", "platform", "mobile app", "web app", "software"
            ]
            
            for keyword in tech_keywords:
                pattern = rf'\b{re.escape(keyword)}\b'
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entities["technologies"].append({
                        "text": match.group(0),
                        "category": "technology",
                        "start": match.start(),
                        "end": match.end()
                    })
                    
        except Exception as e:
            logger.error(f"Technology entity extraction failed: {e}")
    
    async def _extract_industry_entities(self, text: str, entities: Dict[str, Any]):
        """
        Extract industry/vertical entities
        """
        try:
            industry_keywords = [
                "healthcare", "fintech", "edtech", "proptech", "insurtech",
                "e-commerce", "retail", "manufacturing", "logistics", "transportation",
                "energy", "renewable", "sustainability", "biotech", "pharma",
                "gaming", "entertainment", "media", "advertising", "marketing",
                "cybersecurity", "security", "enterprise", "B2B", "B2C"
            ]
            
            for keyword in industry_keywords:
                pattern = rf'\b{re.escape(keyword)}\b'
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entities["industries"].append({
                        "text": match.group(0),
                        "category": "industry",
                        "start": match.start(),
                        "end": match.end()
                    })
                    
        except Exception as e:
            logger.error(f"Industry entity extraction failed: {e}")
    
    def _calculate_sentiment_confidence(self, scores: Dict[str, float]) -> float:
        """
        Calculate overall confidence in sentiment analysis
        """
        try:
            # Use compound score magnitude as base confidence
            base_confidence = abs(scores.get("compound", 0))
            
            # Adjust based on agreement between models
            pos_agreement = abs(scores.get("positive", 0) - scores.get("financial_positive", 0))
            neg_agreement = abs(scores.get("negative", 0) - scores.get("financial_negative", 0))
            
            agreement_penalty = (pos_agreement + neg_agreement) / 2
            
            confidence = max(0.1, base_confidence - agreement_penalty)
            return min(1.0, confidence)
            
        except Exception as e:
            logger.error(f"Confidence calculation failed: {e}")
            return 0.5