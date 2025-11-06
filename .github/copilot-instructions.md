# Research Paper Analysis Chatbot - AI Agent Instructions

## Project Architecture & Big Picture

**Microservices-based** research paper analysis system with Phase 1 & 2 complete. Services communicate via HTTP, share PostgreSQL + pgvector for storage, and use Redis for caching.

### Service Communication Pattern
```
PDF Upload → Document Processing (8001) → Background Task → Vector DB (8002)
                    ↓                                            ↓
                PostgreSQL (documents table)         PostgreSQL (document_chunks + embeddings)
```

**Key Insight**: Document upload returns immediately to user, while Vector DB processing happens asynchronously via `BackgroundTasks`. This prevents timeouts during embedding generation (~30s-5min on first load).

### Active Services (Phases 1-3 Complete)
- **Document Processing** (port 8001): PDF upload, extraction (text, tables, figures, refs), stores in PostgreSQL
- **Vector DB** (port 8002): Text chunking (500 chars, 50 overlap), sentence-transformers embeddings (384d), semantic search via pgvector, **GPU-accelerated** for faster embedding generation
- **LLM Service** (port 8003): AI-powered analysis using OpenAI/Anthropic, RAG-enabled Q&A, document comparison, interactive chat
- **PostgreSQL**: Shared database with `documents` and `document_chunks` tables, pgvector extension enabled
- **Redis**: Currently minimal usage, prepared for caching/sessions

### GPU Configuration
System has **2 NVIDIA GPUs** (RTX 2080 Ti 11GB, GTX 960 4GB):
- **Vector DB** uses GPU 0 (RTX 2080 Ti) for embedding generation (~10-50x faster than CPU)
- **LLM Service** uses GPU 1 (GTX 960) reserved for local model inference (when implemented)
- GPU allocation managed via `CUDA_VISIBLE_DEVICES` in docker-compose.yml
- Sentence-transformers automatically detects and uses CUDA when available

### Placeholders (Future Phases)
- API Gateway (8000), Frontend - basic structure exists but not implemented

## Critical Developer Workflows

### Starting the System
```bash
# Start all Phase 1-3 services (recommended)
docker-compose up -d postgres redis document-processing vector-db llm-service

# Or use profiles
docker-compose --profile phase3 up -d

# Quick start script available: ./start.sh (Linux/Mac)
```

**First Startup**: Vector DB takes 30s-2min to download sentence-transformers model (all-MiniLM-L6-v2). **GPU reduces embedding time from ~5min to ~30s** for typical papers. Monitor with `docker logs -f vector-db-service`.

**LLM Service**: Requires `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` in `.env`. Service starts without keys but endpoints will fail.

### Testing Services
```bash
# Document Processing health (includes Vector DB status)
curl http://localhost:8001/health

# Upload PDF and trigger background processing
curl -X POST -F "file=@paper.pdf" http://localhost:8001/api/v1/upload

# Semantic search across documents
curl -X POST http://localhost:8001/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning methodology", "max_results": 5}'

# LLM analysis (requires API key)
curl -X POST http://localhost:8003/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"document_id": 1, "analysis_type": "summary"}'

# Integration test script (comprehensive)
./test-phase2-integration.sh
```

### Database Migrations (Alembic)
```bash
cd services/document-processing

# Run migrations in container
docker exec document-processing-service alembic upgrade head

# Create new migration (if needed)
docker exec document-processing-service alembic revision --autogenerate -m "description"

# See: alembic/versions/20251104_01_add_extraction_fields.py for JSONB columns example
```

## Project-Specific Conventions

### API Versioning Pattern
All endpoints use `/api/v1/` prefix. Router structure:
```python
# main.py includes api_router at /api prefix
app.include_router(api_router, prefix="/api")

# api/__init__.py includes v1 router at /v1
api_router.include_router(v1_router, prefix="/v1")

# Result: endpoints accessible at /api/v1/upload, /api/v1/search, etc.
```
See `services/document-processing/api/README.md` for versioning strategy.

### Configuration Management (Pydantic Settings)
**Never hardcode values**. All config in `config.py` using Pydantic BaseSettings:
```python
from config import settings

settings.database_url        # From DATABASE_URL env var or .env file
settings.enable_vector_db    # Feature flag for Vector DB integration
settings.upload_dir          # Path object, auto-created
settings.max_file_size       # Validated integer (10MB default)
```

Copy `.env.example` to `.env` for local development. Docker Compose passes env vars automatically.

### Background Processing Pattern
Upload endpoints use FastAPI's `BackgroundTasks` for async processing:
```python
@router.post("/upload")
async def upload_document(
    file: UploadFile,
    background_tasks: BackgroundTasks
):
    # Save file and create DB record immediately
    doc = crud.create_document(db, ...)
    
    # Add Vector DB processing to background (non-blocking)
    background_tasks.add_task(
        process_in_vector_db,
        document_id=doc.id,
        full_text=text,
        sections=sections
    )
    
    return doc  # Return before background processing completes
```
See `services/document-processing/api/v1/endpoints.py:142` for implementation.

### PDF Extraction - Two-Column Handling
`PDFParser` uses **character density projection** to detect multi-column layouts:
```python
# pdf_parser.py detects columns via horizontal density gaps
# Extracts left column fully, then right column (preserves reading order)
# Also extracts: title (largest font), authors (layout heuristics), tables, figures, references
```
This is critical for academic papers - simple `extract_text()` scrambles columns.

### Database Models - JSONB for Complex Data
Store structured extraction results as JSONB (not separate tables):
```python
# models.py
tables_data = Column(JSONB, nullable=True)        # List of table dicts
figures_metadata = Column(JSONB, nullable=True)   # List of figure dicts
references_json = Column(JSONB, nullable=True)    # List of reference dicts
```
Migration: `alembic/versions/20251104_01_add_extraction_fields.py`

### Vector DB Client Pattern (HTTP Communication)
Services communicate via async HTTP client (`VectorDBClient` in `vector_client.py`):
```python
vector_client = get_vector_client()  # Singleton pattern
result = await vector_client.process_document(...)

# Graceful degradation: if Vector DB unavailable, logs warning but doesn't fail upload
# Health check: /health endpoint queries Vector DB and reports status
```

## Integration Points & Data Flows

### Document Upload Flow
1. User POSTs PDF to `/api/v1/upload` (Document Processing)
2. Save file to `uploads_data/` with timestamp prefix
3. `PDFParser` extracts: metadata, text (column-aware), tables, figures, references
4. Create `Document` record in PostgreSQL with JSONB fields
5. Background task sends to Vector DB `/process-document` endpoint
6. Vector DB chunks text, generates embeddings, stores in `document_chunks` table
7. User can immediately search via `/api/v1/search`

### Semantic Search Flow
1. User POSTs query to `/api/v1/search` (Document Processing proxies to Vector DB)
2. Vector DB generates query embedding
3. Cosine similarity search via pgvector: `embedding <=> query_embedding`
4. Returns chunks with similarity scores, document metadata, section names
5. Optional filters: `document_id`, `section` (e.g., only search "methodology")

## Key Files & Directories

**Must-read for understanding architecture:**
- `docker-compose.yml`: Service definitions, ports, dependencies, profiles
- `PHASE2_INTEGRATION_COMPLETE.md`: Vector DB integration guide
- `PHASE3_LLM_SERVICE.md`: LLM service features and API examples
- `services/document-processing/vector_client.py`: Inter-service HTTP communication pattern
- `services/document-processing/utils/pdf_parser.py`: Comprehensive extraction (700+ lines)
- `services/vector-db/text_chunker.py`: Chunking strategy with overlap
- `services/vector-db/embedding_service.py`: Sentence-transformers integration
- `services/llm-service/prompts.py`: LLM prompt templates for different analysis types
- `services/llm-service/llm_client.py`: OpenAI/Anthropic client wrapper

**Service-specific patterns:**
- `services/*/config.py`: Pydantic settings for each service
- `services/*/models.py`: SQLAlchemy models (note pgvector `Vector()` type in vector-db)
- `services/*/crud.py`: Database operations (create, read, update, delete)
- `services/*/api/v1/endpoints.py`: Versioned API endpoints

## Common Gotchas

1. **Vector DB not ready**: First startup downloads 80MB model. Check `docker logs vector-db-service` for "Application startup complete" and "Device: cuda" to confirm GPU is active.

2. **GPU not detected**: If Vector DB shows "Device: cpu", check:
   - NVIDIA Container Toolkit installed: `docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi`
   - Docker Compose version ≥ 1.28 (for `deploy.resources.reservations`)
   - Rebuild image after requirements.txt change: `docker-compose build vector-db`

3. **Port confusion**: Document Processing is 8001 (not 8000). API Gateway will use 8000 in Phase 4.

4. **Docker network URLs**: Services use `http://vector-db:8000` internally, `http://localhost:8002` externally.

5. **Column detection**: If extracted text seems scrambled, check `PDFParser._is_two_column_layout()` threshold (currently 0.3).

6. **Embedding dimension mismatch**: Vector DB uses 384d (all-MiniLM-L6-v2). Changing models requires migration to alter `Vector(384)` column.

7. **Background tasks don't raise exceptions**: Check logs for Vector DB processing errors, not response status.

## Testing & Validation

Run comprehensive tests before committing changes:
```bash
# Integration test (uploads real PDF, tests search)
./test-phase2-integration.sh

# Individual service tests
./test-service.sh document-processing
./test-extraction-endpoints.sh  # Tests table/figure/reference extraction

# Python unit tests
python test_comprehensive.py  # PDFParser feature tests
python test_vector_db.py      # Vector DB operations
```

See `EXTRACTION_TESTING_SUMMARY.md` for extraction feature validation.
