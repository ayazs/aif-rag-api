"""
Central logging module for the application.

This module provides a centralized logging interface.
"""

import logging
from app.logging.config import setup_logging
from app.logging.context import (
    get_correlation_id,
    set_correlation_id,
    get_logging_context,
    set_logging_context,
    clear_logging_context
)

__all__ = [
    "setup_logging",
    "get_logger",
    "get_correlation_id",
    "set_correlation_id",
    "get_logging_context",
    "set_logging_context",
    "clear_logging_context"
]

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.
    
    Args:
        name: Name of the logger (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name) 