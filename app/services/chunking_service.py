"""
Text Chunking Service
Handles splitting of large texts into manageable chunks for processing
"""

import logging
from typing import List, Dict, Tuple
import re

logger = logging.getLogger(__name__)

class ChunkingService:
    """Service for splitting text into chunks for processing"""
    
    def __init__(self, chunk_size: int = 1000, overlap: int = 50):
        """
        Initialize chunking service
        
        Args:
            chunk_size: Maximum size of each chunk in characters
            overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.min_chunk_size = 50  # Minimum viable chunk size
        
        logger.info(f"Chunking service initialized with chunk_size={chunk_size}, overlap={overlap}")
    
    def chunk_text(self, text: str, preserve_sentences: bool = True) -> List[Dict]:
        """
        Split text into chunks for processing
        
        Args:
            text: Input text to chunk
            preserve_sentences: Whether to try to preserve sentence boundaries
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        if not text or len(text.strip()) < self.min_chunk_size:
            return [{
                "chunk_id": 0,
                "text": text.strip(),
                "start_index": 0,
                "end_index": len(text),
                "chunk_number": 1,
                "total_chunks": 1
            }]
        
        # Clean the text
        text = self._clean_text(text)
        
        if preserve_sentences:
            chunks = self._chunk_by_sentences(text)
        else:
            chunks = self._chunk_by_characters(text)
        
        # Add metadata to chunks
        chunk_results = []
        total_chunks = len(chunks)
        
        for i, (chunk_text, start_idx, end_idx) in enumerate(chunks):
            chunk_results.append({
                "chunk_id": i,
                "text": chunk_text,
                "start_index": start_idx,
                "end_index": end_idx,
                "chunk_number": i + 1,
                "total_chunks": total_chunks,
                "chunk_size": len(chunk_text)
            })
        
        logger.info(f"Text chunked into {total_chunks} chunks")
        return chunk_results
    
    def _clean_text(self, text: str) -> str:
        """
        Clean text for better chunking
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special unicode characters that might cause issues
        text = text.encode('ascii', 'ignore').decode('ascii', 'ignore')
        
        return text.strip()
    
    def _chunk_by_sentences(self, text: str) -> List[Tuple[str, int, int]]:
        """
        Chunk text while preserving sentence boundaries
        
        Args:
            text: Input text
            
        Returns:
            List of (chunk_text, start_index, end_index) tuples
        """
        # Split by sentence-ending punctuation
        sentences = self._split_into_sentences(text)
        
        chunks = []
        current_chunk = []
        current_length = 0
        current_start = 0
        
        for sentence, start_idx, end_idx in sentences:
            sentence_length = len(sentence)
            
            # If adding this sentence would exceed chunk size
            if current_length + sentence_length > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_text = ' '.join(current_chunk)
                chunks.append((chunk_text, current_start, start_idx))
                
                # Start new chunk with overlap
                if self.overlap > 0 and len(current_chunk) > 1:
                    # Include last sentence from previous chunk as overlap
                    current_chunk = [current_chunk[-1]]
                    current_length = len(current_chunk[0])
                    current_start = start_idx - current_length
                else:
                    current_chunk = []
                    current_length = 0
                    current_start = start_idx
            
            current_chunk.append(sentence)
            current_length += sentence_length + 1  # +1 for space
        
        # Add remaining chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append((chunk_text, current_start, len(text)))
        
        return chunks
    
    def _chunk_by_characters(self, text: str) -> List[Tuple[str, int, int]]:
        """
        Simple character-based chunking with overlap
        
        Args:
            text: Input text
            
        Returns:
            List of (chunk_text, start_index, end_index) tuples
        """
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            # Calculate end position
            end = min(start + self.chunk_size, text_length)
            
            # Try to find a good breaking point (space, punctuation)
            if end < text_length:
                # Look for the last space or punctuation
                for i in range(end, max(start + self.min_chunk_size, end - 50), -1):
                    if text[i] in ' .,;!?\\n':
                        end = i + 1
                        break
            
            # Extract chunk
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append((chunk_text, start, end))
            
            # Move start position with overlap
            if end < text_length:
                start = end - self.overlap
            else:
                break
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[Tuple[str, int, int]]:
        """
        Split text into sentences with position tracking
        
        Args:
            text: Input text
            
        Returns:
            List of (sentence, start_index, end_index) tuples
        """
        # Regex pattern for sentence boundaries
        sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z])|(?<=[.!?])$'
        
        sentences = []
        current_pos = 0
        
        # Split by sentence-ending punctuation
        parts = re.split(sentence_pattern, text)
        
        for part in parts:
            if part and part.strip():
                part = part.strip()
                start_idx = text.find(part, current_pos)
                end_idx = start_idx + len(part)
                sentences.append((part, start_idx, end_idx))
                current_pos = end_idx
        
        # If no sentences found, treat entire text as one sentence
        if not sentences:
            sentences = [(text, 0, len(text))]
        
        return sentences
    
    def chunk_batch(self, texts: List[str]) -> List[List[Dict]]:
        """
        Chunk multiple texts
        
        Args:
            texts: List of texts to chunk
            
        Returns:
            List of chunk lists for each text
        """
        results = []
        for text in texts:
            chunks = self.chunk_text(text)
            results.append(chunks)
        return results
    
    def merge_chunks(self, chunks: List[str], separator: str = " ") -> str:
        """
        Merge chunks back into a single text
        
        Args:
            chunks: List of chunk texts
            separator: Separator to use between chunks
            
        Returns:
            Merged text
        """
        return separator.join(chunks)
    
    def get_chunk_statistics(self, chunks: List[Dict]) -> Dict:
        """
        Get statistics about chunks
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            Statistics dictionary
        """
        if not chunks:
            return {
                "total_chunks": 0,
                "avg_chunk_size": 0,
                "min_chunk_size": 0,
                "max_chunk_size": 0,
                "total_characters": 0
            }
        
        sizes = [len(chunk["text"]) for chunk in chunks]
        
        return {
            "total_chunks": len(chunks),
            "avg_chunk_size": sum(sizes) / len(sizes),
            "min_chunk_size": min(sizes),
            "max_chunk_size": max(sizes),
            "total_characters": sum(sizes)
        }
