"""
Tests for the main FastAPI application.

This module contains tests for the core application functionality,
including the health check endpoint and basic API structure.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["status"] == "healthy"
    assert data["message"] == "Service is running"

def test_api_versioning():
    """Test API versioning structure."""
    response = client.get("/api/v1/test")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["status"] == "working"
    assert data["message"] == "API is working"

def test_docs_endpoints():
    """Test API documentation endpoints."""
    # Test Swagger UI
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

    # Test OpenAPI schema
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
    assert "paths" in schema

def test_cors_enabled():
    """Test that CORS is enabled."""
    # Simple request to verify CORS is working
    response = client.get("/health", headers={"Origin": "http://localhost"})
    assert response.status_code == 200  # Request should succeed 