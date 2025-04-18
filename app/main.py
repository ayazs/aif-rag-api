"""
Main FastAPI application module.

This module sets up the FastAPI application with:
- CORS middleware configuration
- API versioning
- Router registration
- Application metadata
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_setting

# Initialize FastAPI application with metadata
app = FastAPI(
    title="Document Search API",
    description="A FastAPI application for semantic document search powered by OpenAI embeddings and Pinecone vector database",
    version="1.0.0"
)

# Configure CORS middleware
# Note: In production, replace "*" with specific allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development
    allow_credentials=True,  # Allows cookies and authentication headers
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

# Import and include API router with version prefix
from app.api.routes import router as api_router
app.include_router(api_router, prefix=get_setting('API_V1_STR')) 