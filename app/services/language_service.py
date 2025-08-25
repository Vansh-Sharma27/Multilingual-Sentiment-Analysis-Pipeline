"""
Language detection and translation service
Handles multilingual text processing using langdetect
"""

import logging
from typing import Optional, List, Dict, Tuple
from langdetect import detect, detect_langs, LangDetectException

logger = logging.getLogger(__name__)

class LanguageService:
    """Service for language detection and translation"""
    
    def __init__(self):
        """Initialize language service with models"""
        self.translation_pipeline = None
        self.supported_languages = [
            'en', 'es', 'fr', 'de', 'it', 'pt', 'nl', 'pl', 'ru', 
            'ja', 'ko', 'zh-cn', 'zh-tw', 'ar', 'hi', 'tr'
        ]
        self._initialize_models()
    
    def _initialize_models(self):
        """Lazy initialization of translation models"""
        try:
            # We'll use meta-llama model for translation as specified in the plan
            # For now, using a placeholder - actual implementation will use the specified model
            logger.info("Language service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize language models: {e}")
    
    def detect_language(self, text: str, confidence_threshold: float = 0.7) -> Tuple[str, float]:
        """
        Detect language of the given text
        
        Args:
            text: Input text to analyze
            confidence_threshold: Minimum confidence for detection
            
        Returns:
            Tuple of (language_code, confidence_score)
        """
        try:
            # Clean text for better detection
            cleaned_text = self._clean_text(text)
            
            if len(cleaned_text) < 10:
                return 'en', 0.5  # Default to English for very short texts
            
            # Get detection with confidence scores
            detections = detect_langs(cleaned_text)
            
            if detections:
                best_detection = detections[0]
                if best_detection.prob >= confidence_threshold:
                    return best_detection.lang, best_detection.prob
                else:
                    # Low confidence, try additional methods
                    return self._fallback_detection(cleaned_text)
            
            return 'en', 0.5  # Default fallback
            
        except LangDetectException as e:
            logger.warning(f"Language detection failed: {e}")
            return 'en', 0.5
        except Exception as e:
            logger.error(f"Unexpected error in language detection: {e}")
            return 'en', 0.0
    
    def _clean_text(self, text: str) -> str:
        """
        Clean text for better language detection
        
        Args:
            text: Raw input text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove URLs
        import re
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\\S+@\\S+', '', text)
        
        return text.strip()
    
    def _fallback_detection(self, text: str) -> Tuple[str, float]:
        """
        Fallback language detection method
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (language_code, confidence_score)
        """
        # Simple heuristic-based detection as fallback
        # Check for common patterns in different languages
        
        # Check for CJK characters
        if any('\\u4e00' <= char <= '\\u9fff' for char in text):
            return 'zh-cn', 0.6
        if any('\\u3040' <= char <= '\\u309f' or '\\u30a0' <= char <= '\\u30ff' for char in text):
            return 'ja', 0.6
        if any('\\uac00' <= char <= '\\ud7af' for char in text):
            return 'ko', 0.6
        
        # Check for Arabic script
        if any('\\u0600' <= char <= '\\u06ff' for char in text):
            return 'ar', 0.6
        
        # Check for Cyrillic script
        if any('\\u0400' <= char <= '\\u04ff' for char in text):
            return 'ru', 0.6
        
        # Default to English
        return 'en', 0.5
    
    def translate_to_english(self, text: str, source_lang: str) -> str:
        """
        Translate text to English if needed
        
        Args:
            text: Input text to translate
            source_lang: Source language code
            
        Returns:
            Translated text or original if already English
        """
        if source_lang == 'en':
            return text
        
        try:
            # Check if translation is needed and supported
            if source_lang not in self.supported_languages:
                logger.warning(f"Unsupported language for translation: {source_lang}")
                return text
            
            # For now, return original text - actual implementation will use the model
            # In production, this would use the meta-llama model as specified
            logger.info(f"Translation from {source_lang} to English (placeholder)")
            return text
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text
    
    def batch_detect_languages(self, texts: List[str]) -> List[Tuple[str, float]]:
        """
        Detect languages for multiple texts
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of (language_code, confidence) tuples
        """
        results = []
        for text in texts:
            lang, conf = self.detect_language(text)
            results.append((lang, conf))
        return results
    
    def get_language_statistics(self, texts: List[str]) -> Dict[str, int]:
        """
        Get language distribution statistics
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            Dictionary with language counts
        """
        language_counts = {}
        
        for text in texts:
            lang, _ = self.detect_language(text)
            language_counts[lang] = language_counts.get(lang, 0) + 1
        
        return language_counts
