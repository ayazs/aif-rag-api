"""
Integration tests for the Pinecone vector storage service.
These tests use the real Pinecone client and should be run with caution.
"""

import os
import pytest
from pinecone import ServerlessSpec, PodSpec
from app.config import Settings
from app.services.vector_storage.pinecone import PineconeService
from app.services.vector_storage.exceptions import (
    IndexNotFoundError,
    IndexCreationError,
    IndexDeletionError,
    RateLimitError,
    ServiceTimeoutError
)

# Test configuration
TEST_INDEX_NAME = 'test-index-integration'
TEST_DIMENSION = 1536
TEST_METRIC = 'cosine'

@pytest.fixture
def settings():
    """Create settings instance with Pinecone configuration."""
    # Get Pinecone API key from environment
    api_key = os.getenv("SERVICE_PINECONE_API_KEY")
    if not api_key:
        pytest.skip("SERVICE_PINECONE_API_KEY not set in environment")
    
    # Get Pinecone cloud and region from environment
    cloud = os.getenv("SERVICE_PINECONE_CLOUD", "aws")  # Default to AWS if not specified
    region = os.getenv("SERVICE_PINECONE_REGION", "us-east-1")  # Default to us-east-1 if not specified
    
    # Create settings with Pinecone configuration
    return Settings(
        _env_file=None,  # Don't load from .env file
        SERVICE_PINECONE_API_KEY=api_key,
        SERVICE_PINECONE_CLOUD=cloud,
        SERVICE_PINECONE_REGION=region,
        SERVICE_PINECONE_INDEX_NAME=TEST_INDEX_NAME
    )

@pytest.fixture
def pinecone_service(settings):
    """Create PineconeService instance with real client."""
    config = settings.get_service_config("pinecone")
    return PineconeService(config)

def test_create_and_delete_index(pinecone_service):
    """Test creating and deleting an index with the real Pinecone client."""
    try:
        # Create index
        pinecone_service.create_index(
            name=TEST_INDEX_NAME,
            dimension=TEST_DIMENSION,
            metric=TEST_METRIC
        )
        
        # Verify index exists
        indices = pinecone_service.list_indices()
        assert TEST_INDEX_NAME in indices
        
        # Verify index is ready
        assert pinecone_service.check_index_health(TEST_INDEX_NAME) is True
        
        # Get index details
        index_details = pinecone_service.describe_index(TEST_INDEX_NAME)
        assert index_details['name'] == TEST_INDEX_NAME
        assert index_details['dimension'] == TEST_DIMENSION
        
    finally:
        # Clean up: delete the index
        try:
            pinecone_service.delete_index(TEST_INDEX_NAME)
        except IndexNotFoundError:
            pass  # Index might have been deleted already
        
        # Verify index is deleted
        indices = pinecone_service.list_indices()
        assert TEST_INDEX_NAME not in indices

def test_create_index_already_exists(pinecone_service):
    """Test creating an index that already exists."""
    try:
        # Create index first
        pinecone_service.create_index(
            name=TEST_INDEX_NAME,
            dimension=TEST_DIMENSION,
            metric=TEST_METRIC
        )
        
        # Try to create it again (should not raise an error)
        pinecone_service.create_index(
            name=TEST_INDEX_NAME,
            dimension=TEST_DIMENSION,
            metric=TEST_METRIC
        )
        
    finally:
        # Clean up
        try:
            pinecone_service.delete_index(TEST_INDEX_NAME)
        except IndexNotFoundError:
            pass

def test_delete_nonexistent_index(pinecone_service):
    """Test deleting an index that doesn't exist."""
    with pytest.raises(IndexNotFoundError):
        pinecone_service.delete_index('nonexistent-index')

def test_create_index_with_serverless_spec(pinecone_service):
    """Test creating an index with explicit ServerlessSpec."""
    try:
        spec = ServerlessSpec(
            cloud=pinecone_service.cloud,
            region=pinecone_service.region
        )
        
        pinecone_service.create_index(
            name=TEST_INDEX_NAME,
            dimension=TEST_DIMENSION,
            metric=TEST_METRIC,
            spec=spec
        )
        
        # Verify index exists and has correct configuration
        index_details = pinecone_service.describe_index(TEST_INDEX_NAME)
        assert index_details['name'] == TEST_INDEX_NAME
        assert index_details['dimension'] == TEST_DIMENSION
        assert index_details['metric'] == TEST_METRIC
        assert index_details['spec']['serverless']['cloud'] == pinecone_service.cloud
        assert index_details['spec']['serverless']['region'] == pinecone_service.region
        
    finally:
        try:
            pinecone_service.delete_index(TEST_INDEX_NAME)
        except IndexNotFoundError:
            pass

def test_index_health_checks(pinecone_service):
    """Test various index health check scenarios."""
    try:
        # Create index
        pinecone_service.create_index(
            name=TEST_INDEX_NAME,
            dimension=TEST_DIMENSION,
            metric=TEST_METRIC
        )
        
        # Test health check on existing index
        assert pinecone_service.check_index_health(TEST_INDEX_NAME) is True
        
        # Test health check on non-existent index
        with pytest.raises(IndexNotFoundError):
            pinecone_service.check_index_health('nonexistent-index')
            
    finally:
        try:
            pinecone_service.delete_index(TEST_INDEX_NAME)
        except IndexNotFoundError:
            pass

def test_list_indices(pinecone_service):
    """Test listing indices functionality."""
    try:
        # Create test index
        pinecone_service.create_index(
            name=TEST_INDEX_NAME,
            dimension=TEST_DIMENSION,
            metric=TEST_METRIC
        )
        
        # List indices
        indices = pinecone_service.list_indices()
        assert isinstance(indices, list)
        assert TEST_INDEX_NAME in indices
        
    finally:
        try:
            pinecone_service.delete_index(TEST_INDEX_NAME)
        except IndexNotFoundError:
            pass 