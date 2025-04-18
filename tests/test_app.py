"""
Tests for the main FastAPI application.

This module tests the core application setup, including:
- Application metadata
- CORS configuration
- Router registration
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_app_metadata():
    """Test application metadata is correctly set."""
    assert app.title == "Document Search API"
    assert app.version == "1.0.0"
    assert "OpenAI embeddings" in app.description

def test_cors_configuration():
    """Test CORS headers are properly configured."""
    test_origin = "http://localhost:3000"
    headers = {
        "Origin": test_origin,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type",
    }
    
    response = client.options("/api/v1/test", headers=headers)
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == test_origin
    assert response.headers["access-control-allow-credentials"] == "true"
    
    # FastAPI expands "*" into the actual list of methods
    allowed_methods = response.headers["access-control-allow-methods"].split(", ")
    assert all(method in allowed_methods for method in ["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    assert "Content-Type" in response.headers["access-control-allow-headers"]

def test_api_versioning():
    """Test API versioning is correctly configured."""
    # Test that unversioned endpoint returns 404
    response = client.get("/test")
    assert response.status_code == 404
    
    # Test that versioned endpoint works
    response = client.get("/api/v1/test")
    assert response.status_code == 200 