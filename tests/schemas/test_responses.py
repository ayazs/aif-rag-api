"""
Tests for API response models.

This module contains tests for the base response models used throughout the API.
"""

import pytest
from app.schemas.responses import (
    ErrorResponse,
    SuccessResponse,
    PaginatedResponse
)

def test_error_response():
    """Test ErrorResponse model creation and validation."""
    # Test basic error response
    error = ErrorResponse(detail="Test error")
    assert error.detail == "Test error"
    assert error.code is None

    # Test error response with code
    error_with_code = ErrorResponse(detail="Test error", code="TEST_ERROR")
    assert error_with_code.detail == "Test error"
    assert error_with_code.code == "TEST_ERROR"

    # Test validation
    with pytest.raises(ValueError):
        ErrorResponse()  # Missing required field

def test_success_response():
    """Test SuccessResponse model creation and validation."""
    # Test with string data
    response = SuccessResponse(data="test data", message="Success!")
    assert response.data == "test data"
    assert response.message == "Success!"

    # Test with dict data
    data = {"key": "value"}
    response = SuccessResponse(data=data)
    assert response.data == data
    assert response.message is None

    # Test validation
    with pytest.raises(ValueError):
        SuccessResponse()  # Missing required field

def test_paginated_response():
    """Test PaginatedResponse model creation and validation."""
    items = [1, 2, 3]
    response = PaginatedResponse(
        items=items,
        total=10,
        page=1,
        size=3,
        pages=4
    )
    
    assert response.items == items
    assert response.total == 10
    assert response.page == 1
    assert response.size == 3
    assert response.pages == 4

    # Test validation
    with pytest.raises(ValueError):
        PaginatedResponse()  # Missing required fields

    # Test with empty items
    response = PaginatedResponse(
        items=[],
        total=0,
        page=1,
        size=10,
        pages=0
    )
    assert response.items == []
    assert response.total == 0
    assert response.pages == 0 