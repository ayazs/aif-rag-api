"""Shared fixtures for logging tests."""

import logging
import os
import tempfile
from typing import Generator

import pytest
from app.config import Settings
from app.logging import setup_logging, get_logger


@pytest.fixture
def temp_log_dir() -> Generator[str, None, None]:
    """Create a temporary directory for log files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def settings(temp_log_dir: str) -> Settings:
    """Create settings with logging configuration."""
    return Settings(
        ENVIRONMENT="development",
        LOG_LEVEL="DEBUG",
        LOG_PATH=temp_log_dir,
        LOG_RETENTION_DAYS=1
    )


@pytest.fixture
def logger(settings: Settings) -> logging.Logger:
    """Create a configured logger."""
    setup_logging(settings)
    return get_logger("test_logger")


@pytest.fixture(autouse=True)
def clean_logging_context():
    """Automatically clean logging context before and after each test."""
    from app.logging import clear_logging_context
    clear_logging_context()
    yield
    clear_logging_context() 