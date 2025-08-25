"""
Sentiment Analysis Service using Ollama API
Uses GPT OSS-12B model for advanced sentiment analysis
"""

import logging
import os
from typing import List, Dict, Tuple, Optional
from app.models.review_models import SentimentLabel, Review, TextChunk
from app.services.ollama_service import OllamaService
import time

logger = logging.getLogger(__name__)

class SentimentService:
    """Sentiment analysis service using Ollama API with GPT OSS-12B model"""

    def __init__(self):
        """Initialize sentiment analysis service with Ollama configuration."""
        self.ollama_service = OllamaService()
        logger.info("Sentiment Service initialized with Ollama GPT OSS-12B model")

    def analyze_sentiment(self, text: str) -> Tuple[SentimentLabel, float]:
        """Analyze sentiment using Ollama GPT OSS-12B model."""
        cleaned_text = self._preprocess_text(text)
        if not cleaned_text:
            return SentimentLabel.NEUTRAL, 0.0

        logger.info(f"Analyzing sentiment for text: {cleaned_text[:50]}...")
        
        # Get sentiment from Ollama API
        result = self.ollama_service.analyze_sentiment(cleaned_text)
        logger.info(f"Ollama API result: {result}")
        
        return result



    def analyze_batch(self, texts: List[str]) -> List[Tuple[SentimentLabel, float]]:
        """Analyze sentiment for multiple texts."""
        results = []
        for text in texts:
            result = self.analyze_sentiment(text)
            results.append(result)
            # Small delay to avoid rate limiting
            time.sleep(0.1)
        return results

    def analyze_review(self, review: Review) -> Review:
        """Analyze sentiment for a review and its chunks."""
        # Analyze overall sentiment
        overall_sentiment, overall_confidence = self.analyze_sentiment(review.original_text)
        review.overall_sentiment = overall_sentiment
        review.overall_confidence = overall_confidence

        # Analyze chunks if present
        if review.chunks:
            for chunk in review.chunks:
                chunk_sentiment, chunk_confidence = self.analyze_sentiment(chunk.text)
                chunk.sentiment = chunk_sentiment
                chunk.confidence = chunk_confidence

        return review



    def _preprocess_text(self, text: str) -> str:
        """Clean and prepare text for sentiment analysis."""
        if not text:
            return ""
        
        # Basic cleaning
        text = text.strip()
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Truncate if too long (Llama has token limits)
        max_length = 500  # Reasonable length for sentiment analysis
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        return text

    def get_stats(self) -> Dict:
        """Get service statistics"""
        ollama_stats = self.ollama_service.get_service_stats()
        return {
            "service": "Sentiment Analysis",
            "provider": "Ollama",
            "model": ollama_stats.get("model", "gpt-oss:120b"),
            "status": ollama_stats.get("status", "unknown")
        }
    
    def get_sentiment_statistics(self, sentiments: List[Tuple]) -> Dict:
        """Calculate statistics from sentiment results"""
        positive_count = sum(1 for s, _ in sentiments if s.value == 'positive')
        negative_count = sum(1 for s, _ in sentiments if s.value == 'negative')
        neutral_count = sum(1 for s, _ in sentiments if s.value == 'neutral')
        
        return {
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'total': len(sentiments)
        }
    
    def parallel_analyze(self, chunks: List) -> List[Tuple]:
        """Analyze multiple text chunks using batch processing for better performance"""
        if not chunks:
            return []
        
        # Extract texts from chunks
        texts = [chunk.text for chunk in chunks]
        
        # Use batch sentiment analysis from Ollama service
        try:
            results = self.ollama_service.batch_analyze_sentiment(texts)
            logger.info(f"Batch processed {len(texts)} texts successfully")
            return results
        except Exception as e:
            logger.warning(f"Batch processing failed: {e}, falling back to sequential")
            # Fallback to sequential processing
            results = []
            for chunk in chunks:
                sentiment, confidence = self.analyze_sentiment(chunk.text)
                results.append((sentiment, confidence))
            return results
    
    def batch_analyze(self, texts: List[str]) -> List[Tuple]:
        """Analyze sentiment for multiple texts using batch processing"""
        return self.ollama_service.batch_analyze_sentiment(texts)
