"""
Tests for the document service implementation.
"""

import pytest
from unittest.mock import MagicMock, patch
from app.services.document_processing.document_service import DocumentService
from app.services.document_processing.exceptions import DocumentProcessingError

@pytest.fixture
def mock_openai_service():
    """Create a mock OpenAI service."""
    service = MagicMock()
    service.generate_embeddings.return_value = [[0.1, 0.2, 0.3]]  # Mock embedding
    return service

@pytest.fixture
def document_service(mock_openai_service):
    """Create a document service instance with mocked dependencies."""
    return DocumentService(
        openai_service=mock_openai_service,
        config={
            'chunk_size': 100,
            'chunk_overlap': 20
        }
    )

def test_process_document_success(document_service):
    """Test successful document processing."""
    text = "This is a test document."
    
    result = document_service.process_document(text)
    
    assert len(result) > 0
    assert isinstance(result[0], dict)
    assert "text" in result[0]
    assert "embedding" in result[0]
    assert "start" in result[0]
    assert "end" in result[0]
    assert "index" in result[0]
    assert result[0]["text"] == text  # Since it's a short text, it should be a single chunk

def test_process_document_empty(document_service):
    """Test processing empty document."""
    text = ""
    result = document_service.process_document(text)
    
    assert len(result) == 1
    assert result[0]["text"] == ""
    assert result[0]["embedding"] == [0.1, 0.2, 0.3]

def test_process_document_large(document_service, mock_openai_service):
    """Test processing large document."""
    text = "This is a test. " * 50  # Create a large document
    mock_openai_service.generate_embeddings.return_value = [[0.1, 0.2, 0.3]] * 10  # Multiple embeddings
    
    result = document_service.process_document(text)
    
    assert len(result) > 1  # Should be split into multiple chunks
    for chunk in result:
        assert isinstance(chunk["text"], str)
        assert isinstance(chunk["embedding"], list)
        assert isinstance(chunk["start"], int)
        assert isinstance(chunk["end"], int)
        assert isinstance(chunk["index"], int)
        assert len(chunk["text"]) <= document_service.text_processor.chunk_size

def test_process_document_text_processor_error(document_service):
    """Test handling of text processor errors."""
    with patch.object(document_service.text_processor, 'split_text') as mock_split:
        mock_split.side_effect = Exception("Text processing failed")
        
        with pytest.raises(DocumentProcessingError) as exc_info:
            document_service.process_document("test")
        
        assert "Failed to process document" in str(exc_info.value)
        assert str(exc_info.value.original_error) == "Text processing failed"

def test_process_document_embedding_error(document_service, mock_openai_service):
    """Test handling of embedding generation errors."""
    mock_openai_service.generate_embeddings.side_effect = Exception("Embedding generation failed")
    
    with pytest.raises(DocumentProcessingError) as exc_info:
        document_service.process_document("test")
    
    assert "Failed to process document" in str(exc_info.value)
    assert str(exc_info.value.original_error) == "Embedding generation failed"

def test_document_service_initialization():
    """Test DocumentService initialization with different parameters."""
    # Test with default parameters
    service = DocumentService()
    assert service.text_processor.chunk_size == 1000
    assert service.text_processor.chunk_overlap == 200
    
    # Test with custom config
    service = DocumentService(config={'chunk_size': 500, 'chunk_overlap': 100})
    assert service.text_processor.chunk_size == 500
    assert service.text_processor.chunk_overlap == 100
    
    # Test with direct parameters
    service = DocumentService(chunk_size=300, chunk_overlap=50)
    assert service.text_processor.chunk_size == 300
    assert service.text_processor.chunk_overlap == 50 