from sqlalchemy import Column, Integer, String, Text, DateTime, ARRAY, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from database import Base

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
    doi = Column(String, nullable=True)
    
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
