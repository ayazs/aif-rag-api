"""
Context management for logging.

This module provides utilities for managing logging context,
including correlation IDs and request-specific information.

Context Management:
    - Maintains contextual information across multiple log entries
    - Automatically includes context in all log messages
    - Useful for tracking related operations across components
    - Example: document_id, user_id, request_id

Correlation IDs:
    - Unique identifier for tracking a single operation across services
    - Automatically generated if not provided
    - Essential for distributed system debugging
    - Links related log entries together
    - Example: tracking a document processing request through multiple services

Usage:
    # Set correlation ID for a request
    set_correlation_id("req-123")

    # Add context information
    set_logging_context(document_id="doc-456", user_id="user-789")

    # Log messages will automatically include context and correlation ID
    logger.info("Processing document")
    # Output: {"message": "Processing document", "correlation_id": "req-123", "document_id": "doc-456", ...}

    # Clear context when done
    clear_logging_context()
"""

import contextvars
import uuid
from typing import Dict, Optional

# Context variable for correlation ID
correlation_id: contextvars.ContextVar[str] = contextvars.ContextVar("correlation_id")

# Context variable for additional context
logging_context: contextvars.ContextVar[Dict] = contextvars.ContextVar(
    "logging_context", default={}
)


def get_correlation_id() -> str:
    """
    Get the current correlation ID.
    
    Returns:
        Current correlation ID, or a new one if none exists
    """
    try:
        return correlation_id.get()
    except LookupError:
        new_id = str(uuid.uuid4())
        correlation_id.set(new_id)
        return new_id


def set_correlation_id(cid: Optional[str] = None) -> str:
    """
    Set the correlation ID.
    
    Args:
        cid: Optional correlation ID to set. If None, generates a new one.
        
    Returns:
        The set correlation ID
    """
    if cid is None:
        cid = str(uuid.uuid4())
    correlation_id.set(cid)
    return cid


def get_logging_context() -> Dict:
    """
    Get the current logging context.
    
    Returns:
        Dictionary of context information
    """
    return logging_context.get()


def set_logging_context(**kwargs) -> None:
    """
    Set additional context information for logging.
    
    Args:
        **kwargs: Key-value pairs to add to the logging context
    """
    current_context = logging_context.get()
    current_context.update(kwargs)
    logging_context.set(current_context)


def clear_logging_context() -> None:
    """Clear all logging context information."""
    logging_context.set({}) 