"""Integration tests for the logging system."""

import json
import logging
import os
import tempfile
from typing import Generator

import pytest
from app.config import Settings
from app.logging import (
    setup_logging,
    get_logger,
    set_correlation_id,
    set_logging_context,
    clear_logging_context
)


@pytest.fixture
def temp_log_dir() -> Generator[str, None, None]:
    """Create a temporary directory for log files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def settings(temp_log_dir: str) -> Settings:
    """Create settings with logging configuration."""
    return Settings(
        ENVIRONMENT="production",  # Use production to test file output
        LOG_LEVEL="DEBUG",
        LOG_PATH=temp_log_dir,
        LOG_RETENTION_DAYS=1
    )


def test_complete_logging_flow(settings: Settings, temp_log_dir: str):
    """Test the complete logging flow with all features."""
    # Setup logging
    setup_logging(settings)
    logger = get_logger("test_integration")
    
    # Set correlation ID and context
    set_correlation_id("test-correlation-id")
    set_logging_context(
        user_id="test-user",
        action="integration-test",
        custom_field={"key": "value"}
    )
    
    # Log different types of messages
    logger.info("Info message")
    logger.warning("Warning message", extra={"additional": "data"})
    
    try:
        raise ValueError("Test exception")
    except Exception:
        logger.exception("Error occurred")
    
    # Read log file
    log_file = os.path.join(temp_log_dir, "aif-rag-api.log")
    with open(log_file, "r") as f:
        logs = [json.loads(line) for line in f.readlines()]
    
    # Verify common fields across all logs
    for log in logs:
        assert "timestamp" in log
        assert "level" in log
        assert log["service"] == "aif-rag-api"
        assert log["correlation_id"] == "test-correlation-id"
        assert log["user_id"] == "test-user"
        assert log["action"] == "integration-test"
        assert log["custom_field"] == {"key": "value"}
    
    # Verify specific log entries
    info_log = logs[0]
    assert info_log["level"] == "INFO"
    assert info_log["message"] == "Info message"
    
    warning_log = logs[1]
    assert warning_log["level"] == "WARNING"
    assert warning_log["message"] == "Warning message"
    assert warning_log["additional"] == "data"
    
    error_log = logs[2]
    assert error_log["level"] == "ERROR"
    assert error_log["message"] == "Error occurred"
    assert "exception" in error_log
    assert "ValueError: Test exception" in error_log["exception"]


def test_log_rotation(settings: Settings, temp_log_dir: str):
    """Test log rotation functionality."""
    from time import sleep
    import datetime
    
    # Set up logging
    setup_logging(settings)
    logger = get_logger("test_rotation")
    
    # Log a message
    logger.info("First message")
    
    # Get current log file
    initial_files = set(os.listdir(temp_log_dir))
    assert len(initial_files) == 1
    
    # Simulate midnight rotation
    handler = logging.getLogger().handlers[0]
    handler.rolloverAt = 0  # Force rotation
    sleep(1)  # Ensure timestamp difference
    
    # Log another message to trigger rotation
    logger.info("Second message")
    
    # Check rotated files
    final_files = set(os.listdir(temp_log_dir))
    assert len(final_files) == 2  # Original + rotated
    
    # Verify both messages are preserved
    all_content = ""
    for log_file in final_files:
        with open(os.path.join(temp_log_dir, log_file), "r") as f:
            all_content += f.read()
    
    assert "First message" in all_content
    assert "Second message" in all_content 