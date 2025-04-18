"""
Tests for vector storage service exceptions.
"""

from app.services.vector_storage.exceptions import (
    VectorStorageError,
    IndexNotFoundError,
    IndexCreationError,
    IndexDeletionError,
    ServiceUnavailableError,
    RateLimitError,
    ConfigurationError
)

def test_exception_inheritance():
    """Test that all exceptions inherit from VectorStorageError."""
    assert issubclass(IndexNotFoundError, VectorStorageError)
    assert issubclass(IndexCreationError, VectorStorageError)
    assert issubclass(IndexDeletionError, VectorStorageError)
    assert issubclass(ServiceUnavailableError, VectorStorageError)
    assert issubclass(RateLimitError, VectorStorageError)
    assert issubclass(ConfigurationError, VectorStorageError)

def test_error_messages():
    """Test that error messages are preserved."""
    message = "Test error message"
    exceptions = [
        VectorStorageError,
        IndexNotFoundError,
        IndexCreationError,
        IndexDeletionError,
        ServiceUnavailableError,
        RateLimitError,
        ConfigurationError
    ]
    
    for exc_class in exceptions:
        exc = exc_class(message)
        assert str(exc) == message 