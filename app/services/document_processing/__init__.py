"""
Document processing service package.

This package provides functionality for processing documents through various stages
including text processing, embedding generation, and vector storage.
"""

from app.services.document_processing.document_service import DocumentService
from app.services.document_processing.processors.text import TextProcessor
from app.services.document_processing.exceptions import (
    DocumentProcessingError,
    TextProcessingError,
    ChunkingError,
    MetadataExtractionError,
    ValidationError,
    ProcessingTimeoutError
)

__all__ = [
    'DocumentService',
    'TextProcessor',
    'DocumentProcessingError',
    'TextProcessingError',
    'ChunkingError',
    'MetadataExtractionError',
    'ValidationError',
    'ProcessingTimeoutError'
] 