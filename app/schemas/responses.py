"""
Response models for the API.

This module defines the base response structures used throughout the API to ensure
consistent response formatting and documentation. All API responses should use one
of these models as their base structure.
"""

from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel, Field

# Generic type variable for response data
T = TypeVar('T')

class ErrorResponse(BaseModel):
    """
    Standard error response format for the API.
    
    This model is used to format all error responses consistently, including:
    - Validation errors
    - HTTP exceptions
    - Internal server errors
    
    Attributes:
        detail: A human-readable error message
        code: Optional error code for programmatic handling
    """
    detail: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code for programmatic handling")

class SuccessResponse(BaseModel, Generic[T]):
    """
    Standard success response format for the API.
    
    This model wraps successful responses in a consistent structure that includes:
    - The actual response data
    - An optional success message
    
    Attributes:
        data: The actual response data of type T
        message: Optional success message
    """
    data: T = Field(..., description="Response data")
    message: Optional[str] = Field(None, description="Optional success message")

class PaginatedResponse(BaseModel, Generic[T]):
    """
    Standard paginated response format for the API.
    
    This model provides a consistent structure for paginated responses, including:
    - The list of items for the current page
    - Pagination metadata (total items, current page, etc.)
    
    Attributes:
        items: List of items for the current page
        total: Total number of items across all pages
        page: Current page number (1-based)
        size: Number of items per page
        pages: Total number of pages
    """
    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages") 