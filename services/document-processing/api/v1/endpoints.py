"""
API v1 - Document Processing Endpoints
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from pathlib import Path

from database import get_db
from utils.pdf_parser import PDFParser
from utils.text_processor import TextProcessor
from schemas import DocumentResponse
from config import settings
import crud

# Create API router
router = APIRouter()


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload a research paper PDF
    
    - **file**: PDF file to upload (max 10MB)
    """
    # Validate file type
    if not file.filename or not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Read file content
    contents = await file.read()
    file_size = len(contents)
    
    # Validate file size
    if file_size > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {settings.max_file_size / 1024 / 1024}MB"
        )
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = settings.upload_dir / safe_filename
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(contents)
    
    try:
        # Parse PDF
        parser = PDFParser(str(file_path))
        metadata = parser.extract_metadata()
        text_content = parser.extract_text()
        
        # Process text to extract sections
        processor = TextProcessor(text_content)
        sections = processor.extract_sections()
        
        # Prepare document data
        document_data = {
            "filename": safe_filename,
            "original_filename": file.filename,
            "file_path": str(file_path),
            "file_size": file_size,
            "page_count": metadata.get('page_count', 0),
            "title": metadata.get('title'),
            "authors": metadata.get('authors', []),
            "abstract": sections.get('abstract'),
            "introduction": sections.get('introduction'),
            "methodology": sections.get('methodology'),
            "results": sections.get('results'),
            "conclusion": sections.get('conclusion'),
            "references": sections.get('references'),
            "full_text": text_content,
            "upload_date": datetime.now()
        }
        
        # Create document using CRUD
        document = crud.create_document(db, document_data)
        
        return DocumentResponse.model_validate(document)
        
    except Exception as e:
        # Clean up file on error
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing PDF: {str(e)}"
        )


@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    List all uploaded documents
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    documents = crud.get_documents(db, skip=skip, limit=limit)
    return [DocumentResponse.model_validate(doc) for doc in documents]


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document_by_id(document_id: int, db: Session = Depends(get_db)):
    """
    Get details of a specific document
    
    - **document_id**: ID of the document
    """
    document = crud.get_document(db, document_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    
    return DocumentResponse.model_validate(document)


@router.get("/documents/{document_id}/sections")
async def get_document_sections(document_id: int, db: Session = Depends(get_db)):
    """
    Get all extracted sections from a document
    
    - **document_id**: ID of the document
    """
    document = crud.get_document(db, document_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    
    return {
        "document_id": document.id,
        "title": document.title,
        "sections": {
            "abstract": document.abstract,
            "introduction": document.introduction,
            "methodology": document.methodology,
            "results": document.results,
            "conclusion": document.conclusion,
            "references": document.references
        }
    }


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document_by_id(document_id: int, db: Session = Depends(get_db)):
    """
    Delete a document
    
    - **document_id**: ID of the document to delete
    """
    document = crud.get_document(db, document_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    
    # Delete file from disk
    file_path = Path(document.file_path)
    if file_path.exists():
        file_path.unlink()
    
    # Delete from database using CRUD
    crud.delete_document(db, document_id)
    
    return None
