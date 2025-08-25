"""
Text processing utilities
Handles text chunking, cleaning, and preprocessing
"""

import re
import logging
from typing import List, Tuple
from app.models.review_models import TextChunk

logger = logging.getLogger(__name__)

class TextProcessor:
    """Utility class for text processing operations"""
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        """
        Initialize text processor
        
        Args:
            chunk_size: Maximum size of text chunks in tokens
            chunk_overlap: Number of overlapping tokens between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text
        
        Args:
            text: Raw input text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove control characters
        text = ''.join(char for char in text if ord(char) >= 32 or char == '\\n')
        
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        # Remove multiple consecutive punctuation
        text = re.sub(r'([.!?]){2,}', r'\\1', text)
        
        # Fix spacing around punctuation
        text = re.sub(r'\\s+([.!?,;:])', r'\\1', text)
        
        return text.strip()
    
    def chunk_text(self, text: str) -> List[TextChunk]:
        """
        Split text into chunks for processing
        
        Args:
            text: Input text to chunk
            
        Returns:
            List of text chunks
        """
        # Clean text first
        text = self.clean_text(text)
        
        # Simple word-based chunking
        words = text.split()
        
        if len(words) <= self.chunk_size:
            # Text fits in single chunk
            return [TextChunk(0, text, 0, len(text))]
        
        chunks = []
        chunk_id = 0
        i = 0
        
        while i < len(words):
            # Calculate chunk boundaries
            start_idx = max(0, i - self.chunk_overlap if i > 0 else 0)
            end_idx = min(i + self.chunk_size, len(words))
            
            # Create chunk text
            chunk_words = words[start_idx:end_idx]
            chunk_text = ' '.join(chunk_words)
            
            # Calculate character positions
            char_start = len(' '.join(words[:start_idx])) + (1 if start_idx > 0 else 0)
            char_end = char_start + len(chunk_text)
            
            # Create chunk object
            chunk = TextChunk(
                chunk_id=chunk_id,
                text=chunk_text,
                start_index=char_start,
                end_index=char_end
            )
            chunks.append(chunk)
            
            # Move to next chunk
            i += self.chunk_size - self.chunk_overlap
            chunk_id += 1
        
        return chunks
    
    def extract_sentences(self, text: str) -> List[str]:
        """
        Extract sentences from text
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        # Clean text
        text = self.clean_text(text)
        
        # Simple sentence splitting
        # This is a basic implementation - consider using NLTK for better results
        sentences = re.split(r'[.!?]+', text)
        
        # Clean and filter sentences
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def remove_urls(self, text: str) -> str:
        """
        Remove URLs from text
        
        Args:
            text: Input text
            
        Returns:
            Text with URLs removed
        """
        # Remove HTTP(S) URLs
        text = re.sub(r'https?://\\S+', '', text)
        
        # Remove www URLs
        text = re.sub(r'www\\.\\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\\S+@\\S+', '', text)
        
        return text.strip()
    
    def remove_special_characters(self, text: str, keep_punctuation: bool = True) -> str:
        """
        Remove special characters from text
        
        Args:
            text: Input text
            keep_punctuation: Whether to keep basic punctuation
            
        Returns:
            Cleaned text
        """
        if keep_punctuation:
            # Keep alphanumeric, spaces, and basic punctuation
            pattern = r"[^a-zA-Z0-9\\s.,!?;:'\"-]"
        else:
            # Keep only alphanumeric and spaces
            pattern = r'[^a-zA-Z0-9\\s]'
        
        text = re.sub(pattern, '', text)
        
        # Remove extra spaces
        text = ' '.join(text.split())
        
        return text
    
    def truncate_text(self, text: str, max_length: int = 1000) -> str:
        """
        Truncate text to maximum length
        
        Args:
            text: Input text
            max_length: Maximum character length
            
        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text
        
        # Try to truncate at sentence boundary
        truncated = text[:max_length]
        
        # Find last sentence ending
        last_period = truncated.rfind('.')
        last_question = truncated.rfind('?')
        last_exclamation = truncated.rfind('!')
        
        last_sentence = max(last_period, last_question, last_exclamation)
        
        if last_sentence > max_length * 0.8:  # If we can keep at least 80% of the text
            return truncated[:last_sentence + 1]
        
        # Otherwise, truncate at word boundary
        last_space = truncated.rfind(' ')
        if last_space > max_length * 0.9:
            return truncated[:last_space] + '...'
        
        return truncated + '...'
    
    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        # Simple word-based token counting
        # For more accurate results, use the actual tokenizer
        words = text.split()
        
        # Rough estimate: 1 word ≈ 1.3 tokens
        return int(len(words) * 1.3)
    
    def is_valid_text(self, text: str, min_length: int = 3, max_length: int = 10000) -> Tuple[bool, str]:
        """
        Validate text for processing
        
        Args:
            text: Text to validate
            min_length: Minimum required length
            max_length: Maximum allowed length
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not text or not text.strip():
            return False, "Text is empty"
        
        text_length = len(text.strip())
        
        if text_length < min_length:
            return False, f"Text too short (minimum {min_length} characters)"
        
        if text_length > max_length:
            return False, f"Text too long (maximum {max_length} characters)"
        
        # Check if text contains actual content (not just special characters)
        if not re.search(r'[a-zA-Z0-9]', text):
            return False, "Text contains no alphanumeric content"
        
        return True, ""
