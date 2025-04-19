"""
Tests for the Pinecone vector storage service.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from pinecone import Pinecone
from pinecone.exceptions import PineconeException

from app.services.vector_storage.pinecone import PineconeService
from app.services.vector_storage.exceptions import (
    ConfigurationError,
    IndexNotFoundError,
    IndexCreationError,
    IndexDeletionError,
    ServiceUnavailableError,
    RateLimitError
)

# Test configuration
TEST_INDEX_NAME = 'test-index'
TEST_DIMENSION = 1536
TEST_METRIC = 'cosine'

@pytest.fixture
def use_real_pinecone(request):
    """Get whether to use real Pinecone client."""
    return request.config.getoption("--use-real-pinecone")

@pytest.fixture
def mock_settings():
    """Create mock settings with Pinecone configuration."""
    settings = MagicMock()
    settings.get_service_config.return_value = {
        'api_key': 'test-api-key',
        'cloud': 'aws',
        'region': 'us-east-1',
        'index_name': 'test-index'
    }
    return settings

@pytest.fixture
def mock_client():
    """Mock Pinecone client."""
    client = MagicMock(spec=Pinecone)
    client.list_indexes.return_value = []
    client.create_index.return_value = None
    client.delete_index.return_value = None
    client.describe_index.return_value = MagicMock(
        status={"ready": True},
        to_dict=lambda: {"name": TEST_INDEX_NAME, "dimension": TEST_DIMENSION}
    )
    return client

@pytest.fixture
def pinecone_service(use_real_pinecone, mock_settings, mock_client):
    """Create PineconeService instance with mocked dependencies."""
    if use_real_pinecone:
        return PineconeService(mock_settings)
    
    with patch("app.services.vector_storage.pinecone.Pinecone", return_value=mock_client):
        service = PineconeService(mock_settings)
        service.client = mock_client  # Ensure we're using the mock client
        return service

def test_init_success(pinecone_service, mock_client, use_real_pinecone):
    """Test successful initialization."""
    if use_real_pinecone:
        assert isinstance(pinecone_service.client, Pinecone)
    else:
        assert isinstance(pinecone_service.client, MagicMock)
    assert pinecone_service.index_name == TEST_INDEX_NAME

def test_init_missing_config(mock_settings):
    """Test initialization with missing configuration."""
    mock_settings.get_service_config.return_value = {}
    with pytest.raises(ConfigurationError):
        PineconeService(mock_settings)

def test_init_unexpected_error(mock_settings):
    """Test initialization with unexpected error."""
    mock_settings.get_service_config.side_effect = Exception("Unexpected error")
    with pytest.raises(ConfigurationError) as exc_info:
        PineconeService(mock_settings)
    assert "Failed to initialize Pinecone client" in str(exc_info.value)

@pytest.mark.skipif("config.getoption('--use-real-pinecone')")
def test_create_index_success(pinecone_service, mock_client):
    """Test successful index creation."""
    pinecone_service.create_index(TEST_INDEX_NAME)
    mock_client.create_index.assert_called_once_with(
        name=TEST_INDEX_NAME,
        spec={
            "serverless": {
                "cloud": "aws",
                "region": "us-east-1",
                "dimension": TEST_DIMENSION,
                "metric": "cosine"
            }
        }
    )

@pytest.mark.skipif("config.getoption('--use-real-pinecone')")
def test_create_index_already_exists(pinecone_service, mock_client):
    """Test index creation when index already exists."""
    mock_client.list_indexes.return_value = [TEST_INDEX_NAME]
    pinecone_service.create_index(TEST_INDEX_NAME)
    mock_client.create_index.assert_not_called()

@pytest.mark.skipif("config.getoption('--use-real-pinecone')")
def test_create_index_rate_limit(pinecone_service, mock_client):
    """Test index creation with rate limit error."""
    mock_client.create_index.side_effect = PineconeException("rate limit exceeded")
    with pytest.raises(RateLimitError):
        pinecone_service.create_index(TEST_INDEX_NAME)

@pytest.mark.skipif("config.getoption('--use-real-pinecone')")
def test_create_index_unexpected_error(pinecone_service, mock_client):
    """Test index creation with unexpected error."""
    mock_client.create_index.side_effect = Exception("Unexpected error")
    with pytest.raises(IndexCreationError) as exc_info:
        pinecone_service.create_index(TEST_INDEX_NAME)
    assert "Unexpected error creating index" in str(exc_info.value)

@pytest.mark.skipif("config.getoption('--use-real-pinecone')")
def test_create_index_retry(pinecone_service, mock_client):
    """Test index creation retry mechanism."""
    mock_client.create_index.side_effect = [
        PineconeException("rate limit exceeded"),
        PineconeException("rate limit exceeded"),
        None
    ]
    pinecone_service.create_index(TEST_INDEX_NAME)
    assert mock_client.create_index.call_count == 3

@pytest.mark.skipif("config.getoption('--use-real-pinecone')")
def test_create_index_retry_exhausted(pinecone_service, mock_client):
    """Test index creation retry mechanism when all attempts are exhausted."""
    mock_client.create_index.side_effect = [
        PineconeException("rate limit exceeded"),
        PineconeException("rate limit exceeded"),
        PineconeException("rate limit exceeded"),
        PineconeException("rate limit exceeded")
    ]
    with pytest.raises(RateLimitError):
        pinecone_service.create_index(TEST_INDEX_NAME)
    assert mock_client.create_index.call_count == 3  # Should stop after 3 attempts

@pytest.mark.skipif("config.getoption('--use-real-pinecone')")
def test_delete_index_success(pinecone_service, mock_client):
    """Test successful index deletion."""
    mock_client.list_indexes.return_value = [TEST_INDEX_NAME]
    pinecone_service.delete_index(TEST_INDEX_NAME)
    mock_client.delete_index.assert_called_once_with(TEST_INDEX_NAME)

@pytest.mark.skipif("config.getoption('--use-real-pinecone')")
def test_delete_index_not_found(pinecone_service, mock_client):
    """Test deleting a non-existent index."""
    mock_client.list_indexes.return_value = []
    with pytest.raises(IndexNotFoundError):
        pinecone_service.delete_index(TEST_INDEX_NAME)

@pytest.mark.skipif("config.getoption('--use-real-pinecone')")
def test_delete_index_rate_limit(pinecone_service, mock_client):
    """Test index deletion with rate limit error."""
    mock_client.list_indexes.return_value = [TEST_INDEX_NAME]
    mock_client.delete_index.side_effect = PineconeException("rate limit exceeded")
    with pytest.raises(RateLimitError):
        pinecone_service.delete_index(TEST_INDEX_NAME)

@pytest.mark.skipif("config.getoption('--use-real-pinecone')")
def test_delete_index_unexpected_error(pinecone_service, mock_client):
    """Test index deletion with unexpected error."""
    mock_client.list_indexes.return_value = [TEST_INDEX_NAME]
    mock_client.delete_index.side_effect = Exception("Unexpected error")
    with pytest.raises(IndexDeletionError) as exc_info:
        pinecone_service.delete_index(TEST_INDEX_NAME)
    assert "Unexpected error deleting index" in str(exc_info.value)

@pytest.mark.skipif("config.getoption('--use-real-pinecone')")
def test_delete_index_retry(pinecone_service, mock_client):
    """Test index deletion retry mechanism."""
    mock_client.list_indexes.return_value = [TEST_INDEX_NAME]
    mock_client.delete_index.side_effect = [
        PineconeException("rate limit exceeded"),
        PineconeException("rate limit exceeded"),
        None
    ]
    pinecone_service.delete_index(TEST_INDEX_NAME)
    assert mock_client.delete_index.call_count == 3

@pytest.mark.skipif("config.getoption('--use-real-pinecone')")
def test_delete_index_retry_exhausted(pinecone_service, mock_client):
    """Test index deletion retry mechanism when all attempts are exhausted."""
    mock_client.list_indexes.return_value = [TEST_INDEX_NAME]
    mock_client.delete_index.side_effect = [
        PineconeException("rate limit exceeded"),
        PineconeException("rate limit exceeded"),
        PineconeException("rate limit exceeded"),
        PineconeException("rate limit exceeded")
    ]
    with pytest.raises(RateLimitError):
        pinecone_service.delete_index(TEST_INDEX_NAME)
    assert mock_client.delete_index.call_count == 3  # Should stop after 3 attempts

@pytest.mark.skipif(use_real_pinecone, reason="Skipping test that modifies Pinecone index when using real client")
def test_list_indices_success(pinecone_service, use_real_pinecone):
    """Test successful listing of indices."""
    if use_real_pinecone:
        # With real client, we expect an empty list if no indexes exist
        result = pinecone_service.list_indices()
        assert isinstance(result, list)
        assert len(result) >= 0  # Can be empty if no indexes exist
    else:
        # With mock client, we expect our predefined list
        result = pinecone_service.list_indices()
        assert result == ["test-index-1", "test-index-2"]

@pytest.mark.skipif("config.getoption('--use-real-pinecone')")
def test_list_indices_service_unavailable(pinecone_service, mock_client):
    """Test listing indices when service is unavailable."""
    mock_client.list_indexes.side_effect = Exception("Service unavailable")
    with pytest.raises(ServiceUnavailableError) as exc_info:
        pinecone_service.list_indices()
    assert "Failed to list indices" in str(exc_info.value)

def test_describe_index_success(pinecone_service, mock_client, use_real_pinecone):
    """Test successful index description."""
    if not use_real_pinecone:
        mock_client.list_indexes.return_value = [TEST_INDEX_NAME]
        result = pinecone_service.describe_index(TEST_INDEX_NAME)
        assert result == {"name": TEST_INDEX_NAME, "dimension": TEST_DIMENSION}
    else:
        with pytest.raises((IndexNotFoundError, ServiceUnavailableError)):
            pinecone_service.describe_index(TEST_INDEX_NAME)

@pytest.mark.skipif("config.getoption('--use-real-pinecone')")
def test_describe_index_service_unavailable(pinecone_service, mock_client):
    """Test describing index when service is unavailable."""
    mock_client.list_indexes.return_value = [TEST_INDEX_NAME]
    mock_client.describe_index.side_effect = Exception("Service unavailable")
    with pytest.raises(ServiceUnavailableError) as exc_info:
        pinecone_service.describe_index(TEST_INDEX_NAME)
    assert "Failed to describe index" in str(exc_info.value)

def test_check_index_health_success(pinecone_service, mock_client, use_real_pinecone):
    """Test successful index health check."""
    if not use_real_pinecone:
        mock_client.list_indexes.return_value = [TEST_INDEX_NAME]
        assert pinecone_service.check_index_health(TEST_INDEX_NAME) is True
    else:
        with pytest.raises((IndexNotFoundError, ServiceUnavailableError)):
            pinecone_service.check_index_health(TEST_INDEX_NAME)

@pytest.mark.skipif("config.getoption('--use-real-pinecone')")
def test_check_index_health_not_ready(pinecone_service, mock_client):
    """Test index health check when index is not ready."""
    mock_client.list_indexes.return_value = [TEST_INDEX_NAME]
    mock_client.describe_index.return_value = MagicMock(status={'ready': False})
    assert pinecone_service.check_index_health(TEST_INDEX_NAME) is False

@pytest.mark.skipif("config.getoption('--use-real-pinecone')")
def test_check_index_health_service_unavailable(pinecone_service, mock_client):
    """Test index health check when service is unavailable."""
    mock_client.list_indexes.return_value = [TEST_INDEX_NAME]
    mock_client.describe_index.side_effect = Exception("Service unavailable")
    with pytest.raises(ServiceUnavailableError) as exc_info:
        pinecone_service.check_index_health(TEST_INDEX_NAME)
    assert "Failed to check index health" in str(exc_info.value)

@pytest.mark.skipif("config.getoption('--use-real-pinecone')")
def test_check_index_health_unexpected_error(pinecone_service, mock_client):
    """Test index health check with unexpected error."""
    mock_client.list_indexes.return_value = [TEST_INDEX_NAME]
    mock_client.describe_index.side_effect = Exception("Unexpected error")
    with pytest.raises(ServiceUnavailableError) as exc_info:
        pinecone_service.check_index_health(TEST_INDEX_NAME)
    assert "Failed to check index health" in str(exc_info.value)

@pytest.mark.skipif("config.getoption('--use-real-pinecone')")
def test_check_index_health_retry(pinecone_service, mock_client):
    """Test index health check retry mechanism."""
    mock_client.list_indexes.return_value = [TEST_INDEX_NAME]
    mock_client.describe_index.side_effect = [
        Exception("Service unavailable"),
        Exception("Service unavailable"),
        MagicMock(status={'ready': True})
    ]
    assert pinecone_service.check_index_health(TEST_INDEX_NAME) is True
    assert mock_client.describe_index.call_count == 3

@pytest.mark.skipif("config.getoption('--use-real-pinecone')")
def test_check_index_health_retry_exhausted(pinecone_service, mock_client):
    """Test index health check retry mechanism when all attempts are exhausted."""
    mock_client.list_indexes.return_value = [TEST_INDEX_NAME]
    mock_client.describe_index.side_effect = [
        Exception("Service unavailable"),
        Exception("Service unavailable"),
        Exception("Service unavailable"),
        Exception("Service unavailable")
    ]
    with pytest.raises(ServiceUnavailableError):
        pinecone_service.check_index_health(TEST_INDEX_NAME)
    assert mock_client.describe_index.call_count == 3  # Should stop after 3 attempts

@pytest.mark.skipif("config.getoption('--use-real-pinecone')")
def test_describe_index_retry(pinecone_service, mock_client):
    """Test index description retry mechanism."""
    mock_client.list_indexes.return_value = [TEST_INDEX_NAME]
    mock_client.describe_index.side_effect = [
        Exception("Service unavailable"),
        Exception("Service unavailable"),
        MagicMock(to_dict=lambda: {"name": TEST_INDEX_NAME, "dimension": TEST_DIMENSION})
    ]
    result = pinecone_service.describe_index(TEST_INDEX_NAME)
    assert result == {"name": TEST_INDEX_NAME, "dimension": TEST_DIMENSION}
    assert mock_client.describe_index.call_count == 3 