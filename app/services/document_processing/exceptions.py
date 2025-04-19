"""
Document processing exceptions.

This module defines custom exceptions for the document processing pipeline.
"""

class DocumentProcessingError(Exception):
    """Exception raised when document processing fails."""
    
    def __init__(self, message: str, original_error: Exception = None):
        """
        Initialize the exception.
        
        Args:
            message: Error message describing what went wrong
            original_error: The original exception that caused this error
        """
        super().__init__(message)
        self.original_error = original_error

class TextProcessingError(DocumentProcessingError):
    """Raised when text processing fails."""
    pass

class ChunkingError(DocumentProcessingError):
    """Raised when text chunking fails."""
    pass

class MetadataExtractionError(DocumentProcessingError):
    """Raised when metadata extraction fails."""
    pass

class ValidationError(DocumentProcessingError):
    """Raised when input validation fails."""
    pass

class ProcessingTimeoutError(DocumentProcessingError):
    """Raised when processing takes too long."""
    pass 