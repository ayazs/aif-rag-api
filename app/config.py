"""
Configuration management module.

This module handles loading and accessing environment variables and settings.
It uses python-dotenv to load variables from a .env file and provides
a simple interface to access these settings throughout the application.
"""

import json
from typing import List
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """
    Application settings using Pydantic for type-safe configuration.
    
    This class automatically:
    1. Loads environment variables from .env file
    2. Validates them against the type hints
    3. Provides type-safe access to the values
    
    Default values are used if environment variables are not set.
    """
    
    # API Settings
    API_V1_STR: str = "/api/v1"  # Base path for API v1 endpoints
    PROJECT_NAME: str = "AI Foundation RAG API"  # Name of the project
    
    # CORS Settings
    CORS_ORIGINS: List[str] = ["*"]  # Allowed origins for CORS
    
    # Vector Database Settings
    PINECONE_API_KEY: str  # Pinecone API key
    PINECONE_ENVIRONMENT: str  # Pinecone environment
    PINECONE_INDEX_NAME: str  # Pinecone index name
    
    # OpenAI Settings
    OPENAI_API_KEY: str  # OpenAI API key
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"  # OpenAI embedding model
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_json_list(cls, v):
        """Parse JSON string into list if necessary."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [v]
        return v
    
    # Use ConfigDict instead of class Config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

# Create a single instance of Settings that will be imported throughout the app
# This instance is created when the module is imported and will contain all
# the validated settings from environment variables or defaults
settings = Settings() 