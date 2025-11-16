# Celery Infrastructure Setup - Complete

## Overview
Successfully implemented the Celery task queue infrastructure for async document processing with OCR, DOI extraction, and batch upload capabilities.

## ✅ Completed Components

### 1. Database Schema & Models (`services/document-processing/models.py`)
- **ProcessingJob model**: Tracks individual document processing jobs
  - Fields: job_id (PK), batch_id, document_id (FK), filename, file_size, status (enum), progress (0-100), error_message, timestamps, user_id, metadata (JSONB)
  - Status enum: pending, processing, completed, failed, cancelled
  - Relationships: many-to-one with Document, one-to-many with ProcessingStep

- **ProcessingStep model**: Audit log for granular processing steps
  - Fields: id (PK), job_id (FK), step_name, status, message, details (JSONB), duration_ms, timestamp
  - Tracks each stage: OCR detection, DOI extraction, table/figure extraction, etc.

- **Document model extensions**:
  - `doi` (String): Extracted and validated DOI
  - `batch_id` (String): Groups documents uploaded together
  - `processing_job_id` (FK): Links to processing job
  - `ocr_applied` (Boolean): Indicates if OCR was used

### 2. Database Migration (`alembic/versions/20251110_01_processing_jobs.py`)
✅ Successfully applied migration
- Created processing_jobs and processing_steps tables
- Extended documents table with new fields
- Fixed revision chain issues and duplicate column errors
- Verified via psql queries - all tables and columns exist

### 3. Utility Modules

#### DOI Extractor (`utils/doi_extractor.py`)
- **DOI regex patterns**: Multiple format support (10.xxxx/xxxxx, doi:, http://doi.org/)
- **CrossRef API validation**: Real-time DOI validation with metadata enrichment
- **PDF metadata extraction**: Fallback to PDF metadata for DOI discovery
- Methods:
  - `extract_dois(text)`: Find all DOIs in text
  - `validate_doi(doi)`: Verify via CrossRef API, get metadata
  - `extract_and_validate(text, validate=True)`: Combined extraction + validation
  - `extract_from_pdf_metadata(metadata)`: Parse DOI from PDF info dict

#### OCR Processor (`utils/ocr_processor.py`)
- **Scanned PDF detection**: Text density heuristic (<50 chars/page)
- **Tesseract OCR integration**: Converts PDF pages to images at 300 DPI
- **Automatic fallback**: Only applies OCR when needed
- Methods:
  - `is_scanned_pdf(pdf_path)`: Returns (is_scanned, confidence)
  - `extract_text_with_ocr(pdf_path, dpi=300, lang='eng')`: Full OCR extraction
  - `extract_with_fallback(pdf_path, force_ocr=False)`: Smart OCR decision

#### Jobs CRUD (`jobs_crud.py`)
- **JobsCRUD class**: Static methods for database operations
- Methods:
  - `create_job()`: Generate job_id, create record
  - `get_job(db, job_id)`: Retrieve job with details
  - `get_batch_jobs(db, batch_id)`: All jobs in a batch
  - `get_user_jobs(db, user_id, limit, skip)`: User's processing history
  - `update_job_status(db, job_id, status, progress, error_message, document_id)`: Update job state
  - `cancel_job(db, job_id)`: Cancel running job
  - `add_processing_step(db, job_id, step_name, status, message, details, duration_ms)`: Audit logging
  - `get_job_steps(db, job_id)`: Retrieve step history
  - `get_batch_summary(db, batch_id)`: Aggregate batch statistics

### 4. Celery Configuration (`celery_app.py`)
- **Broker/Backend**: Redis (redis://redis:6379/0)
- **Task routing**: 4 specialized queues
  - `document_processing`: Main processing pipeline
  - `batch_processing`: Batch coordination
  - `metadata_extraction`: DOI extraction tasks
  - `ocr_processing`: OCR-intensive tasks
- **Worker limits**: 3600s hard timeout, 3000s soft timeout, prefetch_multiplier=1, acks_late=True
- **DatabaseTask base class**: Automatic session management with cleanup

### 5. Celery Tasks (`tasks.py`)

#### `process_document_task(job_id, file_path, original_filename, user_id)`
Main async processing pipeline with 9 steps:
1. **Initialize PDF parser**: Load PDF and extract metadata
2. **OCR detection & application**: Check if scanned (>70% confidence), apply Tesseract if needed
3. **DOI extraction**: Extract from text + CrossRef validation
4. **Structure parsing**: Extract sections (abstract, intro, methodology, results, conclusion)
5. **Table extraction**: Parse table structures
6. **Figure extraction**: Extract images with captions
7. **Reference extraction**: Parse citations
8. **Database storage**: Create Document record with all extracted data
9. **Vector DB indexing**: Send to vector-db service for embedding generation

- **Progress tracking**: Updates job.progress from 0% to 100% at each step
- **Audit logging**: Logs each step to processing_steps table with duration_ms
- **Error handling**: Retries up to 3 times with exponential backoff (60s, 120s, 240s)
- **Event loop management**: Properly handles async vector_client calls in sync Celery task

#### `process_batch_task(batch_id, file_data_list, user_id)`
Batch coordinator:
- Creates individual ProcessingJob for each file
- Queues process_document_task for parallel processing
- Returns batch summary with job_ids

#### `extract_doi_task(document_id)`
Async DOI extraction for existing documents:
- Skips if DOI already exists
- Extracts from full_text + validates via CrossRef
- Updates document record

#### `apply_ocr_task(document_id, force=False)`
Reprocess existing document with OCR:
- Skips if ocr_applied=True unless force=True
- Applies Tesseract OCR to file_path
- Updates document.full_text and ocr_applied flag

### 6. Docker Infrastructure

#### Updated Dockerfile (`services/document-processing/Dockerfile`)
Added OCR system dependencies:
```dockerfile
tesseract-ocr          # OCR engine
tesseract-ocr-eng      # English language data
poppler-utils          # PDF to image conversion (already present)
```

#### Updated docker-compose.yml
Added 2 new services:

**celery-worker**:
- Image: Uses document-processing build
- Queues: document_processing, batch_processing, metadata_extraction, ocr_processing
- Concurrency: 2 workers
- Volumes: Same as document-processing (code + uploads)
- Dependencies: postgres, redis, migrate
- Profile: phase4
- Command: `celery -A celery_app worker --loglevel=info -Q ... --concurrency=2`

**flower** (monitoring):
- Image: mher/flower:2.0.1
- Port: 5555 (http://localhost:5555)
- Broker/Backend: Redis
- Profile: phase4
- Purpose: Web UI for Celery task monitoring, stats, worker management

## 🔧 Dependencies Added to requirements.txt
```
celery[redis]==5.3.4    # Task queue + Redis support
flower==2.0.1           # Monitoring web UI
pytesseract==0.3.10     # Tesseract OCR wrapper
pdf2image==1.16.3       # PDF to image conversion
Pillow==10.1.0          # Image processing
requests==2.31.0        # HTTP client (CrossRef API)
```

## 📋 Usage

### Starting Services
```bash
# Start all Phase 4 services (includes Celery workers)
docker-compose --profile phase4 up -d

# Check logs
docker logs -f celery-worker
docker logs -f flower-monitor

# Flower monitoring UI
open http://localhost:5555
```

### Testing Celery Tasks
```python
# In document-processing container
docker exec -it document-processing-service python

from tasks import process_document_task
from jobs_crud import JobsCRUD
from database import SessionLocal

db = SessionLocal()

# Create a job
job = JobsCRUD.create_job(
    db=db,
    filename="test.pdf",
    file_size=1024000,
    user_id="test_user"
)

# Queue processing task
result = process_document_task.delay(
    job.job_id,
    "/app/uploads/test.pdf",
    "test.pdf",
    "test_user"
)

# Check result
print(f"Task ID: {result.id}")
print(f"Status: {result.status}")

# Check job status
job = JobsCRUD.get_job(db, job.job_id)
print(f"Progress: {job.progress}%")
print(f"Status: {job.status}")

# Check processing steps
steps = JobsCRUD.get_job_steps(db, job.job_id)
for step in steps:
    print(f"{step.step_name}: {step.status} ({step.duration_ms}ms)")
```

## 🔄 Processing Flow

### Single Document Upload
```
User uploads PDF
    ↓
API endpoint creates ProcessingJob (status=pending)
    ↓
Queue process_document_task.delay(job_id, file_path, ...)
    ↓
Return job_id immediately to user
    ↓
[Background Celery Worker]
    ↓
Update job: status=processing, progress=10%
    ↓
Extract text (OCR if needed) → progress=25%
    ↓
Extract DOI (CrossRef validation) → progress=35%
    ↓
Parse sections → progress=50%
    ↓
Extract tables/figures/references → progress=70%
    ↓
Save to database → progress=80%
    ↓
Send to vector DB → progress=90%
    ↓
Update job: status=completed, progress=100%
    ↓
Log all steps to processing_steps table
```

### Batch Upload
```
User uploads multiple PDFs
    ↓
API creates batch_id (UUID)
    ↓
Queue process_batch_task.delay(batch_id, file_data_list, ...)
    ↓
Return batch_id immediately
    ↓
[Background Celery Worker]
    ↓
Create ProcessingJob for each file
    ↓
Queue individual process_document_task for each
    ↓
Each document processes in parallel (up to concurrency=2)
    ↓
User can query GET /batches/{batch_id} for summary
```

## 📊 Monitoring

### Database Queries
```sql
-- Check job status
SELECT job_id, filename, status, progress, error_message 
FROM processing_jobs 
WHERE job_id = 'xxx';

-- Check processing steps
SELECT step_name, status, message, duration_ms, timestamp
FROM processing_steps
WHERE job_id = 'xxx'
ORDER BY timestamp;

-- Batch summary
SELECT batch_id, COUNT(*) as total,
       SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
       SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
FROM processing_jobs
GROUP BY batch_id;
```

### Flower UI
- Workers: http://localhost:5555/workers
- Tasks: http://localhost:5555/tasks
- Monitor: http://localhost:5555/monitor

## 🚧 Next Steps (Remaining Todos)

### 6. Create batch upload API endpoints
**File**: `services/document-processing/api/v1/endpoints.py`
```python
@router.post("/batch-upload")
async def batch_upload(files: List[UploadFile], ...):
    # Generate batch_id
    # Save all files to uploads/
    # Queue process_batch_task.delay()
    # Return batch_id

@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    # Return JobsCRUD.get_job() with steps

@router.get("/batches/{batch_id}")
async def get_batch_status(batch_id: str, db: Session = Depends(get_db)):
    # Return JobsCRUD.get_batch_summary()

@router.post("/jobs/{job_id}/cancel")
async def cancel_job(job_id: str, db: Session = Depends(get_db)):
    # Call JobsCRUD.cancel_job()

@router.post("/documents/{document_id}/reprocess")
async def reprocess_document(document_id: int, force_ocr: bool = False, ...):
    # Queue apply_ocr_task.delay() or process_document_task.delay()
```

### 7. Add API Gateway proxy endpoints
**File**: `services/api-gateway/api/v1/workflow_endpoints.py`
- POST /api/v1/batch-upload → document-processing/batch-upload (with auth)
- GET /api/v1/jobs/{job_id} → document-processing/jobs/{job_id} (with auth)
- GET /api/v1/batches → document-processing/batches (filtered by user_id)
- GET /api/v1/batches/{batch_id} → document-processing/batches/{batch_id} (with auth)

### 8. Implement frontend batch upload UI
**File**: `frontend/src/app/batch-upload/page.tsx`
- Multi-file input with drag-and-drop
- Progress bars for each file
- Job status polling (GET /jobs/{job_id} every 2s)
- Batch summary view
- Error handling and retry

### 9. Improve section detection accuracy
**File**: `services/document-processing/utils/text_processor.py`
- Better regex patterns for section headers
- Font size/style analysis (if available)
- Layout-based detection (indentation, spacing)
- ML-based section classification (future)

## 📝 Testing Checklist

Before testing, rebuild and restart:
```bash
docker-compose --profile phase4 down
docker-compose build document-processing  # Includes OCR dependencies
docker-compose --profile phase4 up -d
```

- [ ] Celery worker starts without errors
- [ ] Flower UI accessible at http://localhost:5555
- [ ] process_document_task processes PDF successfully
- [ ] OCR detection works for scanned PDFs
- [ ] DOI extraction with CrossRef validation
- [ ] Processing steps logged to database
- [ ] Job progress updates correctly (0% → 100%)
- [ ] Vector DB indexing completes
- [ ] Error handling and retries work
- [ ] Batch processing queues multiple jobs

## 🐛 Known Issues / Limitations

1. **Linter warnings**: `.delay()` method shows as unknown (false positive - added by Celery decorator at runtime)
2. **Synchronous event loop**: Using `asyncio.run_until_complete()` in Celery task for vector_client (acceptable pattern)
3. **No progress websockets yet**: Frontend will need to poll GET /jobs/{job_id} for status (websockets can be added later)
4. **No distributed task locking**: If same file uploaded twice, both will process (can add Redis locks if needed)
5. **File cleanup**: Uploaded files are never deleted (implement retention policy later)

## 📚 Related Documentation
- See `DOCUMENT_PROCESSING_ENHANCEMENT.md` for original implementation plan
- See `alembic/versions/20251110_01_processing_jobs.py` for migration details
- See `.github/copilot-instructions.md` for updated project context
