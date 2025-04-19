from typing import List, Dict, Any
import re
from app.services.document_processing.exceptions import (
    TextProcessingError,
    ChunkingError,
    MetadataExtractionError
)

class TextProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200, clean_patterns: List[str] = None):
        """
        Initialize the text processor with chunking parameters.
        
        Args:
            chunk_size: Maximum size of each text chunk
            chunk_overlap: Number of characters to overlap between chunks
            clean_patterns: List of regex patterns for text cleaning
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.clean_patterns = clean_patterns or [
            r'\s+',  # Multiple whitespace
            r'[\u200B-\u200D\uFEFF]',  # Zero-width spaces
        ]

    def clean_text(self, text: str) -> str:
        """
        Clean text using the configured patterns.
        
        Args:
            text: The text to clean
            
        Returns:
            Cleaned text
            
        Raises:
            TextProcessingError: If text is None
        """
        if text is None:
            raise TextProcessingError("Text cannot be None")
            
        cleaned = text
        for pattern in self.clean_patterns:
            cleaned = re.sub(pattern, ' ', cleaned)
        return cleaned.strip()

    def split_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: The text to split
            
        Returns:
            List of chunks with their positions and indices
            
        Raises:
            ChunkingError: If text is None
        """
        if text is None:
            raise ChunkingError("Text cannot be None")

        text = text.strip()
        if not text:
            return [{
                "text": "",
                "start": 0,
                "end": 0,
                "index": 0
            }]

        # If text is smaller than chunk size, return it as a single chunk
        if len(text) <= self.chunk_size:
            return [{
                "text": text,
                "start": 0,
                "end": len(text),
                "index": 0
            }]

        chunks = []
        start = 0
        index = 0

        while start < len(text):
            # Calculate end position for this chunk
            end = min(start + self.chunk_size, len(text))
            
            # If we're not at the end, try to find a good breaking point
            if end < len(text):
                # Look for the last space or newline before the end
                last_space = text.rfind(' ', start, end)
                last_newline = text.rfind('\n', start, end)
                
                # Use the later of the two if found
                if last_space > -1 or last_newline > -1:
                    end = max(last_space, last_newline) + 1  # Include the space/newline in this chunk
            
            # Add the chunk
            chunk_text = text[start:end].strip()
            if chunk_text:  # Only add non-empty chunks
                chunks.append({
                    "text": chunk_text,
                    "start": start,
                    "end": end,
                    "index": index
                })
                index += 1
            
            # Move start position for next chunk
            if end == len(text):
                break
            start = max(start + 1, end - self.chunk_overlap)

        return chunks

    def extract_metadata(self, text: str) -> Dict[str, Any]:
        """
        Extract metadata from text.
        
        Args:
            text: The text to analyze
            
        Returns:
            Dictionary containing metadata like length, word count, etc.
            
        Raises:
            MetadataExtractionError: If text is None
        """
        if text is None:
            raise MetadataExtractionError("Text cannot be None")

        if not text:
            return {
                'length': 0,
                'word_count': 0,
                'line_count': 1,
                'has_paragraphs': False
            }

        lines = text.split('\n')
        words = text.split()
        
        return {
            'length': len(text),
            'word_count': len(words),
            'line_count': len(lines),
            'has_paragraphs': len(lines) > 1 and any(not line.strip() for line in lines)
        } 