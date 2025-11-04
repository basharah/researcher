"""
Pydantic schemas for Vector DB Service
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class ChunkBase(BaseModel):
    """Base schema for document chunks"""
    document_id: int
    chunk_index: int
    text: str
    section: Optional[str] = None
    page_number: Optional[int] = None
    chunk_type: str = "text"


class ChunkCreate(ChunkBase):
    """Schema for creating a new chunk"""
    pass


class ChunkResponse(ChunkBase):
    """Schema for chunk responses"""
    id: int
    created_at: datetime
    
    model_config = {"from_attributes": True}


class ChunkWithScore(ChunkResponse):
    """Schema for chunk with similarity score"""
    similarity_score: float = Field(..., description="Cosine similarity score (0-1)")


class ProcessDocumentRequest(BaseModel):
    """Request to process a document and create chunks"""
    document_id: int
    full_text: str
    sections: Optional[dict] = None  # Map of section name to text
    tables: Optional[List[dict]] = None
    references: Optional[str] = None


class ProcessDocumentResponse(BaseModel):
    """Response after processing a document"""
    document_id: int
    chunks_created: int
    embedding_dimension: int
    message: str


class SearchRequest(BaseModel):
    """Request for semantic search"""
    query: str = Field(..., min_length=1, max_length=1000)
    max_results: int = Field(default=10, ge=1, le=50)
    document_id: Optional[int] = None  # Filter by specific document
    section: Optional[str] = None  # Filter by section
    chunk_type: Optional[str] = None  # Filter by chunk type


class SearchResponse(BaseModel):
    """Response from semantic search"""
    query: str
    results_count: int
    chunks: List[ChunkWithScore]
    search_time_ms: float


class EmbeddingRequest(BaseModel):
    """Request to generate embedding for text"""
    text: str = Field(..., min_length=1)


class EmbeddingResponse(BaseModel):
    """Response with embedding vector"""
    text: str
    embedding: List[float]
    dimension: int
