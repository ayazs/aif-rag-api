from typing import List, Dict, Any, Optional
from app.services.document_processing.processors.text import TextProcessor
from app.services.document_processing.exceptions import DocumentProcessingError
from app.services.openai.openai import OpenAIService
from app.config import settings

class DocumentService:
    """Service for processing documents and generating embeddings."""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        openai_service: Optional[OpenAIService] = None,
        vector_store: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the document service.
        
        Args:
            chunk_size: Size of text chunks in characters
            chunk_overlap: Number of characters to overlap between chunks
            openai_service: Optional OpenAI service instance for embeddings
            vector_store: Optional vector store service
            config: Optional configuration dictionary
        """
        # Use provided config or defaults
        if config:
            chunk_size = config.get('chunk_size', chunk_size)
            chunk_overlap = config.get('chunk_overlap', chunk_overlap)
        
        self.text_processor = TextProcessor(chunk_size, chunk_overlap)
        self.embedding_service = openai_service or OpenAIService(settings=settings)
        self.vector_store = vector_store
    
    def process_document(self, text: str) -> List[Dict[str, Any]]:
        """
        Process a document by splitting it into chunks and generating embeddings.
        
        Args:
            text: The document text to process
            
        Returns:
            List of dictionaries containing chunk text and embeddings
            
        Raises:
            DocumentProcessingError: If processing fails
        """
        try:
            # Split text into chunks
            chunks = self.text_processor.split_text(text)
            
            # Generate embeddings for each chunk
            texts = [chunk["text"] for chunk in chunks]
            embeddings = self.embedding_service.generate_embeddings(texts)
            
            # Combine chunks with their embeddings
            for chunk, embedding in zip(chunks, embeddings):
                chunk["embedding"] = embedding
            
            return chunks
            
        except Exception as e:
            raise DocumentProcessingError(
                f"Failed to process document: {str(e)}",
                original_error=e
            ) 