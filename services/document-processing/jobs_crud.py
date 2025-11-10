"""
CRUD Operations for Processing Jobs and Steps
"""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

from models import ProcessingJob, ProcessingStep, Document


class JobsCRUD:
    """CRUD operations for processing jobs"""
    
    @staticmethod
    def create_job(
        db: Session,
        filename: str,
        file_size: Optional[int] = None,
        batch_id: Optional[str] = None,
        user_id: Optional[str] = None,
        job_metadata: Optional[Dict[str, Any]] = None
    ) -> ProcessingJob:
        """Create a new processing job"""
        job_id = f"job_{uuid.uuid4().hex[:16]}"
        
        job = ProcessingJob(
            job_id=job_id,
            batch_id=batch_id,
            filename=filename,
            file_size=file_size,
            status='pending',
            progress=0,
            user_id=user_id,
            job_metadata=job_metadata or {},
            created_at=datetime.utcnow()
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        return job
    
    @staticmethod
    def get_job(db: Session, job_id: str) -> Optional[ProcessingJob]:
        """Get a job by ID"""
        return db.query(ProcessingJob).filter(ProcessingJob.job_id == job_id).first()
    
    @staticmethod
    def get_batch_jobs(db: Session, batch_id: str) -> List[ProcessingJob]:
        """Get all jobs in a batch"""
        return db.query(ProcessingJob).filter(ProcessingJob.batch_id == batch_id).all()
    
    @staticmethod
    def get_user_jobs(
        db: Session,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None
    ) -> List[ProcessingJob]:
        """Get jobs for a user with pagination"""
        query = db.query(ProcessingJob).filter(ProcessingJob.user_id == user_id)
        
        if status:
            query = query.filter(ProcessingJob.status == status)
        
        return query.order_by(ProcessingJob.created_at.desc()).limit(limit).offset(offset).all()
    
    @staticmethod
    def update_job_status(
        db: Session,
        job_id: str,
        status: str,
        progress: Optional[int] = None,
        error_message: Optional[str] = None,
        document_id: Optional[int] = None
    ) -> Optional[ProcessingJob]:
        """Update job status and progress"""
        job = JobsCRUD.get_job(db, job_id)
        
        if not job:
            return None
        
        job.status = status
        
        if progress is not None:
            job.progress = progress
        
        if error_message:
            job.error_message = error_message
        
        if document_id:
            job.document_id = document_id
        
        # Update timestamps based on status
        if status == 'processing' and not job.started_at:
            job.started_at = datetime.utcnow()
        elif status in ['completed', 'failed', 'cancelled']:
            job.completed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(job)
        
        return job
    
    @staticmethod
    def cancel_job(db: Session, job_id: str) -> bool:
        """Cancel a pending or processing job"""
        job = JobsCRUD.get_job(db, job_id)
        
        if not job or job.status in ['completed', 'failed', 'cancelled']:
            return False
        
        job.status = 'cancelled'
        job.completed_at = datetime.utcnow()
        
        db.commit()
        
        return True
    
    @staticmethod
    def add_processing_step(
        db: Session,
        job_id: str,
        step_name: str,
        status: str,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        duration_ms: Optional[int] = None
    ) -> ProcessingStep:
        """Add a processing step log entry"""
        step = ProcessingStep(
            job_id=job_id,
            step_name=step_name,
            status=status,
            message=message,
            details=details or {},
            started_at=started_at or datetime.utcnow(),
            completed_at=completed_at,
            duration_ms=duration_ms
        )
        
        db.add(step)
        db.commit()
        db.refresh(step)
        
        return step
    
    @staticmethod
    def get_job_steps(db: Session, job_id: str) -> List[ProcessingStep]:
        """Get all steps for a job"""
        return db.query(ProcessingStep).filter(
            ProcessingStep.job_id == job_id
        ).order_by(ProcessingStep.started_at).all()
    
    @staticmethod
    def get_batch_summary(db: Session, batch_id: str) -> Dict[str, Any]:
        """Get summary statistics for a batch"""
        jobs = JobsCRUD.get_batch_jobs(db, batch_id)
        
        total = len(jobs)
        by_status = {}
        total_progress = 0
        
        for job in jobs:
            status = job.status
            by_status[status] = by_status.get(status, 0) + 1
            total_progress += job.progress
        
        avg_progress = total_progress / total if total > 0 else 0
        
        return {
            'batch_id': batch_id,
            'total_jobs': total,
            'by_status': by_status,
            'average_progress': avg_progress,
            'completed': by_status.get('completed', 0),
            'failed': by_status.get('failed', 0),
            'processing': by_status.get('processing', 0),
            'pending': by_status.get('pending', 0),
            'cancelled': by_status.get('cancelled', 0),
        }
