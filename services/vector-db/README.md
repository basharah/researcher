# Vector Database Service

## Overview
The Vector Database Service handles document chunking, embedding generation, and semantic search using pgvector and sentence-transformers.

## Features
- **Document Chunking**: Intelligently splits documents into searchable chunks
- **Embedding Generation**: Uses sentence-transformers (all-MiniLM-L6-v2) for semantic embeddings
- **Semantic Search**: Fast cosine similarity search with pgvector
- **Batch Processing**: Efficient handling of large documents

## Architecture

### Components
1. **Text Chunker** (`text_chunker.py`): Splits documents into overlapping chunks
2. **Embedding Service** (`embedding_service.py`): Generates embeddings using sentence-transformers
3. **Database Models** (`models.py`): SQLAlchemy models with pgvector support
4. **CRUD Operations** (`crud.py`): Database operations for chunks and search
5. **API Endpoints** (`main.py`): REST API for processing and searching

### Database Schema

#### DocumentChunk
- `id`: Primary key
- `document_id`: Reference to document in document-processing service
- `chunk_index`: Order of chunk within document
- `text`: Chunk content
- `section`: Section name (abstract, introduction, etc.)
- `page_number`: Source page
- `chunk_type`: Type of content (text, table, reference)
- `embedding`: Vector(384) - semantic embedding
- `created_at`, `updated_at`: Timestamps

#### SearchQuery
- Logs search queries for analytics
- Stores query text and embedding
- Tracks result counts and scores

## Configuration

Settings in `config.py`:

```python
# Embedding model
embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
embedding_dimension = 384

# Chunking
chunk_size = 500  # characters
chunk_overlap = 50  # characters

# Search
max_search_results = 10
```

## API Endpoints

### POST /process-document
Process a document and generate embeddings.

**Request**:
```json
{
  "document_id": 1,
  "full_text": "Complete document text...",
  "sections": {
    "abstract": "...",
    "introduction": "...",
    "methodology": "..."
  }
}
```

**Response**:
```json
{
  "document_id": 1,
  "chunks_created": 25,
  "embedding_dimension": 384,
  "message": "Successfully processed document with 25 chunks"
}
```

### POST /search
Semantic search across document chunks.

**Request**:
```json
{
  "query": "machine learning methods",
  "max_results": 10,
  "document_id": 1,  // optional filter
  "section": "methodology"  // optional filter
}
```

**Response**:
```json
{
  "query": "machine learning methods",
  "results_count": 10,
  "search_time_ms": 45.2,
  "chunks": [
    {
      "id": 123,
      "document_id": 1,
      "chunk_index": 5,
      "text": "We applied machine learning...",
      "section": "methodology",
      "similarity_score": 0.87,
      "created_at": "2025-11-04T..."
    }
  ]
}
```

### POST /embed
Generate embedding for arbitrary text.

**Request**:
```json
{
  "text": "Example text to embed"
}
```

**Response**:
```json
{
  "text": "Example text to embed",
  "embedding": [0.123, -0.456, ...],
  "dimension": 384
}
```

### GET /documents/{document_id}/chunks
Get all chunks for a document.

### DELETE /documents/{document_id}/chunks
Delete all chunks for a document.

## Setup

### Prerequisites
1. PostgreSQL with pgvector extension
2. Python 3.10+

### Enable pgvector

```sql
-- Connect to your database
CREATE EXTENSION IF NOT EXISTS vector;
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

This will download:
- sentence-transformers model (~90MB)
- PyTorch dependencies
- pgvector Python client

### Run the Service

```bash
# Development
uvicorn main:app --reload --port 8002

# Production
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Docker

```bash
docker-compose up vector-db
```

## Usage Example

### 1. Process a Document

```python
import requests

# After uploading a PDF to document-processing service
doc_data = {
    "document_id": 1,
    "full_text": full_text,
    "sections": {
        "abstract": abstract_text,
        "introduction": intro_text,
        "methodology": method_text,
        "results": results_text,
        "conclusion": conclusion_text
    }
}

response = requests.post(
    "http://localhost:8002/process-document",
    json=doc_data
)
print(response.json())
# {"document_id": 1, "chunks_created": 25, ...}
```

### 2. Search for Content

```python
search_query = {
    "query": "What methodology was used?",
    "max_results": 5,
    "section": "methodology"  # optional filter
}

response = requests.post(
    "http://localhost:8002/search",
    json=search_query
)

results = response.json()
for chunk in results["chunks"]:
    print(f"Score: {chunk['similarity_score']:.2f}")
    print(f"Text: {chunk['text'][:100]}...")
    print()
```

## Integration with Document Processing

The Vector DB service is designed to be called by the Document Processing service after a PDF is uploaded and parsed.

**Workflow**:
1. User uploads PDF to Document Processing Service
2. Document Processing extracts text and sections
3. Document Processing calls `/process-document` on Vector DB
4. Vector DB chunks text and generates embeddings
5. Embeddings stored in PostgreSQL with pgvector
6. User can now search semantically across all documents

## Performance

### Embedding Generation
- ~100-200 chunks/second on CPU
- ~1000+ chunks/second on GPU

### Search
- <50ms for similarity search across 10,000 chunks
- Scales with pgvector's indexing

### Storage
- ~1.5KB per chunk (including embedding)
- A 10-page paper typically generates 20-30 chunks

## Model Information

**Default Model**: `sentence-transformers/all-MiniLM-L6-v2`

**Characteristics**:
- Dimension: 384
- Speed: Very fast (best for CPU)
- Quality: Good for general-purpose semantic search
- Size: ~90MB

**Alternative Models**:
```python
# In config.py
embedding_model = "sentence-transformers/all-mpnet-base-v2"  # Higher quality, slower
# or
embedding_model = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"  # Multilingual
```

## Monitoring

### Check Service Status

```bash
curl http://localhost:8002/health
```

### Database Queries

```sql
-- Count chunks per document
SELECT document_id, COUNT(*) as chunk_count
FROM document_chunks
GROUP BY document_id;

-- View recent searches
SELECT query_text, results_count, top_score, created_at
FROM search_queries
ORDER BY created_at DESC
LIMIT 10;
```

## Troubleshooting

### Model Loading Issues
If the embedding model fails to load:
```bash
# Pre-download the model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

### pgvector Extension Not Found
```sql
-- Verify extension is available
SELECT * FROM pg_available_extensions WHERE name = 'vector';

-- Install extension
CREATE EXTENSION vector;
```

### Slow Search Performance
```sql
-- Add index for faster similarity search (optional, for large datasets)
CREATE INDEX ON document_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

## Development

### Running Tests
```bash
# Test embedding generation
curl -X POST http://localhost:8002/embed \
  -H "Content-Type: application/json" \
  -d '{"text": "Test embedding generation"}'

# Test search (after processing a document)
curl -X POST http://localhost:8002/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test query", "max_results": 5}'
```

## Next Steps

1. **Optimization**: Add HNSW indexing for larger datasets
2. **Reranking**: Implement cross-encoder reranking for better results
3. **Caching**: Cache frequently searched queries
4. **Async Processing**: Add background job queue for large documents
5. **Monitoring**: Add metrics and logging

## Dependencies

See `requirements.txt` for full list. Key dependencies:
- `fastapi`: Web framework
- `sentence-transformers`: Embedding generation
- `pgvector`: PostgreSQL vector extension
- `sqlalchemy`: Database ORM
- `torch`: PyTorch for ML models
