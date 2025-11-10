"""
Celery Tasks for Async Document Processing
"""
import asyncio
from celery import Task
from celery_app import celery_app
from sqlalchemy.orm import Session
import time
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from database import SessionLocal
from jobs_crud import JobsCRUD
from utils.pdf_parser import PDFParser
from utils.doi_extractor import DOIExtractor
from utils.ocr_processor import OCRProcessor
from vector_client import get_vector_client
import crud

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """Base task with database session management"""
    _db = None

    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None


@celery_app.task(base=DatabaseTask, bind=True, max_retries=3)
def process_document_task(
    self,
    job_id: str,
    file_path: str,
    original_filename: str,
    user_id: Optional[str] = None
):
    """
    Main document processing task
    
    Steps:
    1. Extract text (with OCR fallback)
    2. Extract DOI
    3. Parse structure (title, authors, sections)
    4. Extract tables, figures, references
    5. Store in database
    6. Send to vector DB for chunking/embedding
    """
    db = self.db
    start_time = time.time()
    
    try:
        # Update job to processing
        JobsCRUD.update_job_status(db, job_id, 'processing', progress=0)
        JobsCRUD.add_processing_step(db, job_id, 'start', 'started', 'Starting document processing')
        
        # Step 1: Initialize PDF parser
        logger.info(f"[{job_id}] Processing document: {original_filename}")
        JobsCRUD.update_job_status(db, job_id, 'processing', progress=10)
        
        step_start = time.time()
        parser = PDFParser(file_path)
        metadata = parser.extract_metadata()
        step_duration = int((time.time() - step_start) * 1000)
        JobsCRUD.add_processing_step(
            db, job_id, 'initialize_parser', 'completed',
            f'Initialized PDF parser for {original_filename}',
            details={'page_count': metadata.get('page_count', 0)},
            duration_ms=step_duration
        )
        
        # Step 2: Check if OCR is needed
        JobsCRUD.update_job_status(db, job_id, 'processing', progress=15)
        step_start = time.time()
        
        is_scanned, confidence = OCRProcessor.is_scanned_pdf(file_path)
        ocr_applied = False
        
        if is_scanned and confidence > 0.7:
            logger.info(f"[{job_id}] Scanned PDF detected (confidence={confidence:.2f}), applying OCR")
            JobsCRUD.add_processing_step(
                db, job_id, 'ocr_detection', 'completed',
                'Scanned PDF detected, will apply OCR',
                details={'is_scanned': is_scanned, 'confidence': confidence}
            )
            
            ocr_result = OCRProcessor.extract_text_with_ocr(file_path)
            
            if ocr_result['success']:
                ocr_applied = True
                full_text = ocr_result['full_text']
                step_duration = int((time.time() - step_start) * 1000)
                JobsCRUD.add_processing_step(
                    db, job_id, 'ocr_extraction', 'completed',
                    f'OCR completed: {ocr_result["total_chars"]} characters extracted',
                    details=ocr_result,
                    duration_ms=step_duration
                )
            else:
                logger.warning(f"[{job_id}] OCR failed, falling back to regular extraction")
                full_text = parser.extract_text()
        else:
            full_text = parser.extract_text()
            JobsCRUD.add_processing_step(
                db, job_id, 'ocr_detection', 'completed',
                'Text-based PDF, OCR not needed',
                details={'is_scanned': is_scanned, 'confidence': confidence}
            )
        
        # Step 3: Extract DOI
        JobsCRUD.update_job_status(db, job_id, 'processing', progress=25)
        step_start = time.time()
        
        # Try to extract DOI from text and validate
        doi = DOIExtractor.extract_and_validate(full_text, validate=True)
        
        if not doi:
            # Try PDF metadata - extract from metadata dict that was already retrieved
            doi = None  # DOI extraction from metadata is done in extract_and_validate above
        
        step_duration = int((time.time() - step_start) * 1000)
        JobsCRUD.add_processing_step(
            db, job_id, 'doi_extraction', 'completed',
            f'DOI extracted: {doi}' if doi else 'No DOI found',
            details={'doi': doi},
            duration_ms=step_duration
        )
        
        # Step 4: Parse document structure
        JobsCRUD.update_job_status(db, job_id, 'processing', progress=35)
        step_start = time.time()
        
        # Use TextProcessor to extract sections from full text
        from utils.text_processor import TextProcessor
        processor = TextProcessor(full_text)
        sections = processor.extract_sections()
        
        step_duration = int((time.time() - step_start) * 1000)
        JobsCRUD.add_processing_step(
            db, job_id, 'structure_parsing', 'completed',
            f'Parsed structure: {len([s for s in sections.values() if s])} sections found',
            details={
                'title': metadata.get('title'),
                'authors': metadata.get('authors'),
                'sections_found': list(sections.keys())
            },
            duration_ms=step_duration
        )
        
        # Step 5: Extract tables
        JobsCRUD.update_job_status(db, job_id, 'processing', progress=50)
        step_start = time.time()
        
        tables_data = parser.extract_tables()
        
        step_duration = int((time.time() - step_start) * 1000)
        JobsCRUD.add_processing_step(
            db, job_id, 'table_extraction', 'completed',
            f'Extracted {len(tables_data)} tables',
            details={'table_count': len(tables_data)},
            duration_ms=step_duration
        )
        
        # Step 6: Extract figures
        JobsCRUD.update_job_status(db, job_id, 'processing', progress=60)
        step_start = time.time()
        
        figures_metadata = parser.extract_figures()
        
        step_duration = int((time.time() - step_start) * 1000)
        JobsCRUD.add_processing_step(
            db, job_id, 'figure_extraction', 'completed',
            f'Extracted {len(figures_metadata)} figures',
            details={'figure_count': len(figures_metadata)},
            duration_ms=step_duration
        )
        
        # Step 7: Extract references
        JobsCRUD.update_job_status(db, job_id, 'processing', progress=70)
        step_start = time.time()
        
        references_json = parser.extract_references()
        
        step_duration = int((time.time() - step_start) * 1000)
        JobsCRUD.add_processing_step(
            db, job_id, 'reference_extraction', 'completed',
            f'Extracted {len(references_json)} references',
            details={'reference_count': len(references_json)},
            duration_ms=step_duration
        )
        
        # Step 8: Create document record
        JobsCRUD.update_job_status(db, job_id, 'processing', progress=80)
        step_start = time.time()
        
        # Prepare document data as a dictionary
        document_data = {
            "filename": Path(file_path).name,
            "original_filename": original_filename,
            "file_path": file_path,
            "file_size": Path(file_path).stat().st_size,
            "page_count": metadata.get('page_count', 0),
            "title": metadata.get('title'),
            "authors": metadata.get('authors', []),
            "abstract": sections.get('abstract'),
            "introduction": sections.get('introduction'),
            "methodology": sections.get('methodology'),
            "results": sections.get('results'),
            "conclusion": sections.get('conclusion'),
            "references": sections.get('references'),
            "full_text": full_text,
            "upload_date": datetime.now(),
            "tables_data": tables_data,
            "figures_metadata": figures_metadata,
            "references_json": references_json,
            "tables_extracted": bool(tables_data),
            "figures_extracted": bool(figures_metadata),
            "references_extracted": bool(references_json),
            "doi": doi,
            "ocr_applied": ocr_applied,
            "processing_job_id": job_id
        }
        
        document = crud.create_document(db, document_data)
        
        step_duration = int((time.time() - step_start) * 1000)
        JobsCRUD.add_processing_step(
            db, job_id, 'database_storage', 'completed',
            f'Document saved to database with ID {document.id}',
            details={'document_id': document.id},
            duration_ms=step_duration
        )
        
        # Step 9: Send to vector DB (sync call to async function)
        JobsCRUD.update_job_status(db, job_id, 'processing', progress=90)
        step_start = time.time()
        
        try:
            vector_client = get_vector_client()
            # Run async function in event loop
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                # Filter out None values from sections for vector DB
                sections_filtered = {k: v for k, v in sections.items() if v is not None}
                loop.run_until_complete(
                    vector_client.process_document(
                        document_id=document.id,
                        full_text=full_text,
                        sections=sections_filtered if sections_filtered else None
                    )
                )
            finally:
                loop.close()
            
            step_duration = int((time.time() - step_start) * 1000)
            JobsCRUD.add_processing_step(
                db, job_id, 'vector_db_indexing', 'completed',
                'Document indexed in vector database',
                duration_ms=step_duration
            )
        except Exception as e:
            logger.warning(f"[{job_id}] Vector DB indexing failed: {e}")
            JobsCRUD.add_processing_step(
                db, job_id, 'vector_db_indexing', 'failed',
                f'Vector DB indexing failed: {str(e)}'
            )
        
        # Complete the job
        total_duration = int((time.time() - start_time) * 1000)
        JobsCRUD.update_job_status(
            db, job_id, 'completed', progress=100, document_id=document.id
        )
        JobsCRUD.add_processing_step(
            db, job_id, 'completion', 'completed',
            f'Processing completed successfully in {total_duration}ms',
            details={'document_id': document.id, 'total_duration_ms': total_duration}
        )
        
        logger.info(f"[{job_id}] Processing completed successfully: document_id={document.id}")
        
        return {
            'success': True,
            'job_id': job_id,
            'document_id': document.id,
            'duration_ms': total_duration
        }
        
    except Exception as e:
        logger.error(f"[{job_id}] Processing failed: {e}", exc_info=True)
        
        error_msg = str(e)
        JobsCRUD.update_job_status(db, job_id, 'failed', error_message=error_msg)
        JobsCRUD.add_processing_step(
            db, job_id, 'error', 'failed',
            f'Processing failed: {error_msg}'
        )
        
        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(f"[{job_id}] Retrying task (attempt {self.request.retries + 1}/{self.max_retries})")
            raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
        
        return {
            'success': False,
            'job_id': job_id,
            'error': error_msg
        }


@celery_app.task(base=DatabaseTask, bind=True)
def process_batch_task(
    self,
    batch_id: str,
    file_data_list: List[Dict[str, Any]],
    user_id: Optional[str] = None
):
    """
    Process a batch of documents
    
    Creates individual processing jobs and monitors overall progress
    """
    db = self.db
    
    try:
        logger.info(f"[{batch_id}] Starting batch processing: {len(file_data_list)} files")
        
        job_ids = []
        
        # Create individual jobs for each file
        for file_data in file_data_list:
            job = JobsCRUD.create_job(
                db=db,
                filename=file_data['filename'],
                file_size=file_data.get('file_size'),
                batch_id=batch_id,
                user_id=user_id,
                job_metadata={'original_index': file_data.get('index', 0)}
            )
            job_ids.append(job.job_id)
            
            # Queue individual processing task
            process_document_task.delay(
                job.job_id,
                file_data['file_path'],
                file_data['filename'],
                user_id
            )
        
        logger.info(f"[{batch_id}] Queued {len(job_ids)} processing jobs")
        
        return {
            'success': True,
            'batch_id': batch_id,
            'job_ids': job_ids,
            'total_files': len(file_data_list)
        }
        
    except Exception as e:
        logger.error(f"[{batch_id}] Batch processing failed: {e}", exc_info=True)
        return {
            'success': False,
            'batch_id': batch_id,
            'error': str(e)
        }


@celery_app.task(base=DatabaseTask, bind=True)
def extract_doi_task(self, document_id: int):
    """
    Extract and validate DOI for an existing document
    """
    db = self.db
    
    try:
        document = crud.get_document(db, document_id)
        
        if not document:
            return {'success': False, 'error': 'Document not found'}
        
        if document.doi:
            logger.info(f"Document {document_id} already has DOI: {document.doi}")
            return {'success': True, 'doi': document.doi, 'updated': False}
        
        # Extract from full text
        doi = DOIExtractor.extract_and_validate(document.full_text, validate=True)
        
        if doi:
            document.doi = doi
            db.commit()
            logger.info(f"DOI extracted for document {document_id}: {doi}")
            return {'success': True, 'doi': doi, 'updated': True}
        else:
            logger.info(f"No DOI found for document {document_id}")
            return {'success': True, 'doi': None, 'updated': False}
            
    except Exception as e:
        logger.error(f"DOI extraction failed for document {document_id}: {e}")
        return {'success': False, 'error': str(e)}


@celery_app.task(base=DatabaseTask, bind=True)
def apply_ocr_task(self, document_id: int, force: bool = False):
    """
    Apply OCR to an existing document
    """
    db = self.db
    
    try:
        document = crud.get_document(db, document_id)
        
        if not document:
            return {'success': False, 'error': 'Document not found'}
        
        if document.ocr_applied and not force:
            logger.info(f"Document {document_id} already has OCR applied")
            return {'success': True, 'ocr_applied': True, 'updated': False}
        
        # Apply OCR
        result = OCRProcessor.extract_with_fallback(document.file_path, force_ocr=True)
        
        if result['success'] and result.get('ocr_applied'):
            # Update document with OCR text
            document.full_text = result['full_text']
            document.ocr_applied = True
            db.commit()
            
            logger.info(f"OCR applied to document {document_id}")
            return {'success': True, 'ocr_applied': True, 'updated': True}
        else:
            return {'success': False, 'error': result.get('error', 'OCR not needed')}
            
    except Exception as e:
        logger.error(f"OCR application failed for document {document_id}: {e}")
        return {'success': False, 'error': str(e)}
