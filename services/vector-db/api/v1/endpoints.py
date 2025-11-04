from fastapi import APIRouter
import logging
import time
from typing import List
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
import schemas
import crud

from text_chunker import get_chunker
from database import get_db
from embedding_service import get_embedding_service

# Create API router
router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/process-document", response_model=schemas.ProcessDocumentResponse)
async def process_document(
    request: schemas.ProcessDocumentRequest,
    db: Session = Depends(get_db)
):
    """
    Process a document: chunk text and generate embeddings
    
    This endpoint receives document content from the Document Processing Service,
    chunks it, generates embeddings, and stores them for semantic search.
    """
    # Initialize services
    chunker = get_chunker()
    embedder = get_embedding_service()
    
    # Delete existing chunks for this document (if reprocessing)
    deleted_count = crud.delete_chunks_by_document(db, request.document_id)
    if deleted_count > 0:
        print(f"Deleted {deleted_count} existing chunks for document {request.document_id}")
    
    # Chunk the document
    sections = request.sections or {}
    chunks = chunker.chunk_with_metadata(request.full_text, sections)
    
    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No chunks could be created from the document"
        )
    
    # Generate embeddings for all chunks
    chunk_texts = [chunk['text'] for chunk in chunks]
    embeddings = embedder.generate_embeddings(chunk_texts)
    
    # Add embeddings to chunk data
    for chunk, embedding in zip(chunks, embeddings):
        chunk['embedding'] = embedding
    
    # Store chunks in database
    created_count = crud.create_chunks_batch(db, chunks, request.document_id)
    
    return schemas.ProcessDocumentResponse(
        document_id=request.document_id,
        chunks_created=created_count,
        embedding_dimension=embedder.dimension,
        message=f"Successfully processed document with {created_count} chunks"
    )


@router.post("/search", response_model=schemas.SearchResponse)
async def semantic_search(
    request: schemas.SearchRequest,
    db: Session = Depends(get_db)
):
    """
    Perform semantic search across document chunks
    
    Uses cosine similarity with pgvector to find the most relevant chunks
    for a given query.
    """
    start_time = time.time()
    
    # Get embedding service
    embedder = get_embedding_service()
    
    # Generate embedding for query
    query_embedding = embedder.generate_embedding(request.query)
    
    # Search for similar chunks
    results = crud.search_similar_chunks(
        db=db,
        query_embedding=query_embedding,
        max_results=request.max_results,
        document_id=request.document_id,
        section=request.section,
        chunk_type=request.chunk_type
    )
    
    # Convert to response format
    chunks_with_scores = []
    for chunk, score in results:
        chunk_dict = {
            "id": chunk.id,
            "document_id": chunk.document_id,
            "chunk_index": chunk.chunk_index,
            "text": chunk.text,
            "section": chunk.section,
            "page_number": chunk.page_number,
            "chunk_type": chunk.chunk_type,
            "created_at": chunk.created_at,
            "similarity_score": score
        }
        chunks_with_scores.append(schemas.ChunkWithScore(**chunk_dict))
    
    # Log the search
    top_score = results[0][1] if results else None
    crud.log_search_query(
        db=db,
        query_text=request.query,
        query_embedding=query_embedding,
        results_count=len(results),
        top_score=top_score
    )
    
    # Calculate search time
    search_time_ms = (time.time() - start_time) * 1000
    
    return schemas.SearchResponse(
        query=request.query,
        results_count=len(chunks_with_scores),
        chunks=chunks_with_scores,
        search_time_ms=search_time_ms
    )


@router.post("/embed", response_model=schemas.EmbeddingResponse)
async def generate_embedding(request: schemas.EmbeddingRequest):
    """
    Generate embedding for arbitrary text
    
    Useful for testing or generating embeddings for external use.
    """
    embedder = get_embedding_service()
    embedding = embedder.generate_embedding(request.text)
    
    return schemas.EmbeddingResponse(
        text=request.text,
        embedding=embedding,
        dimension=len(embedding)
    )


@router.get("/documents/{document_id}/chunks", response_model=List[schemas.ChunkResponse])
async def get_document_chunks(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get all chunks for a specific document"""
    chunks = crud.get_chunks_by_document(db, document_id)
    return [schemas.ChunkResponse.model_validate(chunk) for chunk in chunks]


@router.delete("/documents/{document_id}/chunks")
async def delete_document_chunks(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Delete all chunks for a specific document"""
    deleted_count = crud.delete_chunks_by_document(db, document_id)
    return {
        "document_id": document_id,
        "deleted_chunks": deleted_count,
        "message": f"Deleted {deleted_count} chunks for document {document_id}"
    }
