# Document Search API

A FastAPI application for semantic document search powered by OpenAI embeddings and Pinecone vector database.

## Features

- Document ingestion API endpoint
- Automatic text embedding generation using OpenAI's embedding models
- Vector storage and indexing with Pinecone
- Semantic search capabilities
- RESTful API interface

## Getting Started

### Prerequisites

- Python 3.8+
- OpenAI API key
- Pinecone API key and environment
- Poetry for dependency management

### Installation

1. Clone the repository
```bash
git clone https://github.com/ayazs/aif-rag-api.git
cd aif-rag-api
```

2. Install dependencies using Poetry
```bash
poetry install
```

3. Create a `.env` file in the project root with the following variables:
```env
# API Settings
API_V1_STR=/api/v1

# OpenAI Settings
OPENAI_API_KEY=your_openai_key_here
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Pinecone Settings
PINECONE_API_KEY=your_pinecone_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment_here
PINECONE_INDEX_NAME=document-search
```

### Running the Application

1. Start the development server:
```bash
poetry run uvicorn app.main:app --reload
```

2. Access the API:
- API documentation: http://127.0.0.1:8000/docs
- Test endpoint: http://127.0.0.1:8000/api/v1/test
- OpenAPI schema: http://127.0.0.1:8000/openapi.json

### Testing

Run the API test script:
```bash
./scripts/test_api.sh
```

## Project Structure

```
aif-rag-api/
├── app/
│   ├── api/           # API routes
│   ├── config.py      # Configuration management
│   └── main.py        # FastAPI application
├── scripts/           # Utility scripts
├── tests/             # Test files
├── .env              # Environment variables (not in git)
├── .gitignore        # Git ignore rules
├── LICENSE           # MIT License
├── poetry.lock       # Poetry lock file
└── pyproject.toml    # Project dependencies
```

## Development

- The application uses Poetry for dependency management
- FastAPI with Uvicorn for the web server
- Configuration is managed through environment variables
- API documentation is auto-generated using Swagger UI

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.