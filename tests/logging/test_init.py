"""Tests for logging module initialization."""

import logging
import pytest

from app.logging import (
    setup_logging,
    get_logger,
    get_correlation_id,
    set_correlation_id,
    get_logging_context,
    set_logging_context,
    clear_logging_context
)


def test_module_exports():
    """Test that all expected functions are exported."""
    from app.logging import __all__
    
    expected_exports = {
        "setup_logging",
        "get_logger",
        "get_correlation_id",
        "set_correlation_id",
        "get_logging_context",
        "set_logging_context",
        "clear_logging_context"
    }
    
    assert set(__all__) == expected_exports


def test_get_logger():
    """Test that get_logger returns a proper logger instance."""
    logger = get_logger("test")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test"


def test_logger_inheritance():
    """Test that loggers inherit settings from root logger."""
    # Configure root logger
    root_logger = logging.getLogger()
    original_level = root_logger.level
    try:
        root_logger.setLevel(logging.DEBUG)
        
        # Get a new logger
        logger = get_logger("test.child")
        assert logger.getEffectiveLevel() == logging.DEBUG
        
        # Change root level
        root_logger.setLevel(logging.INFO)
        assert logger.getEffectiveLevel() == logging.INFO
    finally:
        # Restore original level
        root_logger.setLevel(original_level) 