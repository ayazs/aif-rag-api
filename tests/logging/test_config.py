"""Tests for logging configuration."""

import logging
import os
import tempfile

import pytest
from app.config import Settings
from app.logging.config import setup_logging, get_logger
from app.logging.formatters import JSONFormatter


@pytest.fixture
def temp_log_dir():
    """Create a temporary directory for log files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def settings(temp_log_dir):
    """Create settings with logging configuration."""
    return Settings(
        ENVIRONMENT="development",
        LOG_LEVEL="DEBUG",
        LOG_PATH=temp_log_dir,
        LOG_RETENTION_DAYS=1
    )


def test_development_logging_setup(settings):
    """Test logging setup in development environment."""
    setup_logging(settings)
    logger = get_logger("test_logger")
    
    # Check logger effective level
    assert logger.getEffectiveLevel() == logging.DEBUG
    
    # Check root logger has handlers
    root_logger = logging.getLogger()
    assert len(root_logger.handlers) > 0
    assert isinstance(root_logger.handlers[0], logging.StreamHandler)
    assert isinstance(root_logger.handlers[0].formatter, JSONFormatter)


def test_production_logging_setup(settings, temp_log_dir):
    """Test logging setup in production environment."""
    settings.ENVIRONMENT = "production"
    setup_logging(settings)
    logger = get_logger("test_logger")
    
    # Check logger effective level
    assert logger.getEffectiveLevel() == logging.DEBUG
    
    # Check root logger has handlers
    root_logger = logging.getLogger()
    assert len(root_logger.handlers) > 0
    assert isinstance(root_logger.handlers[0], logging.handlers.TimedRotatingFileHandler)
    assert isinstance(root_logger.handlers[0].formatter, JSONFormatter)
    
    # Verify log directory and file creation
    assert os.path.exists(temp_log_dir)
    log_files = os.listdir(temp_log_dir)
    assert any(file.startswith("aif-rag-api.log") for file in log_files)


def test_log_directory_creation(settings, temp_log_dir):
    """Test that log directory is created if it doesn't exist."""
    # Remove the directory
    os.rmdir(temp_log_dir)
    assert not os.path.exists(temp_log_dir)
    
    # Setup logging should recreate it
    setup_logging(settings)
    assert os.path.exists(temp_log_dir)


def test_get_logger_level(settings):
    """Test that get_logger inherits the root logger level."""
    # Set root logger to INFO
    settings.LOG_LEVEL = "INFO"
    setup_logging(settings)
    root_logger = logging.getLogger()
    assert root_logger.level == logging.INFO
    
    # Child logger should inherit root level
    logger = get_logger("test_logger_info")
    assert logger.getEffectiveLevel() == logging.INFO  # Inherits INFO from root


def test_handler_replacement(settings):
    """Test that setup_logging replaces existing handlers."""
    setup_logging(settings)
    root_logger = logging.getLogger()
    initial_handlers = len(root_logger.handlers)
    
    # Setup logging again
    setup_logging(settings)
    assert len(root_logger.handlers) == initial_handlers  # Should not add duplicate handlers 