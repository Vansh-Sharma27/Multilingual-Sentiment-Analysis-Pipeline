"""
File Processing Service
Handles parsing and processing of CSV and TXT files for sentiment analysis
"""

import logging
import csv
import json
import io
from typing import List, Dict, Optional, Tuple
from werkzeug.datastructures import FileStorage

logger = logging.getLogger(__name__)

class FileProcessingService:
    """Service for processing uploaded files for sentiment analysis"""
    
    def __init__(self):
        """Initialize file processing service"""
        self.supported_formats = ['csv', 'json']  # Removed TXT support
        self.max_rows = 1000  # Maximum rows to process from CSV
        
        logger.info("File Processing Service initialized")
    
    def process_file(self, file: FileStorage) -> Dict:
        """
        Process uploaded file and extract texts for analysis
        
        Args:
            file: Uploaded file object
            
        Returns:
            Dictionary with extracted texts and metadata
        """
        if not file or not file.filename:
            return {
                "success": False,
                "error": "No file provided",
                "texts": []
            }
        
        # Get file extension
        extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        if extension not in self.supported_formats:
            return {
                "success": False,
                "error": f"Unsupported file format. Supported: {', '.join(self.supported_formats)}",
                "texts": []
            }
        
        try:
            # Process based on file type
            if extension == 'csv':
                result = self._process_csv(file)
            elif extension == 'json':
                result = self._process_json(file)
            else:
                result = {
                    "success": False,
                    "error": "Unknown file format",
                    "texts": []
                }
            
            # Add file metadata
            result["filename"] = file.filename
            result["format"] = extension
            
            return result
            
        except Exception as e:
            logger.error(f"File processing failed: {e}")
            return {
                "success": False,
                "error": f"Processing failed: {str(e)}",
                "texts": [],
                "filename": file.filename,
                "format": extension
            }
    
    def _process_csv(self, file: FileStorage) -> Dict:
        """
        Process CSV file and extract texts
        
        Args:
            file: CSV file object
            
        Returns:
            Dictionary with extracted texts
        """
        texts = []
        metadata = []
        
        try:
            # Read file content
            content = file.read()
            file.seek(0)
            
            # Try to decode with different encodings
            text_content = None
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    text_content = content.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if not text_content:
                return {
                    "success": False,
                    "error": "Could not decode CSV file",
                    "texts": []
                }
            
            # Parse CSV
            csv_reader = csv.DictReader(io.StringIO(text_content))
            
            # Find text columns (look for common names)
            text_columns = self._identify_text_columns(csv_reader.fieldnames)
            
            if not text_columns:
                return {
                    "success": False,
                    "error": "No text columns found in CSV",
                    "texts": [],
                    "columns": csv_reader.fieldnames
                }
            
            # Extract texts
            row_count = 0
            for row in csv_reader:
                if row_count >= self.max_rows:
                    logger.warning(f"Reached maximum row limit ({self.max_rows})")
                    break
                
                # Combine text from identified columns
                text_parts = []
                row_metadata = {"row_number": row_count + 1}
                
                for col in text_columns:
                    if col in row and row[col]:
                        text_parts.append(row[col])
                        row_metadata[col] = row[col][:50] + "..." if len(row[col]) > 50 else row[col]
                
                if text_parts:
                    combined_text = " ".join(text_parts)
                    texts.append(combined_text)
                    metadata.append(row_metadata)
                
                row_count += 1
            
            return {
                "success": True,
                "texts": texts,
                "metadata": metadata,
                "text_columns": text_columns,
                "total_rows": row_count,
                "truncated": row_count >= self.max_rows
            }
            
        except csv.Error as e:
            logger.error(f"CSV parsing error: {e}")
            return {
                "success": False,
                "error": f"CSV parsing error: {str(e)}",
                "texts": []
            }
    

    
    def _process_json(self, file: FileStorage) -> Dict:
        """
        Process JSON file and extract texts
        
        Args:
            file: JSON file object
            
        Returns:
            Dictionary with extracted texts
        """
        try:
            # Read and parse JSON
            content = file.read()
            file.seek(0)
            
            # Decode JSON
            try:
                data = json.loads(content.decode('utf-8'))
            except UnicodeDecodeError:
                data = json.loads(content.decode('latin-1'))
            
            # Extract texts based on structure
            texts = self._extract_texts_from_json(data)
            
            if not texts:
                return {
                    "success": False,
                    "error": "No text content found in JSON",
                    "texts": []
                }
            
            return {
                "success": True,
                "texts": texts[:self.max_rows],  # Limit number of texts
                "total_items": len(texts),
                "truncated": len(texts) > self.max_rows
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return {
                "success": False,
                "error": f"JSON parsing error: {str(e)}",
                "texts": []
            }
        except Exception as e:
            logger.error(f"JSON processing error: {e}")
            return {
                "success": False,
                "error": f"JSON processing error: {str(e)}",
                "texts": []
            }
    
    def _identify_text_columns(self, columns: List[str]) -> List[str]:
        """
        Identify columns that likely contain text for analysis
        
        Args:
            columns: List of column names
            
        Returns:
            List of identified text column names
        """
        if not columns:
            return []
        
        # Common text column names
        text_indicators = [
            'text', 'comment', 'review', 'feedback', 'description',
            'content', 'message', 'body', 'summary', 'title',
            'opinion', 'response', 'answer', 'question', 'note'
        ]
        
        text_columns = []
        
        for col in columns:
            col_lower = col.lower()
            # Check if column name contains any text indicator
            for indicator in text_indicators:
                if indicator in col_lower:
                    text_columns.append(col)
                    break
        
        # If no columns identified, use the first column
        if not text_columns and columns:
            text_columns = [columns[0]]
        
        return text_columns
    

    
    def _extract_texts_from_json(self, data, texts: Optional[List[str]] = None) -> List[str]:
        """
        Recursively extract text content from JSON structure
        
        Args:
            data: JSON data (dict, list, or primitive)
            texts: Accumulator for extracted texts
            
        Returns:
            List of extracted texts
        """
        if texts is None:
            texts = []
        
        if isinstance(data, dict):
            # Look for text-like keys
            text_keys = ['text', 'content', 'message', 'body', 'review', 'comment', 'description']
            
            for key, value in data.items():
                if any(tk in key.lower() for tk in text_keys):
                    if isinstance(value, str) and len(value) > 20:
                        texts.append(value)
                elif isinstance(value, (dict, list)):
                    self._extract_texts_from_json(value, texts)
                    
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, str) and len(item) > 20:
                    texts.append(item)
                elif isinstance(item, (dict, list)):
                    self._extract_texts_from_json(item, texts)
        
        return texts
    
    def get_sample_data(self, file_format: str) -> str:
        """
        Get sample data for a specific file format
        
        Args:
            file_format: File format (csv, txt, json)
            
        Returns:
            Sample data string
        """
        samples = {
            "csv": "text,rating,date\n\"This product is amazing!\",5,2024-01-01\n\"Not satisfied with the quality\",2,2024-01-02\n\"Good value for money\",4,2024-01-03",
            "json": '[\n  {"id": 1, "text": "Great service!", "rating": 5},\n  {"id": 2, "text": "Could be better", "rating": 3}\n]'
        }
        
        return samples.get(file_format, "")
