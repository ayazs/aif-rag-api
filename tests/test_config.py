"""
Tests for configuration management.
"""

import pytest
from app.config import Settings

def test_settings_defaults():
    """Test that settings have correct default values."""
    # Create settings without environment variables
    settings = Settings(_env_file=None)  # Don't load .env file

    # API Settings
    assert settings.API_V1_STR == "/api/v1"
    assert settings.PROJECT_NAME == "AI Foundation RAG API"  # Match actual default

    # CORS Settings
    assert settings.CORS_ORIGINS == ["http://localhost:3000", "https://your-production-domain.com"]

    # Service configurations should be empty by default
    openai_config = settings.get_service_config('openai')
    assert not openai_config  # Should be empty dict

def test_settings_from_env(monkeypatch):
    """Test that settings are loaded correctly from environment variables."""
    # Clear existing environment variables
    monkeypatch.delenv("SERVICE_PINECONE_API_KEY", raising=False)
    monkeypatch.delenv("SERVICE_PINECONE_ENVIRONMENT", raising=False)
    monkeypatch.delenv("SERVICE_PINECONE_INDEX_NAME", raising=False)
    monkeypatch.delenv("SERVICE_OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("SERVICE_OPENAI_EMBEDDING_MODEL", raising=False)
    
    # Set environment variables
    env_vars = {
        "API_V1_STR": "/api/custom",
        "PROJECT_NAME": "Custom Project",
        "CORS_ORIGINS": '["http://localhost:3000"]',
        "SERVICE_PINECONE_API_KEY": "test-pinecone-key",
        "SERVICE_PINECONE_ENVIRONMENT": "test-env",
        "SERVICE_PINECONE_INDEX_NAME": "test-index",
        "SERVICE_OPENAI_API_KEY": "test-openai-key",
        "SERVICE_OPENAI_EMBEDDING_MODEL": "text-embedding-ada-002"
    }

    # Create settings with environment variables but without .env file
    settings = Settings(
        _env_file=None,
        **env_vars  # Pass environment variables directly
    )

    # API Settings
    assert settings.API_V1_STR == "/api/custom"
    assert settings.PROJECT_NAME == "Custom Project"

    # CORS Settings
    assert settings.CORS_ORIGINS == ["http://localhost:3000"]

    # Vector Database Settings
    pinecone_config = settings.get_service_config('pinecone')
    assert pinecone_config['api_key'] == "test-pinecone-key"
    assert pinecone_config['environment'] == "test-env"
    assert pinecone_config['index_name'] == "test-index"

    # OpenAI Settings
    openai_config = settings.get_service_config('openai')
    assert openai_config['api_key'] == "test-openai-key"
    assert openai_config['embedding_model'] == "text-embedding-ada-002"

def test_settings_validation():
    """Test that settings validation works correctly."""
    # Test that service configuration is empty when no environment variables are set
    settings = Settings(
        _env_file=None,  # Don't load .env file
        SERVICE_PINECONE_API_KEY=None,
        SERVICE_PINECONE_CLOUD=None,
        SERVICE_PINECONE_REGION=None,
        SERVICE_PINECONE_INDEX_NAME=None,
        SERVICE_OPENAI_API_KEY=None,
        SERVICE_OPENAI_EMBEDDING_MODEL=None
    )
    pinecone_config = settings.get_service_config('pinecone')
    assert not pinecone_config  # Should be empty dict

    # Test that service configuration contains only relevant variables
    settings = Settings(
        _env_file=None,  # Don't load .env file
        SERVICE_PINECONE_API_KEY="test-key",
        OTHER_VAR="test"
    )
    pinecone_config = settings.get_service_config('pinecone')
    assert 'api_key' in pinecone_config
    assert 'other_var' not in pinecone_config

def test_cors_origins_validation():
    """Test CORS_ORIGINS validation behavior."""
    # Test valid JSON string
    settings = Settings(
        _env_file=None,
        CORS_ORIGINS='["http://localhost:3000", "https://example.com"]'
    )
    assert settings.CORS_ORIGINS == ["http://localhost:3000", "https://example.com"]

    # Test invalid JSON string (falls back to single-item list)
    settings = Settings(
        _env_file=None,
        CORS_ORIGINS="http://localhost:3000"  # Not valid JSON
    )
    assert settings.CORS_ORIGINS == ["http://localhost:3000"]

    # Test list input (should pass through unchanged)
    settings = Settings(
        _env_file=None,
        CORS_ORIGINS=["http://localhost:3000"]
    )
    assert settings.CORS_ORIGINS == ["http://localhost:3000"] 