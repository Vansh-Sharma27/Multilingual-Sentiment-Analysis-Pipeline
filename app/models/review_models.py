"""
Data models for review and sentiment analysis
"""

from dataclasses import dataclass
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class SentimentLabel(Enum):
    """Sentiment classification labels"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

@dataclass
class Review:
    """Single review data model"""
    id: str
    text: str
    original_language: Optional[str] = None
    translated_text: Optional[str] = None
    sentiment: Optional[SentimentLabel] = None
    confidence_score: Optional[float] = None
    processed_at: Optional[datetime] = None
    metadata: Optional[Dict] = None

@dataclass
class ProcessingResult:
    """Processing result for a batch of reviews"""
    job_id: str
    total_reviews: int
    processed_reviews: int
    positive_count: int
    negative_count: int
    neutral_count: int
    languages_detected: List[str]
    processing_time: float
    gemini_insights: Optional[str] = None
    errors: Optional[List[str]] = None
    created_at: datetime = None
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'job_id': self.job_id,
            'total_reviews': self.total_reviews,
            'processed_reviews': self.processed_reviews,
            'sentiment_distribution': {
                'positive': self.positive_count,
                'negative': self.negative_count,
                'neutral': self.neutral_count
            },
            'languages_detected': self.languages_detected,
            'processing_time': self.processing_time,
            'gemini_insights': self.gemini_insights,
            'errors': self.errors,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

@dataclass
class TextChunk:
    """Text chunk for parallel processing"""
    chunk_id: int
    text: str
    start_index: int
    end_index: int
    language: Optional[str] = None
    
@dataclass
class AnalysisRequest:
    """Request model for sentiment analysis"""
    text: Optional[str] = None
    file_path: Optional[str] = None
    request_id: str = None
    options: Optional[Dict] = None
