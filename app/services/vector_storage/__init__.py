"""
Vector storage service package.

This package provides services for interacting with vector databases,
currently supporting Pinecone as the backend.
"""

from app.services.vector_storage.pinecone import PineconeService

__all__ = ["PineconeService"] 