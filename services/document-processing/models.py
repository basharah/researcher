from sqlalchemy import Column, Integer, String, Text, DateTime, ARRAY, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum


class ProcessingStatus(str, enum.Enum):
    """Processing job status enum"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Document(Base):
    """Model for storing research paper documents"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    original_filename = Column(String)
    file_path = Column(String)
    file_size = Column(Integer)
    page_count = Column(Integer, default=0)
    
    # Metadata
    title = Column(String, nullable=True)
    authors = Column(ARRAY(String), nullable=True)
    publication_date = Column(String, nullable=True)
    doi = Column(String(255), nullable=True, index=True)
    
    # Batch processing fields
    batch_id = Column(String(36), nullable=True, index=True)
    processing_job_id = Column(String(36), ForeignKey('processing_jobs.job_id', ondelete='SET NULL'), nullable=True)
    ocr_applied = Column(Boolean, default=False, nullable=False)
    
    # Content sections
    abstract = Column(Text, nullable=True)
    introduction = Column(Text, nullable=True)
    methodology = Column(Text, nullable=True)
    results = Column(Text, nullable=True)
    conclusion = Column(Text, nullable=True)
    references = Column(Text, nullable=True)
    full_text = Column(Text, nullable=True)

    # Comprehensive extraction artifacts
    tables_data = Column(JSONB, nullable=True)
    figures_metadata = Column(JSONB, nullable=True)
    references_json = Column(JSONB, nullable=True)
    
    # Timestamps
    upload_date = Column(DateTime, default=datetime.utcnow)
    processed_date = Column(DateTime, nullable=True)
    
    # Processing status
    processing_status = Column(String, default="uploaded")  # uploaded, processing, completed, failed
    tables_extracted = Column(Boolean, default=False)
    figures_extracted = Column(Boolean, default=False)
    references_extracted = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}', filename='{self.filename}')>"


class ProcessingJob(Base):
    """Model for tracking document processing jobs"""
    __tablename__ = "processing_jobs"
    
    job_id = Column(String(36), primary_key=True)
    batch_id = Column(String(36), nullable=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), nullable=True)
    filename = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    status = Column(String(20), nullable=False, default='pending', index=True)
    progress = Column(Integer, nullable=False, default=0)  # 0-100
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    user_id = Column(String(36), nullable=True, index=True)
    job_metadata = Column(JSONB, nullable=True)  # Renamed from 'metadata' (reserved in SQLAlchemy)
    
    # Relationships
    steps = relationship("ProcessingStep", back_populates="job", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ProcessingJob(job_id={self.job_id}, filename='{self.filename}', status={self.status})>"
    
    def to_dict(self):
        return {
            "job_id": self.job_id,
            "batch_id": self.batch_id,
            "document_id": self.document_id,
            "filename": self.filename,
            "file_size": self.file_size,
            "status": self.status,
            "progress": self.progress,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "user_id": self.user_id,
            "job_metadata": self.job_metadata
        }


class ProcessingStep(Base):
    """Model for detailed processing step logging"""
    __tablename__ = "processing_steps"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String(36), ForeignKey('processing_jobs.job_id', ondelete='CASCADE'), nullable=False, index=True)
    step_name = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)  # started, completed, failed
    message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    details = Column(JSONB, nullable=True)
    
    # Relationships
    job = relationship("ProcessingJob", back_populates="steps")
    
    def __repr__(self):
        return f"<ProcessingStep(id={self.id}, job_id={self.job_id}, step='{self.step_name}', status={self.status})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "job_id": self.job_id,
            "step_name": self.step_name,
            "status": self.status,
            "message": self.message,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_ms": self.duration_ms,
            "details": self.details
        }
