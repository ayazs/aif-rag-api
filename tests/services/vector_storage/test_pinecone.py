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
    return request.config.getoption("use_real_pinecone", default=False)

@pytest.fixture
def mock_settings():
    """Mock settings object."""
    settings = MagicMock()
    settings.get_service_config.return_value = {
        "api_key": "test-key",
        "environment": "test-env",
        "index_name": TEST_INDEX_NAME
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
def pinecone_service(mock_settings, mock_client):
    """Create PineconeService instance with mocked dependencies."""
    with patch("app.services.vector_storage.pinecone.Pinecone", return_value=mock_client):
        service = PineconeService(mock_settings)
        service.client = mock_client  # Ensure we're using the mock client
        return service

def test_init_success(pinecone_service, mock_client):
    """Test successful initialization."""
    assert isinstance(pinecone_service.client, MagicMock)
    assert pinecone_service.index_name == TEST_INDEX_NAME

def test_init_missing_config(mock_settings):
    """Test initialization with missing configuration."""
    mock_settings.get_service_config.return_value = {}
    with pytest.raises(ConfigurationError):
        PineconeService(mock_settings)

def test_create_index_success(pinecone_service, mock_client):
    """Test successful index creation."""
    pinecone_service.create_index(TEST_INDEX_NAME)
    mock_client.create_index.assert_called_once_with(
        name=TEST_INDEX_NAME,
        dimension=TEST_DIMENSION,
        metric="cosine"
    )

def test_create_index_already_exists(pinecone_service, mock_client):
    """Test index creation when index already exists."""
    mock_client.list_indexes.return_value = [TEST_INDEX_NAME]
    pinecone_service.create_index(TEST_INDEX_NAME)
    mock_client.create_index.assert_not_called()

def test_create_index_rate_limit(pinecone_service, mock_client):
    """Test index creation with rate limit error."""
    mock_client.create_index.side_effect = PineconeException("rate limit exceeded")
    with pytest.raises(RateLimitError):
        pinecone_service.create_index(TEST_INDEX_NAME)

def test_delete_index_success(pinecone_service, mock_client):
    """Test successful index deletion."""
    mock_client.list_indexes.return_value = [TEST_INDEX_NAME]
    pinecone_service.delete_index(TEST_INDEX_NAME)
    mock_client.delete_index.assert_called_once_with(TEST_INDEX_NAME)

def test_delete_index_not_found(pinecone_service, mock_client):
    """Test deleting a non-existent index."""
    mock_client.list_indexes.return_value = []
    with pytest.raises(IndexNotFoundError):
        pinecone_service.delete_index(TEST_INDEX_NAME)

def test_list_indices_success(pinecone_service, mock_client):
    """Test successful index listing."""
    expected_indices = ['index1', 'index2']
    mock_client.list_indexes.return_value = expected_indices
    result = pinecone_service.list_indices()
    assert result == expected_indices

def test_describe_index_success(pinecone_service, mock_client):
    """Test successful index description."""
    mock_client.list_indexes.return_value = [TEST_INDEX_NAME]
    result = pinecone_service.describe_index(TEST_INDEX_NAME)
    assert result == {"name": TEST_INDEX_NAME, "dimension": TEST_DIMENSION}

def test_check_index_health_success(pinecone_service, mock_client):
    """Test successful index health check."""
    mock_client.list_indexes.return_value = [TEST_INDEX_NAME]
    assert pinecone_service.check_index_health(TEST_INDEX_NAME) is True

def test_check_index_health_not_ready(pinecone_service, mock_client):
    """Test index health check when index is not ready."""
    mock_client.list_indexes.return_value = [TEST_INDEX_NAME]
    mock_client.describe_index.return_value = MagicMock(status={'ready': False})
    assert pinecone_service.check_index_health(TEST_INDEX_NAME) is False 