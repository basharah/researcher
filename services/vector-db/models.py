"""
Database models for Vector DB Service
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from datetime import datetime
from pgvector.sqlalchemy import Vector  # type: ignore

from database import Base


class DocumentChunk(Base):
    """
    Represents a chunk of text from a document
    Each document is split into chunks for better embedding and retrieval
    """
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, nullable=False, index=True)  # Reference to document in document-processing service
    chunk_index = Column(Integer, nullable=False)  # Order of chunk in document
    
    # Content
    text = Column(Text, nullable=False)
    section = Column(String(100))  # Which section this chunk came from (abstract, introduction, etc.)
    
    # Metadata
    page_number = Column(Integer)  # Page this chunk came from
    chunk_type = Column(String(50), default="text")  # text, table, reference, etc.
    
    # Embedding
    embedding = Column(Vector(384))  # Vector dimension depends on model (384 for all-MiniLM-L6-v2)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for efficient searching
    __table_args__ = (
        Index('ix_document_chunks_document_id_chunk_index', 'document_id', 'chunk_index'),
        Index('ix_document_chunks_section', 'section'),
    )
    
    def __repr__(self):
        return f"<DocumentChunk(id={self.id}, document_id={self.document_id}, chunk_index={self.chunk_index})>"


class SearchQuery(Base):
    """
    Log of search queries for analytics and improvement
    """
    __tablename__ = "search_queries"
    
    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(Text, nullable=False)
    query_embedding = Column(Vector(384))
    
    # Results metadata
    results_count = Column(Integer)
    top_score = Column(String(50))  # Similarity score of best match
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<SearchQuery(id={self.id}, query='{self.query_text[:50]}...')>"
