"""
Tokenization Optimization Service
Provides advanced tokenization strategies for improved performance in multilingual sentiment analysis
"""

import logging
import hashlib
import time
from typing import List, Dict, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
from functools import lru_cache

logger = logging.getLogger(__name__)

class TokenizationService:
    """
    Advanced tokenization service for performance optimization
    Implements caching, batch processing, and multilingual optimization
    """
    
    def __init__(self):
        """Initialize the tokenization service with optimization features"""
        self.cache = {}
        self.max_cache_size = 2000
        self.batch_size = 16  # Optimal batch size for processing
        self.similarity_threshold = 0.85
        
        # Language-specific optimization patterns
        self.language_patterns = {
            'fr': {
                'accents': r'[àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ]',
                'common_words': ['le', 'la', 'les', 'de', 'du', 'des', 'et', 'ou', 'est', 'sont'],
                'punctuation': r'[«»]'
            },
            'de': {
                'accents': r'[äöüß]',
                'common_words': ['der', 'die', 'das', 'und', 'oder', 'ist', 'sind'],
                'punctuation': r'[„"]'
            },
            'es': {
                'accents': r'[áéíóúüñ¿¡]',
                'common_words': ['el', 'la', 'los', 'las', 'de', 'del', 'y', 'o', 'es', 'son'],
                'punctuation': r'[¿¡]'
            },
            'hi': {
                'script': r'[अ-ह]',
                'common_words': ['है', 'हैं', 'और', 'या', 'का', 'की', 'के'],
                'punctuation': r'[।]'
            },
            'en': {
                'common_words': ['the', 'and', 'is', 'are', 'of', 'to', 'in', 'a', 'that', 'it'],
                'contractions': r"(n't|'re|'ve|'ll|'d|'s)"
            }
        }
        
        logger.info("TokenizationService initialized with advanced optimization features")
    
    def optimize_text_for_analysis(self, text: str, language: str = 'en') -> str:
        """
        Optimize text for sentiment analysis using tokenization strategies
        
        Args:
            text: Input text to optimize
            language: Detected language of the text
            
        Returns:
            Optimized text ready for analysis
        """
        # Check cache first
        cache_key = self._get_cache_key(text, f"optimize_{language}")
        if cache_key in self.cache:
            logger.debug(f"Cache hit for text optimization: {text[:50]}...")
            return self.cache[cache_key]
        
        # Apply optimization pipeline
        optimized_text = self._apply_tokenization_pipeline(text, language)
        
        # Cache the result
        self._cache_result(cache_key, optimized_text)
        
        return optimized_text
    
    def batch_optimize_texts(self, texts: List[str], languages: List[str] = None) -> List[str]:
        """
        Optimize multiple texts using batch processing for better performance
        
        Args:
            texts: List of texts to optimize
            languages: List of corresponding languages (optional)
            
        Returns:
            List of optimized texts
        """
        if not languages:
            languages = ['en'] * len(texts)
        
        start_time = time.time()
        
        # Process in batches for optimal performance
        results = []
        batch_count = 0
        
        for i in range(0, len(texts), self.batch_size):
            batch_texts = texts[i:i + self.batch_size]
            batch_langs = languages[i:i + self.batch_size]
            
            # Use parallel processing for each batch
            batch_results = self._process_batch_parallel(batch_texts, batch_langs)
            results.extend(batch_results)
            
            batch_count += 1
            logger.debug(f"Processed batch {batch_count}, total texts: {len(results)}")
        
        processing_time = time.time() - start_time
        logger.info(f"Batch optimization completed: {len(texts)} texts in {processing_time:.2f}s")
        
        return results
    
    def preprocess_for_translation(self, text: str, source_language: str) -> str:
        """
        Pre-process text before translation to preserve semantic boundaries
        
        Args:
            text: Original text in source language
            source_language: Source language code
            
        Returns:
            Preprocessed text optimized for translation
        """
        # Check cache
        cache_key = self._get_cache_key(text, f"preprocess_{source_language}")
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Apply language-specific preprocessing
        preprocessed = self._apply_pre_translation_optimization(text, source_language)
        
        # Cache result
        self._cache_result(cache_key, preprocessed)
        
        return preprocessed
    
    def postprocess_after_translation(self, text: str, source_language: str) -> str:
        """
        Post-process text after translation to clean up artifacts
        
        Args:
            text: Translated text (usually English)
            source_language: Original source language
            
        Returns:
            Cleaned up translated text
        """
        # Check cache
        cache_key = self._get_cache_key(text, f"postprocess_{source_language}")
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Apply post-translation cleanup
        cleaned = self._apply_post_translation_cleanup(text, source_language)
        
        # Cache result
        self._cache_result(cache_key, cleaned)
        
        return cleaned
    
    def _apply_tokenization_pipeline(self, text: str, language: str) -> str:
        """Apply the complete tokenization optimization pipeline"""
        # Step 1: Basic cleaning
        text = self._basic_text_cleaning(text)
        
        # Step 2: Language-specific optimization
        text = self._apply_language_specific_optimization(text, language)
        
        # Step 3: Sentiment-focused preprocessing
        text = self._apply_sentiment_preprocessing(text)
        
        # Step 4: Token normalization
        text = self._normalize_tokens(text)
        
        return text
    
    def _basic_text_cleaning(self, text: str) -> str:
        """Apply basic text cleaning optimizations"""
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove zero-width characters
        text = re.sub(r'[\u200b-\u200d\ufeff]', '', text)
        
        # Normalize quotes and dashes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        text = text.replace('–', '-').replace('—', '-')
        
        # Fix common encoding issues
        text = text.replace('â€™', "'").replace('â€œ', '"').replace('â€', '"')
        
        return text.strip()
    
    def _apply_language_specific_optimization(self, text: str, language: str) -> str:
        """Apply language-specific optimizations"""
        if language not in self.language_patterns:
            return text
        
        patterns = self.language_patterns[language]
        
        # Handle contractions for English
        if language == 'en' and 'contractions' in patterns:
            text = re.sub(patterns['contractions'], lambda m: m.group(1).replace("'", ""), text)
        
        # Normalize language-specific punctuation
        if 'punctuation' in patterns:
            # Replace language-specific punctuation with standard equivalents
            if language == 'fr':
                text = text.replace('«', '"').replace('»', '"')
            elif language == 'de':
                text = text.replace('„', '"').replace('"', '"')
            elif language == 'es':
                text = text.replace('¿', '').replace('¡', '')
            elif language == 'hi':
                text = text.replace('।', '.')
        
        return text
    
    def _apply_sentiment_preprocessing(self, text: str) -> str:
        """Apply preprocessing specifically optimized for sentiment analysis"""
        # Handle emoticons and emoji (preserve sentiment-bearing elements)
        emoticon_pattern = r'[:\-=][)(\[\]DPpOo/\\|]'
        text = re.sub(emoticon_pattern, lambda m: ' ' + m.group() + ' ', text)
        
        # Handle repeated punctuation (normalize while preserving emphasis)
        text = re.sub(r'([!?]){2,}', r'\1\1', text)  # Max 2 repetitions
        text = re.sub(r'([.]){3,}', '...', text)      # Normalize ellipsis
        
        # Handle ALL CAPS (preserve but normalize)
        words = text.split()
        normalized_words = []
        
        for word in words:
            if len(word) > 2 and word.isupper() and word.isalpha():
                # Convert to title case to preserve emphasis indication
                normalized_words.append(word.capitalize() + '!')
            else:
                normalized_words.append(word)
        
        return ' '.join(normalized_words)
    
    def _normalize_tokens(self, text: str) -> str:
        """Final token normalization for consistent processing"""
        # Ensure consistent spacing around punctuation
        text = re.sub(r'\s+([.!?,;:])', r'\1', text)  # Remove space before punctuation
        text = re.sub(r'([.!?,;:])\s*', r'\1 ', text)  # Ensure space after punctuation
        
        # Remove excessive spaces
        text = ' '.join(text.split())
        
        return text.strip()
    
    def _apply_pre_translation_optimization(self, text: str, source_language: str) -> str:
        """Optimize text before translation to preserve semantic boundaries"""
        # Protect sentiment-bearing phrases
        sentiment_phrases = {
            'fr': ['très bien', 'très mal', 'pas du tout', 'vraiment'],
            'de': ['sehr gut', 'sehr schlecht', 'überhaupt nicht', 'wirklich'],
            'es': ['muy bien', 'muy mal', 'para nada', 'realmente'],
            'hi': ['बहुत अच्छा', 'बहुत बुरा', 'बिल्कुल नहीं']
        }
        
        if source_language in sentiment_phrases:
            # Mark important phrases to preserve during translation
            for phrase in sentiment_phrases[source_language]:
                text = text.replace(phrase, f"[PRESERVE]{phrase}[/PRESERVE]")
        
        return text
    
    def _apply_post_translation_cleanup(self, text: str, source_language: str) -> str:
        """Clean up translation artifacts and restore preserved elements"""
        # Restore preserved phrases
        text = re.sub(r'\[PRESERVE\](.*?)\[/PRESERVE\]', r'\1', text)
        
        # Clean up common translation artifacts
        artifacts = [
            'This product', 'This service', 'The quality', 'The experience'
        ]
        
        # Remove redundant article introductions that weren't in original
        for artifact in artifacts:
            if text.startswith(artifact) and source_language != 'en':
                # If original likely didn't start with English articles, clean up
                text = re.sub(r'^(This|The)\s+', '', text)
                break
        
        return text
    
    def _process_batch_parallel(self, texts: List[str], languages: List[str]) -> List[str]:
        """Process a batch of texts in parallel for better performance"""
        results = [None] * len(texts)
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all tasks
            future_to_index = {
                executor.submit(self.optimize_text_for_analysis, text, lang): i
                for i, (text, lang) in enumerate(zip(texts, languages))
            }
            
            # Collect results maintaining order
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    results[index] = future.result()
                except Exception as e:
                    logger.error(f"Error processing text at index {index}: {e}")
                    results[index] = texts[index]  # Fallback to original
        
        return results
    
    @lru_cache(maxsize=1000)
    def _get_cache_key(self, text: str, operation: str) -> str:
        """Generate cache key with operation context"""
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        return f"{operation}:{text_hash[:16]}"
    
    def _cache_result(self, key: str, result: str) -> None:
        """Cache result with size management"""
        if len(self.cache) >= self.max_cache_size:
            # Remove oldest entries (simple FIFO)
            oldest_keys = list(self.cache.keys())[:100]
            for old_key in oldest_keys:
                del self.cache[old_key]
        
        self.cache[key] = result
    
    def get_optimization_stats(self) -> Dict:
        """Get statistics about optimization performance"""
        return {
            'cache_size': len(self.cache),
            'max_cache_size': self.max_cache_size,
            'cache_hit_rate': getattr(self, '_cache_hits', 0) / max(getattr(self, '_cache_requests', 1), 1),
            'supported_languages': list(self.language_patterns.keys()),
            'batch_size': self.batch_size
        }
    
    def clear_cache(self) -> None:
        """Clear the optimization cache"""
        self.cache.clear()
        logger.info("TokenizationService cache cleared")
