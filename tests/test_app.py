"""
Tests for the main FastAPI application.

This module tests the core application setup, including:
- Application metadata
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

def test_api_versioning():
    """Test API versioning is correctly configured."""
    # Test that unversioned endpoint returns 404
    response = client.get("/test")
    assert response.status_code == 404
    
    # Test that versioned endpoint works
    response = client.get("/api/v1/test")
    assert response.status_code == 200 