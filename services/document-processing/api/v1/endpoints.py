"""
API v1 - Document Processing Endpoints
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pathlib import Path

from database import get_db
from utils.pdf_parser import PDFParser
from utils.text_processor import TextProcessor
from schemas import (
    DocumentResponse,
    TableData,
    FigureMetadata,
    ReferenceItem,
)
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
        # Comprehensive extraction
        figures_dir = settings.upload_dir / 'figures'
        tables = parser.extract_tables()
        figures = parser.extract_figures(output_dir=figures_dir)
        references_struct = parser.extract_references()
        
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
            "upload_date": datetime.now(),
            # New fields
            "tables_data": tables,
            "figures_metadata": figures,
            "references_json": references_struct,
            "tables_extracted": bool(tables),
            "figures_extracted": bool(figures),
            "references_extracted": bool(references_struct),
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


@router.get("/documents/{document_id}/tables", response_model=List[TableData])
async def get_document_tables(document_id: int, db: Session = Depends(get_db)):
    """Return all extracted tables for a document"""
    document = crud.get_document(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document.tables_data or []


@router.get("/documents/{document_id}/figures", response_model=List[FigureMetadata])
async def get_document_figures(document_id: int, db: Session = Depends(get_db)):
    """Return all extracted figures metadata for a document"""
    document = crud.get_document(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document.figures_metadata or []


@router.get("/documents/{document_id}/references/structured", response_model=List[ReferenceItem])
async def get_document_references_structured(document_id: int, db: Session = Depends(get_db)):
    """Return structured references for a document"""
    document = crud.get_document(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document.references_json or []


@router.get("/documents/{document_id}/figure-file/{figure_num}")
async def get_figure_image(document_id: int, figure_num: int, db: Session = Depends(get_db)):
    """Serve a specific figure image file by number"""
    document = crud.get_document(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    figures_meta: List[dict] = document.figures_metadata if isinstance(document.figures_metadata, list) else []
    match_path: Optional[str] = None
    for fig in figures_meta:
        try:
            num = fig.get('figure_num') if isinstance(fig, dict) else None
            if num is not None and int(str(num)) == figure_num:
                match_path = fig.get('file_path')
                break
        except Exception:
            continue
    if not match_path:
        raise HTTPException(status_code=404, detail="Figure not found")
    path = Path(match_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Figure file missing")
    # Let FastAPI serve the file
    return FileResponse(path)


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
    file_path = Path(str(document.file_path))
    if file_path.exists():
        file_path.unlink()
    
    # Delete from database using CRUD
    crud.delete_document(db, document_id)
    
    return None
