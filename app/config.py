"""
Configuration management module.

This module handles loading and accessing environment variables and settings.
It uses python-dotenv to load variables from a .env file and provides
a simple interface to access these settings throughout the application.
"""

import json
from typing import List, Dict, Any, Optional
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
    
    PROJECT_NAME: str = "AI Foundation RAG API"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "https://your-production-domain.com"]
    
    # OpenAI Settings
    SERVICE_OPENAI_API_KEY: Optional[str] = None
    SERVICE_OPENAI_EMBEDDING_MODEL: Optional[str] = None
    SERVICE_OPENAI_CHAT_MODEL: Optional[str] = None
    
    # Pinecone Settings
    SERVICE_PINECONE_API_KEY: Optional[str] = None
    SERVICE_PINECONE_CLOUD: Optional[str] = "aws"  # Default to AWS cloud
    SERVICE_PINECONE_REGION: Optional[str] = "us-east-1"  # Default to us-east-1
    SERVICE_PINECONE_INDEX_NAME: Optional[str] = None
    
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
        case_sensitive=True,
        extra="allow"  # Allow extra fields for service configurations
    )
    
    def get_service_config(self, service: str) -> Dict[str, Any]:
        """Get configuration for a specific service."""
        config = {}
        
        if service == "openai":
            if self.SERVICE_OPENAI_API_KEY:
                config["api_key"] = self.SERVICE_OPENAI_API_KEY
            if self.SERVICE_OPENAI_EMBEDDING_MODEL:
                config["embedding_model"] = self.SERVICE_OPENAI_EMBEDDING_MODEL
            if self.SERVICE_OPENAI_CHAT_MODEL:
                config["chat_model"] = self.SERVICE_OPENAI_CHAT_MODEL
                
        elif service == "pinecone":
            if self.SERVICE_PINECONE_API_KEY:
                config["api_key"] = self.SERVICE_PINECONE_API_KEY
            if self.SERVICE_PINECONE_CLOUD:
                config["cloud"] = self.SERVICE_PINECONE_CLOUD
            if self.SERVICE_PINECONE_REGION:
                config["region"] = self.SERVICE_PINECONE_REGION
            if self.SERVICE_PINECONE_INDEX_NAME:
                config["index_name"] = self.SERVICE_PINECONE_INDEX_NAME
                
        return config

# Create a single instance of Settings that will be imported throughout the app
settings = Settings(_env_file=None)  # Don't load .env file by default 