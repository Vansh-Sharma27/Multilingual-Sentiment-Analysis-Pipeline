"""
Translation Service using Ollama API
Handles translation of multilingual texts to English using GPT OSS-12B model
"""

import logging
import os
from typing import Optional, List, Dict, Tuple
from app.services.language_service import LanguageService
from app.services.ollama_service import OllamaService
import time

logger = logging.getLogger(__name__)

class TranslationService:
    """Service for translating texts to English using Ollama GPT OSS-12B model"""
    
    def __init__(self):
        """Initialize translation service with Ollama API configuration"""
        self.ollama_service = OllamaService()
        self.enabled = True  # Ollama service handles availability internally
        
        # Initialize language service for detection
        self.language_service = LanguageService()
        
        # Cache for translations to avoid redundant API calls
        self.translation_cache = {}
        
        logger.info("Translation Service initialized with Ollama GPT OSS-12B model")
    
    def translate_to_english(self, text: str, source_lang: Optional[str] = None) -> Dict:
        """
        Translate text to English if needed using Ollama GPT OSS-12B
        
        Args:
            text: Text to translate
            source_lang: Source language code (optional, will detect if not provided)
            
        Returns:
            Dictionary with translation results
        """
        # Detect language if not provided
        if not source_lang:
            source_lang, confidence = self.language_service.detect_language(text)
            logger.info(f"Detected language: {source_lang} (confidence: {confidence:.2f})")
        
        # Skip translation if already English
        if source_lang in ['en', 'english']:
            return {
                "original_text": text,
                "translated_text": text,
                "source_language": source_lang,
                "was_translated": False
            }
        
        # Check cache
        cache_key = f"{source_lang}:{text[:100]}"  # Use first 100 chars as cache key
        if cache_key in self.translation_cache:
            logger.info("Using cached translation")
            return self.translation_cache[cache_key]
        
        # Perform translation using Ollama service
        try:
            result = self.ollama_service.translate_text(text, source_lang, 'en')
            
            # Cache the result if translation was successful
            if result.get('was_translated'):
                self.translation_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return {
                "original_text": text,
                "translated_text": text,
                "source_language": source_lang,
                "was_translated": False,
                "error": str(e)
            }
    

    
    def _clean_translation(self, text: str) -> str:
        """
        Clean up translated text
        
        Args:
            text: Raw translated text
            
        Returns:
            Cleaned translation
        """
        # Remove common artifacts from translation
        text = text.strip()
        
        # Remove quotes if the entire text is quoted
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        if text.startswith("'") and text.endswith("'"):
            text = text[1:-1]
        
        # Remove "Translation:" prefix if present
        if text.lower().startswith("translation:"):
            text = text[12:].strip()
        
        return text
    
    def batch_translate(self, texts: List[str], source_langs: Optional[List[str]] = None) -> List[Dict]:
        """
        Translate multiple texts
        
        Args:
            texts: List of texts to translate
            source_langs: Optional list of source language codes
            
        Returns:
            List of translation result dictionaries
        """
        results = []
        
        for i, text in enumerate(texts):
            source_lang = source_langs[i] if source_langs and i < len(source_langs) else None
            result = self.translate_to_english(text, source_lang)
            results.append(result)
            
            # Small delay to avoid rate limiting
            if self.enabled and result.get("was_translated"):
                time.sleep(0.5)
        
        return results
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported languages for translation
        
        Returns:
            List of language codes
        """
        # Llama supports a wide range of languages
        return [
            'en', 'es', 'fr', 'de', 'it', 'pt', 'nl', 'pl', 'ru',
            'ja', 'ko', 'zh', 'ar', 'hi', 'tr', 'sv', 'da', 'no',
            'fi', 'el', 'he', 'cs', 'hu', 'ro', 'th', 'vi', 'id',
            'ms', 'uk', 'bg', 'hr', 'sr', 'sk', 'sl', 'lt', 'lv',
            'et', 'sq', 'mk', 'is', 'ga', 'cy', 'eu', 'gl', 'ca'
        ]
    
    def is_translation_needed(self, text: str, target_lang: str = 'en') -> bool:
        """
        Check if translation is needed
        
        Args:
            text: Text to check
            target_lang: Target language (default: English)
            
        Returns:
            True if translation is needed
        """
        detected_lang, confidence = self.language_service.detect_language(text)
        
        # Don't translate if already in target language or confidence is low
        if detected_lang == target_lang or confidence < 0.5:
            return False
        
        return True
    
    def get_translation_stats(self) -> Dict:
        """
        Get translation service statistics
        
        Returns:
            Statistics dictionary
        """
        ollama_stats = self.ollama_service.get_service_stats()
        return {
            "service": "Translation Service",
            "provider": "Ollama",
            "enabled": self.enabled,
            "model": ollama_stats.get("model", "gpt-oss:120b"),
            "cache_size": len(self.translation_cache),
            "supported_languages": len(self.get_supported_languages())
        }
