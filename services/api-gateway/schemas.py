"""
Pydantic schemas for API Gateway
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# Re-export common schemas from services
class DocumentUploadResponse(BaseModel):
    """Response from document upload"""
    id: int
    filename: str
    title: Optional[str] = None
    authors: Optional[List[str]] = None
    page_count: int
    processing_status: str
    upload_date: datetime


class DocumentListResponse(BaseModel):
    """List of documents"""
    documents: List[Dict[str, Any]]
    total: int
    skip: int
    limit: int


class SearchRequest(BaseModel):
    """Search request"""
    query: str = Field(..., description="Search query")
    max_results: int = Field(10, description="Maximum results to return")
    document_id: Optional[int] = Field(None, description="Filter by document ID")
    section: Optional[str] = Field(None, description="Filter by section")


class SearchResponse(BaseModel):
    """Search response"""
    query: str
    results_count: int
    search_time_ms: float
    chunks: List[Dict[str, Any]]


class AnalysisRequest(BaseModel):
    """Analysis request"""
    document_id: int
    analysis_type: str
    custom_prompt: Optional[str] = None
    use_rag: bool = True
    llm_provider: Optional[str] = None
    model: Optional[str] = None


class QuestionRequest(BaseModel):
    """Question answering request"""
    question: str
    document_ids: Optional[List[int]] = None
    use_rag: bool = True
    llm_provider: Optional[str] = None
    model: Optional[str] = None


class WorkflowRequest(BaseModel):
    """Complete workflow: upload, process, analyze"""
    analysis_type: str = "summary"
    use_rag: bool = True
    llm_provider: Optional[str] = None


class WorkflowResponse(BaseModel):
    """Workflow response with all stages"""
    document_id: int
    document_info: Dict[str, Any]
    vector_processing: Dict[str, Any]
    analysis: Dict[str, Any]
    total_processing_time_ms: float


class ServiceHealthResponse(BaseModel):
    """Aggregated health status"""
    status: str
    services: Dict[str, Dict[str, Any]]
    timestamp: datetime


class GatewayStatsResponse(BaseModel):
    """Gateway statistics"""
    total_requests: int
    requests_per_service: Dict[str, int]
    average_response_time_ms: float
    uptime_seconds: float
