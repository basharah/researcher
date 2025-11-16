# Document Processing Service Enhancement - Phase 1 Implementation

## Overview
This document describes the enhancement of the document processing service with:
1. **DOI Extraction** - Automatic detection and validation of Digital Object Identifiers
2. **Batch Upload** - Multi-file upload with async processing
3. **OCR Support** - Optical Character Recognition for scanned PDFs
4. **Processing Records** - Complete audit trail of all processing steps
5. **Celery Workers** - Distributed task processing for scalability

## Phase 1: Foundation (Completed)

### 1.1 Database Schema ✓

**New Tables:**
- `processing_jobs` - Tracks individual document processing jobs
- `processing_steps` - Detailed logging of each processing step

**Extended `documents` table:**
- `doi` (String, indexed) - Digital Object Identifier
- `batch_id` (String, indexed) - Groups documents from batch uploads
- `processing_job_id` (String, FK) - Links to processing job
- `ocr_applied` (Boolean) - Whether OCR was used

**Migration:** `alembic/versions/20251110_01_processing_jobs.py`

### 1.2 Models ✓

**Created/Updated:**
- `ProcessingJob` - Job tracking with status, progress, timestamps
- `ProcessingStep` - Step-by-step processing log
- `ProcessingStatus` enum - pending, processing, completed, failed, cancelled
- Updated `Document` model with new fields

**File:** `services/document-processing/models.py`

### 1.3 Core Utilities ✓

**DOI Extractor** (`utils/doi_extractor.py`):
- Pattern matching for DOI formats (10.xxxx/xxxxx, doi:, http://doi.org/)
- CrossRef API validation
- Metadata enrichment (title, authors, publication date)
- PDF metadata extraction

**OCR Processor** (`utils/ocr_processor.py`):
- Scanned PDF detection (text density heuristic)
- Tesseract OCR integration
- PDF to image conversion
- Automatic fallback for scanned documents

### 1.4 Dependencies ✓

**Added to `requirements.txt`:**
```
# OCR
pytesseract==0.3.10
pdf2image==1.16.3
Pillow==10.1.0

# Task Queue
celery[redis]==5.3.4
flower==2.0.1

# DOI/API
requests==2.31.0
```

### 1.5 Celery Configuration ✓

**File:** `services/document-processing/celery_app.py`
- Redis as broker and backend
- Task routing to specialized queues
- Timeouts and retry configuration
- Worker resource limits

## Phase 2: Task Implementation (Next)

### 2.1 Celery Tasks

**File to create:** `services/document-processing/tasks.py`

Tasks to implement:
1. `process_document_task(job_id, file_path, user_id)` - Main processing task
   - Extract text (with OCR fallback)
   - Extract DOI
   - Extract tables/figures/references
   - Store in vector DB
   - Update job status and progress

2. `process_batch_task(batch_id, file_paths, user_id)` - Batch coordinator
   - Create individual jobs for each file
   - Monitor overall progress
   - Handle failures gracefully

3. `extract_doi_task(document_id)` - Async DOI extraction and validation

4. `apply_ocr_task(document_id, force=False)` - Reprocess with OCR

### 2.2 Enhanced PDF Parser

**Update:** `utils/pdf_parser.py`

Enhancements needed:
- Integrate DOI extractor
- Add OCR fallback logic
- Improve section detection with:
  - Better font size analysis
  - ML-based header detection (optional)
  - Confidence scoring
  - Nested section handling

### 2.3 CRUD Operations

**Create:** `services/document-processing/jobs_crud.py`

Functions:
- `create_job(db, job_id, filename, ...)` - Create processing job
- `update_job_status(db, job_id, status, progress)` - Update job
- `add_processing_step(db, job_id, step_name, status, ...)` - Log step
- `get_job(db, job_id)` - Get job details
- `get_batch_jobs(db, batch_id)` - Get all jobs in a batch
- `get_user_jobs(db, user_id, limit, offset)` - Paginated user jobs

## Phase 3: API Endpoints (Next)

### 3.1 Document Processing Service

**Update:** `services/document-processing/api/v1/endpoints.py`

New endpoints:
```python
@router.post("/batch-upload")
async def batch_upload(files: List[UploadFile], user_id: str = None)
    # Create batch_id
    # Save files
    # Queue process_batch_task
    # Return batch_id and job_ids

@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str)
    # Return job details with steps

@router.get("/batches/{batch_id}")
async def get_batch_status(batch_id: str)
    # Return all jobs in batch with aggregate status

@router.post("/jobs/{job_id}/cancel")
async def cancel_job(job_id: str)
    # Cancel running job

@router.post("/documents/{document_id}/reprocess")
async def reprocess_document(document_id: int, apply_ocr: bool = False)
    # Queue reprocessing task
```

### 3.2 API Gateway

**Update:** `services/api-gateway/api/v1/workflow_endpoints.py`

New endpoints (proxying to document-processing):
```python
@router.post("/batch-upload")
async def batch_upload_gateway(...)
    # Proxy to document-processing with auth

@router.get("/jobs/{job_id}")
async def get_job_status_gateway(job_id: str)
    # Proxy with auth check

@router.get("/batches")
async def list_user_batches(...)
    # Get authenticated user's batches
```

## Phase 4: Frontend (Next)

### 4.1 Batch Upload Component

**Create:** `frontend/src/app/batch-upload/page.tsx`

Features:
- Multi-file drag & drop
- File list with individual progress bars
- Batch progress aggregation
- Real-time status updates (WebSocket or polling)
- Cancel individual files or entire batch

### 4.2 Processing Status Page

**Create:** `frontend/src/app/jobs/page.tsx`

Features:
- List user's processing jobs
- Filter by status
- View detailed processing steps
- Retry failed jobs

### 4.3 UI Components

**Create:** `frontend/src/components/BatchUploader.tsx`
- File selection UI
- Progress visualization
- Status indicators

**Create:** `frontend/src/components/JobStatusCard.tsx`
- Job summary display
- Progress bar
- Step details collapse

## Phase 5: Docker & Deployment

### 5.1 Docker Compose Updates

**Update:** `docker-compose.yml`

Add services:
```yaml
celery-worker:
  build: ./services/document-processing
  command: celery -A celery_app worker --loglevel=info -Q document_processing,batch_processing
  depends_on:
    - redis
    - postgres
  volumes:
    - ./uploads_data:/app/uploads

celery-beat:
  # For scheduled tasks (cleanup, monitoring)
  
flower:
  # Celery monitoring UI
  image: mher/flower:2.0.1
  ports:
    - "5555:5555"
```

### 5.2 System Dependencies

**Dockerfile updates needed:**
```dockerfile
# Add Tesseract OCR and poppler-utils
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*
```

## Implementation Steps (Recommended Order)

1. ✅ **Run migration**: `docker exec document-processing-service alembic upgrade head`
2. ✅ **Update Docker image**: `docker-compose build document-processing`
3. **Create tasks.py** with basic processing task
4. **Update PDF parser** to use DOI extractor and OCR
5. **Create jobs_crud.py** for database operations
6. **Add batch upload endpoint** to document-processing
7. **Update API Gateway** to proxy batch endpoints
8. **Test with curl/Postman** before frontend work
9. **Add Celery worker** to docker-compose
10. **Create frontend batch upload component**
11. **Add job status monitoring UI**
12. **Load testing and optimization**

## Testing Strategy

### Unit Tests
- DOI extraction patterns
- OCR detection logic
- Task state transitions

### Integration Tests
- Full document processing flow
- Batch upload with multiple files
- Error handling and retries

### Performance Tests
- Concurrent batch uploads
- Worker scaling
- Large PDF handling (100+ pages)

## Configuration

### Environment Variables

Add to `.env`:
```bash
# OCR
TESSERACT_CMD=/usr/bin/tesseract
OCR_DPI=300
OCR_LANGUAGE=eng

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
CELERY_TASK_TIME_LIMIT=3600

# Processing
MAX_BATCH_SIZE=50
MAX_FILE_SIZE_MB=100
ENABLE_OCR=true
ENABLE_DOI_VALIDATION=true
```

## Monitoring & Observability

1. **Flower Dashboard** - http://localhost:5555
   - Active workers
   - Task throughput
   - Failed tasks

2. **Processing Logs** - Structured logging in `processing_steps` table
   - Track every step
   - Measure duration
   - Debug failures

3. **Metrics** (Future)
   - Average processing time per page
   - OCR usage percentage
   - DOI extraction success rate

## Next Steps

Would you like me to:
1. **Continue implementation** - Create tasks.py and CRUD operations?
2. **Update docker-compose** - Add Celery worker and system dependencies?
3. **Create API endpoints** - Batch upload and job management?
4. **Build frontend components** - Batch upload UI?

Let me know which part you'd like me to implement next!
