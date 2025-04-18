"""
API routes module.

This module defines the API endpoints and their handlers.
Each endpoint is versioned under the /api/v1 prefix.
"""

from fastapi import APIRouter

# Create API router instance
router = APIRouter()

@router.get("/test")
async def test_endpoint():
    """
    Test endpoint to verify API functionality.
    
    Returns:
        dict: A simple message indicating the API is working
    """
    return {"message": "API is working"} 