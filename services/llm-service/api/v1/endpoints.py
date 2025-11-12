"""
API v1 - LLM Service Endpoints
"""
from fastapi import APIRouter, HTTPException, status
from typing import Optional
import logging
import time

from schemas import (
    AnalysisRequest, AnalysisResponse,
    QuestionRequest, QuestionResponse,
    CompareDocumentsRequest, CompareResponse,
    ChatRequest, ChatResponse,
    LLMHealthResponse, AnalysisType
)
from llm_client import get_llm_client
from service_client import get_service_client
from prompts import prompt_templates

router = APIRouter()
logger = logging.getLogger(__name__)


async def get_document_context(
    document_id: int,
    section: Optional[str] = None,
    use_rag: bool = True,
    rag_query: Optional[str] = None,
    analysis_type: Optional[AnalysisType] = None,
) -> str:
    """
    Get document context, optionally using RAG
    
    Args:
        document_id: Document ID
        section: Specific section to retrieve
        use_rag: Whether to use RAG for relevant chunks
        rag_query: Query for RAG (if different from section)
        
    Returns:
        Document text context
    """
    service_client = get_service_client()

    # Try RAG for non-summary analyses first
    if use_rag and rag_query and analysis_type not in (AnalysisType.SUMMARY,):
        search_results = await service_client.semantic_search(
            query=rag_query,
            max_results=5,
            document_id=document_id,
            section=section,
        )
        if search_results and search_results.get("chunks"):
            context = "\n\n".join([chunk.get("text", "") for chunk in search_results["chunks"]])
            logger.info(f"LLM context source=rag len={len(context)}")
            return context

    # Fetch sections to build a rich context
    sections_payload = await service_client.get_document_sections(document_id)
    if sections_payload and isinstance(sections_payload, dict):
        sections_dict = sections_payload.get("sections") or {}
        full_text_value = sections_payload.get("full_text") or ""
        if section and section in sections_dict:
            ctx = sections_dict.get(section) or ""
            logger.info(f"LLM context source=section:{section} len={len(ctx)}")
            return ctx
        # Build full context in logical order
        ordered_keys = [
            "abstract",
            "introduction",
            "methodology",
            "results",
            "conclusion",
        ]
        context_parts = []
        # Optionally include title if present
        title = sections_payload.get("title")
        if title:
            context_parts.append(f"Title: {title}")
        for key in ordered_keys:
            val = sections_dict.get(key)
            if val:
                context_parts.append(f"{key.title()}:\n{val}")
        if context_parts:
            ctx = "\n\n".join(context_parts)
            logger.info(f"LLM context source=sections_aggregate len={len(ctx)}")
            return ctx
        # If no structured sections, fall back to full_text if present
        if full_text_value:
            logger.info(f"LLM context source=full_text len={len(full_text_value)}")
            return full_text_value

    # As a last resort, fall back to document basic info (may be minimal)
    doc = await service_client.get_document(document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found",
        )
    if section and section in doc:
        ctx = doc.get(section) or ""
        logger.info(f"LLM context source=doc_field:{section} len={len(ctx)}")
        return ctx
    ctx = doc.get("abstract", "") or ""
    logger.info(f"LLM context source=abstract len={len(ctx)}")
    return ctx


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_document(request: AnalysisRequest):
    """
    Analyze a research paper using LLM
    
    Supports various analysis types:
    - summary: Comprehensive summary
    - literature_review: Extract and analyze literature review
    - key_findings: Identify key findings
    - methodology: Analyze methodology
    - results_analysis: Analyze results
    - limitations: Identify limitations
    - future_work: Suggest future research
    - custom: Use custom prompt
    """
    start_time = time.time()
    llm_client = get_llm_client()
    
    if not llm_client.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No LLM provider configured"
        )
    
    try:
        # Get document context
        if request.analysis_type == AnalysisType.CUSTOM and not request.custom_prompt:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="custom_prompt required for custom analysis"
            )
        
        # Determine RAG query based on analysis type
        rag_query = {
            AnalysisType.LITERATURE_REVIEW: "literature review related work citations",
            AnalysisType.METHODOLOGY: "methodology methods approach",
            AnalysisType.RESULTS_ANALYSIS: "results findings outcomes",
            AnalysisType.LIMITATIONS: "limitations weaknesses constraints",
            AnalysisType.FUTURE_WORK: "future work future research"
        }.get(request.analysis_type, request.analysis_type.value)
        
        context = await get_document_context(
            document_id=request.document_id,
            use_rag=request.use_rag,
            rag_query=rag_query,
            analysis_type=request.analysis_type,
        )
        
        # Build prompt
        if request.analysis_type == AnalysisType.CUSTOM:
            user_prompt = f"{request.custom_prompt}\n\nDocument:\n{context}"
        else:
            user_prompt = prompt_templates.get_analysis_prompt(
                request.analysis_type,
                context
            )
        
        messages = [
            {"role": "system", "content": prompt_templates.get_system_prompt()},
            {"role": "user", "content": user_prompt}
        ]
        
        # Generate response
        result_text, model_used, tokens_used = await llm_client.generate(
            messages=messages,
            provider=request.llm_provider,
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        return AnalysisResponse(
            document_id=request.document_id,
            analysis_type=request.analysis_type.value,
            result=result_text,
            model_used=model_used,
            provider_used=request.llm_provider.value if request.llm_provider else "default",
            tokens_used=tokens_used,
            processing_time_ms=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analyze_document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/question", response_model=QuestionResponse)
async def answer_question(request: QuestionRequest):
    """
    Answer a question about research paper(s) using RAG
    
    Uses semantic search to find relevant passages, then generates
    an answer using the LLM with retrieved context.
    """
    start_time = time.time()
    llm_client = get_llm_client()
    service_client = get_service_client()
    
    if not llm_client.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No LLM provider configured"
        )
    
    try:
        sources = []
        
        if request.use_rag:
            # Perform semantic search
            search_results = await service_client.semantic_search(
                query=request.question,
                max_results=5,
                document_id=request.document_ids[0] if request.document_ids and len(request.document_ids) == 1 else None
            )
            
            if not search_results or not search_results.get("chunks"):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No relevant information found"
                )
            
            context_chunks = [chunk["text"] for chunk in search_results["chunks"]]
            sources = search_results["chunks"]
            
            user_prompt = prompt_templates.get_question_prompt(
                request.question,
                context_chunks
            )
        else:
            # Use full document(s)
            if not request.document_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="document_ids required when use_rag=False"
                )
            
            contexts = []
            for doc_id in request.document_ids:
                context = await get_document_context(doc_id, use_rag=False)
                contexts.append(context)
            
            user_prompt = f"Question: {request.question}\n\nContext:\n" + "\n\n".join(contexts)
        
        messages = [
            {"role": "system", "content": prompt_templates.get_system_prompt()},
            {"role": "user", "content": user_prompt}
        ]
        
        # Generate answer
        answer_text, model_used, tokens_used = await llm_client.generate(
            messages=messages,
            provider=request.llm_provider,
            model=request.model,
            max_tokens=request.max_tokens
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        return QuestionResponse(
            question=request.question,
            answer=answer_text,
            model_used=model_used,
            provider_used=request.llm_provider.value if request.llm_provider else "default",
            tokens_used=tokens_used,
            processing_time_ms=processing_time,
            sources=sources if request.use_rag else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in answer_question: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/compare", response_model=CompareResponse)
async def compare_documents(request: CompareDocumentsRequest):
    """
    Compare multiple research papers
    
    Generates a comparative analysis highlighting similarities,
    differences, and relationships between papers.
    """
    start_time = time.time()
    llm_client = get_llm_client()
    service_client = get_service_client()
    
    if not llm_client.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No LLM provider configured"
        )
    
    try:
        # Get all documents
        documents_data = []
        for doc_id in request.document_ids:
            doc = await service_client.get_document(doc_id)
            if not doc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Document {doc_id} not found"
                )
            documents_data.append(doc)
        
        # Build comparison prompt
        user_prompt = prompt_templates.get_comparison_prompt(
            documents_data,
            request.comparison_aspects or []
        )
        
        messages = [
            {"role": "system", "content": prompt_templates.get_system_prompt()},
            {"role": "user", "content": user_prompt}
        ]
        
        # Generate comparison
        comparison_text, model_used, tokens_used = await llm_client.generate(
            messages=messages,
            provider=request.llm_provider,
            model=request.model
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        return CompareResponse(
            document_ids=request.document_ids,
            comparison=comparison_text,
            model_used=model_used,
            provider_used=request.llm_provider.value if request.llm_provider else "default",
            tokens_used=tokens_used,
            processing_time_ms=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in compare_documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Multi-turn chat with document context
    
    Supports conversational Q&A about research papers with
    optional RAG for context retrieval.
    """
    start_time = time.time()
    llm_client = get_llm_client()
    service_client = get_service_client()
    
    if not llm_client.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No LLM provider configured"
        )
    
    try:
        messages = []
        sources = None
        
        # Add system prompt with context if using RAG
        if request.use_rag and request.document_context:
            # Get latest user message for RAG query
            user_messages = [m for m in request.messages if m.role == "user"]
            if user_messages:
                latest_query = user_messages[-1].content
                
                # Perform semantic search across specified documents
                search_results = await service_client.semantic_search(
                    query=latest_query,
                    max_results=5,
                    document_id=request.document_context[0] if len(request.document_context) == 1 else None
                )
                
                if search_results and search_results.get("chunks"):
                    context_chunks = [chunk["text"] for chunk in search_results["chunks"]]
                    sources = search_results["chunks"]
                    
                    system_prompt = prompt_templates.get_chat_prompt_with_context(context_chunks)
                    messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({"role": "system", "content": prompt_templates.get_system_prompt()})
        
        # Add conversation history
        for msg in request.messages:
            messages.append({"role": msg.role, "content": msg.content})
        
        # Generate response
        response_text, model_used, tokens_used = await llm_client.generate(
            messages=messages,
            provider=request.llm_provider,
            model=request.model
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        return ChatResponse(
            message=response_text,
            model_used=model_used,
            provider_used=request.llm_provider.value if request.llm_provider else "default",
            tokens_used=tokens_used,
            processing_time_ms=processing_time,
            sources=sources
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/health", response_model=LLMHealthResponse)
async def health_check():
    """
    Comprehensive health check
    
    Checks availability of:
    - LLM providers (OpenAI, Anthropic)
    - Vector DB service
    - Document Processing service
    """
    llm_client = get_llm_client()
    service_client = get_service_client()
    
    # Check service availability
    vector_db_ok = await service_client.health_check_vector_db()
    doc_service_ok = await service_client.health_check_document_service()
    
    return LLMHealthResponse(
        status="healthy" if llm_client.is_available() else "degraded",
        openai_available=llm_client.openai_available,
        anthropic_available=llm_client.anthropic_available,
        vector_db_available=vector_db_ok,
        document_service_available=doc_service_ok
    )
