"""
Main FastAPI application module.

This module sets up the core FastAPI application with:
- API configuration and metadata
- CORS middleware
- Exception handlers
- Health check endpoint
- API versioning and routing
- Logging configuration
"""

from fastapi import FastAPI, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.config import settings
from app.api.exceptions import (
    validation_exception_handler,
    http_exception_handler,
    generic_exception_handler
)
from app.schemas.responses import SuccessResponse
from app.logging import setup_logging, get_logger

# Initialize logging
setup_logging(settings)
logger = get_logger(__name__)

# Initialize FastAPI application with metadata
app = FastAPI(
    title="Document Search API",
    description="A FastAPI application for semantic document search powered by OpenAI embeddings and Pinecone vector database",
    version="1.0.0"
)

# Log application startup
logger.info("Starting application", extra={
    "version": "1.0.0",
    "environment": settings.ENVIRONMENT
})

# Register exception handlers for consistent error responses
app.add_exception_handler(Exception, generic_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

# Configure CORS middleware
# TODO: Before deploying to production:
# 1. Replace "*" with specific allowed origins
# 2. Review and restrict allowed methods and headers
# 3. Consider enabling credentials if needed for authentication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=False,  # Credentials not needed in development
    allow_methods=["*"],  # Allow all methods in development
    allow_headers=["*"],  # Allow all headers in development
)

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint.
    
    This endpoint provides a simple way to verify that the API is running and
    responsive. It returns a success response with a health status message.
    
    Returns:
        SuccessResponse with health status information
    """
    logger.debug("Health check requested")
    return SuccessResponse(
        data={"status": "healthy"},
        message="Service is running"
    )

# Import and include the API v1 router
from app.api.routes import router as api_router
app.include_router(api_router, prefix=settings.API_V1_STR) 