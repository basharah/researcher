"""
API v1 - Document Processing Endpoints
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pathlib import Path
import logging

from database import get_db
from utils.pdf_parser import PDFParser
from utils.text_processor import TextProcessor
from schemas import (
    DocumentResponse,
    TableData,
    FigureMetadata,
    ReferenceItem,
)
from api.v1.search_schemas import SearchRequest, SearchResponse
from config import settings
import crud
from vector_client import get_vector_client

# Create API router
router = APIRouter()
logger = logging.getLogger(__name__)


async def process_in_vector_db(document_id: int, full_text: str, sections: dict):
    """
    Background task to send document to Vector DB for processing
    
    Args:
        document_id: ID of the document
        full_text: Complete document text
        sections: Dictionary of extracted sections
    """
    logger.info(f"🔄 Background task started for document {document_id}")
    try:
        vector_client = get_vector_client()
        logger.info(f"📡 Sending document {document_id} to Vector DB...")
        result = await vector_client.process_document(
            document_id=document_id,
            full_text=full_text,
            sections=sections
        )
        if result:
            logger.info(f"✅ Document {document_id} successfully processed in Vector DB")
        else:
            logger.warning(f"⚠️  Document {document_id} processing in Vector DB returned None")
    except Exception as e:
        logger.error(f"Error processing document {document_id} in Vector DB: {e}")


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a research paper PDF
    
    - **file**: PDF file to upload (max 10MB)
    
    After successful upload and processing, the document will be automatically
    sent to the Vector DB service for chunking and embedding generation.
    """
    # Validate file type
    if not file.filename or not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Read file content
    contents = await file.read()
    file_size = len(contents)
    
    # Validate file size
    if file_size > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {settings.max_file_size / 1024 / 1024}MB"
        )
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = settings.upload_dir / safe_filename
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(contents)
    
    try:
        # Parse PDF
        parser = PDFParser(str(file_path))
        metadata = parser.extract_metadata()
        text_content = parser.extract_text()
        # Comprehensive extraction
        figures_dir = settings.upload_dir / 'figures'
        tables = parser.extract_tables()
        figures = parser.extract_figures(output_dir=figures_dir)
        references_struct = parser.extract_references()
        
        # Process text to extract sections
        processor = TextProcessor(text_content)
        sections = processor.extract_sections()
        
        # Prepare document data
        document_data = {
            "filename": safe_filename,
            "original_filename": file.filename,
            "file_path": str(file_path),
            "file_size": file_size,
            "page_count": metadata.get('page_count', 0),
            "title": metadata.get('title'),
            "authors": metadata.get('authors', []),
            "abstract": sections.get('abstract'),
            "introduction": sections.get('introduction'),
            "methodology": sections.get('methodology'),
            "results": sections.get('results'),
            "conclusion": sections.get('conclusion'),
            "references": sections.get('references'),
            "full_text": text_content,
            "upload_date": datetime.now(),
            # New fields
            "tables_data": tables,
            "figures_metadata": figures,
            "references_json": references_struct,
            "tables_extracted": bool(tables),
            "figures_extracted": bool(figures),
            "references_extracted": bool(references_struct),
        }
        
        # Create document using CRUD
        document = crud.create_document(db, document_data)
        
        # Send to Vector DB in background (non-blocking)
        if settings.enable_vector_db:
            logger.info(f"📋 Scheduling Vector DB processing for document {document.id}")
            # IMPORTANT: use injected BackgroundTasks (not a manually created instance)
            background_tasks.add_task(
                process_in_vector_db,
                document.id,
                text_content,
                sections
            )
            logger.info(f"✅ Scheduled Vector DB processing for document {document.id}")
        
        return DocumentResponse.model_validate(document)
        
    except Exception as e:
        # Clean up file on error
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing PDF: {str(e)}"
        )


@router.post("/upload-async")
async def upload_document_async(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a research paper PDF with asynchronous Celery processing
    
    This endpoint uses Celery for background processing, making it suitable
    for production deployments with multiple workers.
    
    - **file**: PDF file to upload (max 10MB)
    
    Returns a job_id for tracking processing status via /jobs/{job_id}
    """
    import uuid
    from tasks import process_document_task
    from jobs_crud import JobsCRUD
    
    # Validate file type
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Read file content
    contents = await file.read()
    file_size = len(contents)
    
    # Validate file size
    if file_size > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {settings.max_file_size / 1024 / 1024}MB"
        )
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = settings.upload_dir / safe_filename
    
    # Save file
    try:
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Create processing job
        job = JobsCRUD.create_job(
            db=db,
            filename=file.filename,
            file_size=file_size,
            user_id=None,  # TODO: Get from auth context
            job_metadata={"upload_type": "async", "upload_timestamp": datetime.now().isoformat()}
        )
        
        # Queue Celery task for processing
        result = process_document_task.delay(
            job.job_id,
            str(file_path),
            file.filename,
            None  # user_id
        )
        
        logger.info(f"📤 Async upload queued: {file.filename} -> Job {job.job_id}, Task {result.id}")
        
        return {
            "success": True,
            "message": "Document upload successful, processing queued",
            "job_id": job.job_id,
            "task_id": result.id,
            "filename": file.filename,
            "status_endpoint": f"/jobs/{job.job_id}"
        }
        
    except Exception as e:
        # Clean up file on error
        if file_path.exists():
            file_path.unlink()
        
        logger.error(f"Async upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing upload: {str(e)}"
        )


@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    List all uploaded documents
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    documents = crud.get_documents(db, skip=skip, limit=limit)
    return [DocumentResponse.model_validate(doc) for doc in documents]


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document_by_id(document_id: int, db: Session = Depends(get_db)):
    """
    Get details of a specific document
    
    - **document_id**: ID of the document
    """
    document = crud.get_document(db, document_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    
    return DocumentResponse.model_validate(document)


@router.get("/documents/{document_id}/sections")
async def get_document_sections(document_id: int, db: Session = Depends(get_db)):
    """
    Get all extracted sections from a document
    
    - **document_id**: ID of the document
    """
    document = crud.get_document(db, document_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    
    return {
        "document_id": document.id,
        "title": document.title,
        "sections": {
            "abstract": document.abstract,
            "introduction": document.introduction,
            "methodology": document.methodology,
            "results": document.results,
            "conclusion": document.conclusion,
            "references": document.references
        }
    }


@router.get("/documents/{document_id}/tables", response_model=List[TableData])
async def get_document_tables(document_id: int, db: Session = Depends(get_db)):
    """Return all extracted tables for a document"""
    document = crud.get_document(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document.tables_data or []


@router.get("/documents/{document_id}/figures", response_model=List[FigureMetadata])
async def get_document_figures(document_id: int, db: Session = Depends(get_db)):
    """Return all extracted figures metadata for a document"""
    document = crud.get_document(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document.figures_metadata or []


@router.get("/documents/{document_id}/references/structured", response_model=List[ReferenceItem])
async def get_document_references_structured(document_id: int, db: Session = Depends(get_db)):
    """Return structured references for a document"""
    document = crud.get_document(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document.references_json or []


@router.get("/documents/{document_id}/figure-file/{figure_num}")
async def get_figure_image(document_id: int, figure_num: int, db: Session = Depends(get_db)):
    """Serve a specific figure image file by number"""
    document = crud.get_document(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    figures_meta: List[dict] = document.figures_metadata if isinstance(document.figures_metadata, list) else []
    match_path: Optional[str] = None
    for fig in figures_meta:
        try:
            num = fig.get('figure_num') if isinstance(fig, dict) else None
            if num is not None and int(str(num)) == figure_num:
                match_path = fig.get('file_path')
                break
        except Exception:
            continue
    if not match_path:
        raise HTTPException(status_code=404, detail="Figure not found")
    path = Path(match_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Figure file missing")
    # Let FastAPI serve the file
    return FileResponse(path)


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document_by_id(document_id: int, db: Session = Depends(get_db)):
    """
    Delete a document
    
    - **document_id**: ID of the document to delete
    
    Also deletes the document's chunks from the Vector DB.
    """
    document = crud.get_document(db, document_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    
    # Delete from Vector DB
    if settings.enable_vector_db:
        vector_client = get_vector_client()
        await vector_client.delete_document_chunks(document_id)
        logger.info(f"Deleted Vector DB chunks for document {document_id}")
    
    # Delete file from disk
    file_path = Path(str(document.file_path))
    if file_path.exists():
        file_path.unlink()
    
    # Delete from database using CRUD
    crud.delete_document(db, document_id)
    
    return None


@router.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """
    Semantic search across all documents using Vector DB
    
    - **query**: Search query text
    - **max_results**: Maximum number of results (1-50)
    - **document_id**: Optional filter by specific document
    - **section**: Optional filter by section
    
    Returns chunks of text semantically similar to the query.
    Requires Vector DB service to be running.
    """
    if not settings.enable_vector_db:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vector DB integration is disabled"
        )
    
    vector_client = get_vector_client()
    
    # Check Vector DB health
    is_healthy = await vector_client.health_check()
    if not is_healthy:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vector DB service is not available"
        )
    
    # Perform search
    result = await vector_client.search(
        query=request.query,
        max_results=request.max_results,
        document_id=request.document_id,
        section=request.section
    )
    
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error performing search in Vector DB"
        )
    
    return SearchResponse(**result)


# ============================================================================
# Batch Upload & Job Management Endpoints
# ============================================================================

@router.post("/batch-upload")
async def batch_upload(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload multiple PDF documents for batch processing
    
    Returns batch_id and list of job_ids for tracking
    """
    import uuid
    from tasks import process_batch_task
    
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided"
        )
    
    # Generate batch ID
    batch_id = f"batch_{uuid.uuid4().hex[:16]}"
    
    # Validate and save all files
    file_data_list = []
    saved_files = []  # Track for cleanup on error
    
    try:
        for idx, file in enumerate(files):
            # Validate file type
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File {file.filename} is not a PDF"
                )
            
            # Generate safe filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"{timestamp}_{idx}_{file.filename}"
            file_path = settings.upload_dir / safe_filename
            
            # Save file
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            saved_files.append(file_path)
            
            # Prepare file data for batch task
            file_data_list.append({
                'filename': file.filename,
                'file_path': str(file_path),
                'file_size': len(content),
                'index': idx
            })
        
        # Queue batch processing task
        result = process_batch_task.delay(
            batch_id=batch_id,
            file_data_list=file_data_list,
            user_id=None  # TODO: Get from auth context
        )
        
        logger.info(f"Batch upload queued: {batch_id} with {len(files)} files")
        
        return {
            "success": True,
            "batch_id": batch_id,
            "total_files": len(files),
            "message": f"Batch processing started for {len(files)} files",
            "task_id": result.id
        }
        
    except Exception as e:
        # Clean up saved files on error
        for file_path in saved_files:
            if file_path.exists():
                file_path.unlink()
        
        logger.error(f"Batch upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch upload failed: {str(e)}"
        )


@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """
    Get status and details of a processing job
    
    Returns job info with processing steps
    """
    from jobs_crud import JobsCRUD
    
    job = JobsCRUD.get_job(db, job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )
    
    # Get processing steps
    steps = JobsCRUD.get_job_steps(db, job_id)
    
    return {
        "job": job.to_dict(),
        "steps": [
            {
                "step_name": step.step_name,
                "status": step.status,
                "message": step.message,
                "details": step.details,
                "duration_ms": step.duration_ms,
                "started_at": step.started_at.isoformat() if step.started_at else None,
                "completed_at": step.completed_at.isoformat() if step.completed_at else None
            }
            for step in steps
        ]
    }


@router.get("/batches/{batch_id}")
async def get_batch_status(batch_id: str, db: Session = Depends(get_db)):
    """
    Get summary and status of all jobs in a batch
    """
    from jobs_crud import JobsCRUD
    
    summary = JobsCRUD.get_batch_summary(db, batch_id)
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch {batch_id} not found"
        )
    
    return summary


@router.get("/batches")
async def list_batches(
    user_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    List all batches (optionally filtered by user_id)
    
    Returns list of batch summaries
    """
    from jobs_crud import JobsCRUD
    from models import ProcessingJob
    
    # Get distinct batch_ids
    query = db.query(ProcessingJob.batch_id).filter(ProcessingJob.batch_id.isnot(None))
    
    if user_id:
        query = query.filter(ProcessingJob.user_id == user_id)
    
    batch_ids = query.distinct().offset(skip).limit(limit).all()
    batch_ids = [b[0] for b in batch_ids]
    
    # Get summary for each batch
    batches = []
    for batch_id in batch_ids:
        summary = JobsCRUD.get_batch_summary(db, batch_id)
        if summary:
            batches.append(summary)
    
    return {
        "batches": batches,
        "total": len(batches)
    }


@router.post("/jobs/{job_id}/cancel")
async def cancel_job(job_id: str, db: Session = Depends(get_db)):
    """
    Cancel a processing job
    
    Note: Only pending or processing jobs can be cancelled
    """
    from jobs_crud import JobsCRUD
    
    job = JobsCRUD.get_job(db, job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )
    
    if job.status in ['completed', 'failed', 'cancelled']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel job in status: {job.status}"
        )
    
    JobsCRUD.cancel_job(db, job_id)
    
    # TODO: Revoke Celery task if it's running
    # from celery_app import celery_app
    # celery_app.control.revoke(task_id, terminate=True)
    
    return {
        "success": True,
        "message": f"Job {job_id} cancelled",
        "job_id": job_id
    }


@router.post("/documents/{document_id}/reprocess")
async def reprocess_document(
    document_id: int,
    force_ocr: bool = False,
    db: Session = Depends(get_db)
):
    """
    Reprocess an existing document
    
    Args:
        document_id: ID of document to reprocess
        force_ocr: If True, force OCR even if document already has OCR applied
    """
    from tasks import apply_ocr_task, process_document_task
    from jobs_crud import JobsCRUD
    
    # Get document
    document = crud.get_document(db, document_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )
    
    if force_ocr:
        # Queue OCR task
        result = apply_ocr_task.delay(document_id, force=True)
        
        return {
            "success": True,
            "message": f"OCR reprocessing queued for document {document_id}",
            "document_id": document_id,
            "task_id": result.id,
            "type": "ocr"
        }
    else:
        # Create new processing job for full reprocessing
        job = JobsCRUD.create_job(
            db=db,
            filename=document.original_filename,
            file_size=document.file_size,
            user_id=None,  # TODO: Get from auth
            job_metadata={"reprocess": True, "original_document_id": document_id}
        )
        
        # Queue full processing task
        result = process_document_task.delay(
            job.job_id,
            document.file_path,
            document.original_filename,
            None  # user_id
        )
        
        return {
            "success": True,
            "message": f"Full reprocessing queued for document {document_id}",
            "document_id": document_id,
            "job_id": job.job_id,
            "task_id": result.id,
            "type": "full"
        }


@router.get("/jobs")
async def list_jobs(
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    List processing jobs with optional filtering
    """
    from jobs_crud import JobsCRUD
    from models import ProcessingJob
    
    query = db.query(ProcessingJob)
    
    if user_id:
        query = query.filter(ProcessingJob.user_id == user_id)
    
    if status:
        query = query.filter(ProcessingJob.status == status)
    
    query = query.order_by(ProcessingJob.created_at.desc())
    jobs = query.offset(skip).limit(limit).all()
    
    return {
        "jobs": [job.to_dict() for job in jobs],
        "total": len(jobs)
    }


