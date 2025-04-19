"""
Unit tests for the Pinecone vector storage service.
"""

import pytest
from unittest.mock import MagicMock, patch
from pinecone import Pinecone, ServerlessSpec
from app.services.vector_storage.pinecone import PineconeService
from app.services.vector_storage.exceptions import (
    IndexNotFoundError,
    IndexCreationError,
    IndexDeletionError,
    RateLimitError,
    ServiceUnavailableError,
    ConfigurationError
)
import tenacity

# Test configuration
TEST_INDEX_NAME = 'test-index'
TEST_DIMENSION = 1536
TEST_METRIC = 'cosine'

@pytest.fixture
def mock_client():
    """Create a mock Pinecone client."""
    mock = MagicMock(spec=Pinecone)
    
    # Create mock index objects
    mock_index = MagicMock()
    mock_index.name = TEST_INDEX_NAME
    mock_index.dimension = TEST_DIMENSION
    mock_index.metric = TEST_METRIC
    mock_index.status = {"ready": True}
    mock_index.to_dict.return_value = {
        "name": TEST_INDEX_NAME,
        "dimension": TEST_DIMENSION,
        "metric": TEST_METRIC,
        "status": {"ready": True}
    }
    
    # Configure mock methods
    mock.list_indexes.return_value = [mock_index]
    mock.describe_index.return_value = mock_index
    mock.create_index.return_value = None
    mock.delete_index.return_value = None
    
    return mock

@pytest.fixture
def pinecone_service(mock_client):
    """Create PineconeService instance with mock client."""
    with patch('app.services.vector_storage.pinecone.Pinecone', return_value=mock_client):
        service = PineconeService({
            "api_key": "test-key",
            "index_name": TEST_INDEX_NAME,
            "cloud": "aws",
            "region": "us-east-1"
        })
        return service

def test_init_success(pinecone_service, mock_client):
    """Test successful initialization."""
    assert pinecone_service.client == mock_client
    assert pinecone_service.index_name == TEST_INDEX_NAME

def test_init_missing_config():
    """Test initialization with missing configuration."""
    with pytest.raises(ConfigurationError) as exc_info:
        PineconeService({})
    assert "Pinecone API key is required" in str(exc_info.value)

def test_init_unexpected_error():
    """Test initialization with unexpected error."""
    with pytest.raises(ConfigurationError) as exc_info:
        PineconeService({"api_key": None})
    assert "Failed to initialize Pinecone service" in str(exc_info.value)

def test_create_index_success(pinecone_service, mock_client):
    """Test successful index creation."""
    # Reset list_indexes to return empty list first
    mock_client.list_indexes.side_effect = [[], [MagicMock(name=TEST_INDEX_NAME)]]
    
    pinecone_service.create_index(
        name=TEST_INDEX_NAME,
        dimension=TEST_DIMENSION,
        metric=TEST_METRIC
    )
    
    mock_client.create_index.assert_called_once_with(
        name=TEST_INDEX_NAME,
        dimension=TEST_DIMENSION,
        metric=TEST_METRIC,
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

def test_create_index_already_exists(pinecone_service, mock_client):
    """Test creating an index that already exists."""
    mock_client.create_index.side_effect = Exception("Index already exists")
    pinecone_service.create_index(
        name=TEST_INDEX_NAME,
        dimension=TEST_DIMENSION,
        metric=TEST_METRIC
    )
    # Should not raise an error

def test_create_index_rate_limit(pinecone_service, mock_client):
    """Test index creation with rate limit error."""
    # Reset list_indexes to return empty list
    mock_client.list_indexes.return_value = []
    # Set up create_index to always raise rate limit error
    mock_client.create_index.side_effect = [
        Exception("rate limit exceeded"),
        Exception("rate limit exceeded"),
        Exception("rate limit exceeded"),
        Exception("rate limit exceeded"),
        Exception("rate limit exceeded")
    ]
    
    with pytest.raises(tenacity.RetryError) as exc_info:
        pinecone_service.create_index(
            name=TEST_INDEX_NAME,
            dimension=TEST_DIMENSION,
            metric=TEST_METRIC
        )
    
    # Verify that create_index was called the maximum number of times
    assert mock_client.create_index.call_count == 5
    # Verify that the underlying error was a RateLimitError
    assert isinstance(exc_info.value.last_attempt.exception(), RateLimitError)
    assert "Rate limit exceeded" in str(exc_info.value.last_attempt.exception())

def test_create_index_unexpected_error(pinecone_service, mock_client):
    """Test index creation with unexpected error."""
    # Reset list_indexes to return empty list
    mock_client.list_indexes.return_value = []
    mock_client.create_index.side_effect = Exception("Unexpected error")
    with pytest.raises(IndexCreationError) as exc_info:
        pinecone_service.create_index(
            name=TEST_INDEX_NAME,
            dimension=TEST_DIMENSION,
            metric=TEST_METRIC
        )
    assert "Failed to create index" in str(exc_info.value)

def test_delete_index_success(pinecone_service, mock_client):
    """Test successful index deletion."""
    pinecone_service.delete_index(TEST_INDEX_NAME)
    mock_client.delete_index.assert_called_once_with(TEST_INDEX_NAME)

def test_delete_index_rate_limit(pinecone_service, mock_client):
    """Test index deletion with rate limit error."""
    mock_client.delete_index.side_effect = Exception("rate limit exceeded")
    with pytest.raises(RateLimitError):
        pinecone_service.delete_index(TEST_INDEX_NAME)

def test_delete_index_unexpected_error(pinecone_service, mock_client):
    """Test index deletion with unexpected error."""
    mock_client.delete_index.side_effect = Exception("Unexpected error")
    with pytest.raises(IndexDeletionError) as exc_info:
        pinecone_service.delete_index(TEST_INDEX_NAME)
    assert "Unexpected error" in str(exc_info.value)

def test_delete_index_retry(pinecone_service, mock_client):
    """Test index deletion retry mechanism."""
    mock_client.delete_index.side_effect = [
        Exception("rate limit exceeded"),
        Exception("rate limit exceeded"),
        None
    ]
    pinecone_service.delete_index(TEST_INDEX_NAME)
    assert mock_client.delete_index.call_count == 3

def test_delete_index_retry_exhausted(pinecone_service, mock_client):
    """Test index deletion retry mechanism when all attempts are exhausted."""
    mock_client.delete_index.side_effect = [
        Exception("rate limit exceeded"),
        Exception("rate limit exceeded"),
        Exception("rate limit exceeded"),
        Exception("rate limit exceeded")
    ]
    with pytest.raises(RateLimitError):
        pinecone_service.delete_index(TEST_INDEX_NAME)
    assert mock_client.delete_index.call_count == 3  # Should stop after 3 attempts

def test_describe_index_success(pinecone_service, mock_client):
    """Test successful index description."""
    result = pinecone_service.describe_index(TEST_INDEX_NAME)
    assert result == {
        "name": TEST_INDEX_NAME,
        "dimension": TEST_DIMENSION,
        "metric": TEST_METRIC,
        "status": {"ready": True}
    }

def test_check_index_health_success(pinecone_service, mock_client):
    """Test successful index health check."""
    assert pinecone_service.check_index_health(TEST_INDEX_NAME) is True

def test_check_index_health_not_ready(pinecone_service, mock_client):
    """Test index health check when index is not ready."""
    mock_index = MagicMock()
    mock_index.status = {"ready": False}
    mock_client.describe_index.return_value = mock_index
    assert pinecone_service.check_index_health(TEST_INDEX_NAME) is False

def test_check_index_health_retry(pinecone_service, mock_client):
    """Test index health check retry mechanism."""
    mock_client.describe_index.side_effect = [
        Exception("Service unavailable"),
        Exception("Service unavailable"),
        MagicMock(status={"ready": True})
    ]
    assert pinecone_service.check_index_health(TEST_INDEX_NAME) is True

def test_check_index_health_retry_exhausted(pinecone_service, mock_client):
    """Test index health check retry mechanism when all attempts are exhausted."""
    mock_client.describe_index.side_effect = [
        Exception("Service unavailable"),
        Exception("Service unavailable"),
        Exception("Service unavailable"),
        Exception("Service unavailable")
    ]
    with pytest.raises(ServiceUnavailableError):
        pinecone_service.check_index_health(TEST_INDEX_NAME)
    assert mock_client.describe_index.call_count == 3  # Should stop after 3 attempts

def test_describe_index_retry(pinecone_service, mock_client):
    """Test index description retry mechanism."""
    mock_client.describe_index.side_effect = [
        Exception("Service unavailable"),
        Exception("Service unavailable"),
        MagicMock(to_dict=lambda: {
            "name": TEST_INDEX_NAME,
            "dimension": TEST_DIMENSION,
            "metric": TEST_METRIC,
            "status": {"ready": True}
        })
    ]
    result = pinecone_service.describe_index(TEST_INDEX_NAME)
    assert result == {
        "name": TEST_INDEX_NAME,
        "dimension": TEST_DIMENSION,
        "metric": TEST_METRIC,
        "status": {"ready": True}
    }

def test_list_indices_service_unavailable(pinecone_service, mock_client):
    """Test listing indices when service is unavailable."""
    mock_client.list_indexes.side_effect = Exception("Service unavailable")
    with pytest.raises(ServiceUnavailableError) as exc_info:
        pinecone_service.list_indices()
    assert "Failed to list indices" in str(exc_info.value)

def test_describe_index_service_unavailable(pinecone_service, mock_client):
    """Test describing index when service is unavailable."""
    mock_client.describe_index.side_effect = Exception("Service unavailable")
    with pytest.raises(ServiceUnavailableError) as exc_info:
        pinecone_service.describe_index(TEST_INDEX_NAME)
    assert "Failed to describe index" in str(exc_info.value)

def test_check_index_health_service_unavailable(pinecone_service, mock_client):
    """Test index health check when service is unavailable."""
    mock_client.describe_index.side_effect = Exception("Service unavailable")
    with pytest.raises(ServiceUnavailableError) as exc_info:
        pinecone_service.check_index_health(TEST_INDEX_NAME)
    assert "Failed to check index health" in str(exc_info.value)

def test_check_index_health_unexpected_error(pinecone_service, mock_client):
    """Test index health check with unexpected error."""
    mock_client.describe_index.side_effect = Exception("Unexpected error")
    with pytest.raises(ServiceUnavailableError) as exc_info:
        pinecone_service.check_index_health(TEST_INDEX_NAME)
    assert "Unexpected error" in str(exc_info.value) 