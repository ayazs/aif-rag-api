"""OpenAI service implementation."""

from typing import List
import openai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import Settings
from app.services.openai.exceptions import (
    EmbeddingError,
    RateLimitError,
    AuthenticationError,
    ServiceUnavailableError
)


class OpenAIService:
    """Service for interacting with OpenAI's API."""

    def __init__(self, settings: Settings):
        """Initialize the OpenAI service.
        
        Args:
            settings: Application settings containing OpenAI configuration
        """
        openai_config = settings.get_service_config('openai')
        
        if not openai_config or not openai_config.get('api_key'):
            raise ValueError("OpenAI API key is required")
            
        self.api_key = openai_config['api_key']
        self.embedding_model = openai_config.get('embedding_model', 'text-embedding-3-small')
        self.client = openai.AsyncOpenAI(api_key=self.api_key)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(ServiceUnavailableError)
    )
    async def generate_embeddings(
        self,
        texts: List[str],
        batch_size: int = 100
    ) -> List[List[float]]:
        """Generate embeddings for a list of texts.
        
        Args:
            texts: List of texts to generate embeddings for
            batch_size: Number of texts to process in each batch
            
        Returns:
            List of embedding vectors
            
        Raises:
            EmbeddingError: If there's an error generating embeddings
            RateLimitError: If OpenAI's rate limit is exceeded
            AuthenticationError: If there's an authentication error
            ServiceUnavailableError: If the service is temporarily unavailable
        """
        if not texts:
            raise ValueError("Input texts cannot be empty")

        try:
            all_embeddings = []
            
            # Process texts in batches
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                try:
                    response = await self.client.embeddings.create(
                        model=self.embedding_model,
                        input=batch
                    )
                    
                    batch_embeddings = [item.embedding for item in response.data]
                    all_embeddings.extend(batch_embeddings)
                    
                except openai.RateLimitError:
                    raise RateLimitError("OpenAI rate limit exceeded")
                except openai.AuthenticationError:
                    raise AuthenticationError("Invalid OpenAI API key")
                except openai.APIError as e:
                    if "service_unavailable" in str(e).lower():
                        raise ServiceUnavailableError("OpenAI service is temporarily unavailable")
                    raise EmbeddingError(f"Error generating embeddings: {str(e)}")
                    
            return all_embeddings
            
        except Exception as e:
            if not isinstance(e, (RateLimitError, AuthenticationError, ServiceUnavailableError, EmbeddingError)):
                raise EmbeddingError(f"Unexpected error generating embeddings: {str(e)}")
            raise 