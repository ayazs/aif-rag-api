"""Exceptions for the OpenAI service."""


class OpenAIError(Exception):
    """Base exception for OpenAI service errors."""
    pass


class EmbeddingError(OpenAIError):
    """Raised when there's an error generating embeddings."""
    pass


class RateLimitError(OpenAIError):
    """Raised when OpenAI's rate limit is exceeded."""
    pass


class AuthenticationError(OpenAIError):
    """Raised when there's an authentication error with OpenAI."""
    pass


class ServiceUnavailableError(OpenAIError):
    """Raised when the OpenAI service is unavailable."""
    pass 