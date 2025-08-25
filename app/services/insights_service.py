"""
Ollama API integration service for insights generation
Generates intelligent insights and summaries using GPT OSS-12B model
"""

import logging
import os
from typing import Dict, List, Optional
from app.models.review_models import ProcessingResult, SentimentLabel
from app.services.ollama_service import OllamaService
import json

logger = logging.getLogger(__name__)

class InsightsService:
    """Service for insights generation using Ollama GPT OSS-12B model"""
    
    def __init__(self):
        """Initialize insights service with Ollama configuration"""
        self.ollama_service = OllamaService()
        logger.info("Insights service initialized with Ollama GPT OSS-12B model")
    
    def generate_insights(self, processing_result: ProcessingResult) -> str:
        """
        Generate insights from sentiment analysis results using Ollama GPT OSS-12B
        
        Args:
            processing_result: Processing result with sentiment statistics
            
        Returns:
            Generated insights text
        """
        try:
            # Use Ollama service to generate insights
            insights = self.ollama_service.generate_insights(processing_result)
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate insights: {e}")
            return self._generate_fallback_insights(processing_result)
    

    
    def _generate_mock_insights(self, result: ProcessingResult) -> str:
        """
        Generate mock insights for testing without API
        
        Args:
            result: Processing result data
            
        Returns:
            Mock insights text
        """
        total = result.total_reviews
        positive_pct = (result.positive_count / total * 100) if total > 0 else 0
        negative_pct = (result.negative_count / total * 100) if total > 0 else 0
        neutral_pct = (result.neutral_count / total * 100) if total > 0 else 0
        
        # Determine insights based on data
        sentiment_health = "excellent" if positive_pct > 70 else "good" if positive_pct > 50 else "concerning" if negative_pct > 40 else "mixed"
        
        insights = f"""
        • **Sentiment Health Assessment**: {sentiment_health.title()} overall sentiment with {positive_pct:.1f}% positive feedback indicating {'strong' if positive_pct > 60 else 'moderate' if positive_pct > 40 else 'weak'} customer satisfaction levels
        
        • **Customer Satisfaction Trends**: The {positive_pct:.1f}%/{negative_pct:.1f}%/{neutral_pct:.1f}% distribution suggests {'stable customer loyalty' if positive_pct > negative_pct * 2 else 'mixed customer experiences requiring attention'}
        
        • **Risk/Opportunity Identification**: {'High retention opportunity' if positive_pct > 60 else 'Customer satisfaction improvement needed' if negative_pct > 30 else 'Balanced feedback requiring strategic focus'}
        
        • **Multilingual Market Insights**: Analysis across {len(result.languages_detected)} languages ({', '.join(result.languages_detected[:3])}{f' and {len(result.languages_detected)-3} more' if len(result.languages_detected) > 3 else ''}) reveals {'consistent global satisfaction' if len(result.languages_detected) > 3 else 'regional feedback patterns'}
        
        • **Actionable Recommendations**: {'Focus on scaling positive experiences and addressing negative feedback systematically' if positive_pct > negative_pct else 'Implement immediate customer satisfaction improvement initiatives'}
        
        • **Benchmarking Context**: Current sentiment distribution {'exceeds industry standards' if positive_pct > 60 else 'aligns with industry averages' if positive_pct > 40 else 'requires improvement to meet industry benchmarks'} for customer feedback analysis
        """
        
        return insights.strip()
    
    def _generate_fallback_insights(self, result: ProcessingResult) -> str:
        """
        Generate basic fallback insights on error
        
        Args:
            result: Processing result data
            
        Returns:
            Basic insights text
        """
        return f"""
        Sentiment Analysis Summary:
        - Total reviews: {result.total_reviews}
        - Positive: {result.positive_count}
        - Negative: {result.negative_count}
        - Neutral: {result.neutral_count}
        - Languages: {', '.join(result.languages_detected)}
        """
    
    def summarize_reviews(self, reviews: List[str], max_reviews: int = 10) -> str:
        """
        Generate summary of review texts using Ollama service
        
        Args:
            reviews: List of review texts
            max_reviews: Maximum number of reviews to summarize
            
        Returns:
            Summary text
        """
        try:
            # Limit reviews for API efficiency
            sample_reviews = reviews[:max_reviews]
            
            # Use Ollama service for summarization
            summary = self.ollama_service.summarize_reviews(sample_reviews)
            return summary
            
        except Exception as e:
            logger.error(f"Failed to summarize reviews: {e}")
            return "Unable to generate review summary at this time."
    
    def generate_improvement_suggestions(self, negative_reviews: List[str]) -> List[str]:
        """
        Generate improvement suggestions based on negative feedback using Ollama service
        
        Args:
            negative_reviews: List of negative review texts
            
        Returns:
            List of improvement suggestions
        """
        try:
            if not negative_reviews:
                return ["No negative feedback to analyze"]
            
            # Use Ollama service for improvement suggestions
            suggestions = self.ollama_service.generate_improvement_suggestions(negative_reviews)
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to generate improvement suggestions: {e}")
            return [
                "Address customer service response times",
                "Improve product quality control", 
                "Enhance user experience and interface",
                "Provide better documentation and support"
            ]
    
    def analyze_language_patterns(self, language_stats: Dict[str, int]) -> Dict:
        """
        Analyze patterns in multilingual data
        
        Args:
            language_stats: Dictionary of language counts
            
        Returns:
            Analysis results
        """
        try:
            total_reviews = sum(language_stats.values())
            
            analysis = {
                'dominant_language': max(language_stats, key=language_stats.get) if language_stats else 'unknown',
                'language_diversity': len(language_stats),
                'distribution': {
                    lang: {
                        'count': count,
                        'percentage': (count / total_reviews * 100) if total_reviews > 0 else 0
                    }
                    for lang, count in language_stats.items()
                }
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze language patterns: {e}")
            return {'error': 'Analysis failed'}
