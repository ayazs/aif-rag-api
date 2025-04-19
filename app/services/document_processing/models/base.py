"""
Base models for document processing.

This module defines the core data structures used throughout the document processing pipeline.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class ProcessingStatus(str, Enum):
    """Status of document processing."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class TextChunk(BaseModel):
    """Represents a chunk of processed text."""
    content: str = Field(..., description="The text content of the chunk")
    position: int = Field(..., description="Position of the chunk in the document")
    metadata: Dict = Field(default_factory=dict, description="Chunk-specific metadata")
    relationships: Optional[Dict] = Field(None, description="Relationships with other chunks")

class ProcessingContext(BaseModel):
    """Tracks the processing state and metadata."""
    correlation_id: str = Field(..., description="Unique identifier for tracking the processing")
    document_id: str = Field(..., description="Unique identifier for the document")
    start_time: datetime = Field(default_factory=datetime.utcnow, description="When processing started")
    metadata: Dict = Field(default_factory=dict, description="Processing metadata")
    status: ProcessingStatus = Field(default=ProcessingStatus.PENDING, description="Current processing status")
    error: Optional[str] = Field(None, description="Error message if processing failed")

class ProcessingResult(BaseModel):
    """Result of document processing."""
    document_id: str = Field(..., description="Unique identifier for the document")
    chunks: List[TextChunk] = Field(..., description="Processed text chunks")
    metadata: Dict = Field(default_factory=dict, description="Document metadata")
    processing_time: float = Field(..., description="Time taken to process the document in seconds")
    status: ProcessingStatus = Field(..., description="Final processing status") 