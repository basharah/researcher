"""
Vector DB Service - Main Application
Handles document chunking, embedding generation, and semantic search
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Import local modules
from database import get_db, engine, Base
from config import settings
from embedding_service import get_embedding_service
from api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager to handle startup and shutdown events"""
    print("🚀 Starting Vector DB Service")
    print("📊 Loading embedding model...")
    get_embedding_service()  # This will load the model
    print("✅ Service ready")
    yield
    # Add any shutdown logic here if needed

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="Service for generating embeddings and semantic search using pgvector",
    version=settings.app_version,
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    debug=settings.debug,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


@app.get("/")
async def root():
    """Service information"""
    return {
        "service": "Vector Database Service",
        "status": "running",
        "version": "1.0.0",
        "embedding_model": settings.embedding_model,
        "embedding_dimension": settings.embedding_dimension
    }


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test database connection
        from sqlalchemy import text as sql_text
        db.execute(sql_text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "database": db_status,
        "embedding_service": "ready"
    }


# Include API router
app.include_router(api_router, prefix=settings.api_prefix)
