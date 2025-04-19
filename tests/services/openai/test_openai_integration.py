"""Integration tests for the OpenAI service."""

import os
import pytest
from app.config import Settings
from app.services.openai.openai import OpenAIService
from app.services.openai.exceptions import (
    EmbeddingError,
    RateLimitError,
    AuthenticationError,
    ServiceUnavailableError
)


@pytest.fixture
def settings():
    """Create settings with OpenAI configuration."""
    return Settings()


@pytest.fixture
def openai_service(settings):
    """Create an OpenAI service instance."""
    return OpenAIService(settings)


@pytest.fixture
def invalid_api_key_service():
    """Create an OpenAI service with invalid API key."""
    # Temporarily modify env var to create service with invalid key
    original_key = os.environ.get('SERVICE_OPENAI_API_KEY')
    os.environ['SERVICE_OPENAI_API_KEY'] = 'invalid-key'
    settings = Settings()
    service = OpenAIService(settings)
    if original_key:
        os.environ['SERVICE_OPENAI_API_KEY'] = original_key
    else:
        del os.environ['SERVICE_OPENAI_API_KEY']
    return service


@pytest.mark.asyncio
async def test_generate_embeddings_success(openai_service):
    """Test successful embedding generation."""
    texts = ["This is a test sentence.", "This is another test sentence."]
    embeddings = await openai_service.generate_embeddings(texts)
    
    assert len(embeddings) == 2
    assert len(embeddings[0]) > 0  # Check that we got actual vectors
    assert len(embeddings[1]) > 0
    assert len(embeddings[0]) == len(embeddings[1])  # Check that vectors have same dimension


@pytest.mark.asyncio
async def test_generate_embeddings_empty_input(openai_service):
    """Test handling of empty input."""
    with pytest.raises(ValueError):
        await openai_service.generate_embeddings([])


@pytest.mark.asyncio
async def test_generate_embeddings_large_batch(openai_service):
    """Test handling of large batch of texts."""
    # Create a list of 200 test sentences
    texts = [f"This is test sentence {i}." for i in range(200)]
    embeddings = await openai_service.generate_embeddings(texts)
    
    assert len(embeddings) == 200
    assert all(len(embedding) > 0 for embedding in embeddings)


@pytest.mark.asyncio
async def test_generate_embeddings_auth_error(invalid_api_key_service):
    """Test handling of authentication error with invalid API key."""
    with pytest.raises(AuthenticationError, match="Invalid OpenAI API key"):
        await invalid_api_key_service.generate_embeddings(["test"])


@pytest.mark.asyncio
async def test_generate_embeddings_invalid_input(openai_service):
    """Test handling of invalid input that would cause an API error."""
    # Send empty strings which should cause an API error
    texts = ["", "", ""]
    
    with pytest.raises(EmbeddingError, match="Error generating embeddings"):
        await openai_service.generate_embeddings(texts)


@pytest.mark.asyncio
async def test_generate_embeddings_invalid_type(openai_service):
    """Test handling of invalid input types."""
    # Send dictionary instead of string which should cause a type error
    texts = [{"text": "not a string"}]  # type: ignore
    
    with pytest.raises(EmbeddingError, match="Error generating embeddings"):
        await openai_service.generate_embeddings(texts) 