"""
Configuration management module.

This module handles loading and accessing environment variables and settings.
It uses python-dotenv to load variables from a .env file and provides
a simple interface to access these settings throughout the application.
"""

import json
from typing import List, Dict, Any
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
    VERSION: str = "0.1.0"
    
    # CORS Settings
    CORS_ORIGINS: List[str] = ["*"]  # Allowed origins for CORS
    
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
    
    def get_service_config(self, service_name: str) -> Dict[str, Any]:
        """Get configuration for a specific service.
        
        Args:
            service_name: Name of the service (e.g., 'pinecone', 'openai')
            
        Returns:
            Dictionary containing all environment variables for the service
            with the SERVICE_ prefix removed
        """
        prefix = f"SERVICE_{service_name.upper()}_"
        config = {}
        
        for key, value in self.model_dump().items():
            if key.startswith(prefix) and value is not None:  # Only include non-None values
                config_key = key[len(prefix):].lower()
                config[config_key] = value
        
        return config

# Create a single instance of Settings that will be imported throughout the app
settings = Settings(_env_file=None)  # Don't load .env file by default 