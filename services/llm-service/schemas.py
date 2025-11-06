"""
Pydantic schemas for LLM Service
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class AnalysisType(str, Enum):
    """Types of analysis that can be performed"""
    SUMMARY = "summary"
    LITERATURE_REVIEW = "literature_review"
    KEY_FINDINGS = "key_findings"
    METHODOLOGY = "methodology"
    RESULTS_ANALYSIS = "results_analysis"
    LIMITATIONS = "limitations"
    FUTURE_WORK = "future_work"
    CUSTOM = "custom"


class AnalysisRequest(BaseModel):
    """Request for document analysis"""
    document_id: int = Field(..., description="ID of the document to analyze")
    analysis_type: AnalysisType = Field(..., description="Type of analysis to perform")
    custom_prompt: Optional[str] = Field(None, description="Custom prompt for analysis (if analysis_type=custom)")
    use_rag: bool = Field(True, description="Whether to use RAG with vector search")
    llm_provider: Optional[LLMProvider] = Field(None, description="LLM provider to use (defaults to config)")
    model: Optional[str] = Field(None, description="Specific model to use")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens in response")
    temperature: Optional[float] = Field(None, description="Temperature for generation (0-1)")


class QuestionRequest(BaseModel):
    """Request for question answering"""
    question: str = Field(..., description="Question to ask about the document(s)")
    document_ids: Optional[List[int]] = Field(None, description="Specific documents to search (if None, search all)")
    use_rag: bool = Field(True, description="Whether to use RAG with vector search")
    llm_provider: Optional[LLMProvider] = Field(None, description="LLM provider to use")
    model: Optional[str] = Field(None, description="Specific model to use")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens in response")


class CompareDocumentsRequest(BaseModel):
    """Request for comparing multiple documents"""
    document_ids: List[int] = Field(..., description="IDs of documents to compare", min_length=2)
    comparison_aspects: Optional[List[str]] = Field(
        None,
        description="Specific aspects to compare (methodology, results, etc.)"
    )
    llm_provider: Optional[LLMProvider] = Field(None, description="LLM provider to use")
    model: Optional[str] = Field(None, description="Specific model to use")


class ChatMessage(BaseModel):
    """Single chat message"""
    role: str = Field(..., description="Role: 'user', 'assistant', or 'system'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Request for multi-turn chat"""
    messages: List[ChatMessage] = Field(..., description="Chat history")
    document_context: Optional[List[int]] = Field(None, description="Document IDs for context")
    use_rag: bool = Field(True, description="Whether to use RAG")
    llm_provider: Optional[LLMProvider] = Field(None, description="LLM provider to use")
    model: Optional[str] = Field(None, description="Specific model to use")


class AnalysisResponse(BaseModel):
    """Response from analysis"""
    document_id: int
    analysis_type: str
    result: str
    model_used: str
    provider_used: str
    tokens_used: Optional[int] = None
    processing_time_ms: float
    sources_used: Optional[List[Dict[str, Any]]] = None  # RAG sources if used


class QuestionResponse(BaseModel):
    """Response from question answering"""
    question: str
    answer: str
    model_used: str
    provider_used: str
    tokens_used: Optional[int] = None
    processing_time_ms: float
    sources: Optional[List[Dict[str, Any]]] = None  # RAG sources


class CompareResponse(BaseModel):
    """Response from document comparison"""
    document_ids: List[int]
    comparison: str
    model_used: str
    provider_used: str
    tokens_used: Optional[int] = None
    processing_time_ms: float


class ChatResponse(BaseModel):
    """Response from chat"""
    message: str
    model_used: str
    provider_used: str
    tokens_used: Optional[int] = None
    processing_time_ms: float
    sources: Optional[List[Dict[str, Any]]] = None


class LLMHealthResponse(BaseModel):
    """Health check response"""
    status: str
    openai_available: bool
    anthropic_available: bool
    vector_db_available: bool
    document_service_available: bool
