"""Tests for logging context management."""

import uuid
from unittest.mock import patch

import pytest
from app.logging.context import (
    get_correlation_id,
    set_correlation_id,
    get_logging_context,
    set_logging_context,
    clear_logging_context
)


def test_correlation_id_generation():
    """Test automatic generation of correlation IDs."""
    # Clear any existing correlation ID
    clear_logging_context()
    
    # Get a new correlation ID
    cid = get_correlation_id()
    assert isinstance(cid, str)
    
    # Should be a valid UUID
    uuid.UUID(cid)  # This will raise ValueError if invalid
    
    # Getting it again should return the same ID
    assert get_correlation_id() == cid


def test_correlation_id_setting():
    """Test setting specific correlation IDs."""
    test_id = "test-correlation-id"
    set_correlation_id(test_id)
    assert get_correlation_id() == test_id
    
    # Setting None should generate a new ID
    new_id = set_correlation_id(None)
    assert new_id != test_id
    assert get_correlation_id() == new_id


def test_logging_context_empty():
    """Test initial empty logging context."""
    clear_logging_context()
    context = get_logging_context()
    assert isinstance(context, dict)
    assert len(context) == 0


def test_logging_context_setting():
    """Test setting and updating logging context."""
    clear_logging_context()
    
    # Set initial context
    set_logging_context(user_id="123", action="test")
    context = get_logging_context()
    assert context["user_id"] == "123"
    assert context["action"] == "test"
    
    # Update existing context
    set_logging_context(action="updated", new_field="value")
    context = get_logging_context()
    assert context["user_id"] == "123"  # Should retain existing value
    assert context["action"] == "updated"  # Should update existing value
    assert context["new_field"] == "value"  # Should add new value


def test_logging_context_clearing():
    """Test clearing logging context."""
    set_logging_context(user_id="123", action="test")
    assert len(get_logging_context()) > 0
    
    clear_logging_context()
    assert len(get_logging_context()) == 0


def test_context_isolation():
    """Test that context is isolated between different parts of code."""
    import threading
    import time
    
    def thread_function():
        set_correlation_id("thread-id")
        set_logging_context(thread_data="test")
        time.sleep(0.1)  # Ensure main thread runs
        assert get_correlation_id() == "thread-id"
        assert get_logging_context()["thread_data"] == "test"
    
    # Set main thread context
    set_correlation_id("main-id")
    set_logging_context(main_data="main")
    
    # Start new thread with different context
    thread = threading.Thread(target=thread_function)
    thread.start()
    
    # Verify main thread context is unchanged
    assert get_correlation_id() == "main-id"
    assert get_logging_context()["main_data"] == "main"
    assert "thread_data" not in get_logging_context()
    
    thread.join() 