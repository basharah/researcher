# Phase 2 Integration Complete: Vector DB Service

## Summary
Successfully integrated the Vector Database Service with the Document Processing Service. The system now automatically processes uploaded PDFs for semantic search.

## Architecture

### Services Implemented

#### 1. Vector DB Service (Port 8002)
- **Models**: DocumentChunk, SearchQuery with pgvector support
- **Embedding**: sentence-transformers/all-MiniLM-L6-v2 (384 dimensions)
- **Database**: PostgreSQL with pgvector extension
- **Features**:
  - Text chunking with configurable size/overlap
  - Batch embedding generation
  - Cosine similarity search
  - Query logging for analytics

#### 2. Document Processing Service (Updated)
- **New Client**: `vector_client.py` for HTTP communication
- **Background Tasks**: Async processing to Vector DB
- **Search Endpoint**: `/api/v1/search` for semantic search
- **Health Check**: Monitors Vector DB availability

### Data Flow

```
1. User uploads PDF
   ↓
2. Document Processing Service
   - Extracts text, tables, figures, references
   - Saves to PostgreSQL
   - Returns response immediately
   ↓
3. Background Task
   - Sends document to Vector DB
   - POST /process-document
   ↓
4. Vector DB Service
   - Chunks text (500 chars, 50 overlap)
   - Generates embeddings
   - Stores in pgvector
   ↓
5. User can search semantically
   - POST /api/v1/search
   - Returns relevant chunks with scores
```

## API Endpoints

### Document Processing Service

#### POST /api/v1/upload
Upload PDF - automatically triggers Vector DB processing in background.

**Response**:
```json
{
  "id": 2,
  "title": "Research Paper Title",
  "authors": ["Author Name"],
  ...
}
```

#### POST /api/v1/search
Semantic search across all documents.

**Request**:
```json
{
  "query": "machine learning methodology",
  "max_results": 10,
  "document_id": 2,  // optional
  "section": "methodology"  // optional
}
```

**Response**:
```json
{
  "query": "machine learning methodology",
  "results_count": 5,
  "search_time_ms": 45.2,
  "chunks": [
    {
      "id": 123,
      "document_id": 2,
      "text": "We applied machine learning techniques...",
      "section": "methodology",
      "similarity_score": 0.87
    }
  ]
}
```

### Vector DB Service

#### POST /process-document
Process a document (called internally by Document Processing).

**Request**:
```json
{
  "document_id": 2,
  "full_text": "Complete document text...",
  "sections": {
    "abstract": "...",
    "methodology": "..."
  }
}
```

**Response**:
```json
{
  "document_id": 2,
  "chunks_created": 25,
  "embedding_dimension": 384,
  "message": "Successfully processed document with 25 chunks"
}
```

#### POST /search
Semantic search (can be called directly or via Document Processing).

#### GET /documents/{id}/chunks
Get all chunks for a document.

#### DELETE /documents/{id}/chunks
Delete all chunks (automatically called when document is deleted).

## Configuration

### Document Processing Service

In `config.py`:
```python
vector_service_url = "http://vector-db:8000"  # Docker network
enable_vector_db = True  # Enable integration
vector_db_timeout = 300  # 5 minutes
```

### Vector DB Service

In `config.py`:
```python
embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
embedding_dimension = 384
chunk_size = 500  # characters
chunk_overlap = 50  # characters
```

## Database Schema

### document_chunks Table
```sql
CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    section VARCHAR(100),
    page_number INTEGER,
    chunk_type VARCHAR(50) DEFAULT 'text',
    embedding VECTOR(384),  -- pgvector
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX ON document_chunks (document_id, chunk_index);
CREATE INDEX ON document_chunks USING ivfflat (embedding vector_cosine_ops);
```

## Integration Features

### 1. Automatic Processing
- PDF upload triggers background task
- Non-blocking - user gets immediate response
- Errors logged but don't affect upload

### 2. Error Handling
- Timeout protection (5 min default)
- Graceful degradation if Vector DB unavailable
- Comprehensive logging

### 3. Cleanup
- Deleting document also deletes Vector DB chunks
- Ensures consistency across services

### 4. Health Monitoring
```bash
curl http://localhost:8001/health
```
Response includes Vector DB status.

## Performance Notes

### Model Loading (First Start)
- **CPU**: 2-5 minutes to load sentence-transformers
- **GPU**: < 30 seconds
- **Optimization**: Model stays loaded in memory after first use

### Embedding Generation
- **CPU**: ~100-200 chunks/second
- **GPU**: ~1000+ chunks/second
- **Strategy**: Batch processing for efficiency

### Search Performance
- **<50ms** for most queries with pgvector
- Scales with database size
- Can add HNSW index for larger datasets

## Testing

### 1. Test Upload with Vector DB Integration

```bash
# Upload a PDF
curl -X POST http://localhost:8001/api/v1/upload \
  -F "file=@paper.pdf"

# Check logs for background processing
docker logs document-processing-service
# Should see: "Scheduled Vector DB processing for document X"
```

### 2. Test Semantic Search

```bash
# Search after processing completes
curl -X POST http://localhost:8001/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the main contribution?",
    "max_results": 5
  }' | python3 -m json.tool
```

### 3. Check Vector DB Directly

```bash
# View chunks
curl http://localhost:8002/documents/2/chunks | python3 -m json.tool

# Direct search
curl -X POST http://localhost:8002/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "max_results": 3}' | python3 -m json.tool
```

## Deployment

### Docker Compose

Start both services:
```bash
docker-compose --profile phase2 up -d
```

Services:
- **document-processing**: Port 8001
- **vector-db**: Port 8002
- **postgres**: Port 5432 (with pgvector)
- **redis**: Port 6379

### Environment Variables

Create `.env`:
```env
# Database
DATABASE_URL=postgresql://researcher:researcher_pass@postgres:5432/research_papers

# Redis
REDIS_URL=redis://redis:6379

# Vector DB Integration
ENABLE_VECTOR_DB=true
VECTOR_SERVICE_URL=http://vector-db:8000
VECTOR_DB_TIMEOUT=300
```

## Next Steps

### Phase 3: LLM Service Integration
1. **Question Answering**: Use Vector DB search + LLM
2. **Summarization**: Multi-document summaries
3. **Literature Review**: Automated review generation
4. **Citation Analysis**: Track and analyze citations

### Phase 4: API Gateway
1. **Unified API**: Single entry point
2. **Authentication**: JWT tokens
3. **Rate Limiting**: Protect services
4. **Load Balancing**: Scale horizontally

### Optimizations
1. **GPU Deployment**: 10x faster embedding generation
2. **Caching**: Cache frequent searches with Redis
3. **HNSW Index**: Better performance for large datasets
4. **Async Processing**: Job queue for very large documents

## Files Modified/Created

### New Files
- `services/vector-db/config.py`
- `services/vector-db/database.py`
- `services/vector-db/models.py`
- `services/vector-db/schemas.py`
- `services/vector-db/embedding_service.py`
- `services/vector-db/text_chunker.py`
- `services/vector-db/crud.py`
- `services/vector-db/main.py` (updated)
- `services/vector-db/README.md`
- `services/vector-db/sql/init_pgvector.sql`
- `services/document-processing/vector_client.py`
- `services/document-processing/api/v1/search_schemas.py`

### Modified Files
- `services/document-processing/config.py`
- `services/document-processing/requirements.txt`
- `services/document-processing/api/v1/endpoints.py`
- `services/document-processing/main.py`
- `services/vector-db/requirements.txt`

## Known Issues & Solutions

### Issue: Vector DB service slow to start
**Cause**: Model downloading/loading on CPU  
**Solution**: Use GPU machine or pre-download model  
**Workaround**: Wait 2-5 minutes on first start

### Issue: Search returns no results
**Cause**: Documents not yet processed  
**Solution**: Check logs, ensure Vector DB is running  
**Debug**: `curl http://localhost:8002/documents/{id}/chunks`

### Issue: Background task fails silently
**Cause**: Vector DB timeout or unavailable  
**Solution**: Check `docker logs document-processing-service`  
**Fix**: Increase timeout or check Vector DB health

## Success Metrics

✅ **Phase 2 Complete**:
- Vector DB service implemented and running
- Document Processing integrated with Vector DB
- Automatic background processing
- Semantic search endpoint functional
- Health monitoring in place
- Error handling and logging
- Documentation complete

🎯 **Ready for Phase 3**: LLM Service integration can now build on top of the semantic search capabilities!
