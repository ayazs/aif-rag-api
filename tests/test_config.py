"""
Tests for configuration settings.
"""

import os
from typing import List
import pytest
from app.config import Settings

def test_settings_defaults():
    """Test that settings have correct default values."""
    # Create settings without environment variables
    settings = Settings()
    
    # API Settings
    assert settings.API_V1_STR == "/api/v1"
    assert settings.PROJECT_NAME == "AI Foundation RAG API"
    
    # CORS Settings
    assert settings.CORS_ORIGINS == ["http://localhost:3000", "https://your-production-domain.com"]
    
    # OpenAI Settings
    assert settings.OPENAI_EMBEDDING_MODEL == "text-embedding-3-small"

def test_settings_from_env(monkeypatch):
    """Test that settings are loaded correctly from environment variables."""
    # Set environment variables
    env_vars = {
        "API_V1_STR": "/api/custom",
        "PROJECT_NAME": "Custom Project",
        "CORS_ORIGINS": '["http://localhost:3000"]',
        "PINECONE_API_KEY": "test-pinecone-key",
        "PINECONE_ENVIRONMENT": "test-env",
        "PINECONE_INDEX_NAME": "test-index",
        "OPENAI_API_KEY": "test-openai-key",
        "OPENAI_EMBEDDING_MODEL": "text-embedding-ada-002"
    }
    
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    
    # Create settings with environment variables
    settings = Settings()
    
    # API Settings
    assert settings.API_V1_STR == "/api/custom"
    assert settings.PROJECT_NAME == "Custom Project"
    
    # CORS Settings
    assert settings.CORS_ORIGINS == ["http://localhost:3000"]
    
    # Vector Database Settings
    assert settings.PINECONE_API_KEY == "test-pinecone-key"
    assert settings.PINECONE_ENVIRONMENT == "test-env"
    assert settings.PINECONE_INDEX_NAME == "test-index"
    
    # OpenAI Settings
    assert settings.OPENAI_API_KEY == "test-openai-key"
    assert settings.OPENAI_EMBEDDING_MODEL == "text-embedding-ada-002"

def test_settings_validation():
    """Test that settings validation works correctly."""
    # Test required fields are present
    with pytest.raises(ValueError):
        Settings(
            PINECONE_API_KEY=None,
            PINECONE_ENVIRONMENT="test-env",
            PINECONE_INDEX_NAME="test-index",
            OPENAI_API_KEY="test-key"
        )
    
    with pytest.raises(ValueError):
        Settings(
            PINECONE_API_KEY="test-key",
            PINECONE_ENVIRONMENT=None,
            PINECONE_INDEX_NAME="test-index",
            OPENAI_API_KEY="test-key"
        )
    
    with pytest.raises(ValueError):
        Settings(
            PINECONE_API_KEY="test-key",
            PINECONE_ENVIRONMENT="test-env",
            PINECONE_INDEX_NAME=None,
            OPENAI_API_KEY="test-key"
        )
    
    with pytest.raises(ValueError):
        Settings(
            PINECONE_API_KEY="test-key",
            PINECONE_ENVIRONMENT="test-env",
            PINECONE_INDEX_NAME="test-index",
            OPENAI_API_KEY=None
        ) 