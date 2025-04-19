"""
Tests for the text processor implementation.
"""

import pytest
from app.services.document_processing.processors.text import TextProcessor
from app.services.document_processing.exceptions import (
    TextProcessingError,
    ChunkingError,
    MetadataExtractionError
)

@pytest.fixture
def text_processor():
    """Create a text processor instance."""
    return TextProcessor(
        chunk_size=100,
        chunk_overlap=20,
        clean_patterns=[
            r'\s+',  # Multiple whitespace
            r'[\u200B-\u200D\uFEFF]',  # Zero-width spaces
        ]
    )

def test_clean_text_basic(text_processor):
    """Test basic text cleaning."""
    text = "  Hello   World  \n\n"
    cleaned = text_processor.clean_text(text)
    assert cleaned == "Hello World"

def test_clean_text_special_chars(text_processor):
    """Test cleaning of special characters."""
    text = "Hello\u200BWorld\u200C\u200D\uFEFF"
    cleaned = text_processor.clean_text(text)
    assert cleaned == "Hello World"

def test_clean_text_empty(text_processor):
    """Test cleaning empty text."""
    text = ""
    cleaned = text_processor.clean_text(text)
    assert cleaned == ""

def test_clean_text_error(text_processor):
    """Test error handling in text cleaning."""
    with pytest.raises(TextProcessingError):
        text_processor.clean_text(None)

def test_split_text_basic(text_processor):
    """Test basic text chunking."""
    text = "This is a test. This is another test. And one more test."
    chunks = text_processor.split_text(text)
    
    assert len(chunks) > 0
    assert all(isinstance(chunk["text"], str) for chunk in chunks)
    assert all(isinstance(chunk["start"], int) for chunk in chunks)
    assert all(isinstance(chunk["end"], int) for chunk in chunks)
    assert all(isinstance(chunk["index"], int) for chunk in chunks)

def test_split_text_small(text_processor):
    """Test chunking small text."""
    text = "Short text"
    chunks = text_processor.split_text(text)
    assert len(chunks) == 1
    assert chunks[0]["text"] == text

def test_split_text_large(text_processor):
    """Test chunking large text."""
    text = "This is a test. " * 100  # Create a long text
    chunks = text_processor.split_text(text)
    assert len(chunks) > 1
    assert all(len(chunk["text"]) <= text_processor.chunk_size for chunk in chunks)

def test_split_text_overlap(text_processor):
    """Test chunk overlap."""
    text = "This is a test. " * 10
    chunks = text_processor.split_text(text)
    
    # Check that chunks overlap
    for i in range(len(chunks) - 1):
        current_chunk = chunks[i]["text"]
        next_chunk = chunks[i + 1]["text"]
        overlap = len(set(current_chunk.split()) & set(next_chunk.split()))
        assert overlap > 0

def test_split_text_error(text_processor):
    """Test error handling in text chunking."""
    with pytest.raises(ChunkingError):
        text_processor.split_text(None)

def test_extract_metadata_basic(text_processor):
    """Test basic metadata extraction."""
    text = "This is a test.\n\nThis is another test."
    metadata = text_processor.extract_metadata(text)
    
    assert isinstance(metadata, dict)
    assert metadata['length'] == len(text)
    assert metadata['word_count'] == 8
    assert metadata['line_count'] == 3
    assert metadata['has_paragraphs'] is True

def test_extract_metadata_empty(text_processor):
    """Test metadata extraction from empty text."""
    text = ""
    metadata = text_processor.extract_metadata(text)
    
    assert metadata['length'] == 0
    assert metadata['word_count'] == 0
    assert metadata['line_count'] == 1
    assert metadata['has_paragraphs'] is False

def test_extract_metadata_error(text_processor):
    """Test error handling in metadata extraction."""
    with pytest.raises(MetadataExtractionError):
        text_processor.extract_metadata(None) 