"""
Pinecone vector storage service implementation.

This module provides a service layer for interacting with Pinecone vector database,
implementing common operations like index management and health checks.
"""

import time
import logging
from pinecone import Pinecone, ServerlessSpec, PodSpec, Index
from typing import List, Optional, Dict, Any, Union
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.services.vector_storage.exceptions import (
    IndexCreationError,
    IndexDeletionError,
    IndexNotFoundError,
    ServiceUnavailableError,
    RateLimitError,
    ConfigurationError,
    ServiceTimeoutError,
    UnexpectedError,
)

logger = logging.getLogger(__name__)

class PineconeService:
    """Service for interacting with Pinecone vector database."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Pinecone service with configuration.
        
        Args:
            config: Dictionary containing Pinecone configuration
                   Required keys: api_key
                   Optional keys: cloud, region, index_name
        """
        if not config.get("api_key"):
            raise ValueError("Pinecone API key is required")
            
        # Initialize Pinecone client
        self.client = Pinecone(api_key=config["api_key"])
        
        # Store configuration
        self.cloud = config.get("cloud", "aws")
        self.region = config.get("region", "us-east-1")
        self.index_name = config.get("index_name")
        
    @retry(
        retry=retry_if_exception_type((RateLimitError, ServiceTimeoutError)),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        stop=stop_after_attempt(5)
    )
    def create_index(
        self,
        name: Optional[str] = None,
        dimension: int = 1536,
        metric: str = "cosine",
        spec: Optional[Union[ServerlessSpec, PodSpec]] = None
    ) -> None:
        """Create a new Pinecone index.
        
        Args:
            name: Name of the index to create. If not provided, uses the configured index_name
            dimension: Dimension of vectors to store in the index (default: 1536 for OpenAI embeddings)
            metric: Distance metric to use (default: cosine)
            spec: Optional index specification (ServerlessSpec or PodSpec)
            
        Raises:
            IndexCreationError: If index creation fails
            RateLimitError: If rate limit is exceeded
            ServiceTimeoutError: If service times out
        """
        try:
            index_name = name or self.index_name
            if not index_name:
                raise ValueError("Index name must be provided either in config or as parameter")
                
            # Check if index already exists
            if index_name in [index.name for index in self.client.list_indexes()]:
                logger.info(f"Index {index_name} already exists")
                return
                
            # Create index with serverless spec if not provided
            if spec is None:
                spec = ServerlessSpec(
                    cloud=self.cloud,
                    region=self.region
                )
                
            self.client.create_index(
                name=index_name,
                dimension=dimension,
                metric=metric,
                spec=spec
            )
            
            # Wait for index to be ready
            while not self._is_index_ready(index_name):
                time.sleep(5)
                
            logger.info(f"Successfully created index {index_name}")
            
        except Exception as e:
            if "already exists" in str(e).lower():
                logger.info(f"Index {index_name} already exists")
                return
            elif "rate limit" in str(e).lower():
                raise RateLimitError(f"Rate limit exceeded while creating index: {str(e)}")
            elif "timeout" in str(e).lower():
                raise ServiceTimeoutError(f"Service timeout while creating index: {str(e)}")
            else:
                raise IndexCreationError(f"Failed to create index: {str(e)}")
                
    def _is_index_ready(self, index_name: str) -> bool:
        """Check if index is ready by describing it."""
        try:
            index = self.client.describe_index(index_name)
            return index.status.get("ready", False)
        except Exception as e:
            logger.warning(f"Error checking index status: {str(e)}")
            return False
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def delete_index(self, name: str) -> None:
        """Delete an existing index.
        
        Args:
            name: Name of the index to delete
            
        Raises:
            IndexNotFoundError: If index does not exist
            IndexDeletionError: If index deletion fails
            RateLimitError: If API rate limits are exceeded
        """
        try:
            if name not in [index.name for index in self.client.list_indexes()]:
                raise IndexNotFoundError(f"Index {name} does not exist")
                
            self.client.delete_index(name)
            logger.info(f"Deleted index {name}")
            
        except IndexNotFoundError:
            raise
        except Exception as e:
            if "rate limit" in str(e).lower():
                raise RateLimitError(f"Rate limit exceeded: {str(e)}")
            else:
                raise IndexDeletionError(f"Failed to delete index: {str(e)}")
    
    def list_indices(self) -> List[str]:
        """List all available indices.
        
        Returns:
            List of index names
            
        Raises:
            ServiceUnavailableError: If service is unavailable
        """
        try:
            return [index.name for index in self.client.list_indexes()]
        except Exception as e:
            raise ServiceUnavailableError(f"Failed to list indices: {str(e)}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def describe_index(self, name: str) -> dict:
        """Get index configuration and stats.
        
        Args:
            name: Name of the index
            
        Returns:
            Dictionary containing index configuration and stats
            
        Raises:
            IndexNotFoundError: If index does not exist
            ServiceUnavailableError: If service is unavailable
        """
        try:
            if name not in [index.name for index in self.client.list_indexes()]:
                raise IndexNotFoundError(f"Index {name} does not exist")
                
            return self.client.describe_index(name).to_dict()
        except Exception as e:
            if "not found" in str(e).lower():
                raise IndexNotFoundError(f"Index {name} does not exist")
            else:
                raise ServiceUnavailableError(f"Failed to describe index: {str(e)}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def check_index_health(self, name: str) -> bool:
        """Check if an index is ready and healthy.
        
        Args:
            name: Name of the index
            
        Returns:
            True if index is ready and healthy, False otherwise
            
        Raises:
            IndexNotFoundError: If index does not exist
            ServiceUnavailableError: If service is unavailable
        """
        try:
            if name not in [index.name for index in self.client.list_indexes()]:
                raise IndexNotFoundError(f"Index {name} does not exist")
                
            index = self.client.describe_index(name)
            return index.status.get("ready", False)
        except IndexNotFoundError:
            raise
        except Exception as e:
            raise ServiceUnavailableError(f"Failed to check index health: {str(e)}") 