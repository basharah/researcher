from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# Request models
class DocumentCreate(BaseModel):
    """Schema for creating a new document"""
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    page_count: int
    title: Optional[str] = None
    authors: Optional[List[str]] = None
    abstract: Optional[str] = None
    introduction: Optional[str] = None
    methodology: Optional[str] = None
    results: Optional[str] = None
    conclusion: Optional[str] = None
    references: Optional[str] = None
    full_text: Optional[str] = None


# Response models
class DocumentResponse(BaseModel):
    id: int
    filename: str
    title: Optional[str]
    authors: Optional[List[str]]
    abstract: Optional[str]
    upload_date: datetime
    file_size: int
    page_count: int
    
    class Config:
        from_attributes = True


class DocumentDetailResponse(DocumentResponse):
    """Extended response with all document fields"""
    original_filename: str
    publication_date: Optional[str]
    doi: Optional[str]
    processing_status: str
    # New comprehensive extraction fields
    tables_extracted: Optional[bool] = None
    figures_extracted: Optional[bool] = None
    references_extracted: Optional[bool] = None
    
    class Config:
        from_attributes = True


class ProcessingStatus(BaseModel):
    document_id: int
    status: str
    message: str
    sections_extracted: int


# New schemas for comprehensive extraction
class TableData(BaseModel):
    page: int
    table_num: int
    data: List[List[Optional[str]]]
    row_count: int
    col_count: int
    caption: Optional[str] = None
    bbox: Optional[List[float]] = None


class FigureMetadata(BaseModel):
    page: int
    figure_num: int
    file_path: Optional[str] = None
    caption: Optional[str] = None
    width: Optional[float] = None
    height: Optional[float] = None
    bbox: Optional[List[float]] = None


class ReferenceItem(BaseModel):
    index: int
    text: str
    year: Optional[int] = None
    title: Optional[str] = None
    authors: List[str] = []
