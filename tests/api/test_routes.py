"""
Tests for API routes.

This module contains tests for all API endpoints defined in app.api.routes.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_test_endpoint():
    """Test the test endpoint returns correct response."""
    response = client.get("/api/v1/test")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "API is working" 