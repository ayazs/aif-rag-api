"""
Logging configuration module.

This module handles the setup and configuration of logging.
"""

import logging
import logging.handlers
import os
from typing import Optional

from app.config import Settings
from app.logging.formatters import JSONFormatter


def setup_logging(settings: Settings) -> None:
    """
    Configure logging based on environment settings.
    
    Args:
        settings: Application settings containing logging configuration
    """
    # Create logs directory if it doesn't exist
    if settings.LOG_PATH:
        os.makedirs(settings.LOG_PATH, exist_ok=True)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create appropriate handler based on environment
    if settings.ENVIRONMENT == "development":
        handler = logging.StreamHandler()
    else:
        log_file = os.path.join(settings.LOG_PATH, "aif-rag-api.log")
        handler = logging.handlers.TimedRotatingFileHandler(
            filename=log_file,
            when="midnight",
            interval=1,
            backupCount=settings.LOG_RETENTION_DAYS,
            encoding="utf-8",
        )

    # Set formatter
    handler.setFormatter(JSONFormatter())
    root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: The name of the logger
        
    Returns:
        A configured logger instance
    """
    logger = logging.getLogger(name)
    # Don't set level on child loggers to allow proper level inheritance
    logger.propagate = True
    return logger 