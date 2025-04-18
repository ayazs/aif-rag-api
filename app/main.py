from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_setting

app = FastAPI(
    title="Document Search API",
    description="A FastAPI application for semantic document search powered by OpenAI embeddings and Pinecone vector database",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from app.api.routes import router as api_router
app.include_router(api_router, prefix=get_setting('API_V1_STR')) 