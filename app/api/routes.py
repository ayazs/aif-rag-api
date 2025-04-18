"""
API routes module.

This module defines the API endpoints and their handlers.
Each endpoint is versioned under the /api/v1 prefix.
"""

from fastapi import APIRouter
from app.schemas.responses import SuccessResponse

# Create API router instance
router = APIRouter()

@router.get("/test")
async def test_endpoint():
    """
    Test endpoint to verify API functionality.
    
    Returns:
        SuccessResponse: A structured response indicating the API is working
    """
    return SuccessResponse(
        data={"status": "working"},
        message="API is working"
    )
