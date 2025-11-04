"""
Additional Pydantic schemas for Vector DB integration
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class SearchRequest(BaseModel):
    """Request for semantic search across documents"""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    max_results: int = Field(default=10, ge=1, le=50, description="Maximum results to return")
    document_id: Optional[int] = Field(default=None, description="Filter by specific document")
    section: Optional[str] = Field(default=None, description="Filter by section (e.g., 'methodology')")


class ChunkResult(BaseModel):
    """A search result chunk"""
    id: int
    document_id: int
    chunk_index: int
    text: str
    section: Optional[str]
    similarity_score: float = Field(..., description="Similarity score (0-1)")


class SearchResponse(BaseModel):
    """Response from semantic search"""
    query: str
    results_count: int
    search_time_ms: float
    chunks: List[ChunkResult]
