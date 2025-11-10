"""
CRUD operations for Vector DB Service
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from models import DocumentChunk, SearchQuery
from schemas import ChunkCreate


def create_chunk(db: Session, chunk_data: ChunkCreate, embedding: List[float]) -> DocumentChunk:
    """
    Create a new document chunk with embedding
    
    Args:
        db: Database session
        chunk_data: Chunk data
        embedding: Embedding vector
        
    Returns:
        Created DocumentChunk
    """
    chunk = DocumentChunk(
        document_id=chunk_data.document_id,
        chunk_index=chunk_data.chunk_index,
        text=chunk_data.text,
        section=chunk_data.section,
        page_number=chunk_data.page_number,
        chunk_type=chunk_data.chunk_type,
        embedding=embedding
    )
    db.add(chunk)
    db.commit()
    db.refresh(chunk)
    return chunk


def create_chunks_batch(db: Session, chunks: List[Dict[str, Any]], document_id: int) -> int:
    """
    Create multiple chunks in a batch
    
    Args:
        db: Database session
        chunks: List of chunk dictionaries (with 'embedding' key)
        document_id: ID of the parent document
        
    Returns:
        Number of chunks created
    """
    db_chunks = []
    for chunk in chunks:
        db_chunk = DocumentChunk(
            document_id=document_id,
            chunk_index=chunk['chunk_index'],
            text=chunk['text'],
            section=chunk.get('section'),
            page_number=chunk.get('page_number'),
            chunk_type=chunk.get('chunk_type', 'text'),
            embedding=chunk['embedding']
        )
        db_chunks.append(db_chunk)
    
    db.add_all(db_chunks)
    db.commit()
    return len(db_chunks)


def get_chunks_by_document(db: Session, document_id: int) -> List[DocumentChunk]:
    """Get all chunks for a specific document"""
    return db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document_id
    ).order_by(DocumentChunk.chunk_index).all()


def delete_chunks_by_document(db: Session, document_id: int) -> int:
    """Delete all chunks for a specific document"""
    count = db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document_id
    ).delete()
    db.commit()
    return count


def search_similar_chunks(
    db: Session,
    query_embedding: List[float],
    max_results: int = 10,
    document_id: Optional[int] = None,
    section: Optional[str] = None,
    chunk_type: Optional[str] = None
) -> List[tuple[DocumentChunk, float]]:
    """
    Search for similar chunks using cosine similarity
    
    Args:
        db: Database session
        query_embedding: Query embedding vector
        max_results: Maximum number of results
        document_id: Filter by document ID (optional)
        section: Filter by section (optional)
        chunk_type: Filter by chunk type (optional)
        
    Returns:
        List of (chunk, similarity_score) tuples
    """
    from sqlalchemy.sql import select
    
    # Build base query with cosine distance
    # Note: <=> is cosine distance, 1 - distance = similarity
    similarity = (1 - DocumentChunk.embedding.cosine_distance(query_embedding)).label('similarity')
    
    query = select(
        DocumentChunk,
        similarity
    )
    
    # Apply filters
    if document_id is not None:
        query = query.where(DocumentChunk.document_id == document_id)
    
    if section:
        query = query.where(DocumentChunk.section == section)
    
    if chunk_type:
        query = query.where(DocumentChunk.chunk_type == chunk_type)
    
    # Order by similarity and limit
    query = query.order_by(similarity.desc()).limit(max_results)
    
    # Execute query
    result = db.execute(query)
    rows = result.fetchall()
    
    # Convert to (DocumentChunk, similarity) tuples
    results = []
    for row in rows:
        chunk = row[0]  # DocumentChunk object
        similarity = float(row[1])  # similarity score
        results.append((chunk, similarity))
    
    return results


def log_search_query(
    db: Session,
    query_text: str,
    query_embedding: List[float],
    results_count: int,
    top_score: Optional[float] = None
) -> SearchQuery:
    """Log a search query for analytics"""
    search_query = SearchQuery(
        query_text=query_text,
        query_embedding=query_embedding,
        results_count=results_count,
        top_score=str(top_score) if top_score else None
    )
    db.add(search_query)
    db.commit()
    db.refresh(search_query)
    return search_query
