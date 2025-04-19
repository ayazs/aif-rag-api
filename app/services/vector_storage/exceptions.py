"""
Custom exceptions for the vector storage service.
"""

class VectorStorageError(Exception):
    """Base exception for vector storage errors."""
    pass

class IndexNotFoundError(VectorStorageError):
    """Raised when an index does not exist."""
    pass

class IndexCreationError(VectorStorageError):
    """Raised when index creation fails."""
    pass

class IndexDeletionError(VectorStorageError):
    """Raised when index deletion fails."""
    pass

class ServiceUnavailableError(VectorStorageError):
    """Raised when the vector storage service is unavailable."""
    pass

class RateLimitError(VectorStorageError):
    """Raised when API rate limits are exceeded."""
    pass

class ConfigurationError(VectorStorageError):
    """Raised when there are issues with service configuration."""
    pass

class ServiceTimeoutError(VectorStorageError):
    """Raised when a service operation times out."""
    pass

class UnexpectedError(VectorStorageError):
    """Raised when an unexpected error occurs."""
    pass 