"""
API v1 - Gateway Endpoints
Unified API that orchestrates all microservices
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Query
from typing import List, Optional
import logging
import time
from datetime import datetime

from schemas import (
    SearchRequest, SearchResponse,
    AnalysisRequest, QuestionRequest,
    WorkflowRequest, WorkflowResponse,
    ServiceHealthResponse, DocumentListResponse
)
from service_client import get_service_client

router = APIRouter()
logger = logging.getLogger(__name__)

# Request counters for stats
request_stats = {
    "total": 0,
    "document_service": 0,
    "vector_service": 0,
    "llm_service": 0,
    "start_time": time.time()
}


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a research paper PDF
    
    Proxies to Document Processing Service which:
    1. Saves the PDF
    2. Extracts text, metadata, tables, figures
    3. Triggers background Vector DB processing
    
    Returns document details immediately.
    """
    request_stats["total"] += 1
    request_stats["document_service"] += 1
    
    if not file.filename or not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    try:
        service_client = get_service_client()
        contents = await file.read()
        
        result = await service_client.upload_document(contents, file.filename)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload document"
            )
        
        logger.info(f"Document uploaded: {result.get('id')} - {file.filename}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """
    List all uploaded documents
    
    Supports pagination with skip/limit.
    """
    request_stats["total"] += 1
    request_stats["document_service"] += 1
    
    try:
        service_client = get_service_client()
        result = await service_client.list_documents(skip, limit)
        return result
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/documents/{document_id}")
async def get_document(document_id: int):
    """
    Get document details by ID
    
    Returns full document metadata and content.
    """
    request_stats["total"] += 1
    request_stats["document_service"] += 1
    
    try:
        service_client = get_service_client()
        result = await service_client.get_document(document_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document {document_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/documents/{document_id}/sections")
async def get_document_sections(document_id: int):
    """Get extracted sections from a document"""
    request_stats["total"] += 1
    request_stats["document_service"] += 1
    
    try:
        service_client = get_service_client()
        result = await service_client.get_document_sections(document_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting sections: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/documents/{document_id}/tables")
async def get_document_tables(document_id: int):
    """Get extracted tables from a document"""
    request_stats["total"] += 1
    request_stats["document_service"] += 1
    
    try:
        service_client = get_service_client()
        result = await service_client.get_document_tables(document_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tables: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/documents/{document_id}")
async def delete_document(document_id: int):
    """
    Delete a document
    
    Removes from both Document Processing and Vector DB.
    """
    request_stats["total"] += 1
    request_stats["document_service"] += 1
    
    try:
        service_client = get_service_client()
        success = await service_client.delete_document(document_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found"
            )
        
        logger.info(f"Document deleted: {document_id}")
        return {"message": f"Document {document_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """
    Semantic search across documents using Vector DB
    
    Uses RAG to find relevant document chunks.
    """
    request_stats["total"] += 1
    request_stats["vector_service"] += 1
    
    try:
        service_client = get_service_client()
        result = await service_client.search_documents(request.dict())
        return result
    except Exception as e:
        logger.error(f"Error searching: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/analyze")
async def analyze_document(request: AnalysisRequest):
    """
    Analyze a research paper using LLM
    
    Supports multiple analysis types:
    - summary, literature_review, key_findings
    - methodology, results_analysis, limitations
    - future_work, custom
    """
    request_stats["total"] += 1
    request_stats["llm_service"] += 1
    
    try:
        service_client = get_service_client()
        result = await service_client.analyze_document(request.dict(exclude_unset=True))
        
        logger.info(f"Analysis completed for document {request.document_id}: {request.analysis_type}")
        return result
    except Exception as e:
        logger.error(f"Error analyzing document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/question")
async def answer_question(request: QuestionRequest):
    """
    Ask a question about research papers
    
    Uses RAG to find relevant context and LLM to generate answer.
    """
    request_stats["total"] += 1
    request_stats["llm_service"] += 1
    
    try:
        service_client = get_service_client()
        result = await service_client.answer_question(request.dict(exclude_unset=True))
        
        logger.info(f"Question answered: {request.question[:50]}...")
        return result
    except Exception as e:
        logger.error(f"Error answering question: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/compare")
async def compare_documents(document_ids: List[int], comparison_aspects: Optional[List[str]] = None):
    """
    Compare multiple research papers
    
    Generates comparative analysis using LLM.
    """
    request_stats["total"] += 1
    request_stats["llm_service"] += 1
    
    if len(document_ids) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 2 documents required for comparison"
        )
    
    try:
        service_client = get_service_client()
        request_data = {"document_ids": document_ids}
        if comparison_aspects:
            request_data["comparison_aspects"] = comparison_aspects
        
        result = await service_client.compare_documents(request_data)
        
        logger.info(f"Comparison completed for documents: {document_ids}")
        return result
    except Exception as e:
        logger.error(f"Error comparing documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/chat")
async def chat(messages: List[dict], document_context: Optional[List[int]] = None, use_rag: bool = True):
    """
    Multi-turn chat with document context
    
    Interactive conversation about research papers.
    """
    request_stats["total"] += 1
    request_stats["llm_service"] += 1
    
    try:
        service_client = get_service_client()
        request_data = {
            "messages": messages,
            "use_rag": use_rag
        }
        if document_context:
            request_data["document_context"] = document_context
        
        result = await service_client.chat(request_data)
        return result
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/workflow/upload-and-analyze", response_model=WorkflowResponse)
async def upload_and_analyze_workflow(
    file: UploadFile = File(...),
    analysis_type: str = Query("summary"),
    use_rag: bool = Query(True)
):
    """
    Complete workflow: Upload PDF → Process → Analyze
    
    Combines multiple operations into a single endpoint:
    1. Upload document
    2. Wait for Vector DB processing
    3. Analyze with LLM
    
    Returns comprehensive results from all stages.
    """
    start_time = time.time()
    request_stats["total"] += 1
    
    if not file.filename or not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    try:
        service_client = get_service_client()
        
        # Step 1: Upload document
        logger.info(f"Workflow: Uploading {file.filename}")
        contents = await file.read()
        upload_result = await service_client.upload_document(contents, file.filename)
        
        if not upload_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload document"
            )
        
        document_id = upload_result["id"]
        logger.info(f"Workflow: Document uploaded with ID {document_id}")
        
        # Step 2: Wait briefly for Vector DB processing (background task)
        # In production, you might poll or use webhooks
        import asyncio
        await asyncio.sleep(5)  # Give Vector DB time to process
        
        # Check if chunks were created
        chunks_info = await service_client.get_document_chunks(document_id)
        
        # Step 3: Analyze document
        logger.info(f"Workflow: Analyzing document {document_id}")
        analysis_result = await service_client.analyze_document({
            "document_id": document_id,
            "analysis_type": analysis_type,
            "use_rag": use_rag
        })
        
        total_time = (time.time() - start_time) * 1000
        
        logger.info(f"Workflow completed for {file.filename} in {total_time:.2f}ms")
        
        return WorkflowResponse(
            document_id=document_id,
            document_info=upload_result,
            vector_processing=chunks_info or {"status": "processing"},
            analysis=analysis_result,
            total_processing_time_ms=total_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in workflow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/health", response_model=ServiceHealthResponse)
async def health_check():
    """
    Comprehensive health check for all services
    
    Returns aggregated status of:
    - Document Processing Service
    - Vector DB Service  
    - LLM Service
    """
    service_client = get_service_client()
    
    # Check all services in parallel
    import asyncio
    doc_health, vec_health, llm_health = await asyncio.gather(
        service_client.check_document_service(),
        service_client.check_vector_service(),
        service_client.check_llm_service(),
        return_exceptions=True
    )
    
    # Determine overall status
    all_healthy = all(
        isinstance(h, dict) and h.get("status") == "healthy"
        for h in [doc_health, vec_health, llm_health]
    )
    
    overall_status = "healthy" if all_healthy else "degraded"
    
    return ServiceHealthResponse(
        status=overall_status,
        services={
            "document_processing": doc_health if isinstance(doc_health, dict) else {"status": "error"},
            "vector_db": vec_health if isinstance(vec_health, dict) else {"status": "error"},
            "llm_service": llm_health if isinstance(llm_health, dict) else {"status": "error"},
        },
        timestamp=datetime.utcnow()
    )


@router.get("/stats")
async def get_stats():
    """
    Gateway statistics
    
    Returns request counts and performance metrics.
    """
    uptime = time.time() - request_stats["start_time"]
    
    return {
        "total_requests": request_stats["total"],
        "requests_per_service": {
            "document_processing": request_stats["document_service"],
            "vector_db": request_stats["vector_service"],
            "llm_service": request_stats["llm_service"]
        },
        "uptime_seconds": uptime,
        "requests_per_minute": (request_stats["total"] / uptime * 60) if uptime > 0 else 0
    }
