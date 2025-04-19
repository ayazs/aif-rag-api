"""
Exception handlers for the API.

This module defines custom exception handlers that ensure consistent error responses
across the API. These handlers catch various types of exceptions and format them
according to our ErrorResponse model.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.schemas.responses import ErrorResponse


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors from FastAPI and Pydantic.
    
    This handler catches validation errors that occur when:
    - Request body doesn't match the expected schema
    - Path/query parameters are invalid
    - Required fields are missing
    
    Args:
        request: The FastAPI request object
        exc: The validation error exception
        
    Returns:
        JSONResponse with a 422 status code and formatted error details
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            detail="Validation error",
            code="VALIDATION_ERROR"
        ).model_dump()
    )

async def http_exception_handler(request: Request, exc):
    """
    Handle HTTP exceptions (404, 403, etc.).
    
    This handler catches HTTP exceptions and formats them according to our
    error response model. It preserves the original status code and error message.
    
    Args:
        request: The FastAPI request object
        exc: The HTTP exception
        
    Returns:
        JSONResponse with the original status code and formatted error details
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            detail=str(exc.detail),
            code=getattr(exc, "code", None)
        ).model_dump()
    )

async def generic_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected exceptions.
    
    This is a catch-all handler for any exceptions not specifically handled
    by other handlers. It ensures that even unexpected errors return a
    consistent error response format.
    
    Args:
        request: The FastAPI request object
        exc: The unexpected exception
        
    Returns:
        JSONResponse with a 500 status code and generic error message
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            detail="An unexpected error occurred",
            code="INTERNAL_SERVER_ERROR"
        ).model_dump()
    ) 