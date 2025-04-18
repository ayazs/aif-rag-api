"""
Pinecone vector storage service implementation.
"""

import time
import logging
from typing import List, Optional
import pinecone
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings
from app.services.vector_storage.exceptions import (
    VectorStorageError,
    IndexNotFoundError,
    IndexCreationError,
    IndexDeletionError,
    ServiceUnavailableError,
    RateLimitError,
    ConfigurationError
)

logger = logging.getLogger(__name__)

class PineconeService:
    """Service for interacting with Pinecone vector database."""
    
    def __init__(self):
        """Initialize the Pinecone service."""
        try:
            config = settings.get_service_config('pinecone')
            pinecone.init(
                api_key=config['api_key'],
                environment=config['environment']
            )
            self.client = pinecone
            self.index_name = config.get('index_name', 'aif-rag-index')
        except KeyError as e:
            raise ConfigurationError(f"Missing required Pinecone configuration: {str(e)}")
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize Pinecone client: {str(e)}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def create_index(self, name: Optional[str] = None, dimension: Optional[int] = None, metric: Optional[str] = None) -> None:
        """Create a new Pinecone index.
        
        Args:
            name: Name of the index to create (defaults to configured index name)
            dimension: Dimension of vectors (defaults to 1536 for OpenAI embeddings)
            metric: Similarity metric (defaults to "cosine")
            
        Raises:
            IndexCreationError: If index creation fails
            RateLimitError: If API rate limits are exceeded
        """
        try:
            name = name or self.index_name
            dimension = dimension or 1536  # Default dimension for OpenAI embeddings
            metric = metric or "cosine"  # Default metric for semantic search
            
            if name in self.client.list_indexes():
                logger.info(f"Index {name} already exists")
                return
                
            self.client.create_index(
                name=name,
                dimension=dimension,
                metric=metric
            )
            
            # Wait for index to be ready
            while not self.client.describe_index(name).status['ready']:
                time.sleep(1)
                
            logger.info(f"Created index {name} with dimension {dimension} and metric {metric}")
            
        except pinecone.exceptions.PineconeException as e:
            if "rate limit" in str(e).lower():
                raise RateLimitError(f"Rate limit exceeded: {str(e)}")
            raise IndexCreationError(f"Failed to create index: {str(e)}")
        except Exception as e:
            raise IndexCreationError(f"Unexpected error creating index: {str(e)}")
    
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
            if name not in self.client.list_indexes():
                raise IndexNotFoundError(f"Index {name} does not exist")
                
            self.client.delete_index(name)
            logger.info(f"Deleted index {name}")
            
        except pinecone.exceptions.PineconeException as e:
            if "rate limit" in str(e).lower():
                raise RateLimitError(f"Rate limit exceeded: {str(e)}")
            raise IndexDeletionError(f"Failed to delete index: {str(e)}")
        except Exception as e:
            raise IndexDeletionError(f"Unexpected error deleting index: {str(e)}")
    
    def list_indices(self) -> List[str]:
        """List all available indices.
        
        Returns:
            List of index names
            
        Raises:
            ServiceUnavailableError: If service is unavailable
        """
        try:
            return self.client.list_indexes()
        except Exception as e:
            raise ServiceUnavailableError(f"Failed to list indices: {str(e)}")
    
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
            if name not in self.client.list_indexes():
                raise IndexNotFoundError(f"Index {name} does not exist")
                
            return self.client.describe_index(name).to_dict()
        except IndexNotFoundError:
            raise
        except Exception as e:
            raise ServiceUnavailableError(f"Failed to describe index: {str(e)}")
    
    def check_index_health(self, name: str) -> bool:
        """Check if index is ready and healthy.
        
        Args:
            name: Name of the index
            
        Returns:
            True if index is ready and healthy, False otherwise
            
        Raises:
            IndexNotFoundError: If index does not exist
            ServiceUnavailableError: If service is unavailable
        """
        try:
            if name not in self.client.list_indexes():
                raise IndexNotFoundError(f"Index {name} does not exist")
                
            index = self.client.describe_index(name)
            return index.status['ready']
        except IndexNotFoundError:
            raise
        except Exception as e:
            raise ServiceUnavailableError(f"Failed to check index health: {str(e)}") 