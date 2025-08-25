"""
File validation utilities
Ensures secure and valid file uploads
"""

import os
import logging
from werkzeug.datastructures import FileStorage
from typing import Tuple

# Try to import magic, but make it optional
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False

logger = logging.getLogger(__name__)

class FileValidator:
    """Utility class for file validation"""
    
    def __init__(self):
        """Initialize file validator with configuration"""
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.allowed_extensions = {'json', 'csv'}  # Removed TXT support
        self.allowed_mime_types = {
            'application/json',
            'text/json',
            'text/csv',
            'application/csv',
            'text/plain'  # CSV files are often detected as text/plain
        }
    
    def validate_file(self, file: FileStorage) -> Tuple[bool, str]:
        """
        Validate uploaded file
        
        Args:
            file: Uploaded file object
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if file exists
        if not file:
            return False, "No file provided"
        
        # Check filename
        if not file.filename:
            return False, "File has no filename"
        
        # Check file extension
        if not self._validate_extension(file.filename):
            return False, f"Invalid file type. Allowed types: {', '.join(self.allowed_extensions)}"
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset file pointer
        
        if file_size > self.max_file_size:
            return False, f"File too large. Maximum size: {self.max_file_size / (1024*1024):.1f}MB"
        
        if file_size == 0:
            return False, "File is empty"
        
        # Check MIME type (if python-magic is available)
        try:
            mime_type = self._get_mime_type(file)
            if mime_type and not self._is_mime_type_valid(mime_type, file.filename):
                logger.warning(f"MIME type validation failed: {mime_type} for file {file.filename}")
                # Don't fail hard on MIME type, just warn
        except Exception as e:
            logger.warning(f"Could not validate MIME type: {e}")
        
        # Check for malicious content patterns
        if not self._check_content_safety(file):
            return False, "File contains potentially unsafe content"
        
        return True, ""
    
    def _validate_extension(self, filename: str) -> bool:
        """
        Validate file extension
        
        Args:
            filename: Name of the file
            
        Returns:
            True if extension is allowed
        """
        if '.' not in filename:
            return False
        
        extension = filename.rsplit('.', 1)[1].lower()
        return extension in self.allowed_extensions
    
    def _is_mime_type_valid(self, mime_type: str, filename: str) -> bool:
        """
        Check if MIME type is valid for the given filename
        
        Args:
            mime_type: Detected MIME type
            filename: Original filename
            
        Returns:
            True if MIME type is valid for the file type
        """
        if not filename or '.' not in filename:
            return mime_type in self.allowed_mime_types
        
        extension = filename.rsplit('.', 1)[1].lower()
        
        # Define valid MIME types for each extension
        valid_mime_types = {
            'csv': {'text/csv', 'application/csv', 'text/plain'},  # CSV files often detected as text/plain
            'json': {'application/json', 'text/json', 'text/plain'}  # JSON files sometimes detected as text/plain
        }
        
        if extension in valid_mime_types:
            return mime_type in valid_mime_types[extension]
        
        # Fallback to general allowed types
        return mime_type in self.allowed_mime_types
    
    def _get_mime_type(self, file: FileStorage) -> str:
        """
        Get MIME type of file
        
        Args:
            file: File object
            
        Returns:
            MIME type string
        """
        try:
            if MAGIC_AVAILABLE:
                # Read first 1024 bytes for magic number detection
                file_header = file.read(1024)
                file.seek(0)  # Reset file pointer
                
                # Use python-magic if available
                mime = magic.from_buffer(file_header, mime=True)
                return mime
            else:
                # Fall through to extension-based detection
                raise ImportError("Magic not available")
        except Exception:
            # Fallback to extension-based detection
            if file.filename:
                ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                mime_map = {
                    'json': 'application/json',
                    'csv': 'text/csv'
                }
                return mime_map.get(ext, 'application/octet-stream')
            return 'application/octet-stream'
    
    def _check_content_safety(self, file: FileStorage) -> bool:
        """
        Check file content for safety
        
        Args:
            file: File object
            
        Returns:
            True if content appears safe
        """
        try:
            # Read sample of file content
            sample = file.read(4096)
            file.seek(0)  # Reset file pointer
            
            # Check for executable signatures
            executable_signatures = [
                b'MZ',  # Windows executable
                b'\\x7fELF',  # Linux executable
                b'\\xca\\xfe\\xba\\xbe',  # Mach-O executable
                b'#!/',  # Shell script
                b'<%',  # Server-side script
                b'<?php'  # PHP script
            ]
            
            for signature in executable_signatures:
                if sample.startswith(signature):
                    logger.warning(f"Detected executable signature: {signature}")
                    return False
            
            # Check for suspicious patterns
            suspicious_patterns = [
                b'<script',  # JavaScript
                b'javascript:',  # JavaScript protocol
                b'onerror=',  # Event handler
                b'onclick=',  # Event handler
                b'eval(',  # JavaScript eval
                b'exec(',  # Python/other exec
                b'system(',  # System call
                b'__import__'  # Python import
            ]
            
            sample_lower = sample.lower()
            for pattern in suspicious_patterns:
                if pattern in sample_lower:
                    logger.warning(f"Detected suspicious pattern: {pattern}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking content safety: {e}")
            return False
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for safe storage
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove path components
        filename = os.path.basename(filename)
        
        # Remove special characters
        import re
        filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        
        # Limit length
        name, ext = os.path.splitext(filename)
        if len(name) > 50:
            name = name[:50]
        
        return name + ext
    
    def get_file_info(self, file: FileStorage) -> dict:
        """
        Get information about uploaded file
        
        Args:
            file: File object
            
        Returns:
            Dictionary with file information
        """
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        return {
            'filename': file.filename,
            'size': file_size,
            'size_mb': file_size / (1024 * 1024),
            'extension': file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else None,
            'mime_type': self._get_mime_type(file)
        }
