"""Tests for OpenAI service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
from openai import AsyncOpenAI, RateLimitError, AuthenticationError, APIError
from openai.types.create_embedding_response import CreateEmbeddingResponse
from openai.types.embedding import Embedding
from tenacity import RetryError

from app.config import Settings
from app.services.openai.openai import OpenAIService
from app.services.openai.exceptions import (
    EmbeddingError,
    RateLimitError as CustomRateLimitError,
    AuthenticationError as CustomAuthError,
    ServiceUnavailableError
)


@pytest.fixture
def mock_settings():
    """Create mock settings."""
    settings = MagicMock(spec=Settings)
    settings.get_service_config.return_value = {
        'api_key': 'test-key',
        'embedding_model': 'text-embedding-3-small'
    }
    return settings


@pytest.fixture
def mock_openai_client():
    """Create mock OpenAI client."""
    with patch('openai.AsyncOpenAI', autospec=True) as mock:
        client = AsyncMock(spec=AsyncOpenAI)
        embeddings = AsyncMock()
        client.embeddings = embeddings
        mock.return_value = client
        yield client


@pytest.fixture
def mock_http_response():
    """Create a mock HTTP response."""
    response = MagicMock(spec=httpx.Response)
    response.status_code = 429
    response.headers = {
        "x-request-id": "test-request-id",
        "openai-organization": "test-org",
        "openai-version": "2020-10-01"
    }
    response.request = MagicMock(spec=httpx.Request)
    response.request.method = "POST"
    response.request.url = "https://api.openai.com/v1/embeddings"
    response.request.headers = {}
    return response


@pytest.mark.asyncio
async def test_init_success(mock_settings, mock_openai_client):
    """Test successful initialization."""
    service = OpenAIService(mock_settings)
    assert isinstance(service.client, AsyncMock)
    assert service.embedding_model == 'text-embedding-3-small'
    assert service.api_key == 'test-key'


@pytest.mark.asyncio
async def test_init_missing_config():
    """Test initialization with missing config."""
    settings = MagicMock(spec=Settings)
    settings.get_service_config.return_value = None
    
    with pytest.raises(ValueError, match="OpenAI API key is required"):
        OpenAIService(settings)


@pytest.mark.asyncio
async def test_generate_embeddings_success(mock_settings, mock_openai_client):
    """Test successful embedding generation."""
    # Setup mock response
    mock_embeddings = [
        Embedding(embedding=[0.1, 0.2, 0.3], index=0, object="embedding"),
        Embedding(embedding=[0.4, 0.5, 0.6], index=1, object="embedding")
    ]
    mock_response = CreateEmbeddingResponse(
        data=mock_embeddings,
        model="text-embedding-3-small",
        object="list",
        usage={"prompt_tokens": 10, "total_tokens": 10}
    )
    mock_openai_client.embeddings.create.return_value = mock_response
    
    # Test
    service = OpenAIService(mock_settings)
    texts = ["test text 1", "test text 2"]
    embeddings = await service.generate_embeddings(texts)
    
    # Verify
    assert len(embeddings) == 2
    assert embeddings[0] == [0.1, 0.2, 0.3]
    assert embeddings[1] == [0.4, 0.5, 0.6]
    mock_openai_client.embeddings.create.assert_called_once_with(
        model='text-embedding-3-small',
        input=texts
    )


@pytest.mark.asyncio
async def test_generate_embeddings_rate_limit(mock_settings, mock_openai_client, mock_http_response):
    """Test rate limit error handling."""
    mock_http_response.status_code = 429
    error = RateLimitError(
        message="Rate limit exceeded",
        response=mock_http_response,
        body={"error": {"message": "Rate limit exceeded", "type": "rate_limit_error"}}
    )
    mock_openai_client.embeddings.create.side_effect = error
    
    service = OpenAIService(mock_settings)
    with pytest.raises(CustomRateLimitError, match="OpenAI rate limit exceeded"):
        await service.generate_embeddings(["test"])


@pytest.mark.asyncio
async def test_generate_embeddings_auth_error(mock_settings, mock_openai_client, mock_http_response):
    """Test authentication error handling."""
    mock_http_response.status_code = 401
    error = AuthenticationError(
        message="Invalid API key",
        response=mock_http_response,
        body={"error": {"message": "Invalid API key", "type": "invalid_request_error"}}
    )
    mock_openai_client.embeddings.create.side_effect = error
    
    service = OpenAIService(mock_settings)
    with pytest.raises(CustomAuthError, match="Invalid OpenAI API key"):
        await service.generate_embeddings(["test"])


@pytest.mark.asyncio
async def test_generate_embeddings_service_unavailable(mock_settings, mock_openai_client, mock_http_response):
    """Test service unavailable error handling."""
    mock_http_response.status_code = 503
    error = APIError(
        message="service_unavailable: The server is temporarily unavailable",
        request=mock_http_response.request,
        body={"error": {"message": "service_unavailable", "type": "service_unavailable"}}
    )
    # Set up the mock to always return the service unavailable error
    mock_openai_client.embeddings.create.side_effect = error
    
    service = OpenAIService(mock_settings)
    # The service will retry 3 times and then give up with a RetryError
    with pytest.raises(RetryError) as exc_info:
        await service.generate_embeddings(["test"])
    
    # Verify that the underlying error is ServiceUnavailableError
    assert isinstance(exc_info.value.last_attempt.exception(), ServiceUnavailableError)
    assert str(exc_info.value.last_attempt.exception()) == "OpenAI service is temporarily unavailable"
    # Verify that the service attempted 3 retries
    assert mock_openai_client.embeddings.create.call_count == 3


@pytest.mark.asyncio
async def test_generate_embeddings_unexpected_error(mock_settings, mock_openai_client):
    """Test unexpected error handling."""
    mock_openai_client.embeddings.create.side_effect = ValueError("Unexpected error")
    
    service = OpenAIService(mock_settings)
    with pytest.raises(EmbeddingError, match="Unexpected error generating embeddings"):
        await service.generate_embeddings(["test"])


@pytest.mark.asyncio
async def test_generate_embeddings_batch_processing(mock_settings, mock_openai_client):
    """Test batch processing of embeddings."""
    texts = ["text1", "text2", "text3"]
    
    # Setup mock responses for each batch
    responses = [
        CreateEmbeddingResponse(
            data=[
                Embedding(embedding=[0.1, 0.2], index=0, object="embedding"),
                Embedding(embedding=[0.3, 0.4], index=1, object="embedding")
            ],
            model="text-embedding-3-small",
            object="list",
            usage={"prompt_tokens": 8, "total_tokens": 8}
        ),
        CreateEmbeddingResponse(
            data=[
                Embedding(embedding=[0.5, 0.6], index=0, object="embedding")
            ],
            model="text-embedding-3-small",
            object="list",
            usage={"prompt_tokens": 4, "total_tokens": 4}
        )
    ]
    
    mock_openai_client.embeddings.create.side_effect = responses
    
    # Test with batch_size=2
    service = OpenAIService(mock_settings)
    embeddings = await service.generate_embeddings(texts, batch_size=2)
    
    # Verify results
    assert len(embeddings) == 3
    assert embeddings[0] == [0.1, 0.2]
    assert embeddings[1] == [0.3, 0.4]
    assert embeddings[2] == [0.5, 0.6]
    
    # Verify API calls
    assert mock_openai_client.embeddings.create.call_count == 2
    mock_openai_client.embeddings.create.assert_any_call(
        model='text-embedding-3-small',
        input=["text1", "text2"]
    )
    mock_openai_client.embeddings.create.assert_any_call(
        model='text-embedding-3-small',
        input=["text3"]
    ) 