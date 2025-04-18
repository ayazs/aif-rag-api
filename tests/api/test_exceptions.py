"""
Tests for API exception handlers.

This module contains tests for the custom exception handlers used in the API.
"""

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from fastapi.exceptions import RequestValidationError, HTTPException

from app.api.exceptions import (
    validation_exception_handler,
    http_exception_handler,
    generic_exception_handler
)

# Create a test app
app = FastAPI()

# Test endpoints to trigger exceptions
@app.get("/validation-error")
async def trigger_validation_error():
    raise RequestValidationError(errors=[])

@app.get("/http-error")
async def trigger_http_error():
    raise HTTPException(status_code=404, detail="Not Found")

@app.get("/generic-error")
async def trigger_generic_error():
    # FastAPI will convert this to an HTTPException with 500 status code
    raise RuntimeError("Test error")

# Register exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

client = TestClient(app)

def test_validation_exception_handler():
    """Test validation exception handler."""
    response = client.get("/validation-error")
    assert response.status_code == 422
    data = response.json()
    assert data["detail"] == "Validation error"
    assert data["code"] == "VALIDATION_ERROR"

def test_http_exception_handler():
    """Test HTTP exception handler."""
    response = client.get("/http-error")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Not Found"
    assert data["code"] is None

def test_generic_exception_handler():
    """Test generic exception handler."""
    with pytest.raises(RuntimeError) as exc_info:
        client.get("/generic-error")
    assert str(exc_info.value) == "Test error" 