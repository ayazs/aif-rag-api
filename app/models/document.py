from pydantic import BaseModel, Field
from typing import List, Optional

class DocumentBase(BaseModel):
    text: str = Field(..., description="The text content of the document")
    metadata: Optional[dict] = Field(default=None, description="Optional metadata about the document")

class DocumentCreate(DocumentBase):
    pass

class DocumentResponse(DocumentBase):
    id: str = Field(..., description="Unique identifier for the document")
    embedding: Optional[List[float]] = Field(default=None, description="Vector embedding of the document")

class SearchRequest(BaseModel):
    query: str = Field(..., description="The search query text")
    top_k: int = Field(default=5, description="Number of results to return")
    filter: Optional[dict] = Field(default=None, description="Optional filter criteria")

class SearchResult(BaseModel):
    document: DocumentResponse
    score: float = Field(..., description="Similarity score between query and document") 