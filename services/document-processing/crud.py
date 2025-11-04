"""
CRUD operations for Document model
Separates database logic from API endpoints
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from models import Document


def get_document(db: Session, document_id: int) -> Optional[Document]:
    """
    Get a single document by ID
    
    Args:
        db: Database session
        document_id: ID of the document to retrieve
    
    Returns:
        Document object or None if not found
    """
    return db.query(Document).filter(Document.id == document_id).first()


def get_document_by_filename(db: Session, filename: str) -> Optional[Document]:
    """
    Get a document by filename
    
    Args:
        db: Database session
        filename: Filename to search for
    
    Returns:
        Document object or None if not found
    """
    return db.query(Document).filter(Document.filename == filename).first()


def get_documents(db: Session, skip: int = 0, limit: int = 10) -> List[Document]:
    """
    Get list of documents with pagination
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
    
    Returns:
        List of Document objects
    """
    return db.query(Document).offset(skip).limit(limit).all()


def get_documents_count(db: Session) -> int:
    """
    Get total count of documents
    
    Args:
        db: Database session
    
    Returns:
        Total number of documents
    """
    return db.query(Document).count()


def create_document(db: Session, document_data: dict) -> Document:
    """
    Create a new document
    
    Args:
        db: Database session
        document_data: Dictionary containing document fields
    
    Returns:
        Created Document object
    """
    document = Document(**document_data)
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def update_document(db: Session, document_id: int, update_data: dict) -> Optional[Document]:
    """
    Update an existing document
    
    Args:
        db: Database session
        document_id: ID of the document to update
        update_data: Dictionary with fields to update
    
    Returns:
        Updated Document object or None if not found
    """
    document = get_document(db, document_id)
    if not document:
        return None
    
    for key, value in update_data.items():
        if hasattr(document, key):
            setattr(document, key, value)
    
    db.commit()
    db.refresh(document)
    return document


def delete_document(db: Session, document_id: int) -> bool:
    """
    Delete a document from database
    
    Args:
        db: Database session
        document_id: ID of the document to delete
    
    Returns:
        True if deleted, False if not found
    """
    document = get_document(db, document_id)
    if not document:
        return False
    
    db.delete(document)
    db.commit()
    return True


def search_documents(db: Session, query: str, skip: int = 0, limit: int = 10) -> List[Document]:
    """
    Search documents by title or abstract
    
    Args:
        db: Database session
        query: Search query string
        skip: Number of records to skip
        limit: Maximum number of records to return
    
    Returns:
        List of matching Document objects
    """
    search_pattern = f"%{query}%"
    return db.query(Document).filter(
        (Document.title.ilike(search_pattern)) |
        (Document.abstract.ilike(search_pattern))
    ).offset(skip).limit(limit).all()
